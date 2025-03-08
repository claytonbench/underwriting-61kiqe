import { createAsyncThunk } from '@reduxjs/toolkit'; // ^1.9.5

// Import application-related type definitions
import {
  ApplicationFormData,
  ApplicationFilters,
  ApplicationSort,
  ApplicationDocument,
  ApplicationStatusHistory,
  ApplicationListItem,
  LoanApplication
} from '../../types/application.types';

// Import API functions for application operations
import {
  getApplications,
  getApplication,
  createApplication,
  updateApplication,
  submitApplication,
  saveApplicationDraft,
  uploadApplicationDocument,
  deleteApplicationDocument,
  getApplicationDocuments,
  getApplicationStatusHistory,
  cancelApplication,
  getApplicationsBySchool,
  getApplicationsByBorrower
} from '../../api/applications';

/**
 * Async thunk to fetch a paginated list of applications
 */
export const fetchApplications = createAsyncThunk(
  'applications/fetchApplications',
  async ({ 
    page, 
    pageSize, 
    filters, 
    sort 
  }: { 
    page: number; 
    pageSize: number; 
    filters?: ApplicationFilters; 
    sort?: ApplicationSort 
  }) => {
    const response = await getApplications({ 
      page, 
      page_size: pageSize, 
      filters, 
      sort 
    });
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch applications');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to fetch a single application by ID with all related details
 */
export const fetchApplicationDetail = createAsyncThunk(
  'applications/fetchApplicationDetail',
  async (id: string) => {
    const response = await getApplication(id);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch application details');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to create a new application
 */
export const createNewApplication = createAsyncThunk(
  'applications/createNewApplication',
  async (applicationData: ApplicationFormData) => {
    const response = await createApplication({
      form_data: applicationData,
      created_by: '' // This will be populated from the auth state by the API middleware
    });
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to create application');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to update an existing application
 */
export const updateExistingApplication = createAsyncThunk(
  'applications/updateExistingApplication',
  async ({ id, applicationData }: { id: string; applicationData: ApplicationFormData }) => {
    const response = await updateApplication(id, {
      application_id: id,
      form_data: applicationData
    });
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to update application');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to submit an application for review
 */
export const submitExistingApplication = createAsyncThunk(
  'applications/submitExistingApplication',
  async (id: string) => {
    const response = await submitApplication(id);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to submit application');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to save a draft of an application
 */
export const saveApplicationDraftAction = createAsyncThunk(
  'applications/saveApplicationDraftAction',
  async ({ id, applicationData }: { id: string; applicationData: ApplicationFormData }) => {
    const response = await saveApplicationDraft(id, applicationData);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to save application draft');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to cancel an application
 */
export const cancelExistingApplication = createAsyncThunk(
  'applications/cancelExistingApplication',
  async (id: string) => {
    const response = await cancelApplication(id);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to cancel application');
    }
    
    return id; // Return the ID for the reducer to handle removal
  }
);

/**
 * Async thunk to fetch documents for an application
 */
export const fetchApplicationDocuments = createAsyncThunk(
  'applications/fetchApplicationDocuments',
  async (applicationId: string) => {
    const response = await getApplicationDocuments(applicationId);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch application documents');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to upload a document for an application
 */
export const uploadDocument = createAsyncThunk(
  'applications/uploadDocument',
  async ({ 
    applicationId, 
    documentType, 
    file 
  }: { 
    applicationId: string; 
    documentType: string; 
    file: File 
  }) => {
    const response = await uploadApplicationDocument({
      application_id: applicationId,
      document_type: documentType,
      file
    });
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to upload document');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to delete a document from an application
 */
export const deleteDocument = createAsyncThunk(
  'applications/deleteDocument',
  async ({ 
    applicationId, 
    documentId 
  }: { 
    applicationId: string; 
    documentId: string 
  }) => {
    const response = await deleteApplicationDocument(applicationId, documentId);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to delete document');
    }
    
    return { applicationId, documentId }; // Return IDs for the reducer to handle removal
  }
);

/**
 * Async thunk to fetch status history for an application
 */
export const fetchStatusHistory = createAsyncThunk(
  'applications/fetchStatusHistory',
  async (applicationId: string) => {
    const response = await getApplicationStatusHistory(applicationId);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch status history');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to fetch a paginated list of applications for a specific school
 */
export const fetchSchoolApplications = createAsyncThunk(
  'applications/fetchSchoolApplications',
  async ({ 
    schoolId,
    page, 
    pageSize, 
    filters, 
    sort 
  }: { 
    schoolId: string;
    page: number; 
    pageSize: number; 
    filters?: ApplicationFilters; 
    sort?: ApplicationSort 
  }) => {
    const response = await getApplicationsBySchool(schoolId, { 
      page, 
      page_size: pageSize, 
      filters, 
      sort 
    });
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch school applications');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to fetch a paginated list of applications for the current borrower
 */
export const fetchBorrowerApplications = createAsyncThunk(
  'applications/fetchBorrowerApplications',
  async ({ 
    page, 
    pageSize, 
    filters, 
    sort 
  }: { 
    page: number; 
    pageSize: number; 
    filters?: ApplicationFilters; 
    sort?: ApplicationSort 
  }) => {
    const response = await getApplicationsByBorrower({ 
      page, 
      page_size: pageSize, 
      filters, 
      sort 
    });
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch borrower applications');
    }
    
    return response.data;
  }
);

/**
 * Synchronous action creator to update application form data in the Redux store
 */
export const setApplicationFormData = (formData: ApplicationFormData) => ({
  type: 'applications/setApplicationFormData',
  payload: formData
});

/**
 * Synchronous action creator to reset application form state in the Redux store
 */
export const resetApplicationForm = () => ({
  type: 'applications/resetApplicationForm'
});

/**
 * Synchronous action creator to reset current application state in the Redux store
 */
export const resetCurrentApplication = () => ({
  type: 'applications/resetCurrentApplication'
});