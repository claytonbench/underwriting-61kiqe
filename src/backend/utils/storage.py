"""
Utility module for document storage operations using AWS S3.

This module provides a unified interface for document storage, retrieval, and management
in the loan management system. It supports secure storage with encryption, versioning,
and temporary access via presigned URLs.
"""

import boto3  # version 1.26.0+
import os
from datetime import datetime
import uuid
from botocore.exceptions import ClientError
from utils.logging import getLogger

# Configure logger
logger = getLogger('storage')


class StorageError(Exception):
    """
    Custom exception class for storage-related errors.
    
    This exception encapsulates original AWS exceptions to provide more context
    while maintaining the original error information.
    """
    
    def __init__(self, message, original_exception=None):
        """
        Initialize a StorageError with a message and optional original exception.
        
        Args:
            message (str): Human-readable error message
            original_exception (Exception, optional): Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception
        logger.error(f"Storage error: {message}", exc_info=original_exception)
    
    def __str__(self):
        """Return string representation of the error."""
        if self.original_exception:
            return f"{self.message} (Original error: {str(self.original_exception)})"
        return self.message


def generate_presigned_url(bucket_name, object_key, expiration=3600, region_name=None, version_id=None):
    """
    Generate a presigned URL for temporary access to a document in S3.
    
    Args:
        bucket_name (str): Name of the S3 bucket
        object_key (str): Key of the object in the bucket
        expiration (int): URL expiration time in seconds (default: 3600)
        region_name (str): AWS region name (default: None, using default region)
        version_id (str): Specific version of the object (default: None, latest version)
        
    Returns:
        str: Presigned URL for temporary access to the object
        
    Raises:
        StorageError: If URL generation fails
    """
    try:
        s3_client = boto3.client('s3', region_name=region_name)
        params = {
            'Bucket': bucket_name,
            'Key': object_key,
            'ExpiresIn': expiration
        }
        
        if version_id:
            params['VersionId'] = version_id
            
        url = s3_client.generate_presigned_url('get_object', Params=params)
        logger.debug(f"Generated presigned URL for {object_key} with expiration {expiration}s")
        return url
    except ClientError as e:
        error_message = f"Failed to generate presigned URL for {object_key}: {str(e)}"
        logger.error(error_message)
        raise StorageError(error_message, e)


class S3Storage:
    """
    Class providing a unified interface for S3 storage operations.
    
    This class implements methods for storing, retrieving, and managing documents in S3,
    with support for versioning, encryption, and access control.
    """
    
    def __init__(self, bucket_name=None, region_name=None):
        """
        Initialize the S3Storage with AWS credentials and configuration.
        
        Args:
            bucket_name (str): Name of the S3 bucket (default: from environment)
            region_name (str): AWS region name (default: from environment or 'us-east-1')
        """
        self.bucket_name = bucket_name or os.environ.get('S3_BUCKET_NAME')
        if not self.bucket_name:
            raise ValueError("S3 bucket name must be provided or set in S3_BUCKET_NAME environment variable")
            
        self.region_name = region_name or os.environ.get('AWS_REGION', 'us-east-1')
        
        try:
            self.s3_client = boto3.client('s3', region_name=self.region_name)
            logger.info(f"Initialized S3Storage with bucket: {self.bucket_name}, region: {self.region_name}")
        except ClientError as e:
            error_message = f"Failed to initialize S3 client: {str(e)}"
            logger.error(error_message)
            raise StorageError(error_message, e)
    
    def store(self, file_obj, key, content_type=None, encrypt=True, metadata=None):
        """
        Store a file in S3 with optional encryption and metadata.
        
        Args:
            file_obj: File-like object or bytes to store
            key (str): Object key (path) in S3
            content_type (str): MIME type of the file (default: None, auto-detected)
            encrypt (bool): Whether to encrypt the file (default: True)
            metadata (dict): Additional metadata to store with the file (default: None)
            
        Returns:
            dict: Dictionary containing object key, URL, and version ID
            
        Raises:
            StorageError: If file storage fails
        """
        try:
            params = {
                'Bucket': self.bucket_name,
                'Key': key,
                'Body': file_obj
            }
            
            if content_type:
                params['ContentType'] = content_type
                
            if metadata:
                params['Metadata'] = metadata
                
            if encrypt:
                params['ServerSideEncryption'] = 'AES256'
                
            response = self.s3_client.put_object(**params)
            
            result = {
                'key': key,
                'url': f"s3://{self.bucket_name}/{key}",
                'version_id': response.get('VersionId')
            }
            
            logger.info(f"Successfully stored object {key} in bucket {self.bucket_name}")
            return result
        except ClientError as e:
            error_message = f"Failed to store object {key} in bucket {self.bucket_name}: {str(e)}"
            logger.error(error_message)
            raise StorageError(error_message, e)
    
    def retrieve(self, key, version_id=None):
        """
        Retrieve a file from S3 by its key.
        
        Args:
            key (str): Object key (path) in S3
            version_id (str): Specific version of the object (default: None, latest version)
            
        Returns:
            tuple: (file_content, content_type, metadata) tuple
            
        Raises:
            StorageError: If file retrieval fails
        """
        try:
            params = {
                'Bucket': self.bucket_name,
                'Key': key
            }
            
            if version_id:
                params['VersionId'] = version_id
                
            response = self.s3_client.get_object(**params)
            
            content = response['Body'].read()
            content_type = response.get('ContentType')
            metadata = response.get('Metadata', {})
            
            logger.info(f"Successfully retrieved object {key} from bucket {self.bucket_name}")
            return content, content_type, metadata
        except ClientError as e:
            error_message = f"Failed to retrieve object {key} from bucket {self.bucket_name}: {str(e)}"
            logger.error(error_message)
            raise StorageError(error_message, e)
    
    def delete(self, key, version_id=None):
        """
        Delete a file from S3 by its key.
        
        Args:
            key (str): Object key (path) in S3
            version_id (str): Specific version to delete (default: None, latest version)
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            StorageError: If file deletion fails
        """
        try:
            params = {
                'Bucket': self.bucket_name,
                'Key': key
            }
            
            if version_id:
                params['VersionId'] = version_id
                
            self.s3_client.delete_object(**params)
            
            logger.info(f"Successfully deleted object {key} from bucket {self.bucket_name}")
            return True
        except ClientError as e:
            error_message = f"Failed to delete object {key} from bucket {self.bucket_name}: {str(e)}"
            logger.error(error_message)
            raise StorageError(error_message, e)
    
    def get_presigned_url(self, key, expiration=3600, version_id=None):
        """
        Generate a presigned URL for temporary access to a file.
        
        Args:
            key (str): Object key (path) in S3
            expiration (int): URL expiration time in seconds (default: 3600)
            version_id (str): Specific version of the object (default: None, latest version)
            
        Returns:
            str: Presigned URL for temporary access to the file
            
        Raises:
            StorageError: If URL generation fails
        """
        try:
            return generate_presigned_url(
                self.bucket_name, 
                key, 
                expiration=expiration, 
                region_name=self.region_name,
                version_id=version_id
            )
        except StorageError as e:
            # Re-raise the original error
            raise e
        except Exception as e:
            error_message = f"Failed to generate presigned URL for {key}: {str(e)}"
            logger.error(error_message)
            raise StorageError(error_message, e)
    
    def list(self, prefix=None, max_items=1000):
        """
        List objects in S3 with an optional prefix.
        
        Args:
            prefix (str): Prefix to filter objects (default: None, list all)
            max_items (int): Maximum number of items to return (default: 1000)
            
        Returns:
            list: List of dictionaries containing object keys and metadata
            
        Raises:
            StorageError: If listing fails
        """
        try:
            params = {
                'Bucket': self.bucket_name,
                'MaxKeys': max_items
            }
            
            if prefix:
                params['Prefix'] = prefix
                
            response = self.s3_client.list_objects_v2(**params)
            
            result = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    result.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'etag': obj['ETag'].strip('"'),
                        'storage_class': obj.get('StorageClass')
                    })
            
            logger.info(f"Listed {len(result)} objects with prefix '{prefix}' in bucket {self.bucket_name}")
            return result
        except ClientError as e:
            error_message = f"Failed to list objects in bucket {self.bucket_name}: {str(e)}"
            logger.error(error_message)
            raise StorageError(error_message, e)
    
    def get_versions(self, key):
        """
        Get all versions of an object in S3.
        
        Args:
            key (str): Object key (path) in S3
            
        Returns:
            list: List of dictionaries containing version information
            
        Raises:
            StorageError: If version listing fails
        """
        try:
            response = self.s3_client.list_object_versions(
                Bucket=self.bucket_name,
                Prefix=key
            )
            
            versions = []
            if 'Versions' in response:
                for version in response['Versions']:
                    if version['Key'] == key:
                        versions.append({
                            'version_id': version['VersionId'],
                            'last_modified': version['LastModified'].isoformat(),
                            'is_latest': version['IsLatest'],
                            'size': version['Size'],
                            'etag': version['ETag'].strip('"')
                        })
            
            logger.info(f"Retrieved {len(versions)} versions of object {key} from bucket {self.bucket_name}")
            return versions
        except ClientError as e:
            error_message = f"Failed to get versions of object {key} from bucket {self.bucket_name}: {str(e)}"
            logger.error(error_message)
            raise StorageError(error_message, e)
    
    def copy(self, source_key, destination_key, source_version_id=None):
        """
        Copy an object to a new location in S3.
        
        Args:
            source_key (str): Source object key
            destination_key (str): Destination object key
            source_version_id (str): Specific version to copy (default: None, latest version)
            
        Returns:
            dict: Dictionary containing new object key and version ID
            
        Raises:
            StorageError: If copy operation fails
        """
        try:
            source = {
                'Bucket': self.bucket_name,
                'Key': source_key
            }
            
            if source_version_id:
                source['VersionId'] = source_version_id
                
            response = self.s3_client.copy_object(
                CopySource=source,
                Bucket=self.bucket_name,
                Key=destination_key
            )
            
            result = {
                'key': destination_key,
                'version_id': response.get('VersionId')
            }
            
            logger.info(f"Successfully copied object from {source_key} to {destination_key} in bucket {self.bucket_name}")
            return result
        except ClientError as e:
            error_message = f"Failed to copy object from {source_key} to {destination_key} in bucket {self.bucket_name}: {str(e)}"
            logger.error(error_message)
            raise StorageError(error_message, e)