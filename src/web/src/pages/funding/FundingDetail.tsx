import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom'; // ^6.14.0
import { useDispatch, useSelector } from 'react-redux'; // ^8.1.0
import {
  Grid,
  Typography,
  Button,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Tabs,
  Tab,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Box,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton
} from '@mui/material'; // ^5.14.0
import {
  Add as AddIcon,
  Edit as EditIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  AttachMoney as AttachMoneyIcon,
  Note as NoteIcon
} from '@mui/icons-material'; // ^5.14.0
import Page from '../../components/common/Page';
import StatusBadge from '../../components/common/StatusBadge';
import LoadingOverlay from '../../components/common/Loading';
import ConfirmationDialog from '../../components/common/Confirmation';
import DataTable from '../../components/common/DataTable';
import { formatCurrency } from '../../utils/formatting';
import { formatDate } from '../../utils/date';
import usePermissions from '../../hooks/usePermissions';
import {
  FundingRequestStatus,
  DisbursementStatus,
  DisbursementMethod,
  VerificationStatus,
  FundingNoteType,
  FundingRequestDetail,
  Disbursement,
  EnrollmentVerification,
  StipulationVerification,
  FundingNote,
  TableColumn
} from '../../types/funding.types';
import {
  fetchFundingRequestById,
  approveFundingRequest,
  rejectFundingRequest,
  verifyEnrollment,
  verifyStipulation,
  createDisbursement,
  updateDisbursementStatus,
  addFundingNote
} from '../../store/thunks/fundingThunks';
import {
  selectSelectedFundingRequest,
  selectFundingLoading,
  selectFundingError
} from '../../store/slices/fundingSlice';

/**
 * Main component for displaying detailed information about a funding request
 */
