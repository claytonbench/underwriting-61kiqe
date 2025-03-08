import React, { useState, useEffect } from 'react'; // react v^18.2.0
import { useParams, useNavigate } from 'react-router-dom'; // react-router-dom v^6.14.0
import { useDispatch, useSelector } from 'react-redux'; // react-redux v^8.1.0
import {
  Typography,
  Button,
  Grid,
  Divider,
  Box,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  IconButton,
  Tooltip
} from '@mui/material'; // @mui/material v^5.14.0
import { Edit, Delete, ArrowBack, Add, Warning } from '@mui/icons-material'; // @mui/icons-material v^5.14.0
import { DatePicker } from '@mui/x-date-pickers'; // @mui/x-date-pickers v^6.0.0
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'; // @mui/x-date-pickers v^6.0.0
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns'; // @mui/x-date-pickers v^6.0.0

import Page from '../../components/common/Page'; // src/web/src/components/common/Page/Page.tsx
import CustomCard from '../../components/common/Card'; // src/web/src/components/common/Card/Card.tsx
import LoadingSpinner from '../../components/common/Loading/LoadingSpinner'; // src/web/src/components/common/Loading/LoadingSpinner.tsx
import StatusBadge from '../../components/common/StatusBadge'; // src/web/src/components/common/StatusBadge/StatusBadge.tsx
import ProgramForm from '../../components/SchoolManagement/ProgramForm'; // src/web/src/components/SchoolManagement/ProgramForm.tsx
import usePermissions from '../../hooks/usePermissions'; // src/web/src/hooks/usePermissions.ts
import { formatCurrency, formatDate } from '../../utils/formatting'; // src/web/src/utils/formatting.ts
import {
  fetchProgramById,
  createNewProgramVersion,
  updateExistingProgram,
  deleteExistingProgram,
  selectSelectedProgram,
  selectSchoolLoading,
  selectSchoolError
} from '../../store/slices/schoolSlice'; // src/web/src/store/slices/schoolSlice.ts
import {
  Program,
 ProgramDetail,
  ProgramStatus,
  ProgramVersionCreateRequest
} from '../../types/school.types'; // src/web/src/types/school.types.ts

/**
 * Main component for displaying program details and managing program versions
 * @returns Rendered program detail page
 */
