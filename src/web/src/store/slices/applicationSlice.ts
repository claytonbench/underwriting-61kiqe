import { createSlice, PayloadAction } from '@reduxjs/toolkit'; // ^1.9.5
// Import application-related type definitions
import {
  ApplicationState, ApplicationFilters, ApplicationSort, ApplicationSortField, ApplicationDetail, ApplicationFormData, ApplicationListItem, ApplicationRequiredAction, ApplicationTimelineEvent, ApplicationCountsByStatus
} from '../../types/application.types';
// Import common type definitions
import { SortDirection } from '../../types/common.types';
// Import application-related async thunks
import {
  fetchApplications, fetchApplicationsBySchool, fetchApplicationsByBorrower, fetchApplicationById, createNewApplication, updateExistingApplication, submitExistingApplication, saveApplicationDraftThunk, cancelExistingApplication, fetchApplicationDocuments, uploadDocument, deleteDocument, fetchApplicationStatusHistory
} from '../thunks/applicationThunks';
// Import root state type
import { RootState } from '../rootReducer';

/**
 * Initial state for the application slice
 */
const initialState: ApplicationState = {
  applications: [],
  selectedApplication: null,
  loading: false,
  error: null,
  totalApplications: 0,
  filters: {
    status: null,
    school_id: null,
    program_id: null,
    borrower_name: null,
    date_range: { start: null, end: null },
    has_co_borrower: null
  },
  sort: null,
  page: 1,
  pageSize: 10,
  countsByStatus: null,
  currentFormData: null,
  formStep: 1,
  requiredActions: [],
  timelineEvents: []
};

/**
 * Redux slice for application state management
 */
