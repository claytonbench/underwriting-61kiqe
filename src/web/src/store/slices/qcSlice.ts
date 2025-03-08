import { createSlice, PayloadAction } from '@reduxjs/toolkit'; // ^1.9.5
import {
  QCState,
  QCReview,
  QCReviewListItem,
  QCReviewFilters,
  QCReviewSort,
  QCVerificationStatus,
  QCCountsByStatus
} from '../../types/qc.types';
import { SortDirection } from '../../types/common.types';
import {
  fetchQCReviewsThunk,
  fetchQCReviewDetailThunk,
  createQCReviewThunk,
  assignQCReviewThunk,
  updateQCReviewStatusThunk,
  fetchDocumentVerificationsThunk,
  verifyDocumentThunk,
  rejectDocumentThunk,
  fetchStipulationVerificationsThunk,
  verifyStipulationThunk,
  rejectStipulationThunk,
  waiveStipulationThunk,
  fetchChecklistItemsThunk,
  verifyChecklistItemThunk,
  rejectChecklistItemThunk,
  waiveChecklistItemThunk,
  fetchQCNotesThunk,
  createQCNoteThunk,
  fetchQCReviewSummaryThunk
} from '../thunks/qcThunks';
import { RootState } from '../rootReducer';

/**
 * Initial state for the QC slice
 */
const initialState: QCState = {
  qcReviews: [],
  selectedQCReview: null,
  loading: false,
  error: null,
  totalQCReviews: 0,
  filters: {
    status: null,
    priority: null,
    assigned_to: null,
    application_id: null,
    borrower_name: null,
    school_id: null,
    date_range: { start: null, end: null }
  },
  sort: null,
  page: 1,
  pageSize: 10,
  countsByStatus: null
};

/**
 * Redux slice for QC state management
 */
