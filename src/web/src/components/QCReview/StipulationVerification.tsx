import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardActions, 
  Typography, 
  Button, 
  TextField, 
  Box, 
  Chip 
} from '@mui/material';
import { 
  CheckCircleOutline, 
  CancelOutlined, 
  RemoveCircleOutline 
} from '@mui/icons-material';

// Import custom hooks and types
import useStyles from './styles';
import { QCStipulationVerification, QCVerificationStatus } from '../../types/qc.types';
import useForm from '../../hooks/useForm';

/**
 * Props interface for the StipulationVerification component
 */
interface StipulationVerificationProps {
  stipulation: QCStipulationVerification;
  onVerify: (id: string, comments: string) => Promise<void>;
  onReject: (id: string, comments: string) => Promise<void>;
  onWaive: (id: string, comments: string) => Promise<void>;
  isReadOnly?: boolean;
}

/**
 * Component that renders and manages stipulation verification in the QC review process
 * Allows QC personnel to verify, reject, or waive stipulations with comments
 * 
 * @param props - Component props
 * @returns JSX.Element - Rendered component
 */
const StipulationVerification: React.FC<StipulationVerificationProps> = (props) => {
  const { stipulation, onVerify, onReject, onWaive, isReadOnly = false } = props;
  const classes = useStyles();
  const [loading, setLoading] = useState<boolean>(false);

  // Initialize form state for comments
  const { values, handleChange, setFieldValue } = useForm(
    { comments: stipulation.comments || '' },
    {},
    () => {}
  );

  // Set initial comments from stipulation when component mounts or stipulation changes
  useEffect(() => {
    setFieldValue('comments', stipulation.comments || '');
  }, [stipulation, setFieldValue]);

  /**
   * Handle verifying the stipulation
   */
  const handleVerify = async (): Promise<void> => {
    if (loading || isReadOnly) return;
    
    setLoading(true);
    try {
      await onVerify(stipulation.id, values.comments);
    } catch (error) {
      console.error('Error verifying stipulation:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle rejecting the stipulation
   */
  const handleReject = async (): Promise<void> => {
    if (loading || isReadOnly) return;
    
    setLoading(true);
    try {
      await onReject(stipulation.id, values.comments);
    } catch (error) {
      console.error('Error rejecting stipulation:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle waiving the stipulation
   */
  const handleWaive = async (): Promise<void> => {
    if (loading || isReadOnly) return;
    
    setLoading(true);
    try {
      await onWaive(stipulation.id, values.comments);
    } catch (error) {
      console.error('Error waiving stipulation:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Get card class based on stipulation status
   */
  const getCardClass = (): string => {
    switch (stipulation.status) {
      case QCVerificationStatus.VERIFIED:
        return classes.verifiedCard;
      case QCVerificationStatus.REJECTED:
        return classes.rejectedCard;
      case QCVerificationStatus.WAIVED:
        return classes.waivedCard;
      default:
        return classes.unverifiedCard;
    }
  };

  /**
   * Get chip props based on stipulation status
   */
  const getStatusChipProps = () => {
    switch (stipulation.status) {
      case QCVerificationStatus.VERIFIED:
        return {
          label: 'Verified',
          className: `${classes.statusChip} ${classes.verifiedChip}`,
          icon: <CheckCircleOutline className={classes.verifiedIcon} />
        };
      case QCVerificationStatus.REJECTED:
        return {
          label: 'Rejected',
          className: `${classes.statusChip} ${classes.rejectedChip}`,
          icon: <CancelOutlined className={classes.rejectedIcon} />
        };
      case QCVerificationStatus.WAIVED:
        return {
          label: 'Waived',
          className: `${classes.statusChip} ${classes.waivedChip}`,
          icon: <RemoveCircleOutline className={classes.waivedIcon} />
        };
      default:
        return {
          label: 'Unverified',
          className: `${classes.statusChip} ${classes.unverifiedChip}`,
          icon: null
        };
    }
  };

  const statusChipProps = getStatusChipProps();

  return (
    <Card className={`${classes.stipulationCard} ${getCardClass()}`}>
      <CardHeader
        title={
          <Box display="flex" alignItems="center">
            <Typography variant="subtitle1" className={classes.stipulationTitle}>
              {stipulation.stipulation_description}
            </Typography>
            <Chip
              size="small"
              {...statusChipProps}
              icon={statusChipProps.icon}
            />
          </Box>
        }
      />
      <CardContent className={classes.cardContent}>
        {stipulation.comments && (
          <Typography variant="body2" color="textSecondary" gutterBottom>
            {stipulation.comments}
          </Typography>
        )}
        <TextField
          label="Verification Comments"
          name="comments"
          value={values.comments}
          onChange={handleChange}
          disabled={loading || isReadOnly}
          multiline
          rows={2}
          variant="outlined"
          size="small"
          fullWidth
          className={classes.commentsField}
        />
      </CardContent>
      {!isReadOnly && (
        <CardActions className={classes.cardActions}>
          <Button
            variant="contained"
            color="primary"
            size="small"
            onClick={handleVerify}
            disabled={loading || stipulation.status === QCVerificationStatus.VERIFIED}
            className={classes.actionButton}
            startIcon={<CheckCircleOutline />}
          >
            Verify
          </Button>
          <Button
            variant="contained"
            color="error"
            size="small"
            onClick={handleReject}
            disabled={loading || stipulation.status === QCVerificationStatus.REJECTED}
            className={classes.actionButton}
            startIcon={<CancelOutlined />}
          >
            Reject
          </Button>
          <Button
            variant="contained"
            color="warning"
            size="small"
            onClick={handleWaive}
            disabled={loading || stipulation.status === QCVerificationStatus.WAIVED}
            className={classes.actionButton}
            startIcon={<RemoveCircleOutline />}
          >
            Waive
          </Button>
        </CardActions>
      )}
    </Card>
  );
};

export default StipulationVerification;