import { AnyAction } from 'redux'; // ^4.2.1
import { ApplicationState } from '../../types/application.types';
import {
  fetchApplications,
  fetchApplicationDetail,
  createNewApplication,
  updateExistingApplication,
  submitExistingApplication,
  saveApplicationDraftAction,
  cancelExistingApplication,
  fetchApplicationDocuments,
  uploadDocument,
  deleteDocument,
  fetchStatusHistory,
  fetchSchoolApplications,
  fetchBorrowerApplications,
  setApplicationFormData,
  resetApplicationForm,
  resetCurrentApplication
} from '../actions/applicationActions';

/**
 * Initial state for the application reducer
 */
const initialState: ApplicationState = {
  applications: [],
  selectedApplication: null,
  loading: false,
  error: null,
  totalApplications: 0,
  filters: {},
  sort: null,
  page: 1,
  pageSize: 10,
  countsByStatus: null,
  currentFormData: null,
  formStep: 1,
  requiredActions: [],
  timelineEvents: [],
  documents: [],
  statusHistory: []
};

/**
 * Redux reducer for managing application state changes
 * Handles actions related to loan applications including fetching, creating,
 * updating, and processing applications throughout their lifecycle
 * 
 * @param state - Current application state
 * @param action - Action to be processed
 * @returns Updated application state
 */
