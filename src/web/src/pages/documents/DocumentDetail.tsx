import React, { useState, useEffect } from 'react'; // react v18.2.0
import { useParams, useNavigate } from 'react-router-dom'; // react-router-dom v6.14.0
import { useDispatch, useSelector } from 'react-redux'; // react-redux v8.1.1
import { Box, Grid, Typography, Button, Card, CardContent, CardActions, Divider, Tooltip, IconButton } from '@mui/material'; // mui/material v5.14.0
import DownloadIcon from '@mui/icons-material/Download'; // mui/icons-material v5.14.0
import EmailIcon from '@mui/icons-material/Email'; // mui/icons-material v5.14.0
import ArrowBackIcon from '@mui/icons-material/ArrowBack'; // mui/icons-material v5.14.0
import Page from '../../components/common/Page';
import StatusBadge from '../../components/common/StatusBadge';
import LoadingSpinner from '../../components/common/Loading/LoadingSpinner';
import DocumentPreview from '../../components/DocumentSigning/DocumentPreview';
import {
  Document,
  SignatureRequest,
  DocumentType,
  DocumentStatus,
  SignatureRequestStatus,
} from '../../types/document.types';
import {
  fetchDocumentById,
  getDocumentDownloadUrl,
  createNewSignatureRequest,
  sendSignatureReminderEmail,
  clearSelectedDocument,
} from '../../store/thunks/documentThunks';

/**
 * Main component for displaying document details
 * @returns Rendered document detail page
 */
