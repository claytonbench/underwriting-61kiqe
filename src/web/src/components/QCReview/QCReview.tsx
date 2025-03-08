import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  Button,
  TextField,
  FormControl,
  FormControlLabel,
  RadioGroup,
  Radio,
  CircularProgress,
  Divider,
  Grid,
  Card,
  CardContent,
  CardActions,
  Alert,
} from '@mui/material'; // Material-UI components v5.14.0
import { TabContext, TabPanel } from '@mui/lab'; // Material-UI lab components v5.0.0-alpha.136
import { useDispatch, useSelector } from 'react-redux'; // Redux hooks v8.1.1
import {
  QCReview as QCReviewType,
  QCVerificationStatus,
  QCStatus,
  QCReturnReason,
} from '../../types/qc.types';
import useStyles from './styles';
import DocumentVerificationComponent from './DocumentVerification';
import StipulationVerification from './StipulationVerification';
import ChecklistItem from './ChecklistItem';
import {
  selectSelectedQCReview,
  selectLoading,
  selectError,
} from '../../store/slices/qcSlice';
import {
  verifyDocumentThunk,
  rejectDocumentThunk,
  verifyStipulationThunk,
  rejectStipulationThunk,
  waiveStipulationThunk,
  verifyChecklistItemThunk,
  rejectChecklistItemThunk,
  submitQCDecisionThunk,
} from '../../store/thunks/qcThunks';

/**
 * Props for the QCReview component
 */
interface QCReviewProps {
  qcReviewId: string;
  applicationId: string;
  isReadOnly?: boolean;
}

/**
 * Main component for the QC review interface that allows QC personnel to review and verify loan applications
 */
