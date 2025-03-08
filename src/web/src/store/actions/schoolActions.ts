import { ThunkAction, Dispatch, AnyAction } from '@reduxjs/toolkit'; // ^1.9.5

// Import types for schools and programs
import {
  School,
  SchoolDetail,
  SchoolCreateRequest,
  SchoolUpdateRequest,
  Program,
  ProgramDetail,
  ProgramCreateRequest,
  ProgramUpdateRequest,
  ProgramVersionCreateRequest,
  SchoolFilters,
  ProgramFilters
} from '../../types/school.types';

// Import actions from Redux slice
import {
  setSchoolFilters,
  setProgramFilters,
  resetSchoolState,
  clearSchoolError,
  
  // Import async thunks
  fetchSchools,
  fetchSchoolById,
  createNewSchool,
  updateExistingSchool,
  deleteExistingSchool,
  fetchPrograms,
  fetchProgramsBySchool,
  fetchProgramById,
  createNewProgram,
  updateExistingProgram,
  deleteExistingProgram,
  createNewProgramVersion,
  fetchProgramVersions,
  fetchSchoolContacts,
  createNewSchoolContact,
  updateExistingSchoolContact,
  deleteExistingSchoolContact,
  fetchSchoolDocuments,
  uploadSchoolDocumentThunk,
  deleteSchoolDocumentThunk,
  getDocumentDownloadUrl
} from '../slices/schoolSlice';

/**
 * Action creator that loads schools with optional pagination and filtering
 * 
 * @param options - Optional pagination and filtering parameters
 * @returns Thunk action that dispatches the fetchSchools async thunk
 */
export const loadSchools = (
  options: { page?: number; pageSize?: number; filters?: SchoolFilters } = {}
): ThunkAction<Promise<void>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      const { page = 1, pageSize = 10, filters } = options;
      
      // Set filters if provided
      if (filters) {
        dispatch(setSchoolFilters(filters));
      }
      
      // Fetch schools with pagination and filters
      await dispatch(fetchSchools({ page, pageSize, filters }));
    } catch (error) {
      console.error('Error loading schools:', error);
      throw error;
    }
  };
};

/**
 * Action creator that loads detailed information for a specific school
 * 
 * @param schoolId - Unique identifier of the school
 * @returns Thunk action that dispatches the fetchSchoolById async thunk
 */
export const loadSchoolDetails = (
  schoolId: string
): ThunkAction<Promise<void>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      await dispatch(fetchSchoolById(schoolId));
    } catch (error) {
      console.error('Error loading school details:', error);
      throw error;
    }
  };
};

/**
 * Action creator that creates a new school
 * 
 * @param schoolData - School creation data
 * @returns Thunk action that dispatches the createNewSchool async thunk and returns the created school
 */
export const createSchool = (
  schoolData: SchoolCreateRequest
): ThunkAction<Promise<School>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      const result = await dispatch(createNewSchool(schoolData));
      return result.payload as School;
    } catch (error) {
      console.error('Error creating school:', error);
      throw error;
    }
  };
};

/**
 * Action creator that updates an existing school
 * 
 * @param schoolId - Unique identifier of the school to update
 * @param schoolData - School update data
 * @returns Thunk action that dispatches the updateExistingSchool async thunk and returns the updated school
 */
export const updateSchool = (
  schoolId: string, 
  schoolData: SchoolUpdateRequest
): ThunkAction<Promise<School>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      const result = await dispatch(updateExistingSchool({ schoolId, schoolData }));
      return result.payload as School;
    } catch (error) {
      console.error('Error updating school:', error);
      throw error;
    }
  };
};

/**
 * Action creator that deletes a school
 * 
 * @param schoolId - Unique identifier of the school to delete
 * @returns Thunk action that dispatches the deleteExistingSchool async thunk
 */
export const deleteSchool = (
  schoolId: string
): ThunkAction<Promise<void>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      await dispatch(deleteExistingSchool(schoolId));
    } catch (error) {
      console.error('Error deleting school:', error);
      throw error;
    }
  };
};

/**
 * Action creator that loads programs with optional pagination and filtering
 * 
 * @param options - Optional pagination and filtering parameters
 * @returns Thunk action that dispatches the fetchPrograms async thunk
 */
