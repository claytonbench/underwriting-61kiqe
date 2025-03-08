/**
 * Redux thunks for handling asynchronous operations related to loan applications
 * in the loan management system. These thunks encapsulate API calls and dispatch
 * appropriate actions to update the Redux store based on the results.
 */
import { createAsyncThunk } from '@reduxjs/toolkit'; // ^1.9.5

import {
  ApplicationDetail,
  ApplicationFormData,
  ApplicationFilters,
  ApplicationSort,
  ApplicationListItem,
  ApplicationDocument,
  ApplicationStatusHistory,
  ApplicationRequiredAction,
  ApplicationTimelineEvent,
  ApplicationCountsByStatus
} from '../../types/application.types';
import { UUID } from '../../types/common.types';
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
  getApplicationsByBorrower,
  getApplicationRequiredActions,
  getApplicationTimeline,
  getApplicationCountsByStatus,
  updateApplicationStatus
} from '../../api/applications';
import { handleApiError } from '../../config/api';

/**
 * Thunk to fetch a paginated list of applications with optional filtering and sorting
 */
export const fetchApplications = createAsyncThunk(
  'applications/fetchApplications',
  async ({ page = 1, pageSize = 10, filters, sort }: {
    page?: number;
    pageSize?: number;
    filters?: ApplicationFilters;
    sort?: ApplicationSort;
  }, { dispatch }) => {
    try {
      dispatch({ type: 'application/setLoading', payload: true });
      dispatch({ type: 'application/setError', payload: null });

      const response = await getApplications({ page, page_size: pageSize, filters, sort });

      if (response.success && response.data) {
        dispatch({ type: 'application/setApplications', payload: response.data.results });
        dispatch({ type: 'application/setTotalApplications', payload: response.data.total });
        dispatch({ type: 'application/setLoading', payload: false });
      } else {
        throw new Error(response.message || 'Failed to fetch applications');
      }
    } catch (error) {
      handleApiError(error);
      dispatch({ type: 'application/setError', payload: error.message });
      dispatch({ type: 'application/setLoading', payload: false });
    }
  }
);

/**
 * Thunk to fetch a paginated list of applications for a specific school
 */
export const fetchApplicationsBySchool = createAsyncThunk(
  'applications/fetchApplicationsBySchool',
  async ({ schoolId, page = 1, pageSize = 10, filters, sort }: {
    schoolId: UUID;
    page?: number;
    pageSize?: number;
    filters?: ApplicationFilters;
    sort?: ApplicationSort;
  }, { dispatch }) => {
    try {
      dispatch({ type: 'application/setLoading', payload: true });
      dispatch({ type: 'application/setError', payload: null });

      const response = await getApplicationsBySchool(schoolId, {
        page,
        page_size: pageSize,
        filters,
        sort
      });

      if (response.success && response.data) {
        dispatch({ type: 'application/setApplications', payload: response.data.results });
        dispatch({ type: 'application/setTotalApplications', payload: response.data.total });
        dispatch({ type: 'application/setLoading', payload: false });
      } else {
        throw new Error(response.message || 'Failed to fetch applications by school');
      }
    } catch (error) {
      handleApiError(error);
      dispatch({ type: 'application/setError', payload: error.message });
      dispatch({ type: 'application/setLoading', payload: false });
    }
  }
);

/**
 * Thunk to fetch a paginated list of applications for the current borrower
 */
export const fetchApplicationsByBorrower = createAsyncThunk(
  'applications/fetchApplicationsByBorrower',
  async ({ page = 1, pageSize = 10, filters, sort }: {
    page?: number;
    pageSize?: number;
    filters?: ApplicationFilters;
    sort?: ApplicationSort;
  }, { dispatch }) => {
    try {
      dispatch({ type: 'application/setLoading', payload: true });
      dispatch({ type: 'application/setError', payload: null });

      const response = await getApplicationsByBorrower({
        page,
        page_size: pageSize,
        filters,
        sort
      });

      if (response.success && response.data) {
        dispatch({ type: 'application/setApplications', payload: response.data.results });
        dispatch({ type: 'application/setTotalApplications', payload: response.data.total });
        dispatch({ type: 'application/setLoading', payload: false });
      } else {
        throw new Error(response.message || 'Failed to fetch borrower applications');
      }
    } catch (error) {
      handleApiError(error);
      dispatch({ type: 'application/setError', payload: error.message });
      dispatch({ type: 'application/setLoading', payload: false });
    }
  }
);

