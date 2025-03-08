import { createReducer } from '@reduxjs/toolkit'; // ^1.9.5

import {
  UnderwritingState,
  UnderwritingQueueItem,
  UnderwritingQueueFilters,
  UnderwritingQueueSort
} from '../../types/underwriting.types';

import {
  setUnderwritingFilters,
  setUnderwritingSort,
  selectApplication,
  clearSelectedApplication,
  resetUnderwritingState,
  clearUnderwritingError,
  updateDecisionDraft,
  fetchUnderwritingQueue,
  fetchAssignedApplications,
  fetchApplicationDetail,
  assignApplicationToUnderwriter,
  unassignApplicationFromUnderwriter,
  startReviewingApplication,
  fetchCreditInformation,
  uploadCreditReportFile,
  submitDecision,
  fetchDecision,
  saveDraftDecision,
  fetchStipulations,
  updateStipulationStatus,
  addNote,
  fetchNotes,
  fetchMetrics,
  updateApplicationPriority,
  requestApplicationRevision
} from '../actions/underwritingActions';

/**
 * Creates the initial state for the underwriting reducer
 * @returns Initial state object for the underwriting reducer
 */
const createInitialState = (): UnderwritingState => ({
  queue: {
    items: [],
    total: 0,
    page: 1,
    pageSize: 10,
    totalPages: 0
  },
  assignedApplications: {
    items: [],
    total: 0,
    page: 1,
    pageSize: 10,
    totalPages: 0
  },
  currentApplication: null,
  creditInformation: {
    borrower: null,
    coBorrower: null
  },
  decision: null,
  stipulations: [],
  notes: [],
  metrics: null,
  filters: {
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
  sort: null,
  loading: {
    queue: false,
    assignedApplications: false,
    applicationDetail: false,
    creditInformation: false,
    decision: false,
    stipulations: false,
    notes: false,
    metrics: false
  },
  error: null,
  decisionDraft: null
});

/**
 * Reducer for managing the underwriting state in the loan management system.
 * Handles state transitions for underwriting queue management, application review,
 * credit information, decision making, stipulations, and notes.
 */
const underwritingReducer = createReducer(createInitialState(), (builder) => {
  builder
    // Handle simple actions
    .addCase(setUnderwritingFilters, (state, action) => {
      state.filters = action.payload;
    })
    .addCase(setUnderwritingSort, (state, action) => {
      state.sort = action.payload;
    })
    .addCase(selectApplication, (state, action) => {
      state.loading.applicationDetail = true;
      state.error = null;
    })
    .addCase(clearSelectedApplication, (state) => {
      state.currentApplication = null;
      state.creditInformation.borrower = null;
      state.creditInformation.coBorrower = null;
      state.decision = null;
      state.stipulations = [];
      state.notes = [];
    })
    .addCase(resetUnderwritingState, () => {
      return createInitialState();
    })
    .addCase(clearUnderwritingError, (state) => {
      state.error = null;
    })
    .addCase(updateDecisionDraft, (state, action) => {
      state.decisionDraft = action.payload;
    })

    // Handle async action: fetchUnderwritingQueue
    .addCase(fetchUnderwritingQueue.pending, (state) => {
      state.loading.queue = true;
      state.error = null;
    })
    .addCase(fetchUnderwritingQueue.fulfilled, (state, action) => {
      state.queue.items = action.payload.results;
      state.queue.total = action.payload.total;
      state.queue.page = action.payload.page;
      state.queue.pageSize = action.payload.page_size;
      state.queue.totalPages = action.payload.total_pages;
      state.loading.queue = false;
    })
    .addCase(fetchUnderwritingQueue.rejected, (state, action) => {
      state.loading.queue = false;
      state.error = action.error.message || 'Failed to fetch underwriting queue';
    })

    // Handle async action: fetchAssignedApplications
    .addCase(fetchAssignedApplications.pending, (state) => {
      state.loading.assignedApplications = true;
      state.error = null;
    })
    .addCase(fetchAssignedApplications.fulfilled, (state, action) => {
      state.assignedApplications.items = action.payload.results;
      state.assignedApplications.total = action.payload.total;
      state.assignedApplications.page = action.payload.page;
      state.assignedApplications.pageSize = action.payload.page_size;
      state.assignedApplications.totalPages = action.payload.total_pages;
      state.loading.assignedApplications = false;
    })
    .addCase(fetchAssignedApplications.rejected, (state, action) => {
      state.loading.assignedApplications = false;
      state.error = action.error.message || 'Failed to fetch assigned applications';
    })

    // Handle async action: fetchApplicationDetail
    .addCase(fetchApplicationDetail.pending, (state) => {
      state.loading.applicationDetail = true;
      state.error = null;
    })
    .addCase(fetchApplicationDetail.fulfilled, (state, action) => {
      state.currentApplication = action.payload;
      state.loading.applicationDetail = false;
    })
    .addCase(fetchApplicationDetail.rejected, (state, action) => {
      state.loading.applicationDetail = false;
      state.error = action.error.message || 'Failed to fetch application details';
    })

    // Handle async action: fetchCreditInformation
    .addCase(fetchCreditInformation.pending, (state) => {
      state.loading.creditInformation = true;
      state.error = null;
    })
    .addCase(fetchCreditInformation.fulfilled, (state, action) => {
      if (action.payload.is_co_borrower) {
        state.creditInformation.coBorrower = action.payload;
      } else {
        state.creditInformation.borrower = action.payload;
      }
      state.loading.creditInformation = false;
    })
    .addCase(fetchCreditInformation.rejected, (state, action) => {
      state.loading.creditInformation = false;
      state.error = action.error.message || 'Failed to fetch credit information';
    })

    // Handle async action: uploadCreditReportFile
    .addCase(uploadCreditReportFile.pending, (state) => {
      state.loading.creditInformation = true;
      state.error = null;
    })
    .addCase(uploadCreditReportFile.fulfilled, (state, action) => {
      if (action.payload.is_co_borrower) {
        state.creditInformation.coBorrower = action.payload;
      } else {
        state.creditInformation.borrower = action.payload;
      }
      state.loading.creditInformation = false;
    })
    .addCase(uploadCreditReportFile.rejected, (state, action) => {
      state.loading.creditInformation = false;
      state.error = action.error.message || 'Failed to upload credit report';
    })

    // Handle async action: fetchDecision
    .addCase(fetchDecision.pending, (state) => {
      state.loading.decision = true;
      state.error = null;
    })
    .addCase(fetchDecision.fulfilled, (state, action) => {
      state.decision = action.payload;
      state.loading.decision = false;
    })
    .addCase(fetchDecision.rejected, (state, action) => {
      state.loading.decision = false;
      state.error = action.error.message || 'Failed to fetch decision';
    })

    // Handle async action: submitDecision
    .addCase(submitDecision.pending, (state) => {
      state.loading.decision = true;
      state.error = null;
    })
    .addCase(submitDecision.fulfilled, (state, action) => {
      state.decision = action.payload;
      state.decisionDraft = null;
      state.loading.decision = false;
    })
    .addCase(submitDecision.rejected, (state, action) => {
      state.loading.decision = false;
      state.error = action.error.message || 'Failed to submit decision';
    })

    // Handle async action: saveDraftDecision
    .addCase(saveDraftDecision.pending, (state) => {
      state.loading.decision = true;
      state.error = null;
    })
    .addCase(saveDraftDecision.fulfilled, (state, action) => {
      state.decisionDraft = action.payload;
      state.loading.decision = false;
    })
    .addCase(saveDraftDecision.rejected, (state, action) => {
      state.loading.decision = false;
      state.error = action.error.message || 'Failed to save draft decision';
    })

    // Handle async action: fetchStipulations
    .addCase(fetchStipulations.pending, (state) => {
      state.loading.stipulations = true;
      state.error = null;
    })
    .addCase(fetchStipulations.fulfilled, (state, action) => {
      state.stipulations = action.payload;
      state.loading.stipulations = false;
    })
    .addCase(fetchStipulations.rejected, (state, action) => {
      state.loading.stipulations = false;
      state.error = action.error.message || 'Failed to fetch stipulations';
    })

    // Handle async action: updateStipulationStatus
    .addCase(updateStipulationStatus.fulfilled, (state, action) => {
      const updatedStipulation = action.payload;
      const index = state.stipulations.findIndex(s => s.id === updatedStipulation.id);
      if (index !== -1) {
        state.stipulations[index] = updatedStipulation;
      }
    })
    .addCase(updateStipulationStatus.rejected, (state, action) => {
      state.error = action.error.message || 'Failed to update stipulation status';
    })

    // Handle async action: fetchNotes
    .addCase(fetchNotes.pending, (state) => {
      state.loading.notes = true;
      state.error = null;
    })
    .addCase(fetchNotes.fulfilled, (state, action) => {
      state.notes = action.payload;
      state.loading.notes = false;
    })
    .addCase(fetchNotes.rejected, (state, action) => {
      state.loading.notes = false;
      state.error = action.error.message || 'Failed to fetch notes';
    })

    // Handle async action: addNote
    .addCase(addNote.fulfilled, (state, action) => {
      state.notes = [action.payload, ...state.notes];
    })
    .addCase(addNote.rejected, (state, action) => {
      state.error = action.error.message || 'Failed to add note';
    })

    // Handle async action: fetchMetrics
    .addCase(fetchMetrics.pending, (state) => {
      state.loading.metrics = true;
      state.error = null;
    })
    .addCase(fetchMetrics.fulfilled, (state, action) => {
      state.metrics = action.payload;
      state.loading.metrics = false;
    })
    .addCase(fetchMetrics.rejected, (state, action) => {
      state.loading.metrics = false;
      state.error = action.error.message || 'Failed to fetch metrics';
    })

    // Handle application queue item updates
    .addCase(assignApplicationToUnderwriter.fulfilled, (state, action) => {
      const updatedQueue = action.payload;
      const index = state.queue.items.findIndex(item => item.queue_id === updatedQueue.id);
      if (index !== -1) {
        state.queue.items[index] = {
          ...state.queue.items[index],
          assigned_to: updatedQueue.assigned_to,
          assigned_to_name: updatedQueue.assigned_to_name || state.queue.items[index].assigned_to_name,
          status: updatedQueue.status
        };
      }
    })
    .addCase(assignApplicationToUnderwriter.rejected, (state, action) => {
      state.error = action.error.message || 'Failed to assign application';
    })

    .addCase(unassignApplicationFromUnderwriter.fulfilled, (state, action) => {
      const updatedQueue = action.payload;
      const index = state.queue.items.findIndex(item => item.queue_id === updatedQueue.id);
      if (index !== -1) {
        state.queue.items[index] = {
          ...state.queue.items[index],
          assigned_to: null,
          assigned_to_name: null,
          status: updatedQueue.status
        };
      }
    })
    .addCase(unassignApplicationFromUnderwriter.rejected, (state, action) => {
      state.error = action.error.message || 'Failed to unassign application';
    })

    .addCase(startReviewingApplication.fulfilled, (state, action) => {
      const updatedQueue = action.payload;
      const index = state.queue.items.findIndex(item => item.queue_id === updatedQueue.id);
      if (index !== -1) {
        state.queue.items[index] = {
          ...state.queue.items[index],
          status: updatedQueue.status
        };
      }
    })
    .addCase(startReviewingApplication.rejected, (state, action) => {
      state.error = action.error.message || 'Failed to start application review';
    })

    .addCase(updateApplicationPriority.fulfilled, (state, action) => {
      const updatedQueue = action.payload;
      const index = state.queue.items.findIndex(item => item.queue_id === updatedQueue.id);
      if (index !== -1) {
        state.queue.items[index] = {
          ...state.queue.items[index],
          priority: updatedQueue.priority
        };
      }
    })
    .addCase(updateApplicationPriority.rejected, (state, action) => {
      state.error = action.error.message || 'Failed to update priority';
    })

    .addCase(requestApplicationRevision.fulfilled, (state, action) => {
      const updatedApplication = action.payload;
      const index = state.queue.items.findIndex(item => item.application_id === updatedApplication.application_id);
      if (index !== -1) {
        state.queue.items[index] = {
          ...state.queue.items[index],
          status: updatedApplication.status
        };
      }
    })
    .addCase(requestApplicationRevision.rejected, (state, action) => {
      state.error = action.error.message || 'Failed to request revision';
    });
});

export default underwritingReducer;