const FundingDetail: React.FC = () => {
  // Extract funding request ID from route parameters
  const { id } = useParams<{ id: string }>();

  // Initialize Redux dispatch and navigation functions
  const dispatch = useDispatch();
  const navigate = useNavigate();

  // Select funding request details, loading state, and error from Redux store
  const fundingRequest = useSelector(selectSelectedFundingRequest);
  const loading = useSelector(selectFundingLoading);
  const error = useSelector(selectFundingError);

  // Initialize state for dialogs (approval, rejection, enrollment verification, stipulation verification, disbursement creation, note creation)
  const [approvalDialogOpen, setApprovalDialogOpen] = useState(false);
  const [rejectionDialogOpen, setRejectionDialogOpen] = useState(false);
  const [enrollmentVerificationDialogOpen, setEnrollmentVerificationDialogOpen] = useState(false);
  const [selectedStipulation, setSelectedStipulation] = useState<StipulationVerification | null>(null);
  const [stipulationVerificationDialogOpen, setStipulationVerificationDialogOpen] = useState(false);
  const [disbursementDialogOpen, setDisbursementDialogOpen] = useState(false);
  const [noteDialogOpen, setNoteDialogOpen] = useState(false);

  // Initialize state for tab management
  const [selectedTab, setSelectedTab] = useState(0);

  // Check user permissions for funding actions
  const { checkPermission } = usePermissions();
  const canApprove = checkPermission('funding:approve');
  const canReject = checkPermission('funding:reject');
  const canVerifyEnrollment = checkPermission('funding:verify_enrollment');
  const canVerifyStipulations = checkPermission('funding:verify_stipulations');
  const canCreateDisbursement = checkPermission('funding:create_disbursement');
  const canUpdateDisbursement = checkPermission('funding:update_disbursement');
  const canAddNote = checkPermission('funding:add_note');

  /**
   * Fetch funding request details on component mount
   */
  useEffect(() => {
    if (id) {
      dispatch(fetchFundingRequestById(id));
    }
  }, [id, dispatch]);

  /**
   * Handle approval dialog open/close and submission
   */
  const handleApprovalDialogOpen = useCallback(() => {
    setApprovalDialogOpen(true);
  }, []);

  const handleApprovalDialogClose = useCallback(() => {
    setApprovalDialogOpen(false);
  }, []);

  const handleApprove = useCallback((approvalData: FundingApprovalRequest) => {
    dispatch(approveFundingRequest(approvalData));
    setApprovalDialogOpen(false);
  }, [dispatch]);

  /**
   * Handle rejection dialog open/close and submission
   */
  const handleRejectionDialogOpen = useCallback(() => {
    setRejectionDialogOpen(true);
  }, []);

  const handleRejectionDialogClose = useCallback(() => {
    setRejectionDialogOpen(false);
  }, []);

  const handleReject = useCallback(({ fundingRequestId, comments }: { fundingRequestId: UUID; comments: string }) => {
    dispatch(rejectFundingRequest({ fundingRequestId, comments }));
    setRejectionDialogOpen(false);
  }, [dispatch]);

  /**
   * Handle enrollment verification dialog open/close and submission
   */
  const handleEnrollmentVerificationDialogOpen = useCallback(() => {
    setEnrollmentVerificationDialogOpen(true);
  }, []);

  const handleEnrollmentVerificationDialogClose = useCallback(() => {
    setEnrollmentVerificationDialogOpen(false);
  }, []);

  const handleVerifyEnrollmentSubmit = useCallback((verificationData: EnrollmentVerificationRequest) => {
    dispatch(verifyEnrollment(verificationData));
    setEnrollmentVerificationDialogOpen(false);
  }, [dispatch]);

  /**
   * Handle stipulation verification dialog open/close and submission
   */
  const handleStipulationVerificationDialogOpen = useCallback((stipulation: StipulationVerification) => {
    setSelectedStipulation(stipulation);
    setStipulationVerificationDialogOpen(true);
  }, []);

  const handleStipulationVerificationDialogClose = useCallback(() => {
    setSelectedStipulation(null);
    setStipulationVerificationDialogOpen(false);
  }, []);

  const handleVerifyStipulationSubmit = useCallback((verificationData: StipulationVerificationRequest) => {
    dispatch(verifyStipulation(verificationData));
    setSelectedStipulation(null);
    setStipulationVerificationDialogOpen(false);
  }, [dispatch]);

  /**
   * Handle disbursement creation dialog open/close and submission
   */
  const handleDisbursementDialogOpen = useCallback(() => {
    setDisbursementDialogOpen(true);
  }, []);

  const handleDisbursementDialogClose = useCallback(() => {
    setDisbursementDialogOpen(false);
  }, []);

  const handleCreateDisbursementSubmit = useCallback((disbursementData: DisbursementCreateRequest) => {
    dispatch(createDisbursement(disbursementData));
    setDisbursementDialogOpen(false);
  }, [dispatch]);

  /**
   * Handle note creation dialog open/close and submission
   */
  const handleNoteDialogOpen = useCallback(() => {
    setNoteDialogOpen(true);
  }, []);

  const handleNoteDialogClose = useCallback(() => {
    setNoteDialogOpen(false);
  }, []);

  const handleAddNoteSubmit = useCallback((noteData: FundingNoteCreateRequest) => {
    dispatch(addFundingNote(noteData));
    setNoteDialogOpen(false);
  }, [dispatch]);

  /**
   * Handle tab change events
   */
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  /**
   * Render page with funding request details
   */
  return (
    <Page title="Funding Request Details" description="View and manage funding request information">
      <LoadingOverlay isLoading={loading} message="Loading funding request details..." />

      {error && (
        <Alert severity="error" onClose={() => navigate('/funding')}>
          {error}
        </Alert>
      )}

      {fundingRequest && (
        <>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Card>
                <CardHeader
                  title={`Funding Request #${fundingRequest.funding_request.id}`}
                  subheader={`Application #${fundingRequest.funding_request.application_id}`}
                />
                <CardContent>
                  <Typography variant="body1">
                    Status: <StatusBadge status={fundingRequest.funding_request.status} />
                  </Typography>
                  <Typography variant="body1">
                    Requested Amount: {formatCurrency(fundingRequest.funding_request.requested_amount)}
                  </Typography>
                  {fundingRequest.funding_request.approved_amount && (
                    <Typography variant="body1">
                      Approved Amount: {formatCurrency(fundingRequest.funding_request.approved_amount)}
                    </Typography>
                  )}
                  <Typography variant="body1">
                    Borrower: {fundingRequest.borrower_name}
                  </Typography>
                  <Typography variant="body1">
                    School: {fundingRequest.school_name}
                  </Typography>
                  <Typography variant="body1">
                    Program: {fundingRequest.program_name}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Tabs value={selectedTab} onChange={handleTabChange} aria-label="Funding details tabs">
            <Tab label="Overview" />
            <Tab label="Stipulations" />
            <Tab label="Disbursements" />
            <Tab label="Notes" />
          </Tabs>
          <Divider />

          {selectedTab === 0 && (
            <FundingOverview fundingRequest={fundingRequest} />
          )}

          {selectedTab === 1 && (
            <StipulationsTab
              fundingRequest={fundingRequest}
              canVerifyStipulations={canVerifyStipulations}
              onVerifyStipulation={handleStipulationVerificationDialogOpen}
            />
          )}

          {selectedTab === 2 && (
            <DisbursementsTab
              fundingRequest={fundingRequest}
              canCreateDisbursement={canCreateDisbursement}
              onCreateDisbursement={handleDisbursementDialogOpen}
              onUpdateDisbursementStatus={() => { /* TODO: Implement update disbursement status */ }}
            />
          )}

          {selectedTab === 3 && (
            <NotesTab
              fundingRequest={fundingRequest}
              canAddNote={canAddNote}
              onAddNote={handleNoteDialogOpen}
            />
          )}

          <Box mt={2}>
            {fundingRequest.funding_request.status === FundingRequestStatus.PENDING && canApprove && (
              <Button variant="contained" color="primary" onClick={handleApprovalDialogOpen} startIcon={<CheckIcon />}>
                Approve Funding
              </Button>
            )}
            {fundingRequest.funding_request.status !== FundingRequestStatus.REJECTED && canReject && (
              <Button variant="contained" color="error" onClick={handleRejectionDialogOpen} startIcon={<CloseIcon />} sx={{ ml: 1 }}>
                Reject Funding
              </Button>
            )}
            {fundingRequest.funding_request.status === FundingRequestStatus.ENROLLMENT_VERIFIED && canVerifyEnrollment && (
              <Button variant="contained" color="success" onClick={handleEnrollmentVerificationDialogOpen} startIcon={<CheckIcon />} sx={{ ml: 1 }}>
                Verify Enrollment
              </Button>
            )}
          </Box>
        </>
      )}

      {/* Dialogs */}
      <ApprovalDialog
        open={approvalDialogOpen}
        onClose={handleApprovalDialogClose}
        onApprove={handleApprove}
        fundingRequest={fundingRequest?.funding_request}
      />

      <RejectionDialog
        open={rejectionDialogOpen}
        onClose={handleRejectionDialogClose}
        onReject={handleReject}
        fundingRequest={fundingRequest?.funding_request}
      />

      <EnrollmentVerificationDialog
        open={enrollmentVerificationDialogOpen}
        onClose={handleEnrollmentVerificationDialogClose}
        onVerify={handleVerifyEnrollmentSubmit}
        fundingRequest={fundingRequest?.funding_request}
      />

      <StipulationVerificationDialog
        open={stipulationVerificationDialogOpen}
        onClose={handleStipulationVerificationDialogClose}
        onVerify={handleVerifyStipulationSubmit}
        stipulation={selectedStipulation}
      />

      <DisbursementDialog
        open={disbursementDialogOpen}
        onClose={handleDisbursementDialogClose}
        onCreate={handleCreateDisbursementSubmit}
        fundingRequest={fundingRequest?.funding_request}
      />

      <NoteDialog
        open={noteDialogOpen}
        onClose={handleNoteDialogClose}
        onAdd={handleAddNoteSubmit}
        fundingRequest={fundingRequest?.funding_request}
      />
    </Page>
  );
};

