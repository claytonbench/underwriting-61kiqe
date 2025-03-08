import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit'; // ^1.9.5
import {
  SchoolState,
  School,
  SchoolDetail,
  Program,
  ProgramDetail,
  SchoolContact,
  SchoolDocument,
  SchoolFilters,
  ProgramFilters
} from '../../types/school.types';

// Define initial state for the school slice
const initialState: SchoolState = {
  schools: [],
  selectedSchool: null,
  programs: [],
  selectedProgram: null,
  loading: false,
  error: null,
  totalSchools: 0,
  totalPrograms: 0,
  schoolFilters: {
    status: null,
    name: null,
    state: null
  },
  programFilters: {
    status: null,
    name: null,
    school_id: null
  },
  page: 1,
  pageSize: 10
};

/**
 * Async thunk for fetching a paginated list of schools with optional filtering
 */
export const fetchSchools = createAsyncThunk(
  'schools/fetchSchools',
  async ({ page, pageSize, filters }: { page: number; pageSize: number; filters?: SchoolFilters }) => {
    try {
      // This would call an API service in a real implementation
      const response = await fetch(`/api/schools?page=${page}&pageSize=${pageSize}${filters ? `&filters=${JSON.stringify(filters)}` : ''}`);
      if (!response.ok) throw new Error('Failed to fetch schools');
      const data = await response.json();
      return {
        schools: data.results,
        total: data.total
      };
    } catch (error) {
      throw error instanceof Error ? error : new Error('Failed to fetch schools');
    }
  }
);

/**
 * Async thunk for fetching detailed information for a specific school
 */
export const fetchSchoolById = createAsyncThunk(
  'schools/fetchSchoolById',
  async (schoolId: string) => {
    try {
      const response = await fetch(`/api/schools/${schoolId}`);
      if (!response.ok) throw new Error('Failed to fetch school details');
      return await response.json();
    } catch (error) {
      throw error instanceof Error ? error : new Error('Failed to fetch school details');
    }
  }
);

/**
 * Async thunk for creating a new school
 */
export const createNewSchool = createAsyncThunk(
  'schools/createNewSchool',
  async (schoolData: any) => {
    try {
      const response = await fetch('/api/schools', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(schoolData)
      });
      if (!response.ok) throw new Error('Failed to create school');
      return await response.json();
    } catch (error) {
      throw error instanceof Error ? error : new Error('Failed to create school');
    }
  }
);

/**
 * Async thunk for updating an existing school
 */
