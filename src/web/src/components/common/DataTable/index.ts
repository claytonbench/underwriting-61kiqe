// Import main components
import DataTable from './DataTable';
import TableActions from './TableActions';
import TableFilters from './TableFilters';
import TablePagination from './TablePagination';

// Import interfaces
import { DataTableProps, TableColumn, TableAction } from './DataTable';
import { TableActionsProps } from './TableActions';
import { TableFiltersProps, FilterConfig } from './TableFilters';
import { TablePaginationProps } from './TablePagination';

// Re-export components
export { TableActions, TableFilters, TablePagination };

// Re-export interfaces
export { 
  DataTableProps, 
  TableColumn, 
  TableAction, 
  TableActionsProps, 
  TableFiltersProps, 
  FilterConfig, 
  TablePaginationProps 
};

// Export default component
export default DataTable;