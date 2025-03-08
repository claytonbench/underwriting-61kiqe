import React from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Divider, 
  FormControlLabel, 
  Checkbox, 
  Alert 
} from '@mui/material';
import useStyles from './styles';
import CustomCard from '../common/Card/Card';
import StatusBadge from '../common/StatusBadge/StatusBadge';
import { formatCurrency } from '../../utils/formatting';
import { formatDate } from '../../utils/date';
import { ApplicationFormData } from '../../types/application.types';

/**
 * Props interface for the ReviewSubmitStep component
 */
interface ReviewSubmitStepProps {
  /**
   * Complete form data from all previous steps
   */
  formData: ApplicationFormData;
  /**
   * Whether the terms and conditions have been accepted
   */
  termsAccepted: boolean;
  /**
   * Callback function when terms acceptance changes
   */
  onTermsChange: (accepted: boolean) => void;
  /**
   * Validation errors for the review step
   */
  errors?: Record<string, string>;
}

/**
 * Formats address fields into a single string representation
 * 
 * @param address_line1 - First line of the address
 * @param address_line2 - Optional second line of the address
 * @param city - City name
 * @param state - State code
 * @param zip_code - ZIP code
 * @returns Formatted address string
 */
const formatAddress = (
  address_line1: string,
  address_line2: string | null,
  city: string,
  state: string,
  zip_code: string
): string => {
  let formattedAddress = address_line1;
  if (address_line2) {
    formattedAddress += `\n${address_line2}`;
  }
  formattedAddress += `\n${city}, ${state} ${zip_code}`;
  return formattedAddress;
};

/**
 * Component that displays a summary of all application information for final review before submission
 */
