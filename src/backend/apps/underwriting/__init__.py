import logging  # version standard library

from .apps import UnderwritingConfig  # src/backend/apps/underwriting/apps.py
from .models import UnderwritingQueue, CreditInformation, UnderwritingDecision, DecisionReason, Stipulation, UnderwritingNote  # src/backend/apps/underwriting/models.py
from .services import UnderwritingService  # src/backend/apps/underwriting/services.py
from .rules import UnderwritingRuleEngine  # src/backend/apps/underwriting/rules.py
from .signals import connect_signals as connect_underwriting_signals  # src/backend/apps/underwriting/signals.py

# Initialize logger
logger = logging.getLogger(__name__)

default_app_config = 'src.backend.apps.underwriting.apps.UnderwritingConfig'
"""Specify the default Django app configuration for the underwriting app"""

# Call connect_underwriting_signals to register signal handlers for underwriting events
connect_underwriting_signals()

__all__ = [
    'default_app_config',
    'UnderwritingConfig',
    'UnderwritingQueue',
    'CreditInformation',
    'UnderwritingDecision',
    'DecisionReason',
    'Stipulation',
    'UnderwritingNote',
    'UnderwritingService',
    'UnderwritingRuleEngine',
]
"""
Exposes the following components for external use:
- default_app_config: Specifies the default Django app configuration for the underwriting app
- UnderwritingConfig: The Django app configuration class for the underwriting app
- UnderwritingQueue: The UnderwritingQueue model for managing the underwriting queue
    - assign_to_underwriter: Assigns an application to an underwriter
    - update_status: Updates the status of an application in the queue
    - is_overdue: Checks if an application is overdue for review
    - calculate_due_date: Calculates the due date for an application based on priority
- CreditInformation: The CreditInformation model for managing credit report data
    - get_download_url: Generates a download URL for the credit report
    - get_credit_tier: Determines the credit tier based on the credit score
- UnderwritingDecision: The UnderwritingDecision model for managing loan decisions
    - get_reasons: Retrieves the reasons for the underwriting decision
    - get_stipulations: Retrieves the stipulations associated with the underwriting decision
    - apply_decision: Applies the underwriting decision to the loan application
- DecisionReason: The DecisionReason model for tracking decision justifications
- Stipulation: The Stipulation model for managing loan conditions
    - mark_satisfied: Marks a stipulation as satisfied
    - mark_rejected: Marks a stipulation as rejected
    - mark_waived: Marks a stipulation as waived
    - is_overdue: Checks if a stipulation is overdue
- UnderwritingNote: The UnderwritingNote model for tracking underwriter notes
- UnderwritingService: The UnderwritingService class for underwriting business logic
    - get_queue: Retrieves the underwriting queue
    - add_to_queue: Adds an application to the underwriting queue
    - assign_application: Assigns an application to an underwriter
    - evaluate_application: Evaluates a loan application
    - create_decision: Creates an underwriting decision
- UnderwritingRuleEngine: The UnderwritingRuleEngine class for decision rule evaluation
    - evaluate_application: Evaluates a loan application
    - get_auto_decision: Gets an automatic underwriting decision
"""