import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom'; // ^6.14.0
import { 
  Box, 
  Typography, 
  Button, 
  Paper, 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  TextField 
} from '@mui/material'; // ^5.14.0

import useStyles from './styles';
import DocumentPreview from './DocumentPreview';
import SignatureCapture from './SignatureCapture';
import CustomStepper from '../common/Stepper/Stepper';
import Page from '../common/Page/Page';
import LoadingOverlay from '../common/Loading/LoadingOverlay';

import { Document, DocumentSigningSession } from '../../types/document.types';
import { getSigningSession, completeSignature, declineSignature } from '../../api/documents';

/**
 * State interface for the DocumentSigning component
 */
interface DocumentSigningState {
  currentStep: number;
  signingSession: DocumentSigningSession | null;
  loading: boolean;
  error: string | null;
  signatureData: string | null;
  declineDialogOpen: boolean;
  declineReason: string;
  submitting: boolean;
}

/**
 * A component that implements the document signing workflow, allowing users to
 * review, sign, and submit electronic signatures for loan documents.
 * 
 * Implements the UI design requirements for the document signing interface and follows
 * the e-signature workflow as specified in the technical specifications.
 */
const DocumentSigning: React.FC = () => {
  // Extract the signature request ID from URL parameters
  const { signatureRequestId } = useParams<{ signatureRequestId: string }>();
  const navigate = useNavigate();
  
  // State management
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [signingSession, setSigningSession] = useState<DocumentSigningSession | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [signatureData, setSignatureData] = useState<string | null>(null);
  const [declineDialogOpen, setDeclineDialogOpen] = useState<boolean>(false);
  const [declineReason, setDeclineReason] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);
  
  // Get styled components
  const classes = useStyles();
  
  // Fetch signing session data when component mounts
  useEffect(() => {
    const fetchSigningSession = async () => {
      if (!signatureRequestId) {
        setLoading(false);
        setError('Missing signature request ID');
        return;
      }
      
      try {
        const response = await getSigningSession(signatureRequestId);
        
        if (response.success && response.data) {
          setSigningSession(response.data);
          setLoading(false);
        } else {
          setLoading(false);
          setError(response.message || 'Failed to load signing session');
        }
      } catch (error) {
        setLoading(false);
        setError('An unexpected error occurred while loading the signing session');
      }
    };
    
    fetchSigningSession();
  }, [signatureRequestId]);
  
  // Handle moving to the next step in the signing process
  const handleNextStep = useCallback(() => {
    setCurrentStep(prev => prev + 1);
  }, []);
  
  // Handle moving to the previous step in the signing process
  const handlePreviousStep = useCallback(() => {
    setCurrentStep(prev => Math.max(0, prev - 1));
  }, []);
  
  // Handle capturing signature data
  const handleSignatureCapture = useCallback((data: string) => {
    setSignatureData(data);
    setCurrentStep(prev => prev + 1); // Move to next step after capturing signature
  }, []);
  
  // Handle submitting the signed document
  const handleSignatureSubmit = useCallback(async () => {
    if (!signatureRequestId || !signatureData) return;
    
    setSubmitting(true);
    
    try {
      const response = await completeSignature(signatureRequestId);
      
      if (response.success) {
        // Navigate back to documents page with success message
        navigate('/documents', { 
          state: { 
            success: true, 
            message: 'Document signed successfully!' 
          } 
        });
      } else {
        setSubmitting(false);
        setError(response.message || 'Failed to submit signature');
      }
    } catch (error) {
      setSubmitting(false);
      setError('An unexpected error occurred while submitting the signature');
    }
  }, [signatureRequestId, signatureData, navigate]);
  
  // Handle declining to sign
  const handleSignatureDecline = useCallback(async () => {
    if (!signatureRequestId || !declineReason) return;
    
    setSubmitting(true);
    
    try {
      const response = await declineSignature({
        signatureRequestId,
        reason: declineReason
      });
      
      if (response.success) {
        // Navigate back to documents page with decline message
        navigate('/documents', { 
          state: { 
            success: true, 
            message: 'Document signature declined' 
          } 
        });
      } else {
        setSubmitting(false);
        setDeclineDialogOpen(false);
        setError(response.message || 'Failed to decline signature');
      }
    } catch (error) {
      setSubmitting(false);
      setDeclineDialogOpen(false);
      setError('An unexpected error occurred while declining the signature');
    }
  }, [signatureRequestId, declineReason, navigate]);
  
  // Handle opening the decline dialog
  const openDeclineDialog = useCallback(() => {
    setDeclineDialogOpen(true);
  }, []);
  
  // Handle closing the decline dialog
  const closeDeclineDialog = useCallback(() => {
    setDeclineDialogOpen(false);
    setDeclineReason('');
  }, []);
  
  // Handle canceling the signing process
  const handleCancel = useCallback(() => {
    navigate('/documents');
  }, [navigate]);
  
  // Show loading overlay while data is being fetched
  if (loading) {
    return <LoadingOverlay isLoading={true} message="Loading document signing session..." />;
  }
  
  // Show error message if signing session couldn't be loaded
  if (error || !signingSession) {
    return (
      <Page title="Document Signing">
        <Box p={3} textAlign="center">
          <Typography variant="h6" color="error" gutterBottom>
            Error Loading Document Signing Session
          </Typography>
          <Typography variant="body1" paragraph>
            {error || 'Unable to load the document signing session. Please try again later.'}
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={handleCancel}
            aria-label="Return to documents"
          >
            Return to Documents
          </Button>
        </Box>
      </Page>
    );
  }
  
  // Define steps for the signing process
  const steps = ['Review Document', 'Sign Document', 'Confirm Signature'];
  
  // Render the component
  return (
    <Page title={`Sign Document - ${signingSession.document.file_name}`}>
      <Paper className={classes.root}>
        {/* Stepper to show progress */}
        <Box className={classes.stepperContainer}>
          <CustomStepper
            activeStep={currentStep}
            steps={steps}
          />
        </Box>
        
        {/* Document review step */}
        {currentStep === 0 && (
          <>
            <Typography variant="h6" gutterBottom>
              Please review the document before signing
            </Typography>
            <DocumentPreview
              documentUrl={signingSession.document_url}
              document={signingSession.document}
            />
            <Box className={classes.instructions}>
              <Typography variant="body2" color="textSecondary">
                Please review the document carefully. Once you proceed to signing, you are confirming
                that you have read and understand the document contents.
              </Typography>
            </Box>
          </>
        )}
        
        {/* Signature capture step */}
        {currentStep === 1 && (
          <SignatureCapture
            onCapture={handleSignatureCapture}
            onCancel={handlePreviousStep}
          />
        )}
        
        {/* Confirmation step */}
        {currentStep === 2 && (
          <>
            <Typography variant="h6" gutterBottom>
              Confirm your signature
            </Typography>
            
            <Box mb={2}>
              <Typography variant="body1">
                Document: {signingSession.document.file_name}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Signer: {signingSession.signer.name} ({signingSession.signer.email})
              </Typography>
            </Box>
            
            {signatureData && (
              <Box className={classes.signaturePreview} mb={3}>
                <Typography variant="subtitle2" gutterBottom>
                  Your signature:
                </Typography>
                <img
                  src={signatureData}
                  alt="Your signature"
                  style={{ maxWidth: '100%' }}
                />
              </Box>
            )}
            
            <Box>
              <Typography variant="body2" color="textSecondary" paragraph>
                By clicking "Submit Signature", you acknowledge that this electronic signature 
                will be the legal equivalent of your manual signature on the document.
                This electronic signature constitutes your acceptance of the terms contained in this document.
              </Typography>
            </Box>
          </>
        )}
        
        {/* Navigation buttons */}
        <Box className={classes.navigationButtons}>
          <Box className={classes.buttonGroup}>
            {currentStep > 0 && currentStep < 2 && (
              <Button
                variant="outlined"
                onClick={handlePreviousStep}
                disabled={submitting}
                aria-label="Back to previous step"
              >
                Back
              </Button>
            )}
            
            <Button
              variant="outlined"
              color="secondary"
              onClick={openDeclineDialog}
              disabled={submitting}
              aria-label="Decline to sign"
            >
              Decline to Sign
            </Button>
            
            <Button
              variant="outlined"
              color="inherit"
              onClick={handleCancel}
              disabled={submitting}
              aria-label="Cancel and return to documents"
            >
              Cancel
            </Button>
          </Box>
          
          <Box>
            {currentStep === 0 && (
              <Button
                variant="contained"
                color="primary"
                onClick={handleNextStep}
                disabled={submitting}
                aria-label="Proceed to signing"
              >
                Proceed to Sign
              </Button>
            )}
            
            {currentStep === 2 && (
              <Button
                variant="contained"
                color="primary"
                onClick={handleSignatureSubmit}
                disabled={submitting || !signatureData}
                aria-label="Submit signature"
              >
                Submit Signature
              </Button>
            )}
          </Box>
        </Box>
        
        {/* Loading overlay during submission */}
        <LoadingOverlay
          isLoading={submitting}
          message={declineDialogOpen ? "Processing decline request..." : "Submitting signature..."}
        />
      </Paper>
      
      {/* Decline reason dialog */}
      <Dialog
        open={declineDialogOpen}
        onClose={closeDeclineDialog}
        aria-labelledby="decline-dialog-title"
        aria-describedby="decline-dialog-description"
      >
        <DialogTitle id="decline-dialog-title">Decline to Sign</DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph id="decline-dialog-description">
            Please provide a reason for declining to sign this document:
          </Typography>
          <TextField
            autoFocus
            margin="dense"
            id="decline-reason"
            label="Reason"
            type="text"
            fullWidth
            multiline
            rows={4}
            value={declineReason}
            onChange={(e) => setDeclineReason(e.target.value)}
            disabled={submitting}
            aria-required="true"
            inputProps={{
              'aria-label': 'Reason for declining',
              'data-testid': 'decline-reason-input'
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={closeDeclineDialog} 
            color="primary" 
            disabled={submitting}
            aria-label="Cancel decline"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSignatureDecline}
            color="secondary"
            disabled={!declineReason.trim() || submitting}
            aria-label="Confirm decline"
          >
            Decline Signature
          </Button>
        </DialogActions>
      </Dialog>
    </Page>
  );
};

export default DocumentSigning;