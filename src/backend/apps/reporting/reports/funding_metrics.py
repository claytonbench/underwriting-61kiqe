"""
Implements the FundingMetricsReport class for generating reports on loan funding metrics.

This report provides insights into disbursement volumes, funding timelines, school payments,
and other funding-related analytics to support business monitoring and financial oversight.
"""

import datetime
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg, ExpressionWrapper, DurationField, F, Min, Max
from django.db.models.functions import Trunc
import json
import pandas as pd

# Import models and constants
from ...apps.funding.models import FundingRequest, Disbursement
from ...apps.funding.constants import FUNDING_REQUEST_STATUS, DISBURSEMENT_STATUS
from ..reporting.models import SavedReport

# Default parameters for the funding metrics report
DEFAULT_PARAMETERS = {
    'date_range': {
        'start_date': None,
        'end_date': None
    },
    'school_id': None,
    'program_id': None,
    'group_by': 'status',
    'time_interval': 'month',
    'include_time_to_fund': True
}

# Grouping of funding statuses into logical categories
FUNDING_STATUS_GROUPS = {
    'pending': [
        'pending_enrollment',
        'enrollment_verified',
        'pending_stipulations'
    ],
    'approved': [
        'stipulations_complete',
        'approved',
        'scheduled_for_disbursement'
    ],
    'completed': [
        'disbursed'
    ],
    'cancelled': [
        'rejected',
        'cancelled'
    ]
}

# Valid time intervals for trend analysis
TIME_INTERVALS = ['day', 'week', 'month', 'quarter', 'year']


