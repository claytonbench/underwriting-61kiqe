import React from 'react';
import { Typography, Box } from '@mui/material';
import { 
  Timeline, 
  TimelineItem, 
  TimelineSeparator, 
  TimelineConnector, 
  TimelineContent, 
  TimelineDot,
  TimelineOppositeContent
} from '@mui/lab';
import { format } from 'date-fns';

import useStyles from './styles';
import CustomCard from '../common/Card';
import { ApplicationStatus, ApplicationStatusHistory } from '../../types/application.types';

/**
 * Props interface for the StatusTimeline component
 */
export interface StatusTimelineProps {
  statusHistory: ApplicationStatusHistory[];
  currentStatus: ApplicationStatus;
  className?: string;
}

/**
 * Determines the color for a timeline dot based on the application status
 */
const getStatusColor = (status: ApplicationStatus): 'success' | 'error' | 'warning' | 'info' | 'default' => {
  switch(status) {
    // Terminal success states
    case ApplicationStatus.FUNDED:
    case ApplicationStatus.FULLY_EXECUTED:
    case ApplicationStatus.READY_TO_FUND:
    case ApplicationStatus.QC_APPROVED:
    case ApplicationStatus.COMMITMENT_ACCEPTED:
    case ApplicationStatus.APPROVED:
      return 'success';
    
    // Terminal failure states
    case ApplicationStatus.DENIED:
    case ApplicationStatus.ABANDONED:
    case ApplicationStatus.DOCUMENTS_EXPIRED:
    case ApplicationStatus.COMMITMENT_DECLINED:
      return 'error';
    
    // States requiring attention
    case ApplicationStatus.REVISION_REQUESTED:
    case ApplicationStatus.QC_REJECTED:
    case ApplicationStatus.COUNTER_OFFER_MADE:
    case ApplicationStatus.INCOMPLETE:
      return 'warning';
    
    // Active processing states
    case ApplicationStatus.IN_REVIEW:
    case ApplicationStatus.COMMITMENT_SENT:
    case ApplicationStatus.DOCUMENTS_SENT:
    case ApplicationStatus.PARTIALLY_EXECUTED:
    case ApplicationStatus.QC_REVIEW:
      return 'info';
    
    // Initial states
    case ApplicationStatus.DRAFT:
    case ApplicationStatus.SUBMITTED:
    default:
      return 'default';
  }
};

/**
 * Converts application status enum values to human-readable labels
 */
const getStatusLabel = (status: ApplicationStatus): string => {
  // Convert snake_case to Title Case
  return status
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

/**
 * Formats a date string for display in the timeline
 */
const formatDate = (dateString: string): string => {
  return format(new Date(dateString), 'MMM d, yyyy');
};

/**
 * Component that displays a timeline of application status changes,
 * showing the progression of a loan application through various stages
 * of the approval process.
 */
const StatusTimeline: React.FC<StatusTimelineProps> = ({ 
  statusHistory, 
  currentStatus,
  className 
}) => {
  const classes = useStyles();
  
  // Sort status history by date (oldest first for chronological display)
  const sortedHistory = [...statusHistory].sort((a, b) => 
    new Date(a.changed_at).getTime() - new Date(b.changed_at).getTime()
  );

  if (sortedHistory.length === 0) {
    return (
      <CustomCard title="Application Timeline" className={className}>
        <Box p={2} textAlign="center">
          <Typography variant="body1" color="textSecondary">
            No application history available
          </Typography>
        </Box>
      </CustomCard>
    );
  }

  return (
    <CustomCard title="Application Timeline" className={className}>
      <Timeline aria-label="Application status timeline">
        {sortedHistory.map((statusEntry, index) => {
          const isCurrentStatus = statusEntry.new_status === currentStatus;
          return (
            <TimelineItem key={statusEntry.id}>
              <TimelineOppositeContent className={classes.timelineDate}>
                {formatDate(statusEntry.changed_at)}
              </TimelineOppositeContent>
              <TimelineSeparator>
                <TimelineDot 
                  color={getStatusColor(statusEntry.new_status)} 
                  className={classes.timelineDot}
                  variant={isCurrentStatus ? "filled" : "outlined"}
                />
                {index < sortedHistory.length - 1 && <TimelineConnector />}
              </TimelineSeparator>
              <TimelineContent className={classes.timelineContent}>
                <Typography 
                  variant="body1" 
                  fontWeight={isCurrentStatus ? 600 : 400}
                >
                  {getStatusLabel(statusEntry.new_status)}
                  {isCurrentStatus && ' (Current)'}
                </Typography>
                {statusEntry.comments && (
                  <Typography variant="body2" color="textSecondary">
                    {statusEntry.comments}
                  </Typography>
                )}
              </TimelineContent>
            </TimelineItem>
          );
        })}
      </Timeline>
    </CustomCard>
  );
};

export default StatusTimeline;