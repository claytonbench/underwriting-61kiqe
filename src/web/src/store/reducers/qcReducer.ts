import { createReducer } from '@reduxjs/toolkit'; // ^1.9.5
import { QCState, QCReviewFilters, QCReviewSort } from '../../types/qc.types';
import { SortDirection } from '../../types/common.types';
import {
  fetchQCReviews,
  fetchQCReviewDetail,
  fetchQCReviewByApplication,
  assignQCReviewToReviewer,
  startQCReviewProcess,
  updateQCReviewStatusAction,
  fetchDocumentVerifications,
  verifyDocumentAction,
  rejectDocumentAction,
  fetchStipulationVerifications,
  verifyStipulationAction,
  rejectStipulationAction,
  waiveStipulationAction,
  fetchChecklistItems,
  verifyChecklistItemAction,
  rejectChecklistItemAction,
  waiveChecklistItemAction,
  fetchQCNotes,
  createQCNoteAction,
  fetchQCReviewSummaryAction,
  fetchMyAssignedQCReviews
} from '../actions/qcActions';

// Define initial state
const initialState: QCState = {
  qcReviews: [],
  selectedQCReview: null,
  loading: false,
  error: null,
  totalQCReviews: 0,
  filters: {},
  sort: null,
  page: 1,
  pageSize: 10,
  countsByStatus: null
};

// Action handler functions
function setQCReviewFilters(state: QCState, action: { payload: QCReviewFilters }) {
  state.filters = action.payload;
}

function setQCReviewSort(state: QCState, action: { payload: QCReviewSort | null }) {
  state.sort = action.payload;
}

function resetQCState() {
  return initialState;
}

function clearQCError(state: QCState) {
  state.error = null;
}

// Define QC reducer
const qcReducer = createReducer(initialState, (builder) => {
  // Synchronous actions
  builder
    .addCase('qc/setQCReviewFilters', setQCReviewFilters)
    .addCase('qc/setQCReviewSort', setQCReviewSort)
    .addCase('qc/resetQCState', resetQCState)
    .addCase('qc/clearQCError', clearQCError);

  // Async thunks for QC reviews list
  builder
    .addCase(fetchQCReviews.pending, (state) => {
      state.loading = true;
      state.error = null;
    })
    .addCase(fetchQCReviews.fulfilled, (state, action) => {
      state.loading = false;
      state.qcReviews = action.payload.results;
      state.totalQCReviews = action.payload.total;
      state.page = action.payload.page;
      state.pageSize = action.payload.page_size;
    })
    .addCase(fetchQCReviews.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch QC reviews';
    });

  // Handle fetchMyAssignedQCReviews
  builder
    .addCase(fetchMyAssignedQCReviews.pending, (state) => {
      state.loading = true;
      state.error = null;
    })
    .addCase(fetchMyAssignedQCReviews.fulfilled, (state, action) => {
      state.loading = false;
      state.qcReviews = action.payload.results;
      state.totalQCReviews = action.payload.total;
      state.page = action.payload.page;
      state.pageSize = action.payload.page_size;
    })
    .addCase(fetchMyAssignedQCReviews.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch assigned QC reviews';
    });

  // Handle fetchQCReviewDetail
  builder
    .addCase(fetchQCReviewDetail.pending, (state) => {
      state.loading = true;
      state.error = null;
    })
    .addCase(fetchQCReviewDetail.fulfilled, (state, action) => {
      state.loading = false;
      state.selectedQCReview = action.payload;
    })
    .addCase(fetchQCReviewDetail.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch QC review details';
    });

  // Handle fetchQCReviewByApplication
  builder
    .addCase(fetchQCReviewByApplication.pending, (state) => {
      state.loading = true;
      state.error = null;
    })
    .addCase(fetchQCReviewByApplication.fulfilled, (state, action) => {
      state.loading = false;
      state.selectedQCReview = action.payload;
    })
    .addCase(fetchQCReviewByApplication.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch QC review for application';
    });

  // Handle assignQCReviewToReviewer
  builder
    .addCase(assignQCReviewToReviewer.pending, (state) => {
      state.loading = true;
      state.error = null;
    })
    .addCase(assignQCReviewToReviewer.fulfilled, (state, action) => {
      state.loading = false;
      state.selectedQCReview = action.payload;
      
      // Update the review in the list if it exists
      const index = state.qcReviews.findIndex(review => review.id === action.payload.id);
      if (index !== -1) {
        state.qcReviews[index] = {
          ...state.qcReviews[index],
          assigned_to_name: action.payload.assigned_to_name,
          status: action.payload.status
        };
      }
    })
    .addCase(assignQCReviewToReviewer.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to assign QC review';
    });

  // Handle startQCReviewProcess
  builder
    .addCase(startQCReviewProcess.pending, (state) => {
      state.loading = true;
      state.error = null;
    })
    .addCase(startQCReviewProcess.fulfilled, (state, action) => {
      state.loading = false;
      state.selectedQCReview = action.payload;
      
      // Update the review in the list if it exists
      const index = state.qcReviews.findIndex(review => review.id === action.payload.id);
      if (index !== -1) {
        state.qcReviews[index] = {
          ...state.qcReviews[index],
          status: action.payload.status
        };
      }
    })
    .addCase(startQCReviewProcess.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to start QC review process';
    });

  // Handle updateQCReviewStatusAction
  builder
    .addCase(updateQCReviewStatusAction.pending, (state) => {
      state.loading = true;
      state.error = null;
    })
    .addCase(updateQCReviewStatusAction.fulfilled, (state, action) => {
      state.loading = false;
      state.selectedQCReview = action.payload;
      
      // Update the review in the list if it exists
      const index = state.qcReviews.findIndex(review => review.id === action.payload.id);
      if (index !== -1) {
        state.qcReviews[index] = {
          ...state.qcReviews[index],
          status: action.payload.status
        };
      }
    })
    .addCase(updateQCReviewStatusAction.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to update QC review status';
    });

  // Handle fetchQCReviewSummaryAction
  builder
    .addCase(fetchQCReviewSummaryAction.pending, (state) => {
      state.loading = true;
      state.error = null;
    })
    .addCase(fetchQCReviewSummaryAction.fulfilled, (state, action) => {
      state.loading = false;
      state.countsByStatus = action.payload;
    })
    .addCase(fetchQCReviewSummaryAction.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch QC review summary';
    });
});

export default qcReducer;