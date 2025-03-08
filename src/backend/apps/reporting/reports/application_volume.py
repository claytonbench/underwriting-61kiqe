"""
Application Volume Report Generator for the loan management system.

This module implements the ApplicationVolumeReport class which generates
reports on loan application volume metrics, status distribution, processing times,
and conversion rates to support business analytics and operational monitoring.
"""

from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Count, F, Avg, ExpressionWrapper, DurationField
from django.db.models.functions import Trunc
import json
import pandas as pd

from ..apps.applications.models import LoanApplication, ApplicationStatusHistory
from ..utils.constants import APPLICATION_STATUS
from ..apps.applications.constants import APPLICATION_TYPES, APPLICATION_TERMINAL_STATUSES
from ..reporting.models import SavedReport

# Default report parameters
DEFAULT_PARAMETERS = {
    'date_range': {
        'start_date': None,
        'end_date': None
    },
    'school_id': None,
    'program_id': None,
    'application_type': None,
    'group_by': 'status',  # Options: 'status', 'school', 'program'
    'time_interval': 'day',  # Options: 'day', 'week', 'month', 'quarter', 'year'
    'include_processing_time': True
}

# Status groupings for easier analysis
STATUS_GROUPS = {
    'new': ['draft', 'submitted'],
    'in_progress': ['in_review', 'revision_requested'],
    'approved': [
        'approved', 'commitment_sent', 'commitment_accepted', 
        'documents_sent', 'partially_executed', 'fully_executed',
        'qc_review', 'qc_approved', 'ready_to_fund', 'funded'
    ],
    'declined': ['denied', 'commitment_declined'],
    'abandoned': ['abandoned', 'incomplete', 'documents_expired']
}

# Valid time intervals for trending data
TIME_INTERVALS = ['day', 'week', 'month', 'quarter', 'year']