/**
 * Component for displaying the overview tab of funding request details
 */
interface FundingOverviewProps {
  fundingRequest: FundingRequestDetail;
}

const FundingOverview: React.FC<FundingOverviewProps> = ({ fundingRequest }) => {
  return (
    <Grid container spacing={2}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardHeader title="Funding Request Information" />
          <CardContent>
            <Typography variant="body1">ID: {fundingRequest.funding_request.id}</Typography>
            <Typography variant="body1">Status: <StatusBadge status={fundingRequest.funding_request.status} /></Typography>
            <Typography variant="body1">Requested Amount: {formatCurrency(fundingRequest.funding_request.requested_amount)}</Typography>
            {fundingRequest.funding_request.approved_amount && (
              <Typography variant="body1">Approved Amount: {formatCurrency(fundingRequest.funding_request.approved_amount)}</Typography>
            )}
            <Typography variant="body1">Requested Date: {formatDate(fundingRequest.funding_request.requested_at, 'MM/DD/YYYY')}</Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardHeader title="Borrower Information" />
          <CardContent>
            <Typography variant="body1">Name: {fundingRequest.borrower_name}</Typography>
            <Typography variant="body1">School: {fundingRequest.school_name}</Typography>
            <Typography variant="body1">Program: {fundingRequest.program_name}</Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardHeader title="Application Information" />
          <CardContent>
            <Typography variant="body1">Application ID: {fundingRequest.funding_request.application_id}</Typography>
            <Typography variant="body1">Application Status: <StatusBadge status={fundingRequest.application_status} /></Typography>
          </CardContent>
        </Card>
      </Grid>

      {fundingRequest.enrollment_verification && (
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Enrollment Verification" />
            <CardContent>
              <Typography variant="body1">Verification Type: {fundingRequest.enrollment_verification.verification_type}</Typography>
              <Typography variant="body1">Verified By: {fundingRequest.enrollment_verification.verified_by}</Typography>
              <Typography variant="body1">Verified At: {formatDate(fundingRequest.enrollment_verification.verified_at, 'MM/DD/YYYY')}</Typography>
              <Typography variant="body1">Start Date: {formatDate(fundingRequest.enrollment_verification.start_date, 'MM/DD/YYYY')}</Typography>
            </CardContent>
          </Card>
        </Grid>
      )}
    </Grid>
  );
};