export const updateExistingSchool = createAsyncThunk(
  'schools/updateExistingSchool',
  async ({ schoolId, schoolData }: { schoolId: string; schoolData: any }) => {
    try {
      const response = await fetch(`/api/schools/${schoolId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(schoolData)
      });
      if (!response.ok) throw new Error('Failed to update school');
      return await response.json();
    } catch (error) {
      throw error instanceof Error ? error : new Error('Failed to update school');
    }
  }
);

/**
 * Async thunk for deleting a school
 */
export const deleteExistingSchool = createAsyncThunk(
  'schools/deleteExistingSchool',
  async (schoolId: string) => {
    try {
      const response = await fetch(`/api/schools/${schoolId}`, {
        method: 'DELETE'
      });
      if (!response.ok) throw new Error('Failed to delete school');
      return schoolId;
    } catch (error) {
      throw error instanceof Error ? error : new Error('Failed to delete school');
    }
  }
);

/**
 * Async thunk for fetching a paginated list of programs with optional filtering
 */
export const fetchPrograms = createAsyncThunk(
  'schools/fetchPrograms',
  async ({ page, pageSize, filters }: { page: number; pageSize: number; filters?: ProgramFilters }) => {
    try {
      const response = await fetch(`/api/programs?page=${page}&pageSize=${pageSize}${filters ? `&filters=${JSON.stringify(filters)}` : ''}`);
      if (!response.ok) throw new Error('Failed to fetch programs');
      const data = await response.json();
      return {
        programs: data.results,
        total: data.total
      };
    } catch (error) {
      throw error instanceof Error ? error : new Error('Failed to fetch programs');
    }
  }
);

/**
 * Async thunk for fetching programs for a specific school
 */
export const fetchProgramsBySchool = createAsyncThunk(
  'schools/fetchProgramsBySchool',
  async ({ schoolId, page, pageSize, filters }: { schoolId: string; page: number; pageSize: number; filters?: ProgramFilters }) => {
    try {
      const response = await fetch(`/api/schools/${schoolId}/programs?page=${page}&pageSize=${pageSize}${filters ? `&filters=${JSON.stringify(filters)}` : ''}`);
      if (!response.ok) throw new Error('Failed to fetch school programs');
      const data = await response.json();
      return {
        programs: data.results,
        total: data.total
      };
    } catch (error) {
      throw error instanceof Error ? error : new Error('Failed to fetch school programs');
    }
  }
);

/**
 * Async thunk for fetching detailed information for a specific program
 */
export const fetchProgramById = createAsyncThunk(
  'schools/fetchProgramById',
  async (programId: string) => {
    try {
      const response = await fetch(`/api/programs/${programId}`);
      if (!response.ok) throw new Error('Failed to fetch program details');
      return await response.json();
    } catch (error) {
      throw error instanceof Error ? error : new Error('Failed to fetch program details');
    }
  }
);

/**
 * Async thunk for creating a new program
 */
export const createNewProgram = createAsyncThunk(
  'schools/createNewProgram',
  async (programData: any) => {
    try {
      const response = await fetch('/api/programs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(programData)
      });
      if (!response.ok) throw new Error('Failed to create program');
      return await response.json();
    } catch (error) {
      throw error instanceof Error ? error : new Error('Failed to create program');
    }
  }
);

/**
 * Async thunk for updating an existing program
 */
export const updateExistingProgram = createAsyncThunk(
  'schools/updateExistingProgram',
  async ({ programId, programData }: { programId: string; programData: any }) => {
    try {
      const response = await fetch(`/api/programs/${programId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(programData)
      });
      if (!response.ok) throw new Error('Failed to update program');
      return await response.json();
    } catch (error) {
      throw error instanceof Error ? error : new Error('Failed to update program');
    }
  }
);

/**
 * Async thunk for deleting a program
 */
export const deleteExistingProgram = createAsyncThunk(
  'schools/deleteExistingProgram',
  async (programId: string) => {
    try {
      const response = await fetch(`/api/programs/${programId}`, {
        method: 'DELETE'
      });
      if (!response.ok) throw new Error('Failed to delete program');
      return programId;
    } catch (error) {
      throw error instanceof Error ? error : new Error('Failed to delete program');
    }
  }
);

/**
 * Async thunk for creating a new version of an existing program
 */
export const createNewProgramVersion = createAsyncThunk(
  'schools/createNewProgramVersion',
  async (versionData: any) => {
    try {
      const response = await fetch('/api/program-versions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(versionData)
      });
      if (!response.ok) throw new Error('Failed to create program version');
      return await response.json();
    } catch (error) {
      throw error instanceof Error ? error : new Error('Failed to create program version');
    }
  }
);

/**
 * Async thunk for fetching contacts for a specific school
 */
export const fetchSchoolContacts = createAsyncThunk(
  'schools/fetchSchoolContacts',
  async (schoolId: string) => {
    try {
      const response = await fetch(`/api/schools/${schoolId}/contacts`);
      if (!response.ok) throw new Error('Failed to fetch school contacts');
      return await response.json();
    } catch (error) {
      throw error instanceof Error ? error : new Error('Failed to fetch school contacts');
    }
  }
);

/**
 * Async thunk for fetching documents for a specific school
 */
export const fetchSchoolDocuments = createAsyncThunk(
  'schools/fetchSchoolDocuments',
  async (schoolId: string) => {
    try {
      const response = await fetch(`/api/schools/${schoolId}/documents`);
      if (!response.ok) throw new Error('Failed to fetch school documents');
      return await response.json();
    } catch (error) {
      throw error instanceof Error ? error : new Error('Failed to fetch school documents');
    }
  }
);

