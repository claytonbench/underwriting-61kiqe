# src/web/src/pages/school/SchoolAdminDashboard.tsx
```tsx
import React, { useEffect, useState } from 'react'; // React v18.0+, useEffect, useState
import { useNavigate } from 'react-router-dom'; // react-router-dom
import { useDispatch, useSelector } from 'react-redux'; // react-redux
import { Grid, Typography, Button, Box, Divider } from '@mui/material'; // Material-UI v5.14.0+, Grid, Typography, Button, Box, Divider
import { Add as AddIcon, Visibility as VisibilityIcon, Edit as EditIcon } from '@mui/icons-material'; // Material-UI v5.14.0+, Add as AddIcon, Visibility as VisibilityIcon, Edit as EditIcon
import Page from '../../components/common/Page';
import Card from '../../components/common/Card';
import DataTable from '../../components/common/DataTable';
import StatusBadge from '../../components/common/StatusBadge';
import { useAuthContext } from '../../context/AuthContext';
import { fetchApplicationsBySchool, fetchApplicationCountsByStatus } from '../../store/thunks/applicationThunks';
import { getPendingSignatures } from '../../api/documents';
import { getSchoolPrograms } from '../../api/schools';
import { selectApplications, selectLoading as selectApplicationsLoading, selectTotalApplications } from '../../store/slices/applicationSlice';
import { ApplicationListItem, ApplicationStatus, ApplicationCountsByStatus } from '../../types/application.types';
import { SignatureRequest, DocumentType } from '../../types/document.types';
import { Program } from '../../types/school.types';
import { formatCurrency } from '../../utils/formatting';
import { formatDate } from '../../utils/date';

/**
 * Main component for the school administrator dashboard page
 * @returns Rendered dashboard page
 */
const SchoolAdminDashboard: React.FC = () => {
  // Get the current authenticated user from useAuthContext
  const { state: authState } = useAuthContext();
  const user = authState.user;

  // Get the school ID from the authenticated user's profile
  const schoolId = user?.schoolId;

  // Initialize state for application counts, pending signatures, and programs
  const [applicationCounts, setApplicationCounts] = useState<ApplicationCountsByStatus | null>(null);
  const [pendingSignatures, setPendingSignatures] = useState<SignatureRequest[]>([]);
  const [programs, setPrograms] = useState<Program[]>([]);

  // Initialize state for loading indicators for each data section
  const [countsLoading, setCountsLoading] = useState(true);
  const [signaturesLoading, setSignaturesLoading] = useState(true);
  const [programsLoading, setProgramsLoading] = useState(true);

  // Get Redux dispatch function and selectors for application data
  const dispatch = useDispatch();
  const applications = useSelector(selectApplications);
  const applicationsLoading = useSelector(selectApplicationsLoading);
  const totalApplications = useSelector(selectTotalApplications);

  // Get navigation function for routing
  const navigate = useNavigate();

  /**
   * Fetches recent applications for the school
   */
  const fetchApplicationData = () => {
    if (!schoolId) return;
    dispatch(fetchApplicationsBySchool({ schoolId }));
  };

  /**
   * Fetches application counts by status for the school
   */
  const fetchApplicationCounts = async () => {
    if (!schoolId) return;
    setCountsLoading(true);
    try {
      const counts = await dispatch(fetchApplicationCountsByStatus({ schoolId })).unwrap();
      setApplicationCounts(counts);
    } catch (error) {
      console.error('Failed to fetch application counts:', error);
    } finally {
      setCountsLoading(false);
    }
  };

  /**
   * Fetches documents requiring signature for the school administrator
   */
  const fetchPendingDocuments = async () => {
    if (!schoolId) return;
    setSignaturesLoading(true);
    try {
      const response = await getPendingSignatures();
      if (response.success && response.data) {
        // Filter signature requests for those where the signer is the current user
        const filteredSignatures = response.data.filter(signatureRequest => signatureRequest.signer_type === 'school' && signatureRequest.signer_id === user?.id);
        setPendingSignatures(filteredSignatures);
      } else {
        console.error('Failed to fetch pending signatures:', response.message);
      }
    } catch (error) {
      console.error('Failed to fetch pending signatures:', error);
    } finally {
      setSignaturesLoading(false);
    }
  };

  /**
   * Fetches program data for the school
   */
  const fetchProgramData = async () => {
    if (!schoolId) return;
    setProgramsLoading(true);
    try {
      const response = await getSchoolPrograms(schoolId, { page: 1, pageSize: 100 });
      if (response.success && response.data) {
        setPrograms(response.data.results);
      } else {
        console.error('Failed to fetch school programs:', response.message);
      }
    } catch (error) {
      console.error('Failed to fetch school programs:', error);
    } finally {
      setProgramsLoading(false);
    }
  };

  // Fetch data when component mounts
  useEffect(() => {
    fetchApplicationData();
    fetchApplicationCounts();
    fetchPendingDocuments();
    fetchProgramData();
  }, [schoolId, dispatch]);

  /**
   * Handles click on the View button for an application
   * @param application ApplicationListItem
   */
  const handleViewApplication = (application: ApplicationListItem) => {
    navigate(`/applications/${application.id}`);
  };

  /**
   * Handles click on the Sign button for a document
   * @param signatureRequest SignatureRequest
   */
  const handleSignDocument = (signatureRequest: SignatureRequest) => {
    navigate(`/documents/sign/${signatureRequest.id}`);
  };

  /**
   * Handles click on the View button for a program
   * @param program Program
   */
  const handleViewProgram = (program: Program) => {
    navigate(`/schools/${schoolId}/programs/${program.id}`);
  };

  /**
   * Handles click on the New Application button
   */
  const handleNewApplication = () => {
    navigate('/applications/new');
  };

  // Define columns for the recent applications table
  const applicationColumns = React.useMemo(
    () => [
      { field: 'borrower_name', headerName: 'Student', width: 200 },
      { field: 'program_name', headerName: 'Program', width: 200 },
      { field: 'requested_amount', headerName: 'Amount', width: 120, align: 'right', render: (value: number) => formatCurrency(value) },
      { field: 'submission_date', headerName: 'Received', width: 120, render: (value: string) => formatDate(value, 'MM/DD/YYYY') },
      { field: 'status', headerName: 'Status', width: 150, render: (value: ApplicationStatus) => <StatusBadge status={value} /> },
      {
        field: 'actions', headerName: 'Action', width: 100, align: 'center',
        render: (_value: any, row: ApplicationListItem) => (
          <Button startIcon={<VisibilityIcon />} size="small" onClick={() => handleViewApplication(row)}>
            View
          </Button>
        ),
      },
    ],
    [handleViewApplication]
  );

  // Define columns for the documents requiring signature table
  const documentColumns = React.useMemo(
    () => [
      { field: 'signer_name', headerName: 'Signer', width: 200 },
      { field: 'document_type', headerName: 'Document', width: 200 },
      {
        field: 'actions', headerName: 'Action', width: 100, align: 'center',
        render: (_value: any, row: SignatureRequest) => (
          <Button startIcon={<EditIcon />} size="small" onClick={() => handleSignDocument(row)}>
            Sign
          </Button>
        ),
      },
    ],
    [handleSignDocument]
  );

  // Define columns for the program summary table
  const programColumns = React.useMemo(
    () => [
      { field: 'name', headerName: 'Program', width: 250 },
      { field: 'duration_weeks', headerName: 'Duration (Weeks)', width: 120, align: 'center' },
      { field: 'current_tuition', headerName: 'Tuition', width: 120, align: 'right', render: (value: number) => formatCurrency(value) },
      {
        field: 'actions', headerName: 'Action', width: 100, align: 'center',
        render: (_value: any, row: Program) => (
          <Button startIcon={<VisibilityIcon />} size="small" onClick={() => handleViewProgram(row)}>
            View
          </Button>
        ),
      },
    ],
    [handleViewProgram]
  );

  /**
   * Renders the application overview section
   */
  const renderApplicationOverview = () => {
    return (
      <Card title="Applications Overview" actions={<Button startIcon={<AddIcon />} onClick={handleNewApplication}>New Application</Button>}>
        {countsLoading ? (
          <Box display="flex" justifyContent="center" alignItems="center" height={100}>
            <Typography>Loading application counts...</Typography>
          </Box>
        ) : (
          <Grid container spacing={2} mb={2}>
            <Grid item xs={6} md={3}>
              <Typography variant="subtitle1">New: {applicationCounts?.draft}</Typography>
            </Grid>
            <Grid item xs={6} md={3}>
              <Typography variant="subtitle1">In Review: {applicationCounts?.in_review}</Typography>
            </Grid>
            <Grid item xs={6} md={3}>
              <Typography variant="subtitle1">Approved: {applicationCounts?.approved}</Typography>
            </Grid>
            <Grid item xs={6} md={3}>
              <Typography variant="subtitle1">Declined: {applicationCounts?.denied}</Typography>
            </Grid>
          </Grid>
        )}
        <Divider />
        <Box mt={2}>
          {applicationsLoading ? (
            <Box display="flex" justifyContent="center" alignItems="center" height={200}>
              <Typography>Loading recent applications...</Typography>
            </Box>
          ) : (
            <DataTable
              data={applications}
              columns={applicationColumns}
              totalItems={totalApplications}
              loading={applicationsLoading}
              emptyStateMessage="No applications found"
              pagination
              onPageChange={() => {}} // Add dummy function to avoid errors
              onPageSizeChange={() => {}} // Add dummy function to avoid errors
            />
          )}
        </Box>
      </Card>
    );
  };

  /**
   * Renders the documents requiring signature section
   */
  const renderDocumentsRequiringSignature = () => {
    return (
      <Card title="Documents Requiring Signature">
        {signaturesLoading ? (
          <Box display="flex" justifyContent="center" alignItems="center" height={100}>
            <Typography>Loading documents...</Typography>
          </Box>
        ) : pendingSignatures.length === 0 ? (
          <Box display="flex" justifyContent="center" alignItems="center" height={100}>
            <Typography>No documents requiring your signature</Typography>
          </Box>
        ) : (
          <DataTable
            data={pendingSignatures}
            columns={documentColumns}
            loading={signaturesLoading}
            emptyStateMessage="No documents requiring signature"
            pagination={false}
          />
        )}
      </Card>
    );
  };

  /**
   * Renders the program summary section
   */
  const renderProgramSummary = () => {
    return (
      <Card title="Program Summary">
        {programsLoading ? (
          <Box display="flex" justifyContent="center" alignItems="center" height={100}>
            <Typography>Loading programs...</Typography>
          </Box>
        ) : programs.length === 0 ? (
          <Box display="flex" justifyContent="center" alignItems="center" height={100}>
            <Typography>No programs found</Typography>
          </Box>
        ) : (
          <DataTable
            data={programs}
            columns={programColumns}
            loading={programsLoading}
            emptyStateMessage="No programs found"
            pagination={false}
          />
        )}
      </Card>
    );
  };

  // Render the dashboard with application overview, documents requiring signature, and program summary sections
  return (
    <Page title="School Administrator Dashboard">
      <Grid container spacing={2}>
        <Grid item xs={12}>
          {renderApplicationOverview()}
        </Grid>
        <Grid item xs={12}>
          {renderDocumentsRequiringSignature()}
        </Grid>
        <Grid item xs={12}>
          {renderProgramSummary()}
        </Grid>
      </Grid>
    </Page>
  );
};

export default SchoolAdminDashboard;