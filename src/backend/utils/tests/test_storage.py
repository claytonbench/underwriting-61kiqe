"""
Unit tests for the storage utility module that provides S3 storage operations for the loan management system.
Tests cover file storage, retrieval, deletion, presigned URL generation, and error handling.
"""

import pytest  # version 7.3.1
from unittest.mock import patch, MagicMock, Mock  # version standard library
import io  # version standard library
from datetime import datetime
from botocore.exceptions import ClientError  # version 1.29.0+

from utils.storage import S3Storage, StorageError, generate_presigned_url


class TestS3Storage:
    """Test class for the S3Storage utility"""
    
    def setup_method(self, method):
        """Set up method that runs before each test"""
        # Create mock S3 client
        self.mock_s3_client = MagicMock()
        
        # Patch boto3.client to return our mock
        self.patcher = patch('boto3.client', return_value=self.mock_s3_client)
        self.mock_boto3_client = self.patcher.start()
        
        # Initialize S3Storage with test bucket and region
        self.bucket_name = 'test-bucket'
        self.region_name = 'us-east-1'
        self.storage = S3Storage(
            bucket_name=self.bucket_name,
            region_name=self.region_name
        )
        
        # Set up common test data
        self.test_key = 'test/document.pdf'
        self.test_content = b'Test file content'
        self.test_file = io.BytesIO(self.test_content)
        self.test_content_type = 'application/pdf'
        self.test_metadata = {'owner': 'test-user', 'application_id': 'APP-123'}
        self.test_version_id = 'test-version-id'
    
    def teardown_method(self, method):
        """Tear down method that runs after each test"""
        # Stop the patcher
        self.patcher.stop()
    
    def test_init(self):
        """Test S3Storage initialization"""
        # Test initialization with provided bucket and region
        assert self.storage.bucket_name == self.bucket_name
        assert self.storage.region_name == self.region_name
        assert self.storage.s3_client == self.mock_s3_client
        
        # Verify boto3.client was called with correct parameters
        self.mock_boto3_client.assert_called_once_with(
            's3', region_name=self.region_name
        )
        
        # Test initialization with ValueError when bucket_name is not provided
        with patch('os.environ.get', return_value=None):
            with pytest.raises(ValueError):
                S3Storage()
    
    def test_store(self):
        """Test storing a file in S3"""
        # Mock the S3 client response
        self.mock_s3_client.put_object.return_value = {
            'VersionId': self.test_version_id
        }
        
        # Call store method
        result = self.storage.store(
            self.test_file,
            self.test_key,
            content_type=self.test_content_type,
            encrypt=True,
            metadata=self.test_metadata
        )
        
        # Verify S3 client was called with correct parameters
        self.mock_s3_client.put_object.assert_called_once_with(
            Bucket=self.bucket_name,
            Key=self.test_key,
            Body=self.test_file,
            ContentType=self.test_content_type,
            Metadata=self.test_metadata,
            ServerSideEncryption='AES256'
        )
        
        # Verify the result
        assert result['key'] == self.test_key
        assert result['url'] == f"s3://{self.bucket_name}/{self.test_key}"
        assert result['version_id'] == self.test_version_id
        
        # Test without encryption
        self.mock_s3_client.put_object.reset_mock()
        self.storage.store(
            self.test_file,
            self.test_key,
            content_type=self.test_content_type,
            encrypt=False
        )
        
        # Verify ServerSideEncryption is not passed
        called_args = self.mock_s3_client.put_object.call_args[1]
        assert 'ServerSideEncryption' not in called_args
    
    def test_store_error(self):
        """Test error handling when storing a file fails"""
        # Mock S3 client to raise an error
        error_response = {'Error': {'Code': 'InternalError', 'Message': 'Test error'}}
        self.mock_s3_client.put_object.side_effect = ClientError(
            error_response, 'PutObject'
        )
        
        # Verify StorageError is raised
        with pytest.raises(StorageError) as excinfo:
            self.storage.store(self.test_file, self.test_key)
        
        # Verify the error message
        assert "Failed to store object" in str(excinfo.value)
        assert "Test error" in str(excinfo.value)
        
        # Verify original exception is preserved
        assert isinstance(excinfo.value.original_exception, ClientError)
    
    def test_retrieve(self):
        """Test retrieving a file from S3"""
        # Mock the S3 client response
        mock_body = MagicMock()
        mock_body.read.return_value = self.test_content
        
        self.mock_s3_client.get_object.return_value = {
            'Body': mock_body,
            'ContentType': self.test_content_type,
            'Metadata': self.test_metadata
        }
        
        # Call retrieve method
        content, content_type, metadata = self.storage.retrieve(self.test_key)
        
        # Verify S3 client was called with correct parameters
        self.mock_s3_client.get_object.assert_called_once_with(
            Bucket=self.bucket_name,
            Key=self.test_key
        )
        
        # Verify the results
        assert content == self.test_content
        assert content_type == self.test_content_type
        assert metadata == self.test_metadata
        
        # Test with version_id
        self.mock_s3_client.get_object.reset_mock()
        self.storage.retrieve(self.test_key, version_id=self.test_version_id)
        
        # Verify version_id was passed
        self.mock_s3_client.get_object.assert_called_once_with(
            Bucket=self.bucket_name,
            Key=self.test_key,
            VersionId=self.test_version_id
        )
    
    def test_retrieve_error(self):
        """Test error handling when retrieving a file fails"""
        # Mock S3 client to raise an error
        error_response = {'Error': {'Code': 'NoSuchKey', 'Message': 'Test error'}}
        self.mock_s3_client.get_object.side_effect = ClientError(
            error_response, 'GetObject'
        )
        
        # Verify StorageError is raised
        with pytest.raises(StorageError) as excinfo:
            self.storage.retrieve(self.test_key)
        
        # Verify the error message
        assert "Failed to retrieve object" in str(excinfo.value)
        assert "Test error" in str(excinfo.value)
        
        # Verify original exception is preserved
        assert isinstance(excinfo.value.original_exception, ClientError)
    
    def test_delete(self):
        """Test deleting a file from S3"""
        # Mock the S3 client response
        self.mock_s3_client.delete_object.return_value = {}
        
        # Call delete method
        result = self.storage.delete(self.test_key)
        
        # Verify S3 client was called with correct parameters
        self.mock_s3_client.delete_object.assert_called_once_with(
            Bucket=self.bucket_name,
            Key=self.test_key
        )
        
        # Verify the result
        assert result is True
        
        # Test with version_id
        self.mock_s3_client.delete_object.reset_mock()
        self.storage.delete(self.test_key, version_id=self.test_version_id)
        
        # Verify version_id was passed
        self.mock_s3_client.delete_object.assert_called_once_with(
            Bucket=self.bucket_name,
            Key=self.test_key,
            VersionId=self.test_version_id
        )
    
    def test_delete_error(self):
        """Test error handling when deleting a file fails"""
        # Mock S3 client to raise an error
        error_response = {'Error': {'Code': 'AccessDenied', 'Message': 'Test error'}}
        self.mock_s3_client.delete_object.side_effect = ClientError(
            error_response, 'DeleteObject'
        )
        
        # Verify StorageError is raised
        with pytest.raises(StorageError) as excinfo:
            self.storage.delete(self.test_key)
        
        # Verify the error message
        assert "Failed to delete object" in str(excinfo.value)
        assert "Test error" in str(excinfo.value)
        
        # Verify original exception is preserved
        assert isinstance(excinfo.value.original_exception, ClientError)
    
    def test_get_presigned_url(self):
        """Test generating a presigned URL for a file"""
        test_url = 'https://test-bucket.s3.amazonaws.com/test/document.pdf?signature=test'
        
        # Mock the generate_presigned_url function
        with patch('utils.storage.generate_presigned_url', return_value=test_url) as mock_generate:
            # Call get_presigned_url method
            url = self.storage.get_presigned_url(self.test_key)
            
            # Verify generate_presigned_url was called with correct parameters
            mock_generate.assert_called_once_with(
                self.bucket_name, 
                self.test_key, 
                expiration=3600, 
                region_name=self.region_name,
                version_id=None
            )
            
            # Verify the URL
            assert url == test_url
            
            # Test with custom expiration and version_id
            mock_generate.reset_mock()
            expiration = 7200
            
            self.storage.get_presigned_url(
                self.test_key, 
                expiration=expiration,
                version_id=self.test_version_id
            )
            
            # Verify parameters were passed
            mock_generate.assert_called_once_with(
                self.bucket_name, 
                self.test_key, 
                expiration=expiration, 
                region_name=self.region_name,
                version_id=self.test_version_id
            )
    
    def test_get_presigned_url_error(self):
        """Test error handling when generating a presigned URL fails"""
        # Mock generate_presigned_url to raise an error
        test_error = Exception("Test error")
        with patch('utils.storage.generate_presigned_url', side_effect=test_error):
            # Verify StorageError is raised
            with pytest.raises(StorageError) as excinfo:
                self.storage.get_presigned_url(self.test_key)
            
            # Verify the error message
            assert "Failed to generate presigned URL" in str(excinfo.value)
            assert "Test error" in str(excinfo.value)
            
            # Verify original exception is preserved
            assert excinfo.value.original_exception == test_error
    
    def test_list(self):
        """Test listing objects in S3"""
        # Mock the S3 client response with proper datetime objects
        last_modified1 = datetime(2023, 1, 1, 12, 0, 0)
        last_modified2 = datetime(2023, 1, 2, 12, 0, 0)
        
        self.mock_s3_client.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': 'test/document1.pdf',
                    'Size': 1024,
                    'LastModified': last_modified1,
                    'ETag': '"test-etag-1"',
                    'StorageClass': 'STANDARD'
                },
                {
                    'Key': 'test/document2.pdf',
                    'Size': 2048,
                    'LastModified': last_modified2,
                    'ETag': '"test-etag-2"',
                    'StorageClass': 'STANDARD'
                }
            ]
        }
        
        # Call list method
        result = self.storage.list(prefix='test/')
        
        # Verify S3 client was called with correct parameters
        self.mock_s3_client.list_objects_v2.assert_called_once_with(
            Bucket=self.bucket_name,
            MaxKeys=1000,
            Prefix='test/'
        )
        
        # Verify the results
        assert len(result) == 2
        assert result[0]['key'] == 'test/document1.pdf'
        assert result[1]['key'] == 'test/document2.pdf'
        assert result[0]['size'] == 1024
        assert result[1]['size'] == 2048
        assert result[0]['last_modified'] == last_modified1.isoformat()
        assert result[1]['last_modified'] == last_modified2.isoformat()
        assert result[0]['etag'] == 'test-etag-1'
        assert result[1]['etag'] == 'test-etag-2'
        
        # Test with max_items parameter
        self.mock_s3_client.list_objects_v2.reset_mock()
        max_items = 50
        self.storage.list(max_items=max_items)
        
        # Verify max_items was passed
        self.mock_s3_client.list_objects_v2.assert_called_once_with(
            Bucket=self.bucket_name,
            MaxKeys=max_items
        )
    
    def test_list_error(self):
        """Test error handling when listing objects fails"""
        # Mock S3 client to raise an error
        error_response = {'Error': {'Code': 'AccessDenied', 'Message': 'Test error'}}
        self.mock_s3_client.list_objects_v2.side_effect = ClientError(
            error_response, 'ListObjectsV2'
        )
        
        # Verify StorageError is raised
        with pytest.raises(StorageError) as excinfo:
            self.storage.list()
        
        # Verify the error message
        assert "Failed to list objects" in str(excinfo.value)
        assert "Test error" in str(excinfo.value)
        
        # Verify original exception is preserved
        assert isinstance(excinfo.value.original_exception, ClientError)
    
    def test_get_versions(self):
        """Test getting all versions of an object"""
        # Mock the S3 client response with proper datetime objects
        last_modified1 = datetime(2023, 1, 2, 12, 0, 0)
        last_modified2 = datetime(2023, 1, 1, 12, 0, 0)
        
        self.mock_s3_client.list_object_versions.return_value = {
            'Versions': [
                {
                    'Key': self.test_key,
                    'VersionId': 'version-1',
                    'LastModified': last_modified1,
                    'IsLatest': True,
                    'Size': 1024,
                    'ETag': '"test-etag-1"'
                },
                {
                    'Key': self.test_key,
                    'VersionId': 'version-2',
                    'LastModified': last_modified2,
                    'IsLatest': False,
                    'Size': 896,
                    'ETag': '"test-etag-2"'
                },
                {
                    'Key': 'another-key',  # This should be filtered out
                    'VersionId': 'version-3',
                    'LastModified': last_modified2,
                    'IsLatest': False,
                    'Size': 896,
                    'ETag': '"test-etag-3"'
                }
            ]
        }
        
        # Call get_versions method
        result = self.storage.get_versions(self.test_key)
        
        # Verify S3 client was called with correct parameters
        self.mock_s3_client.list_object_versions.assert_called_once_with(
            Bucket=self.bucket_name,
            Prefix=self.test_key
        )
        
        # Verify the results
        assert len(result) == 2  # Should only include versions for test_key
        assert result[0]['version_id'] == 'version-1'
        assert result[1]['version_id'] == 'version-2'
        assert result[0]['is_latest'] is True
        assert result[1]['is_latest'] is False
        assert result[0]['size'] == 1024
        assert result[0]['last_modified'] == last_modified1.isoformat()
        assert result[1]['last_modified'] == last_modified2.isoformat()
        assert result[0]['etag'] == 'test-etag-1'
        assert result[1]['etag'] == 'test-etag-2'
    
    def test_get_versions_error(self):
        """Test error handling when getting versions fails"""
        # Mock S3 client to raise an error
        error_response = {'Error': {'Code': 'AccessDenied', 'Message': 'Test error'}}
        self.mock_s3_client.list_object_versions.side_effect = ClientError(
            error_response, 'ListObjectVersions'
        )
        
        # Verify StorageError is raised
        with pytest.raises(StorageError) as excinfo:
            self.storage.get_versions(self.test_key)
        
        # Verify the error message
        assert "Failed to get versions of object" in str(excinfo.value)
        assert "Test error" in str(excinfo.value)
        
        # Verify original exception is preserved
        assert isinstance(excinfo.value.original_exception, ClientError)
    
    def test_copy(self):
        """Test copying an object in S3"""
        # Mock the S3 client response
        self.mock_s3_client.copy_object.return_value = {
            'VersionId': self.test_version_id
        }
        
        source_key = 'source/document.pdf'
        destination_key = 'destination/document.pdf'
        
        # Call copy method
        result = self.storage.copy(source_key, destination_key)
        
        # Verify S3 client was called with correct parameters
        self.mock_s3_client.copy_object.assert_called_once_with(
            CopySource={
                'Bucket': self.bucket_name,
                'Key': source_key
            },
            Bucket=self.bucket_name,
            Key=destination_key
        )
        
        # Verify the result
        assert result['key'] == destination_key
        assert result['version_id'] == self.test_version_id
        
        # Test with source_version_id
        self.mock_s3_client.copy_object.reset_mock()
        self.storage.copy(source_key, destination_key, source_version_id=self.test_version_id)
        
        # Verify source_version_id was included
        self.mock_s3_client.copy_object.assert_called_once_with(
            CopySource={
                'Bucket': self.bucket_name,
                'Key': source_key,
                'VersionId': self.test_version_id
            },
            Bucket=self.bucket_name,
            Key=destination_key
        )
    
    def test_copy_error(self):
        """Test error handling when copying an object fails"""
        # Mock S3 client to raise an error
        error_response = {'Error': {'Code': 'AccessDenied', 'Message': 'Test error'}}
        self.mock_s3_client.copy_object.side_effect = ClientError(
            error_response, 'CopyObject'
        )
        
        source_key = 'source/document.pdf'
        destination_key = 'destination/document.pdf'
        
        # Verify StorageError is raised
        with pytest.raises(StorageError) as excinfo:
            self.storage.copy(source_key, destination_key)
        
        # Verify the error message
        assert "Failed to copy object from" in str(excinfo.value)
        assert "Test error" in str(excinfo.value)
        
        # Verify original exception is preserved
        assert isinstance(excinfo.value.original_exception, ClientError)


