import React, { useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
} from '@mui/material';
import {
  CheckCircleOutline,
  CancelOutlined,
  RadioButtonUnchecked
} from '@mui/icons-material';

import useStyles from './styles';
import {
  QCChecklistItem,
  QCVerificationStatus,
} from '../../types/qc.types';

interface ChecklistItemProps {
  checklistItem: QCChecklistItem;
  onVerify: (itemId: string, comments: string) => void;
  onReject: (itemId: string, comments: string) => void;
  isReadOnly?: boolean;
}

/**
 * Component that renders a checklist item in the QC review process with verification controls
 */
const ChecklistItem: React.FC<ChecklistItemProps> = ({
  checklistItem,
  onVerify,
  onReject,
  isReadOnly = false
}) => {
  const classes = useStyles();
  const [comments, setComments] = useState(checklistItem.comments || '');

  const handleVerify = useCallback(() => {
    onVerify(checklistItem.id, comments);
  }, [checklistItem.id, comments, onVerify]);

  const handleReject = useCallback(() => {
    onReject(checklistItem.id, comments);
  }, [checklistItem.id, comments, onReject]);

  const handleCommentsChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setComments(event.target.value);
  };

  // Determine card class based on status
  let cardClass = classes.checklistCard;
  switch (checklistItem.status) {
    case QCVerificationStatus.VERIFIED:
      cardClass = `${cardClass} ${classes.verifiedCard}`;
      break;
    case QCVerificationStatus.REJECTED:
      cardClass = `${cardClass} ${classes.rejectedCard}`;
      break;
    default:
      cardClass = `${cardClass} ${classes.unverifiedCard}`;
  }

  // Render status icon based on status
  const getStatusIcon = () => {
    switch (checklistItem.status) {
      case QCVerificationStatus.VERIFIED:
        return <CheckCircleOutline className={`${classes.statusIcon} ${classes.verifiedIcon}`} aria-hidden="true" />;
      case QCVerificationStatus.REJECTED:
        return <CancelOutlined className={`${classes.statusIcon} ${classes.rejectedIcon}`} aria-hidden="true" />;
      default:
        return <RadioButtonUnchecked className={`${classes.statusIcon} ${classes.unverifiedIcon}`} aria-hidden="true" />;
    }
  };

  return (
    <Card 
      className={cardClass} 
      elevation={1}
      tabIndex={0}
      role="region"
      aria-label={`Checklist item: ${checklistItem.item_text} - Status: ${checklistItem.status}`}
    >
      <CardContent className={classes.cardContent}>
        <Box display="flex" alignItems="center">
          {getStatusIcon()}
          <Typography 
            variant="body1" 
            className={classes.checklistTitle}
          >
            {checklistItem.item_text}
          </Typography>
        </Box>
        
        <TextField
          label="Comments"
          variant="outlined"
          fullWidth
          multiline
          rows={2}
          className={classes.commentsField}
          value={comments}
          onChange={handleCommentsChange}
          disabled={isReadOnly}
          aria-label="Verification comments"
          placeholder="Add verification notes here..."
        />
        
        {!isReadOnly && (
          <Box display="flex" justifyContent="flex-end" mt={2}>
            <Button
              variant="contained"
              color="error"
              onClick={handleReject}
              className={classes.actionButton}
              disabled={checklistItem.status === QCVerificationStatus.REJECTED}
              aria-label="Reject checklist item"
            >
              Reject
            </Button>
            <Button
              variant="contained"
              color="primary"
              onClick={handleVerify}
              className={classes.actionButton}
              disabled={checklistItem.status === QCVerificationStatus.VERIFIED}
              aria-label="Verify checklist item"
            >
              Verify
            </Button>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default ChecklistItem;