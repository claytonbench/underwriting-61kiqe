# src/backend/apps/reporting/reports/underwriting_metrics.py
"""
Implements the UnderwritingMetricsReport class for generating reports on loan underwriting metrics.
This report provides insights into approval rates, decision trends, processing times, and stipulation metrics
to support business analytics and operational monitoring of the underwriting process.
"""

import json  # standard library
from datetime import datetime  # standard library

import pandas  # version 2.1+
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Min, Max, Q  # Django 4.2+
from django.db.models.functions import Trunc  # Django 4.2+
from django.utils import timezone  # Django 4.2+

from apps.applications.models import ApplicationStatusHistory, LoanApplication  # Import the LoanApplication model for querying application data
from apps.reporting.models import SavedReport  # Import the SavedReport model for storing report results
from apps.underwriting.models import (  # Import the UnderwritingQueue model for queue metrics
    CreditInformation,  # Import the CreditInformation model for credit metrics
    DecisionReason,  # Import the DecisionReason model for tracking denial reasons
    Stipulation,  # Import the Stipulation model for stipulation metrics
    UnderwritingDecision,  # Import the UnderwritingDecision model for decision data
    UnderwritingQueue,
)
from utils.constants import UNDERWRITING_DECISION  # Import underwriting decision constants for report categorization

DEFAULT_PARAMETERS = {
    'date_range': {'start_date': 'None', 'end_date': 'None'},
    'school_id': 'None',
    'program_id': 'None',
    'underwriter_id': 'None',
    'group_by': '"decision"',
    'time_interval': '"day"',
    'include_credit_metrics': 'True',
    'include_stipulation_metrics': 'True',
}

DECISION_GROUPS = {
    'approved': [UNDERWRITING_DECISION['APPROVE']],
    'denied': [UNDERWRITING_DECISION['DENY']],
    'revision': [UNDERWRITING_DECISION['REVISE']],
}

TIME_INTERVALS = ['day', 'week', 'month', 'quarter', 'year']

SLA_TARGET_HOURS = 48