const DocumentDetail: React.FC = () => {
  // Extract document ID from URL parameters using useParams
  const { id } = useParams<{ id: string }>();

  // Initialize Redux dispatch function using useDispatch
  const dispatch = useDispatch();

  // Initialize navigation function using useNavigate
  const navigate = useNavigate();

  // Select document state from Redux store using useSelector
  const { selectedDocument, loading, error } = useSelector((state: any) => state.document);

  // Initialize state for document preview URL
  const [documentUrl, setDocumentUrl] = useState<string | null>(null);

  // Fetch document data when component mounts or ID changes
  useEffect(() => {
    if (id) {
      dispatch(fetchDocumentById(id));
    }
  }, [id, dispatch]);

  // Clean up by clearing selected document when component unmounts
  useEffect(() => {
    return () => {
      dispatch(clearSelectedDocument());
    };
  }, [dispatch]);

  // Implement handleDownload function to download the document
  const handleDownload = () => {
    if (selectedDocument) {
      dispatch(getDocumentDownloadUrl(selectedDocument.id));
      // In a real implementation, trigger the download using a library or a direct link
      console.log(`Downloading document: ${selectedDocument.file_name}`);
    }
  };

  // Implement handleCreateSignatureRequest function to create a new signature request
  const handleCreateSignatureRequest = () => {
    if (selectedDocument) {
      // Dispatch the createNewSignatureRequest thunk
      dispatch(createNewSignatureRequest({
        document_id: selectedDocument.id,
        signer_id: 'signer-id', // Replace with actual signer ID
        signer_type: 'borrower', // Replace with actual signer type
      }));
    }
  };

  // Implement handleSendReminder function to send signature reminder emails
  const handleSendReminder = (signatureRequestId: string) => {
    // Dispatch the sendSignatureReminderEmail thunk
    dispatch(sendSignatureReminderEmail(signatureRequestId));
  };

  // Implement handleBack function to navigate back to document list
  const handleBack = () => {
    navigate(-1); // Navigate back to the previous page
  };

  // Helper function to format date strings
  const formatDate = (dateString: string | null | undefined): string => {
    if (!dateString) {
      return 'N/A';
    }
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    } catch (e) {
      return 'N/A';
    }
  };

  // Helper function to get human-readable document type label
  const getDocumentTypeLabel = (type: DocumentType): string => {
    switch (type) {
      case DocumentType.LOAN_AGREEMENT:
        return 'Loan Agreement';
      case DocumentType.COMMITMENT_LETTER:
        return 'Commitment Letter';
      case DocumentType.DISCLOSURE_FORM:
        return 'Disclosure Form';
      case DocumentType.PROMISSORY_NOTE:
        return 'Promissory Note';
      case DocumentType.TRUTH_IN_LENDING:
        return 'Truth in Lending Disclosure';
      case DocumentType.ENROLLMENT_AGREEMENT:
        return 'Enrollment Agreement';
      case DocumentType.IDENTIFICATION:
        return 'Identification Document';
      case DocumentType.INCOME_VERIFICATION:
        return 'Income Verification';
      default:
        return type;
    }
  };

  // Render loading spinner while document is loading
  if (loading) {
    return (
      <Page title="Document Details">
        <LoadingSpinner label="Loading document details..." />
      </Page>
    );
  }

  // Render error message if there was an error loading the document
  if (error) {
    return (
      <Page title="Document Details">
        <Typography color="error">{error}</Typography>
      </Page>
    );
  }

  // Render document details including metadata, status, and actions
  if (selectedDocument) {
    return (
      <Page
        title="Document Details"
        actions={
          <>
            <Button variant="outlined" startIcon={<ArrowBackIcon />} onClick={handleBack}>
              Back
            </Button>
          </>
        }
      >
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {selectedDocument.file_name}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Type: {getDocumentTypeLabel(selectedDocument.document_type)}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Status: <StatusBadge status={selectedDocument.status} />
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Generated: {formatDate(selectedDocument.generated_at)}
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" startIcon={<DownloadIcon />} onClick={handleDownload}>
                  Download
                </Button>
                <Button size="small" onClick={handleCreateSignatureRequest}>
                  Request Signature
                </Button>
              </CardActions>
            </Card>
          </Grid>

          {/* Render document preview section */}
          <Grid item xs={12} md={6}>
            <DocumentPreview documentUrl={documentUrl || selectedDocument.download_url || ''} document={selectedDocument} />
          </Grid>

          {/* Render signature requests section with status and actions */}
          {selectedDocument.signature_requests && selectedDocument.signature_requests.length > 0 && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Signature Requests
                  </Typography>
                  {selectedDocument.signature_requests.map((request) => (
                    <Box key={request.id} mb={2}>
                      <Divider />
                      <Typography variant="subtitle1">Signer: {request.signer_name}</Typography>
                      <Typography variant="body2" color="textSecondary">
                        Status: <StatusBadge status={request.status} />
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Requested: {formatDate(request.requested_at)}
                      </Typography>
                      {request.status === SignatureRequestStatus.PENDING && (
                        <Tooltip title="Send Reminder Email">
                          <IconButton onClick={() => handleSendReminder(request.id)}>
                            <EmailIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Box>
                  ))}
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      </Page>
    );
  }

  return null;
};

/**
 * Helper function to format date strings
 * @param dateString dateString
 * @returns Formatted date string or 'N/A' if input is invalid
 */
const formatDate = (dateString: string | null | undefined): string => {
  // Check if dateString is null, undefined, or empty
  if (!dateString) {
    return 'N/A';
  }
  // Return 'N/A' if dateString is invalid
  try {
    // Create a new Date object from the dateString
    const date = new Date(dateString);
    // Format the date using toLocaleDateString with appropriate options
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } catch (e) {
    return 'N/A';
  }
};

/**
 * Helper function to get human-readable document type label
 * @param type type
 * @returns Human-readable document type label
 */
const getDocumentTypeLabel = (type: DocumentType): string => {
  // Map DocumentType enum values to human-readable labels
  switch (type) {
    // Return the appropriate label based on the input type
    case DocumentType.LOAN_AGREEMENT:
      return 'Loan Agreement';
    case DocumentType.COMMITMENT_LETTER:
      return 'Commitment Letter';
    case DocumentType.DISCLOSURE_FORM:
      return 'Disclosure Form';
    case DocumentType.PROMISSORY_NOTE:
      return 'Promissory Note';
    case DocumentType.TRUTH_IN_LENDING:
      return 'Truth in Lending Disclosure';
    case DocumentType.ENROLLMENT_AGREEMENT:
      return 'Enrollment Agreement';
    case DocumentType.IDENTIFICATION:
      return 'Identification Document';
    case DocumentType.INCOME_VERIFICATION:
      return 'Income Verification';
    // Return the original type string if no mapping exists
    default:
      return type;
  }
};

export default DocumentDetail;