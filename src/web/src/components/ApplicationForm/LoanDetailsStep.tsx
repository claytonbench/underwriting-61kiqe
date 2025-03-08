import React, { useState, useEffect } from 'react';
import { 
  Grid, 
  Typography, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  FormHelperText,
  Box,
  Divider,
  CircularProgress,
  SelectChangeEvent
} from '@mui/material';

import useStyles from './styles';
import CurrencyField from '../FormElements/CurrencyField';
import DateField from '../FormElements/DateField';
import { getSchools, getSchoolPrograms, getProgramById } from '../../api/schools';
import { LoanDetailsFormData, FormState } from '../../hooks/useForm';

// Interface for the component props
interface LoanDetailsStepProps {
  formState: FormState;
}

// Interface for school data
interface School {
  id: string;
  name: string;
}

// Interface for program data
interface Program {
  id: string;
  name: string;
  current_tuition: number;
  duration_weeks: number;
}

/**
 * Calculate the requested loan amount based on tuition, deposit, and other funding
 * @param tuition The tuition amount
 * @param deposit The deposit amount
 * @param otherFunding Other funding sources amount
 * @returns The calculated requested amount (tuition - deposit - otherFunding) or 0 if negative
 */
const calculateRequestedAmount = (tuition: number, deposit: number, otherFunding: number): number => {
  // Convert to numbers with default of 0 if null/undefined
  const tuitionAmount = tuition || 0;
  const depositAmount = deposit || 0;
  const otherFundingAmount = otherFunding || 0;
  
  // Calculate the max loan amount
  const calculatedAmount = tuitionAmount - depositAmount - otherFundingAmount;
  
  // Return 0 if the calculation is negative
  return calculatedAmount > 0 ? calculatedAmount : 0;
};

/**
 * A form component representing the loan details step in the multi-step loan application process.
 * It allows users to select a school and program, enter program dates, and specify financial
 * details including tuition amount, deposit amount, other funding, and requested loan amount.
 */