export const applicationSlice = createSlice({
  name: 'application',
  initialState,
  reducers: {
    /**
     * Sets the applications list
     * @param {ApplicationState} state - The current state
     * @param {PayloadAction<ApplicationListItem[]>} action - The action containing the applications list
     */
    setApplications: (state: ApplicationState, action: PayloadAction<ApplicationListItem[]>) => {
      state.applications = action.payload;
    },
    /**
     * Sets the selected application details
     * @param {ApplicationState} state - The current state
     * @param {PayloadAction<ApplicationDetail | null>} action - The action containing the selected application details
     */
    setSelectedApplication: (state: ApplicationState, action: PayloadAction<ApplicationDetail | null>) => {
      state.selectedApplication = action.payload;
    },
    /**
     * Sets the loading state
     * @param {ApplicationState} state - The current state
     * @param {PayloadAction<boolean>} action - The action containing the loading state
     */
    setLoading: (state: ApplicationState, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    /**
     * Sets the error state
     * @param {ApplicationState} state - The current state
     * @param {PayloadAction<string | null>} action - The action containing the error message
     */
    setError: (state: ApplicationState, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    /**
     * Sets the total applications count
     * @param {ApplicationState} state - The current state
     * @param {PayloadAction<number>} action - The action containing the total applications count
     */
    setTotalApplications: (state: ApplicationState, action: PayloadAction<number>) => {
      state.totalApplications = action.payload;
    },
    /**
     * Sets the filter options
     * @param {ApplicationState} state - The current state
     * @param {PayloadAction<ApplicationFilters>} action - The action containing the filter options
     */
    setFilters: (state: ApplicationState, action: PayloadAction<ApplicationFilters>) => {
      state.filters = action.payload;
    },
    /**
     * Sets the sort options
     * @param {ApplicationState} state - The current state
     * @param {PayloadAction<ApplicationSort | null>} action - The action containing the sort options
     */
    setSort: (state: ApplicationState, action: PayloadAction<ApplicationSort | null>) => {
      state.sort = action.payload;
    },
    /**
     * Sets the current page number
     * @param {ApplicationState} state - The current state
     * @param {PayloadAction<number>} action - The action containing the page number
     */
    setPage: (state: ApplicationState, action: PayloadAction<number>) => {
      state.page = action.payload;
    },
    /**
     * Sets the page size
     * @param {ApplicationState} state - The current state
     * @param {PayloadAction<number>} action - The action containing the page size
     */
    setPageSize: (state: ApplicationState, action: PayloadAction<number>) => {
      state.pageSize = action.payload;
    },
    /**
     * Sets the counts by status
     * @param {ApplicationState} state - The current state
     * @param {PayloadAction<ApplicationCountsByStatus | null>} action - The action containing the counts by status
     */
    setCountsByStatus: (state: ApplicationState, action: PayloadAction<ApplicationCountsByStatus | null>) => {
      state.countsByStatus = action.payload;
    },
    /**
     * Sets the current form data
     * @param {ApplicationState} state - The current state
     * @param {PayloadAction<ApplicationFormData | null>} action - The action containing the form data
     */
    setCurrentFormData: (state: ApplicationState, action: PayloadAction<ApplicationFormData | null>) => {
      state.currentFormData = action.payload;
    },
    /**
     * Updates part of the current form data
     * @param {ApplicationState} state - The current state
     * @param {PayloadAction<Partial<ApplicationFormData>>} action - The action containing the partial form data
     */
    updateCurrentFormData: (state: ApplicationState, action: PayloadAction<Partial<ApplicationFormData>>) => {
      state.currentFormData = state.currentFormData ? { ...state.currentFormData, ...action.payload } : null;
    },
    /**
     * Sets the current form step
     * @param {ApplicationState} state - The current state
     * @param {PayloadAction<number>} action - The action containing the form step
     */
    setFormStep: (state: ApplicationState, action: PayloadAction<number>) => {
      state.formStep = action.payload;
    },
    /**
     * Increments the form step
     * @param {ApplicationState} state - The current state
     */
    incrementFormStep: (state: ApplicationState) => {
      state.formStep += 1;
    },
    /**
     * Decrements the form step
     * @param {ApplicationState} state - The current state
     */
    decrementFormStep: (state: ApplicationState) => {
      state.formStep -= 1;
    },
    /**
     * Resets the form step to 1
     * @param {ApplicationState} state - The current state
     */
    resetFormStep: (state: ApplicationState) => {
      state.formStep = 1;
    },
    /**
     * Resets the application state to initial values
     * @param {ApplicationState} state - The current state
     */
    resetApplicationState: (state: ApplicationState) => {
      state.applications = [];
      state.selectedApplication = null;
      state.loading = false;
      state.error = null;
      state.totalApplications = 0;
      state.filters = {
        status: null,
        school_id: null,
        program_id: null,
        borrower_name: null,
        date_range: { start: null, end: null },
        has_co_borrower: null
      };
      state.sort = null;
      state.page = 1;
      state.pageSize = 10;
      state.countsByStatus = null;
      state.currentFormData = null;
      state.formStep = 1;
      state.requiredActions = [];
      state.timelineEvents = [];
    },
    /**
     * Sets the required actions for the selected application
     * @param {ApplicationState} state - The current state
     * @param {PayloadAction<ApplicationRequiredAction[]>} action - The action containing the required actions
     */
    setRequiredActions: (state: ApplicationState, action: PayloadAction<ApplicationRequiredAction[]>) => {
      state.requiredActions = action.payload;
    },
    /**
     * Sets the timeline events for the selected application
     * @param {ApplicationState} state - The current state
     * @param {PayloadAction<ApplicationTimelineEvent[]>} action - The action containing the timeline events
     */
    setTimelineEvents: (state: ApplicationState, action: PayloadAction<ApplicationTimelineEvent[]>) => {
      state.timelineEvents = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      // Handle fetchApplications async thunk results
      .addCase(fetchApplications.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchApplications.fulfilled, (state, action) => {
        state.applications = action.payload.results;
        state.totalApplications = action.payload.total;
        state.loading = false;
      })
      .addCase(fetchApplications.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch applications';
      })
      // Handle fetchApplicationsBySchool async thunk results
      .addCase(fetchApplicationsBySchool.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchApplicationsBySchool.fulfilled, (state, action) => {
        state.applications = action.payload.results;
        state.totalApplications = action.payload.total;
        state.loading = false;
      })
      .addCase(fetchApplicationsBySchool.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch applications by school';
      })
      // Handle fetchApplicationsByBorrower async thunk results
      .addCase(fetchApplicationsByBorrower.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchApplicationsByBorrower.fulfilled, (state, action) => {
        state.applications = action.payload.results;
        state.totalApplications = action.payload.total;
        state.loading = false;
      })
      .addCase(fetchApplicationsByBorrower.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch borrower applications';
      })
      // Handle fetchApplicationById async thunk results
      .addCase(fetchApplicationById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchApplicationById.fulfilled, (state, action) => {
        state.selectedApplication = action.payload;
        state.loading = false;
      })
      .addCase(fetchApplicationById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch application details';
      })
      // Handle createNewApplication async thunk results
      .addCase(createNewApplication.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createNewApplication.fulfilled, (state, action) => {
        state.selectedApplication = action.payload;
        state.loading = false;
      })
      .addCase(createNewApplication.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to create application';
      })
      // Handle updateExistingApplication async thunk results
      .addCase(updateExistingApplication.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateExistingApplication.fulfilled, (state, action) => {
        state.selectedApplication = action.payload;
        state.loading = false;
      })
      .addCase(updateExistingApplication.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to update application';
      })
      // Handle submitExistingApplication async thunk results
      .addCase(submitExistingApplication.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(submitExistingApplication.fulfilled, (state, action) => {
        state.selectedApplication = action.payload;
        state.loading = false;
      })
      .addCase(submitExistingApplication.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to submit application';
      })
      // Handle saveApplicationDraftThunk async thunk results
      .addCase(saveApplicationDraftThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(saveApplicationDraftThunk.fulfilled, (state, action) => {
        state.selectedApplication = action.payload;
        state.loading = false;
      })
      .addCase(saveApplicationDraftThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to save application draft';
      })
      // Handle cancelExistingApplication async thunk results
      .addCase(cancelExistingApplication.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(cancelExistingApplication.fulfilled, (state, action) => {
        state.applications = state.applications.filter(app => app.id !== action.payload);
        state.selectedApplication = null;
        state.loading = false;
      })
      .addCase(cancelExistingApplication.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to cancel application';
      })
      // Handle fetchApplicationDocuments async thunk results
      .addCase(fetchApplicationDocuments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchApplicationDocuments.fulfilled, (state, action) => {
        if (state.selectedApplication) {
          state.selectedApplication.documents = action.payload;
        }
        state.loading = false;
      })
      .addCase(fetchApplicationDocuments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch application documents';
      })
      // Handle uploadDocument async thunk results
      .addCase(uploadDocument.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(uploadDocument.fulfilled, (state, action) => {
        if (state.selectedApplication && state.selectedApplication.documents) {
          state.selectedApplication.documents = [...state.selectedApplication.documents, action.payload];
        }
        state.loading = false;
      })
      .addCase(uploadDocument.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to upload document';
      })
      // Handle deleteDocument async thunk results
      .addCase(deleteDocument.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteDocument.fulfilled, (state, action) => {
        if (state.selectedApplication && state.selectedApplication.documents) {
          state.selectedApplication.documents = state.selectedApplication.documents.filter(doc => doc.id !== action.meta.arg.documentId);
        }
        state.loading = false;
      })
      .addCase(deleteDocument.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to delete document';
      })
      // Handle fetchApplicationStatusHistory async thunk results
      .addCase(fetchApplicationStatusHistory.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchApplicationStatusHistory.fulfilled, (state, action) => {
        if (state.selectedApplication) {
          state.selectedApplication.status_history = action.payload;
        }
        state.loading = false;
      })
      .addCase(fetchApplicationStatusHistory.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch status history';
      });
  },
});

