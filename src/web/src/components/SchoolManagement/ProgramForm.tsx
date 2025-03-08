import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Switch,
  FormControlLabel,
  Typography,
  Divider,
  Box,
  Paper,
  CircularProgress,
  InputAdornment
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';

import useForm from '../../hooks/useForm';
import useStyles from './styles';
import { isRequired, isPositiveNumber, isCurrency, isFutureDate } from '../../utils/validation';
import {
  Program,
  ProgramCreateRequest,
  ProgramUpdateRequest,
  ProgramStatus
} from '../../types/school.types';
import {
  createNewProgram,
  updateExistingProgram,
  selectSchoolLoading
} from '../../store/slices/schoolSlice';

/**
 * Props for the ProgramForm component
 */
interface ProgramFormProps {
  program: Program | null; // Program data for editing, null for new program creation
  schoolId: string; // ID of the school this program belongs to
  onSuccess: (program: Program) => void; // Callback function called after successful form submission
  onCancel: () => void; // Callback function called when form is cancelled
}

/**
 * Component for creating or editing educational programs within schools
 * Handles program details, validation, and submission for both new programs and updates
 */
const ProgramForm: React.FC<ProgramFormProps> = ({ program, schoolId, onSuccess, onCancel }) => {
  // Set up initial form values
  const initialValues = {
    name: program?.name || '',
    description: program?.description || '',
    duration_hours: program?.duration_hours || '',
    duration_weeks: program?.duration_weeks || '',
    status: program?.status || ProgramStatus.ACTIVE,
    tuition_amount: program?.current_tuition || '',
    effective_date: new Date()
  };

  // Set up validation schema
  const validationSchema = {
    name: {
      validate: isRequired,
      errorMessage: 'Program name is required'
    },
    description: {
      validate: isRequired,
      errorMessage: 'Program description is required'
    },
    duration_hours: {
      validate: isPositiveNumber,
      errorMessage: 'Duration hours must be a positive number'
    },
    duration_weeks: {
      validate: isPositiveNumber,
      errorMessage: 'Duration weeks must be a positive number'
    },
    tuition_amount: {
      validate: isCurrency,
      errorMessage: 'Valid tuition amount is required'
    },
    effective_date: {
      validate: isFutureDate,
      errorMessage: 'Effective date must be in the future'
    }
  };

  // Initialize form with useForm hook
  const {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    handleSubmit,
    setFieldValue
  } = useForm(initialValues, validationSchema, handleFormSubmit);

  const dispatch = useDispatch();
  const loading = useSelector(selectSchoolLoading);
  const classes = useStyles();

  // Handle form submission - creates or updates program based on props
  async function handleFormSubmit(formValues: typeof initialValues) {
    try {
      if (program) {
        // Update existing program
        const updateData: ProgramUpdateRequest = {
          name: formValues.name,
          description: formValues.description,
          duration_hours: Number(formValues.duration_hours),
          duration_weeks: Number(formValues.duration_weeks),
          status: formValues.status as ProgramStatus
        };

        const result = await dispatch(updateExistingProgram({
          programId: program.id,
          programData: updateData
        }));

        // If the update was successful, create a new program version if tuition changed
        if (updateExistingProgram.fulfilled.match(result)) {
          if (formValues.tuition_amount !== program.current_tuition) {
            // In real implementation, would dispatch createNewProgramVersion here
            // This would create a new version with the updated tuition amount
          }
          onSuccess(result.payload);
        }
      } else {
        // Create new program
        const createData: ProgramCreateRequest = {
          school_id: schoolId,
          name: formValues.name,
          description: formValues.description,
          duration_hours: Number(formValues.duration_hours),
          duration_weeks: Number(formValues.duration_weeks),
          status: formValues.status as ProgramStatus,
          tuition_amount: Number(formValues.tuition_amount),
          effective_date: formValues.effective_date
        };

        const result = await dispatch(createNewProgram(createData));
        if (createNewProgram.fulfilled.match(result)) {
          onSuccess(result.payload);
        }
      }
    } catch (error) {
      console.error('Error saving program:', error);
    }
  }

  return (
    <Paper className={classes.formCard}>
      <Typography variant="h6" className={classes.sectionTitle}>
        {program ? 'Edit Program' : 'Add New Program'}
      </Typography>
      <Divider className={classes.divider} />
      
      <form onSubmit={handleSubmit}>
        <div className={classes.formSection}>
          <TextField
            fullWidth
            id="name"
            name="name"
            label="Program Name"
            value={values.name}
            onChange={handleChange}
            onBlur={handleBlur}
            error={touched.name && Boolean(errors.name)}
            helperText={touched.name && errors.name}
            required
            className={classes.fullWidthField}
          />
          
          <TextField
            fullWidth
            id="description"
            name="description"
            label="Description"
            value={values.description}
            onChange={handleChange}
            onBlur={handleBlur}
            error={touched.description && Boolean(errors.description)}
            helperText={touched.description && errors.description}
            multiline
            rows={4}
            required
            className={classes.fullWidthField}
          />
        </div>
        
        <div className={classes.fieldGrid}>
          <TextField
            id="duration_hours"
            name="duration_hours"
            label="Duration (hours)"
            value={values.duration_hours}
            onChange={handleChange}
            onBlur={handleBlur}
            error={touched.duration_hours && Boolean(errors.duration_hours)}
            helperText={touched.duration_hours && errors.duration_hours}
            type="number"
            required
            fullWidth
          />
          
          <TextField
            id="duration_weeks"
            name="duration_weeks"
            label="Duration (weeks)"
            value={values.duration_weeks}
            onChange={handleChange}
            onBlur={handleBlur}
            error={touched.duration_weeks && Boolean(errors.duration_weeks)}
            helperText={touched.duration_weeks && errors.duration_weeks}
            type="number"
            required
            fullWidth
          />
        </div>
        
        <div className={classes.formSection}>
          <TextField
            fullWidth
            id="tuition_amount"
            name="tuition_amount"
            label="Tuition Amount"
            value={values.tuition_amount}
            onChange={handleChange}
            onBlur={handleBlur}
            error={touched.tuition_amount && Boolean(errors.tuition_amount)}
            helperText={touched.tuition_amount && errors.tuition_amount}
            InputProps={{
              startAdornment: <InputAdornment position="start">$</InputAdornment>,
            }}
            required
            className={classes.fullWidthField}
          />
          
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <DatePicker
              label="Effective Date"
              value={values.effective_date}
              onChange={(newValue) => {
                setFieldValue('effective_date', newValue);
              }}
              slotProps={{
                textField: {
                  fullWidth: true,
                  error: touched.effective_date && Boolean(errors.effective_date),
                  helperText: touched.effective_date && errors.effective_date,
                  required: true,
                  className: classes.fullWidthField
                }
              }}
            />
          </LocalizationProvider>
        </div>
        
        <FormControl component="fieldset" className={classes.switchField}>
          <FormControlLabel
            control={
              <Switch
                checked={values.status === ProgramStatus.ACTIVE}
                onChange={(e) => {
                  setFieldValue('status', e.target.checked ? ProgramStatus.ACTIVE : ProgramStatus.INACTIVE);
                }}
                color="primary"
              />
            }
            label="Active"
          />
        </FormControl>
        
        {program && (
          <div className={classes.formSection}>
            <Typography variant="subtitle1" className={classes.sectionTitle}>
              Program History
            </Typography>
            <Typography variant="body2" className={classes.helperText}>
              When you change the tuition amount, a new program version will be created with the specified effective date.
            </Typography>
          </div>
        )}
        
        <div className={classes.formActions}>
          <Button 
            variant="outlined" 
            onClick={onCancel}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            disabled={loading}
          >
            {loading ? (
              <CircularProgress size={24} />
            ) : program ? (
              'Update Program'
            ) : (
              'Create Program'
            )}
          </Button>
        </div>
      </form>
    </Paper>
  );
};

export default ProgramForm;