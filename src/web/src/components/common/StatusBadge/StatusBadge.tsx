import React from 'react';
import { Chip, ChipProps } from '@mui/material'; // v5.14.0
import useStyles from './styles';
import { ApplicationStatus } from '../../../types/application.types';

/**
 * Interface defining the props for the StatusBadge component
 */
export interface StatusBadgeProps {
  /**
   * The status value to display - can be a string or ApplicationStatus enum value
   */
  status: string | ApplicationStatus;
  
  /**
   * Optional CSS class name for additional styling
   */
  className?: string;
}

/**
 * Determines the appropriate color variant based on the status value
 * 
 * @param status - The status value to analyze
 * @returns The variant name (success, error, warning, info, or default)
 */
const getStatusVariant = (status: string | ApplicationStatus): string => {
  // Convert to lowercase string for consistent comparison
  const statusStr = String(status).toLowerCase();
  
  // Success variant (green)
  if (statusStr === 'approved' || 
      statusStr === 'fully_executed' || 
      statusStr === 'qc_approved' || 
      statusStr === 'ready_to_fund' || 
      statusStr === 'funded' || 
      statusStr === 'commitment_accepted' ||
      statusStr.includes('success') ||
      statusStr.includes('complete')) {
    return 'success';
  }
  
  // Error variant (red)
  if (statusStr === 'denied' || 
      statusStr === 'qc_rejected' || 
      statusStr === 'abandoned' || 
      statusStr === 'documents_expired' || 
      statusStr === 'commitment_declined' ||
      statusStr.includes('error') ||
      statusStr.includes('fail') ||
      statusStr.includes('rejected')) {
    return 'error';
  }
  
  // Warning variant (amber)
  if (statusStr === 'revision_requested' || 
      statusStr === 'counter_offer_made' || 
      statusStr === 'incomplete' || 
      statusStr === 'draft' ||
      statusStr.includes('pending') || 
      statusStr.includes('warning')) {
    return 'warning';
  }
  
  // Info variant (light blue)
  if (statusStr === 'in_review' || 
      statusStr === 'submitted' || 
      statusStr === 'commitment_sent' || 
      statusStr === 'documents_sent' || 
      statusStr === 'partially_executed' || 
      statusStr === 'qc_review' ||
      statusStr.includes('process') ||
      statusStr.includes('progress')) {
    return 'info';
  }
  
  // Default variant (gray) for other statuses
  return 'default';
};

/**
 * Formats the status value into a human-readable label
 * 
 * @param status - The status value to format
 * @returns Formatted status label
 */
const getStatusLabel = (status: string | ApplicationStatus): string => {
  let statusStr = String(status);
  
  // Replace underscores with spaces
  statusStr = statusStr.replace(/_/g, ' ');
  
  // Convert to title case (capitalize first letter of each word)
  return statusStr
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

/**
 * Component that renders a status badge with appropriate styling based on the status value
 */
const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className }) => {
  const variant = getStatusVariant(status);
  const label = getStatusLabel(status);
  const classes = useStyles();
  
  // Determine CSS class based on the variant
  const variantClass = 
    variant === 'success' ? classes.success :
    variant === 'error' ? classes.error :
    variant === 'warning' ? classes.warning :
    variant === 'info' ? classes.info :
    classes.default;
  
  return (
    <Chip
      label={label}
      className={`${classes.root} ${variantClass} ${className || ''}`}
      size="small"
      aria-label={`Status: ${label}`}
    />
  );
};

export default StatusBadge;