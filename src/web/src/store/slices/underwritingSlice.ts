import { createSlice, PayloadAction } from '@reduxjs/toolkit'; // @reduxjs/toolkit ^1.9.5
import {
  UnderwritingState,
  UnderwritingQueueFilters,
  UnderwritingQueueSort,
  UnderwritingQueueSortField,
  SortDirection,
  UnderwritingDecisionRequest,
  UnderwritingApplicationDetail,
  UnderwritingQueueItem
} from '../../types/underwriting.types';
import {
  fetchUnderwritingQueue,
  fetchAssignedApplications,
  assignApplicationToUnderwriter,
  unassignApplicationFromUnderwriter,
  startReviewingApplication,
  fetchCreditInformation,
  uploadCreditReportFile,
  submitDecision,
  fetchDecision,
  saveDraftDecision,
  fetchStipulations,
  addNote,
  fetchNotes,
  fetchMetrics,
  updateApplicationPriority,
  requestApplicationRevision
} from '../thunks/underwritingThunks';

/**
 * Initial state for the underwriting slice
 */
const initialState: UnderwritingState = {
  queueItems: [], // Array of applications in the underwriting queue
  selectedApplication: null, // Currently selected application for detailed review
  loading: false, // Loading state indicator
  error: null, // Error message if any operation fails
  totalItems: 0, // Total count of items in the queue
  filters: { // Filter criteria for the underwriting queue
    status: null,
    priority: null,
    assigned_to: null,
    borrower_name: null,
    school_id: null,
    is_overdue: null,
    date_range: {
      start: null,
      end: null
    }
  },
  sort: { // Sort criteria for the underwriting queue
    field: UnderwritingQueueSortField.SUBMISSION_DATE,
    direction: SortDirection.DESC
  },
  page: 1, // Current page number for pagination
  pageSize: 10, // Number of items per page
  metrics: null, // Performance metrics for underwriting
  decisionDraft: null, // Draft of an underwriting decision being prepared
};

/**
 * Redux Toolkit slice for underwriting state management
 */