const LoanDetailsStep: React.FC<LoanDetailsStepProps> = ({ formState }) => {
  const styles = useStyles();
  
  // State for schools and programs
  const [schools, setSchools] = useState<School[]>([]);
  const [programs, setPrograms] = useState<Program[]>([]);
  const [selectedProgram, setSelectedProgram] = useState<Program | null>(null);
  
  // Loading states
  const [loadingSchools, setLoadingSchools] = useState(false);
  const [loadingPrograms, setLoadingPrograms] = useState(false);
  const [loadingProgramDetails, setLoadingProgramDetails] = useState(false);
  
  // Fetch schools on component mount
  useEffect(() => {
    const fetchSchools = async () => {
      setLoadingSchools(true);
      try {
        const response = await getSchools({ page: 1, page_size: 100 });
        if (response.success && response.data) {
          setSchools(response.data.results);
        } else {
          setSchools([]);
          console.error('Failed to fetch schools:', response.message);
          formState.setFieldError('school_id', 'Unable to load schools. Please try again later.');
        }
      } catch (error) {
        setSchools([]);
        console.error('Error fetching schools:', error);
        formState.setFieldError('school_id', 'Unable to load schools. Please try again later.');
      } finally {
        setLoadingSchools(false);
      }
    };
    
    fetchSchools();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
  
  // Fetch programs when school selection changes
  useEffect(() => {
    if (formState.values.school_id) {
      const fetchPrograms = async () => {
        setLoadingPrograms(true);
        try {
          const response = await getSchoolPrograms(formState.values.school_id, { page: 1, page_size: 100 });
          if (response.success && response.data) {
            setPrograms(response.data.results);
          } else {
            setPrograms([]);
            console.error('Failed to fetch programs:', response.message);
            formState.setFieldError('program_id', 'Unable to load programs. Please try again later.');
          }
        } catch (error) {
          setPrograms([]);
          console.error('Error fetching programs:', error);
          formState.setFieldError('program_id', 'Unable to load programs. Please try again later.');
        } finally {
          setLoadingPrograms(false);
        }
      };
      
      fetchPrograms();
    } else {
      setPrograms([]);
    }
  }, [formState.values.school_id]); // eslint-disable-line react-hooks/exhaustive-deps
  
  // Fetch program details when program selection changes
  useEffect(() => {
    if (formState.values.program_id) {
      const fetchProgramDetails = async () => {
        setLoadingProgramDetails(true);
        try {
          const response = await getProgramById(formState.values.program_id);
          if (response.success && response.data) {
            setSelectedProgram(response.data);
            
            // Update tuition amount based on program data
            formState.setFieldValue('tuition_amount', response.data.current_tuition);
            
            // Calculate completion date based on start date and program duration
            if (formState.values.start_date) {
              const startDate = new Date(formState.values.start_date);
              const durationWeeks = response.data.duration_weeks;
              const completionDate = new Date(startDate);
              completionDate.setDate(startDate.getDate() + (durationWeeks * 7));
              
              formState.setFieldValue('completion_date', completionDate.toISOString().split('T')[0]);
            }
          } else {
            setSelectedProgram(null);
            console.error('Failed to fetch program details:', response.message);
            formState.setFieldError('program_id', 'Unable to load program details. Please try again later.');
          }
        } catch (error) {
          setSelectedProgram(null);
          console.error('Error fetching program details:', error);
          formState.setFieldError('program_id', 'Unable to load program details. Please try again later.');
        } finally {
          setLoadingProgramDetails(false);
        }
      };
      
      fetchProgramDetails();
    } else {
      setSelectedProgram(null);
    }
  }, [formState.values.program_id]); // eslint-disable-line react-hooks/exhaustive-deps
  
  // Recalculate requested amount when financial values change
  useEffect(() => {
    const { tuition_amount, deposit_amount, other_funding } = formState.values;
    
    const requestedAmount = calculateRequestedAmount(
      tuition_amount,
      deposit_amount,
      other_funding
    );
    
    formState.setFieldValue('requested_amount', requestedAmount);
  }, [
    formState.values.tuition_amount,
    formState.values.deposit_amount,
    formState.values.other_funding,
  ]); // eslint-disable-line react-hooks/exhaustive-deps
  
  // Handle school selection change
  const handleSchoolChange = (event: SelectChangeEvent) => {
    const schoolId = event.target.value;
    formState.setFieldValue('school_id', schoolId);
    
    // Reset program selection and related fields when school changes
    formState.setFieldValue('program_id', '');
    formState.setFieldValue('tuition_amount', null);
    formState.setFieldValue('completion_date', '');
    setSelectedProgram(null);
  };
  
  // Handle program selection change
  const handleProgramChange = (event: SelectChangeEvent) => {
    const programId = event.target.value;
    formState.setFieldValue('program_id', programId);
  };
  
  // Handle start date change
  const handleStartDateChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const startDate = event.target.value;
    formState.setFieldValue('start_date', startDate);
    
    // Calculate completion date if program is selected
    if (selectedProgram && startDate) {
      const startDateObj = new Date(startDate);
      const durationWeeks = selectedProgram.duration_weeks;
      const completionDate = new Date(startDateObj);
      completionDate.setDate(startDateObj.getDate() + (durationWeeks * 7));
      
      formState.setFieldValue('completion_date', completionDate.toISOString().split('T')[0]);
    }
  };
  
  // Handle changes to financial fields
  const handleFinancialFieldChange = (field: string, value: number | null) => {
    formState.setFieldValue(field, value);
  };
  
  // Get current date for min date on start date field
  const today = new Date().toISOString().split('T')[0];
  
  return (
    <Grid container spacing={3}>
      {/* School and Program Selection */}
      <Grid item xs={12} md={6}>
        <FormControl fullWidth error={!!formState.errors.school_id}>
          <InputLabel id="school-select-label">School</InputLabel>
          <Select
            labelId="school-select-label"
            id="school-select"
            value={formState.values.school_id || ''}
            onChange={handleSchoolChange}
            label="School"
            disabled={loadingSchools}
            onBlur={(e) => formState.handleBlur(e as any)}
            name="school_id"
          >
            <MenuItem value="" disabled>
              Select a school
            </MenuItem>
            {loadingSchools ? (
              <MenuItem value="" disabled>
                <CircularProgress size={20} /> Loading...
              </MenuItem>
            ) : (
              schools.map((school) => (
                <MenuItem key={school.id} value={school.id}>
                  {school.name}
                </MenuItem>
              ))
            )}
          </Select>
          {formState.errors.school_id && (
            <FormHelperText>{formState.errors.school_id}</FormHelperText>
          )}
        </FormControl>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControl fullWidth error={!!formState.errors.program_id}>
          <InputLabel id="program-select-label">Program</InputLabel>
          <Select
            labelId="program-select-label"
            id="program-select"
            value={formState.values.program_id || ''}
            onChange={handleProgramChange}
            label="Program"
            disabled={!formState.values.school_id || loadingPrograms}
            onBlur={(e) => formState.handleBlur(e as any)}
            name="program_id"
          >
            <MenuItem value="" disabled>
              {!formState.values.school_id ? 'Select a school first' : 'Select a program'}
            </MenuItem>
            {loadingPrograms ? (
              <MenuItem value="" disabled>
                <CircularProgress size={20} /> Loading...
              </MenuItem>
            ) : (
              programs.map((program) => (
                <MenuItem key={program.id} value={program.id}>
                  {program.name}
                </MenuItem>
              ))
            )}
          </Select>
          {formState.errors.program_id && (
            <FormHelperText>{formState.errors.program_id}</FormHelperText>
          )}
        </FormControl>
      </Grid>
      
      {/* Program Dates */}
      <Grid item xs={12}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <DateField
              name="start_date"
              label="Start Date"
              value={formState.values.start_date || ''}
              onChange={handleStartDateChange}
              onBlur={(e) => formState.handleBlur(e as any)}
              error={!!formState.errors.start_date}
              helperText={formState.errors.start_date || 'When will you start the program?'}
              required
              fullWidth
              minDate={today}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <DateField
              name="completion_date"
              label="Completion Date"
              value={formState.values.completion_date || ''}
              onChange={(e) => formState.handleChange(e as any)}
              onBlur={(e) => formState.handleBlur(e as any)}
              error={!!formState.errors.completion_date}
              helperText={
                formState.errors.completion_date || 
                (selectedProgram ? 'Auto-calculated based on program duration' : 'Select a program and start date first')
              }
              required
              fullWidth
              minDate={formState.values.start_date || today}
              disabled={!formState.values.start_date || !selectedProgram}
            />
          </Grid>
        </Grid>
      </Grid>
      
      {/* Financial Information */}
      <Grid item xs={12}>
        <Typography variant="h6" className={styles.sectionTitle}>
          Financial Information
        </Typography>
        <Divider />
        
        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12} md={6}>
            <CurrencyField
              name="tuition_amount"
              label="Tuition Amount"
              value={formState.values.tuition_amount}
              onChange={(value) => handleFinancialFieldChange('tuition_amount', value)}
              error={!!formState.errors.tuition_amount}
              helperText={
                formState.errors.tuition_amount || 
                (selectedProgram ? 'Automatically filled from program data' : 'Enter the total cost of tuition')
              }
              required
              fullWidth
              disabled={loadingProgramDetails || !!selectedProgram}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <CurrencyField
              name="deposit_amount"
              label="Deposit Amount"
              value={formState.values.deposit_amount}
              onChange={(value) => handleFinancialFieldChange('deposit_amount', value)}
              error={!!formState.errors.deposit_amount}
              helperText={
                formState.errors.deposit_amount || 
                'Enter any deposit amount you have already paid'
              }
              required
              fullWidth
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <CurrencyField
              name="other_funding"
              label="Other Funding"
              value={formState.values.other_funding}
              onChange={(value) => handleFinancialFieldChange('other_funding', value)}
              error={!!formState.errors.other_funding}
              helperText={
                formState.errors.other_funding || 
                'Enter any other funding sources (scholarships, grants, etc.)'
              }
              required
              fullWidth
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <CurrencyField
              name="requested_amount"
              label="Requested Amount"
              value={formState.values.requested_amount}
              onChange={(value) => handleFinancialFieldChange('requested_amount', value)}
              error={!!formState.errors.requested_amount}
              helperText={
                formState.errors.requested_amount || 
                'Calculated as: Tuition - Deposit - Other Funding'
              }
              required
              fullWidth
              disabled={true}
            />
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  );
};

export default LoanDetailsStep;