import { apiClient, handleApiError } from '../config/api';
import { API_ENDPOINTS } from '../config/constants';
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
  SchoolContact,
  SchoolContactCreateRequest,
  SchoolContactUpdateRequest,
  SchoolFilters,
  ProgramFilters,
  SchoolListResponse,
  ProgramListResponse
} from '../types/school.types';
import { ApiResponse, PaginationParams } from '../types/common.types';

/**
 * Fetches a paginated list of schools with optional filtering
 * 
 * @param params - Pagination parameters
 * @param filters - Optional filters for schools
 * @returns Promise resolving to a paginated list of schools
 */
export const getSchools = async (
  params: PaginationParams,
  filters?: SchoolFilters
): Promise<ApiResponse<SchoolListResponse>> => {
  try {
    // Construct query parameters
    const queryParams = new URLSearchParams({
      page: params.page.toString(),
      page_size: params.page_size.toString(),
      ...filters?.status && { status: filters.status },
      ...filters?.name && { name: filters.name },
      ...filters?.state && { state: filters.state },
    });

    // Make API request
    const response = await apiClient.get(
      `${API_ENDPOINTS.SCHOOLS.BASE}?${queryParams.toString()}`
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches detailed information for a specific school by ID
 * 
 * @param schoolId - Unique identifier of the school
 * @returns Promise resolving to detailed school information
 */
export const getSchoolById = async (
  schoolId: string
): Promise<ApiResponse<SchoolDetail>> => {
  try {
    const response = await apiClient.get(
      API_ENDPOINTS.SCHOOLS.BY_ID(schoolId)
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Creates a new school with the provided information
 * 
 * @param schoolData - School creation data
 * @returns Promise resolving to the created school
 */
export const createSchool = async (
  schoolData: SchoolCreateRequest
): Promise<ApiResponse<School>> => {
  try {
    const response = await apiClient.post(
      API_ENDPOINTS.SCHOOLS.BASE,
      schoolData
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Updates an existing school with the provided information
 * 
 * @param schoolId - Unique identifier of the school to update
 * @param schoolData - School update data
 * @returns Promise resolving to the updated school
 */
export const updateSchool = async (
  schoolId: string,
  schoolData: SchoolUpdateRequest
): Promise<ApiResponse<School>> => {
  try {
    const response = await apiClient.put(
      API_ENDPOINTS.SCHOOLS.BY_ID(schoolId),
      schoolData
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Deletes a school by ID
 * 
 * @param schoolId - Unique identifier of the school to delete
 * @returns Promise resolving to a success response with no data
 */
export const deleteSchool = async (
  schoolId: string
): Promise<ApiResponse<void>> => {
  try {
    const response = await apiClient.delete(
      API_ENDPOINTS.SCHOOLS.BY_ID(schoolId)
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches a paginated list of programs with optional filtering
 * 
 * @param params - Pagination parameters
 * @param filters - Optional filters for programs
 * @returns Promise resolving to a paginated list of programs
 */
export const getPrograms = async (
  params: PaginationParams,
  filters?: ProgramFilters
): Promise<ApiResponse<ProgramListResponse>> => {
  try {
    // Construct query parameters
    const queryParams = new URLSearchParams({
      page: params.page.toString(),
      page_size: params.page_size.toString(),
      ...filters?.status && { status: filters.status },
      ...filters?.name && { name: filters.name },
      ...filters?.school_id && { school_id: filters.school_id },
    });

    // Make API request
    const response = await apiClient.get(
      `${API_ENDPOINTS.SCHOOLS.PROGRAMS}?${queryParams.toString()}`
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches detailed information for a specific program by ID
 * 
 * @param programId - Unique identifier of the program
 * @returns Promise resolving to detailed program information
 */
export const getProgramById = async (
  programId: string
): Promise<ApiResponse<ProgramDetail>> => {
  try {
    const response = await apiClient.get(
      API_ENDPOINTS.SCHOOLS.PROGRAM_BY_ID(programId)
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches all programs for a specific school
 * 
 * @param schoolId - Unique identifier of the school
 * @param params - Pagination parameters
 * @returns Promise resolving to a paginated list of school programs
 */
export const getSchoolPrograms = async (
  schoolId: string,
  params: PaginationParams
): Promise<ApiResponse<ProgramListResponse>> => {
  try {
    // Construct query parameters
    const queryParams = new URLSearchParams({
      page: params.page.toString(),
      page_size: params.page_size.toString(),
      school_id: schoolId,
    });

    // Make API request
    const response = await apiClient.get(
      `${API_ENDPOINTS.SCHOOLS.PROGRAMS}?${queryParams.toString()}`
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Creates a new program with the provided information
 * 
 * @param programData - Program creation data
 * @returns Promise resolving to the created program
 */
export const createProgram = async (
  programData: ProgramCreateRequest
): Promise<ApiResponse<Program>> => {
  try {
    const response = await apiClient.post(
      API_ENDPOINTS.SCHOOLS.PROGRAMS,
      programData
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Updates an existing program with the provided information
 * 
 * @param programId - Unique identifier of the program to update
 * @param programData - Program update data
 * @returns Promise resolving to the updated program
 */
export const updateProgram = async (
  programId: string,
  programData: ProgramUpdateRequest
): Promise<ApiResponse<Program>> => {
  try {
    const response = await apiClient.put(
      API_ENDPOINTS.SCHOOLS.PROGRAM_BY_ID(programId),
      programData
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Deletes a program by ID
 * 
 * @param programId - Unique identifier of the program to delete
 * @returns Promise resolving to a success response with no data
 */
export const deleteProgram = async (
  programId: string
): Promise<ApiResponse<void>> => {
  try {
    const response = await apiClient.delete(
      API_ENDPOINTS.SCHOOLS.PROGRAM_BY_ID(programId)
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Creates a new version of an existing program
 * 
 * @param versionData - Program version creation data
 * @returns Promise resolving to the program with the new version
 */
export const createProgramVersion = async (
  versionData: ProgramVersionCreateRequest
): Promise<ApiResponse<ProgramDetail>> => {
  try {
    // Create version as a sub-resource of the program
    const response = await apiClient.post(
      `${API_ENDPOINTS.SCHOOLS.PROGRAM_BY_ID(versionData.program_id)}/versions`,
      versionData
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches all contacts for a specific school
 * 
 * @param schoolId - Unique identifier of the school
 * @returns Promise resolving to a list of school contacts
 */
export const getSchoolContacts = async (
  schoolId: string
): Promise<ApiResponse<SchoolContact[]>> => {
  try {
    const response = await apiClient.get(
      `${API_ENDPOINTS.SCHOOLS.CONTACTS}?school_id=${schoolId}`
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Creates a new contact for a school
 * 
 * @param contactData - School contact creation data
 * @returns Promise resolving to the created school contact
 */
export const createSchoolContact = async (
  contactData: SchoolContactCreateRequest
): Promise<ApiResponse<SchoolContact>> => {
  try {
    const response = await apiClient.post(
      API_ENDPOINTS.SCHOOLS.CONTACTS,
      contactData
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Updates an existing school contact
 * 
 * @param contactId - Unique identifier of the contact to update
 * @param contactData - School contact update data
 * @returns Promise resolving to the updated school contact
 */
export const updateSchoolContact = async (
  contactId: string,
  contactData: SchoolContactUpdateRequest
): Promise<ApiResponse<SchoolContact>> => {
  try {
    const response = await apiClient.put(
      `${API_ENDPOINTS.SCHOOLS.CONTACTS}/${contactId}`,
      contactData
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Deletes a school contact by ID
 * 
 * @param contactId - Unique identifier of the contact to delete
 * @returns Promise resolving to a success response with no data
 */
export const deleteSchoolContact = async (
  contactId: string
): Promise<ApiResponse<void>> => {
  try {
    const response = await apiClient.delete(
      `${API_ENDPOINTS.SCHOOLS.CONTACTS}/${contactId}`
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};