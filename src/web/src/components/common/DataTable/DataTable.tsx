import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Box,
  Paper,
  Typography,
  CircularProgress
} from '@mui/material';

import useStyles from './styles';
import TableActions from './TableActions';
import TableFilters from './TableFilters';
import TablePagination from './TablePagination';
import { FilterOption, SortDirection } from '../../../types/common.types';
import { useIsMobile } from '../../../responsive/helpers';

/**
 * Interface for table column configuration
 */
interface TableColumn<T> {
  /** Field name in the data object */
  field: string;
  /** Display name for the column header */
  headerName: string;
  /** Column width */
  width?: number | string;
  /** Whether the column is sortable */
  sortable?: boolean;
  /** Text alignment for the column */
  align?: 'left' | 'center' | 'right';
  /** Custom render function for the cell */
  render?: (value: any, row: T, index: number) => React.ReactNode;
  /** Whether to show this column only on mobile devices */
  mobileOnly?: boolean;
  /** Whether to show this column only on desktop devices */
  desktopOnly?: boolean;
}

/**
 * Interface for table row action configuration
 */
interface TableAction<T> {
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
 * Props interface for the DataTable component
 */
interface DataTableProps<T> {
  /** Array of data items to display in the table */
  data: T[];
  /** Configuration for table columns */
  columns: TableColumn<T>[];
  /** Whether the table is in a loading state */
  loading?: boolean;
  /** Message to display when there is no data */
  emptyStateMessage?: string;
  /** Row actions configuration */
  actions?: TableAction<T>[];
  
  /** Whether to enable pagination */
  pagination?: boolean;
  /** Current page number (1-based) */
  page?: number;
  /** Number of items per page */
  pageSize?: number;
  /** Total number of items across all pages */
  totalItems?: number;
  /** Callback when page changes */
  onPageChange?: (page: number) => void;
  /** Callback when page size changes */
  onPageSizeChange?: (pageSize: number) => void;
  /** Available page size options */
  pageSizeOptions?: number[];
  
  /** Whether to enable column sorting */
  sorting?: boolean;
  /** Current sort field */
  sortField?: string;
  /** Current sort direction */
  sortDirection?: SortDirection;
  /** Callback when sort changes */
  onSortChange?: (field: string, direction: SortDirection) => void;
  
  /** Whether to enable filtering */
  filtering?: boolean;
  /** Current filter options */
  filterOptions?: FilterOption[];
  /** Configuration for available filters */
  filterConfig?: FilterConfig[];
  /** Callback when filters change */
  onFilterChange?: (filters: FilterOption[]) => void;
  
  /** Whether rows can be selected */
  selectable?: boolean;
  /** Currently selected rows */
  selectedRows?: T[];
  /** Callback when selection changes */
  onSelectionChange?: (selectedRows: T[]) => void;
  
  /** Fields to display in mobile view */
  mobileFields?: string[];
  
