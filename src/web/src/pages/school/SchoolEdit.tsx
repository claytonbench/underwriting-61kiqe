# src/web/src/pages/school/SchoolEdit.tsx
```tsx
import React, { useEffect } from 'react'; // version: ^18.2.0
import { useNavigate, useParams } from 'react-router-dom'; // version: ^6.16.0
import { useDispatch, useSelector } from 'react-redux'; // version: ^8.1.1
import { Button } from '@mui/material'; // version: ^5.14.0
import ArrowBack from '@mui/icons-material/ArrowBack'; // version: ^5.14.0

import Page from '../../components/common/Page';
import SchoolForm from '../../components/SchoolManagement/SchoolForm';
import LoadingOverlay from '../../components/common/Loading/LoadingOverlay';
import {
  loadSchoolDetails,
  updateSchool,
} from '../../store/actions/schoolActions';
import {
  selectSelectedSchool,
  selectSchoolLoading,
  selectSchoolError,
} from '../../store/slices/schoolSlice';
import { School } from '../../types/school.types';

/**
 * Page component for editing an existing school
 *
 * Fetches school details, renders a form for editing, and handles the update process.
 *
 * @returns {JSX.Element} Rendered school edit page
 */
const SchoolEdit: React.FC = () => {
  // Initialize navigate function using useNavigate hook
  const navigate = useNavigate();

  // Extract schoolId from URL parameters using useParams hook
  const { schoolId } = useParams<{ schoolId: string }>();

  // Initialize Redux dispatch function using useDispatch hook
  const dispatch = useDispatch();

  // Select school data, loading state, and error state from Redux store using useSelector
  const selectedSchool = useSelector(selectSelectedSchool);
  const loading = useSelector(selectSchoolLoading);
  const error = useSelector(selectSchoolError);

  // Use useEffect to fetch school details when component mounts or schoolId changes
  useEffect(() => {
    if (schoolId) {
      dispatch(loadSchoolDetails(schoolId));
    }
  }, [dispatch, schoolId]);

  /**
   * Defines handleSubmitSuccess function to handle successful form submission
   * @param {School} updatedSchool - The updated school object
   */
  const handleSubmitSuccess = (updatedSchool: School) => {
    // Navigate to the school details page after successful update
    navigate(`/schools/${updatedSchool.id}`);
  };

  /**
   * Defines handleCancel function to navigate back to school list or detail page
   */
  const handleCancel = () => {
    // Navigate back to the school list page
    navigate('/schools');
  };

  return (
    <Page
      title="Edit School"
      actions={
        <Button
          variant="outlined"
          startIcon={<ArrowBack />}
          onClick={handleCancel}
          data-testid="back-button"
        >
          Back
        </Button>
      }
    >
      {/* Render LoadingOverlay component when loading is true */}
      <LoadingOverlay isLoading={loading} message="Loading school details..." />

      {/* Render SchoolForm component with selected school data and handlers */}
      {selectedSchool && (
        <SchoolForm
          school={selectedSchool}
          onSubmitSuccess={handleSubmitSuccess}
          onCancel={handleCancel}
        />
      )}

      {/* Display error message if there is an error fetching school data */}
      {error && <p>Error: {error}</p>}
    </Page>
  );
};

export default SchoolEdit;