export const underwritingSlice = createSlice({
  name: 'underwriting',
  initialState,
  reducers: {
    /**
     * Sets the currently selected application for detailed review
     * @param state - The current state
     * @param action - Payload containing the selected application
     */
    setSelectedApplication: (state: UnderwritingState, action: PayloadAction<UnderwritingApplicationDetail>) => {
      state.selectedApplication = action.payload;
    },
    /**
     * Clears the currently selected application
     * @param state - The current state
     */
    clearSelectedApplication: (state: UnderwritingState) => {
      state.selectedApplication = null;
    },
    /**
     * Updates the filter criteria for the underwriting queue
     * @param state - The current state
     * @param action - Payload containing the filter criteria to update
     */
    setFilters: (state: UnderwritingState, action: PayloadAction<Partial<UnderwritingQueueFilters>>) => {
      state.filters = { ...state.filters, ...action.payload };
      state.page = 1; // Reset page to 1 when filters change
    },
    /**
     * Resets all filters to their default values
     * @param state - The current state
     */
    resetFilters: (state: UnderwritingState) => {
      state.filters = {
        status: null,
        priority: null,
        assigned_to: null,
        borrower_name: null,
        school_id: null,
        is_overdue: null,
        date_range: {
          start: null,
          end: null
        }
      };
      state.page = 1; // Reset page to 1
    },
    /**
     * Sets the sort criteria for the underwriting queue
     * @param state - The current state
     * @param action - Payload containing the sort criteria
     */
    setSort: (state: UnderwritingState, action: PayloadAction<UnderwritingQueueSort>) => {
      state.sort = action.payload;
    },
    /**
     * Sets the current page number for pagination
     * @param state - The current state
     * @param action - Payload containing the page number
     */
    setPage: (state: UnderwritingState, action: PayloadAction<number>) => {
      state.page = action.payload;
    },
    /**
     * Sets the number of items per page
     * @param state - The current state
     * @param action - Payload containing the page size
     */
    setPageSize: (state: UnderwritingState, action: PayloadAction<number>) => {
      state.pageSize = action.payload;
      state.page = 1; // Reset page to 1 when page size changes
    },
    /**
     * Updates the draft of an underwriting decision
     * @param state - The current state
     * @param action - Payload containing the partial underwriting decision request
     */
    updateDecisionDraft: (state: UnderwritingState, action: PayloadAction<Partial<UnderwritingDecisionRequest>>) => {
      state.decisionDraft = { ...state.decisionDraft, ...action.payload };
    },
    /**
     * Clears the draft of an underwriting decision
     * @param state - The current state
     */
    clearDecisionDraft: (state: UnderwritingState) => {
      state.decisionDraft = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Handle fetchUnderwritingQueue async thunk
      .addCase(fetchUnderwritingQueue.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUnderwritingQueue.fulfilled, (state, action) => {
        state.loading = false;
        state.queueItems = action.payload.results;
        state.totalItems = action.payload.total;
      })
      .addCase(fetchUnderwritingQueue.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch underwriting queue';
      })
      // Handle fetchAssignedApplications async thunk
      .addCase(fetchAssignedApplications.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAssignedApplications.fulfilled, (state, action) => {
        state.loading = false;
        state.queueItems = action.payload.results;
        state.totalItems = action.payload.total;
      })
      .addCase(fetchAssignedApplications.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch assigned applications';
      })
      // Handle assignApplicationToUnderwriter async thunk
      .addCase(assignApplicationToUnderwriter.fulfilled, (state, action) => {
        const updatedItem = action.payload;
        const index = state.queueItems.findIndex(item => item.application_id === updatedItem.application_id);
        if (index !== -1) {
          state.queueItems[index] = {
            ...state.queueItems[index],
            assigned_to: updatedItem.assigned_to,
            status: updatedItem.status
          };
        }
        if (state.selectedApplication && state.selectedApplication.application.id === updatedItem.application_id) {
          state.selectedApplication = {
            ...state.selectedApplication,
            queue_item: updatedItem
          };
        }
      })
      // Handle unassignApplicationFromUnderwriter async thunk
      .addCase(unassignApplicationFromUnderwriter.fulfilled, (state, action) => {
        const updatedItem = action.payload;
        const index = state.queueItems.findIndex(item => item.application_id === updatedItem.application_id);
        if (index !== -1) {
          state.queueItems[index] = {
            ...state.queueItems[index],
            assigned_to: updatedItem.assigned_to,
            status: updatedItem.status
          };
        }
          if (state.selectedApplication && state.selectedApplication.application.id === updatedItem.application_id) {
            state.selectedApplication = {
              ...state.selectedApplication,
              queue_item: updatedItem
            };
          }
      })
      // Handle startReviewingApplication async thunk
      .addCase(startReviewingApplication.fulfilled, (state, action) => {
        const updatedItem = action.payload;
        const index = state.queueItems.findIndex(item => item.application_id === updatedItem.application_id);
        if (index !== -1) {
          state.queueItems[index] = {
            ...state.queueItems[index],
            status: updatedItem.status
          };
        }
          if (state.selectedApplication && state.selectedApplication.application.id === updatedItem.application_id) {
            state.selectedApplication = {
              ...state.selectedApplication,
              queue_item: updatedItem
            };
          }
      })
      // Handle fetchCreditInformation async thunk
      .addCase(fetchCreditInformation.fulfilled, (state, action) => {
        if (state.selectedApplication) {
          if (action.payload.is_co_borrower) {
            state.selectedApplication = {
              ...state.selectedApplication,
              co_borrower_credit: action.payload
            };
          } else {
            state.selectedApplication = {
              ...state.selectedApplication,
              borrower_credit: action.payload
            };
          }
        }
      })
      // Handle uploadCreditReportFile async thunk
      .addCase(uploadCreditReportFile.fulfilled, (state, action) => {
         if (state.selectedApplication) {
          if (action.payload.is_co_borrower) {
            state.selectedApplication = {
              ...state.selectedApplication,
              co_borrower_credit: action.payload
            };
          } else {
            state.selectedApplication = {
              ...state.selectedApplication,
              borrower_credit: action.payload
            };
          }
        }
      })
      // Handle submitDecision async thunk
      .addCase(submitDecision.fulfilled, (state, action) => {
        if (state.selectedApplication) {
          state.selectedApplication = {
            ...state.selectedApplication,
            decision: action.payload
          };
        }
        state.decisionDraft = null;
      })
      // Handle fetchDecision async thunk
      .addCase(fetchDecision.fulfilled, (state, action) => {
        if (state.selectedApplication) {
          state.selectedApplication = {
            ...state.selectedApplication,
            decision: action.payload
          };
        }
      })
      // Handle saveDraftDecision async thunk
      .addCase(saveDraftDecision.fulfilled, (state, action) => {
        state.decisionDraft = action.payload;
      })
      // Handle fetchStipulations async thunk
      .addCase(fetchStipulations.fulfilled, (state, action) => {
        if (state.selectedApplication) {
          state.selectedApplication = {
            ...state.selectedApplication,
            stipulations: action.payload
          };
        }
      })
      // Handle addNote async thunk
      .addCase(addNote.fulfilled, (state, action) => {
        if (state.selectedApplication && state.selectedApplication.notes) {
          state.selectedApplication = {
            ...state.selectedApplication,
            notes: [action.payload, ...state.selectedApplication.notes]
          };
        }
      })
      // Handle fetchNotes async thunk
      .addCase(fetchNotes.fulfilled, (state, action) => {
        if (state.selectedApplication) {
          state.selectedApplication = {
            ...state.selectedApplication,
            notes: action.payload
          };
        }
      })
       // Handle fetchMetrics async thunk
      .addCase(fetchMetrics.fulfilled, (state, action) => {
        state.metrics = action.payload;
      })
      // Handle updateApplicationPriority async thunk
      .addCase(updateApplicationPriority.fulfilled, (state, action) => {
        const updatedQueue = action.payload;
        const index = state.queueItems.findIndex(item => item.application_id === updatedQueue.application_id);
        if (index !== -1) {
          state.queueItems[index] = {
            ...state.queueItems[index],
            priority: updatedQueue.priority
          };
        }
          if (state.selectedApplication && state.selectedApplication.application.id === updatedQueue.application_id) {
            state.selectedApplication = {
              ...state.selectedApplication,
              queue_item: updatedQueue
            };
          }
      })
      // Handle requestApplicationRevision async thunk
      .addCase(requestApplicationRevision.fulfilled, (state, action) => {
        const updatedApplication = action.payload;
        const index = state.queueItems.findIndex(item => item.application_id === updatedApplication.application_id);
        if (index !== -1) {
          state.queueItems[index] = {
            ...state.queueItems[index],
            status: updatedApplication.status
          };
        }
          if (state.selectedApplication && state.selectedApplication.application.id === updatedApplication.application_id) {
            state.selectedApplication = {
              ...state.selectedApplication,
              queue_item: updatedApplication
            };
          }
      });
  },
});

// Action creators are generated for each case reducer function
export const {
  setSelectedApplication,
  clearSelectedApplication,
  setFilters,
  resetFilters,
  setSort,
  setPage,
  setPageSize,
  updateDecisionDraft,
  clearDecisionDraft
} = underwritingSlice.actions;

// Export the reducer
export default underwritingSlice.reducer;