import React, { useState, useEffect, useCallback } from 'react'; // React v18.0+
import { Box, Button, Paper, Typography, CircularProgress, Alert } from '@mui/material'; // Material-UI v5.14.0
import { useNavigate, useParams } from 'react-router-dom'; // React Router v6.14.0

import BorrowerInfoStep from './BorrowerInfoStep';
import EmploymentInfoStep from './EmploymentInfoStep';
import CoBorrowerInfoStep from './CoBorrowerInfoStep';
import LoanDetailsStep from './LoanDetailsStep';
import ReviewSubmitStep from './ReviewSubmitStep';
import useStyles from './styles';
import CustomStepper from '../common/Stepper/Stepper';
import useForm, { FormState } from '../../hooks/useForm';
import { ApplicationFormData } from '../../types/application.types';
import { createApplication, saveApplicationDraft, submitApplication } from '../../api/applications';

/**
 * Interface for the properties of the ApplicationFormContainer component
 */
interface ApplicationFormContainerProps {
  /**
   * Initial values for the form, used when editing an existing application
   */
  initialValues?: Partial<ApplicationFormData>;
  /**
   * Callback function called after successful submission
   * @param applicationId - The ID of the submitted application
   */
  onSubmitSuccess?: (applicationId: string) => void;
  /**
   * Callback function called when cancelling the form
   */
  onCancel?: () => void;
}

/**
 * Container component that manages the multi-step loan application form process
 * Orchestrates the different form steps, handles navigation between steps,
 * manages form state, and handles form submission.
 */
