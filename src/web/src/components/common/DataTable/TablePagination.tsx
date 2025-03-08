import React from 'react';
import {
  Box,
  Typography,
  Pagination,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import useStyles from './styles';
import { useIsMobile } from '../../../responsive/helpers';

/**
 * Props interface for the TablePagination component
 */
interface TablePaginationProps {
  /** Current page number (1-based) */
  page: number;
  /** Number of items per page */
  pageSize: number;
  /** Total number of items across all pages */
  totalItems: number;
  /** Callback when page changes */
  onPageChange: (page: number) => void;
  /** Callback when page size changes */
  onPageSizeChange: (pageSize: number) => void;
  /** Available page size options */
  pageSizeOptions?: number[];
  /** Additional CSS class for styling */
  className?: string;
}

/**
 * A reusable pagination component for data tables
 */
const TablePagination = (props: TablePaginationProps): JSX.Element => {
  const {
    page,
    pageSize,
    totalItems,
    onPageChange,
    onPageSizeChange,
    pageSizeOptions = [10, 25, 50, 100],
    className,
  } = props;
  
  const { StyledPaginationContainer } = useStyles();
  const isMobile = useIsMobile();

  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  
  // Starting and ending item indices for the current page
  const startItem = totalItems === 0 ? 0 : (page - 1) * pageSize + 1;
  const endItem = Math.min(page * pageSize, totalItems);

  /**
   * Handles page change events from the Pagination component
   */
  const handlePageChange = (event: React.ChangeEvent<unknown>, page: number): void => {
    onPageChange(page);
  };

  /**
   * Handles page size change events from the Select component
   */
  const handlePageSizeChange = (event: React.ChangeEvent<{ value: unknown }>): void => {
    // Type assertion because Material-UI v5 uses SelectChangeEvent
    const target = event.target as { value: unknown };
    const newPageSize = Number(target.value);
    onPageSizeChange(newPageSize);
  };

  return (
    <StyledPaginationContainer className={className}>
      {!isMobile && (
        <Box sx={{ minWidth: 120 }}>
          <FormControl size="small" fullWidth>
            <InputLabel id="rows-per-page-label">Rows per page</InputLabel>
            <Select
              labelId="rows-per-page-label"
              id="rows-per-page"
              value={pageSize.toString()}
              label="Rows per page"
              onChange={handlePageSizeChange as any}
            >
              {pageSizeOptions.map((option) => (
                <MenuItem key={option} value={option.toString()}>
                  {option}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      )}

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap', justifyContent: isMobile ? 'center' : 'flex-start' }}>
        <Typography variant="body2" color="text.secondary">
          Showing {startItem} to {endItem} of {totalItems} entries
        </Typography>
        
        <Pagination
          count={totalPages}
          page={page}
          onChange={handlePageChange}
          color="primary"
          size={isMobile ? "small" : "medium"}
          showFirstButton={!isMobile}
          showLastButton={!isMobile}
          siblingCount={isMobile ? 0 : 1}
          boundaryCount={isMobile ? 1 : 2}
          aria-label="Data table pagination"
        />
      </Box>
    </StyledPaginationContainer>
  );
};

export default TablePagination;