import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Box, CircularProgress } from '@mui/material';

import Page from '../../components/common/Page';
import ProgramForm from '../../components/SchoolManagement/ProgramForm';
import { Program } from '../../types/school.types';
import { selectSchoolLoading } from '../../store/slices/schoolSlice';

/**
 * Component for creating a new educational program within a school.
 * Renders a form interface for entering program details including name, 
 * description, duration, tuition amount, and effective date.
 * Handles the submission process and redirects users after successful creation.
 */
const ProgramNew: React.FC = () => {
  // Get the school ID from URL parameters
  const { schoolId } = useParams<{ schoolId: string }>();
  
  // Initialize navigation and Redux hooks
  const navigate = useNavigate();
  const dispatch = useDispatch();
  
  // Get loading state from Redux store
  const loading = useSelector(selectSchoolLoading);

  /**
   * Handler for successful program creation
   * Redirects to the program list page for the school
   * @param program - The newly created program
   */
  const handleSuccess = (program: Program) => {
    // Redirect to the program list for the school
    navigate(`/schools/${schoolId}/programs`);
  };

  /**
   * Handler for form cancellation
   * Navigates back to the program list or school detail page
   */
  const handleCancel = () => {
    // Return to the programs list for this school
    navigate(`/schools/${schoolId}/programs`);
  };

  // If schoolId is not provided, show an error
  if (!schoolId) {
    return (
      <Page title="Error" description="School ID is required to create a program">
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          School ID is missing. Please go back and try again.
        </Box>
      </Page>
    );
  }

  return (
    <Page 
      title="Add New Program" 
      description="Create a new educational program with details including name, duration, tuition amount, and effective date"
    >
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : (
        <ProgramForm
          program={null} // null indicates new program creation
          schoolId={schoolId}
          onSuccess={handleSuccess}
          onCancel={handleCancel}
        />
      )}
    </Page>
  );
};

export default ProgramNew;