const ProgramDetail: React.FC = () => {
  // Extract programId from URL parameters using useParams
  const { programId } = useParams<{ programId: string }>();

  // Initialize Redux dispatch and navigation functions
  const dispatch = useDispatch();
  const navigate = useNavigate();

  // Get program data, loading state, and error state from Redux store
  const program = useSelector(selectSelectedProgram);
  const loading = useSelector(selectSchoolLoading);
  const error = useSelector(selectSchoolError);

  // Initialize state for edit mode, delete confirmation, and new version dialog
  const [isEditMode, setIsEditMode] = useState<boolean>(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<boolean>(false);
  const [showNewVersionDialog, setShowNewVersionDialog] = useState<boolean>(false);
  const [newVersionData, setNewVersionData] = useState<ProgramVersionCreateRequest>({ program_id: '', tuition_amount: '', effective_date: new Date() });

  // Check user permissions for editing and deleting programs
  const { hasPermission } = usePermissions();
  const canEdit = hasPermission('program:update');
  const canDelete = hasPermission('program:delete');

  // Fetch program data on component mount using programId
  useEffect(() => {
    if (programId) {
      dispatch(fetchProgramById(programId));
    }
  }, [dispatch, programId]);

  // Handle navigation back to program list
  const handleBack = () => {
    navigate(-1);
  };

  // Handle edit mode toggle
  const handleEditToggle = () => {
    setIsEditMode(!isEditMode);
  };

  // Handle program update submission
  const handleUpdateSubmit = (updatedProgram: Program) => {
    dispatch(updateExistingProgram({ programId: updatedProgram.id, programData: updatedProgram }));
    setIsEditMode(false);
  };

  // Handle delete confirmation dialog open/close
  const handleDeleteClick = () => {
    setShowDeleteConfirm(true);
  };

  const handleDeleteCancel = () => {
    setShowDeleteConfirm(false);
  };

  // Handle program deletion
  const handleDeleteConfirm = () => {
    if (programId) {
      dispatch(deleteExistingProgram(programId));
      navigate(-1);
      setShowDeleteConfirm(false);
    }
  };

  // Handle new version dialog open/close
  const handleNewVersionClick = () => {
    if (program) {
      setNewVersionData({ program_id: program.id, tuition_amount: '', effective_date: new Date() });
      setShowNewVersionDialog(true);
    }
  };

  const handleNewVersionCancel = () => {
    setShowNewVersionDialog(false);
  };

  // Handle new version submission
  const handleNewVersionChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setNewVersionData({ ...newVersionData, [event.target.name]: event.target.value });
  };

  const handleDateChange = (date: Date | null) => {
    if (date) {
      setNewVersionData({ ...newVersionData, effective_date: date });
    }
  };

  const handleNewVersionSubmit = () => {
    dispatch(createNewProgramVersion(newVersionData));
    setShowNewVersionDialog(false);
  };

  // Render loading spinner while data is loading
  if (loading) {
    return (
      <Page title="Program Details">
        <LoadingSpinner label="Loading program details..." />
      </Page>
    );
  }

  // Render error message if there's an error
  if (error) {
    return (
      <Page title="Program Details">
        <Typography color="error">Error: {error}</Typography>
      </Page>
    );
  }

  // Render program edit form if in edit mode
  if (isEditMode && program) {
    return (
      <Page
        title={`Edit Program: ${program.name}`}
        actions={
          <Button variant="contained" onClick={handleEditToggle}>
            Cancel Edit
          </Button>
        }
      >
        <ProgramForm
          program={program}
          schoolId={program.school_id}
          onSuccess={handleUpdateSubmit}
          onCancel={handleEditToggle}
        />
      </Page>
    );
  }

  // Render program details view with basic information, version history, and student statistics
  return (
    <Page
      title={program?.name || 'Program Details'}
      actions={
        <>
          <Tooltip title="Back to Programs">
            <IconButton color="primary" onClick={handleBack}>
              <ArrowBack />
            </IconButton>
          </Tooltip>
          {canEdit && (
            <Tooltip title="Edit Program">
              <IconButton color="primary" onClick={handleEditToggle}>
                <Edit />
              </IconButton>
            </Tooltip>
          )}
          {canDelete && (
            <Tooltip title="Delete Program">
              <IconButton color="error" onClick={handleDeleteClick}>
                <Delete />
              </IconButton>
            </Tooltip>
          )}
        </>
      }
    >
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <CustomCard title="Program Information">
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="body1">
                  <strong>Description:</strong> {program?.description}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body1">
                  <strong>Duration:</strong> {program?.duration_weeks} weeks ({program?.duration_hours} hours)
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body1">
                  <strong>School:</strong> {program?.school_name}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body1">
                  <strong>Status:</strong> <StatusBadge status={program?.status || ProgramStatus.ACTIVE} />
                </Typography>
              </Grid>
            </Grid>
          </CustomCard>
        </Grid>

        <Grid item xs={12} md={4}>
          <CustomCard title="Student Statistics">
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="h6">
                  {program?.student_count || 0} Students Enrolled
                </Typography>
              </Grid>
            </Grid>
          </CustomCard>
        </Grid>

        <Grid item xs={12}>
          <CustomCard
            title="Version History"
            actions={
              canEdit ? (
                <Button variant="contained" startIcon={<Add />} onClick={handleNewVersionClick}>
                  Add Version
                </Button>
              ) : null
            }
          >
            <TableContainer>
              <Table aria-label="program version history">
                <TableHead>
                  <TableRow>
                    <TableCell>Version</TableCell>
                    <TableCell align="right">Tuition Amount</TableCell>
                    <TableCell align="right">Effective Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {program?.versions?.map((version) => (
                    <TableRow key={version.id}>
                      <TableCell component="th" scope="row">
                        {version.version_number}
                      </TableCell>
                      <TableCell align="right">{formatCurrency(version.tuition_amount)}</TableCell>
                      <TableCell align="right">{formatDate(version.effective_date)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CustomCard>
        </Grid>
      </Grid>

      {/* Render delete confirmation dialog */}
      <Dialog
        open={showDeleteConfirm}
        onClose={handleDeleteCancel}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          <Warning color="warning" sx={{ marginRight: 1 }} />
          Confirm Delete
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Are you sure you want to delete this program? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDeleteConfirm} color="error" autoFocus>
            Confirm
          </Button>
        </DialogActions>
      </Dialog>

      {/* Render new version dialog */}
      <Dialog open={showNewVersionDialog} onClose={handleNewVersionCancel} aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">Create New Version</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Enter the new tuition amount and effective date for this program version.
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            id="tuition_amount"
            name="tuition_amount"
            label="Tuition Amount"
            type="number"
            fullWidth
            value={newVersionData.tuition_amount}
            onChange={handleNewVersionChange}
          />
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <DatePicker
              label="Effective Date"
              value={newVersionData.effective_date}
              onChange={handleDateChange}
              renderInput={(params) => <TextField {...params} margin="dense" fullWidth />}
            />
          </LocalizationProvider>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleNewVersionCancel} color="primary">
            Cancel
          </Button>
          <Button onClick={handleNewVersionSubmit} color="primary">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Page>
  );
};

export default ProgramDetail;