class ApplicationVolumeReport:
    """
    Report generator for application volume metrics, providing insights into application
    submission trends, status distribution, and processing times.
    """
    
    @property
    def report_type(self):
        """Return the report type identifier."""
        return 'application_volume'
    
    def __init__(self):
        """Initialize the ApplicationVolumeReport with default values."""
        pass
    
    def validate_parameters(self, parameters):
        """
        Validates the report parameters before generation.
        
        Args:
            parameters (dict): The parameters for report generation
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check if time_interval is valid
        time_interval = parameters.get('time_interval')
        if time_interval and time_interval not in TIME_INTERVALS:
            return False, f"Invalid time_interval. Must be one of: {', '.join(TIME_INTERVALS)}"
        
        # Validate date range if provided
        date_range = parameters.get('date_range', {})
        start_date = date_range.get('start_date')
        end_date = date_range.get('end_date')
        
        if start_date and end_date:
            try:
                # Parse and validate dates
                if isinstance(start_date, str):
                    start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                if isinstance(end_date, str):
                    end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                
                if start_date > end_date:
                    return False, "Start date must be before end date"
            except (ValueError, TypeError):
                return False, "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)."
                
        # Validate school_id exists if provided
        school_id = parameters.get('school_id')
        if school_id:
            try:
                from ...apps.schools.models import School
                school_exists = School.objects.filter(id=school_id).exists()
                if not school_exists:
                    return False, f"School with ID {school_id} does not exist"
            except Exception:
                pass
            
        # Validate program_id exists if provided
        program_id = parameters.get('program_id')
        if program_id:
            try:
                from ...apps.schools.models import Program
                program_exists = Program.objects.filter(id=program_id).exists()
                if not program_exists:
                    return False, f"Program with ID {program_id} does not exist"
            except Exception:
                pass
            
        # Validate application_type is valid if provided
        application_type = parameters.get('application_type')
        if application_type and application_type not in APPLICATION_TYPES.values():
            valid_types = ', '.join(APPLICATION_TYPES.values())
            return False, f"Invalid application_type. Must be one of: {valid_types}"
            
        return True, None
        
    def prepare_parameters(self, parameters):
        """
        Prepares and normalizes the report parameters.
        
        Args:
            parameters (dict): The report parameters to normalize
            
        Returns:
            dict: Normalized parameters with defaults applied
        """
        # Start with default parameters
        normalized = DEFAULT_PARAMETERS.copy()
        
        # Update with provided parameters
        if parameters:
            for key, value in parameters.items():
                if key in normalized:
                    normalized[key] = value
        
        # Set default date range if not provided (last 30 days)
        if not normalized['date_range']['start_date'] or not normalized['date_range']['end_date']:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)
            
            normalized['date_range']['start_date'] = start_date
            normalized['date_range']['end_date'] = end_date
        
        # Convert string dates to datetime objects
        if normalized['date_range']['start_date'] and isinstance(normalized['date_range']['start_date'], str):
            normalized['date_range']['start_date'] = datetime.fromisoformat(
                normalized['date_range']['start_date'].replace('Z', '+00:00'))
        
        if normalized['date_range']['end_date'] and isinstance(normalized['date_range']['end_date'], str):
            normalized['date_range']['end_date'] = datetime.fromisoformat(
                normalized['date_range']['end_date'].replace('Z', '+00:00'))
        
        return normalized
    
    def generate(self, report, parameters):
        """
        Generates the application volume report based on the provided parameters.
        
        Args:
            report (SavedReport): The report object to update with results
            parameters (dict): Parameters for report generation
            
        Returns:
            bool: True if report generation was successful, False otherwise
        """
        # Update report status to generating
        report.update_status('generating')
        
        # Validate parameters
        is_valid, error_message = self.validate_parameters(parameters)
        if not is_valid:
            report.set_error(error_message)
            return False
        
        # Prepare parameters with defaults
        params = self.prepare_parameters(parameters)
        
        try:
            # Base queryset for application data
            queryset = LoanApplication.objects.all()
            
            # Apply filters based on parameters
            if params['date_range']['start_date'] and params['date_range']['end_date']:
                queryset = queryset.filter(
                    created_at__gte=params['date_range']['start_date'],
                    created_at__lte=params['date_range']['end_date']
                )
            
            if params['school_id']:
                queryset = queryset.filter(school_id=params['school_id'])
            
            if params['program_id']:
                queryset = queryset.filter(program_id=params['program_id'])
            
            if params['application_type']:
                queryset = queryset.filter(application_type=params['application_type'])
            
            # Generate the metrics
            volume_metrics = self.get_application_volume(queryset, params)
            status_distribution = self.get_status_distribution(queryset, params)
            time_trend = self.get_time_trend(queryset, params)
            conversion_rates = self.get_conversion_rates(queryset, params)
            
            # Get processing time metrics if requested
            processing_time = {}
            if params['include_processing_time']:
                processing_time = self.get_processing_time(queryset, params)
            
            # Get school/program breakdown if grouping by those fields
            school_program_breakdown = {}
            if params['group_by'] in ['school', 'program']:
                school_program_breakdown = self.get_school_program_breakdown(queryset, params)
            
            # Format results
            results = self.format_results(
                volume_metrics,
                status_distribution,
                time_trend,
                processing_time,
                conversion_rates,
                school_program_breakdown
            )
            
            # Generate export file if needed
            file_path = None
            file_format = params.get('export_format')
            if file_format:
                file_path = self.generate_export_file(results, file_format)
            
            # Update report with results
            report.set_results(results, file_path=file_path, file_format=file_format)
            
            return True
            
        except Exception as e:
            error_message = f"Error generating application volume report: {str(e)}"
            report.set_error(error_message)
            return False
    
    def get_application_volume(self, queryset, parameters):
        """
        Calculates the total application volume and growth metrics.
        
        Args:
            queryset (QuerySet): The filtered application queryset
            parameters (dict): Report parameters
            
        Returns:
            dict: Application volume metrics
        """
        # Get total count
        total_count = queryset.count()
        
        # Calculate timeframe in days
        start_date = parameters['date_range']['start_date']
        end_date = parameters['date_range']['end_date']
        date_range_days = (end_date - start_date).days or 1  # Avoid division by zero
        
        # Get counts for previous period of same length for comparison
        previous_start = start_date - timedelta(days=date_range_days)
        previous_end = start_date - timedelta(days=1)
        
        previous_count = LoanApplication.objects.filter(
            created_at__gte=previous_start,
            created_at__lte=previous_end
        ).count()
        
        # Calculate growth percentage
        if previous_count > 0:
            growth_percentage = ((total_count - previous_count) / previous_count) * 100
        else:
            growth_percentage = None
        
        # Calculate average volume by selected time interval
        avg_volume = total_count / date_range_days
        if parameters['time_interval'] == 'week':
            avg_volume = avg_volume * 7
        elif parameters['time_interval'] == 'month':
            avg_volume = avg_volume * 30
        
        return {
            'total_applications': total_count,
            'previous_period_applications': previous_count,
            'growth_percentage': growth_percentage,
            f'average_applications_per_{parameters["time_interval"]}': avg_volume,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': date_range_days
            }
        }
    
    def get_status_distribution(self, queryset, parameters):
        """
        Calculates the distribution of applications by status.
        
        Args:
            queryset (QuerySet): The filtered application queryset
            parameters (dict): Report parameters
            
        Returns:
            dict: Status distribution data
        """
        # Count applications by status
        status_counts = queryset.values('status').annotate(count=Count('id'))
        
        # Convert to dictionary for easier manipulation
        status_dict = {item['status']: item['count'] for item in status_counts}
        
        # Calculate total for percentages
        total = sum(status_dict.values())
        
        # Format with percentages
        status_distribution = {
            'by_status': {
                status: {
                    'count': status_dict.get(status, 0),
                    'percentage': (status_dict.get(status, 0) / total * 100) if total > 0 else 0
                }
                for status in APPLICATION_STATUS.values()
            },
            'total': total
        }
        
        # Group statuses into categories if requested
        status_distribution['by_category'] = {}
        for category, statuses in STATUS_GROUPS.items():
            category_count = sum(status_dict.get(status, 0) for status in statuses)
            status_distribution['by_category'][category] = {
                'count': category_count,
                'percentage': (category_count / total * 100) if total > 0 else 0
            }
        
        return status_distribution
    
    def get_time_trend(self, queryset, parameters):
        """
        Generates time-based trend data for application volume.
        
        Args:
            queryset (QuerySet): The filtered application queryset
            parameters (dict): Report parameters
            
        Returns:
            dict: Time-based trend data
        """
        time_interval = parameters['time_interval']
        
        # Determine the date trunc function to use
        if time_interval == 'day':
            trunc_func = 'day'
        elif time_interval == 'week':
            trunc_func = 'week'
        elif time_interval == 'month':
            trunc_func = 'month'
        elif time_interval == 'quarter':
            trunc_func = 'quarter'
        else:  # year
            trunc_func = 'year'
            
        # Group by date interval and status
        trend_data = queryset.annotate(
            interval=Trunc('created_at', trunc_func)
        ).values('interval', 'status').annotate(
            count=Count('id')
        ).order_by('interval')
        
        # Organize data by interval and status
        result = {}
        for item in trend_data:
            interval_str = item['interval'].isoformat()
            status = item['status']
            
            if interval_str not in result:
                result[interval_str] = {
                    'total': 0,
                    'by_status': {}
                }
            
            result[interval_str]['by_status'][status] = item['count']
            result[interval_str]['total'] += item['count']
            
        # Format trend data as a list sorted by date
        trend_list = [
            {
                'date': interval,
                'total': data['total'],
                'by_status': data['by_status']
            }
            for interval, data in sorted(result.items())
        ]
        
        # Add running totals if requested
        if parameters.get('include_running_totals', False):
            running_total = 0
            running_totals_by_status = {}
            
            for interval in trend_list:
                running_total += interval['total']
                interval['running_total'] = running_total
                
                for status, count in interval['by_status'].items():
                    running_totals_by_status[status] = running_totals_by_status.get(status, 0) + count
                    
                interval['running_totals_by_status'] = running_totals_by_status.copy()
        
        return {
            'interval': time_interval,
            'data': trend_list
        }
    
    def get_processing_time(self, queryset, parameters):
        """
        Calculates metrics for application processing times.
        
        Args:
            queryset (QuerySet): The filtered application queryset
            parameters (dict): Report parameters
            
        Returns:
            dict: Processing time metrics
        """
        # Find applications with status changes
        status_transitions = ApplicationStatusHistory.objects.filter(
            application__in=queryset
        ).values(
            'application_id', 'previous_status', 'new_status', 'changed_at'
        ).order_by('application_id', 'changed_at')
        
        # Calculate time in each status
        status_time_data = {}
        app_time_data = {}
        
        for record in status_transitions:
            app_id = record['application_id']
            prev_status = record['previous_status']
            new_status = record['new_status']
            changed_at = record['changed_at']
            
            if app_id not in app_time_data:
                app_time_data[app_id] = {'transitions': [], 'submission_to_decision': None}
            
            app_time_data[app_id]['transitions'].append({
                'previous_status': prev_status,
                'new_status': new_status,
                'changed_at': changed_at
            })
            
            # Track key transitions for metrics
            if prev_status == APPLICATION_STATUS['SUBMITTED'] and new_status in [
                APPLICATION_STATUS['APPROVED'], APPLICATION_STATUS['DENIED']
            ]:
                # Find the original submission time
                submission_records = ApplicationStatusHistory.objects.filter(
                    application_id=app_id,
                    new_status=APPLICATION_STATUS['SUBMITTED']
                ).order_by('changed_at')
                
                if submission_records.exists():
                    submission_time = submission_records.first().changed_at
                    decision_time = changed_at
                    time_to_decision = (decision_time - submission_time).total_seconds() / 3600  # hours
                    app_time_data[app_id]['submission_to_decision'] = time_to_decision
        
        # Compute average time in each status
        status_pairs = {}
        for app_id, data in app_time_data.items():
            for i in range(len(data['transitions']) - 1):
                curr = data['transitions'][i]
                next_record = data['transitions'][i + 1]
                
                status = curr['new_status']
                time_in_status = (next_record['changed_at'] - curr['changed_at']).total_seconds() / 3600  # hours
                
                if status not in status_pairs:
                    status_pairs[status] = []
                
                status_pairs[status].append(time_in_status)
        
        # Calculate statistics for each status
        status_time_stats = {}
        for status, times in status_pairs.items():
            if times:
                status_time_stats[status] = {
                    'average_hours': sum(times) / len(times),
                    'min_hours': min(times),
                    'max_hours': max(times),
                    'count': len(times)
                }
        
        # Calculate average time from submission to decision
        decision_times = [data['submission_to_decision'] for app_id, data in app_time_data.items() 
                         if data['submission_to_decision'] is not None]
        
        avg_time_to_decision = None
        if decision_times:
            avg_time_to_decision = sum(decision_times) / len(decision_times)
        
        return {
            'average_time_to_decision_hours': avg_time_to_decision,
            'status_timing': status_time_stats,
            'sample_size': len(decision_times)
        }
    
    def get_conversion_rates(self, queryset, parameters):
        """
        Calculates conversion rates between application statuses.
        
        Args:
            queryset (QuerySet): The filtered application queryset
            parameters (dict): Report parameters
            
        Returns:
            dict: Conversion rate metrics
        """
        # Count applications by status
        status_counts = {
            status: queryset.filter(status=status).count()
            for status in APPLICATION_STATUS.values()
        }
        
        # Add count for grouped statuses
        for category, statuses in STATUS_GROUPS.items():
            status_counts[f'group_{category}'] = queryset.filter(status__in=statuses).count()
        
        # Calculate key conversion metrics
        
        # Draft to Submitted rate
        draft_count = status_counts.get(APPLICATION_STATUS['DRAFT'], 0)
        submitted_count = status_counts.get(APPLICATION_STATUS['SUBMITTED'], 0)
        submission_rate = (submitted_count / (draft_count + submitted_count)) * 100 if (draft_count + submitted_count) > 0 else 0
        
        # Submitted to Approved rate
        approved_status = [
            APPLICATION_STATUS['APPROVED'],
            APPLICATION_STATUS['COMMITMENT_SENT'],
            APPLICATION_STATUS['COMMITMENT_ACCEPTED'],
            APPLICATION_STATUS['DOCUMENTS_SENT'],
            APPLICATION_STATUS['PARTIALLY_EXECUTED'],
            APPLICATION_STATUS['FULLY_EXECUTED'],
            APPLICATION_STATUS['QC_REVIEW'],
            APPLICATION_STATUS['QC_APPROVED'],
            APPLICATION_STATUS['READY_TO_FUND'],
            APPLICATION_STATUS['FUNDED']
        ]
        
        approved_count = sum(status_counts.get(status, 0) for status in approved_status)
        denied_count = status_counts.get(APPLICATION_STATUS['DENIED'], 0)
        
        approval_rate = (approved_count / (approved_count + denied_count)) * 100 if (approved_count + denied_count) > 0 else 0
        
        # Approved to Funded rate
        funded_count = status_counts.get(APPLICATION_STATUS['FUNDED'], 0)
        funding_rate = (funded_count / approved_count) * 100 if approved_count > 0 else 0
        
        # Overall completion rate (submitted to funded)
        completion_rate = (funded_count / submitted_count) * 100 if submitted_count > 0 else 0
        
        # Terminal status breakdown
        terminal_status_counts = {
            status: status_counts.get(status, 0)
            for status in APPLICATION_TERMINAL_STATUSES
        }
        
        total_terminal = sum(terminal_status_counts.values())
        terminal_percentages = {
            status: (count / total_terminal * 100) if total_terminal > 0 else 0
            for status, count in terminal_status_counts.items()
        }
        
        return {
            'submission_rate': submission_rate,
            'approval_rate': approval_rate,
            'funding_rate': funding_rate,
            'completion_rate': completion_rate,
            'terminal_status_distribution': {
                'counts': terminal_status_counts,
                'percentages': terminal_percentages,
                'total': total_terminal
            }
        }
    
    def get_school_program_breakdown(self, queryset, parameters):
        """
        Breaks down application metrics by school and program.
        
        Args:
            queryset (QuerySet): The filtered application queryset
            parameters (dict): Report parameters
            
        Returns:
            dict: School and program breakdown data
        """
        # Group by school
        school_data = queryset.values('school_id', 'school__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        schools = {}
        for item in school_data:
            school_id = item['school_id']
            school_name = item['school__name']
            
            if school_id not in schools:
                schools[school_id] = {
                    'id': school_id,
                    'name': school_name,
                    'total_applications': item['count'],
                    'programs': {}
                }
                
                # Calculate approval rate for this school
                school_apps = queryset.filter(school_id=school_id)
                approved_count = school_apps.filter(status__in=[
                    APPLICATION_STATUS['APPROVED'], 
                    APPLICATION_STATUS['COMMITMENT_SENT'],
                    APPLICATION_STATUS['COMMITMENT_ACCEPTED'],
                    APPLICATION_STATUS['DOCUMENTS_SENT'],
                    APPLICATION_STATUS['PARTIALLY_EXECUTED'],
                    APPLICATION_STATUS['FULLY_EXECUTED'],
                    APPLICATION_STATUS['QC_REVIEW'],
                    APPLICATION_STATUS['QC_APPROVED'],
                    APPLICATION_STATUS['READY_TO_FUND'],
                    APPLICATION_STATUS['FUNDED']
                ]).count()
                
                denied_count = school_apps.filter(status=APPLICATION_STATUS['DENIED']).count()
                
                approval_rate = (approved_count / (approved_count + denied_count)) * 100 if (approved_count + denied_count) > 0 else 0
                schools[school_id]['approval_rate'] = approval_rate
        
        # Group by program for each school
        program_data = queryset.values('school_id', 'program_id', 'program__name').annotate(
            count=Count('id')
        ).order_by('school_id', '-count')
        
        for item in program_data:
            school_id = item['school_id']
            program_id = item['program_id']
            program_name = item['program__name']
            
            if school_id in schools:
                if program_id not in schools[school_id]['programs']:
                    schools[school_id]['programs'][program_id] = {
                        'id': program_id,
                        'name': program_name,
                        'application_count': item['count']
                    }
                    
                    # Calculate approval rate for this program
                    program_apps = queryset.filter(program_id=program_id)
                    approved_count = program_apps.filter(status__in=[
                        APPLICATION_STATUS['APPROVED'], 
                        APPLICATION_STATUS['COMMITMENT_SENT'],
                        APPLICATION_STATUS['COMMITMENT_ACCEPTED'],
                        APPLICATION_STATUS['DOCUMENTS_SENT'],
                        APPLICATION_STATUS['PARTIALLY_EXECUTED'],
                        APPLICATION_STATUS['FULLY_EXECUTED'],
                        APPLICATION_STATUS['QC_REVIEW'],
                        APPLICATION_STATUS['QC_APPROVED'],
                        APPLICATION_STATUS['READY_TO_FUND'],
                        APPLICATION_STATUS['FUNDED']
                    ]).count()
                    
                    denied_count = program_apps.filter(status=APPLICATION_STATUS['DENIED']).count()
                    
                    approval_rate = (approved_count / (approved_count + denied_count)) * 100 if (approved_count + denied_count) > 0 else 0
                    schools[school_id]['programs'][program_id]['approval_rate'] = approval_rate
        
        # Convert to list format
        school_list = []
        for school_id, school_data in schools.items():
            program_list = [program for program_id, program in school_data['programs'].items()]
            school_data['programs'] = sorted(program_list, key=lambda x: x['application_count'], reverse=True)
            school_list.append(school_data)
        
        return {
            'schools': sorted(school_list, key=lambda x: x['total_applications'], reverse=True)
        }
    
    def format_results(self, volume_metrics, status_distribution, time_trend, 
                      processing_time, conversion_rates, school_program_breakdown):
        """
        Formats the report results into the required structure.
        
        Args:
            volume_metrics (dict): Application volume metrics
            status_distribution (dict): Status distribution data
            time_trend (dict): Time-based trend data
            processing_time (dict): Processing time metrics
            conversion_rates (dict): Conversion rate metrics
            school_program_breakdown (dict): School and program breakdown data
            
        Returns:
            dict: Formatted report results
        """
        return {
            'metadata': {
                'generated_at': timezone.now().isoformat(),
                'report_type': 'application_volume'
            },
            'volume_metrics': volume_metrics,
            'status_distribution': status_distribution,
            'time_trend': time_trend,
            'processing_time': processing_time,
            'conversion_rates': conversion_rates,
            'school_program_breakdown': school_program_breakdown
        }
    
    def generate_export_file(self, results, format):
        """
        Generates an export file (CSV/Excel) from the report data.
        
        Args:
            results (dict): The report results
            format (str): The desired file format (csv, xlsx, etc.)
            
        Returns:
            str: Path to the generated file
        """
        # Convert results to pandas DataFrames for export
        report_date = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f"application_volume_report_{report_date}"
        
        # Create DataFrames for different sections
        volume_df = pd.DataFrame([results['volume_metrics']])
        
        # Status distribution
        status_df = pd.DataFrame([{
            'status': status,
            'count': data['count'],
            'percentage': data['percentage']
        } for status, data in results['status_distribution']['by_status'].items()])
        
        # Time trend
        trend_df = pd.DataFrame(results['time_trend']['data'])
        
        # School breakdown
        schools_df = pd.DataFrame([{
            'school_id': school['id'],
            'school_name': school['name'],
            'total_applications': school['total_applications'],
            'approval_rate': school['approval_rate'],
        } for school in results['school_program_breakdown'].get('schools', [])])
        
        # Create file in the appropriate format
        file_path = f"/tmp/{filename}.{format}"
        
        if format == 'csv':
            # Create a CSV with multiple sections
            with open(file_path, 'w') as f:
                f.write("APPLICATION VOLUME REPORT\n\n")
                f.write("VOLUME METRICS\n")
                volume_df.to_csv(f, index=False)
                f.write("\nSTATUS DISTRIBUTION\n")
                status_df.to_csv(f, index=False)
                f.write("\nTIME TREND\n")
                trend_df.to_csv(f, index=False)
                f.write("\nSCHOOL BREAKDOWN\n")
                schools_df.to_csv(f, index=False)
                
        elif format == 'xlsx':
            # Create Excel with multiple sheets
            with pd.ExcelWriter(file_path) as writer:
                volume_df.to_excel(writer, sheet_name='Volume Metrics', index=False)
                status_df.to_excel(writer, sheet_name='Status Distribution', index=False)
                trend_df.to_excel(writer, sheet_name='Time Trend', index=False)
                schools_df.to_excel(writer, sheet_name='School Breakdown', index=False)
        
        # In a production environment, we would upload this file to S3 storage
        # from utils.storage import S3Storage
        # s3_storage = S3Storage()
        # s3_path = s3_storage.store(file_path, f"reports/{filename}.{format}")
        # return s3_path
        
        return file_path