const QCReviewComponent: React.FC<QCReviewProps> = ({ qcReviewId, applicationId, isReadOnly = false }) => {
  // Get styles using the useStyles hook
  const styles = useStyles();

  // Initialize Redux dispatch and selectors for QC review data, loading state, and errors
  const dispatch = useDispatch();
  const qcReview = useSelector(selectSelectedQCReview);
  const loading = useSelector(selectLoading);
  const error = useSelector(selectError);

  // Set up state for active tab, decision (approve/return), return reason, notes, and form validation
  const [activeTab, setActiveTab] = useState('1');
  const [decision, setDecision] = useState<QCStatus | null>(null);
  const [returnReason, setReturnReason] = useState<QCReturnReason | null>(null);
  const [notes, setNotes] = useState('');
  const [formError, setFormError] = useState('');

  // Create useEffect to fetch QC review data when component mounts
  useEffect(() => {
    // Dispatch thunk to fetch QC review details
    // Example: dispatch(fetchQCReviewDetailThunk(qcReviewId));
  }, [dispatch, qcReviewId]);

  // Create handler functions for document verification/rejection
  const handleVerifyDocument = useCallback(
    async (documentVerificationId: string, comments: string) => {
      try {
        await dispatch(
          verifyDocumentThunk({
            document_verification_id: documentVerificationId,
            comments,
          })
        ).unwrap();
      } catch (e: any) {
        setFormError(e.message);
      }
    },
    [dispatch]
  );

  const handleRejectDocument = useCallback(
    async (documentVerificationId: string, comments: string) => {
      try {
        await dispatch(
          rejectDocumentThunk({
            document_verification_id: documentVerificationId,
            comments,
          })
        ).unwrap();
      } catch (e: any) {
        setFormError(e.message);
      }
    },
    [dispatch]
  );

  // Create handler functions for stipulation verification/rejection/waiving
  const handleVerifyStipulation = useCallback(
    async (stipulationVerificationId: string, comments: string) => {
      try {
        await dispatch(
          verifyStipulationThunk({
            stipulation_verification_id: stipulationVerificationId,
            comments,
          })
        ).unwrap();
      } catch (e: any) {
        setFormError(e.message);
      }
    },
    [dispatch]
  );

  const handleRejectStipulation = useCallback(
    async (stipulationVerificationId: string, comments: string) => {
      try {
        await dispatch(
          rejectStipulationThunk({
            stipulation_verification_id: stipulationVerificationId,
            comments,
          })
        ).unwrap();
      } catch (e: any) {
        setFormError(e.message);
      }
    },
    [dispatch]
  );

  const handleWaiveStipulation = useCallback(
    async (stipulationVerificationId: string, comments: string) => {
      try {
        await dispatch(
          waiveStipulationThunk({
            stipulation_verification_id: stipulationVerificationId,
            comments,
          })
        ).unwrap();
      } catch (e: any) {
        setFormError(e.message);
      }
    },
    [dispatch]
  );

  // Create handler functions for checklist item verification/rejection
  const handleVerifyChecklistItem = useCallback(
    async (checklistItemId: string, comments: string) => {
      try {
        await dispatch(
          verifyChecklistItemThunk({
            checklist_item_id: checklistItemId,
            comments,
          })
        ).unwrap();
      } catch (e: any) {
        setFormError(e.message);
      }
    },
    [dispatch]
  );

  const handleRejectChecklistItem = useCallback(
    async (checklistItemId: string, comments: string) => {
      try {
        await dispatch(
          rejectChecklistItemThunk({
            checklist_item_id: checklistItemId,
            comments,
          })
        ).unwrap();
      } catch (e: any) {
        setFormError(e.message);
      }
    },
    [dispatch]
  );

  // Create handler function for tab changes
  const handleTabChange = (event: React.SyntheticEvent, newValue: string) => {
    setActiveTab(newValue);
  };

  // Create handler function for decision radio button changes
  const handleDecisionChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setDecision(event.target.value as QCStatus);
  };

  // Create handler function for return reason changes
  const handleReturnReasonChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setReturnReason(event.target.value as QCReturnReason);
  };

  // Create handler function for notes changes
  const handleNotesChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setNotes(event.target.value);
  };

  // Create handler function for submitting the QC decision
  const handleSubmit = async () => {
    if (!decision) {
      setFormError('Please select a decision');
      return;
    }

    if (decision === QCStatus.RETURNED && !returnReason) {
      setFormError('Please select a return reason');
      return;
    }

    setFormError('');

    try {
      await dispatch(
        submitQCDecisionThunk({
          qc_review_id: qcReviewId,
          status: decision,
          return_reason: returnReason,
          notes: notes,
        })
      ).unwrap();
    } catch (e: any) {
      setFormError(e.message);
    }
  };

  // Render loading state if data is being fetched
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="200px">
        <CircularProgress />
      </Box>
    );
  }

  // Render error state if there was an error fetching data
  if (error) {
    return (
      <Alert severity="error" className={styles.root}>
        {error}
      </Alert>
    );
  }

  // Render empty state if no QC review data is available
  if (!qcReview) {
    return (
      <Alert severity="info" className={styles.root}>
        No QC review data available.
      </Alert>
    );
  }

  // Render the main QC review interface with tabs for Documents, Stipulations, and Checklist
  return (
    <Paper className={styles.root} elevation={2}>
      <Typography variant="h6" gutterBottom>
        Quality Control Review
      </Typography>
      <TabContext value={activeTab}>
        <Box className={styles.tabsContainer}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            aria-label="QC review tabs"
          >
            <Tab label="Documents" value="1" id="documents-tab" aria-controls="documents-panel" />
            <Tab label="Stipulations" value="2" id="stipulations-tab" aria-controls="stipulations-panel" />
            <Tab label="Checklist" value="3" id="checklist-tab" aria-controls="checklist-panel" />
          </Tabs>
        </Box>
        <TabPanel value="1" className={styles.tabPanel} id="documents-panel" aria-labelledby="documents-tab">
          {qcReview.document_verifications.map((documentVerification) => (
            <DocumentVerificationComponent
              key={documentVerification.id}
              documentVerification={documentVerification}
              onVerify={handleVerifyDocument}
              onReject={handleRejectDocument}
              isReadOnly={isReadOnly}
            />
          ))}
        </TabPanel>
        <TabPanel value="2" className={styles.tabPanel} id="stipulations-panel" aria-labelledby="stipulations-tab">
          {qcReview.stipulation_verifications.map((stipulation) => (
            <StipulationVerification
              key={stipulation.id}
              stipulation={stipulation}
              onVerify={handleVerifyStipulation}
              onReject={handleRejectStipulation}
              onWaive={handleWaiveStipulation}
              isReadOnly={isReadOnly}
            />
          ))}
        </TabPanel>
        <TabPanel value="3" className={styles.tabPanel} id="checklist-panel" aria-labelledby="checklist-tab">
          {qcReview.checklist_items.map((checklistItem) => (
            <ChecklistItem
              key={checklistItem.id}
              checklistItem={checklistItem}
              onVerify={handleVerifyChecklistItem}
              onReject={handleRejectChecklistItem}
              isReadOnly={isReadOnly}
            />
          ))}
        </TabPanel>
      </TabContext>
      <Divider />
      <Box className={styles.decisionSection}>
        <Typography variant="h6" className={styles.decisionTitle}>
          QC Decision
        </Typography>
        <FormControl component="fieldset" error={!!formError}>
          <RadioGroup
            aria-label="qc-decision"
            name="qcDecision"
            value={decision || ''}
            onChange={handleDecisionChange}
            className={styles.decisionOptions}
          >
            <FormControlLabel
              value={QCStatus.APPROVED}
              control={<Radio aria-label="Approve application" />}
              label="Approve"
            />
            <FormControlLabel
              value={QCStatus.RETURNED}
              control={<Radio aria-label="Return application" />}
              label="Return"
            />
          </RadioGroup>
        </FormControl>
        {decision === QCStatus.RETURNED && (
          <TextField
            select
            label="Return Reason"
            value={returnReason || ''}
            onChange={handleReturnReasonChange}
            fullWidth
            variant="outlined"
            className={styles.returnReasonField}
            SelectProps={{
              native: true,
            }}
            aria-label="Return reason"
          >
            <option value="">Select a reason</option>
            <option value={QCReturnReason.INCOMPLETE_DOCUMENTATION}>Incomplete Documentation</option>
            <option value={QCReturnReason.INCORRECT_INFORMATION}>Incorrect Information</option>
            <option value={QCReturnReason.MISSING_SIGNATURES}>Missing Signatures</option>
            <option value={QCReturnReason.STIPULATION_NOT_MET}>Stipulation Not Met</option>
            <option value={QCReturnReason.COMPLIANCE_ISSUE}>Compliance Issue</option>
            <option value={QCReturnReason.OTHER}>Other</option>
          </TextField>
        )}
        <TextField
          label="Notes"
          multiline
          rows={3}
          value={notes}
          onChange={handleNotesChange}
          fullWidth
          variant="outlined"
          className={styles.notesField}
          aria-label="Additional notes"
          placeholder="Add any additional notes here..."
        />
        {formError && (
          <Typography color="error" variant="body2">
            {formError}
          </Typography>
        )}
        <Button
          variant="contained"
          color="primary"
          className={styles.submitButton}
          onClick={handleSubmit}
          disabled={loading || isReadOnly}
          aria-label="Submit QC decision"
        >
          Submit
        </Button>
      </Box>
    </Paper>
  );
};

export default QCReviewComponent;