  /** Additional CSS class for styling */
  className?: string;
}

/**
 * Filter configuration for table filters
 */
interface FilterConfig {
  field: string;
  label: string;
  type: 'text' | 'select' | 'date' | 'dateRange' | 'boolean';
  options?: { value: string | number; label: string }[];
  width?: string | number;
  placeholder?: string;
  mobileOnly?: boolean;
  desktopOnly?: boolean;
}

/**
 * A reusable data table component with sorting, filtering, pagination, and row actions
 */
const DataTable = <T,>(props: DataTableProps<T>): JSX.Element => {
  const {
    data,
    columns,
    loading = false,
    emptyStateMessage = 'No data available',
    actions,
    
    pagination = true,
    page: externalPage = 1,
    pageSize: externalPageSize = 10,
    totalItems,
    onPageChange,
    onPageSizeChange,
    pageSizeOptions = [10, 25, 50, 100],
    
    sorting = true,
    sortField: externalSortField,
    sortDirection: externalSortDirection = SortDirection.ASC,
    onSortChange,
    
    filtering = false,
    filterOptions = [],
    filterConfig = [],
    onFilterChange,
    
    selectable = false,
    selectedRows = [],
    onSelectionChange,
    
    mobileFields,
    
    className
  } = props;

  // Internal state for controlled/uncontrolled behavior
  const [page, setPage] = useState(externalPage);
  const [pageSize, setPageSize] = useState(externalPageSize);
  const [sortField, setSortField] = useState<string | undefined>(externalSortField);
  const [sortDirection, setSortDirection] = useState(externalSortDirection);
  const [filters, setFilters] = useState<FilterOption[]>(filterOptions);

  // Update internal state when props change
  useEffect(() => {
    setPage(externalPage);
  }, [externalPage]);

  useEffect(() => {
    setPageSize(externalPageSize);
  }, [externalPageSize]);

  useEffect(() => {
    setSortField(externalSortField);
  }, [externalSortField]);

  useEffect(() => {
    setSortDirection(externalSortDirection);
  }, [externalSortDirection]);

  useEffect(() => {
    setFilters(filterOptions);
  }, [filterOptions]);

  const isMobile = useIsMobile();
  const styles = useStyles();

  /**
   * Handles column header click to change sort direction
   */
  const handleSort = (field: string) => {
    if (!sorting) return;
    
    let newDirection = SortDirection.ASC;
    
    if (sortField === field) {
      // Toggle direction if already sorting by this field
      newDirection = sortDirection === SortDirection.ASC ? SortDirection.DESC : SortDirection.ASC;
    }
    
    setSortField(field);
    setSortDirection(newDirection);
    
    if (onSortChange) {
      onSortChange(field, newDirection);
    }
  };

  /**
   * Handles filter changes from the TableFilters component
   */
  const handleFilterChange = (filters: FilterOption[]) => {
    setFilters(filters);
    setPage(1); // Reset to first page when filters change
    
    if (onFilterChange) {
      onFilterChange(filters);
    }
  };

  /**
   * Handles page change events from the TablePagination component
   */
  const handlePageChange = (page: number) => {
    setPage(page);
    
    if (onPageChange) {
      onPageChange(page);
    }
  };

  /**
   * Handles page size change events from the TablePagination component
   */
  const handlePageSizeChange = (pageSize: number) => {
    setPageSize(pageSize);
    setPage(1); // Reset to first page when page size changes
    
    if (onPageSizeChange) {
      onPageSizeChange(pageSize);
    }
  };

  /**
   * Renders the table header with sortable column headers
   */
  const renderTableHeader = () => {
    const {
      StyledTableHead,
      StyledTableRow,
      StyledTableHeaderCell
    } = styles;

    return (
      <StyledTableHead>
        <StyledTableRow>
          {columns.map((column, index) => {
            // Skip columns that should only show on mobile if we're on desktop
            if (column.mobileOnly && !isMobile) return null;
            
            // Skip columns that should only show on desktop if we're on mobile
            if (column.desktopOnly && isMobile) return null;
            
            return (
              <StyledTableHeaderCell
                key={column.field}
                align={column.align || 'left'}
                style={{ width: column.width }}
                sortDirection={sortField === column.field ? sortDirection.toLowerCase() as 'asc' | 'desc' : false}
              >
                {sorting && column.sortable !== false ? (
                  <TableSortLabel
                    active={sortField === column.field}
                    direction={sortField === column.field ? sortDirection.toLowerCase() as 'asc' | 'desc' : 'asc'}
                    onClick={() => handleSort(column.field)}
                    aria-label={`Sort by ${column.headerName}`}
                  >
                    {column.headerName}
                  </TableSortLabel>
                ) : (
                  column.headerName
                )}
              </StyledTableHeaderCell>
            );
          })}
          
          {actions && actions.length > 0 && (
            <StyledTableHeaderCell align="right" aria-label="Actions">
              Actions
            </StyledTableHeaderCell>
          )}
        </StyledTableRow>
      </StyledTableHead>
    );
  };

  /**
   * Renders the table body with data rows
   */
  const renderTableBody = () => {
    const {
      StyledTableBody,
      StyledTableRow,
      StyledTableCell,
      StyledLoadingContainer,
      StyledEmptyStateContainer
    } = styles;

    // Show loading state
    if (loading) {
      return (
        <StyledTableBody>
          <TableRow>
            <TableCell colSpan={columns.length + (actions && actions.length > 0 ? 1 : 0)}>
              <StyledLoadingContainer>
                <CircularProgress size={40} aria-label="Loading data" />
              </StyledLoadingContainer>
            </TableCell>
          </TableRow>
        </StyledTableBody>
      );
    }

    // Show empty state
    if (!data.length) {
      return (
        <StyledTableBody>
          <TableRow>
            <TableCell colSpan={columns.length + (actions && actions.length > 0 ? 1 : 0)}>
              <StyledEmptyStateContainer>
                <Typography variant="body2">{emptyStateMessage}</Typography>
              </StyledEmptyStateContainer>
            </TableCell>
          </TableRow>
        </StyledTableBody>
      );
    }

    // Render data rows
    return (
      <StyledTableBody>
        {data.map((row, rowIndex) => (
          <StyledTableRow
            key={rowIndex}
            hover
            className={selectedRows?.includes(row) ? 'selected' : ''}
            onClick={selectable && onSelectionChange ? () => {
              const isSelected = selectedRows.includes(row);
              const newSelectedRows = isSelected
                ? selectedRows.filter(selectedRow => selectedRow !== row)
                : [...selectedRows, row];
              onSelectionChange(newSelectedRows);
            } : undefined}
            role={selectable ? 'checkbox' : undefined}
            aria-selected={selectable ? selectedRows.includes(row) : undefined}
            tabIndex={selectable ? 0 : undefined}
          >
            {columns.map((column, columnIndex) => {
              // Skip columns that should only show on mobile if we're on desktop
              if (column.mobileOnly && !isMobile) return null;
              
              // Skip columns that should only show on desktop if we're on mobile
              if (column.desktopOnly && isMobile) return null;
              
              const value = row[column.field as keyof T];
              
              return (
                <StyledTableCell
                  key={columnIndex}
                  align={column.align || 'left'}
                >
                  {column.render ? column.render(value, row, rowIndex) : value as React.ReactNode}
                </StyledTableCell>
              );
            })}
            
            {actions && actions.length > 0 && (
              <StyledTableCell align="right">
                <TableActions actions={actions} row={row} />
              </StyledTableCell>
            )}
          </StyledTableRow>
        ))}
      </StyledTableBody>
    );
  };

  /**
   * Renders a mobile-optimized view of the table data
   */
  const renderMobileView = () => {
    const {
      StyledMobileCardContainer,
      StyledMobileCard,
      StyledLoadingContainer,
      StyledEmptyStateContainer,
      StyledActionsContainer
    } = styles;

    // Show loading state
    if (loading) {
      return (
        <StyledLoadingContainer>
          <CircularProgress size={40} aria-label="Loading data" />
        </StyledLoadingContainer>
      );
    }

    // Show empty state
    if (!data.length) {
      return (
        <StyledEmptyStateContainer>
          <Typography variant="body2">{emptyStateMessage}</Typography>
        </StyledEmptyStateContainer>
      );
    }

    const displayFields = mobileFields || columns
      .filter(column => !column.desktopOnly)
      .map(column => column.field)
      .slice(0, 3); // Limit to first 3 fields by default

    return (
      <StyledMobileCardContainer role="table" aria-label="Data table">
        {data.map((row, rowIndex) => (
          <StyledMobileCard key={rowIndex} role="row">
            <Box className="card-header" role="rowheader">
              {/* Primary identifier for the row */}
              <Typography variant="subtitle1">
                {displayFields.length > 0 && 
                 row[displayFields[0] as keyof T] as React.ReactNode}
              </Typography>
            </Box>
            <Box className="card-content">
              {displayFields.slice(1).map(field => {
                const column = columns.find(col => col.field === field);
                if (!column) return null;
                
                const value = row[field as keyof T];
                
                return (
                  <Box key={field} display="flex" justifyContent="space-between" alignItems="center" role="cell">
                    <Typography variant="subtitle2" color="text.secondary">
                      {column.headerName}:
                    </Typography>
                    <Typography variant="body2">
                      {column.render ? column.render(value, row, rowIndex) : value as React.ReactNode}
                    </Typography>
                  </Box>
                );
              })}
            </Box>
            
            {actions && actions.length > 0 && (
              <Box className="card-actions">
                <TableActions actions={actions} row={row} />
              </Box>
            )}
          </StyledMobileCard>
        ))}
      </StyledMobileCardContainer>
    );
  };

  const {
    StyledTableContainer,
    StyledTable
  } = styles;

  return (
    <Box className={className}>
      {/* Filters */}
      {filtering && filterConfig.length > 0 && (
        <TableFilters
          filters={filters}
          filterConfig={filterConfig}
          onFilterChange={handleFilterChange}
        />
      )}
      
      {/* Table or Mobile View */}
      {isMobile ? (
        renderMobileView()
      ) : (
        <StyledTableContainer component={Paper}>
          <StyledTable aria-label="data table">
            {renderTableHeader()}
            {renderTableBody()}
          </StyledTable>
        </StyledTableContainer>
      )}
      
      {/* Pagination */}
      {pagination && totalItems !== undefined && (
        <TablePagination
          page={page}
          pageSize={pageSize}
          totalItems={totalItems}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
          pageSizeOptions={pageSizeOptions}
        />
      )}
    </Box>
  );
};

export default DataTable;