/**
 * Component for displaying the stipulations tab with verification controls
 */
interface StipulationsTabProps {
  fundingRequest: FundingRequestDetail;
  canVerifyStipulations: boolean;
  onVerifyStipulation: (stipulation: StipulationVerification) => void;
}

const StipulationsTab: React.FC<StipulationsTabProps> = ({ fundingRequest, canVerifyStipulations, onVerifyStipulation }) => {
  return (
    <Grid container spacing={2}>
      {fundingRequest.stipulation_verifications.map(stipulation => (
        <Grid item xs={12} key={stipulation.stipulation_id}>
          <Card>
            <CardContent>
              <Typography variant="body1">Stipulation: {stipulation.stipulation_description}</Typography>
              <Typography variant="body1">Status: <StatusBadge status={stipulation.status} /></Typography>
              {canVerifyStipulations && stipulation.status === VerificationStatus.PENDING && (
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => onVerifyStipulation(stipulation)}
                  startIcon={<EditIcon />}
                >
                  Verify Stipulation
                </Button>
              )}
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

/**
 * Component for displaying the disbursements tab with creation and status update controls
 */
interface DisbursementsTabProps {
  fundingRequest: FundingRequestDetail;
  canCreateDisbursement: boolean;
  onCreateDisbursement: () => void;
  onUpdateDisbursementStatus: (disbursementId: UUID, status: DisbursementStatus) => void;
}

const DisbursementsTab: React.FC<DisbursementsTabProps> = ({ fundingRequest, canCreateDisbursement, onCreateDisbursement, onUpdateDisbursementStatus }) => {
  // Define table columns for disbursements (amount, date, method, status, actions)
  const disbursementColumns: TableColumn<Disbursement>[] = [
    { field: 'amount', headerName: 'Amount', render: (value) => formatCurrency(value) },
    { field: 'disbursement_date', headerName: 'Date', render: (value) => formatDate(value, 'MM/DD/YYYY') },
    { field: 'disbursement_method', headerName: 'Method' },
    { field: 'status', headerName: 'Status', render: (value) => <StatusBadge status={value} /> },
  ];

  // Define table actions for disbursements (update status)
  const disbursementActions = [
    {
      icon: <EditIcon />,
      label: 'Update Status',
      onClick: (row: Disbursement) => {
        // TODO: Implement update disbursement status
        console.log('Update status clicked for disbursement:', row.id);
        onUpdateDisbursementStatus(row.id, row.status);
      },
      isVisible: (row: Disbursement) => row.status !== DisbursementStatus.COMPLETED,
    },
  ];

  return (
    <>
      <DataTable
        data={fundingRequest.disbursements}
        columns={disbursementColumns}
        actions={disbursementActions}
        emptyStateMessage="No disbursements found for this funding request."
      />

      {canCreateDisbursement && (
        <Box mt={2}>
          <Button variant="contained" color="primary" onClick={onCreateDisbursement} startIcon={<AttachMoneyIcon />}>
            Create Disbursement
          </Button>
        </Box>
      )}
    </>
  );
};

/**
 * Component for displaying the notes tab with note creation control
 */
interface NotesTabProps {
  fundingRequest: FundingRequestDetail;
  canAddNote: boolean;
  onAddNote: () => void;
}

const NotesTab: React.FC<NotesTabProps> = ({ fundingRequest, canAddNote, onAddNote }) => {
  // Define table columns for notes (type, text, created by, date)
  const noteColumns: TableColumn<FundingNote>[] = [
    { field: 'note_type', headerName: 'Type' },
    { field: 'note_text', headerName: 'Text' },
    { field: 'created_by_name', headerName: 'Created By' },
    { field: 'created_at', headerName: 'Date', render: (value) => formatDate(value, 'MM/DD/YYYY') },
  ];

  return (
    <>
      <DataTable
        data={fundingRequest.notes}
        columns={noteColumns}
        emptyStateMessage="No notes found for this funding request."
      />

      {canAddNote && (
        <Box mt={2}>
          <Button variant="contained" color="primary" onClick={onAddNote} startIcon={<NoteIcon />}>
            Add Note
          </Button>
        </Box>
      )}
    </>
  );
};

/**
 * Dialog component for approving a funding request
 */
interface ApprovalDialogProps {
  open: boolean;
  onClose: () => void;
  onApprove: (approvalData: FundingApprovalRequest) => void;
  fundingRequest: FundingRequest | undefined;
}

const ApprovalDialog: React.FC<ApprovalDialogProps> = ({ open, onClose, onApprove, fundingRequest }) => {
  const [approvedAmount, setApprovedAmount] = useState('');
  const [comments, setComments] = useState('');

  const handleSubmit = () => {
    if (fundingRequest) {
      const approvalData: FundingApprovalRequest = {
        funding_request_id: fundingRequest.id,
        approved_amount: parseFloat(approvedAmount),
        comments: comments,
      };
      onApprove(approvalData);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} aria-labelledby="approval-dialog-title">
      <DialogTitle id="approval-dialog-title">Approve Funding Request</DialogTitle>
      <DialogContent>
        <TextField
          label="Approved Amount"
          value={approvedAmount}
          onChange={(e) => setApprovedAmount(e.target.value)}
          fullWidth
          margin="normal"
          variant="outlined"
        />
        <TextField
          label="Comments"
          value={comments}
          onChange={(e) => setComments(e.target.value)}
          fullWidth
          margin="normal"
          variant="outlined"
          multiline
          rows={4}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} color="primary" variant="contained">
          Approve
        </Button>
      </DialogActions>
    </Dialog>
  );
};

/**
 * Dialog component for rejecting a funding request
 */
interface RejectionDialogProps {
  open: boolean;
  onClose: () => void;
  onReject: ({ fundingRequestId, comments }: { fundingRequestId: UUID; comments: string }) => void;
  fundingRequest: FundingRequest | undefined;
}

const RejectionDialog: React.FC<RejectionDialogProps> = ({ open, onClose, onReject, fundingRequest }) => {
  const [comments, setComments] = useState('');

  const handleSubmit = () => {
    if (fundingRequest) {
      onReject({ fundingRequestId: fundingRequest.id, comments });
    }
  };

  return (
    <Dialog open={open} onClose={onClose} aria-labelledby="rejection-dialog-title">
      <DialogTitle id="rejection-dialog-title">Reject Funding Request</DialogTitle>
      <DialogContent>
        <TextField
          label="Comments"
          value={comments}
          onChange={(e) => setComments(e.target.value)}
          fullWidth
          margin="normal"
          variant="outlined"
          multiline
          rows={4}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} color="error" variant="contained">
          Reject
        </Button>
      </DialogActions>
    </Dialog>
  );
};

/**
 * Dialog component for verifying enrollment
 */
interface EnrollmentVerificationDialogProps {
  open: boolean;
  onClose: () => void;
  onVerify: (verificationData: EnrollmentVerificationRequest) => void;
  fundingRequest: FundingRequest | undefined;
}

const EnrollmentVerificationDialog: React.FC<EnrollmentVerificationDialogProps> = ({ open, onClose, onVerify, fundingRequest }) => {
  const [verificationType, setVerificationType] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [comments, setComments] = useState('');

  const handleSubmit = () => {
    if (fundingRequest) {
      const verificationData: EnrollmentVerificationRequest = {
        funding_request_id: fundingRequest.id,
        verification_type: verificationType,
        start_date: startDate,
        comments: comments,
        document_id: null, // TODO: Implement document upload
      };
      onVerify(verificationData);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} aria-labelledby="enrollment-verification-dialog-title">
      <DialogTitle id="enrollment-verification-dialog-title">Verify Enrollment</DialogTitle>
      <DialogContent>
        <FormControl fullWidth margin="normal" variant="outlined">
          <InputLabel id="verification-type-label">Verification Type</InputLabel>
          <Select
            labelId="verification-type-label"
            value={verificationType}
            onChange={(e) => setVerificationType(e.target.value)}
            label="Verification Type"
          >
            <MenuItem value="enrollment_agreement">Enrollment Agreement</MenuItem>
            <MenuItem value="school_confirmation">School Confirmation</MenuItem>
            <MenuItem value="attendance_verification">Attendance Verification</MenuItem>
          </Select>
        </FormControl>
        <TextField
          label="Start Date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          fullWidth
          margin="normal"
          variant="outlined"
        />
        <TextField
          label="Comments"
          value={comments}
          onChange={(e) => setComments(e.target.value)}
          fullWidth
          margin="normal"
          variant="outlined"
          multiline
          rows={4}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} color="primary" variant="contained">
          Verify
        </Button>
      </DialogActions>
    </Dialog>
  );
};

/**
 * Dialog component for verifying a stipulation
 */
interface StipulationVerificationDialogProps {
  open: boolean;
  onClose: () => void;
  onVerify: (verificationData: StipulationVerificationRequest) => void;
  stipulation: StipulationVerification | null;
}

const StipulationVerificationDialog: React.FC<StipulationVerificationDialogProps> = ({ open, onClose, onVerify, stipulation }) => {
  const [status, setStatus] = useState<string>('');
  const [comments, setComments] = useState('');

  const handleSubmit = () => {
    if (stipulation) {
      const verificationData: StipulationVerificationRequest = {
        funding_request_id: stipulation.funding_request_id,
        stipulation_id: stipulation.stipulation_id,
        status: status,
        comments: comments,
      };
      onVerify(verificationData);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} aria-labelledby="stipulation-verification-dialog-title">
      <DialogTitle id="stipulation-verification-dialog-title">Verify Stipulation</DialogTitle>
      <DialogContent>
        <FormControl fullWidth margin="normal" variant="outlined">
          <InputLabel id="verification-status-label">Verification Status</InputLabel>
          <Select
            labelId="verification-status-label"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            label="Verification Status"
          >
            <MenuItem value="verified">Verified</MenuItem>
            <MenuItem value="rejected">Rejected</MenuItem>
            <MenuItem value="waived">Waived</MenuItem>
          </Select>
        </FormControl>
        <TextField
          label="Comments"
          value={comments}
          onChange={(e) => setComments(e.target.value)}
          fullWidth
          margin="normal"
          variant="outlined"
          multiline
          rows={4}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} color="primary" variant="contained">
          Verify
        </Button>
      </DialogActions>
    </Dialog>
  );
};