/**
 * Thunk to fetch a single application by ID with all related details
 */
export const fetchApplicationById = createAsyncThunk(
  'applications/fetchApplicationById',
  async (id: UUID, { dispatch }) => {
    try {
      dispatch({ type: 'application/setLoading', payload: true });
      dispatch({ type: 'application/setError', payload: null });

      const response = await getApplication(id);

      if (response.success && response.data) {
        dispatch({ type: 'application/setSelectedApplication', payload: response.data });
        dispatch({ type: 'application/setLoading', payload: false });
      } else {
        throw new Error(response.message || 'Failed to fetch application details');
      }
    } catch (error) {
      handleApiError(error);
      dispatch({ type: 'application/setError', payload: error.message });
      dispatch({ type: 'application/setLoading', payload: false });
    }
  }
);

/**
 * Thunk to create a new application
 */
export const createNewApplication = createAsyncThunk(
  'applications/createNewApplication',
  async (formData: ApplicationFormData, { dispatch }): Promise<UUID> => {
    try {
      dispatch({ type: 'application/setLoading', payload: true });
      dispatch({ type: 'application/setError', payload: null });

      const response = await createApplication(formData);

      if (response.success && response.data) {
        dispatch({ type: 'application/setSelectedApplication', payload: response.data });
        dispatch({ type: 'application/setLoading', payload: false });
        return response.data.id;
      } else {
        throw new Error(response.message || 'Failed to create application');
      }
    } catch (error) {
      handleApiError(error);
      dispatch({ type: 'application/setError', payload: error.message });
      dispatch({ type: 'application/setLoading', payload: false });
      throw error; // Re-throw for component to handle
    }
  }
);

/**
 * Thunk to update an existing application
 */
export const updateExistingApplication = createAsyncThunk(
  'applications/updateExistingApplication',
  async ({ id, formData }: { id: UUID; formData: ApplicationFormData }, { dispatch }) => {
    try {
      dispatch({ type: 'application/setLoading', payload: true });
      dispatch({ type: 'application/setError', payload: null });

      const response = await updateApplication(id, formData);

      if (response.success && response.data) {
        dispatch({ type: 'application/setSelectedApplication', payload: response.data });
        dispatch({ type: 'application/setLoading', payload: false });
      } else {
        throw new Error(response.message || 'Failed to update application');
      }
    } catch (error) {
      handleApiError(error);
      dispatch({ type: 'application/setError', payload: error.message });
      dispatch({ type: 'application/setLoading', payload: false });
    }
  }
);

/**
 * Thunk to submit an application for review, changing its status from draft to submitted
 */
export const submitExistingApplication = createAsyncThunk(
  'applications/submitExistingApplication',
  async (id: UUID, { dispatch }) => {
    try {
      dispatch({ type: 'application/setLoading', payload: true });
      dispatch({ type: 'application/setError', payload: null });

      const response = await submitApplication(id);

      if (response.success && response.data) {
        dispatch({ type: 'application/setSelectedApplication', payload: response.data });
        dispatch({ type: 'application/setLoading', payload: false });
      } else {
        throw new Error(response.message || 'Failed to submit application');
      }
    } catch (error) {
      handleApiError(error);
      dispatch({ type: 'application/setError', payload: error.message });
      dispatch({ type: 'application/setLoading', payload: false });
    }
  }
);

/**
 * Thunk to save a draft of an application without submitting it for review
 */
export const saveApplicationDraftThunk = createAsyncThunk(
  'applications/saveApplicationDraftThunk',
  async ({ id, formData }: { id: UUID; formData: ApplicationFormData }, { dispatch }) => {
    try {
      dispatch({ type: 'application/setLoading', payload: true });
      dispatch({ type: 'application/setError', payload: null });

      const response = await saveApplicationDraft(id, formData);

      if (response.success && response.data) {
        dispatch({ type: 'application/setSelectedApplication', payload: response.data });
        dispatch({ type: 'application/setLoading', payload: false });
      } else {
        throw new Error(response.message || 'Failed to save application draft');
      }
    } catch (error) {
      handleApiError(error);
      dispatch({ type: 'application/setError', payload: error.message });
      dispatch({ type: 'application/setLoading', payload: false });
    }
  }
);

/**
 * Thunk to cancel an application, changing its status to abandoned
 */