export const qcSlice = createSlice({
  name: 'qc',
  initialState,
  reducers: {
    /**
     * Sets the QC reviews list
     * @param {QCState} state - The current QC state
     * @param {PayloadAction<QCReviewListItem[]>} action - The action containing the QC reviews list
     */
    setQCReviews: (state: QCState, action: PayloadAction<QCReviewListItem[]>) => {
      state.qcReviews = action.payload;
    },

    /**
     * Sets the selected QC review details
     * @param {QCState} state - The current QC state
     * @param {PayloadAction<QCReview | null>} action - The action containing the selected QC review details
     */
    setSelectedQCReview: (state: QCState, action: PayloadAction<QCReview | null>) => {
      state.selectedQCReview = action.payload;
    },

    /**
     * Sets the loading state
     * @param {QCState} state - The current QC state
     * @param {PayloadAction<boolean>} action - The action containing the loading state
     */
    setLoading: (state: QCState, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },

    /**
     * Sets the error state
     * @param {QCState} state - The current QC state
     * @param {PayloadAction<string | null>} action - The action containing the error message
     */
    setError: (state: QCState, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },

    /**
     * Sets the total QC reviews count
     * @param {QCState} state - The current QC state
     * @param {PayloadAction<number>} action - The action containing the total QC reviews count
     */
    setTotalQCReviews: (state: QCState, action: PayloadAction<number>) => {
      state.totalQCReviews = action.payload;
    },

    /**
     * Sets the filter options
     * @param {QCState} state - The current QC state
     * @param {PayloadAction<QCReviewFilters>} action - The action containing the filter options
     */
    setFilters: (state: QCState, action: PayloadAction<QCReviewFilters>) => {
      state.filters = action.payload;
    },

    /**
     * Sets the sort options
     * @param {QCState} state - The current QC state
     * @param {PayloadAction<QCReviewSort | null>} action - The action containing the sort options
     */
    setSort: (state: QCState, action: PayloadAction<QCReviewSort | null>) => {
      state.sort = action.payload;
    },

    /**
     * Sets the current page number
     * @param {QCState} state - The current QC state
     * @param {PayloadAction<number>} action - The action containing the current page number
     */
    setPage: (state: QCState, action: PayloadAction<number>) => {
      state.page = action.payload;
    },

    /**
     * Sets the page size
     * @param {QCState} state - The current QC state
     * @param {PayloadAction<number>} action - The action containing the page size
     */
    setPageSize: (state: QCState, action: PayloadAction<number>) => {
      state.pageSize = action.payload;
    },

    /**
     * Sets the counts by status
     * @param {QCState} state - The current QC state
     * @param {PayloadAction<QCCountsByStatus | null>} action - The action containing the counts by status
     */
    setCountsByStatus: (state: QCState, action: PayloadAction<QCCountsByStatus | null>) => {
      state.countsByStatus = action.payload;
    },

    /**
     * Resets the QC state to initial values
     * @param {QCState} state - The current QC state
     */
    resetQCState: (state: QCState) => {
      state.qcReviews = [];
      state.selectedQCReview = null;
      state.loading = false;
      state.error = null;
      state.totalQCReviews = 0;
      state.filters = {
        status: null,
        priority: null,
        assigned_to: null,
        application_id: null,
        borrower_name: null,
        school_id: null,
        date_range: { start: null, end: null }
      };
      state.sort = null;
      state.page = 1;
      state.pageSize = 10;
      state.countsByStatus = null;
    },

    /**
     * Updates a document verification status in the selected QC review
     * @param {QCState} state - The current QC state
     * @param {PayloadAction<{ id: string; status: QCVerificationStatus; comments?: string }>} action - The action containing the document verification update
     */
    updateDocumentVerification: (state: QCState, action: PayloadAction<{ id: string; status: QCVerificationStatus; comments?: string }>) => {
      if (state.selectedQCReview && state.selectedQCReview.document_verifications) {
        const documentVerification = state.selectedQCReview.document_verifications.find(doc => doc.id === action.payload.id);
        if (documentVerification) {
          documentVerification.status = action.payload.status;
          documentVerification.comments = action.payload.comments || null;
        }
      }
    },

    /**
     * Updates a stipulation verification status in the selected QC review
     * @param {QCState} state - The current QC state
     * @param {PayloadAction<{ id: string; status: QCVerificationStatus; comments?: string }>} action - The action containing the stipulation verification update
     */
    updateStipulationVerification: (state: QCState, action: PayloadAction<{ id: string; status: QCVerificationStatus; comments?: string }>) => {
      if (state.selectedQCReview && state.selectedQCReview.stipulation_verifications) {
        const stipulationVerification = state.selectedQCReview.stipulation_verifications.find(stip => stip.id === action.payload.id);
        if (stipulationVerification) {
          stipulationVerification.status = action.payload.status;
          stipulationVerification.comments = action.payload.comments || null;
        }
      }
    },

    /**
     * Updates a checklist item status in the selected QC review
     * @param {QCState} state - The current QC state
     * @param {PayloadAction<{ id: string; status: QCVerificationStatus; comments?: string }>} action - The action containing the checklist item update
     */
    updateChecklistItem: (state: QCState, action: PayloadAction<{ id: string; status: QCVerificationStatus; comments?: string }>) => {
      if (state.selectedQCReview && state.selectedQCReview.checklist_items) {
        const checklistItem = state.selectedQCReview.checklist_items.find(item => item.id === action.payload.id);
        if (checklistItem) {
          checklistItem.status = action.payload.status;
          checklistItem.comments = action.payload.comments || null;
        }
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Handle fetchQCReviewsThunk
      .addCase(fetchQCReviewsThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchQCReviewsThunk.fulfilled, (state, action) => {
        state.loading = false;
        state.qcReviews = action.payload.reviews;
        state.totalQCReviews = action.payload.total;
      })
      .addCase(fetchQCReviewsThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch QC reviews';
      })

      // Handle fetchQCReviewDetailThunk
      .addCase(fetchQCReviewDetailThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchQCReviewDetailThunk.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedQCReview = action.payload;
      })
      .addCase(fetchQCReviewDetailThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch QC review details';
      })

      // Handle createQCReviewThunk
      .addCase(createQCReviewThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createQCReviewThunk.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedQCReview = action.payload;
        state.qcReviews.push(action.payload as QCReviewListItem);
      })
      .addCase(createQCReviewThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to create QC review';
      })

      // Handle assignQCReviewThunk
      .addCase(assignQCReviewThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(assignQCReviewThunk.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedQCReview = action.payload;
        state.qcReviews = state.qcReviews.map(review =>
          review.id === action.payload?.id ? action.payload : review
        );
      })
      .addCase(assignQCReviewThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to assign QC review';
      })

      // Handle updateQCReviewStatusThunk
      .addCase(updateQCReviewStatusThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateQCReviewStatusThunk.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedQCReview = action.payload;
        state.qcReviews = state.qcReviews.map(review =>
          review.id === action.payload?.id ? action.payload : review
        );
      })
      .addCase(updateQCReviewStatusThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to update QC review status';
      })

      // Handle fetchDocumentVerificationsThunk
      .addCase(fetchDocumentVerificationsThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDocumentVerificationsThunk.fulfilled, (state, action) => {
        if (state.selectedQCReview) {
          state.selectedQCReview.document_verifications = action.payload;
        }
        state.loading = false;
      })
      .addCase(fetchDocumentVerificationsThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch document verifications';
      })

      // Handle verifyDocumentThunk
      .addCase(verifyDocumentThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(verifyDocumentThunk.fulfilled, (state, action) => {
        state.loading = false;
        if (state.selectedQCReview && state.selectedQCReview.document_verifications) {
          const documentVerification = state.selectedQCReview.document_verifications.find(doc => doc.id === action.payload.id);
          if (documentVerification) {
            documentVerification.status = action.payload.status;
            documentVerification.comments = action.payload.comments || null;
          }
        }
      })
      .addCase(verifyDocumentThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to verify document';
      })

      // Handle rejectDocumentThunk
      .addCase(rejectDocumentThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(rejectDocumentThunk.fulfilled, (state, action) => {
        state.loading = false;
        if (state.selectedQCReview && state.selectedQCReview.document_verifications) {
          const documentVerification = state.selectedQCReview.document_verifications.find(doc => doc.id === action.payload.id);
          if (documentVerification) {
            documentVerification.status = action.payload.status;
            documentVerification.comments = action.payload.comments || null;
          }
        }
      })
      .addCase(rejectDocumentThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to reject document';
      })

      // Handle fetchStipulationVerificationsThunk
      .addCase(fetchStipulationVerificationsThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchStipulationVerificationsThunk.fulfilled, (state, action) => {
        if (state.selectedQCReview) {
          state.selectedQCReview.stipulation_verifications = action.payload;
        }
        state.loading = false;
      })
      .addCase(fetchStipulationVerificationsThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch stipulation verifications';
      })

      // Handle verifyStipulationThunk
      .addCase(verifyStipulationThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(verifyStipulationThunk.fulfilled, (state, action) => {
        state.loading = false;
        if (state.selectedQCReview && state.selectedQCReview.stipulation_verifications) {
          const stipulationVerification = state.selectedQCReview.stipulation_verifications.find(stip => stip.id === action.payload.id);
          if (stipulationVerification) {
            stipulationVerification.status = action.payload.status;
            stipulationVerification.comments = action.payload.comments || null;
          }
        }
      })
      .addCase(verifyStipulationThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to verify stipulation';
      })

      // Handle rejectStipulationThunk
      .addCase(rejectStipulationThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(rejectStipulationThunk.fulfilled, (state, action) => {
        state.loading = false;
        if (state.selectedQCReview && state.selectedQCReview.stipulation_verifications) {
          const stipulationVerification = state.selectedQCReview.stipulation_verifications.find(stip => stip.id === action.payload.id);
          if (stipulationVerification) {
            stipulationVerification.status = action.payload.status;
            stipulationVerification.comments = action.payload.comments || null;
          }
        }
      })
      .addCase(rejectStipulationThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to reject stipulation';
      })

      // Handle waiveStipulationThunk
      .addCase(waiveStipulationThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(waiveStipulationThunk.fulfilled, (state, action) => {
        state.loading = false;
        if (state.selectedQCReview && state.selectedQCReview.stipulation_verifications) {
          const stipulationVerification = state.selectedQCReview.stipulation_verifications.find(stip => stip.id === action.payload.id);
          if (stipulationVerification) {
            stipulationVerification.status = action.payload.status;
            stipulationVerification.comments = action.payload.comments || null;
          }
        }
      })
      .addCase(waiveStipulationThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to waive stipulation';
      })

      // Handle fetchChecklistItemsThunk
      .addCase(fetchChecklistItemsThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchChecklistItemsThunk.fulfilled, (state, action) => {
        if (state.selectedQCReview) {
          state.selectedQCReview.checklist_items = action.payload;
        }
        state.loading = false;
      })
      .addCase(fetchChecklistItemsThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch checklist items';
      })

      // Handle verifyChecklistItemThunk
      .addCase(verifyChecklistItemThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(verifyChecklistItemThunk.fulfilled, (state, action) => {
        state.loading = false;
        if (state.selectedQCReview && state.selectedQCReview.checklist_items) {
          const checklistItem = state.selectedQCReview.checklist_items.find(item => item.id === action.payload.id);
          if (checklistItem) {
            checklistItem.status = action.payload.status;
            checklistItem.comments = action.payload.comments || null;
          }
        }
      })
      .addCase(verifyChecklistItemThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to verify checklist item';
      })

      // Handle rejectChecklistItemThunk
      .addCase(rejectChecklistItemThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(rejectChecklistItemThunk.fulfilled, (state, action) => {
        state.loading = false;
        if (state.selectedQCReview && state.selectedQCReview.checklist_items) {
          const checklistItem = state.selectedQCReview.checklist_items.find(item => item.id === action.payload.id);
          if (checklistItem) {
            checklistItem.status = action.payload.status;
            checklistItem.comments = action.payload.comments || null;
          }
        }
      })
      .addCase(rejectChecklistItemThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to reject checklist item';
      })

      // Handle waiveChecklistItemThunk
      .addCase(waiveChecklistItemThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(waiveChecklistItemThunk.fulfilled, (state, action) => {
        state.loading = false;
        if (state.selectedQCReview && state.selectedQCReview.checklist_items) {
          const checklistItem = state.selectedQCReview.checklist_items.find(item => item.id === action.payload.id);
          if (checklistItem) {
            checklistItem.status = action.payload.status;
            checklistItem.comments = action.payload.comments || null;
          }
        }
      })
      .addCase(waiveChecklistItemThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to waive checklist item';
      })

      // Handle fetchQCNotesThunk
      .addCase(fetchQCNotesThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchQCNotesThunk.fulfilled, (state, action) => {
        if (state.selectedQCReview) {
          state.selectedQCReview.notes = action.payload;
        }
        state.loading = false;
      })
      .addCase(fetchQCNotesThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch QC notes';
      })

      // Handle createQCNoteThunk
      .addCase(createQCNoteThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createQCNoteThunk.fulfilled, (state, action) => {
        state.loading = false;
        if (state.selectedQCReview && state.selectedQCReview.notes) {
          state.selectedQCReview.notes = [...state.selectedQCReview.notes, action.payload];
        } else if (state.selectedQCReview) {
          state.selectedQCReview.notes = [action.payload];
        }
      })
      .addCase(createQCNoteThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to create QC note';
      })

      // Handle fetchQCReviewSummaryThunk
      .addCase(fetchQCReviewSummaryThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchQCReviewSummaryThunk.fulfilled, (state, action) => {
        state.loading = false;
        state.countsByStatus = action.payload;
      })
      .addCase(fetchQCReviewSummaryThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch QC review summary';
      });
  },
});

// Extract the action creators from the slice
export const {
  setQCReviews,
  setSelectedQCReview,
  setLoading,
  setError,
  setTotalQCReviews,
  setFilters,
  setSort,
  setPage,
  setPageSize,
  setCountsByStatus,
  resetQCState,
  updateDocumentVerification,
  updateStipulationVerification,
  updateChecklistItem
} = qcSlice.actions;

// Define selectors to access the state
export const selectQCState = (state: RootState) => state.qc;
export const selectQCReviews = (state: RootState) => state.qc.qcReviews;
export const selectSelectedQCReview = (state: RootState) => state.qc.selectedQCReview;
export const selectLoading = (state: RootState) => state.qc.loading;
export const selectError = (state: RootState) => state.qc.error;
export const selectTotalQCReviews = (state: RootState) => state.qc.totalQCReviews;
export const selectFilters = (state: RootState) => state.qc.filters;
export const selectSort = (state: RootState) => state.qc.sort;
export const selectPage = (state: RootState) => state.qc.page;
export const selectPageSize = (state: RootState) => state.qc.pageSize;
export const selectCountsByStatus = (state: RootState) => state.qc.countsByStatus;

// Export the reducer
export default qcSlice.reducer;