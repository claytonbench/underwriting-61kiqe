import React, { useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  CheckCircleOutline,
  CancelOutlined,
  RadioButtonUnchecked,
  VisibilityOutlined,
  GetAppOutlined
} from '@mui/icons-material';

import useStyles from './styles';
import { DocumentVerification, QCVerificationStatus } from '../../types/qc.types';
import { Document, DocumentType } from '../../types/document.types';

/**
 * Props for the DocumentVerification component
 */
interface DocumentVerificationProps {
  documentVerification: DocumentVerification;
  onVerify: (id: string, comments: string) => void;
  onReject: (id: string, comments: string) => void;
  isReadOnly?: boolean;
}

/**
 * Component that renders a document verification item in the QC review process.
 * Allows QC reviewers to verify or reject documents with comments during the loan 
 * application review process.
 */
const DocumentVerificationComponent: React.FC<DocumentVerificationProps> = ({
  documentVerification,
  onVerify,
  onReject,
  isReadOnly = false
}) => {
  const styles = useStyles();
  const [comments, setComments] = useState(documentVerification.comments || '');

  // Handle verify action
  const handleVerify = useCallback(() => {
    onVerify(documentVerification.id, comments);
  }, [documentVerification.id, comments, onVerify]);

  // Handle reject action
  const handleReject = useCallback(() => {
    onReject(documentVerification.id, comments);
  }, [documentVerification.id, comments, onReject]);

  // Handle comments change
  const handleCommentsChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setComments(event.target.value);
  };

  // Handle view document
  const handleViewDocument = useCallback(() => {
    if (documentVerification.document.download_url) {
      window.open(documentVerification.document.download_url, '_blank', 'noopener,noreferrer');
    }
  }, [documentVerification.document.download_url]);

  // Handle download document
  const handleDownloadDocument = useCallback(() => {
    if (documentVerification.document.download_url) {
      const link = document.createElement('a');
      link.href = documentVerification.document.download_url;
      link.download = documentVerification.document.file_name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }, [documentVerification.document.download_url, documentVerification.document.file_name]);

  // Determine card style based on verification status
  let cardClassName = `${styles.documentCard} `;
  let statusIcon = null;

  switch (documentVerification.status) {
    case QCVerificationStatus.VERIFIED:
      cardClassName += styles.verifiedCard;
      statusIcon = (
        <CheckCircleOutline 
          className={`${styles.statusIcon} ${styles.verifiedIcon}`} 
          fontSize="small" 
          aria-label="Verified"
        />
      );
      break;
    case QCVerificationStatus.REJECTED:
      cardClassName += styles.rejectedCard;
      statusIcon = (
        <CancelOutlined 
          className={`${styles.statusIcon} ${styles.rejectedIcon}`} 
          fontSize="small" 
          aria-label="Rejected"
        />
      );
      break;
    default:
      cardClassName += styles.unverifiedCard;
      statusIcon = (
        <RadioButtonUnchecked 
          className={`${styles.statusIcon} ${styles.unverifiedIcon}`} 
          fontSize="small" 
          aria-label="Unverified"
        />
      );
  }

  return (
    <Card className={cardClassName}>
      <CardContent className={styles.cardContent}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center">
            {statusIcon}
            <Typography 
              variant="subtitle1" 
              className={styles.documentTitle}
              component="div"
            >
              {documentVerification.document.document_type}
            </Typography>
          </Box>
          <Box>
            <Tooltip title="View Document">
              <IconButton 
                size="small" 
                onClick={handleViewDocument}
                aria-label="View document"
              >
                <VisibilityOutlined fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Download Document">
              <IconButton 
                size="small" 
                onClick={handleDownloadDocument}
                aria-label="Download document"
              >
                <GetAppOutlined fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        
        <Typography variant="body2" color="textSecondary">
          {documentVerification.document.file_name}
        </Typography>
        
        <TextField
          label="Verification Comments"
          multiline
          rows={3}
          value={comments}
          onChange={handleCommentsChange}
          fullWidth
          variant="outlined"
          className={styles.commentsField}
          disabled={isReadOnly}
          aria-label="Verification comments"
          placeholder="Add comments about document verification here"
        />
        
        {!isReadOnly && (
          <Box className={styles.documentActions}>
            <Button
              variant="outlined"
              color="error"
              className={styles.actionButton}
              onClick={handleReject}
              startIcon={<CancelOutlined />}
              disabled={documentVerification.status === QCVerificationStatus.REJECTED}
              aria-label="Reject document"
            >
              Reject
            </Button>
            <Button
              variant="outlined"
              color="success"
              className={styles.actionButton}
              onClick={handleVerify}
              startIcon={<CheckCircleOutline />}
              disabled={documentVerification.status === QCVerificationStatus.VERIFIED}
              aria-label="Verify document"
            >
              Verify
            </Button>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default DocumentVerificationComponent;