/**
 * Dialog component for creating a disbursement
 */
interface DisbursementDialogProps {
  open: boolean;
  onClose: () => void;
  onCreate: (disbursementData: DisbursementCreateRequest) => void;
  fundingRequest: FundingRequest | undefined;
}

const DisbursementDialog: React.FC<DisbursementDialogProps> = ({ open, onClose, onCreate, fundingRequest }) => {
  const [amount, setAmount] = useState('');
  const [disbursementDate, setDisbursementDate] = useState('');
  const [disbursementMethod, setDisbursementMethod] = useState<string>('');
  const [comments, setComments] = useState('');

  const handleSubmit = () => {
    if (fundingRequest) {
      const disbursementData: DisbursementCreateRequest = {
        funding_request_id: fundingRequest.id,
        amount: parseFloat(amount),
        disbursement_date: disbursementDate,
        disbursement_method: disbursementMethod as DisbursementMethod,
        comments: comments,
      };
      onCreate(disbursementData);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} aria-labelledby="disbursement-dialog-title">
      <DialogTitle id="disbursement-dialog-title">Create Disbursement</DialogTitle>
      <DialogContent>
        <TextField
          label="Amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          fullWidth
          margin="normal"
          variant="outlined"
        />
        <TextField
          label="Disbursement Date"
          value={disbursementDate}
          onChange={(e) => setDisbursementDate(e.target.value)}
          fullWidth
          margin="normal"
          variant="outlined"
        />
        <FormControl fullWidth margin="normal" variant="outlined">
          <InputLabel id="disbursement-method-label">Disbursement Method</InputLabel>
          <Select
            labelId="disbursement-method-label"
            value={disbursementMethod}
            onChange={(e) => setDisbursementMethod(e.target.value)}
            label="Disbursement Method"
          >
            <MenuItem value="ach">ACH</MenuItem>
            <MenuItem value="wire">Wire</MenuItem>
            <MenuItem value="check">Check</MenuItem>
            <MenuItem value="internal_transfer">Internal Transfer</MenuItem>
          </Select>
        </FormControl>
        <TextField
          label="Comments"
          value={comments}
          onChange={(e) => setComments(e.target.value)}
          fullWidth
          margin="normal"
          variant="outlined"
          multiline
          rows={4}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} color="primary" variant="contained">
          Create
        </Button>
      </DialogActions>
    </Dialog>
  );
};

