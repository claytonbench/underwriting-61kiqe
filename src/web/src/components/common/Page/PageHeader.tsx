import React from 'react';
import { Box, Typography } from '@mui/material';
import useStyles from './styles';

/**
 * Props interface for the PageHeader component
 */
interface PageHeaderProps {
  /** Title text displayed in the header */
  title: string;
  /** Optional description text displayed below the title */
  description?: string;
  /** Optional action buttons or elements to display in the header */
  actions?: React.ReactNode;
}

/**
 * A reusable page header component that displays a title, optional description, and action buttons.
 * Provides consistent header styling across the application and supports responsive layouts.
 * 
 * @param props - Component props
 * @returns Rendered page header component
 */
const PageHeader: React.FC<PageHeaderProps> = ({ 
  title, 
  description, 
  actions 
}) => {
  const classes = useStyles();

  return (
    <Box className={classes.pageHeader}>
      <Box className={classes.headerContent}>
        <Typography variant="h4" className={classes.headerTitle}>
          {title}
        </Typography>
        {description && (
          <Typography variant="body1" className={classes.headerDescription}>
            {description}
          </Typography>
        )}
      </Box>
      {actions && (
        <Box className={classes.headerActions}>
          {actions}
        </Box>
      )}
    </Box>
  );
};

export default PageHeader;