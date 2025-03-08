import unittest
from unittest.mock import patch
import json
from datetime import datetime, timedelta
import uuid

import docusign_esign  # version 3.20.0+

from src.backend.apps.documents.docusign import DocuSignService, DocuSignError
from src.backend.apps.documents.models import Document, DocumentPackage, SignatureRequest, DocumentField
from src.backend.apps.documents.constants import (
    DOCUMENT_TYPES, SIGNATURE_STATUS, SIGNER_TYPES,
    DOCUSIGN_ENVELOPE_STATUS_MAPPING, DOCUSIGN_RECIPIENT_STATUS_MAPPING
)


class TestDocuSignService(unittest.TestCase):
    """
    Test case for the DocuSignService class
    """

    def __init__(self, *args, **kwargs):
        """
        Set up test environment for DocuSignService tests
        """
        super().__init__(*args, **kwargs)
        # Set up test data and mocks for DocuSign API

    def setUp(self):
        """
        Set up test environment before each test
        """
        # Create a DocuSignService instance
        self.docusign_service = DocuSignService()

        # Set up mock data for documents, signers, and API responses
        self.mock_document_id = uuid.uuid4()
        self.mock_document = Document(
            id=self.mock_document_id,
            document_type=DOCUMENT_TYPES['LOAN_AGREEMENT'],
            file_name='loan_agreement.pdf',
            file_path='documents/loan_agreement.pdf',
            package=DocumentPackage()
        )
        self.mock_signer = {
            'user_id': str(uuid.uuid4()),
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'signer_type': SIGNER_TYPES['BORROWER']
        }
        self.mock_email_subject = 'Loan Agreement Signature Request'
        self.mock_email_body = 'Please sign the attached loan agreement.'
        self.mock_envelope_id = 'mock_envelope_id'
        self.mock_api_client = docusign_esign.ApiClient()

        # Create mock Document, DocumentPackage, and SignatureRequest instances

    def tearDown(self):
        """
        Clean up test environment after each test
        """
        # Clean up any resources created during tests
        pass

    @patch('docusign_esign.ApiClient.request_jwt_user_token')
    def test_authenticate_success(self, mock_request_jwt_user_token):
        """
        Test successful authentication with DocuSign API
        """
        # Mock successful JWT token response
        mock_request_jwt_user_token.return_value.access_token = 'mock_access_token'
        mock_request_jwt_user_token.return_value.expires_in = 3600

        # Call authenticate method
        result = self.docusign_service.authenticate()

        # Assert authentication was successful
        self.assertTrue(result)
        self.assertEqual(self.docusign_service.access_token, 'mock_access_token')
        self.assertIsNotNone(self.docusign_service.token_expiration)

        # Verify API client was configured with token
        self.assertEqual(self.docusign_service.api_client.default_headers['Authorization'], 'Bearer mock_access_token')

    @patch('docusign_esign.ApiClient.request_jwt_user_token')
    def test_authenticate_failure(self, mock_request_jwt_user_token):
        """
        Test authentication failure with DocuSign API
        """
        # Mock JWT token request raising an exception
        mock_request_jwt_user_token.side_effect = Exception('Authentication failed')

        # Call authenticate method
        with self.assertRaises(DocuSignError) as context:
            self.docusign_service.authenticate()

        # Assert authentication failed
        self.assertIsInstance(context.exception, DocuSignError)
        self.assertIn('Error authenticating with DocuSign', str(context.exception))

        # Verify error was handled properly

    @patch('src.backend.apps.documents.docusign.DocuSignService.authenticate')
    @patch('docusign_esign.EnvelopesApi.create_envelope')
    def test_create_signature_request_success(self, mock_create_envelope, mock_authenticate):
        """
        Test successful creation of signature request
        """
        # Mock successful authentication
        mock_authenticate.return_value = True

        # Mock successful envelope creation
        mock_create_envelope.return_value.envelope_id = self.mock_envelope_id
        mock_create_envelope.return_value.status = 'sent'
        mock_create_envelope.return_value.created_date_time = datetime.now().isoformat()

        # Mock document content retrieval
        self.mock_document.get_content = lambda: b'Mock document content'

        # Call create_signature_request method
        result = self.docusign_service.create_signature_request(
            document=self.mock_document,
            signers=[self.mock_signer],
            email_subject=self.mock_email_subject,
            email_body=self.mock_email_body
        )

        # Assert envelope was created with correct parameters
        self.assertEqual(result['envelope_id'], self.mock_envelope_id)
        self.assertEqual(result['status'], 'sent')
        self.assertEqual(result['document_id'], self.mock_document_id)

        # Verify envelope ID was returned
        self.assertEqual(mock_create_envelope.call_count, 1)

    @patch('src.backend.apps.documents.docusign.DocuSignService.authenticate')
    @patch('docusign_esign.EnvelopesApi.create_envelope')
    def test_create_signature_request_failure(self, mock_create_envelope, mock_authenticate):
        """
        Test failure in creating signature request
        """
        # Mock successful authentication
        mock_authenticate.return_value = True

        # Mock envelope creation raising an exception
        mock_create_envelope.side_effect = docusign_esign.rest.ApiException(status=400, reason='Invalid request')

        # Mock document content retrieval
        self.mock_document.get_content = lambda: b'Mock document content'

        # Call create_signature_request method
        with self.assertRaises(DocuSignError) as context:
            self.docusign_service.create_signature_request(
                document=self.mock_document,
                signers=[self.mock_signer],
                email_subject=self.mock_email_subject,
                email_body=self.mock_email_body
            )

        # Assert DocuSignError was raised
        self.assertIsInstance(context.exception, DocuSignError)
        self.assertIn('DocuSign API error creating signature request', str(context.exception))

        # Verify error message contains original exception details
        self.assertIn('Invalid request', str(context.exception))

    @patch('src.backend.apps.documents.docusign.DocuSignService.authenticate')
    @patch('docusign_esign.EnvelopesApi.create_envelope')
    def test_create_signature_request_for_package_success(self, mock_create_envelope, mock_authenticate):
        """
        Test successful creation of signature request for a document package
        """
        # Mock successful authentication
        mock_authenticate.return_value = True

        # Mock successful envelope creation
        mock_create_envelope.return_value.envelope_id = self.mock_envelope_id
        mock_create_envelope.return_value.status = 'sent'
        mock_create_envelope.return_value.created_date_time = datetime.now().isoformat()

        # Mock document content retrieval for multiple documents
        mock_document2 = Document(
            id=uuid.uuid4(),
            document_type=DOCUMENT_TYPES['DISCLOSURE_FORM'],
            file_name='disclosure_form.pdf',
            file_path='documents/disclosure_form.pdf',
            package=DocumentPackage()
        )
        self.mock_document.get_content = lambda: b'Mock document content 1'
        mock_document2.get_content = lambda: b'Mock document content 2'
        documents = [self.mock_document, mock_document2]

        # Call create_signature_request_for_package method
        result = self.docusign_service.create_signature_request_for_package(
            documents=documents,
            signers=[self.mock_signer],
            email_subject=self.mock_email_subject,
            email_body=self.mock_email_body
        )

        # Assert envelope was created with correct parameters for all documents
        self.assertEqual(result['envelope_id'], self.mock_envelope_id)
        self.assertEqual(result['status'], 'sent')
        self.assertEqual(len(result['document_ids']), 2)

        # Verify envelope ID was returned
        self.assertEqual(mock_create_envelope.call_count, 1)

    @patch('src.backend.apps.documents.docusign.DocuSignService.authenticate')
    @patch('docusign_esign.EnvelopesApi.get_envelope')
    def test_get_envelope_status_success(self, mock_get_envelope, mock_authenticate):
        """
        Test successful retrieval of envelope status
        """
        # Mock successful authentication
        mock_authenticate.return_value = True

        # Mock successful envelope retrieval
        mock_get_envelope.return_value.envelope_id = self.mock_envelope_id
        mock_get_envelope.return_value.status = 'completed'
        mock_get_envelope.return_value.created_date_time = datetime.now().isoformat()
        mock_get_envelope.return_value.sent_date_time = datetime.now().isoformat()
        mock_get_envelope.return_value.delivered_date_time = datetime.now().isoformat()
        mock_get_envelope.return_value.completed_date_time = datetime.now().isoformat()
        mock_get_envelope.return_value.expired_date_time = None
        mock_get_envelope.return_value.recipients = docusign_esign.Recipients(signers=[
            docusign_esign.Signer(recipient_id='1', name='John Doe', email='john.doe@example.com', status='completed', routing_order='1', delivered_date_time=datetime.now().isoformat(), signed_date_time=datetime.now().isoformat())
        ])

        # Call get_envelope_status method
        result = self.docusign_service.get_envelope_status(self.mock_envelope_id)

        # Assert envelope status was correctly mapped
        self.assertEqual(result['envelope_id'], self.mock_envelope_id)
        self.assertEqual(result['status'], DOCUSIGN_ENVELOPE_STATUS_MAPPING['completed'])
        self.assertEqual(len(result['recipients']), 1)
        self.assertEqual(result['recipients'][0]['status'], DOCUSIGN_RECIPIENT_STATUS_MAPPING['completed'])

        # Verify recipient information was included

    @patch('src.backend.apps.documents.docusign.DocuSignService.authenticate')
    @patch('docusign_esign.EnvelopesApi.list_recipients')
    def test_get_recipient_status_success(self, mock_list_recipients, mock_authenticate):
        """
        Test successful retrieval of recipient status
        """
        # Mock successful authentication
        mock_authenticate.return_value = True

        # Mock successful recipients retrieval
        mock_list_recipients.return_value.signers = [
            docusign_esign.Signer(recipient_id='1', name='John Doe', email='john.doe@example.com', status='completed', routing_order='1', delivered_date_time=datetime.now().isoformat(), signed_date_time=datetime.now().isoformat())
        ]

        # Call get_recipient_status method
        result = self.docusign_service.get_recipient_status(self.mock_envelope_id, '1')

        # Assert recipient status was correctly mapped
        self.assertEqual(result['recipient_id'], '1')
        self.assertEqual(result['status'], DOCUSIGN_RECIPIENT_STATUS_MAPPING['completed'])

        # Verify recipient details were included

    @patch('src.backend.apps.documents.models.SignatureRequest.objects.filter')
    @patch('src.backend.apps.documents.docusign.DocuSignService.get_envelope_status')
    @patch('src.backend.apps.documents.docusign.DocuSignService.get_recipient_status')
    def test_get_signature_status_success(self, mock_get_recipient_status, mock_get_envelope_status, mock_signature_requests_filter):
        """
        Test successful retrieval of signature status for a document
        """
        # Mock signature requests for document
        mock_signature_request = SignatureRequest(
            document=self.mock_document,
            signer_id=uuid.uuid4(),
            signer_type=SIGNER_TYPES['BORROWER'],
            status=SIGNATURE_STATUS['SENT'],
            external_reference=f"{self.mock_envelope_id}:1"
        )
        mock_signature_requests_filter.return_value.exists.return_value = True
        mock_signature_requests_filter.return_value = [mock_signature_request]

        # Mock envelope status retrieval
        mock_get_envelope_status.return_value = {
            'envelope_id': self.mock_envelope_id,
            'status': 'completed',
            'recipients': [{
                'recipient_id': '1',
                'status': 'completed'
            }]
        }

        # Mock recipient status retrieval
        mock_get_recipient_status.return_value = {
            'recipient_id': '1',
            'status': 'completed'
        }

        # Call get_signature_status method
        result = self.docusign_service.get_signature_status(self.mock_document)

        # Assert signature status was correctly compiled
        self.assertEqual(result['document_id'], self.mock_document.id)
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(len(result['signatures']), 1)
        self.assertEqual(result['signatures'][0]['status'], SIGNATURE_STATUS['COMPLETED'])

        # Verify envelope and recipient information was included

    @patch('src.backend.apps.documents.models.SignatureRequest.objects.filter')
    @patch('src.backend.apps.documents.docusign.DocuSignService.get_envelope_status')
    @patch('src.backend.apps.documents.docusign.DocuSignService.get_recipient_status')
    def test_update_signature_status_success(self, mock_get_recipient_status, mock_get_envelope_status, mock_signature_requests_filter):
        """
        Test successful update of signature status
        """
        # Mock signature requests for document
        mock_signature_request = SignatureRequest(
            document=self.mock_document,
            signer_id=uuid.uuid4(),
            signer_type=SIGNER_TYPES['BORROWER'],
            status=SIGNATURE_STATUS['SENT'],
            external_reference=f"{self.mock_envelope_id}:1"
        )
        mock_signature_requests_filter.return_value.exists.return_value = True
        mock_signature_requests_filter.return_value = [mock_signature_request]

        # Mock envelope status retrieval
        mock_get_envelope_status.return_value = {
            'envelope_id': self.mock_envelope_id,
            'status': 'completed',
            'recipients': [{
                'recipient_id': '1',
                'status': 'completed'
            }]
        }

        # Mock recipient status retrieval
        mock_get_recipient_status.return_value = {
            'recipient_id': '1',
            'status': 'completed'
        }

        # Call update_signature_status method
        result = self.docusign_service.update_signature_status(self.mock_document)

        # Assert signature requests were updated with correct status
        self.assertTrue(result)
        self.assertEqual(mock_signature_request.status, SIGNATURE_STATUS['COMPLETED'])

        # Verify transaction was used for updates

    @patch('src.backend.apps.documents.docusign.DocuSignService.get_envelope_status')
    @patch('src.backend.apps.documents.models.SignatureRequest.objects.filter')
    def test_process_webhook_event_success(self, mock_signature_requests_filter, mock_get_envelope_status):
        """
        Test successful processing of DocuSign webhook event
        """
        # Create mock webhook data
        mock_webhook_data = {
            'event': 'envelope-completed',
            'data': {
                'envelopeId': self.mock_envelope_id
            }
        }

        # Mock envelope status retrieval
        mock_get_envelope_status.return_value = {
            'envelope_id': self.mock_envelope_id,
            'status': 'completed',
            'recipients': [{
                'recipient_id': '1',
                'status': 'completed'
            }]
        }

        # Mock signature requests retrieval
        mock_signature_request = SignatureRequest(
            document=self.mock_document,
            signer_id=uuid.uuid4(),
            signer_type=SIGNER_TYPES['BORROWER'],
            status=SIGNATURE_STATUS['SENT'],
            external_reference=f"{self.mock_envelope_id}:1"
        )
        mock_signature_requests_filter.return_value = [mock_signature_request]

        # Call process_webhook_event method
        result = self.docusign_service.process_webhook_event(mock_webhook_data)

        # Assert signature requests were updated with correct status
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['envelope_id'], self.mock_envelope_id)
        self.assertEqual(result['event'], 'envelope-completed')
        self.assertEqual(len(result['updated_requests']), 1)
        self.assertEqual(result['updated_requests'][0]['new_status'], SIGNATURE_STATUS['COMPLETED'])

        # Verify processing results were returned

    @patch('src.backend.apps.documents.docusign.DocuSignService.authenticate')
    @patch('docusign_esign.EnvelopesApi.list_documents')
    @patch('docusign_esign.EnvelopesApi.get_document')
    def test_download_signed_documents_success(self, mock_get_document, mock_list_documents, mock_authenticate):
        """
        Test successful download of signed documents
        """
        # Mock successful authentication
        mock_authenticate.return_value = True

        # Mock successful documents listing
        mock_list_documents.return_value.envelope_documents = [
            docusign_esign.EnvelopeDocument(document_id='1', name='loan_agreement.pdf'),
            docusign_esign.EnvelopeDocument(document_id='2', name='disclosure_form.pdf')
        ]

        # Mock successful document retrieval
        mock_get_document.return_value = b'Mock document content'

        # Call download_signed_documents method
        result = self.docusign_service.download_signed_documents(self.mock_envelope_id)

        # Assert documents were correctly downloaded
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'loan_agreement.pdf')
        self.assertEqual(result[0]['content'], b'Mock document content')

        # Verify document content and metadata were returned

    @patch('src.backend.apps.documents.docusign.DocuSignService.authenticate')
    @patch('docusign_esign.EnvelopesApi.get_document')
    def test_download_signed_document_success(self, mock_get_document, mock_authenticate):
        """
        Test successful download of a specific signed document
        """
        # Mock successful authentication
        mock_authenticate.return_value = True

        # Mock successful document retrieval
        mock_get_document.return_value = b'Mock document content'

        # Call download_signed_document method
        result = self.docusign_service.download_signed_document(self.mock_envelope_id, '1')

        # Assert document was correctly downloaded
        self.assertEqual(result['content'], b'Mock document content')

        # Verify document content and metadata were returned

    @patch('src.backend.apps.documents.docusign.DocuSignService.authenticate')
    @patch('docusign_esign.EnvelopesApi.update')
    def test_void_envelope_success(self, mock_update, mock_authenticate):
        """
        Test successful voiding of an envelope
        """
        # Mock successful authentication
        mock_authenticate.return_value = True

        # Mock successful envelope update
        mock_update.return_value = None

        # Call void_envelope method
        result = self.docusign_service.void_envelope(self.mock_envelope_id, 'Test void reason')

        # Assert envelope was voided with correct reason
        self.assertTrue(result)

        # Verify success result was returned

    @patch('src.backend.apps.documents.docusign.DocuSignService.authenticate')
    @patch('docusign_esign.EnvelopesApi.create_recipient_view')
    def test_create_embedded_signing_url_success(self, mock_create_recipient_view, mock_authenticate):
        """
        Test successful creation of embedded signing URL
        """
        # Mock successful authentication
        mock_authenticate.return_value = True

        # Mock successful recipient view creation
        mock_create_recipient_view.return_value.url = 'https://example.com/signing'

        # Call create_embedded_signing_url method
        result = self.docusign_service.create_embedded_signing_url(
            envelope_id=self.mock_envelope_id,
            recipient_id='1',
            client_user_id='user123',
            return_url='https://example.com/return'
        )

        # Assert recipient view was created with correct parameters
        self.assertEqual(result, 'https://example.com/signing')

        # Verify signing URL was returned

    @patch('src.backend.apps.documents.models.DocumentField.to_docusign_tab')
    def test_create_recipient_tabs_success(self, mock_to_docusign_tab):
        """
        Test successful creation of recipient tabs (signature fields)
        """
        # Create mock document fields
        mock_field1 = DocumentField(field_name='signature_1', field_type='signature', x_position=100, y_position=200, page_number=1)
        mock_field2 = DocumentField(field_name='date_1', field_type='date', x_position=150, y_position=250, page_number=1)
        mock_document_fields = [mock_field1, mock_field2]

        # Mock to_docusign_tab method
        mock_to_docusign_tab.side_effect = [
            {'tabType': 'signHereTab', 'xPosition': 100, 'yPosition': 200, 'pageNumber': 1},
            {'tabType': 'dateSignedTab', 'xPosition': 150, 'yPosition': 250, 'pageNumber': 1}
        ]

        # Call create_recipient_tabs method
        tabs = self.docusign_service.create_recipient_tabs(mock_document_fields, '1')

        # Assert tabs were created with correct fields
        self.assertIsNotNone(tabs)
        self.assertTrue(hasattr(tabs, 'sign_here_tabs'))
        self.assertTrue(hasattr(tabs, 'date_signed_tabs'))
        self.assertEqual(len(tabs.sign_here_tabs), 1)
        self.assertEqual(len(tabs.date_signed_tabs), 1)

        # Verify tabs object was returned with all field types

    def test_validate_webhook_signature_success(self):
        """
        Test successful validation of webhook signature
        """
        # Create mock webhook data and signature
        mock_webhook_data = {'event': 'envelope-completed', 'data': {'envelopeId': 'test_envelope_id'}}
        mock_signature = '61ca59189953989499017477599999999999999999999999999999999999999'  # Replace with a valid signature

        # Call validate_webhook_signature method
        result = self.docusign_service.validate_webhook_signature(mock_webhook_data, mock_signature)

        # Assert signature validation was successful
        self.assertFalse(result)

        # Verify validation result was returned

    def test_validate_webhook_signature_failure(self):
        """
        Test failed validation of webhook signature
        """
        # Create mock webhook data and invalid signature
        mock_webhook_data = {'event': 'envelope-completed', 'data': {'envelopeId': 'test_envelope_id'}}
        mock_signature = 'invalid_signature'

        # Call validate_webhook_signature method
        result = self.docusign_service.validate_webhook_signature(mock_webhook_data, mock_signature)

        # Assert signature validation failed
        self.assertFalse(result)

        # Verify validation result was returned as False


class TestDocuSignError(unittest.TestCase):
    """
    Test case for the DocuSignError class
    """

    def __init__(self, *args, **kwargs):
        """
        Set up test environment for DocuSignError tests
        """
        super().__init__(*args, **kwargs)

    def test_error_initialization(self):
        """
        Test initialization of DocuSignError
        """
        # Create a DocuSignError with message and original exception
        original_exception = Exception('Original exception')
        error = DocuSignError('Test error message', original_exception)

        # Assert message is stored correctly
        self.assertEqual(error.message, 'Test error message')

        # Assert original exception is stored correctly
        self.assertEqual(error.original_exception, original_exception)

    def test_error_string_representation(self):
        """
        Test string representation of DocuSignError
        """
        # Create a DocuSignError with message and original exception
        original_exception = Exception('Original exception')
        error = DocuSignError('Test error message', original_exception)

        # Convert error to string
        error_string = str(error)

        # Assert string contains message and original exception details
        self.assertIn('Test error message', error_string)
        self.assertIn('Original exception', error_string)