class FundingMetricsReport:
    """
    Report generator for funding metrics, providing insights into disbursement volumes,
    funding timelines, and school payments.
    """
    
    @property
    def report_type(self):
        return 'funding_metrics'
    
    def __init__(self):
        """
        Initialize the FundingMetricsReport with default values.
        """
        pass
    
    def validate_parameters(self, parameters):
        """
        Validates the report parameters before generation.
        
        Args:
            parameters (dict): Parameters for the report generation
            
        Returns:
            tuple: Tuple containing (is_valid, error_message)
        """
        # Validate time interval
        time_interval = parameters.get('time_interval', DEFAULT_PARAMETERS['time_interval'])
        if time_interval not in TIME_INTERVALS:
            return False, f"Invalid time_interval: {time_interval}. Must be one of {TIME_INTERVALS}"
        
        # Validate date range if provided
        date_range = parameters.get('date_range', {})
        start_date = date_range.get('start_date')
        end_date = date_range.get('end_date')
        
        if start_date and end_date:
            # Convert string dates to datetime objects if needed
            if isinstance(start_date, str):
                try:
                    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                except ValueError:
                    return False, f"Invalid start_date format: {start_date}. Must be YYYY-MM-DD"
            
            if isinstance(end_date, str):
                try:
                    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
                except ValueError:
                    return False, f"Invalid end_date format: {end_date}. Must be YYYY-MM-DD"
            
            # Ensure start_date is before end_date
            if start_date > end_date:
                return False, f"start_date ({start_date}) must be before end_date ({end_date})"
        
        # Validate school_id if provided
        school_id = parameters.get('school_id')
        if school_id:
            # In a real implementation, we would check if the school exists
            # For this exercise, we'll just pass validation
            pass
        
        # Validate program_id if provided
        program_id = parameters.get('program_id')
        if program_id:
            # In a real implementation, we would check if the program exists
            # For this exercise, we'll just pass validation
            pass
        
        return True, None
    
    def prepare_parameters(self, parameters):
        """
        Prepares and normalizes the report parameters.
        
        Args:
            parameters (dict): Parameters for the report generation
            
        Returns:
            dict: Normalized parameters with defaults applied
        """
        # Start with default parameters
        prepared_params = DEFAULT_PARAMETERS.copy()
        
        # Update with provided parameters
        if parameters:
            prepared_params.update(parameters)
        
        # Set default date range if not provided
        date_range = prepared_params.get('date_range', {})
        if not date_range.get('start_date'):
            # Default to last 30 days
            end_date = timezone.now().date()
            start_date = end_date - datetime.timedelta(days=30)
            prepared_params['date_range'] = {
                'start_date': start_date,
                'end_date': end_date
            }
        else:
            # Convert string dates to datetime objects if needed
            start_date = date_range.get('start_date')
            end_date = date_range.get('end_date')
            
            if isinstance(start_date, str):
                prepared_params['date_range']['start_date'] = datetime.datetime.strptime(
                    start_date, '%Y-%m-%d').date()
            
            if isinstance(end_date, str):
                prepared_params['date_range']['end_date'] = datetime.datetime.strptime(
                    end_date, '%Y-%m-%d').date()
        
        return prepared_params
    
    def generate(self, report, parameters):
        """
        Generates the funding metrics report based on the provided parameters.
        
        Args:
            report (SavedReport): The report instance to update
            parameters (dict): Parameters for the report generation
            
        Returns:
            bool: True if report generation was successful, False otherwise
        """
        # Update report status to GENERATING
        report.update_status('generating')
        
        # Validate parameters
        is_valid, error_message = self.validate_parameters(parameters)
        if not is_valid:
            report.set_error(error_message)
            return False
        
        try:
            # Prepare parameters with defaults
            prepared_params = self.prepare_parameters(parameters)
            
            # Build base queries for funding requests and disbursements
            funding_queryset = self._build_funding_query(prepared_params)
            disbursement_queryset = self._build_disbursement_query(prepared_params)
            
            # Generate metrics
            volume_metrics = self.get_disbursement_volume(funding_queryset, disbursement_queryset, prepared_params)
            status_distribution = self.get_status_distribution(funding_queryset, prepared_params)
            time_trend = self.get_time_trend(disbursement_queryset, prepared_params)
            
            # Generate time-to-fund metrics if requested
            time_to_fund = {}
            if prepared_params.get('include_time_to_fund', True):
                time_to_fund = self.get_time_to_fund(funding_queryset, disbursement_queryset, prepared_params)
            
            # Generate school/program breakdown
            school_program_breakdown = self.get_school_program_breakdown(
                funding_queryset, disbursement_queryset, prepared_params)
            
            # Format results
            results = self.format_results(
                volume_metrics,
                status_distribution,
                time_trend,
                time_to_fund,
                school_program_breakdown
            )
            
            # Generate export file if requested
            file_path = None
            file_format = None
            if parameters.get('export_format'):
                file_format = parameters.get('export_format')
                file_path = self.generate_export_file(results, file_format)
            
            # Update report with results
            report.set_results(results, file_path, file_format)
            
            return True
            
        except Exception as e:
            report.set_error(f"Error generating funding metrics report: {str(e)}")
            return False
    
    def _build_funding_query(self, parameters):
        """
        Builds the base query for funding requests based on parameters.
        
        Args:
            parameters (dict): Report parameters
            
        Returns:
            QuerySet: Filtered funding request queryset
        """
        queryset = FundingRequest.objects.all()
        
        # Apply date range filter
        date_range = parameters.get('date_range', {})
        start_date = date_range.get('start_date')
        end_date = date_range.get('end_date')
        
        if start_date:
            queryset = queryset.filter(requested_at__gte=start_date)
        
        if end_date:
            # Include the entire end date
            end_datetime = datetime.datetime.combine(
                end_date, datetime.time(23, 59, 59))
            queryset = queryset.filter(requested_at__lte=end_datetime)
        
        # Apply school filter if provided
        school_id = parameters.get('school_id')
        if school_id:
            queryset = queryset.filter(application__school_id=school_id)
        
        # Apply program filter if provided
        program_id = parameters.get('program_id')
        if program_id:
            queryset = queryset.filter(application__program_id=program_id)
        
        return queryset
    
    def _build_disbursement_query(self, parameters):
        """
        Builds the base query for disbursements based on parameters.
        
        Args:
            parameters (dict): Report parameters
            
        Returns:
            QuerySet: Filtered disbursement queryset
        """
        queryset = Disbursement.objects.all()
        
        # Apply date range filter
        date_range = parameters.get('date_range', {})
        start_date = date_range.get('start_date')
        end_date = date_range.get('end_date')
        
        if start_date:
            queryset = queryset.filter(disbursement_date__gte=start_date)
        
        if end_date:
            # Include the entire end date
            end_datetime = datetime.datetime.combine(
                end_date, datetime.time(23, 59, 59))
            queryset = queryset.filter(disbursement_date__lte=end_datetime)
        
        # Apply school filter if provided
        school_id = parameters.get('school_id')
        if school_id:
            queryset = queryset.filter(funding_request__application__school_id=school_id)
        
        # Apply program filter if provided
        program_id = parameters.get('program_id')
        if program_id:
            queryset = queryset.filter(funding_request__application__program_id=program_id)
        
        return queryset
    
    def get_disbursement_volume(self, funding_queryset, disbursement_queryset, parameters):
        """
        Calculates the total disbursement volume and growth metrics.
        
        Args:
            funding_queryset (QuerySet): Filtered funding request queryset
            disbursement_queryset (QuerySet): Filtered disbursement queryset
            parameters (dict): Report parameters
            
        Returns:
            dict: Disbursement volume metrics
        """
        # Count total funding requests
        total_requests = funding_queryset.count()
        
        # Calculate total disbursed amount
        disbursed_amount = disbursement_queryset.filter(
            status=DISBURSEMENT_STATUS['COMPLETED']
        ).aggregate(
            total=Sum('amount')
        ).get('total', 0) or 0
        
        # Calculate average disbursement amount
        completed_disbursements = disbursement_queryset.filter(
            status=DISBURSEMENT_STATUS['COMPLETED']
        )
        
        count_completed = completed_disbursements.count()
        avg_amount = 0
        if count_completed > 0:
            avg_amount = disbursed_amount / count_completed
        
        # Calculate previous period metrics for growth calculation
        date_range = parameters.get('date_range', {})
        current_start = date_range.get('start_date')
        current_end = date_range.get('end_date')
        
        growth_percentage = 0
        previous_amount = 0
        
        if current_start and current_end:
            # Calculate date range for previous period of same length
            period_length = (current_end - current_start).days
            previous_end = current_start - datetime.timedelta(days=1)
            previous_start = previous_end - datetime.timedelta(days=period_length)
            
            # Query previous period
            previous_disbursements = Disbursement.objects.filter(
                disbursement_date__gte=previous_start,
                disbursement_date__lte=previous_end,
                status=DISBURSEMENT_STATUS['COMPLETED']
            )
            
            if parameters.get('school_id'):
                previous_disbursements = previous_disbursements.filter(
                    funding_request__application__school_id=parameters.get('school_id')
                )
                
            if parameters.get('program_id'):
                previous_disbursements = previous_disbursements.filter(
                    funding_request__application__program_id=parameters.get('program_id')
                )
            
            previous_amount = previous_disbursements.aggregate(
                total=Sum('amount')
            ).get('total', 0) or 0
            
            # Calculate growth percentage
            if previous_amount > 0:
                growth_percentage = ((disbursed_amount - previous_amount) / previous_amount) * 100
        
        return {
            'total_requests': total_requests,
            'total_disbursed': disbursed_amount,
            'avg_disbursement': avg_amount,
            'previous_period_amount': previous_amount,
            'growth_percentage': growth_percentage,
            'completed_disbursements': count_completed
        }
    
    def get_status_distribution(self, queryset, parameters):
        """
        Calculates the distribution of funding requests by status.
        
        Args:
            queryset (QuerySet): Filtered funding request queryset
            parameters (dict): Report parameters
            
        Returns:
            dict: Status distribution data
        """
        # Group by status
        status_counts = queryset.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        total_count = queryset.count()
        status_data = []
        
        for status_count in status_counts:
            status = status_count['status']
            count = status_count['count']
            percentage = (count / total_count * 100) if total_count > 0 else 0
            
            status_data.append({
                'status': status,
                'count': count,
                'percentage': percentage
            })
        
        # Apply grouping if specified
        group_by = parameters.get('group_by')
        if group_by == 'category':
            # Group by logical categories (pending, approved, completed, cancelled)
            category_data = {category: 0 for category in FUNDING_STATUS_GROUPS.keys()}
            
            for status_item in status_data:
                status = status_item['status']
                count = status_item['count']
                
                # Find which category this status belongs to
                for category, statuses in FUNDING_STATUS_GROUPS.items():
                    if status in statuses:
                        category_data[category] += count
                        break
            
            # Calculate percentages for categories
            grouped_data = []
            for category, count in category_data.items():
                percentage = (count / total_count * 100) if total_count > 0 else 0
                grouped_data.append({
                    'category': category,
                    'count': count,
                    'percentage': percentage
                })
            
            return {
                'by_category': grouped_data,
                'by_status': status_data,
                'total_count': total_count
            }
        
        return {
            'by_status': status_data,
            'total_count': total_count
        }
    
    def get_time_trend(self, queryset, parameters):
        """
        Generates time-based trend data for disbursements.
        
        Args:
            queryset (QuerySet): Filtered disbursement queryset
            parameters (dict): Report parameters
            
        Returns:
            dict: Time-based trend data
        """
        # Determine time interval for grouping
        time_interval = parameters.get('time_interval', 'month')
        
        # Apply status filter to only include completed disbursements
        completed_queryset = queryset.filter(status=DISBURSEMENT_STATUS['COMPLETED'])
        
        # Group by time interval
        truncated_date = Trunc('disbursement_date', time_interval)
        trend_data = completed_queryset.annotate(
            interval=truncated_date
        ).values('interval').annotate(
            amount=Sum('amount'),
            count=Count('id')
        ).order_by('interval')
        
        # Convert to list of dicts for output
        results = []
        running_total = 0
        
        for item in trend_data:
            interval_date = item['interval']
            amount = item['amount'] or 0
            count = item['count']
            
            # Calculate running total
            running_total += amount
            
            results.append({
                'interval': interval_date.strftime('%Y-%m-%d'),
                'amount': amount,
                'count': count,
                'running_total': running_total
            })
        
        return {
            'time_interval': time_interval,
            'trend_data': results
        }
    
    def get_time_to_fund(self, funding_queryset, disbursement_queryset, parameters):
        """
        Calculates metrics for time from approval to disbursement.
        
        Args:
            funding_queryset (QuerySet): Filtered funding request queryset
            disbursement_queryset (QuerySet): Filtered disbursement queryset
            parameters (dict): Report parameters
            
        Returns:
            dict: Time-to-fund metrics
        """
        # This is a complex calculation that would normally be done with Django ORM
        # For simplicity, we'll implement a more straightforward approach
        
        # Get all completed disbursements with their funding requests
        completed_disbursements = disbursement_queryset.filter(
            status=DISBURSEMENT_STATUS['COMPLETED']
        ).select_related('funding_request')
        
        # Calculate time to fund for each request
        time_to_fund_days = []
        
        for disbursement in completed_disbursements:
            funding_request = disbursement.funding_request
            
            if funding_request.approved_at and disbursement.disbursement_date:
                # Calculate days between approval and disbursement
                approval_date = funding_request.approved_at.date()
                disbursement_date = disbursement.disbursement_date.date()
                days_to_fund = (disbursement_date - approval_date).days
                
                # Only include positive values (can't fund before approval)
                if days_to_fund >= 0:
                    time_to_fund_days.append(days_to_fund)
        
        # Calculate metrics if we have data
        if time_to_fund_days:
            avg_days = sum(time_to_fund_days) / len(time_to_fund_days)
            min_days = min(time_to_fund_days)
            max_days = max(time_to_fund_days)
            
            # Calculate median
            time_to_fund_days.sort()
            n = len(time_to_fund_days)
            if n % 2 == 0:
                median_days = (time_to_fund_days[n//2 - 1] + time_to_fund_days[n//2]) / 2
            else:
                median_days = time_to_fund_days[n//2]
            
            # Create time distribution
            time_distribution = self._get_time_distribution(time_to_fund_days)
            
            return {
                'average_days': avg_days,
                'median_days': median_days,
                'min_days': min_days,
                'max_days': max_days,
                'request_count': len(time_to_fund_days),
                'time_distribution': time_distribution
            }
        
        # Return empty metrics if no data
        return {
            'average_days': 0,
            'median_days': 0,
            'min_days': 0,
            'max_days': 0,
            'request_count': 0,
            'time_distribution': []
        }
    
    def _get_time_distribution(self, days_list):
        """
        Helper method to create a distribution of time-to-fund values.
        
        Args:
            days_list (list): List of time-to-fund values in days
            
        Returns:
            list: Distribution of values by range
        """
        if not days_list:
            return []
        
        # Define distribution ranges
        ranges = [
            {'label': '0-1 days', 'min': 0, 'max': 1, 'count': 0},
            {'label': '2-3 days', 'min': 2, 'max': 3, 'count': 0},
            {'label': '4-7 days', 'min': 4, 'max': 7, 'count': 0},
            {'label': '8-14 days', 'min': 8, 'max': 14, 'count': 0},
            {'label': '15+ days', 'min': 15, 'max': float('inf'), 'count': 0}
        ]
        
        # Count values in each range
        for days in days_list:
            for range_def in ranges:
                if range_def['min'] <= days <= range_def['max']:
                    range_def['count'] += 1
                    break
        
        # Calculate percentages
        total = len(days_list)
        for range_def in ranges:
            range_def['percentage'] = (range_def['count'] / total * 100) if total > 0 else 0
        
        return ranges
    
    def get_school_program_breakdown(self, funding_queryset, disbursement_queryset, parameters):
        """
        Breaks down funding metrics by school and program.
        
        Args:
            funding_queryset (QuerySet): Filtered funding request queryset
            disbursement_queryset (QuerySet): Filtered disbursement queryset
            parameters (dict): Report parameters
            
        Returns:
            dict: School and program breakdown data
        """
        # Group funding requests by school
        school_metrics = funding_queryset.values(
            'application__school_id', 
            'application__school__name'
        ).annotate(
            request_count=Count('id'),
            disbursed_count=Count('id', filter=Q(status=FUNDING_REQUEST_STATUS['DISBURSED']))
        ).order_by('application__school__name')
        
        # Get disbursement amounts by school
        school_disbursements = disbursement_queryset.filter(
            status=DISBURSEMENT_STATUS['COMPLETED']
        ).values('funding_request__application__school_id').annotate(
            total_amount=Sum('amount')
        )
        
        # Create a lookup for school disbursement amounts
        school_amount_map = {
            item['funding_request__application__school_id']: item['total_amount']
            for item in school_disbursements
        }
        
        # Prepare school breakdown with program details
        schools_data = []
        
        for school in school_metrics:
            school_id = school['application__school_id']
            
            # Get program metrics for this school
            programs_metrics = self._get_school_programs(
                funding_queryset, 
                disbursement_queryset, 
                school_id
            )
            
            # Add school data with program details
            schools_data.append({
                'school_id': school_id,
                'school_name': school['application__school__name'],
                'request_count': school['request_count'],
                'disbursed_count': school['disbursed_count'],
                'total_amount': school_amount_map.get(school_id, 0),
                'programs': programs_metrics
            })
        
        return {
            'schools': schools_data
        }
    
    def _get_school_programs(self, funding_queryset, disbursement_queryset, school_id):
        """
        Helper method to get program metrics for a specific school.
        
        Args:
            funding_queryset (QuerySet): Filtered funding request queryset
            disbursement_queryset (QuerySet): Filtered disbursement queryset
            school_id (UUID): School ID
            
        Returns:
            list: Program metrics for the school
        """
        # Filter to the specified school
        school_funding = funding_queryset.filter(application__school_id=school_id)
        
        # Group by program
        program_metrics = school_funding.values(
            'application__program_id',
            'application__program__name'
        ).annotate(
            request_count=Count('id'),
            disbursed_count=Count('id', filter=Q(status=FUNDING_REQUEST_STATUS['DISBURSED']))
        ).order_by('application__program__name')
        
        # Get disbursement amounts by program
        program_disbursements = disbursement_queryset.filter(
            status=DISBURSEMENT_STATUS['COMPLETED'],
            funding_request__application__school_id=school_id
        ).values('funding_request__application__program_id').annotate(
            total_amount=Sum('amount')
        )
        
        # Create a lookup for program disbursement amounts
        program_amount_map = {
            item['funding_request__application__program_id']: item['total_amount']
            for item in program_disbursements
        }
        
        # Prepare program metrics
        programs_data = []
        
        for program in program_metrics:
            program_id = program['application__program_id']
            
            programs_data.append({
                'program_id': program_id,
                'program_name': program['application__program__name'],
                'request_count': program['request_count'],
                'disbursed_count': program['disbursed_count'],
                'total_amount': program_amount_map.get(program_id, 0)
            })
        
        return programs_data
    
    def format_results(self, volume_metrics, status_distribution, time_trend, time_to_fund, school_program_breakdown):
        """
        Formats the report results into the required structure.
        
        Args:
            volume_metrics (dict): Disbursement volume metrics
            status_distribution (dict): Status distribution data
            time_trend (dict): Time-based trend data
            time_to_fund (dict): Time-to-fund metrics
            school_program_breakdown (dict): School and program breakdown data
            
        Returns:
            dict: Formatted report results
        """
        # Combine all sections into a single results dictionary
        results = {
            'metadata': {
                'generated_at': timezone.now().isoformat(),
                'report_type': self.report_type
            },
            'volume_metrics': volume_metrics,
            'status_distribution': status_distribution,
            'time_trend': time_trend,
            'school_program_breakdown': school_program_breakdown
        }
        
        # Add time-to-fund data if available
        if time_to_fund:
            results['time_to_fund'] = time_to_fund
        
        return results
    
    def generate_export_file(self, results, format='csv'):
        """
        Generates an export file (CSV/Excel) from the report data.
        
        Args:
            results (dict): Report results to export
            format (str): Export format ('csv' or 'xlsx')
            
        Returns:
            str: Path to the generated file
        """
        import uuid
        
        # Create a unique filename
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        filename = f"funding_metrics_{timestamp}_{uuid.uuid4()}.{format}"
        
        try:
            # Convert results to DataFrames
            dfs = {}
            
            # Volume metrics
            volume_df = pd.DataFrame([results['volume_metrics']])
            
            # Status distribution
            if 'by_category' in results['status_distribution']:
                status_df = pd.DataFrame(results['status_distribution']['by_category'])
            else:
                status_df = pd.DataFrame(results['status_distribution']['by_status'])
            
            # Time trend
            time_trend_df = pd.DataFrame(results['time_trend']['trend_data'])
            
            # Time to fund
            if 'time_to_fund' in results:
                # Basic metrics
                ttf_basic = {
                    'average_days': results['time_to_fund']['average_days'],
                    'median_days': results['time_to_fund']['median_days'],
                    'min_days': results['time_to_fund']['min_days'],
                    'max_days': results['time_to_fund']['max_days'],
                    'request_count': results['time_to_fund']['request_count']
                }
                time_to_fund_df = pd.DataFrame([ttf_basic])
                
                # Distribution
                if 'time_distribution' in results['time_to_fund']:
                    ttf_dist_df = pd.DataFrame(results['time_to_fund']['time_distribution'])
                    dfs['time_to_fund_distribution'] = ttf_dist_df
                
                dfs['time_to_fund'] = time_to_fund_df
            
            # School breakdown
            schools = []
            for school in results['school_program_breakdown']['schools']:
                schools.append({
                    'school_id': school['school_id'],
                    'school_name': school['school_name'],
                    'request_count': school['request_count'],
                    'disbursed_count': school['disbursed_count'],
                    'total_amount': school['total_amount']
                })
            schools_df = pd.DataFrame(schools)
            dfs['schools'] = schools_df
            
            # Program breakdown
            programs = []
            for school in results['school_program_breakdown']['schools']:
                for program in school['programs']:
                    programs.append({
                        'school_id': school['school_id'],
                        'school_name': school['school_name'],
                        'program_id': program['program_id'],
                        'program_name': program['program_name'],
                        'request_count': program['request_count'],
                        'disbursed_count': program['disbursed_count'],
                        'total_amount': program['total_amount']
                    })
            programs_df = pd.DataFrame(programs)
            dfs['programs'] = programs_df
            
            # Add main dataframes
            dfs['volume_metrics'] = volume_df
            dfs['status_distribution'] = status_df
            dfs['time_trend'] = time_trend_df
            
            # Generate file based on format
            from ...utils.storage import S3Storage
            
            # In a real implementation, we would:
            # 1. Create a temporary file
            # 2. Write the DataFrames to the file
            # 3. Upload to S3
            # 4. Return the S3 path
            
            # For now, we'll just return a simulated path
            file_path = f"reports/{filename}"
            
            return file_path
            
        except Exception as e:
            # Log the error
            print(f"Error generating export file: {str(e)}")
            return None