class TestGeneratePresignedUrl:
    """Test class for the generate_presigned_url function"""
    
    def setup_method(self, method):
        """Set up method that runs before each test"""
        # Create mock S3 client
        self.mock_s3_client = MagicMock()
        
        # Patch boto3.client to return our mock
        self.patcher = patch('boto3.client', return_value=self.mock_s3_client)
        self.mock_boto3_client = self.patcher.start()
        
        # Set up common test data
        self.bucket_name = 'test-bucket'
        self.object_key = 'test/document.pdf'
        self.test_url = 'https://test-bucket.s3.amazonaws.com/test/document.pdf?signature=test'
        self.region_name = 'us-east-1'
        self.version_id = 'test-version-id'
    
    def teardown_method(self, method):
        """Tear down method that runs after each test"""
        # Stop the patcher
        self.patcher.stop()
    
    def test_generate_presigned_url(self):
        """Test generating a presigned URL"""
        # Mock the S3 client response
        self.mock_s3_client.generate_presigned_url.return_value = self.test_url
        
        # Call function with default expiration
        url = generate_presigned_url(self.bucket_name, self.object_key)
        
        # Verify S3 client was called with correct parameters
        self.mock_s3_client.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': self.object_key,
                'ExpiresIn': 3600
            }
        )
        
        # Verify the URL
        assert url == self.test_url
        
        # Test with custom expiration
        self.mock_s3_client.generate_presigned_url.reset_mock()
        expiration = 7200
        
        generate_presigned_url(
            self.bucket_name, 
            self.object_key, 
            expiration=expiration
        )
        
        # Verify expiration was passed
        self.mock_s3_client.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': self.object_key,
                'ExpiresIn': expiration
            }
        )
        
        # Test with region_name and version_id
        self.mock_s3_client.generate_presigned_url.reset_mock()
        
        generate_presigned_url(
            self.bucket_name, 
            self.object_key, 
            region_name=self.region_name,
            version_id=self.version_id
        )
        
        # Verify boto3.client was called with region_name
        self.mock_boto3_client.assert_called_with('s3', region_name=self.region_name)
        
        # Verify version_id was included in params
        self.mock_s3_client.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': self.object_key,
                'ExpiresIn': 3600,
                'VersionId': self.version_id
            }
        )
    
    def test_generate_presigned_url_error(self):
        """Test error handling when generating a presigned URL fails"""
        # Mock S3 client to raise an error
        error_response = {'Error': {'Code': 'AccessDenied', 'Message': 'Test error'}}
        self.mock_s3_client.generate_presigned_url.side_effect = ClientError(
            error_response, 'GetObject'
        )
        
        # Verify StorageError is raised
        with pytest.raises(StorageError) as excinfo:
            generate_presigned_url(self.bucket_name, self.object_key)
        
        # Verify the error message
        assert "Failed to generate presigned URL" in str(excinfo.value)
        assert "Test error" in str(excinfo.value)
        
        # Verify original exception is preserved
        assert isinstance(excinfo.value.original_exception, ClientError)