// Action creators are generated for each case reducer function
export const {
  setApplications,
  setSelectedApplication,
  setLoading,
  setError,
  setTotalApplications,
  setFilters,
  setSort,
  setPage,
  setPageSize,
  setCountsByStatus,
  setCurrentFormData,
  updateCurrentFormData,
  setFormStep,
  incrementFormStep,
  decrementFormStep,
  resetFormStep,
  resetApplicationState,
  setRequiredActions,
  setTimelineEvents
} = applicationSlice.actions;

/**
 * Selects the application state from the root state
 * @param {RootState} state - The root state
 * @returns {ApplicationState} The application state slice
 */
export const selectApplicationState = (state: RootState) => state.application;

/**
 * Selects the applications list from state
 * @param {RootState} state - The root state
 * @returns {ApplicationListItem[]} The applications list
 */
export const selectApplications = (state: RootState) => state.application.applications;

/**
 * Selects the selected application from state
 * @param {RootState} state - The root state
 * @returns {ApplicationDetail | null} The selected application details
 */
export const selectSelectedApplication = (state: RootState) => state.application.selectedApplication;

/**
 * Selects the loading state
 * @param {RootState} state - The root state
 * @returns {boolean} The loading state
 */
export const selectLoading = (state: RootState) => state.application.loading;

/**
 * Selects the error state
 * @param {RootState} state - The root state
 * @returns {string | null} The error message
 */
export const selectError = (state: RootState) => state.application.error;

/**
 * Selects the total applications count
 * @param {RootState} state - The root state
 * @returns {number} The total applications count
 */
export const selectTotalApplications = (state: RootState) => state.application.totalApplications;

/**
 * Selects the current filters
 * @param {RootState} state - The root state
 * @returns {ApplicationFilters} The current filters
 */
export const selectFilters = (state: RootState) => state.application.filters;

/**
 * Selects the current sort options
 * @param {RootState} state - The root state
 * @returns {ApplicationSort | null} The current sort options
 */
export const selectSort = (state: RootState) => state.application.sort;

/**
 * Selects the current page number
 * @param {RootState} state - The root state
 * @returns {number} The current page number
 */
export const selectPage = (state: RootState) => state.application.page;

/**
 * Selects the current page size
 * @param {RootState} state - The root state
 * @returns {number} The current page size
 */
export const selectPageSize = (state: RootState) => state.application.pageSize;

/**
 * Selects the counts by status
 * @param {RootState} state - The root state
 * @returns {ApplicationCountsByStatus | null} The counts by status
 */
export const selectCountsByStatus = (state: RootState) => state.application.countsByStatus;

/**
 * Selects the current form data
 * @param {RootState} state - The root state
 * @returns {ApplicationFormData | null} The current form data
 */
export const selectCurrentFormData = (state: RootState) => state.application.currentFormData;

/**
 * Selects the current form step
 * @param {RootState} state - The root state
 * @returns {number} The current form step
 */
export const selectFormStep = (state: RootState) => state.application.formStep;

/**
 * Selects the required actions
 * @param {RootState} state - The root state
 * @returns {ApplicationRequiredAction[]} The required actions
 */
export const selectRequiredActions = (state: RootState) => state.application.requiredActions;

/**
 * Selects the timeline events
 * @param {RootState} state - The root state
 * @returns {ApplicationTimelineEvent[]} The timeline events
 */
export const selectTimelineEvents = (state: RootState) => state.application.timelineEvents;

// Export the reducer
export default applicationSlice.reducer;