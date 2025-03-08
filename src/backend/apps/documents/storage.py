"""
Document storage service for the loan management system.

This module provides a specialized wrapper around the S3Storage utility to handle
document storage, retrieval, versioning, and access management for loan-related
documents. It supports different document types with appropriate security measures.
"""

import os
import datetime
import uuid
from django.conf import settings

from utils.logging import getLogger
from utils.storage import S3Storage, StorageError
from .constants import DOCUMENT_OUTPUT_PATHS, DOCUMENT_TEMPLATE_PATHS

# Configure logger
logger = getLogger('document_storage')


class DocumentStorageError(Exception):
    """
    Custom exception class for document storage-related errors.
    
    This exception provides additional context for storage errors while
    preserving the original exception information.
    """
    
    def __init__(self, message, original_exception=None):
        """
        Initialize the DocumentStorageError with a message and original exception.
        
        Args:
            message (str): Human-readable error message
            original_exception (Exception, optional): Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception
        logger.error(f"Document storage error: {message}", exc_info=original_exception)
    
    def __str__(self):
        """Return a string representation of the error."""
        if self.original_exception:
            return f"{self.message} (Original error: {str(self.original_exception)})"
        return self.message


class DocumentStorage:
    """
    Class that provides document storage operations for the loan management system.
    
    This class wraps the S3Storage utility to provide specialized document handling
    with proper paths, versioning, and security controls for loan documents.
    """
    
    def __init__(self):
        """
        Initialize the DocumentStorage with S3 configuration from settings.
        
        Retrieves configuration from Django settings or environment variables.
        """
        self.bucket_name = getattr(settings, 'DOCUMENT_STORAGE_BUCKET', 
                                  os.environ.get('DOCUMENT_STORAGE_BUCKET'))
        if not self.bucket_name:
            raise ValueError("Document storage bucket name must be set in DOCUMENT_STORAGE_BUCKET setting or environment variable")
        
        self.region_name = getattr(settings, 'AWS_REGION', os.environ.get('AWS_REGION', 'us-east-1'))
        
        # Initialize the underlying S3 storage
        self.s3_storage = S3Storage(self.bucket_name, self.region_name)
        logger.info(f"Initialized DocumentStorage with bucket: {self.bucket_name}, region: {self.region_name}")
    
    def store_document(self, content, document_type, file_name=None, content_type=None, metadata=None):
        """
        Store a document in S3 with appropriate path based on document type.
        
        Args:
            content (bytes): Document content
            document_type (str): Type of document (e.g., 'loan_agreement', 'disclosure_form')
            file_name (str, optional): Name of the file (if not provided, one will be generated)
            content_type (str, optional): MIME type of the document
            metadata (dict, optional): Additional metadata to store with the document
            
        Returns:
            dict: Dictionary containing file path, version ID, and other storage details
            
        Raises:
            DocumentStorageError: If document storage fails
        """
        try:
            # Get the appropriate output path for this document type
            if document_type not in DOCUMENT_OUTPUT_PATHS:
                raise ValueError(f"Unknown document type: {document_type}")
                
            output_path = DOCUMENT_OUTPUT_PATHS[document_type]
            
            # Generate a unique file name if not provided
            if not file_name:
                file_extension = '.pdf'  # Default extension
                file_name = self.generate_file_name(None, file_extension)
            elif '.' not in file_name:
                file_name = f"{file_name}.pdf"  # Add default extension if none present
            
            # Construct the full S3 key (path + filename)
            file_path = os.path.join(output_path, file_name)
            
            # Store the document with encryption enabled
            result = self.s3_storage.store(
                file_obj=content,
                key=file_path,
                content_type=content_type,
                encrypt=True,  # Always encrypt documents
                metadata=metadata
            )
            
            # Add the file name to the result
            result['file_name'] = file_name
            
            logger.info(f"Successfully stored {document_type} document: {file_path}")
            return result
            
        except (ValueError, StorageError) as e:
            error_message = f"Failed to store {document_type} document: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocumentStorageError(error_message, e)
        except Exception as e:
            error_message = f"Unexpected error storing {document_type} document: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocumentStorageError(error_message, e)
    
    def store_template(self, content, template_type, file_name=None, content_type=None, metadata=None):
        """
        Store a document template in S3 with appropriate path.
        
        Args:
            content (bytes): Template content
            template_type (str): Type of template (e.g., 'loan_agreement', 'disclosure_form')
            file_name (str, optional): Name of the file (if not provided, one will be generated)
            content_type (str, optional): MIME type of the template
            metadata (dict, optional): Additional metadata to store with the template
            
        Returns:
            dict: Dictionary containing file path, version ID, and other storage details
            
        Raises:
            DocumentStorageError: If template storage fails
        """
        try:
            # Get the appropriate template path for this template type
            if template_type not in DOCUMENT_TEMPLATE_PATHS:
                raise ValueError(f"Unknown template type: {template_type}")
                
            template_base_path = os.path.dirname(DOCUMENT_TEMPLATE_PATHS[template_type])
            
            # Generate a unique file name if not provided
            if not file_name:
                # Extract extension from the original template path
                original_template = os.path.basename(DOCUMENT_TEMPLATE_PATHS[template_type])
                _, file_extension = os.path.splitext(original_template)
                file_name = self.generate_file_name(None, file_extension)
            elif '.' not in file_name:
                # Default to HTML for templates if no extension
                file_name = f"{file_name}.html"
            
            # Construct the full S3 key (path + filename)
            file_path = os.path.join(template_base_path, file_name)
            
            # Store the template
            result = self.s3_storage.store(
                file_obj=content,
                key=file_path,
                content_type=content_type,
                encrypt=True,  # Always encrypt templates
                metadata=metadata
            )
            
            # Add the file name to the result
            result['file_name'] = file_name
            
            logger.info(f"Successfully stored {template_type} template: {file_path}")
            return result
            
        except (ValueError, StorageError) as e:
            error_message = f"Failed to store {template_type} template: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocumentStorageError(error_message, e)
        except Exception as e:
            error_message = f"Unexpected error storing {template_type} template: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocumentStorageError(error_message, e)
    
    def retrieve_document(self, file_path, version_id=None):
        """
        Retrieve a document from S3 by its file path.
        
        Args:
            file_path (str): Path to the document in S3
            version_id (str, optional): Specific version of the document to retrieve
            
        Returns:
            tuple: (content, content_type, metadata) tuple
            
        Raises:
            DocumentStorageError: If document retrieval fails
        """
        try:
            content, content_type, metadata = self.s3_storage.retrieve(file_path, version_id)
            logger.info(f"Successfully retrieved document: {file_path}")
            return content, content_type, metadata
        except StorageError as e:
            error_message = f"Failed to retrieve document {file_path}: {str(e)}"
            logger.error(error_message)
            raise DocumentStorageError(error_message, e)
        except Exception as e:
            error_message = f"Unexpected error retrieving document {file_path}: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocumentStorageError(error_message, e)
    
    def delete_document(self, file_path, version_id=None):
        """
        Delete a document from S3 by its file path.
        
        Args:
            file_path (str): Path to the document in S3
            version_id (str, optional): Specific version of the document to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            DocumentStorageError: If document deletion fails
        """
        try:
            result = self.s3_storage.delete(file_path, version_id)
            logger.info(f"Successfully deleted document: {file_path}")
            return result
        except StorageError as e:
            error_message = f"Failed to delete document {file_path}: {str(e)}"
            logger.error(error_message)
            raise DocumentStorageError(error_message, e)
        except Exception as e:
            error_message = f"Unexpected error deleting document {file_path}: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocumentStorageError(error_message, e)
    
    def get_document_url(self, file_path, expiration=3600, version_id=None):
        """
        Generate a presigned URL for temporary access to a document.
        
        Args:
            file_path (str): Path to the document in S3
            expiration (int): URL expiration time in seconds (default: 3600 [1 hour])
            version_id (str, optional): Specific version of the document
            
        Returns:
            str: Presigned URL for the document
            
        Raises:
            DocumentStorageError: If URL generation fails
        """
        try:
            url = self.s3_storage.get_presigned_url(file_path, expiration, version_id)
            logger.info(f"Generated presigned URL for document {file_path} with expiration {expiration}s")
            return url
        except StorageError as e:
            error_message = f"Failed to generate presigned URL for document {file_path}: {str(e)}"
            logger.error(error_message)
            raise DocumentStorageError(error_message, e)
        except Exception as e:
            error_message = f"Unexpected error generating presigned URL for document {file_path}: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocumentStorageError(error_message, e)
    
    def get_document_versions(self, file_path):
        """
        Get all versions of a document in S3.
        
        Args:
            file_path (str): Path to the document in S3
            
        Returns:
            list: List of dictionaries containing version information
            
        Raises:
            DocumentStorageError: If version listing fails
        """
        try:
            versions = self.s3_storage.get_versions(file_path)
            logger.info(f"Retrieved {len(versions)} versions of document {file_path}")
            return versions
        except StorageError as e:
            error_message = f"Failed to get versions of document {file_path}: {str(e)}"
            logger.error(error_message)
            raise DocumentStorageError(error_message, e)
        except Exception as e:
            error_message = f"Unexpected error getting versions of document {file_path}: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocumentStorageError(error_message, e)
    
    def copy_document(self, source_path, destination_path, source_version_id=None):
        """
        Copy a document to a new location in S3.
        
        Args:
            source_path (str): Source document path
            destination_path (str): Destination document path
            source_version_id (str, optional): Specific version of the source document
            
        Returns:
            dict: Dictionary containing the new file path and version ID
            
        Raises:
            DocumentStorageError: If copy operation fails
        """
        try:
            result = self.s3_storage.copy(source_path, destination_path, source_version_id)
            logger.info(f"Successfully copied document from {source_path} to {destination_path}")
            return result
        except StorageError as e:
            error_message = f"Failed to copy document from {source_path} to {destination_path}: {str(e)}"
            logger.error(error_message)
            raise DocumentStorageError(error_message, e)
        except Exception as e:
            error_message = f"Unexpected error copying document from {source_path} to {destination_path}: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocumentStorageError(error_message, e)
    
    def generate_file_name(self, original_name=None, extension=None):
        """
        Generate a unique file name for a document.
        
        Args:
            original_name (str, optional): Original file name to derive extension from
            extension (str, optional): File extension (with dot, e.g. '.pdf')
            
        Returns:
            str: Generated file name
        """
        # If extension not provided, try to extract from original name
        if not extension and original_name:
            _, extension = os.path.splitext(original_name)
        
        # If still no extension, use default
        if not extension:
            extension = '.pdf'
        
        # Generate a timestamp and UUID for uniqueness
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4().hex[:8])
        
        # Construct and return the file name
        return f"{timestamp}_{unique_id}{extension}"