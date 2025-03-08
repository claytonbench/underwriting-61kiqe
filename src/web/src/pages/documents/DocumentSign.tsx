import React, { useEffect } from 'react'; // ^18.2.0
import { useParams, useNavigate } from 'react-router-dom'; // ^6.14.0
import { Box, Typography, Alert } from '@mui/material'; // ^5.14.0

import DocumentSigning from '../../components/DocumentSigning/DocumentSigning';
import Page from '../../components/common/Page/Page';
import LoadingSpinner from '../../components/common/Loading/LoadingSpinner';
import useAuth from '../../hooks/useAuth';
import { ERROR_PATHS } from '../../config/routes';

/**
 * Main page component for document signing functionality
 * 
 * @returns The rendered document signing page
 */
const DocumentSign: React.FC = () => {
  // LD1: Extract signatureRequestId from URL parameters using useParams
  const { signatureRequestId } = useParams<{ signatureRequestId: string }>();

  // LD1: Get navigation function using useNavigate
  const navigate = useNavigate();

  // LD1: Get authentication state and user information using useAuth hook
  const { state: authState } = useAuth();

  // LD1: Implement useEffect to verify user authentication and permissions
  useEffect(() => {
    // LD1: Check if the user is authenticated
    if (!authState.isAuthenticated && !authState.loading) {
      // LD1: Redirect to error page if user is not authenticated
      navigate(ERROR_PATHS.FORBIDDEN);
      return;
    }

    // LD1: Check if signatureRequestId is present
    if (!signatureRequestId && !authState.loading) {
      // LD1: Redirect to error page if signatureRequestId is missing
      navigate(ERROR_PATHS.NOT_FOUND);
      return;
    }
  }, [authState.isAuthenticated, authState.loading, navigate, signatureRequestId]);

  // LD1: Render Page component with appropriate title
  return (
    <Page title="Sign Document">
      {/* LD1: Render loading indicator while authentication state is being determined */}
      {authState.loading ? (
        <LoadingSpinner message="Verifying authentication..." />
      ) : (
        <>
          {/* LD1: Render error message if an error occurs */}
          {authState.error && (
            <Box p={3}>
              <Alert severity="error">{authState.error}</Alert>
            </Box>
          )}

          {/* LD1: Render DocumentSigning component with the signature request ID */}
          {signatureRequestId && (
            <DocumentSigning />
          )}
        </>
      )}
    </Page>
  );
};

// LD1: Export the DocumentSign component
export default DocumentSign;