export const loadPrograms = (
  options: { page?: number; pageSize?: number; filters?: ProgramFilters } = {}
): ThunkAction<Promise<void>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      const { page = 1, pageSize = 10, filters } = options;
      
      // Set filters if provided
      if (filters) {
        dispatch(setProgramFilters(filters));
      }
      
      // Fetch programs with pagination and filters
      await dispatch(fetchPrograms({ page, pageSize, filters }));
    } catch (error) {
      console.error('Error loading programs:', error);
      throw error;
    }
  };
};

/**
 * Action creator that loads programs for a specific school
 * 
 * @param schoolId - Unique identifier of the school
 * @param options - Optional pagination and filtering parameters
 * @returns Thunk action that dispatches the fetchProgramsBySchool async thunk
 */
export const loadSchoolPrograms = (
  schoolId: string,
  options: { page?: number; pageSize?: number; filters?: ProgramFilters } = {}
): ThunkAction<Promise<void>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      const { page = 1, pageSize = 10, filters } = options;
      
      // Set filters if provided
      if (filters) {
        dispatch(setProgramFilters(filters));
      }
      
      // Fetch programs for the specified school
      await dispatch(fetchProgramsBySchool({ schoolId, page, pageSize, filters }));
    } catch (error) {
      console.error('Error loading school programs:', error);
      throw error;
    }
  };
};

/**
 * Action creator that loads detailed information for a specific program
 * 
 * @param programId - Unique identifier of the program
 * @returns Thunk action that dispatches the fetchProgramById async thunk
 */
export const loadProgramDetails = (
  programId: string
): ThunkAction<Promise<void>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      await dispatch(fetchProgramById(programId));
    } catch (error) {
      console.error('Error loading program details:', error);
      throw error;
    }
  };
};

/**
 * Action creator that creates a new program
 * 
 * @param programData - Program creation data
 * @returns Thunk action that dispatches the createNewProgram async thunk and returns the created program
 */
export const createProgram = (
  programData: ProgramCreateRequest
): ThunkAction<Promise<Program>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      const result = await dispatch(createNewProgram(programData));
      return result.payload as Program;
    } catch (error) {
      console.error('Error creating program:', error);
      throw error;
    }
  };
};

/**
 * Action creator that updates an existing program
 * 
 * @param programId - Unique identifier of the program to update
 * @param programData - Program update data
 * @returns Thunk action that dispatches the updateExistingProgram async thunk and returns the updated program
 */
export const updateProgram = (
  programId: string, 
  programData: ProgramUpdateRequest
): ThunkAction<Promise<Program>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      const result = await dispatch(updateExistingProgram({ programId, programData }));
      return result.payload as Program;
    } catch (error) {
      console.error('Error updating program:', error);
      throw error;
    }
  };
};

/**
 * Action creator that deletes a program
 * 
 * @param programId - Unique identifier of the program to delete
 * @returns Thunk action that dispatches the deleteExistingProgram async thunk
 */
export const deleteProgram = (
  programId: string
): ThunkAction<Promise<void>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      await dispatch(deleteExistingProgram(programId));
    } catch (error) {
      console.error('Error deleting program:', error);
      throw error;
    }
  };
};

/**
 * Action creator that creates a new version of an existing program
 * 
 * @param versionData - Program version creation data
 * @returns Thunk action that dispatches the createNewProgramVersion async thunk
 */
export const createProgramVersion = (
  versionData: ProgramVersionCreateRequest
): ThunkAction<Promise<void>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      await dispatch(createNewProgramVersion(versionData));
    } catch (error) {
      console.error('Error creating program version:', error);
      throw error;
    }
  };
};

/**
 * Action creator that loads all versions of a specific program
 * 
 * @param programId - Unique identifier of the program
 * @returns Thunk action that dispatches the fetchProgramVersions async thunk
 */
export const loadProgramVersions = (
  programId: string
): ThunkAction<Promise<void>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      await dispatch(fetchProgramVersions(programId));
    } catch (error) {
      console.error('Error loading program versions:', error);
      throw error;
    }
  };
};

/**
 * Action creator that loads contacts for a specific school
 * 
 * @param schoolId - Unique identifier of the school
 * @returns Thunk action that dispatches the fetchSchoolContacts async thunk
 */
export const loadSchoolContacts = (
  schoolId: string
): ThunkAction<Promise<void>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      await dispatch(fetchSchoolContacts(schoolId));
    } catch (error) {
      console.error('Error loading school contacts:', error);
      throw error;
    }
  };
};

