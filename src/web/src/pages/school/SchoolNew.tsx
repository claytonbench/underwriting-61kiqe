import React, { useState } from 'react'; // version: ^18.2.0
import { useNavigate } from 'react-router-dom'; // version: ^6.14.0
import { useDispatch } from 'react-redux'; // version: ^8.1.1
import { Box, Typography, Alert } from '@mui/material'; // version: ^5.14.0

import Page from '../../components/common/Page';
import SchoolForm from '../../components/SchoolManagement/SchoolForm';
import { School } from '../../types/school.types';
import { createSchool } from '../../store/actions/schoolActions';

/**
 * Component for creating a new school
 *
 * This component provides a user interface for system administrators to create new
 * school entities within the loan management system. It includes a form for entering
 * school details and handles the submission process.
 *
 * @returns Rendered new school page
 */
const SchoolNew: React.FC = () => {
  // Initialize state for loading and error
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Get the navigate function for routing
  const navigate = useNavigate();

  // Get the dispatch function for Redux actions
  const dispatch = useDispatch();

  /**
   * Handles form submission to create a new school
   *
   * @param school - The school data to be created
   */
  const handleSubmit = async (school: School) => {
    // Set loading state to true
    setLoading(true);

    // Clear any previous errors
    setError(null);

    try {
      // Dispatch createSchool action with the school data
      await dispatch(createSchool(school)).unwrap();

      // On success, navigate to the schools list page
      navigate('/schools');
    } catch (err: any) {
      // On error, set the error state and loading to false
      setError(err.message || 'Failed to create school');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handles cancellation of school creation
   * Navigates back to the schools list page
   */
  const handleCancel = () => {
    // Navigate back to the schools list page
    navigate('/schools');
  };

  // Render the Page component with appropriate title
  return (
    <Page title="Create New School">
      {/* Display loading indicator when submitting */}
      {loading && (
        <Box>
          <Typography variant="body1">Submitting...</Typography>
        </Box>
      )}

      {/* Display error message if submission fails */}
      {error && (
        <Alert severity="error">
          {error}
        </Alert>
      )}

      {/* Render the SchoolForm component for creating a new school */}
      <SchoolForm
        school={null}
        onSubmitSuccess={handleSubmit}
        onCancel={handleCancel}
      />
    </Page>
  );
};

export default SchoolNew;