const ApplicationFormContainer: React.FC<ApplicationFormContainerProps> = ({ initialValues, onSubmitSuccess, onCancel }) => {
  const classes = useStyles();
  
  // Initialize form state with useForm hook and initial values
  const { 
    values, 
    errors, 
    touched, 
    isSubmitting, 
    isValid, 
    handleChange, 
    handleBlur, 
    handleSubmit: handleFormSubmit, 
    setFieldValue, 
    setFieldTouched,
    setFieldError,
    validateField: validateStep
  } = useForm<ApplicationFormData>(
    {
      borrower_info: {
        first_name: '',
        middle_name: '',
        last_name: '',
        ssn: '',
        dob: '',
        email: '',
        phone: '',
        citizenship_status: '',
        address_line1: '',
        address_line2: '',
        city: '',
        state: '',
        zip_code: '',
        housing_status: '',
        housing_payment: 0,
      },
      employment_info: {
        employment_type: '',
        employer_name: '',
        occupation: '',
        employer_phone: '',
        years_employed: 0,
        months_employed: 0,
        annual_income: 0,
        other_income: 0,
        other_income_source: '',
      },
      has_co_borrower: false,
      co_borrower_info: null,
      loan_details: {
        school_id: '',
        program_id: '',
        start_date: '',
        completion_date: '',
        tuition_amount: 0,
        deposit_amount: 0,
        other_funding: 0,
        requested_amount: 0,
      },
    },
    {}, // Validation schema will be added later
    async (formValues) => {
      // This is intentionally left empty, the actual submission logic is in handleSubmit
    }
  );

  // Set up state for current step, loading state, error state, and terms acceptance
  const [activeStep, setActiveStep] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [termsAccepted, setTermsAccepted] = useState<boolean>(false);
  const [applicationId, setApplicationId] = useState<string | null>(null);

  // Get application ID from URL parameters if editing an existing application
  const { id: applicationIdParam } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // Load existing application data if editing
  useEffect(() => {
    if (applicationIdParam) {
      setApplicationId(applicationIdParam);
      // TODO: Fetch existing application data and populate the form
      // For now, we'll just log the ID
      console.log('Editing existing application with ID:', applicationIdParam);
    }
  }, [applicationIdParam]);

  // Define step labels for the stepper component
  const steps = [
    'Borrower Information',
    'Employment Information',
    'Co-Borrower Information',
    'Loan Details',
    'Review & Submit',
  ];

  /**
   * Handles advancing to the next step after validation
   */
  const handleNext = useCallback(() => {
    // Validate the current step using validateStep function
    const isValidStep = validateStep(activeStep, values, errors);

    if (isValidStep) {
      // If validation passes, increment activeStep
      setActiveStep((prevActiveStep) => {
        let nextStep = prevActiveStep + 1;
        // If on co-borrower step and has_co_borrower is false, skip to loan details step
        if (nextStep === 2 && !values.has_co_borrower) {
          nextStep = 3;
        }
        return nextStep;
      });
    }
  }, [activeStep, values, errors, validateStep]);

  /**
   * Handles going back to the previous step
   */
  const handleBack = useCallback(() => {
    setActiveStep((prevActiveStep) => {
      let nextStep = prevActiveStep - 1;
      // If on loan details step and has_co_borrower is false, skip back to employment step
      if (nextStep === 3 && !values.has_co_borrower) {
        nextStep = 1;
      }
      return nextStep;
    });
  }, [values.has_co_borrower]);

  /**
   * Handles final form submission
   */
  const handleSubmit = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      let appId = applicationId;

      // If editing existing application, update it with saveApplicationDraft
      if (applicationId) {
        await saveApplicationDraft(applicationId, values);
      } else {
        // If creating new application, create it with createApplication
        const createResponse = await createApplication({ form_data: values, created_by: 'user-id' }); // Replace 'user-id' with actual user ID
        if (createResponse.success && createResponse.data) {
          appId = createResponse.data.id;
          setApplicationId(createResponse.data.id);
        } else {
          throw new Error(createResponse.message || 'Failed to create application');
        }
      }

      // Submit the application with submitApplication
      if (appId) {
        await submitApplication(appId);
        // Call onSubmitSuccess callback with application ID
        onSubmitSuccess?.(appId);
        // Navigate to success page
        navigate(`/application-success/${appId}`);
      } else {
        throw new Error('Application ID is missing');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred during submission.');
    } finally {
      setIsLoading(false);
    }
  }, [applicationId, values, navigate, onSubmitSuccess]);

  /**
   * Handles saving the application as a draft
   */
  const handleSaveDraft = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      let appId = applicationId;

      // If editing existing application, update it with saveApplicationDraft
      if (applicationId) {
        await saveApplicationDraft(applicationId, values);
      } else {
        // If creating new application, create it with createApplication
        const createResponse = await createApplication({ form_data: values, created_by: 'user-id' }); // Replace 'user-id' with actual user ID
        if (createResponse.success && createResponse.data) {
          appId = createResponse.data.id;
          setApplicationId(createResponse.data.id);
        } else {
          throw new Error(createResponse.message || 'Failed to create application');
        }
      }

      setIsLoading(false);
    } catch (err: any) {
      setError(err.message || 'An error occurred while saving the draft.');
    } finally {
      setIsLoading(false);
    }
  }, [applicationId, values]);

  /**
   * Handles changes to terms and conditions acceptance
   * @param accepted - Whether the terms are accepted
   */
  const handleTermsChange = (accepted: boolean) => {
    setTermsAccepted(accepted);
  };

  /**
   * Renders the appropriate form step component based on activeStep
   */
  const renderCurrentStep = () => {
    switch (activeStep) {
      case 0:
        return (
          <BorrowerInfoStep
            values={values.borrower_info}
            errors={errors.borrower_info || {}}
            touched={touched.borrower_info || {}}
            handleChange={handleChange}
            handleBlur={handleBlur}
            setFieldValue={setFieldValue}
            setFieldTouched={setFieldTouched}
            isSubmitting={isSubmitting}
            isValid={isValid}
          />
        );
      case 1:
        return (
          <EmploymentInfoStep
            values={values.employment_info}
            errors={errors.employment_info || {}}
            touched={touched.employment_info || {}}
            handleChange={handleChange}
            handleBlur={handleBlur}
            setFieldValue={setFieldValue}
          />
        );
      case 2:
        return (
          <CoBorrowerInfoStep
            values={values}
            errors={errors}
            touched={touched}
            handleChange={handleChange}
            handleBlur={handleBlur}
            setFieldValue={setFieldValue}
            setFieldTouched={setFieldTouched}
            isSubmitting={isSubmitting}
            isValid={isValid}
          />
        );
      case 3:
        return (
          <LoanDetailsStep
            formState={{
              values: values.loan_details,
              errors: errors.loan_details || {},
              touched: touched.loan_details || {},
              handleChange,
              handleBlur,
              setFieldValue,
              setFieldError
            }}
          />
        );
      case 4:
        return (
          <ReviewSubmitStep
            formData={values}
            termsAccepted={termsAccepted}
            onTermsChange={handleTermsChange}
            errors={errors}
          />
        );
      default:
        return <Typography>Unknown step</Typography>;
    }
  };

  /**
   * Renders the navigation buttons for moving between steps
   */
  const renderNavigation = () => (
    <Box className={classes.buttonContainer}>
      <Button
        disabled={activeStep === 0 || isLoading}
        onClick={handleBack}
        className={classes.backButton}
      >
        Back
      </Button>
      <div>
        <Button
          disabled={isLoading}
          onClick={handleSaveDraft}
          className={classes.saveButton}
        >
          Save Draft
        </Button>
        {activeStep < steps.length - 1 ? (
          <Button
            variant="contained"
            color="primary"
            disabled={isLoading}
            onClick={handleNext}
            className={classes.nextButton}
          >
            Next
          </Button>
        ) : (
          <Button
            variant="contained"
            color="primary"
            disabled={isLoading || !termsAccepted}
            onClick={handleSubmit}
            className={classes.nextButton}
          >
            Submit
          </Button>
        )}
      </div>
    </Box>
  );

  return (
    <Box className={classes.formContainer}>
      <Paper className={classes.formPaper} elevation={3}>
        <Typography variant="h4" component="h2" gutterBottom>
          Loan Application
        </Typography>

        <CustomStepper activeStep={activeStep} steps={steps} />

        {isLoading && (
          <Box display="flex" justifyContent="center" alignItems="center">
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Alert severity="error" className={classes.errorText}>
            {error}
          </Alert>
        )}

        {renderCurrentStep()}
        {renderNavigation()}
      </Paper>
    </Box>
  );
};

export default ApplicationFormContainer;