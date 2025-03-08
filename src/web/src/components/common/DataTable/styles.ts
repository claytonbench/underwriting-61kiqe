import { styled } from '@mui/material/styles';
import { makeStyles } from '@mui/styles';
import { alpha, Theme } from '@mui/material/styles';
import { Box, TableContainer, Table, TableHead, TableBody, TableRow, TableCell, Paper } from '@mui/material';
import { mediaQueries } from '../../responsive/breakpoints';

/**
 * Custom hook that returns styled components for the DataTable component
 * Provides responsive styling with different layouts for desktop, tablet, and mobile
 * Ensures accessibility compliance with proper contrast and focus states
 */
const useStyles = () => {
  // Table container with responsive padding and border radius
  const StyledTableContainer = styled(TableContainer)(({ theme }) => ({
    padding: theme.spacing(2),
    borderRadius: theme.shape.borderRadius,
    boxShadow: theme.shadows[1],
    overflow: 'hidden',
    [mediaQueries.mobile]: {
      padding: theme.spacing(1)
    }
  }));

  // Main table component with responsive width
  const StyledTable = styled(Table)(({ theme }) => ({
    minWidth: 650,
    tableLayout: 'fixed',
    [mediaQueries.mobile]: {
      minWidth: 'auto'
    }
  }));

  // Table header with distinctive background
  const StyledTableHead = styled(TableHead)(({ theme }) => ({
    backgroundColor: theme.palette.background.default
  }));

  // Table body with alternating row colors for better readability
  const StyledTableBody = styled(TableBody)(({ theme }) => ({
    '& tr:nth-of-type(odd)': {
      backgroundColor: theme.palette.action.hover
    }
  }));

  // Table row with hover effect and selected state
  const StyledTableRow = styled(TableRow)(({ theme }) => ({
    '&:hover': {
      backgroundColor: theme.palette.action.hover
    },
    '&.selected': {
      backgroundColor: alpha(theme.palette.primary.main, 0.1)
    }
  }));

  // Standard table cell with responsive padding
  const StyledTableCell = styled(TableCell)(({ theme }) => ({
    padding: theme.spacing(1.5),
    [mediaQueries.mobile]: {
      padding: theme.spacing(1)
    }
  }));

  // Header cell with bold text for better distinction
  const StyledTableHeaderCell = styled(TableCell)(({ theme }) => ({
    fontWeight: 600,
    backgroundColor: theme.palette.background.default,
    padding: theme.spacing(1.5),
    [mediaQueries.mobile]: {
      padding: theme.spacing(1)
    }
  }));

  // Container for action buttons with proper spacing
  const StyledActionsContainer = styled(Box)(({ theme }) => ({
    display: 'flex',
    justifyContent: 'flex-end',
    gap: theme.spacing(1)
  }));

  // Container for pagination with responsive layout
  const StyledPaginationContainer = styled(Box)(({ theme }) => ({
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: theme.spacing(2, 0),
    [mediaQueries.mobile]: {
      flexDirection: 'column',
      gap: theme.spacing(2),
      alignItems: 'center'
    }
  }));

  // Container for filters with responsive layout
  const StyledFiltersContainer = styled(Box)(({ theme }) => ({
    display: 'flex',
    flexWrap: 'wrap',
    gap: theme.spacing(2),
    marginBottom: theme.spacing(2),
    [mediaQueries.mobile]: {
      flexDirection: 'column',
      gap: theme.spacing(1)
    }
  }));

  // Container for mobile card view layout (alternative to table for small screens)
  const StyledMobileCardContainer = styled(Box)(({ theme }) => ({
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing(2)
  }));

  // Card design for mobile view that replaces table rows
  const StyledMobileCard = styled(Paper)(({ theme }) => ({
    padding: theme.spacing(2),
    borderRadius: theme.shape.borderRadius,
    boxShadow: theme.shadows[1],
    '& .card-header': {
      fontWeight: 600,
      marginBottom: theme.spacing(1)
    },
    '& .card-content': {
      display: 'flex',
      flexDirection: 'column',
      gap: theme.spacing(1)
    },
    '& .card-actions': {
      display: 'flex',
      justifyContent: 'flex-end',
      marginTop: theme.spacing(1)
    }
  }));

  // Loading state container for table
  const StyledLoadingContainer = styled(Box)(({ theme }) => ({
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing(4)
  }));

  // Empty state container for table with no data
  const StyledEmptyStateContainer = styled(Box)(({ theme }) => ({
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing(4),
    color: theme.palette.text.secondary
  }));

  return {
    StyledTableContainer,
    StyledTable,
    StyledTableHead,
    StyledTableBody,
    StyledTableRow,
    StyledTableCell,
    StyledTableHeaderCell,
    StyledActionsContainer,
    StyledPaginationContainer,
    StyledFiltersContainer,
    StyledMobileCardContainer,
    StyledMobileCard,
    StyledLoadingContainer,
    StyledEmptyStateContainer
  };
};

export default useStyles;