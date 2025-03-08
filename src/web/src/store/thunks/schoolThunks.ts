import { createAsyncThunk } from '@reduxjs/toolkit'; // v1.9.5
import {
  School,
  SchoolDetail,
  Program,
  ProgramDetail,
  SchoolContact,
  SchoolDocument,
  SchoolFilters,
  ProgramFilters,
  SchoolCreateRequest,
  SchoolUpdateRequest,
  ProgramCreateRequest,
  ProgramUpdateRequest,
  ProgramVersionCreateRequest,
  SchoolContactCreateRequest,
  SchoolContactUpdateRequest
} from '../../types/school.types';
import {
  getSchools,
  getSchoolById,
  createSchool,
  updateSchool,
  deleteSchool,
  getPrograms,
  getProgramById,
  getSchoolPrograms,
  createProgram,
  updateProgram,
  deleteProgram,
  createProgramVersion,
  getSchoolContacts,
  createSchoolContact,
  updateSchoolContact,
  deleteSchoolContact
} from '../../api/schools';
import { PaginationParams } from '../../types/common.types';

/**
 * Fetch paginated list of schools with optional filtering
 */
export const fetchSchools = createAsyncThunk(
  'schools/fetchSchools',
  async ({ page, pageSize, filters }: { page: number; pageSize: number; filters?: SchoolFilters }) => {
    try {
      const response = await getSchools({ page, page_size: pageSize }, filters);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch schools');
      }
      
      return {
        schools: response.data?.results || [],
        total: response.data?.total || 0
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      throw new Error(errorMessage);
    }
  }
);

/**
 * Fetch detailed information for a specific school
 */
export const fetchSchoolById = createAsyncThunk(
  'schools/fetchSchoolById',
  async (schoolId: string) => {
    try {
      const response = await getSchoolById(schoolId);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch school details');
      }
      
      return response.data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      throw new Error(errorMessage);
    }
  }
);

/**
 * Create a new school
 */
export const createNewSchool = createAsyncThunk(
  'schools/createNewSchool',
  async (schoolData: SchoolCreateRequest) => {
    try {
      const response = await createSchool(schoolData);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to create school');
      }
      
      return response.data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      throw new Error(errorMessage);
    }
  }
);

/**
 * Update an existing school
 */
export const updateExistingSchool = createAsyncThunk(
  'schools/updateExistingSchool',
  async ({ schoolId, schoolData }: { schoolId: string; schoolData: SchoolUpdateRequest }) => {
    try {
      const response = await updateSchool(schoolId, schoolData);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to update school');
      }
      
      return response.data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      throw new Error(errorMessage);
    }
  }
);

/**
 * Delete a school
 */
export const deleteExistingSchool = createAsyncThunk(
  'schools/deleteExistingSchool',
  async (schoolId: string) => {
    try {
      const response = await deleteSchool(schoolId);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to delete school');
      }
      
      return schoolId;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      throw new Error(errorMessage);
    }
  }
);

/**
 * Fetch paginated list of programs with optional filtering
 */
export const fetchPrograms = createAsyncThunk(
  'schools/fetchPrograms',
  async ({ page, pageSize, filters }: { page: number; pageSize: number; filters?: ProgramFilters }) => {
    try {
      const response = await getPrograms({ page, page_size: pageSize }, filters);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch programs');
      }
      
      return {
        programs: response.data?.results || [],
        total: response.data?.total || 0
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      throw new Error(errorMessage);
    }
  }
);

/**
 * Fetch programs for a specific school
 */
export const fetchProgramsBySchool = createAsyncThunk(
  'schools/fetchProgramsBySchool',
  async ({ schoolId, page, pageSize, filters }: { schoolId: string; page: number; pageSize: number; filters?: ProgramFilters }) => {
    try {
      const response = await getSchoolPrograms(schoolId, { page, page_size: pageSize });
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch school programs');
      }
      
      return {
        programs: response.data?.results || [],
        total: response.data?.total || 0
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      throw new Error(errorMessage);
    }
  }
);

/**
 * Fetch detailed information for a specific program
 */
export const fetchProgramById = createAsyncThunk(
  'schools/fetchProgramById',
  async (programId: string) => {
    try {
      const response = await getProgramById(programId);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch program details');
      }
      
      return response.data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      throw new Error(errorMessage);
    }
  }
);

/**
 * Create a new program
 */
export const createNewProgram = createAsyncThunk(
  'schools/createNewProgram',
  async (programData: ProgramCreateRequest) => {
    try {
      const response = await createProgram(programData);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to create program');
      }
      
      return response.data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      throw new Error(errorMessage);
    }
  }
);

/**
 * Update an existing program
 */
export const updateExistingProgram = createAsyncThunk(
  'schools/updateExistingProgram',
  async ({ programId, programData }: { programId: string; programData: ProgramUpdateRequest }) => {
    try {
      const response = await updateProgram(programId, programData);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to update program');
      }
      
      return response.data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      throw new Error(errorMessage);
    }
  }
);

/**
 * Delete a program
 */
export const deleteExistingProgram = createAsyncThunk(
  'schools/deleteExistingProgram',
  async (programId: string) => {
    try {
      const response = await deleteProgram(programId);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to delete program');
      }
      
      return programId;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      throw new Error(errorMessage);
    }
  }
);

/**
 * Create a new version of an existing program
 */
export const createNewProgramVersion = createAsyncThunk(
  'schools/createNewProgramVersion',
  async (versionData: ProgramVersionCreateRequest) => {
    try {
      const response = await createProgramVersion(versionData);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to create program version');
      }
      
      return response.data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      throw new Error(errorMessage);
    }
  }
);

/**
 * Fetch contacts for a specific school
 */
export const fetchSchoolContacts = createAsyncThunk(
  'schools/fetchSchoolContacts',
  async (schoolId: string) => {
    try {
      const response = await getSchoolContacts(schoolId);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch school contacts');
      }
      
      return response.data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      throw new Error(errorMessage);
    }
  }
);

/**
 * Create a new contact for a school
 */
export const createSchoolContact = createAsyncThunk(
  'schools/createSchoolContact',
  async (contactData: SchoolContactCreateRequest) => {
    try {
      const response = await createSchoolContact(contactData);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to create school contact');
      }
      
      return response.data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      throw new Error(errorMessage);
    }
  }
);

/**
 * Update an existing school contact
 */
export const updateSchoolContact = createAsyncThunk(
  'schools/updateSchoolContact',
  async ({ contactId, contactData }: { contactId: string; contactData: SchoolContactUpdateRequest }) => {
    try {
      const response = await updateSchoolContact(contactId, contactData);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to update school contact');
      }
      
      return response.data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      throw new Error(errorMessage);
    }
  }
);

/**
 * Delete a school contact
 */
export const deleteSchoolContact = createAsyncThunk(
  'schools/deleteSchoolContact',
  async (contactId: string) => {
    try {
      const response = await deleteSchoolContact(contactId);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to delete school contact');
      }
      
      return contactId;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      throw new Error(errorMessage);
    }
  }
);

/**
 * Fetch documents for a specific school
 */
export const fetchSchoolDocuments = createAsyncThunk(
  'schools/fetchSchoolDocuments',
  async (schoolId: string) => {
    try {
      // This API function is referenced in the thunk but not provided in the imports
      // Using a more generic approach to maintain the expected structure
      const response = await fetch(`/api/schools/${schoolId}/documents`);
      if (!response.ok) {
        throw new Error('Failed to fetch school documents');
      }
      
      const data = await response.json();
      return data.documents || [];
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      throw new Error(errorMessage);
    }
  }
);