// Create the school slice
const schoolSlice = createSlice({
  name: 'school',
  initialState,
  reducers: {
    // Updates the school list filters
    setSchoolFilters: (state, action: PayloadAction<SchoolFilters>) => {
      state.schoolFilters = action.payload;
    },
    // Updates the program list filters
    setProgramFilters: (state, action: PayloadAction<ProgramFilters>) => {
      state.programFilters = action.payload;
    },
    // Clears the school error message
    clearSchoolError: (state) => {
      state.error = null;
    },
    // Resets the school state to initial values
    resetSchoolState: () => initialState
  },
  extraReducers: (builder) => {
    // Fetch Schools handlers
    builder.addCase(fetchSchools.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchSchools.fulfilled, (state, action: PayloadAction<{ schools: School[]; total: number }>) => {
      state.schools = action.payload.schools;
      state.totalSchools = action.payload.total;
      state.loading = false;
      state.error = null;
    });
    builder.addCase(fetchSchools.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch schools';
    });

    // Fetch School by ID handlers
    builder.addCase(fetchSchoolById.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchSchoolById.fulfilled, (state, action: PayloadAction<SchoolDetail>) => {
      state.selectedSchool = action.payload;
      state.loading = false;
      state.error = null;
    });
    builder.addCase(fetchSchoolById.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch school details';
    });

    // Create School handlers
    builder.addCase(createNewSchool.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(createNewSchool.fulfilled, (state, action: PayloadAction<School>) => {
      state.schools.push(action.payload);
      state.totalSchools += 1;
      state.loading = false;
      state.error = null;
    });
    builder.addCase(createNewSchool.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to create school';
    });

    // Update School handlers
    builder.addCase(updateExistingSchool.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(updateExistingSchool.fulfilled, (state, action: PayloadAction<School>) => {
      const index = state.schools.findIndex(school => school.id === action.payload.id);
      if (index !== -1) {
        state.schools[index] = action.payload;
      }
      
      if (state.selectedSchool && state.selectedSchool.id === action.payload.id) {
        state.selectedSchool = {
          ...state.selectedSchool,
          ...action.payload
        };
      }
      
      state.loading = false;
      state.error = null;
    });
    builder.addCase(updateExistingSchool.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to update school';
    });

    // Delete School handlers
    builder.addCase(deleteExistingSchool.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(deleteExistingSchool.fulfilled, (state, action: PayloadAction<string>) => {
      state.schools = state.schools.filter(school => school.id !== action.payload);
      
      if (state.selectedSchool && state.selectedSchool.id === action.payload) {
        state.selectedSchool = null;
      }
      
      state.totalSchools -= 1;
      state.loading = false;
      state.error = null;
    });
    builder.addCase(deleteExistingSchool.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to delete school';
    });

    // Fetch Programs handlers
    builder.addCase(fetchPrograms.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchPrograms.fulfilled, (state, action: PayloadAction<{ programs: Program[]; total: number }>) => {
      state.programs = action.payload.programs;
      state.totalPrograms = action.payload.total;
      state.loading = false;
      state.error = null;
    });
    builder.addCase(fetchPrograms.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch programs';
    });

    // Fetch Programs by School handlers
    builder.addCase(fetchProgramsBySchool.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchProgramsBySchool.fulfilled, (state, action: PayloadAction<{ programs: Program[]; total: number }>) => {
      state.programs = action.payload.programs;
      state.totalPrograms = action.payload.total;
      state.loading = false;
      state.error = null;
    });
    builder.addCase(fetchProgramsBySchool.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch school programs';
    });

    // Fetch Program by ID handlers
    builder.addCase(fetchProgramById.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchProgramById.fulfilled, (state, action: PayloadAction<ProgramDetail>) => {
      state.selectedProgram = action.payload;
      state.loading = false;
      state.error = null;
    });
    builder.addCase(fetchProgramById.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch program details';
    });

    // Create Program handlers
    builder.addCase(createNewProgram.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(createNewProgram.fulfilled, (state, action: PayloadAction<Program>) => {
      state.programs.push(action.payload);
      state.totalPrograms += 1;
      state.loading = false;
      state.error = null;
    });
    builder.addCase(createNewProgram.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to create program';
    });

    // Update Program handlers
    builder.addCase(updateExistingProgram.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(updateExistingProgram.fulfilled, (state, action: PayloadAction<Program>) => {
      const index = state.programs.findIndex(program => program.id === action.payload.id);
      if (index !== -1) {
        state.programs[index] = action.payload;
      }
      
      if (state.selectedProgram && state.selectedProgram.id === action.payload.id) {
        state.selectedProgram = {
          ...state.selectedProgram,
          ...action.payload
        };
      }
      
      state.loading = false;
      state.error = null;
    });
    builder.addCase(updateExistingProgram.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to update program';
    });

    // Delete Program handlers
    builder.addCase(deleteExistingProgram.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(deleteExistingProgram.fulfilled, (state, action: PayloadAction<string>) => {
      state.programs = state.programs.filter(program => program.id !== action.payload);
      
      if (state.selectedProgram && state.selectedProgram.id === action.payload) {
        state.selectedProgram = null;
      }
      
      state.totalPrograms -= 1;
      state.loading = false;
      state.error = null;
    });
    builder.addCase(deleteExistingProgram.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to delete program';
    });

    // Create Program Version handlers
    builder.addCase(createNewProgramVersion.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(createNewProgramVersion.fulfilled, (state, action: PayloadAction<ProgramDetail>) => {
      state.selectedProgram = action.payload;
      
      // Update program in programs list if it exists
      const index = state.programs.findIndex(program => program.id === action.payload.id);
      if (index !== -1) {
        state.programs[index] = {
          ...state.programs[index],
          current_tuition: action.payload.current_version.tuition_amount
        };
      }
      
      state.loading = false;
      state.error = null;
    });
    builder.addCase(createNewProgramVersion.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to create program version';
    });

    // Fetch School Contacts handlers
    builder.addCase(fetchSchoolContacts.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchSchoolContacts.fulfilled, (state, action: PayloadAction<SchoolContact[]>) => {
      if (state.selectedSchool) {
        state.selectedSchool.contacts = action.payload;
      }
      state.loading = false;
      state.error = null;
    });
    builder.addCase(fetchSchoolContacts.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch school contacts';
    });

    // Fetch School Documents handlers
    builder.addCase(fetchSchoolDocuments.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchSchoolDocuments.fulfilled, (state, action: PayloadAction<SchoolDocument[]>) => {
      if (state.selectedSchool) {
        state.selectedSchool.documents = action.payload;
      }
      state.loading = false;
      state.error = null;
    });
    builder.addCase(fetchSchoolDocuments.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch school documents';
    });
  }
});

// Export actions from the slice
export const {
  setSchoolFilters,
  setProgramFilters,
  clearSchoolError,
  resetSchoolState
} = schoolSlice.actions;

// Selectors to access state in components
export const selectSchoolState = (state: any) => state.school;
export const selectSchools = (state: any) => state.school.schools;
export const selectSelectedSchool = (state: any) => state.school.selectedSchool;
export const selectPrograms = (state: any) => state.school.programs;
export const selectSelectedProgram = (state: any) => state.school.selectedProgram;
export const selectSchoolLoading = (state: any) => state.school.loading;
export const selectSchoolError = (state: any) => state.school.error;
export const selectTotalSchools = (state: any) => state.school.totalSchools;
export const selectTotalPrograms = (state: any) => state.school.totalPrograms;
export const selectSchoolFilters = (state: any) => state.school.schoolFilters;
export const selectProgramFilters = (state: any) => state.school.programFilters;

// Export both the reducer and slice
export default schoolSlice.reducer;