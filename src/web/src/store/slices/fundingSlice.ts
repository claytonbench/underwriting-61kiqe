import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import {
  FundingState,
  FundingFilters,
  DisbursementFilters,
  FundingSort,
  DisbursementSort,
} from '../../types/funding.types';
import {
  fetchFundingRequests,
  fetchFundingRequestById,
  fetchFundingRequestsByApplication,
  approveFundingRequest,
  rejectFundingRequest,
  fetchDisbursements,
  fetchDisbursementById,
  fetchDisbursementsByFundingRequest,
  createDisbursement,
  updateDisbursementStatus,
  verifyEnrollment,
  fetchEnrollmentVerification,
  verifyStipulation,
  fetchStipulationVerifications,
  addFundingNote,
  fetchFundingNotes,
  fetchFundingStatusSummary,
} from '../thunks/fundingThunks';

/**
 * Initial state for the funding slice
 */
const initialState: FundingState = {
  fundingRequests: [],
  selectedFundingRequest: null,
  disbursements: [],
  selectedDisbursement: null,
  loading: false,
  error: null,
  totalFundingRequests: 0,
  totalDisbursements: 0,
  fundingFilters: {
    status: null,
    application_id: null,
    borrower_name: null,
    school_name: null,
    date_range: { start: null, end: null },
    amount_range: { min: null, max: null },
  },
  disbursementFilters: {
    status: null,
    funding_request_id: null,
    application_id: null,
    borrower_name: null,
    school_name: null,
    disbursement_method: null,
    date_range: { start: null, end: null },
    amount_range: { min: null, max: null },
  },
  fundingSort: null,
  disbursementSort: null,
  fundingPage: 1,
  disbursementPage: 1,
  pageSize: 10,
  statusSummary: null,
};

/**
 * Redux slice for funding state management
 * Handles all funding-related state including funding requests, disbursements,
 * enrollment verification, and stipulation verification.
 */
