import React from 'react';
import { Box, Paper } from '@mui/material';
import useStyles from './styles';
import PageHeader from './PageHeader';

/**
 * Props interface for the Page component
 */
interface PageProps {
  /** Page title displayed in the header */
  title?: string;
  /** Optional description text displayed below the title */
  description?: string;
  /** Optional action buttons or elements to display in the header */
  actions?: React.ReactNode;
  /** Page content to be rendered within the page container */
  children: React.ReactNode;
  /** Additional CSS class for styling */
  className?: string;
}

/**
 * A reusable page container component that provides consistent layout and structure.
 * Serves as the base layout component for all page content, ensuring visual consistency
 * across the application while supporting responsive design.
 * 
 * @param props - Component props
 * @returns Rendered page component with consistent layout
 */
const Page: React.FC<PageProps> = ({
  title,
  description,
  actions,
  children,
  className,
}) => {
  const classes = useStyles();

  return (
    <Box className={`${classes.pageContainer}${className ? ` ${className}` : ''}`}>
      {title && (
        <PageHeader 
          title={title} 
          description={description} 
          actions={actions} 
        />
      )}
      <Paper className={classes.contentContainer}>
        {children}
      </Paper>
    </Box>
  );
};

export default Page;