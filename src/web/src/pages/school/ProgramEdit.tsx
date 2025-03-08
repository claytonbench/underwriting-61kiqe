import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom'; // react-router-dom v6.0.0
import { useDispatch, useSelector } from 'react-redux'; // react-redux v8.0.0
import { Box, Card, CardContent, CircularProgress, Snackbar, Alert } from '@mui/material'; // @mui/material v5.14.0

import Page from '../../components/common/Page';
import Breadcrumbs from '../../components/common/Breadcrumbs';
import ProgramForm from '../../components/SchoolManagement/ProgramForm';
import { getProgramById, updateProgram } from '../../api/schools';
import { Program, ProgramDetail, ProgramUpdateRequest } from '../../types/school.types';
import { usePermissions } from '../../hooks/usePermissions';
import { fetchProgramById as fetchProgram, updateExistingProgram, selectSelectedProgram, selectSchoolLoading } from '../../store/slices/schoolSlice';

/**
 * Component that provides a form for editing an existing program
 * @returns Rendered program editing page
 */
const ProgramEdit: React.FC = () => {
  // Extract programId from URL parameters
  const { id: programId } = useParams<{ id: string }>();

  // Initialize state for notifications and loading
  const [notification, setNotification] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });

  // Initialize Redux dispatch and selectors
  const dispatch = useDispatch();
  const selectedProgram = useSelector(selectSelectedProgram);
  const loading = useSelector(selectSchoolLoading);

  // Check user permissions
  const { checkPermission } = usePermissions();
  const canEditProgram = checkPermission('program:edit');

  // Initialize navigation
  const navigate = useNavigate();

  // Fetch program details on component mount
  useEffect(() => {
    if (programId) {
      dispatch(fetchProgram(programId));
    }
  }, [dispatch, programId]);

  /**
   * Handles form submission to update an existing program
   * @param programData Program data
   */
  const handleSubmit = async (programData: ProgramUpdateRequest) => {
    setNotification({ open: false, message: '', severity: 'success' });
    if (!programId) {
      setNotification({ open: true, message: 'Program ID is missing.', severity: 'error' });
      return;
    }

    try {
      setNotification({ open: false, message: '', severity: 'success' });
      const result = await dispatch(
        updateExistingProgram({
          programId: programId,
          programData: programData,
        })
      );

      if (updateExistingProgram.fulfilled.match(result)) {
        setNotification({ open: true, message: 'Program updated successfully!', severity: 'success' });
        navigate(`/programs/${programId}`);
      } else {
        setNotification({ open: true, message: 'Failed to update program.', severity: 'error' });
      }
    } catch (error: any) {
      console.error('Error updating program:', error);
      setNotification({ open: true, message: error?.message || 'An unexpected error occurred', severity: 'error' });
    }
  };

  /**
   * Handles cancellation of program editing
   */
  const handleCancel = () => {
    if (programId) {
      navigate(`/programs/${programId}`);
    } else {
      navigate('/programs');
    }
  };

  // Create breadcrumb items
  const breadcrumbItems = [
    { label: 'Programs', path: '/programs' },
    { label: selectedProgram?.name || 'Program Details', path: `/programs/${programId}` },
    { label: 'Edit', path: `/programs/${programId}/edit` },
  ];

  // Render loading indicator while fetching program data
  if (loading || !selectedProgram) {
    return (
      <Page title="Edit Program">
        <Box display="flex" justifyContent="center" alignItems="center" height="200px">
          <CircularProgress />
        </Box>
      </Page>
    );
  }

  // Render the component
  return (
    <Page title="Edit Program" description="Edit an existing educational program" >
      <Breadcrumbs breadcrumbs={breadcrumbItems} />
      <Card>
        <CardContent>
          <ProgramForm
            program={selectedProgram}
            schoolId={selectedProgram.school_id}
            onSuccess={(program: Program) => {
              setNotification({ open: true, message: 'Program updated successfully!', severity: 'success' });
              navigate(`/programs/${program.id}`);
            }}
            onCancel={handleCancel}
          />
        </CardContent>
      </Card>

      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setNotification({ ...notification, open: false })} severity={notification.severity} sx={{ width: '100%' }}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Page>
  );
};

export default ProgramEdit;