/**
 * Action creator that creates a new contact for a school
 * 
 * @param contactData - School contact creation data
 * @returns Thunk action that dispatches the createNewSchoolContact async thunk
 */
export const createSchoolContact = (
  contactData: any
): ThunkAction<Promise<void>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      await dispatch(createNewSchoolContact(contactData));
    } catch (error) {
      console.error('Error creating school contact:', error);
      throw error;
    }
  };
};

/**
 * Action creator that updates an existing school contact
 * 
 * @param contactId - Unique identifier of the contact to update
 * @param contactData - School contact update data
 * @returns Thunk action that dispatches the updateExistingSchoolContact async thunk
 */
export const updateSchoolContact = (
  contactId: string, 
  contactData: any
): ThunkAction<Promise<void>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      await dispatch(updateExistingSchoolContact({ contactId, contactData }));
    } catch (error) {
      console.error('Error updating school contact:', error);
      throw error;
    }
  };
};

/**
 * Action creator that deletes a school contact
 * 
 * @param contactId - Unique identifier of the contact to delete
 * @returns Thunk action that dispatches the deleteExistingSchoolContact async thunk
 */
export const deleteSchoolContact = (
  contactId: string
): ThunkAction<Promise<void>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      await dispatch(deleteExistingSchoolContact(contactId));
    } catch (error) {
      console.error('Error deleting school contact:', error);
      throw error;
    }
  };
};

/**
 * Action creator that loads documents for a specific school
 * 
 * @param schoolId - Unique identifier of the school
 * @returns Thunk action that dispatches the fetchSchoolDocuments async thunk
 */
export const loadSchoolDocuments = (
  schoolId: string
): ThunkAction<Promise<void>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      await dispatch(fetchSchoolDocuments(schoolId));
    } catch (error) {
      console.error('Error loading school documents:', error);
      throw error;
    }
  };
};

/**
 * Action creator that uploads a document for a school
 * 
 * @param schoolId - Unique identifier of the school
 * @param documentType - Type of document being uploaded
 * @param file - File to upload
 * @param status - Status of the document
 * @returns Thunk action that dispatches the uploadSchoolDocumentThunk async thunk
 */
export const uploadSchoolDocument = (
  schoolId: string,
  documentType: string,
  file: File,
  status: string
): ThunkAction<Promise<void>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      await dispatch(uploadSchoolDocumentThunk({ schoolId, documentType, file, status }));
    } catch (error) {
      console.error('Error uploading school document:', error);
      throw error;
    }
  };
};

/**
 * Action creator that deletes a school document
 * 
 * @param schoolId - Unique identifier of the school
 * @param documentId - Unique identifier of the document to delete
 * @returns Thunk action that dispatches the deleteSchoolDocumentThunk async thunk
 */
export const deleteSchoolDocument = (
  schoolId: string,
  documentId: string
): ThunkAction<Promise<void>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      await dispatch(deleteSchoolDocumentThunk({ schoolId, documentId }));
    } catch (error) {
      console.error('Error deleting school document:', error);
      throw error;
    }
  };
};

/**
 * Action creator that gets a download URL for a school document
 * 
 * @param schoolId - Unique identifier of the school
 * @param documentId - Unique identifier of the document
 * @returns Thunk action that dispatches the getDocumentDownloadUrl async thunk and returns the download URL
 */
export const getSchoolDocumentDownloadUrl = (
  schoolId: string,
  documentId: string
): ThunkAction<Promise<string>, any, unknown, AnyAction> => {
  return async (dispatch: Dispatch) => {
    try {
      const result = await dispatch(getDocumentDownloadUrl({ schoolId, documentId }));
      return result.payload as string;
    } catch (error) {
      console.error('Error getting document download URL:', error);
      throw error;
    }
  };
};

/**
 * Action creator that resets the school state to its initial values
 * 
 * @returns Thunk action that dispatches the resetSchoolState action
 */
export const resetSchools = (): ThunkAction<void, any, unknown, AnyAction> => {
  return (dispatch: Dispatch) => {
    dispatch(resetSchoolState());
  };
};

/**
 * Action creator that clears any errors in the school state
 * 
 * @returns Thunk action that dispatches the clearSchoolError action
 */
export const clearErrors = (): ThunkAction<void, any, unknown, AnyAction> => {
  return (dispatch: Dispatch) => {
    dispatch(clearSchoolError());
  };
};