export const cancelExistingApplication = createAsyncThunk(
  'applications/cancelExistingApplication',
  async (id: UUID, { dispatch }) => {
    try {
      dispatch({ type: 'application/setLoading', payload: true });
      dispatch({ type: 'application/setError', payload: null });

      const response = await cancelApplication(id);

      if (response.success) {
        // Refresh applications list after cancellation
        dispatch(fetchApplications({}));
        dispatch({ type: 'application/setLoading', payload: false });
      } else {
        throw new Error(response.message || 'Failed to cancel application');
      }
    } catch (error) {
      handleApiError(error);
      dispatch({ type: 'application/setError', payload: error.message });
      dispatch({ type: 'application/setLoading', payload: false });
    }
  }
);

/**
 * Thunk to fetch all documents for an application
 */
export const fetchApplicationDocuments = createAsyncThunk(
  'applications/fetchApplicationDocuments',
  async (id: UUID, { dispatch, getState }): Promise<ApplicationDocument[]> => {
    try {
      dispatch({ type: 'application/setLoading', payload: true });
      dispatch({ type: 'application/setError', payload: null });

      const response = await getApplicationDocuments(id);

      if (response.success && response.data) {
        // Update selected application with the documents
        const state = getState() as any;
        const selectedApplication = state.application.selectedApplication;
        if (selectedApplication) {
          const updatedApplication = { ...selectedApplication, documents: response.data };
          dispatch({ type: 'application/setSelectedApplication', payload: updatedApplication });
        }
        dispatch({ type: 'application/setLoading', payload: false });
        return response.data;
      } else {
        throw new Error(response.message || 'Failed to fetch application documents');
      }
    } catch (error) {
      handleApiError(error);
      dispatch({ type: 'application/setError', payload: error.message });
      dispatch({ type: 'application/setLoading', payload: false });
      return [];
    }
  }
);

/**
 * Thunk to upload a document for an application
 */
export const uploadDocument = createAsyncThunk(
  'applications/uploadDocument',
  async ({ applicationId, documentType, file }: {
    applicationId: UUID;
    documentType: string;
    file: File;
  }, { dispatch }): Promise<ApplicationDocument> => {
    try {
      dispatch({ type: 'application/setLoading', payload: true });
      dispatch({ type: 'application/setError', payload: null });

      const response = await uploadApplicationDocument({
        application_id: applicationId,
        document_type: documentType,
        file
      });

      if (response.success && response.data) {
        // Refresh documents list
        dispatch(fetchApplicationDocuments(applicationId));
        dispatch({ type: 'application/setLoading', payload: false });
        return response.data;
      } else {
        throw new Error(response.message || 'Failed to upload document');
      }
    } catch (error) {
      handleApiError(error);
      dispatch({ type: 'application/setError', payload: error.message });
      dispatch({ type: 'application/setLoading', payload: false });
      throw error; // Re-throw for component to handle
    }
  }
);

/**
 * Thunk to delete a document from an application
 */
export const deleteDocument = createAsyncThunk(
  'applications/deleteDocument',
  async ({ applicationId, documentId }: { applicationId: UUID; documentId: UUID }, { dispatch }) => {
    try {
      dispatch({ type: 'application/setLoading', payload: true });
      dispatch({ type: 'application/setError', payload: null });

      const response = await deleteApplicationDocument(applicationId, documentId);

      if (response.success) {
        // Refresh documents list
        dispatch(fetchApplicationDocuments(applicationId));
        dispatch({ type: 'application/setLoading', payload: false });
      } else {
        throw new Error(response.message || 'Failed to delete document');
      }
    } catch (error) {
      handleApiError(error);
      dispatch({ type: 'application/setError', payload: error.message });
      dispatch({ type: 'application/setLoading', payload: false });
    }
  }
);

/**
 * Thunk to fetch the status history for an application
 */
