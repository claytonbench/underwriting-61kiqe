# src/web/src/pages/qc/QCDetail.tsx
```typescript
import React, { useEffect, useCallback } from 'react'; // react v18.2.0
import { useParams, useNavigate } from 'react-router-dom'; // react-router-dom v6.14.0
import { useDispatch, useSelector } from 'react-redux'; // react-redux v8.1.1
import { Box, Button, Typography, Alert, Breadcrumbs, Link } from '@mui/material'; // @mui/material v5.14.0
import ArrowBack from '@mui/icons-material/ArrowBack'; // @mui/icons-material v5.14.0

import Page from '../../components/common/Page';
import QCReview from '../../components/QCReview';
import LoadingOverlay from '../../components/common/Loading';
import {
  fetchQCReviewDetailThunk,
  fetchQCReviewByApplicationThunk,
} from '../../store/thunks/qcThunks';
import {
  selectSelectedQCReview,
  selectLoading,
  selectError,
} from '../../store/slices/qcSlice';

/**
 * QCDetail Component
 *
 * This component displays detailed information about a Quality Control (QC) review
 * for a loan application. It allows QC personnel to review documents, verify
 * stipulations, complete checklist items, and make approval or rejection decisions
 * before funding.
 */
const QCDetail: React.FC = () => {
  // Initialize Redux hooks
  const dispatch = useDispatch();
  const qcReview = useSelector(selectSelectedQCReview);
  const loading = useSelector(selectLoading);
  const error = useSelector(selectError);

  // Initialize React Router hooks
  const { qcReviewId, applicationId } = useParams<{ qcReviewId?: string; applicationId?: string }>();
  const navigate = useNavigate();

  /**
   * Handler for back button click in the QC detail page
   */
  const handleBackClick = useCallback(() => {
    navigate('/qc'); // Navigate back to QC list page
  }, [navigate]);

  // Fetch QC review data when component mounts
  useEffect(() => {
    if (qcReviewId) {
      // Fetch QC review by ID
      dispatch(fetchQCReviewDetailThunk(qcReviewId));
    } else if (applicationId) {
      // Fetch QC review by application ID
      dispatch(fetchQCReviewByApplicationThunk(applicationId));
    }
  }, [dispatch, qcReviewId, applicationId]);

  return (
    <Page
      title="QC Review Details"
      actions={
        <Button
          variant="outlined"
          startIcon={<ArrowBack />}
          onClick={handleBackClick}
          aria-label="Back to QC List"
        >
          Back to QC List
        </Button>
      }
    >
      {/* Loading Overlay */}
      {loading && <LoadingOverlay isLoading={true} message="Loading QC Review Details..." />}

      {/* Error Alert */}
      {error && (
        <Alert severity="error">
          {error}
        </Alert>
      )}

      {/* Breadcrumbs */}
      <Breadcrumbs aria-label="breadcrumb">
        <Link underline="hover" color="inherit" href="/qc">
          QC
        </Link>
        <Typography color="text.primary">QC Review Details</Typography>
      </Breadcrumbs>

      {/* QC Review Component */}
      {qcReview && (
        <QCReview
          qcReviewId={qcReview.id}
          applicationId={qcReview.application_id}
        />
      )}
    </Page>
  );
};

export default QCDetail;