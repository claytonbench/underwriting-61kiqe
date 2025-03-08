import React from 'react';
import { Typography, Box, List, ListItem, Button } from '@mui/material';
import { format } from 'date-fns';
import useStyles from './styles';
import CustomCard from '../common/Card/Card';
import { ApplicationRequiredAction } from '../../types/application.types';

/**
 * Interface defining the props for the RequiredActions component
 */
export interface RequiredActionsProps {
  /**
   * Array of required actions to be displayed
   */
  actions: ApplicationRequiredAction[];
  /**
   * Callback function triggered when an action button is clicked
   */
  onAction: (actionType: string, data?: any) => void;
  /**
   * Optional CSS class name to apply to the component
   */
  className?: string;
}

/**
 * Formats a date string for display
 * @param dateString - The date string to format (ISO8601 format)
 * @returns Formatted date string (MM/DD/YYYY) or empty string if date is invalid
 */
const formatDate = (dateString: string | null | undefined): string => {
  if (!dateString) return '';
  try {
    return format(new Date(dateString), 'MM/dd/yyyy');
  } catch (error) {
    console.error('Error formatting date:', error);
    return '';
  }
};

/**
 * Determines the button text based on action type
 * @param actionType - The type of action
 * @returns Appropriate button text for the action
 */
const getActionButtonText = (actionType: string): string => {
  switch (actionType) {
    case 'sign_document':
      return 'Sign Now';
    case 'upload_document':
      return 'Upload';
    case 'view_document':
      return 'View';
    default:
      return 'Complete';
  }
};

/**
 * Component that displays required actions for a loan application.
 * Shows a list of pending tasks that the user needs to complete, such as signing documents
 * or uploading required information, with action buttons to initiate those tasks.
 */
const RequiredActions: React.FC<RequiredActionsProps> = ({ 
  actions = [], 
  onAction, 
  className 
}) => {
  const classes = useStyles();

  return (
    <CustomCard 
      title="Required Actions" 
      className={className}
    >
      {!actions || actions.length === 0 ? (
        <Typography variant="body1" className={classes.noActions}>
          No actions required at this time.
        </Typography>
      ) : (
        <List className={classes.actionsList} aria-label="required action items">
          {actions.map((action) => (
            <ListItem key={action.id} className={classes.actionItem}>
              <Box display="flex" flexDirection="column" flexGrow={1}>
                <Typography variant="body1" className={classes.actionDescription}>
                  {action.description}
                </Typography>
                {action.due_date && (
                  <Typography variant="body2" className={classes.actionDueDate}>
                    Due by {formatDate(action.due_date)}
                  </Typography>
                )}
              </Box>
              <Button 
                variant="contained" 
                color="primary" 
                className={classes.actionButton}
                onClick={() => onAction(action.action_type, {
                  id: action.id,
                  entityId: action.related_entity_id,
                  entityType: action.related_entity_type
                })}
                aria-label={`${getActionButtonText(action.action_type)} ${action.description}`}
              >
                {getActionButtonText(action.action_type)}
              </Button>
            </ListItem>
          ))}
        </List>
      )}
    </CustomCard>
  );
};

export default RequiredActions;