export const fetchApplicationStatusHistory = createAsyncThunk(
  'applications/fetchApplicationStatusHistory',
  async (id: UUID, { dispatch, getState }): Promise<ApplicationStatusHistory[]> => {
    try {
      dispatch({ type: 'application/setLoading', payload: true });
      dispatch({ type: 'application/setError', payload: null });

      const response = await getApplicationStatusHistory(id);

      if (response.success && response.data) {
        // Update selected application with the status history
        const state = getState() as any;
        const selectedApplication = state.application.selectedApplication;
        if (selectedApplication) {
          const updatedApplication = { ...selectedApplication, status_history: response.data };
          dispatch({ type: 'application/setSelectedApplication', payload: updatedApplication });
        }
        dispatch({ type: 'application/setLoading', payload: false });
        return response.data;
      } else {
        throw new Error(response.message || 'Failed to fetch status history');
      }
    } catch (error) {
      handleApiError(error);
      dispatch({ type: 'application/setError', payload: error.message });
      dispatch({ type: 'application/setLoading', payload: false });
      return [];
    }
  }
);

/**
 * Thunk to fetch required actions for an application
 */
export const fetchApplicationRequiredActions = createAsyncThunk(
  'applications/fetchApplicationRequiredActions',
  async (id: UUID, { dispatch }): Promise<ApplicationRequiredAction[]> => {
    try {
      dispatch({ type: 'application/setLoading', payload: true });
      dispatch({ type: 'application/setError', payload: null });

      const response = await getApplicationRequiredActions(id);

      if (response.success && response.data) {
        // Update store with required actions
        dispatch({ type: 'application/setRequiredActions', payload: response.data });
        dispatch({ type: 'application/setLoading', payload: false });
        return response.data;
      } else {
        throw new Error(response.message || 'Failed to fetch required actions');
      }
    } catch (error) {
      handleApiError(error);
      dispatch({ type: 'application/setError', payload: error.message });
      dispatch({ type: 'application/setLoading', payload: false });
      return [];
    }
  }
);

/**
 * Thunk to fetch timeline events for an application
 */
export const fetchApplicationTimeline = createAsyncThunk(
  'applications/fetchApplicationTimeline',
  async (id: UUID, { dispatch }): Promise<ApplicationTimelineEvent[]> => {
    try {
      dispatch({ type: 'application/setLoading', payload: true });
      dispatch({ type: 'application/setError', payload: null });

      const response = await getApplicationTimeline(id);

      if (response.success && response.data) {
        // Update store with timeline events
        dispatch({ type: 'application/setTimelineEvents', payload: response.data });
        dispatch({ type: 'application/setLoading', payload: false });
        return response.data;
      } else {
        throw new Error(response.message || 'Failed to fetch timeline events');
      }
    } catch (error) {
      handleApiError(error);
      dispatch({ type: 'application/setError', payload: error.message });
      dispatch({ type: 'application/setLoading', payload: false });
      return [];
    }
  }
);

/**
 * Thunk to fetch counts of applications grouped by status
 */
export const fetchApplicationCountsByStatus = createAsyncThunk(
  'applications/fetchApplicationCountsByStatus',
  async ({ schoolId }: { schoolId?: UUID } = {}, { dispatch }): Promise<ApplicationCountsByStatus | null> => {
    try {
      dispatch({ type: 'application/setLoading', payload: true });
      dispatch({ type: 'application/setError', payload: null });

      const response = await getApplicationCountsByStatus({ schoolId });

      if (response.success && response.data) {
        // Update store with counts data
        dispatch({ type: 'application/setCountsByStatus', payload: response.data });
        dispatch({ type: 'application/setLoading', payload: false });
        return response.data;
      } else {
        throw new Error(response.message || 'Failed to fetch application counts');
      }
    } catch (error) {
      handleApiError(error);
      dispatch({ type: 'application/setError', payload: error.message });
      dispatch({ type: 'application/setLoading', payload: false });
      return null;
    }
  }
);

/**
 * Thunk to update the status of an application
 */
export const updateApplicationStatus = createAsyncThunk(
  'applications/updateApplicationStatus',
  async ({ applicationId, status, comments }: {
    applicationId: UUID;
    status: string;
    comments?: string;
  }, { dispatch }) => {
    try {
      dispatch({ type: 'application/setLoading', payload: true });
      dispatch({ type: 'application/setError', payload: null });

      const response = await updateApplicationStatus({
        application_id: applicationId,
        status,
        comments
      });

      if (response.success) {
        // Refresh application details
        dispatch(fetchApplicationById(applicationId));
        dispatch({ type: 'application/setLoading', payload: false });
      } else {
        throw new Error(response.message || 'Failed to update application status');
      }
    } catch (error) {
      handleApiError(error);
      dispatch({ type: 'application/setError', payload: error.message });
      dispatch({ type: 'application/setLoading', payload: false });
    }
  }
);