/**
 * Dialog component for adding a note
 */
interface NoteDialogProps {
  open: boolean;
  onClose: () => void;
  onAdd: (noteData: FundingNoteCreateRequest) => void;
  fundingRequest: FundingRequest | undefined;
}

const NoteDialog: React.FC<NoteDialogProps> = ({ open, onClose, onAdd, fundingRequest }) => {
  const [noteType, setNoteType] = useState<string>('');
  const [noteText, setNoteText] = useState('');

  const handleSubmit = () => {
    if (fundingRequest) {
      const noteData: FundingNoteCreateRequest = {
        funding_request_id: fundingRequest.id,
        note_type: noteType as FundingNoteType,
        note_text: noteText,
      };
      onAdd(noteData);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} aria-labelledby="note-dialog-title">
      <DialogTitle id="note-dialog-title">Add Note</DialogTitle>
      <DialogContent>
        <FormControl fullWidth margin="normal" variant="outlined">
          <InputLabel id="note-type-label">Note Type</InputLabel>
          <Select
            labelId="note-type-label"
            value={noteType}
            onChange={(e) => setNoteType(e.target.value)}
            label="Note Type"
          >
            <MenuItem value="general">General</MenuItem>
            <MenuItem value="approval">Approval</MenuItem>
            <MenuItem value="rejection">Rejection</MenuItem>
            <MenuItem value="stipulation">Stipulation</MenuItem>
            <MenuItem value="disbursement">Disbursement</MenuItem>
            <MenuItem value="cancellation">Cancellation</MenuItem>
          </Select>
        </FormControl>
        <TextField
          label="Note Text"
          value={noteText}
          onChange={(e) => setNoteText(e.target.value)}
          fullWidth
          margin="normal"
          variant="outlined"
          multiline
          rows={4}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} color="primary" variant="contained">
          Add
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default FundingDetail;