export const fundingSlice = createSlice({
  name: 'funding',
  initialState,
  reducers: {
    /**
     * Sets the filters for funding requests list
     */
    setFundingFilters(state, action: PayloadAction<FundingFilters>) {
      state.fundingFilters = action.payload;
      state.fundingPage = 1; // Reset to first page when filters change
    },
    
    /**
     * Sets the filters for disbursements list
     */
    setDisbursementFilters(state, action: PayloadAction<DisbursementFilters>) {
      state.disbursementFilters = action.payload;
      state.disbursementPage = 1; // Reset to first page when filters change
    },
    
    /**
     * Sets the sort options for funding requests list
     */
    setFundingSort(state, action: PayloadAction<FundingSort | null>) {
      state.fundingSort = action.payload;
    },
    
    /**
     * Sets the sort options for disbursements list
     */
    setDisbursementSort(state, action: PayloadAction<DisbursementSort | null>) {
      state.disbursementSort = action.payload;
    },
    
    /**
     * Sets the current page number for funding requests pagination
     */
    setFundingPage(state, action: PayloadAction<number>) {
      state.fundingPage = action.payload;
    },
    
    /**
     * Sets the current page number for disbursements pagination
     */
    setDisbursementPage(state, action: PayloadAction<number>) {
      state.disbursementPage = action.payload;
    },
    
    /**
     * Sets the page size for both funding requests and disbursements pagination
     */
    setPageSize(state, action: PayloadAction<number>) {
      state.pageSize = action.payload;
      state.fundingPage = 1; // Reset pages when page size changes
      state.disbursementPage = 1;
    },
    
    /**
     * Clears any funding-related error messages
     */
    clearFundingError(state) {
      state.error = null;
    },
    
    /**
     * Resets the funding state to initial values
     */
    resetFundingState() {
      return initialState;
    },
  },
  extraReducers: (builder) => {
    // ======= Funding Requests Thunks =======
    
    // Handle fetchFundingRequests
    builder
      .addCase(fetchFundingRequests.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchFundingRequests.fulfilled, (state, action) => {
        state.loading = false;
        state.fundingRequests = action.payload.items;
        state.totalFundingRequests = action.payload.total;
        state.fundingPage = action.payload.page;
      })
      .addCase(fetchFundingRequests.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch funding requests';
      });

    // Handle fetchFundingRequestById
    builder
      .addCase(fetchFundingRequestById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchFundingRequestById.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedFundingRequest = action.payload;
      })
      .addCase(fetchFundingRequestById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch funding request details';
      });

    // Handle approveFundingRequest
    builder
      .addCase(approveFundingRequest.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(approveFundingRequest.fulfilled, (state, action) => {
        state.loading = false;
        
        // Update the funding request in the list if it exists
        const index = state.fundingRequests.findIndex(request => request.id === action.payload.funding_request.id);
        if (index !== -1) {
          state.fundingRequests[index] = {
            ...state.fundingRequests[index],
            status: action.payload.funding_request.status,
            approved_amount: action.payload.funding_request.approved_amount,
            approved_at: action.payload.funding_request.approved_at,
          };
        }
        
        // Update selected funding request if it's the same one
        if (state.selectedFundingRequest && state.selectedFundingRequest.funding_request.id === action.payload.funding_request.id) {
          state.selectedFundingRequest = {
            ...state.selectedFundingRequest,
            funding_request: action.payload.funding_request,
          };
        }
      })
      .addCase(approveFundingRequest.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to approve funding request';
      });

    // Handle rejectFundingRequest
    builder
      .addCase(rejectFundingRequest.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(rejectFundingRequest.fulfilled, (state, action) => {
        state.loading = false;
        
        // Update the funding request in the list if it exists
        const index = state.fundingRequests.findIndex(request => request.id === action.payload.funding_request.id);
        if (index !== -1) {
          state.fundingRequests[index] = {
            ...state.fundingRequests[index],
            status: action.payload.funding_request.status,
          };
        }
        
        // Update selected funding request if it's the same one
        if (state.selectedFundingRequest && state.selectedFundingRequest.funding_request.id === action.payload.funding_request.id) {
          state.selectedFundingRequest = {
            ...state.selectedFundingRequest,
            funding_request: action.payload.funding_request,
          };
        }
      })
      .addCase(rejectFundingRequest.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to reject funding request';
      });

    // ======= Disbursements Thunks =======
    
    // Handle fetchDisbursements
    builder
      .addCase(fetchDisbursements.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDisbursements.fulfilled, (state, action) => {
        state.loading = false;
        state.disbursements = action.payload.items;
        state.totalDisbursements = action.payload.total;
        state.disbursementPage = action.payload.page;
      })
      .addCase(fetchDisbursements.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch disbursements';
      });

    // Handle fetchDisbursementById
    builder
      .addCase(fetchDisbursementById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDisbursementById.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedDisbursement = action.payload;
      })
      .addCase(fetchDisbursementById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch disbursement details';
      });

    // Handle createDisbursement
    builder
      .addCase(createDisbursement.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createDisbursement.fulfilled, (state, action) => {
        state.loading = false;
        
        // Update selected funding request if it matches the funding request for the new disbursement
        if (state.selectedFundingRequest && state.selectedFundingRequest.funding_request.id === action.payload.funding_request_id) {
          if (state.selectedFundingRequest.disbursements) {
            state.selectedFundingRequest = {
              ...state.selectedFundingRequest,
              disbursements: [...state.selectedFundingRequest.disbursements, action.payload],
            };
          } else {
            state.selectedFundingRequest = {
              ...state.selectedFundingRequest,
              disbursements: [action.payload],
            };
          }
        }
        
        // Set the selected disbursement to the newly created one
        state.selectedDisbursement = action.payload;
      })
      .addCase(createDisbursement.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to create disbursement';
      });

    // Handle updateDisbursementStatus
    builder
      .addCase(updateDisbursementStatus.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateDisbursementStatus.fulfilled, (state, action) => {
        state.loading = false;
        
        // Update the disbursement in the list if it exists
        const index = state.disbursements.findIndex(disb => disb.id === action.payload.id);
        if (index !== -1) {
          state.disbursements[index] = {
            ...state.disbursements[index],
            status: action.payload.status,
          };
        }
        
        // Update selected disbursement if it's the same one
        if (state.selectedDisbursement && state.selectedDisbursement.id === action.payload.id) {
          state.selectedDisbursement = action.payload;
        }
        
        // Update disbursement in selectedFundingRequest if applicable
        if (state.selectedFundingRequest && state.selectedFundingRequest.disbursements) {
          const disbIndex = state.selectedFundingRequest.disbursements.findIndex(disb => disb.id === action.payload.id);
          if (disbIndex !== -1) {
            const updatedDisbursements = [...state.selectedFundingRequest.disbursements];
            updatedDisbursements[disbIndex] = action.payload;
            state.selectedFundingRequest = {
              ...state.selectedFundingRequest,
              disbursements: updatedDisbursements,
            };
          }
        }
      })
      .addCase(updateDisbursementStatus.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to update disbursement status';
      });

    // ======= Enrollment & Stipulation Verification Thunks =======
    
    // Handle verifyEnrollment
    builder
      .addCase(verifyEnrollment.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(verifyEnrollment.fulfilled, (state, action) => {
        state.loading = false;
        
        // Update selectedFundingRequest if it exists and matches
        if (state.selectedFundingRequest && state.selectedFundingRequest.funding_request.id === action.payload.funding_request_id) {
          state.selectedFundingRequest = {
            ...state.selectedFundingRequest,
            enrollment_verification: action.payload,
            // Also update the funding request status if needed
            funding_request: {
              ...state.selectedFundingRequest.funding_request,
              status: 'enrollment_verified', // Update status based on verification
            },
          };
        }
        
        // Update funding request status in the list if it exists
        const index = state.fundingRequests.findIndex(req => req.id === action.payload.funding_request_id);
        if (index !== -1) {
          state.fundingRequests[index] = {
            ...state.fundingRequests[index],
            status: 'enrollment_verified', // Update status based on verification
          };
        }
      })
      .addCase(verifyEnrollment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to verify enrollment';
      });

    // Handle verifyStipulation
    builder
      .addCase(verifyStipulation.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(verifyStipulation.fulfilled, (state, action) => {
        state.loading = false;
        
        // Update selectedFundingRequest if it exists and matches
        if (state.selectedFundingRequest && state.selectedFundingRequest.funding_request.id === action.payload.funding_request_id) {
          // Update the specific stipulation in the stipulation_verifications array
          if (state.selectedFundingRequest.stipulation_verifications) {
            const stipIndex = state.selectedFundingRequest.stipulation_verifications.findIndex(
              stip => stip.id === action.payload.id || stip.stipulation_id === action.payload.stipulation_id
            );
            
            if (stipIndex !== -1) {
              const updatedStipulations = [...state.selectedFundingRequest.stipulation_verifications];
              updatedStipulations[stipIndex] = action.payload;
              
              state.selectedFundingRequest = {
                ...state.selectedFundingRequest,
                stipulation_verifications: updatedStipulations,
              };
            } else {
              // If stipulation not found, add it to the array
              state.selectedFundingRequest = {
                ...state.selectedFundingRequest,
                stipulation_verifications: [...state.selectedFundingRequest.stipulation_verifications, action.payload],
              };
            }
          } else {
            // If stipulation_verifications doesn't exist yet, create it
            state.selectedFundingRequest = {
              ...state.selectedFundingRequest,
              stipulation_verifications: [action.payload],
            };
          }
        }
      })
      .addCase(verifyStipulation.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to verify stipulation';
      });

    // ======= Funding Notes Thunks =======
    
    // Handle addFundingNote
    builder
      .addCase(addFundingNote.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(addFundingNote.fulfilled, (state, action) => {
        state.loading = false;
        
        // Update selectedFundingRequest if it exists and matches
        if (state.selectedFundingRequest && state.selectedFundingRequest.funding_request.id === action.payload.funding_request_id) {
          // Add the new note to the notes array
          if (state.selectedFundingRequest.notes) {
            state.selectedFundingRequest = {
              ...state.selectedFundingRequest,
              notes: [...state.selectedFundingRequest.notes, action.payload],
            };
          } else {
            state.selectedFundingRequest = {
              ...state.selectedFundingRequest,
              notes: [action.payload],
            };
          }
        }
      })
      .addCase(addFundingNote.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to add funding note';
      });

    // ======= Funding Status Summary Thunk =======
    
    // Handle fetchFundingStatusSummary
    builder
      .addCase(fetchFundingStatusSummary.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchFundingStatusSummary.fulfilled, (state, action) => {
        state.loading = false;
        state.statusSummary = action.payload;
      })
      .addCase(fetchFundingStatusSummary.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch funding status summary';
      });
  },
});

// Export actions
export const {
  setFundingFilters,
  setDisbursementFilters,
  setFundingSort,
  setDisbursementSort,
  setFundingPage,
  setDisbursementPage,
  setPageSize,
  clearFundingError,
  resetFundingState,
} = fundingSlice.actions;

// Export reducer
export default fundingSlice.reducer;