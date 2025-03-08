import React from 'react';
import { IconButton, Tooltip, Box } from '@mui/material';
import useStyles from './styles';

/**
 * Interface for table row action configuration
 */
export interface TableAction<T> {
  /** Icon to display for the action */
  icon: React.ReactNode;
  /** Tooltip text for the action */
  label: string;
  /** Click handler for the action */
  onClick: (row: T) => void;
  /** Function to determine if the action should be visible for a row */
  isVisible?: (row: T) => boolean;
  /** Function to determine if the action should be disabled for a row */
  isDisabled?: (row: T) => boolean;
  /** Color of the action button */
  color?: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
}

/**
 * Props interface for the TableActions component
 */
export interface TableActionsProps<T> {
  /** Array of action configurations */
  actions: TableAction<T>[];
  /** Data for the current row */
  row: T;
  /** Additional CSS class for styling */
  className?: string;
}

/**
 * Renders a set of action buttons for a table row
 * 
 * Provides a flexible way to add interactive actions like view, edit, delete, or custom operations
 * to table rows. Each action can have conditional visibility and disabled states based on row data.
 */
const TableActions = <T,>({ actions, row, className }: TableActionsProps<T>): JSX.Element => {
  const { StyledActionsContainer } = useStyles();

  return (
    <StyledActionsContainer className={className}>
      {actions.map((action, index) => {
        // Check if the action should be visible for this row
        const isVisible = action.isVisible ? action.isVisible(row) : true;
        
        if (!isVisible) return null;
        
        // Determine if the action should be disabled
        const isDisabled = action.isDisabled ? action.isDisabled(row) : false;
        
        return (
          <Tooltip key={index} title={action.label} aria-label={action.label}>
            <span>
              <IconButton
                onClick={() => action.onClick(row)}
                color={action.color || 'default'}
                disabled={isDisabled}
                size="small"
                aria-label={action.label}
              >
                {action.icon}
              </IconButton>
            </span>
          </Tooltip>
        );
      })}
    </StyledActionsContainer>
  );
};

export default TableActions;