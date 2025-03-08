import React, { useState, useCallback } from 'react';
import {
  Box,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  IconButton,
  Tooltip,
  Collapse,
  Paper,
  Grid,
  FormHelperText
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers';
import FilterListIcon from '@mui/icons-material/FilterList';
import ClearIcon from '@mui/icons-material/Clear';

import useStyles from './styles';
import { FilterOption } from '../../../types/common.types';
import { useIsMobile } from '../../../responsive/helpers';

/**
 * Interface for filter configuration
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
 * Props interface for the TableFilters component
 */
interface TableFiltersProps {
  filters: FilterOption[];
  filterConfig: FilterConfig[];
  onFilterChange: (filters: FilterOption[]) => void;
  className?: string;
}

/**
 * A component that provides filtering controls for the DataTable component.
 * It renders a set of filter inputs based on the provided filter configuration,
 * allowing users to filter tabular data by various criteria.
 */
const TableFilters: React.FC<TableFiltersProps> = ({
  filters,
  filterConfig,
  onFilterChange,
  className
}) => {
  const [activeFilters, setActiveFilters] = useState<FilterOption[]>(filters || []);
  const [showMobileFilters, setShowMobileFilters] = useState(false);
  const isMobile = useIsMobile();
  const {
    StyledFiltersContainer
  } = useStyles();

  /**
   * Handles changes to filter values and updates the filter state
   */
  const handleFilterChange = useCallback((field: string, value: any) => {
    const newFilters = [...activeFilters];
    const existingFilterIndex = newFilters.findIndex(f => f.field === field);

    if (value === null || value === undefined || value === '') {
      // Remove filter if value is empty
      if (existingFilterIndex !== -1) {
        newFilters.splice(existingFilterIndex, 1);
      }
    } else {
      // Update existing filter or add new one
      if (existingFilterIndex !== -1) {
        newFilters[existingFilterIndex] = { field, value };
      } else {
        newFilters.push({ field, value });
      }
    }

    setActiveFilters(newFilters);
    onFilterChange(newFilters);
  }, [activeFilters, onFilterChange]);

  /**
   * Clears all active filters
   */
  const handleClearFilters = useCallback(() => {
    setActiveFilters([]);
    onFilterChange([]);
  }, [onFilterChange]);

  /**
   * Gets the current value of a specific filter field
   */
  const getFilterValue = useCallback((field: string) => {
    const filter = activeFilters.find(f => f.field === field);
    return filter ? filter.value : null;
  }, [activeFilters]);

  /**
   * Toggles the mobile filter panel visibility
   */
  const toggleMobileFilters = useCallback(() => {
    setShowMobileFilters(prev => !prev);
  }, []);

  /**
   * Renders the appropriate filter control based on filter type
   */
  const renderFilterControl = useCallback((filter: FilterConfig) => {
    const currentValue = getFilterValue(filter.field);
    
    // Skip rendering if filter should only show on mobile but we're on desktop
    if (filter.mobileOnly && !isMobile) return null;
    
    // Skip rendering if filter should only show on desktop but we're on mobile
    if (filter.desktopOnly && isMobile) return null;
    
    // Common props for all form controls
    const commonProps = {
      id: `filter-${filter.field}`,
      'aria-label': `Filter by ${filter.label}`,
      style: { width: filter.width || '100%' }
    };

    switch (filter.type) {
      case 'text':
        return (
          <TextField
            {...commonProps}
            label={filter.label}
            placeholder={filter.placeholder || `Filter by ${filter.label.toLowerCase()}`}
            value={currentValue || ''}
            onChange={(e) => handleFilterChange(filter.field, e.target.value)}
            size={isMobile ? "small" : "medium"}
            variant="outlined"
            fullWidth
          />
        );
        
      case 'select':
        return (
          <FormControl fullWidth variant="outlined" size={isMobile ? "small" : "medium"}>
            <InputLabel id={`filter-${filter.field}-label`}>{filter.label}</InputLabel>
            <Select
              {...commonProps}
              labelId={`filter-${filter.field}-label`}
              value={currentValue || ''}
              onChange={(e) => handleFilterChange(filter.field, e.target.value)}
              label={filter.label}
            >
              <MenuItem value="">
                <em>All</em>
              </MenuItem>
              {filter.options?.map(option => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        );
        
      case 'date':
        return (
          <DatePicker
            label={filter.label}
            value={currentValue}
            onChange={(date) => handleFilterChange(filter.field, date)}
            slotProps={{
              textField: {
                ...commonProps,
                fullWidth: true,
                variant: "outlined",
                size: isMobile ? "small" : "medium",
                placeholder: filter.placeholder || `Select ${filter.label.toLowerCase()}`
              }
            }}
          />
        );
        
      case 'dateRange':
        const startValue = currentValue ? currentValue.start : null;
        const endValue = currentValue ? currentValue.end : null;
        
        return (
          <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: 1, width: '100%' }}>
            <DatePicker
              label={`${filter.label} Start`}
              value={startValue}
              onChange={(date) => handleFilterChange(filter.field, { 
                start: date, 
                end: endValue 
              })}
              slotProps={{
                textField: {
                  fullWidth: true,
                  variant: "outlined",
                  size: isMobile ? "small" : "medium"
                }
              }}
            />
            <DatePicker
              label={`${filter.label} End`}
              value={endValue}
              onChange={(date) => handleFilterChange(filter.field, { 
                start: startValue, 
                end: date 
              })}
              slotProps={{
                textField: {
                  fullWidth: true,
                  variant: "outlined",
                  size: isMobile ? "small" : "medium"
                }
              }}
            />
          </Box>
        );
        
      case 'boolean':
        return (
          <FormControl fullWidth variant="outlined" size={isMobile ? "small" : "medium"}>
            <InputLabel id={`filter-${filter.field}-label`}>{filter.label}</InputLabel>
            <Select
              {...commonProps}
              labelId={`filter-${filter.field}-label`}
              value={currentValue === null ? '' : currentValue}
              onChange={(e) => handleFilterChange(filter.field, e.target.value)}
              label={filter.label}
            >
              <MenuItem value="">
                <em>All</em>
              </MenuItem>
              <MenuItem value="true">Yes</MenuItem>
              <MenuItem value="false">No</MenuItem>
            </Select>
          </FormControl>
        );
        
      default:
        return null;
    }
  }, [getFilterValue, handleFilterChange, isMobile]);

  // If there are no filter configurations, don't render anything
  if (!filterConfig || filterConfig.length === 0) {
    return null;
  }

  // Mobile view with collapsible filter panel
  if (isMobile) {
    return (
      <Box className={className} sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Tooltip title={showMobileFilters ? "Hide filters" : "Show filters"}>
            <Button
              variant="outlined"
              startIcon={<FilterListIcon />}
              onClick={toggleMobileFilters}
              aria-expanded={showMobileFilters}
              aria-controls="filter-panel"
            >
              Filters {activeFilters.length > 0 ? `(${activeFilters.length})` : ''}
            </Button>
          </Tooltip>
          
          {activeFilters.length > 0 && (
            <Tooltip title="Clear all filters">
              <IconButton onClick={handleClearFilters} aria-label="Clear filters">
                <ClearIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>
        
        <Collapse in={showMobileFilters} timeout="auto" unmountOnExit>
          <Paper elevation={1} sx={{ p: 2, mb: 2 }} id="filter-panel">
            <Grid container spacing={2}>
              {filterConfig.map((filter, index) => (
                <Grid item xs={12} key={filter.field}>
                  {renderFilterControl(filter)}
                </Grid>
              ))}
              
              <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={() => onFilterChange(activeFilters)}
                  disabled={activeFilters.length === 0}
                >
                  Apply Filters
                </Button>
                
                {activeFilters.length > 0 && (
                  <Button 
                    variant="outlined" 
                    color="secondary" 
                    onClick={handleClearFilters}
                    sx={{ ml: 1 }}
                  >
                    Clear
                  </Button>
                )}
              </Grid>
            </Grid>
          </Paper>
        </Collapse>
      </Box>
    );
  }

  // Desktop view with horizontal filters
  return (
    <StyledFiltersContainer className={className}>
      {filterConfig.map((filter) => (
        <Box key={filter.field} sx={{ minWidth: filter.width || 200 }}>
          {renderFilterControl(filter)}
        </Box>
      ))}
      
      <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 1 }}>
        <Button 
          variant="contained" 
          color="primary"
          onClick={() => onFilterChange(activeFilters)}
          disabled={activeFilters.length === 0}
          startIcon={<FilterListIcon />}
        >
          Apply Filters
        </Button>
        
        {activeFilters.length > 0 && (
          <Button 
            variant="outlined" 
            color="secondary" 
            onClick={handleClearFilters}
            startIcon={<ClearIcon />}
          >
            Clear Filters
          </Button>
        )}
      </Box>
    </StyledFiltersContainer>
  );
};

export default TableFilters;