const applicationReducer = (
  state: ApplicationState = initialState,
  action: AnyAction
): ApplicationState => {
  switch (action.type) {
    // Fetch applications
    case fetchApplications.pending.type:
      return {
        ...state,
        loading: true,
        error: null
      };
    case fetchApplications.fulfilled.type:
      return {
        ...state,
        loading: false,
        applications: action.payload.results,
        totalApplications: action.payload.total,
        page: action.payload.page,
        error: null
      };
    case fetchApplications.rejected.type:
      return {
        ...state,
        loading: false,
        error: action.error.message || 'Failed to fetch applications'
      };

    // Fetch application detail
    case fetchApplicationDetail.pending.type:
      return {
        ...state,
        loading: true,
        error: null
      };
    case fetchApplicationDetail.fulfilled.type:
      return {
        ...state,
        loading: false,
        selectedApplication: action.payload,
        error: null
      };
    case fetchApplicationDetail.rejected.type:
      return {
        ...state,
        loading: false,
        error: action.error.message || 'Failed to fetch application details'
      };

    // Create new application
    case createNewApplication.pending.type:
      return {
        ...state,
        loading: true,
        error: null
      };
    case createNewApplication.fulfilled.type:
      return {
        ...state,
        loading: false,
        applications: [action.payload, ...state.applications],
        error: null
      };
    case createNewApplication.rejected.type:
      return {
        ...state,
        loading: false,
        error: action.error.message || 'Failed to create application'
      };

    // Update existing application
    case updateExistingApplication.pending.type:
      return {
        ...state,
        loading: true,
        error: null
      };
    case updateExistingApplication.fulfilled.type:
      return {
        ...state,
        loading: false,
        applications: state.applications.map(app => 
          app.id === action.payload.id ? { ...app, ...action.payload } : app
        ),
        selectedApplication: state.selectedApplication?.application.id === action.payload.id 
          ? { ...state.selectedApplication, application: { ...state.selectedApplication.application, ...action.payload } }
          : state.selectedApplication,
        error: null
      };
    case updateExistingApplication.rejected.type:
      return {
        ...state,
        loading: false,
        error: action.error.message || 'Failed to update application'
      };

    // Submit existing application
    case submitExistingApplication.pending.type:
      return {
        ...state,
        loading: true,
        error: null
      };
    case submitExistingApplication.fulfilled.type:
      return {
        ...state,
        loading: false,
        applications: state.applications.map(app => 
          app.id === action.payload.id ? { ...app, status: action.payload.status } : app
        ),
        selectedApplication: state.selectedApplication?.application.id === action.payload.id 
          ? { ...state.selectedApplication, application: { ...state.selectedApplication.application, ...action.payload } }
          : state.selectedApplication,
        error: null
      };
    case submitExistingApplication.rejected.type:
      return {
        ...state,
        loading: false,
        error: action.error.message || 'Failed to submit application'
      };

    // Save application draft
    case saveApplicationDraftAction.pending.type:
      return {
        ...state,
        loading: true,
        error: null
      };
    case saveApplicationDraftAction.fulfilled.type:
      return {
        ...state,
        loading: false,
        applications: state.applications.map(app => 
          app.id === action.payload.id ? { ...app, ...action.payload } : app
        ),
        selectedApplication: state.selectedApplication?.application.id === action.payload.id 
          ? { ...state.selectedApplication, application: { ...state.selectedApplication.application, ...action.payload } }
          : state.selectedApplication,
        error: null
      };
    case saveApplicationDraftAction.rejected.type:
      return {
        ...state,
        loading: false,
        error: action.error.message || 'Failed to save application draft'
      };

    // Cancel existing application
    case cancelExistingApplication.pending.type:
      return {
        ...state,
        loading: true,
        error: null
      };
    case cancelExistingApplication.fulfilled.type:
      return {
        ...state,
        loading: false,
        applications: state.applications.filter(app => app.id !== action.payload),
        selectedApplication: state.selectedApplication?.application.id === action.payload
          ? null
          : state.selectedApplication,
        error: null
      };
    case cancelExistingApplication.rejected.type:
      return {
        ...state,
        loading: false,
        error: action.error.message || 'Failed to cancel application'
      };

    // Fetch application documents
    case fetchApplicationDocuments.pending.type:
      return {
        ...state,
        loading: true,
        error: null
      };
    case fetchApplicationDocuments.fulfilled.type:
      return {
        ...state,
        loading: false,
        documents: action.payload,
        error: null
      };
    case fetchApplicationDocuments.rejected.type:
      return {
        ...state,
        loading: false,
        error: action.error.message || 'Failed to fetch application documents'
      };

    // Upload document
    case uploadDocument.pending.type:
      return {
        ...state,
        loading: true,
        error: null
      };
    case uploadDocument.fulfilled.type:
      return {
        ...state,
        loading: false,
        documents: [...state.documents, action.payload],
        error: null
      };
    case uploadDocument.rejected.type:
      return {
        ...state,
        loading: false,
        error: action.error.message || 'Failed to upload document'
      };

    // Delete document
    case deleteDocument.pending.type:
      return {
        ...state,
        loading: true,
        error: null
      };
    case deleteDocument.fulfilled.type:
      return {
        ...state,
        loading: false,
        documents: state.documents.filter(
          doc => doc.id !== action.payload.documentId
        ),
        error: null
      };
    case deleteDocument.rejected.type:
      return {
        ...state,
        loading: false,
        error: action.error.message || 'Failed to delete document'
      };

    // Fetch status history
    case fetchStatusHistory.pending.type:
      return {
        ...state,
        loading: true,
        error: null
      };
    case fetchStatusHistory.fulfilled.type:
      return {
        ...state,
        loading: false,
        statusHistory: action.payload,
        error: null
      };
    case fetchStatusHistory.rejected.type:
      return {
        ...state,
        loading: false,
        error: action.error.message || 'Failed to fetch status history'
      };

    // Fetch school applications
    case fetchSchoolApplications.pending.type:
      return {
        ...state,
        loading: true,
        error: null
      };
    case fetchSchoolApplications.fulfilled.type:
      return {
        ...state,
        loading: false,
        applications: action.payload.results,
        totalApplications: action.payload.total,
        page: action.payload.page,
        error: null
      };
    case fetchSchoolApplications.rejected.type:
      return {
        ...state,
        loading: false,
        error: action.error.message || 'Failed to fetch school applications'
      };

    // Fetch borrower applications
    case fetchBorrowerApplications.pending.type:
      return {
        ...state,
        loading: true,
        error: null
      };
    case fetchBorrowerApplications.fulfilled.type:
      return {
        ...state,
        loading: false,
        applications: action.payload.results,
        totalApplications: action.payload.total,
        page: action.payload.page,
        error: null
      };
    case fetchBorrowerApplications.rejected.type:
      return {
        ...state,
        loading: false,
        error: action.error.message || 'Failed to fetch borrower applications'
      };

    // Set application form data
    case 'applications/setApplicationFormData':
      return {
        ...state,
        currentFormData: action.payload
      };

    // Reset application form
    case 'applications/resetApplicationForm':
      return {
        ...state,
        currentFormData: null,
        formStep: 1
      };

    // Reset current application
    case 'applications/resetCurrentApplication':
      return {
        ...state,
        selectedApplication: null
      };

    default:
      return state;
  }
};

export default applicationReducer;