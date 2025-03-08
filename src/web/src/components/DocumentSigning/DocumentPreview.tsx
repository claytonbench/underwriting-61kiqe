import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography, IconButton } from '@mui/material'; // ^5.14.0
import { ChevronLeft, ChevronRight } from '@mui/icons-material'; // ^5.14.0
import useStyles from './styles';
import CustomCard from '../common/Card/Card';
import LoadingSpinner from '../common/Loading/LoadingSpinner';
import { Document, DocumentType } from '../../types/document.types';

/**
 * Props for the DocumentPreview component
 */
interface DocumentPreviewProps {
  /** URL of the document to display */
  documentUrl: string;
  /** Document object containing metadata */
  document: Document;
  /** Whether the document is currently loading */
  loading?: boolean;
  /** Error message if document loading failed */
  error?: string | null;
  /** Additional CSS class name for styling */
  className?: string;
}

/**
 * Component that displays a document for preview before signing.
 * Supports various document types including PDFs and images with page navigation
 * for multi-page documents.
 */
const DocumentPreview: React.FC<DocumentPreviewProps> = ({
  documentUrl,
  document,
  loading = false,
  error = null,
  className,
}) => {
  // State for tracking the current page and total pages
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [isLoading, setIsLoading] = useState<boolean>(loading || true);
  const [errorMessage, setErrorMessage] = useState<string | null>(error);

  // Reference to the document container
  const documentRef = useRef<HTMLDivElement>(null);
  
  // Get styled components
  const classes = useStyles();

  // Determine if the document is a PDF-like document that might have multiple pages
  const isPdfLike = 
    document.document_type === DocumentType.LOAN_AGREEMENT ||
    document.document_type === DocumentType.DISCLOSURE_FORM ||
    document.document_type === DocumentType.PROMISSORY_NOTE ||
    document.document_type === DocumentType.TRUTH_IN_LENDING ||
    document.document_type === DocumentType.COMMITMENT_LETTER ||
    document.file_name.toLowerCase().endsWith('.pdf');

  // Handle document loading and initialization
  useEffect(() => {
    setIsLoading(loading);
    setErrorMessage(error);
    
    // If we have a document URL and it's not loading, attempt to determine the total pages
    if (documentUrl && !loading) {
      if (isPdfLike) {
        // In a real implementation, we would use a library like PDF.js to get the total pages
        // For now, we'll just use a placeholder value based on document type
        let estimatedTotalPages = 1;
        
        switch (document.document_type) {
          case DocumentType.LOAN_AGREEMENT:
            estimatedTotalPages = 10;
            break;
          case DocumentType.DISCLOSURE_FORM:
            estimatedTotalPages = 5;
            break;
          case DocumentType.TRUTH_IN_LENDING:
            estimatedTotalPages = 3;
            break;
          case DocumentType.PROMISSORY_NOTE:
            estimatedTotalPages = 7;
            break;
          case DocumentType.COMMITMENT_LETTER:
            estimatedTotalPages = 2;
            break;
          default:
            estimatedTotalPages = 1;
        }
        
        setTotalPages(estimatedTotalPages);
        setIsLoading(false);
      } else {
        // For non-PDF documents, assume single page
        setTotalPages(1);
        setIsLoading(false);
      }
    }
  }, [documentUrl, loading, error, isPdfLike, document.document_type]);

  // Handle document load error
  const handleDocumentError = () => {
    setErrorMessage("Failed to load document. Please try again or download the document to view it.");
  };

  // Handle navigation to previous page
  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  // Handle navigation to next page
  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  // Render loading spinner during document loading
  if (isLoading) {
    return (
      <CustomCard className={className}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <LoadingSpinner label="Loading document..." />
        </Box>
      </CustomCard>
    );
  }

  // Render error message if there was an error loading the document
  if (errorMessage) {
    return (
      <CustomCard className={className}>
        <Box 
          display="flex" 
          flexDirection="column" 
          justifyContent="center" 
          alignItems="center" 
          minHeight="400px"
          p={3}
          textAlign="center"
        >
          <Typography color="error" variant="h6" gutterBottom>
            Error loading document
          </Typography>
          <Typography color="textSecondary">
            {errorMessage}
          </Typography>
          {document.download_url && (
            <Box mt={2}>
              <a href={document.download_url} download={document.file_name} target="_blank" rel="noopener noreferrer">
                Download document instead
              </a>
            </Box>
          )}
        </Box>
      </CustomCard>
    );
  }

  // Get the appropriate document viewer based on file type
  const renderDocumentViewer = () => {
    // For PDF-like documents
    if (isPdfLike) {
      return (
        <iframe
          src={`${documentUrl}#page=${currentPage}`}
          title={document.file_name}
          width="100%"
          height="100%"
          style={{ border: 'none' }}
          onError={handleDocumentError}
          aria-label="PDF document viewer"
          data-testid="pdf-viewer"
        />
      );
    }
    
    // Check if it's an image
    const isImage = /\.(jpg|jpeg|png|gif|bmp)$/i.test(document.file_name);
    if (isImage) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" height="100%">
          <img 
            src={documentUrl} 
            alt={document.file_name} 
            style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} 
            onError={handleDocumentError}
            data-testid="image-viewer"
          />
        </Box>
      );
    }
    
    // Fallback to generic object viewer
    return (
      <Box width="100%" height="100%" display="flex" flexDirection="column" alignItems="center" justifyContent="center">
        <object
          data={documentUrl}
          type={getDocumentMimeType(document.file_name, document.document_type)}
          width="100%"
          height="100%"
          aria-label="Document viewer"
          data-testid="generic-viewer"
        >
          <Box p={3} textAlign="center">
            <Typography>
              Unable to display document. Please download to view.
            </Typography>
          </Box>
        </object>
        {document.download_url && (
          <Box mt={2} mb={2}>
            <a href={document.download_url} download={document.file_name} target="_blank" rel="noopener noreferrer">
              Download {document.file_name}
            </a>
          </Box>
        )}
      </Box>
    );
  };

  // Helper function to get MIME type for the document
  const getDocumentMimeType = (fileName: string, documentType: DocumentType): string => {
    if (fileName.toLowerCase().endsWith('.pdf')) return 'application/pdf';
    if (fileName.toLowerCase().endsWith('.doc')) return 'application/msword';
    if (fileName.toLowerCase().endsWith('.docx')) return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
    if (fileName.toLowerCase().endsWith('.xls')) return 'application/vnd.ms-excel';
    if (fileName.toLowerCase().endsWith('.xlsx')) return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
    if (fileName.toLowerCase().endsWith('.jpg') || fileName.toLowerCase().endsWith('.jpeg')) return 'image/jpeg';
    if (fileName.toLowerCase().endsWith('.png')) return 'image/png';
    if (fileName.toLowerCase().endsWith('.gif')) return 'image/gif';
    
    // Fallback based on document type
    switch (documentType) {
      case DocumentType.LOAN_AGREEMENT:
      case DocumentType.DISCLOSURE_FORM:
      case DocumentType.PROMISSORY_NOTE:
      case DocumentType.TRUTH_IN_LENDING:
      case DocumentType.COMMITMENT_LETTER:
        return 'application/pdf';
      case DocumentType.IDENTIFICATION:
      case DocumentType.INCOME_VERIFICATION:
        return 'image/jpeg';
      default:
        return 'application/octet-stream';
    }
  };

  return (
    <CustomCard className={className}>
      {/* Document title */}
      <Typography variant="h6" gutterBottom>
        {document.file_name}
      </Typography>
      
      {/* Document preview container */}
      <Box 
        className={classes.documentPreviewContainer} 
        ref={documentRef}
        data-testid="document-preview"
      >
        {renderDocumentViewer()}
      </Box>
      
      {/* Page navigation controls - only show for PDFs with multiple pages */}
      {isPdfLike && totalPages > 1 && (
        <Box className={classes.pageNavigation}>
          <IconButton 
            onClick={handlePreviousPage} 
            disabled={currentPage <= 1}
            aria-label="Previous page"
            size="medium"
          >
            <ChevronLeft />
          </IconButton>
          
          <Typography variant="body2">
            Page {currentPage} of {totalPages}
          </Typography>
          
          <IconButton 
            onClick={handleNextPage} 
            disabled={currentPage >= totalPages}
            aria-label="Next page"
            size="medium"
          >
            <ChevronRight />
          </IconButton>
        </Box>
      )}
    </CustomCard>
  );
};

export default DocumentPreview;