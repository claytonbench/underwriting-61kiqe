"""
Implements the integration with DocuSign for e-signature collection in the loan management system.

This module provides a service class that handles all interactions with the DocuSign API,
including creating signature requests, tracking signature status, processing webhook events,
and downloading signed documents.
"""

import os
import json
import base64
import datetime
import uuid
import requests
import docusign_esign  # version 3.20.0+
from django.conf import settings  # version 4.2+
from django.db import transaction  # version 4.2+

from utils.logging import getLogger
from .models import Document, DocumentPackage, SignatureRequest, DocumentField
from .storage import DocumentStorage, document_storage
from .constants import (
    DOCUSIGN_ENVELOPE_STATUS_MAPPING,
    DOCUSIGN_RECIPIENT_STATUS_MAPPING,
    DOCUMENT_TYPES,
    SIGNATURE_STATUS,
    SIGNER_TYPES,
    DOCUMENT_SIGNING_SEQUENCE
)

# Configure logger
logger = getLogger('docusign')


class DocuSignError(Exception):
    """
    Custom exception class for DocuSign-related errors.
    """
    
    def __init__(self, message, original_exception=None):
        """
        Initialize the DocuSignError with a message and original exception.
        
        Args:
            message (str): Human-readable error message
            original_exception (Exception, optional): Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception
        logger.error(f"DocuSign error: {message}", exc_info=original_exception)
    
    def __str__(self):
        """
        Returns a string representation of the error.
        
        Returns:
            str: String representation of the error
        """
        if self.original_exception:
            return f"{self.message} (Original error: {str(self.original_exception)})"
        return self.message


class DocuSignService:
    """
    Service class that provides DocuSign e-signature functionality.
    
    This class encapsulates all interactions with the DocuSign API, handling authentication,
    signature requests, status tracking, and document retrieval.
    """
    
    def __init__(self):
        """
        Initialize the DocuSignService with configuration from settings.
        """
        try:
            # Get DocuSign configuration from settings
            self.base_url = settings.DOCUSIGN_BASE_URL
            self.oauth_host = settings.DOCUSIGN_OAUTH_HOST
            self.client_id = settings.DOCUSIGN_CLIENT_ID
            self.client_secret = settings.DOCUSIGN_CLIENT_SECRET
            self.redirect_uri = settings.DOCUSIGN_REDIRECT_URI
            self.private_key_path = settings.DOCUSIGN_PRIVATE_KEY_PATH
            self.user_id = settings.DOCUSIGN_USER_ID
            self.account_id = settings.DOCUSIGN_ACCOUNT_ID
            
            # Initialize API client with default values
            self.api_client = docusign_esign.ApiClient()
            self.api_client.host = self.base_url
            
            # Set up envelopes API
            self.envelopes_api = None
            
            # Initialize access token as None (will be set during authentication)
            self.access_token = None
            self.token_expiration = None
            
            logger.info("DocuSignService initialized successfully")
        except AttributeError as e:
            error_message = f"Missing DocuSign configuration setting: {str(e)}"
            logger.error(error_message)
            raise DocuSignError(error_message, e)
        except Exception as e:
            error_message = f"Error initializing DocuSignService: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocuSignError(error_message, e)
    
    def authenticate(self):
        """
        Authenticates with DocuSign API using JWT grant.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        try:
            # Check if current token is still valid
            if self.access_token and self.token_expiration and self.token_expiration > datetime.datetime.now():
                logger.debug("Using existing DocuSign access token")
                return True
            
            logger.info("Authenticating with DocuSign API using JWT grant")
            
            # Read private key
            with open(self.private_key_path, "r") as private_key_file:
                private_key = private_key_file.read()
            
            # Set up API client for authentication
            self.api_client = docusign_esign.ApiClient()
            self.api_client.host = self.oauth_host
            
            # Request access token using JWT grant
            response = self.api_client.request_jwt_user_token(
                client_id=self.client_id,
                user_id=self.user_id,
                oauth_host_name=self.oauth_host,
                private_key_bytes=private_key,
                expires_in=3600  # 1 hour
            )
            
            # Extract and store access token and expiration
            self.access_token = response.access_token
            expires_in = response.expires_in
            self.token_expiration = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
            
            # Configure API client with token
            self.api_client = docusign_esign.ApiClient()
            self.api_client.host = self.base_url
            self.api_client.set_default_header("Authorization", f"Bearer {self.access_token}")
            
            # Initialize envelopes API
            self.envelopes_api = docusign_esign.EnvelopesApi(self.api_client)
            
            logger.info("Successfully authenticated with DocuSign API")
            return True
        except docusign_esign.rest.ApiException as e:
            error_message = f"DocuSign API authentication error: {str(e)}"
            logger.error(error_message)
            raise DocuSignError(error_message, e)
        except Exception as e:
            error_message = f"Error authenticating with DocuSign: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocuSignError(error_message, e)
    
    def create_signature_request(self, document, signers, email_subject, email_body):
        """
        Creates a signature request for a document.
        
        Args:
            document (Document): The document to send for signature
            signers (list): List of dictionaries containing signer information
                           Each signer must have: user_id, name, email, signer_type
            email_subject (str): Subject line for the email sent to signers
            email_body (str): Email body content for the email sent to signers
            
        Returns:
            dict: Dictionary with envelope ID and other details
        """
        try:
            # Authenticate with DocuSign
            self.authenticate()
            
            # Get document content
            content = document.get_content()
            if not content:
                raise ValueError(f"Failed to retrieve content for document {document.id}")
            
            # Create envelope definition
            envelope_definition = docusign_esign.EnvelopeDefinition(
                email_subject=email_subject,
                email_blurb=email_body,
                status="sent"  # Send immediately
            )
            
            # Add document to envelope
            docusign_document = docusign_esign.Document(
                document_base64=base64.b64encode(content).decode('utf-8'),
                name=document.file_name,
                file_extension=document.file_name.split('.')[-1],
                document_id=str(document.id)
            )
            envelope_definition.documents = [docusign_document]
            
            # Add signers to envelope
            signing_sequence = DOCUMENT_SIGNING_SEQUENCE.get(document.document_type, [])
            if not signing_sequence:
                logger.warning(f"No signing sequence found for document type {document.document_type}, using default order")
                signing_sequence = [signer['signer_type'] for signer in signers]
            
            # Reorder signers based on signing sequence
            ordered_signers = []
            for signer_type in signing_sequence:
                for signer in signers:
                    if signer['signer_type'] == signer_type:
                        ordered_signers.append(signer)
                        break
            
            # Add remaining signers that weren't in the sequence
            for signer in signers:
                if signer not in ordered_signers:
                    ordered_signers.append(signer)
            
            # Create recipients
            docusign_signers = []
            for i, signer in enumerate(ordered_signers, start=1):
                # Get document fields for this signer
                document_fields = DocumentField.objects.filter(
                    document=document,
                    field_name__startswith=f"{signer['signer_type'].lower()}_"
                )
                
                # Create tabs for the signer
                tabs = self.create_recipient_tabs(document_fields, str(i))
                
                # Create signer
                docusign_signer = docusign_esign.Signer(
                    email=signer['email'],
                    name=signer['name'],
                    recipient_id=str(i),
                    routing_order=str(i),
                    client_user_id=str(signer['user_id']),
                    tabs=tabs
                )
                docusign_signers.append(docusign_signer)
            
            # Create recipients object
            recipients = docusign_esign.Recipients(signers=docusign_signers)
            envelope_definition.recipients = recipients
            
            # Send envelope
            envelope_summary = self.envelopes_api.create_envelope(
                account_id=self.account_id,
                envelope_definition=envelope_definition
            )
            
            # Extract relevant information
            envelope_id = envelope_summary.envelope_id
            
            # Create signature requests in database
            for i, signer in enumerate(ordered_signers, start=1):
                SignatureRequest.objects.create(
                    document=document,
                    signer_id=signer['user_id'],
                    signer_type=signer['signer_type'],
                    status=SIGNATURE_STATUS['SENT'],
                    requested_at=datetime.datetime.now(),
                    external_reference=f"{envelope_id}:{i}"
                )
            
            # Update document status
            document.status = 'sent'
            document.save()
            
            logger.info(f"Created signature request for document {document.id}, envelope ID: {envelope_id}")
            
            return {
                'envelope_id': envelope_id,
                'status': envelope_summary.status,
                'created': envelope_summary.created_date_time,
                'document_id': document.id
            }
        except docusign_esign.rest.ApiException as e:
            error_message = f"DocuSign API error creating signature request: {str(e)}"
            logger.error(error_message)
            raise DocuSignError(error_message, e)
        except Exception as e:
            error_message = f"Error creating signature request: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocuSignError(error_message, e)
    
    def create_signature_request_for_package(self, documents, signers, email_subject, email_body):
        """
        Creates a signature request for multiple documents in a package.
        
        Args:
            documents (list): List of Document objects to send for signature
            signers (list): List of dictionaries containing signer information
                           Each signer must have: user_id, name, email, signer_type
            email_subject (str): Subject line for the email sent to signers
            email_body (str): Email body content for the email sent to signers
            
        Returns:
            dict: Dictionary with envelope ID and other details
        """
        try:
            # Authenticate with DocuSign
            self.authenticate()
            
            # Create envelope definition
            envelope_definition = docusign_esign.EnvelopeDefinition(
                email_subject=email_subject,
                email_blurb=email_body,
                status="sent"  # Send immediately
            )
            
            # Add documents to envelope
            docusign_documents = []
            for i, document in enumerate(documents, start=1):
                # Get document content
                content = document.get_content()
                if not content:
                    raise ValueError(f"Failed to retrieve content for document {document.id}")
                
                docusign_document = docusign_esign.Document(
                    document_base64=base64.b64encode(content).decode('utf-8'),
                    name=document.file_name,
                    file_extension=document.file_name.split('.')[-1],
                    document_id=str(i)
                )
                docusign_documents.append(docusign_document)
            
            envelope_definition.documents = docusign_documents
            
            # Determine combined signing sequence
            signing_sequence = []
            for document in documents:
                doc_sequence = DOCUMENT_SIGNING_SEQUENCE.get(document.document_type, [])
                for signer_type in doc_sequence:
                    if signer_type not in signing_sequence:
                        signing_sequence.append(signer_type)
            
            if not signing_sequence:
                logger.warning(f"No signing sequence found for any document, using default order")
                signing_sequence = [signer['signer_type'] for signer in signers]
            
            # Reorder signers based on signing sequence
            ordered_signers = []
            for signer_type in signing_sequence:
                for signer in signers:
                    if signer['signer_type'] == signer_type and signer not in ordered_signers:
                        ordered_signers.append(signer)
            
            # Add remaining signers that weren't in the sequence
            for signer in signers:
                if signer not in ordered_signers:
                    ordered_signers.append(signer)
            
            # Create recipients
            docusign_signers = []
            for i, signer in enumerate(ordered_signers, start=1):
                # Collect tabs for this signer across all documents
                all_tabs = docusign_esign.Tabs()
                
                for j, document in enumerate(documents, start=1):
                    # Get document fields for this signer and document
                    document_fields = DocumentField.objects.filter(
                        document=document,
                        field_name__startswith=f"{signer['signer_type'].lower()}_"
                    )
                    
                    # Skip if no fields for this signer in this document
                    if not document_fields.exists():
                        continue
                    
                    # Create tabs for this document
                    document_tabs = self.create_recipient_tabs(document_fields, str(i), document_id=str(j))
                    
                    # Merge tabs into the signer's tabs
                    if hasattr(document_tabs, 'sign_here_tabs') and document_tabs.sign_here_tabs:
                        if not hasattr(all_tabs, 'sign_here_tabs') or not all_tabs.sign_here_tabs:
                            all_tabs.sign_here_tabs = []
                        all_tabs.sign_here_tabs.extend(document_tabs.sign_here_tabs)
                    
                    if hasattr(document_tabs, 'date_signed_tabs') and document_tabs.date_signed_tabs:
                        if not hasattr(all_tabs, 'date_signed_tabs') or not all_tabs.date_signed_tabs:
                            all_tabs.date_signed_tabs = []
                        all_tabs.date_signed_tabs.extend(document_tabs.date_signed_tabs)
                    
                    if hasattr(document_tabs, 'text_tabs') and document_tabs.text_tabs:
                        if not hasattr(all_tabs, 'text_tabs') or not all_tabs.text_tabs:
                            all_tabs.text_tabs = []
                        all_tabs.text_tabs.extend(document_tabs.text_tabs)
                    
                    if hasattr(document_tabs, 'checkbox_tabs') and document_tabs.checkbox_tabs:
                        if not hasattr(all_tabs, 'checkbox_tabs') or not all_tabs.checkbox_tabs:
                            all_tabs.checkbox_tabs = []
                        all_tabs.checkbox_tabs.extend(document_tabs.checkbox_tabs)
                    
                    if hasattr(document_tabs, 'initial_here_tabs') and document_tabs.initial_here_tabs:
                        if not hasattr(all_tabs, 'initial_here_tabs') or not all_tabs.initial_here_tabs:
                            all_tabs.initial_here_tabs = []
                        all_tabs.initial_here_tabs.extend(document_tabs.initial_here_tabs)
                
                # Create signer
                docusign_signer = docusign_esign.Signer(
                    email=signer['email'],
                    name=signer['name'],
                    recipient_id=str(i),
                    routing_order=str(i),
                    client_user_id=str(signer['user_id']),
                    tabs=all_tabs
                )
                docusign_signers.append(docusign_signer)
            
            # Create recipients object
            recipients = docusign_esign.Recipients(signers=docusign_signers)
            envelope_definition.recipients = recipients
            
            # Send envelope
            envelope_summary = self.envelopes_api.create_envelope(
                account_id=self.account_id,
                envelope_definition=envelope_definition
            )
            
            # Extract relevant information
            envelope_id = envelope_summary.envelope_id
            
            # Create signature requests in database
            for document in documents:
                for i, signer in enumerate(ordered_signers, start=1):
                    # Check if this signer should sign this document
                    doc_sequence = DOCUMENT_SIGNING_SEQUENCE.get(document.document_type, [])
                    if not doc_sequence or signer['signer_type'] in doc_sequence:
                        SignatureRequest.objects.create(
                            document=document,
                            signer_id=signer['user_id'],
                            signer_type=signer['signer_type'],
                            status=SIGNATURE_STATUS['SENT'],
                            requested_at=datetime.datetime.now(),
                            external_reference=f"{envelope_id}:{i}"
                        )
            
            # Update documents status
            for document in documents:
                document.status = 'sent'
                document.save()
            
            logger.info(f"Created signature request for {len(documents)} documents, envelope ID: {envelope_id}")
            
            return {
                'envelope_id': envelope_id,
                'status': envelope_summary.status,
                'created': envelope_summary.created_date_time,
                'document_ids': [doc.id for doc in documents]
            }
        except docusign_esign.rest.ApiException as e:
            error_message = f"DocuSign API error creating signature request for package: {str(e)}"
            logger.error(error_message)
            raise DocuSignError(error_message, e)
        except Exception as e:
            error_message = f"Error creating signature request for package: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocuSignError(error_message, e)
    
    def get_envelope_status(self, envelope_id):
        """
        Gets the status of a DocuSign envelope.
        
        Args:
            envelope_id (str): The envelope ID to check
            
        Returns:
            dict: Dictionary with envelope status details
        """
        try:
            # Authenticate with DocuSign
            self.authenticate()
            
            # Get envelope information
            envelope = self.envelopes_api.get_envelope(
                account_id=self.account_id,
                envelope_id=envelope_id
            )
            
            # Get recipients
            recipients = self.envelopes_api.list_recipients(
                account_id=self.account_id,
                envelope_id=envelope_id
            )
            
            # Map DocuSign status to internal status
            status = DOCUSIGN_ENVELOPE_STATUS_MAPPING.get(
                envelope.status.lower(),
                envelope.status.upper()
            )
            
            # Compile recipient information
            recipient_statuses = []
            if hasattr(recipients, 'signers') and recipients.signers:
                for signer in recipients.signers:
                    recipient_status = {
                        'recipient_id': signer.recipient_id,
                        'name': signer.name,
                        'email': signer.email,
                        'status': DOCUSIGN_RECIPIENT_STATUS_MAPPING.get(
                            signer.status.lower(),
                            signer.status.upper()
                        ),
                        'routing_order': signer.routing_order,
                        'delivered_date': signer.delivered_date_time,
                        'signed_date': signer.signed_date_time,
                    }
                    recipient_statuses.append(recipient_status)
            
            # Compile envelope status
            result = {
                'envelope_id': envelope.envelope_id,
                'status': status,
                'created_date': envelope.created_date_time,
                'sent_date': envelope.sent_date_time,
                'delivered_date': envelope.delivered_date_time,
                'completed_date': envelope.completed_date_time,
                'expired_date': envelope.expired_date_time,
                'recipients': recipient_statuses
            }
            
            logger.info(f"Retrieved status for envelope {envelope_id}: {status}")
            return result
        except docusign_esign.rest.ApiException as e:
            error_message = f"DocuSign API error getting envelope status: {str(e)}"
            logger.error(error_message)
            raise DocuSignError(error_message, e)
        except Exception as e:
            error_message = f"Error getting envelope status: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocuSignError(error_message, e)
    
    def get_recipient_status(self, envelope_id, recipient_id):
        """
        Gets the status of a specific recipient in an envelope.
        
        Args:
            envelope_id (str): The envelope ID
            recipient_id (str): The recipient ID
            
        Returns:
            dict: Dictionary with recipient status details
        """
        try:
            # Authenticate with DocuSign
            self.authenticate()
            
            # Get recipient information
            recipients = self.envelopes_api.list_recipients(
                account_id=self.account_id,
                envelope_id=envelope_id
            )
            
            # Find the specific recipient
            recipient = None
            if hasattr(recipients, 'signers') and recipients.signers:
                for signer in recipients.signers:
                    if signer.recipient_id == recipient_id:
                        recipient = signer
                        break
            
            if not recipient:
                raise ValueError(f"Recipient {recipient_id} not found in envelope {envelope_id}")
            
            # Map DocuSign status to internal status
            status = DOCUSIGN_RECIPIENT_STATUS_MAPPING.get(
                recipient.status.lower(),
                recipient.status.upper()
            )
            
            # Compile recipient status
            result = {
                'recipient_id': recipient.recipient_id,
                'name': recipient.name,
                'email': recipient.email,
                'status': status,
                'routing_order': recipient.routing_order,
                'delivered_date': recipient.delivered_date_time,
                'signed_date': recipient.signed_date_time,
            }
            
            logger.info(f"Retrieved status for recipient {recipient_id} in envelope {envelope_id}: {status}")
            return result
        except docusign_esign.rest.ApiException as e:
            error_message = f"DocuSign API error getting recipient status: {str(e)}"
            logger.error(error_message)
            raise DocuSignError(error_message, e)
        except Exception as e:
            error_message = f"Error getting recipient status: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocuSignError(error_message, e)
    
    def get_signature_status(self, document):
        """
        Gets the status of all signatures for a document.
        
        Args:
            document (Document): The document to check
            
        Returns:
            dict: Dictionary with signature status information
        """
        try:
            # Get all signature requests for this document
            signature_requests = SignatureRequest.objects.filter(document=document)
            
            if not signature_requests.exists():
                logger.warning(f"No signature requests found for document {document.id}")
                return {
                    'document_id': document.id,
                    'status': document.status,
                    'signatures': []
                }
            
            # Group signature requests by envelope ID
            envelope_requests = {}
            for request in signature_requests:
                if request.external_reference:
                    envelope_id, recipient_id = request.external_reference.split(':')
                    if envelope_id not in envelope_requests:
                        envelope_requests[envelope_id] = []
                    envelope_requests[envelope_id].append((request, recipient_id))
            
            # Get status for each envelope
            envelope_statuses = {}
            for envelope_id, requests in envelope_requests.items():
                try:
                    envelope_statuses[envelope_id] = self.get_envelope_status(envelope_id)
                except DocuSignError:
                    logger.warning(f"Could not get status for envelope {envelope_id}")
                    continue
            
            # Compile signature statuses
            signatures = []
            for envelope_id, requests in envelope_requests.items():
                if envelope_id not in envelope_statuses:
                    continue
                
                envelope_status = envelope_statuses[envelope_id]
                
                for request, recipient_id in requests:
                    # Find recipient status in envelope
                    recipient_status = None
                    for recipient in envelope_status['recipients']:
                        if recipient['recipient_id'] == recipient_id:
                            recipient_status = recipient
                            break
                    
                    if not recipient_status:
                        logger.warning(f"Recipient {recipient_id} not found in envelope {envelope_id}")
                        continue
                    
                    # Get signer information from SignatureRequest
                    signature = {
                        'signature_id': request.id,
                        'signer_id': request.signer_id,
                        'signer_type': request.signer_type,
                        'status': recipient_status['status'],
                        'requested_at': request.requested_at,
                        'completed_at': request.completed_at,
                        'envelope_id': envelope_id,
                        'recipient_id': recipient_id,
                        'delivered_date': recipient_status.get('delivered_date'),
                        'signed_date': recipient_status.get('signed_date')
                    }
                    
                    signatures.append(signature)
            
            # Determine overall document status based on signatures
            status = document.status
            if status == 'sent' and signatures:
                # Check if any signatures are completed
                if all(sig['status'] == SIGNATURE_STATUS['COMPLETED'] for sig in signatures):
                    status = 'completed'
                elif any(sig['status'] == SIGNATURE_STATUS['COMPLETED'] for sig in signatures):
                    status = 'partially_signed'
                        
                # Check if any signatures are declined
                if any(sig['status'] == SIGNATURE_STATUS['DECLINED'] for sig in signatures):
                    status = 'declined'
                
                # Check if envelope is expired
                if any(sig['status'] == SIGNATURE_STATUS['EXPIRED'] for sig in signatures):
                    status = 'expired'
            
            result = {
                'document_id': document.id,
                'status': status,
                'signatures': signatures
            }
            
            logger.info(f"Retrieved signature status for document {document.id}: {status}")
            return result
        except Exception as e:
            error_message = f"Error getting signature status for document {document.id}: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocuSignError(error_message, e)
    
    @transaction.atomic
    def update_signature_status(self, document):
        """
        Updates the status of signature requests based on DocuSign status.
        
        Args:
            document (Document): The document to update
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            # Get all signature requests for this document
            signature_requests = SignatureRequest.objects.filter(document=document)
            
            if not signature_requests.exists():
                logger.warning(f"No signature requests found for document {document.id}")
                return False
            
            # Group signature requests by envelope ID
            envelope_requests = {}
            for request in signature_requests:
                if request.external_reference:
                    envelope_id, recipient_id = request.external_reference.split(':')
                    if envelope_id not in envelope_requests:
                        envelope_requests[envelope_id] = []
                    envelope_requests[envelope_id].append((request, recipient_id))
            
            # Get status for each envelope
            for envelope_id, requests in envelope_requests.items():
                try:
                    envelope_status = self.get_envelope_status(envelope_id)
                    
                    # Update each signature request
                    for request, recipient_id in requests:
                        # Find recipient status in envelope
                        recipient_status = None
                        for recipient in envelope_status['recipients']:
                            if recipient['recipient_id'] == recipient_id:
                                recipient_status = recipient
                                break
                        
                        if not recipient_status:
                            logger.warning(f"Recipient {recipient_id} not found in envelope {envelope_id}")
                            continue
                        
                        # Update signature request status
                        new_status = recipient_status['status']
                        if request.status != new_status:
                            old_status = request.status
                            request.status = new_status
                            
                            # Set completed_at if status is COMPLETED
                            if new_status == SIGNATURE_STATUS['COMPLETED'] and not request.completed_at:
                                request.completed_at = datetime.datetime.now()
                            
                            request.save()
                            logger.info(f"Updated signature request {request.id} status from {old_status} to {new_status}")
                except Exception as e:
                    logger.error(f"Error updating status for envelope {envelope_id}: {str(e)}")
                    continue
            
            # Update document status based on signature statuses
            status_result = self.get_signature_status(document)
            if document.status != status_result['status']:
                document.status = status_result['status']
                document.save()
                logger.info(f"Updated document {document.id} status to {document.status}")
            
            return True
        except Exception as e:
            error_message = f"Error updating signature status for document {document.id}: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocuSignError(error_message, e)
    
    def process_webhook_event(self, webhook_data):
        """
        Processes webhook notifications from DocuSign.
        
        Args:
            webhook_data (dict): The webhook data from DocuSign
            
        Returns:
            dict: Dictionary with processing results
        """
        try:
            logger.info(f"Processing DocuSign webhook event")
            
            # Validate webhook data structure
            if 'event' not in webhook_data or 'data' not in webhook_data:
                raise ValueError("Invalid webhook data: missing 'event' or 'data'")
            
            event = webhook_data['event']
            data = webhook_data['data']
            
            if 'envelopeId' not in data:
                raise ValueError("Invalid webhook data: missing 'envelopeId'")
            
            envelope_id = data['envelopeId']
            logger.info(f"Processing DocuSign webhook event {event} for envelope {envelope_id}")
            
            # Get envelope status
            envelope_status = self.get_envelope_status(envelope_id)
            
            # Find signature requests associated with this envelope
            signature_requests = []
            for request in SignatureRequest.objects.all():
                if request.external_reference and request.external_reference.startswith(f"{envelope_id}:"):
                    signature_requests.append(request)
            
            if not signature_requests:
                logger.warning(f"No signature requests found for envelope {envelope_id}")
                return {
                    'status': 'warning',
                    'message': f"No signature requests found for envelope {envelope_id}",
                    'envelope_id': envelope_id,
                    'event': event
                }
            
            # Update signature requests based on envelope status
            updated_requests = []
            for request in signature_requests:
                envelope_id, recipient_id = request.external_reference.split(':')
                
                # Find recipient status in envelope
                recipient_status = None
                for recipient in envelope_status['recipients']:
                    if recipient['recipient_id'] == recipient_id:
                        recipient_status = recipient
                        break
                
                if not recipient_status:
                    logger.warning(f"Recipient {recipient_id} not found in envelope {envelope_id}")
                    continue
                
                # Update signature request status
                new_status = recipient_status['status']
                if request.status != new_status:
                    old_status = request.status
                    request.status = new_status
                    
                    # Set completed_at if status is COMPLETED
                    if new_status == SIGNATURE_STATUS['COMPLETED'] and not request.completed_at:
                        request.completed_at = datetime.datetime.now()
                    
                    request.save()
                    updated_requests.append({
                        'request_id': request.id,
                        'old_status': old_status,
                        'new_status': new_status
                    })
                    logger.info(f"Updated signature request {request.id} status from {old_status} to {new_status}")
            
            # Update document statuses based on signature statuses
            updated_documents = []
            documents = set(request.document for request in signature_requests)
            for document in documents:
                status_result = self.get_signature_status(document)
                if document.status != status_result['status']:
                    old_status = document.status
                    document.status = status_result['status']
                    document.save()
                    updated_documents.append({
                        'document_id': document.id,
                        'old_status': old_status,
                        'new_status': document.status
                    })
                    logger.info(f"Updated document {document.id} status from {old_status} to {document.status}")
            
            return {
                'status': 'success',
                'message': f"Processed webhook event {event} for envelope {envelope_id}",
                'envelope_id': envelope_id,
                'event': event,
                'updated_requests': updated_requests,
                'updated_documents': updated_documents
            }
        except docusign_esign.rest.ApiException as e:
            error_message = f"DocuSign API error processing webhook event: {str(e)}"
            logger.error(error_message)
            raise DocuSignError(error_message, e)
        except Exception as e:
            error_message = f"Error processing webhook event: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocuSignError(error_message, e)
    
    def download_signed_documents(self, envelope_id):
        """
        Downloads signed documents from a DocuSign envelope.
        
        Args:
            envelope_id (str): The envelope ID
            
        Returns:
            list: List of dictionaries with document content and metadata
        """
        try:
            # Authenticate with DocuSign
            self.authenticate()
            
            # Get envelope documents
            envelope_docs = self.envelopes_api.list_documents(
                account_id=self.account_id,
                envelope_id=envelope_id
            )
            
            # Download each document
            documents = []
            for doc in envelope_docs.envelope_documents:
                document_id = doc.document_id
                document_name = doc.name
                
                # Get document content
                document_content = self.envelopes_api.get_document(
                    account_id=self.account_id,
                    envelope_id=envelope_id,
                    document_id=document_id
                )
                
                documents.append({
                    'document_id': document_id,
                    'name': document_name,
                    'content': document_content,
                    'envelope_id': envelope_id
                })
            
            logger.info(f"Downloaded {len(documents)} documents from envelope {envelope_id}")
            return documents
        except docusign_esign.rest.ApiException as e:
            error_message = f"DocuSign API error downloading documents: {str(e)}"
            logger.error(error_message)
            raise DocuSignError(error_message, e)
        except Exception as e:
            error_message = f"Error downloading documents: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocuSignError(error_message, e)
    
    def download_signed_document(self, envelope_id, document_id):
        """
        Downloads a specific signed document from a DocuSign envelope.
        
        Args:
            envelope_id (str): The envelope ID
            document_id (str): The document ID
            
        Returns:
            dict: Dictionary with document content and metadata
        """
        try:
            # Authenticate with DocuSign
            self.authenticate()
            
            # Get envelope document list to get document name
            envelope_docs = self.envelopes_api.list_documents(
                account_id=self.account_id,
                envelope_id=envelope_id
            )
            
            # Find document name
            document_name = None
            for doc in envelope_docs.envelope_documents:
                if doc.document_id == document_id:
                    document_name = doc.name
                    break
            
            if not document_name:
                raise ValueError(f"Document {document_id} not found in envelope {envelope_id}")
            
            # Get document content
            document_content = self.envelopes_api.get_document(
                account_id=self.account_id,
                envelope_id=envelope_id,
                document_id=document_id
            )
            
            result = {
                'document_id': document_id,
                'name': document_name,
                'content': document_content,
                'envelope_id': envelope_id
            }
            
            logger.info(f"Downloaded document {document_id} from envelope {envelope_id}")
            return result
        except docusign_esign.rest.ApiException as e:
            error_message = f"DocuSign API error downloading document: {str(e)}"
            logger.error(error_message)
            raise DocuSignError(error_message, e)
        except Exception as e:
            error_message = f"Error downloading document: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocuSignError(error_message, e)
    
    def void_envelope(self, envelope_id, void_reason):
        """
        Voids (cancels) a DocuSign envelope.
        
        Args:
            envelope_id (str): The envelope ID to void
            void_reason (str): Reason for voiding the envelope
            
        Returns:
            bool: True if voiding was successful, False otherwise
        """
        try:
            # Authenticate with DocuSign
            self.authenticate()
            
            # Create void envelope request
            envelope = docusign_esign.Envelope(
                status="voided",
                voided_reason=void_reason
            )
            
            # Send void request
            self.envelopes_api.update(
                account_id=self.account_id,
                envelope_id=envelope_id,
                envelope=envelope
            )
            
            logger.info(f"Voided envelope {envelope_id} with reason: {void_reason}")
            
            # Update signature requests associated with this envelope
            for request in SignatureRequest.objects.all():
                if request.external_reference and request.external_reference.startswith(f"{envelope_id}:"):
                    request.status = SIGNATURE_STATUS['VOIDED']
                    request.save()
                    logger.info(f"Updated signature request {request.id} status to VOIDED")
            
            # Update document statuses
            documents = set(request.document for request in SignatureRequest.objects.filter(
                external_reference__startswith=f"{envelope_id}:"
            ))
            for document in documents:
                document.status = 'voided'
                document.save()
                logger.info(f"Updated document {document.id} status to voided")
            
            return True
        except docusign_esign.rest.ApiException as e:
            error_message = f"DocuSign API error voiding envelope: {str(e)}"
            logger.error(error_message)
            raise DocuSignError(error_message, e)
        except Exception as e:
            error_message = f"Error voiding envelope: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocuSignError(error_message, e)
    
    def create_embedded_signing_url(self, envelope_id, recipient_id, client_user_id, return_url):
        """
        Creates a URL for embedded signing experience.
        
        Args:
            envelope_id (str): The envelope ID
            recipient_id (str): The recipient ID
            client_user_id (str): The client user ID
            return_url (str): URL to redirect to after signing
            
        Returns:
            str: URL for embedded signing
        """
        try:
            # Authenticate with DocuSign
            self.authenticate()
            
            # Create recipient view request
            recipient_view_request = docusign_esign.RecipientViewRequest(
                authentication_method="None",
                client_user_id=client_user_id,
                recipient_id=recipient_id,
                return_url=return_url,
                user_name="Embedded Signer",
                email="signer@example.com"
            )
            
            # Get the recipient view URL
            results = self.envelopes_api.create_recipient_view(
                account_id=self.account_id,
                envelope_id=envelope_id,
                recipient_view_request=recipient_view_request
            )
            
            # Return the URL
            signing_url = results.url
            
            logger.info(f"Created embedded signing URL for envelope {envelope_id}, recipient {recipient_id}")
            return signing_url
        except docusign_esign.rest.ApiException as e:
            error_message = f"DocuSign API error creating embedded signing URL: {str(e)}"
            logger.error(error_message)
            raise DocuSignError(error_message, e)
        except Exception as e:
            error_message = f"Error creating embedded signing URL: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocuSignError(error_message, e)
    
    def create_recipient_tabs(self, document_fields, recipient_id, document_id=None):
        """
        Creates signature tabs (fields) for a recipient.
        
        Args:
            document_fields (QuerySet): QuerySet of DocumentField objects
            recipient_id (str): The recipient ID
            document_id (str, optional): The document ID (default: None)
            
        Returns:
            docusign_esign.Tabs: DocuSign tabs object
        """
        try:
            signature_tabs = []
            date_tabs = []
            text_tabs = []
            checkbox_tabs = []
            initial_tabs = []
            
            for field in document_fields:
                tab = field.to_docusign_tab()
                
                # Add recipient and document IDs
                tab['recipient_id'] = recipient_id
                if document_id:
                    tab['document_id'] = document_id
                
                # Add tab to appropriate list based on type
                if tab['tabType'] == 'signHereTab':
                    # Convert to DocuSign SignHere object
                    sign_tab = docusign_esign.SignHere(
                        document_id=tab['document_id'],
                        page_number=tab['pageNumber'],
                        recipient_id=tab['recipient_id'],
                        tab_label=tab.get('tabLabel', 'Sign Here'),
                        x_position=tab['xPosition'],
                        y_position=tab['yPosition']
                    )
                    signature_tabs.append(sign_tab)
                
                elif tab['tabType'] == 'dateSignedTab':
                    # Convert to DocuSign DateSigned object
                    date_tab = docusign_esign.DateSigned(
                        document_id=tab['document_id'],
                        page_number=tab['pageNumber'],
                        recipient_id=tab['recipient_id'],
                        tab_label=tab.get('tabLabel', 'Date'),
                        x_position=tab['xPosition'],
                        y_position=tab['yPosition']
                    )
                    date_tabs.append(date_tab)
                
                elif tab['tabType'] == 'textTab':
                    # Convert to DocuSign Text object
                    text_tab = docusign_esign.Text(
                        document_id=tab['document_id'],
                        page_number=tab['pageNumber'],
                        recipient_id=tab['recipient_id'],
                        tab_label=tab.get('tabLabel', 'Text'),
                        x_position=tab['xPosition'],
                        y_position=tab['yPosition'],
                        value=tab.get('value', '')
                    )
                    text_tabs.append(text_tab)
                
                elif tab['tabType'] == 'checkboxTab':
                    # Convert to DocuSign Checkbox object
                    checkbox_tab = docusign_esign.Checkbox(
                        document_id=tab['document_id'],
                        page_number=tab['pageNumber'],
                        recipient_id=tab['recipient_id'],
                        tab_label=tab.get('tabLabel', 'Checkbox'),
                        x_position=tab['xPosition'],
                        y_position=tab['yPosition'],
                        selected=tab.get('selected', False)
                    )
                    checkbox_tabs.append(checkbox_tab)
                
                elif tab['tabType'] == 'initialHereTab':
                    # Convert to DocuSign InitialHere object
                    initial_tab = docusign_esign.InitialHere(
                        document_id=tab['document_id'],
                        page_number=tab['pageNumber'],
                        recipient_id=tab['recipient_id'],
                        tab_label=tab.get('tabLabel', 'Initial'),
                        x_position=tab['xPosition'],
                        y_position=tab['yPosition']
                    )
                    initial_tabs.append(initial_tab)
            
            # Create Tabs object with all tab types
            tabs = docusign_esign.Tabs()
            
            if signature_tabs:
                tabs.sign_here_tabs = signature_tabs
            
            if date_tabs:
                tabs.date_signed_tabs = date_tabs
            
            if text_tabs:
                tabs.text_tabs = text_tabs
            
            if checkbox_tabs:
                tabs.checkbox_tabs = checkbox_tabs
            
            if initial_tabs:
                tabs.initial_here_tabs = initial_tabs
            
            return tabs
        except Exception as e:
            error_message = f"Error creating recipient tabs: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocuSignError(error_message, e)
    
    def validate_webhook_signature(self, webhook_data, signature):
        """
        Validates the signature of a DocuSign webhook.
        
        Args:
            webhook_data (dict): The webhook data
            signature (str): The signature to validate
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            import hmac
            import hashlib
            
            # Get webhook secret from settings
            webhook_secret = settings.DOCUSIGN_WEBHOOK_SECRET
            
            # Convert webhook data to JSON string
            data_string = json.dumps(webhook_data, separators=(',', ':'))
            
            # Compute the HMAC-SHA256 using the webhook secret
            computed_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                data_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare computed signature with provided signature
            is_valid = computed_signature == signature
            
            if is_valid:
                logger.info("DocuSign webhook signature validated successfully")
            else:
                logger.warning("DocuSign webhook signature validation failed")
            
            return is_valid
        except Exception as e:
            error_message = f"Error validating webhook signature: {str(e)}"
            logger.error(error_message, exc_info=True)
            return False


# Create singleton instance
docusign_service = DocuSignService()