class UnderwritingMetricsReport:
    """
    Report generator for underwriting metrics, providing insights into approval rates, decision trends,
    processing times, and stipulation metrics
    """

    report_type = 'underwriting_metrics'

    def __init__(self):
        """Initialize the UnderwritingMetricsReport with default values"""
        pass

    def validate_parameters(self, parameters):
        """
        Validates the report parameters before generation

        Args:
            parameters (dict): Report parameters

        Returns:
            tuple: Tuple containing (is_valid, error_message)
        """
        time_interval = parameters.get('time_interval')
        if time_interval and time_interval not in TIME_INTERVALS:
            return False, f"Invalid time interval: {time_interval}. Must be one of {TIME_INTERVALS}"

        start_date = parameters.get('date_range', {}).get('start_date')
        end_date = parameters.get('date_range', {}).get('end_date')

        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                if start > end:
                    return False, "Start date must be before end date"
            except ValueError:
                return False, "Invalid date format. Use YYYY-MM-DD"

        school_id = parameters.get('school_id')
        if school_id and not LoanApplication.objects.filter(school_id=school_id).exists():
            return False, f"Invalid school ID: {school_id}"

        program_id = parameters.get('program_id')
        if program_id and not LoanApplication.objects.filter(program_id=program_id).exists():
            return False, f"Invalid program ID: {program_id}"

        underwriter_id = parameters.get('underwriter_id')
        if underwriter_id and not UnderwritingDecision.objects.filter(underwriter_id=underwriter_id).exists():
            return False, f"Invalid underwriter ID: {underwriter_id}"

        return True, None

    def prepare_parameters(self, parameters):
        """
        Prepares and normalizes the report parameters

        Args:
            parameters (dict): Report parameters

        Returns:
            dict: Normalized parameters with defaults applied
        """
        prepared_params = DEFAULT_PARAMETERS.copy()
        prepared_params.update(parameters)

        # Set default date range if not provided (last 30 days)
        if prepared_params['date_range']['start_date'] == 'None' or prepared_params['date_range']['end_date'] == 'None':
            end_date = timezone.now().date()
            start_date = end_date - timezone.timedelta(days=30)
            prepared_params['date_range']['start_date'] = start_date.strftime('%Y-%m-%d')
            prepared_params['date_range']['end_date'] = end_date.strftime('%Y-%m-%d')

        # Convert string dates to datetime objects
        start_date_str = prepared_params['date_range']['start_date']
        end_date_str = prepared_params['date_range']['end_date']

        prepared_params['date_range']['start_date'] = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        prepared_params['date_range']['end_date'] = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        return prepared_params

    def generate(self, report, parameters):
        """
        Generates the underwriting metrics report based on the provided parameters

        Args:
            report (SavedReport): The report instance to update
            parameters (dict): Report parameters

        Returns:
            bool: True if report generation was successful, False otherwise
        """
        report.update_status('GENERATING')

        is_valid, error_message = self.validate_parameters(parameters)
        if not is_valid:
            report.set_error(error_message)
            return False

        prepared_params = self.prepare_parameters(parameters)

        # Build base queryset for UnderwritingDecision
        queryset = UnderwritingDecision.objects.filter(is_deleted=False)

        # Apply date range filter
        start_date = prepared_params['date_range']['start_date']
        end_date = prepared_params['date_range']['end_date']
        queryset = queryset.filter(decision_date__date__range=[start_date, end_date])

        # Apply school filter
        school_id = prepared_params.get('school_id')
        if school_id and school_id != 'None':
            queryset = queryset.filter(application__school_id=school_id)

        # Apply program filter
        program_id = prepared_params.get('program_id')
        if program_id and program_id != 'None':
            queryset = queryset.filter(application__program_id=program_id)

        # Apply underwriter filter
        underwriter_id = prepared_params.get('underwriter_id')
        if underwriter_id and underwriter_id != 'None':
            queryset = queryset.filter(underwriter_id=underwriter_id)

        # Generate decision metrics
        decision_metrics = self.get_decision_metrics(queryset, prepared_params)

        # Generate time trend data
        time_trend = self.get_time_trend(queryset, prepared_params)

        # Generate processing time metrics
        processing_time_metrics = self.get_processing_time_metrics(queryset, prepared_params)

        # Generate credit metrics if requested
        credit_metrics = {}
        if prepared_params.get('include_credit_metrics') == 'True':
            credit_metrics = self.get_credit_metrics(queryset, prepared_params)

        # Generate stipulation metrics if requested
        stipulation_metrics = {}
        if prepared_params.get('include_stipulation_metrics') == 'True':
            stipulation_metrics = self.get_stipulation_metrics(queryset, prepared_params)

        # Generate denial reason metrics
        denial_reason_metrics = self.get_denial_reason_metrics(queryset, prepared_params)

        # Generate underwriter performance metrics
        underwriter_performance = self.get_underwriter_performance(queryset, prepared_params)

        # Generate school program breakdown
        school_program_breakdown = self.get_school_program_breakdown(queryset, prepared_params)

        # Format results
        results = self.format_results(
            decision_metrics, time_trend, processing_time_metrics,
            credit_metrics, stipulation_metrics, denial_reason_metrics,
            underwriter_performance, school_program_breakdown
        )

        # Generate export file (CSV/Excel) if requested
        file_path = None
        # file_format = parameters.get('export_format')
        # if file_format:
        #     file_path = self.generate_export_file(results, file_format)

        # Update report with results and file path
        report.set_results(results, file_path=file_path)

        return True

    def get_decision_metrics(self, queryset, parameters):
        """
        Calculates metrics related to underwriting decisions

        Args:
            queryset (QuerySet): Base queryset for UnderwritingDecision
            parameters (dict): Report parameters

        Returns:
            dict: Decision metrics including approval rate, denial rate, and revision rate
        """
        total_decisions = queryset.count()
        approved_count = queryset.filter(decision=UNDERWRITING_DECISION['APPROVE']).count()
        denied_count = queryset.filter(decision=UNDERWRITING_DECISION['DENY']).count()
        revision_count = queryset.filter(decision=UNDERWRITING_DECISION['REVISE']).count()

        approval_rate = (approved_count / total_decisions) * 100 if total_decisions else 0
        denial_rate = (denied_count / total_decisions) * 100 if total_decisions else 0
        revision_rate = (revision_count / total_decisions) * 100 if total_decisions else 0

        # Calculate metrics for previous period for comparison
        start_date = parameters['date_range']['start_date']
        end_date = parameters['date_range']['end_date']
        time_delta = end_date - start_date
        previous_start_date = start_date - time_delta
        previous_end_date = start_date - timezone.timedelta(days=1)

        previous_queryset = UnderwritingDecision.objects.filter(
            decision_date__date__range=[previous_start_date, previous_end_date]
        )
        previous_total_decisions = previous_queryset.count()
        previous_approved_count = previous_queryset.filter(decision=UNDERWRITING_DECISION['APPROVE']).count()
        previous_denial_count = previous_queryset.filter(decision=UNDERWRITING_DECISION['DENY']).count()
        previous_revision_count = previous_queryset.filter(decision=UNDERWRITING_DECISION['REVISE']).count()

        previous_approval_rate = (previous_approved_count / previous_total_decisions) * 100 if previous_total_decisions else 0
        previous_denial_rate = (previous_denial_count / previous_total_decisions) * 100 if previous_total_decisions else 0
        previous_revision_rate = (previous_revision_count / previous_total_decisions) * 100 if previous_total_decisions else 0

        # Calculate growth/decline percentages
        approval_rate_change = approval_rate - previous_approval_rate
        denial_rate_change = denial_rate - previous_denial_rate
        revision_rate_change = revision_rate - previous_revision_rate

        return {
            'total_decisions': total_decisions,
            'approval_count': approved_count,
            'denial_count': denied_count,
            'revision_count': revision_count,
            'approval_rate': approval_rate,
            'denial_rate': denial_rate,
            'revision_rate': revision_rate,
            'approval_rate_change': approval_rate_change,
            'denial_rate_change': denial_rate_change,
            'revision_rate_change': revision_rate_change,
        }

    def get_time_trend(self, queryset, parameters):
        """
        Generates time-based trend data for underwriting decisions

        Args:
            queryset (QuerySet): Base queryset for UnderwritingDecision
            parameters (dict): Report parameters

        Returns:
            dict: Time-based trend data for decisions
        """
        time_interval = parameters.get('time_interval', 'day')

        # Truncate the decision_date to the specified time interval
        truncated_date = Trunc('decision_date', time_interval, output_field=models.DateTimeField())

        # Annotate the queryset with the truncated date and count decisions
        trend_data = queryset.annotate(time=truncated_date).values('time').annotate(
            total=Count('id'),
            approved=Count('id', filter=Q(decision=UNDERWRITING_DECISION['APPROVE'])),
            denied=Count('id', filter=Q(decision=UNDERWRITING_DECISION['DENY'])),
            revision=Count('id', filter=Q(decision=UNDERWRITING_DECISION['REVISE']))
        ).order_by('time')

        # Calculate approval rate for each interval
        trend = []
        for item in trend_data:
            total = item['total']
            approved = item['approved']
            approval_rate = (approved / total) * 100 if total else 0
            trend.append({
                'time': item['time'].strftime('%Y-%m-%d %H:%M:%S'),
                'total': total,
                'approved': approved,
                'denied': item['denied'],
                'revision': item['revision'],
                'approval_rate': approval_rate,
            })

        return {'trend': trend}

    def get_processing_time_metrics(self, queryset, parameters):
        """
        Calculates metrics for underwriting processing times

        Args:
            queryset (QuerySet): Base queryset for UnderwritingDecision
            parameters (dict): Report parameters

        Returns:
            dict: Processing time metrics
        """
        # Join with ApplicationStatusHistory to track status changes
        queryset = queryset.annotate(
            submission_time=Min('application__statushistory__changed_at', filter=Q(
                application__statushistory__new_status='submitted')),
        )

        # Calculate time from submission to decision
        queryset = queryset.annotate(
            processing_time=ExpressionWrapper(
                F('decision_date') - F('submission_time'),
                output_field=DurationField()
            )
        )

        # Calculate time in underwriting queue
        queryset = queryset.annotate(
            queue_time=ExpressionWrapper(
                F('decision_date') - F('application__underwriting_queue_entries__assignment_date'),
                output_field=DurationField()
            )
        )

        # Calculate average, median, min, and max processing times
        avg_processing_time = queryset.aggregate(avg=Avg('processing_time'))['avg']
        min_processing_time = queryset.aggregate(min=Min('processing_time'))['min']
        max_processing_time = queryset.aggregate(max=Max('processing_time'))['max']

        # Calculate SLA compliance percentage (decisions within target hours)
        sla_compliant_count = queryset.filter(processing_time__lte=timezone.timedelta(hours=SLA_TARGET_HOURS)).count()
        sla_compliance_percentage = (sla_compliant_count / queryset.count()) * 100 if queryset.count() else 0

        # Group processing times by decision type
        processing_times_by_decision = queryset.values('decision').annotate(
            avg_time=Avg('processing_time')
        )

        return {
            'average_processing_time': avg_processing_time.total_seconds() / 3600 if avg_processing_time else None,
            'minimum_processing_time': min_processing_time.total_seconds() / 3600 if min_processing_time else None,
            'maximum_processing_time': max_processing_time.total_seconds() / 3600 if max_processing_time else None,
            'sla_compliance_percentage': sla_compliance_percentage,
            'processing_times_by_decision': list(processing_times_by_decision)
        }

    def get_credit_metrics(self, queryset, parameters):
        """
        Calculates metrics related to credit scores and decisions

        Args:
            queryset (QuerySet): Base queryset for UnderwritingDecision
            parameters (dict): Report parameters

        Returns:
            dict: Credit metrics including approval rates by credit score range
        """
        # Join with CreditInformation to get credit scores
        queryset = queryset.annotate(credit_score=F('application__credit_information__credit_score'))

        # Group credit scores into ranges (excellent, good, fair, poor)
        credit_score_ranges = {
            'excellent': Q(credit_score__gte=750),
            'good': Q(credit_score__range=(700, 749)),
            'fair': Q(credit_score__range=(650, 699)),
            'poor': Q(credit_score__lt=650),
        }

        # Calculate approval rate for each credit score range
        approval_rates_by_credit_score = {}
        for range_name, score_range in credit_score_ranges.items():
            total_in_range = queryset.filter(score_range).count()
            approved_in_range = queryset.filter(score_range, decision=UNDERWRITING_DECISION['APPROVE']).count()
            approval_rate = (approved_in_range / total_in_range) * 100 if total_in_range else 0
            approval_rates_by_credit_score[range_name] = approval_rate

        # Calculate average credit score for approved vs. denied applications
        avg_credit_score_approved = queryset.filter(decision=UNDERWRITING_DECISION['APPROVE']).aggregate(
            avg_score=Avg('credit_score'))['avg_score'] or 0
        avg_credit_score_denied = queryset.filter(decision=UNDERWRITING_DECISION['DENY']).aggregate(
            avg_score=Avg('credit_score'))['avg_score'] or 0

        # Calculate average debt-to-income ratio for approved vs. denied applications
        avg_dti_approved = queryset.filter(decision=UNDERWRITING_DECISION['APPROVE']).aggregate(
            avg_dti=Avg('application__credit_information__debt_to_income_ratio'))['avg_dti'] or 0
        avg_dti_denied = queryset.filter(decision=UNDERWRITING_DECISION['DENY']).aggregate(
            avg_dti=Avg('application__credit_information__debt_to_income_ratio'))['avg_dti'] or 0

        return {
            'approval_rates_by_credit_score': approval_rates_by_credit_score,
            'average_credit_score_approved': avg_credit_score_approved,
            'average_credit_score_denied': avg_credit_score_denied,
            'average_dti_approved': avg_dti_approved,
            'average_dti_denied': avg_dti_denied,
        }

    def get_stipulation_metrics(self, queryset, parameters):
        """
        Calculates metrics related to stipulations in underwriting decisions

        Args:
            queryset (QuerySet): Base queryset for UnderwritingDecision
            parameters (dict): Report parameters

        Returns:
            dict: Stipulation metrics
        """
        # Join with Stipulation to get stipulation data
        queryset = queryset.annotate(stipulation_count=Count('application__stipulations'))

        # Calculate average stipulations per approved application
        avg_stipulations_per_approved = queryset.filter(decision=UNDERWRITING_DECISION['APPROVE']).aggregate(
            avg_stipulations=Avg('stipulation_count'))['avg_stipulations'] or 0

        # Group stipulations by type
        stipulations_by_type = Stipulation.objects.filter(application__underwriting_decision__in=queryset).values(
            'stipulation_type').annotate(count=Count('id'))

        # Calculate satisfaction rate for stipulations
        total_stipulations = Stipulation.objects.filter(application__underwriting_decision__in=queryset).count()
        satisfied_stipulations = Stipulation.objects.filter(
            application__underwriting_decision__in=queryset, status='satisfied').count()
        satisfaction_rate = (satisfied_stipulations / total_stipulations) * 100 if total_stipulations else 0

        # Calculate average time to satisfy stipulations
        # This requires more complex logic and potentially custom SQL
        # For now, we'll leave it as a placeholder

        return {
            'average_stipulations_per_approved': avg_stipulations_per_approved,
            'stipulations_by_type': list(stipulations_by_type),
            'stipulation_satisfaction_rate': satisfaction_rate,
            'average_time_to_satisfy': None,  # Placeholder
        }

    def get_denial_reason_metrics(self, queryset, parameters):
        """
        Calculates metrics related to denial reasons

        Args:
            queryset (QuerySet): Base queryset for UnderwritingDecision
            parameters (dict): Report parameters

        Returns:
            dict: Denial reason metrics
        """
        # Filter queryset for denied applications
        denied_queryset = queryset.filter(decision=UNDERWRITING_DECISION['DENY'])

        # Join with DecisionReason to get denial reasons
        denial_reasons = denied_queryset.values('reasons__reason_code').annotate(count=Count('id'))

        # Calculate total denials
        total_denials = denied_queryset.count()

        # Calculate percentage for each reason code
        denial_reason_metrics = []
        for reason in denial_reasons:
            reason_code = reason['reasons__reason_code']
            count = reason['count']
            percentage = (count / total_denials) * 100 if total_denials else 0
            denial_reason_metrics.append({
                'reason_code': reason_code,
                'count': count,
                'percentage': percentage,
            })

        return {
            'denial_reason_metrics': denial_reason_metrics,
        }

    def get_underwriter_performance(self, queryset, parameters):
        """
        Calculates performance metrics for underwriters

        Args:
            queryset (QuerySet): Base queryset for UnderwritingDecision
            parameters (dict): Report parameters

        Returns:
            dict: Underwriter performance metrics
        """
        # Group decisions by underwriter
        underwriter_data = queryset.values('underwriter').annotate(
            total_decisions=Count('id'),
            approved_decisions=Count('id', filter=Q(decision=UNDERWRITING_DECISION['APPROVE'])),
        )

        # Calculate total decisions, approval rate, and average processing time per underwriter
        underwriter_performance = []
        for underwriter in underwriter_data:
            total_decisions = underwriter['total_decisions']
            approved_decisions = underwriter['approved_decisions']
            approval_rate = (approved_decisions / total_decisions) * 100 if total_decisions else 0

            # Calculate average processing time per underwriter
            # This requires more complex logic and potentially custom SQL
            # For now, we'll leave it as a placeholder

            underwriter_performance.append({
                'underwriter_id': underwriter['underwriter'],
                'total_decisions': total_decisions,
                'approval_rate': approval_rate,
                'average_processing_time': None,  # Placeholder
                'sla_compliance_percentage': None,  # Placeholder
            })

        return {
            'underwriter_performance': underwriter_performance,
        }

    def get_school_program_breakdown(self, queryset, parameters):
        """
        Breaks down underwriting metrics by school and program

        Args:
            queryset (QuerySet): Base queryset for UnderwritingDecision
            parameters (dict): Report parameters

        Returns:
            dict: School and program breakdown data
        """
        # Group decisions by school
        school_data = queryset.values('application__school__name').annotate(
            total_decisions=Count('id'),
            approved_decisions=Count('id', filter=Q(decision=UNDERWRITING_DECISION['APPROVE'])),
        )

        # For each school, group by program
        school_program_breakdown = []
        for school in school_data:
            school_name = school['application__school__name']
            total_decisions = school['total_decisions']
            approved_decisions = school['approved_decisions']
            approval_rate = (approved_decisions / total_decisions) * 100 if total_decisions else 0

            # Group by program within each school
            program_data = queryset.filter(application__school__name=school_name).values(
                'application__program__name').annotate(
                program_total=Count('id'),
                program_approved=Count('id', filter=Q(decision=UNDERWRITING_DECISION['APPROVE']))
            )

            program_breakdown = []
            for program in program_data:
                program_name = program['application__program__name']
                program_total = program['program_total']
                program_approved = program['program_approved']
                program_approval_rate = (program_approved / program_total) * 100 if program_total else 0

                program_breakdown.append({
                    'program_name': program_name,
                    'program_total': program_total,
                    'program_approved': program_approved,
                    'program_approval_rate': program_approval_rate,
                })

            school_program_breakdown.append({
                'school_name': school_name,
                'total_decisions': total_decisions,
                'approved_decisions': approved_decisions,
                'approval_rate': approval_rate,
                'program_breakdown': program_breakdown,
            })

        return {
            'school_program_breakdown': school_program_breakdown,
        }

    def format_results(self, decision_metrics, time_trend, processing_time_metrics,
                       credit_metrics, stipulation_metrics, denial_reason_metrics,
                       underwriter_performance, school_program_breakdown):
        """
        Formats the report results into the required structure

        Args:
            decision_metrics (dict): Decision metrics
            time_trend (dict): Time-based trend data
            processing_time_metrics (dict): Processing time metrics
            credit_metrics (dict): Credit metrics
            stipulation_metrics (dict): Stipulation metrics
            denial_reason_metrics (dict): Denial reason metrics
            underwriter_performance (dict): Underwriter performance metrics
            school_program_breakdown (dict): School and program breakdown data

        Returns:
            dict: Formatted report results
        """
        results = {
            'decision_metrics': decision_metrics,
            'time_trend': time_trend,
            'processing_time_metrics': processing_time_metrics,
            'credit_metrics': credit_metrics,
            'stipulation_metrics': stipulation_metrics,
            'denial_reason_metrics': denial_reason_metrics,
            'underwriter_performance': underwriter_performance,
            'school_program_breakdown': school_program_breakdown,
            'generation_time': datetime.now().isoformat(),
            'parameters_used': self.prepare_parameters,
        }

        return results

    def generate_export_file(self, results, format):
        """
        Generates an export file (CSV/Excel) from the report data

        Args:
            results (dict): Report data
            format (str): Export format (CSV/Excel)

        Returns:
            str: Path to the generated file
        """
        # Convert results to pandas DataFrame
        df = pandas.DataFrame(results)

        # Format the data appropriately for export
        # (e.g., format dates, numbers, etc.)

        # Generate file in the requested format (CSV/Excel)
        if format == 'csv':
            file_path = '/tmp/report.csv'  # Temporary location
            df.to_csv(file_path)
        elif format == 'excel':
            file_path = '/tmp/report.xlsx'  # Temporary location
            df.to_excel(file_path)
        else:
            raise ValueError(f"Unsupported export format: {format}")

        # Save to temporary location

        # Upload to S3 storage
        # s3_storage = S3Storage()
        # s3_storage.store(file_path, 'reports/report.csv')

        # Return the file path
        return file_path