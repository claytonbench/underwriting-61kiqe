import React, { useState, useEffect } from 'react'; // react ^18.2.0
import { Box, Typography, CircularProgress, Alert } from '@mui/material'; // @mui/material ^5.14.0
import { useParams } from 'react-router-dom'; // react-router-dom ^6.14.0

import ApplicationReview from '../../components/ApplicationReview/ApplicationReview';
import Page from '../../components/common/Page';
import { createUnderwritingDecision } from '../../api/underwriting';
import useAuth from '../../hooks/useAuth';
import Breadcrumbs from '../../components/common/Breadcrumbs';
import { UnderwritingDecision } from '../../types/underwriting.types';

/**
 * Interface for route parameters, specifically for extracting the application ID
 */
interface RouteParams {
  applicationId: string;
}

/**
 * Interface for data required to submit an underwriting decision
 */
interface DecisionSubmitData {
  decision: UnderwritingDecision;
  comments: string;
  approvedAmount: number | null;
  interestRate: number | null;
  termMonths: number | null;
  reasons: Array<{ reason_code: string; is_primary: boolean; }>;
  stipulations: Array<{ stipulation_type: string; description: string; required_by_date: string; }>;
}

/**
 * A page component that provides a comprehensive interface for underwriters to review loan applications and make decisions
 * @returns A JSX element that renders the application review page
 */
const ApplicationReviewPage: React.FC = () => {
  // Extract the application ID from the URL parameters
  const { applicationId } = useParams<RouteParams>();

  // Initialize state variables for loading, error, and success states
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);

  // Get user information and permissions from the authentication context
  const { state: authState } = useAuth();

  /**
   * Handles the submission of an underwriting decision
   * @param data The underwriting decision data to submit
   */
  const handleDecisionSubmit = async (data: DecisionSubmitData) => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // Call the createUnderwritingDecision API function
      if (applicationId) {
        const response = await createUnderwritingDecision({
          application_id: applicationId,
          decision: data.decision,
          comments: data.comments,
          approved_amount: data.approvedAmount,
          interest_rate: data.interestRate,
          term_months: data.termMonths,
          reasons: data.reasons,
          stipulations: data.stipulations,
        });

        if (response.success) {
          setSuccess(true);
        } else {
          setError(response.message || 'Failed to submit decision');
        }
      } else {
        setError('Application ID is missing');
      }
    } catch (err) {
      setError('An unexpected error occurred while submitting the decision');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Determine if the user has read-only access based on their permissions
  const readOnly = authState.user && !authState.user.permissions.includes('underwriting.make_decisions');

  return (
    <Page title="Application Review">
      {/* Breadcrumbs navigation */}
      <Breadcrumbs breadcrumbs={[
        { path: '/underwriting/queue', label: 'Underwriting' },
        { path: `/underwriting/review/${applicationId}`, label: 'Application Review' }
      ]} />

      {/* Loading indicator */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Error message */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {/* Success message */}
      {success && (
        <Alert severity="success" sx={{ mt: 2 }}>
          Decision submitted successfully!
        </Alert>
      )}

      {/* Application Review Component */}
      {applicationId && (
        <ApplicationReview
          applicationId={applicationId}
          onSubmit={handleDecisionSubmit}
          readOnly={readOnly}
        />
      )}
    </Page>
  );
};

export default ApplicationReviewPage;