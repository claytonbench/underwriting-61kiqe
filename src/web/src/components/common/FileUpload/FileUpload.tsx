import React, { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { Button, Typography, LinearProgress } from '@mui/material'; // ^5.14.0
import { CloudUpload, Delete, InsertDriveFile } from '@mui/icons-material'; // ^5.14.0
import useStyles from './styles';
import LoadingSpinner from '../Loading/LoadingSpinner';
import { FileUploadResponse } from '../../types/common.types';

/**
 * Props interface for the FileUpload component
 */
interface FileUploadProps {
  /** MIME types or file extensions to accept */
  accept?: string;
  /** Maximum file size in bytes */
  maxSize?: number;
  /** Callback when a file is selected */
  onFileSelect?: (file: File) => void;
  /** Callback to handle file upload */
  onFileUpload: (file: File) => Promise<FileUploadResponse>;
  /** Whether the component is disabled */
  disabled?: boolean;
  /** Whether there is an error state */
  error?: boolean;
  /** Helper text to display below the component */
  helperText?: string;
  /** Label for the upload component */
  label?: string;
  /** Whether to allow multiple file selection */
  multiple?: boolean;
}

/**
 * Formats file size in bytes to a human-readable format
 * @param bytes - The file size in bytes
 * @returns Formatted file size with appropriate unit (KB, MB, GB)
 */
const formatFileSize = (bytes: number): string => {
  if (bytes === 0 || !bytes) return '0 Bytes';
  
  const units = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  
  return `${parseFloat((bytes / Math.pow(1024, i)).toFixed(2))} ${units[i]}`;
};

/**
 * A reusable file upload component that provides drag-and-drop functionality,
 * file selection, progress indication, and error handling for document uploads
 * in the loan management system.
 * 
 * @param props - Component props
 * @returns A file upload component
 */
const FileUpload: React.FC<FileUploadProps> = ({
  accept = 'application/pdf, image/jpeg, image/png',
  maxSize = 10 * 1024 * 1024, // 10MB
  onFileSelect,
  onFileUpload,
  disabled = false,
  error = false,
  helperText,
  label = 'Drag and drop a file here, or click to select',
  multiple = false,
}) => {
  // State management
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  
  // Get styles
  const classes = useStyles();
  
  // Reference to the file input element
  const inputRef = useRef<HTMLInputElement>(null);

  // Handle drag events
  const handleDrag = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (disabled) return;

    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  // Handle drop event
  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (disabled) return;
    
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  // Handle file input change
  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelect(e.target.files[0]);
    }
  };

  // Validate and process selected file
  const handleFileSelect = (file: File) => {
    setUploadError(null);
    
    // Validate file type
    const fileType = file.type;
    const acceptedTypes = accept.split(',').map(type => type.trim());
    
    if (acceptedTypes.length > 0 && !acceptedTypes.some(type => {
      if (type.startsWith('.')) {
        // Check file extension
        return file.name.endsWith(type);
      } else {
        // Check MIME type
        return fileType === type || (type.includes('/*') && fileType.startsWith(type.split('/*')[0]));
      }
    })) {
      setUploadError(`File type not accepted. Please select a file of type: ${accept}`);
      return;
    }
    
    // Validate file size
    if (file.size > maxSize) {
      setUploadError(`File size exceeds the maximum allowed size of ${formatFileSize(maxSize)}`);
      return;
    }
    
    // Set selected file
    setSelectedFile(file);
    
    // Call onFileSelect callback if provided
    if (onFileSelect) {
      onFileSelect(file);
    }
  };

  // Handle file upload
  const handleUpload = async () => {
    if (!selectedFile || isUploading) return;
    
    setIsUploading(true);
    setUploadProgress(0);
    setUploadError(null);
    
    // Create a simulated progress interval
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + 10;
      });
    }, 300);
    
    try {
      // Call the provided upload function
      const response = await onFileUpload(selectedFile);
      
      // Complete the progress
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // Clear the selected file after successful upload
      setTimeout(() => {
        setSelectedFile(null);
        setUploadProgress(0);
        setIsUploading(false);
      }, 1000);
    } catch (error) {
      clearInterval(progressInterval);
      setUploadProgress(0);
      setIsUploading(false);
      setUploadError(error instanceof Error ? error.message : 'An error occurred during upload');
    }
  };

  // Handle file removal
  const handleRemove = () => {
    setSelectedFile(null);
    setUploadProgress(0);
    setUploadError(null);
    
    // Reset the file input
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  // Trigger the file input click
  const handleButtonClick = () => {
    if (inputRef.current) {
      inputRef.current.click();
    }
  };

  // Determine dropzone class based on state
  const dropzoneClass = `${classes.dropzone} ${dragActive ? classes.dropzoneActive : ''} ${disabled ? classes.dropzoneDisabled : ''}`;

  return (
    <div data-testid="file-upload-component">
      {/* Hidden file input */}
      <input
        type="file"
        ref={inputRef}
        style={{ display: 'none' }}
        accept={accept}
        multiple={multiple}
        onChange={handleChange}
        aria-hidden="true"
        disabled={disabled || isUploading}
      />
      
      {/* Drag and drop area */}
      <div
        className={dropzoneClass}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={disabled ? undefined : handleButtonClick}
        onKeyDown={(e) => {
          if (!disabled && (e.key === 'Enter' || e.key === ' ')) {
            e.preventDefault();
            handleButtonClick();
          }
        }}
        tabIndex={disabled ? -1 : 0}
        role="button"
        aria-label={label}
        aria-disabled={disabled}
        data-testid="dropzone"
      >
        <CloudUpload fontSize="large" color="primary" />
        <Typography variant="body1" component="p" sx={{ mt: 1 }}>
          {label}
        </Typography>
        <Typography variant="caption" color="textSecondary">
          Supported formats: {accept}
        </Typography>
        <Typography variant="caption" color="textSecondary">
          Maximum size: {formatFileSize(maxSize)}
        </Typography>
      </div>
      
      {/* Display selected file */}
      {selectedFile && (
        <div className={classes.fileInfo} data-testid="selected-file-info">
          <InsertDriveFile className={classes.fileIcon} />
          <Typography className={classes.fileName} variant="body2">
            {selectedFile.name} ({formatFileSize(selectedFile.size)})
          </Typography>
        </div>
      )}
      
      {/* Upload progress */}
      {uploadProgress > 0 && (
        <div className={classes.progressContainer} data-testid="upload-progress">
          <LinearProgress
            variant="determinate"
            value={uploadProgress}
            aria-label="Upload progress"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={uploadProgress}
          />
        </div>
      )}
      
      {/* Action buttons */}
      {selectedFile && (
        <div className={classes.actionsContainer} data-testid="file-actions">
          <Button
            variant="contained"
            color="primary"
            startIcon={<CloudUpload />}
            className={classes.uploadButton}
            onClick={handleUpload}
            disabled={isUploading || disabled}
            aria-label="Upload file"
            data-testid="upload-button"
          >
            {isUploading ? 'Uploading...' : 'Upload'}
          </Button>
          <Button
            variant="outlined"
            color="secondary"
            startIcon={<Delete />}
            onClick={handleRemove}
            disabled={isUploading || disabled}
            aria-label="Remove file"
            data-testid="remove-button"
          >
            Remove
          </Button>
        </div>
      )}
      
      {/* Loading spinner during upload */}
      {isUploading && (
        <LoadingSpinner 
          size={24} 
          label="Uploading..." 
          data-testid="upload-spinner"
        />
      )}
      
      {/* Error message */}
      {(error || uploadError) && (
        <Typography 
          className={classes.errorText} 
          role="alert"
          data-testid="error-message"
        >
          {uploadError || helperText}
        </Typography>
      )}
      
      {/* Helper text */}
      {!error && !uploadError && helperText && (
        <Typography 
          className={classes.helperText}
          data-testid="helper-text"
        >
          {helperText}
        </Typography>
      )}
    </div>
  );
};

export default FileUpload;