const ReviewSubmitStep: React.FC<ReviewSubmitStepProps> = ({
  formData,
  termsAccepted,
  onTermsChange,
  errors = {}
}) => {
  const classes = useStyles();
  const { 
    borrower_info, 
    employment_info, 
    has_co_borrower, 
    co_borrower_info, 
    loan_details 
  } = formData;

  // Calculate the available loan amount
  const availableLoanAmount = 
    loan_details.tuition_amount - 
    loan_details.deposit_amount - 
    loan_details.other_funding;

  return (
    <Box className={classes.formSection}>
      <Typography variant="h5" className={classes.sectionTitle}>
        Review and Submit Application
      </Typography>
      <Typography variant="body1" gutterBottom>
        Please review all your information carefully before submitting. You can go back to make changes if needed.
      </Typography>

      {/* Borrower Information Section */}
      <CustomCard
        title="Borrower Information"
        sx={{ mt: 3 }}
      >
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Full Name</Typography>
            <Typography variant="body1">
              {`${borrower_info.first_name} ${borrower_info.middle_name || ''} ${borrower_info.last_name}`.trim()}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Social Security Number</Typography>
            <Typography variant="body1">
              {`XXX-XX-${borrower_info.ssn.slice(-4)}`}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Date of Birth</Typography>
            <Typography variant="body1">
              {formatDate(borrower_info.dob, 'MM/DD/YYYY')}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Citizenship Status</Typography>
            <StatusBadge status={borrower_info.citizenship_status} />
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Email</Typography>
            <Typography variant="body1">{borrower_info.email}</Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Phone</Typography>
            <Typography variant="body1">{borrower_info.phone}</Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2">Address</Typography>
            <Typography variant="body1" style={{ whiteSpace: 'pre-line' }}>
              {formatAddress(
                borrower_info.address_line1,
                borrower_info.address_line2,
                borrower_info.city,
                borrower_info.state,
                borrower_info.zip_code
              )}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Housing Status</Typography>
            <Typography variant="body1">
              {borrower_info.housing_status.replace(/_/g, ' ')}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Housing Payment</Typography>
            <Typography variant="body1">
              {formatCurrency(borrower_info.housing_payment)}
            </Typography>
          </Grid>
        </Grid>
      </CustomCard>

      {/* Employment Information Section */}
      <CustomCard
        title="Employment Information"
        sx={{ mt: 3 }}
      >
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Employment Type</Typography>
            <StatusBadge status={employment_info.employment_type} />
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Employer</Typography>
            <Typography variant="body1">{employment_info.employer_name}</Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Occupation</Typography>
            <Typography variant="body1">{employment_info.occupation}</Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Employer Phone</Typography>
            <Typography variant="body1">{employment_info.employer_phone}</Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Employment Duration</Typography>
            <Typography variant="body1">
              {`${employment_info.years_employed} years, ${employment_info.months_employed} months`}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Annual Income</Typography>
            <Typography variant="body1">
              {formatCurrency(employment_info.annual_income)}
            </Typography>
          </Grid>
          {employment_info.other_income > 0 && (
            <>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2">Other Income</Typography>
                <Typography variant="body1">
                  {formatCurrency(employment_info.other_income)}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2">Other Income Source</Typography>
                <Typography variant="body1">
                  {employment_info.other_income_source || 'Not specified'}
                </Typography>
              </Grid>
            </>
          )}
        </Grid>
      </CustomCard>

      {/* Co-Borrower Information Section (conditional) */}
      {has_co_borrower && co_borrower_info && (
        <CustomCard
          title="Co-Borrower Information"
          sx={{ mt: 3 }}
        >
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2">Relationship to Borrower</Typography>
              <Typography variant="body1">
                {co_borrower_info.relationship.replace(/_/g, ' ')}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2">Full Name</Typography>
              <Typography variant="body1">
                {`${co_borrower_info.first_name} ${co_borrower_info.middle_name || ''} ${co_borrower_info.last_name}`.trim()}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2">Social Security Number</Typography>
              <Typography variant="body1">
                {`XXX-XX-${co_borrower_info.ssn.slice(-4)}`}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2">Date of Birth</Typography>
              <Typography variant="body1">
                {formatDate(co_borrower_info.dob, 'MM/DD/YYYY')}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2">Citizenship Status</Typography>
              <StatusBadge status={co_borrower_info.citizenship_status} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2">Email</Typography>
              <Typography variant="body1">{co_borrower_info.email}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2">Phone</Typography>
              <Typography variant="body1">{co_borrower_info.phone}</Typography>
            </Grid>
            {!co_borrower_info.same_address && co_borrower_info.address_line1 && (
              <Grid item xs={12}>
                <Typography variant="subtitle2">Address</Typography>
                <Typography variant="body1" style={{ whiteSpace: 'pre-line' }}>
                  {formatAddress(
                    co_borrower_info.address_line1,
                    co_borrower_info.address_line2,
                    co_borrower_info.city || '',
                    co_borrower_info.state || '',
                    co_borrower_info.zip_code || ''
                  )}
                </Typography>
              </Grid>
            )}
            {co_borrower_info.same_address && (
              <Grid item xs={12}>
                <Typography variant="subtitle2">Address</Typography>
                <Typography variant="body1">Same as Borrower</Typography>
              </Grid>
            )}
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2">Employment Type</Typography>
              <StatusBadge status={co_borrower_info.employment_type} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2">Employer</Typography>
              <Typography variant="body1">{co_borrower_info.employer_name}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2">Occupation</Typography>
              <Typography variant="body1">{co_borrower_info.occupation}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2">Annual Income</Typography>
              <Typography variant="body1">
                {formatCurrency(co_borrower_info.annual_income)}
              </Typography>
            </Grid>
          </Grid>
        </CustomCard>
      )}

      {/* Loan Details Section */}
      <CustomCard
        title="Loan Details"
        sx={{ mt: 3 }}
      >
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">School</Typography>
            <Typography variant="body1">
              {/* School name would typically come from a lookup based on ID */}
              {loan_details.school_id}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Program</Typography>
            <Typography variant="body1">
              {/* Program name would typically come from a lookup based on ID */}
              {loan_details.program_id}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Start Date</Typography>
            <Typography variant="body1">
              {formatDate(loan_details.start_date, 'MM/DD/YYYY')}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Completion Date</Typography>
            <Typography variant="body1">
              {formatDate(loan_details.completion_date, 'MM/DD/YYYY')}
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle1" gutterBottom>
              Loan Amount Calculation
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Tuition Amount</Typography>
            <Typography variant="body1">
              {formatCurrency(loan_details.tuition_amount)}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Deposit Amount</Typography>
            <Typography variant="body1">
              {formatCurrency(loan_details.deposit_amount)}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Other Funding</Typography>
            <Typography variant="body1">
              {formatCurrency(loan_details.other_funding)}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Requested Loan Amount</Typography>
            <Typography variant="body1" fontWeight="bold">
              {formatCurrency(loan_details.requested_amount)}
            </Typography>
          </Grid>
        </Grid>
      </CustomCard>

      {/* Terms and Conditions */}
      <Box mt={3}>
        <FormControlLabel
          control={
            <Checkbox
              checked={termsAccepted}
              onChange={(e) => onTermsChange(e.target.checked)}
              name="termsAccepted"
              color="primary"
              aria-label="Accept terms and conditions"
            />
          }
          label="I accept the terms and conditions and confirm that all information provided is accurate."
        />
        {errors.termsAccepted && (
          <Alert severity="error" sx={{ mt: 1 }}>
            {errors.termsAccepted}
          </Alert>
        )}
      </Box>
    </Box>
  );
};

export default ReviewSubmitStep;