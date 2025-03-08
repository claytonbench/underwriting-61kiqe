import { AnyAction } from 'redux';
import { FundingState } from '../../types/funding.types';
import {
  fetchFundingRequests, fetchFundingRequestById, fetchFundingRequestsByApplication,
  approveFundingRequest, rejectFundingRequest, fetchDisbursements,
  fetchDisbursementById, fetchDisbursementsByFundingRequest, createDisbursement,
  updateDisbursementStatus, verifyEnrollment, fetchEnrollmentVerification,
  verifyStipulation, fetchStipulationVerifications, addFundingNote,
  fetchFundingNotes, fetchFundingStatusSummary
} from '../thunks/fundingThunks';
import {
  setFundingFilters, setFundingSort, setDisbursementFilters,
  setDisbursementSort, resetFundingState, clearFundingError
} from '../slices/fundingSlice';

/**
 * Initial state for the funding reducer
 */
const initialState: FundingState = {
  fundingRequests: [],
  selectedFundingRequest: null,
  disbursements: [],
  selectedDisbursement: null,
  fundingRequestDisbursements: [],
  enrollmentVerification: null,
  stipulationVerifications: [],
  fundingNotes: [],
  statusSummary: null,
  fundingFilters: {},
  fundingSort: null,
  disbursementFilters: {},
  disbursementSort: null,
  loading: false,
  disbursementLoading: false,
  verificationLoading: false,
  notesLoading: false,
  summaryLoading: false,
  error: null
};

/**
 * Redux reducer function for handling funding state changes
 */
export default function fundingReducer(state: FundingState = initialState, action: AnyAction): FundingState {
  switch (action.type) {
    // Funding Requests actions
    case fetchFundingRequests.pending.type:
      return {
        ...state,
        loading: true,
        error: null
      };
    case fetchFundingRequests.fulfilled.type:
      return {
        ...state,
        loading: false,
        fundingRequests: action.payload.items,
        total: action.payload.total,
        page: action.payload.page,
        pageSize: action.payload.pageSize,
        totalPages: action.payload.totalPages
      };
    case fetchFundingRequests.rejected.type:
      return {
        ...state,
        loading: false,
        error: action.error.message || 'Failed to fetch funding requests'
      };

    case fetchFundingRequestById.pending.type:
      return {
        ...state,
        loading: true,
        error: null
      };
    case fetchFundingRequestById.fulfilled.type:
      return {
        ...state,
        loading: false,
        selectedFundingRequest: action.payload
      };
    case fetchFundingRequestById.rejected.type:
      return {
        ...state,
        loading: false,
        error: action.error.message || 'Failed to fetch funding request details'
      };

    case fetchFundingRequestsByApplication.pending.type:
      return {
        ...state,
        loading: true,
        error: null
      };
    case fetchFundingRequestsByApplication.fulfilled.type:
      return {
        ...state,
        loading: false,
        fundingRequests: action.payload
      };
    case fetchFundingRequestsByApplication.rejected.type:
      return {
        ...state,
        loading: false,
        error: action.error.message || 'Failed to fetch funding requests by application'
      };

    case approveFundingRequest.pending.type:
      return {
        ...state,
        loading: true,
        error: null
      };
    case approveFundingRequest.fulfilled.type:
      return {
        ...state,
        loading: false,
        selectedFundingRequest: action.payload
      };
    case approveFundingRequest.rejected.type:
      return {
        ...state,
        loading: false,
        error: action.error.message || 'Failed to approve funding request'
      };

    case rejectFundingRequest.pending.type:
      return {
        ...state,
        loading: true,
        error: null
      };
    case rejectFundingRequest.fulfilled.type:
      return {
        ...state,
        loading: false,
        selectedFundingRequest: action.payload
      };
    case rejectFundingRequest.rejected.type:
      return {
        ...state,
        loading: false,
        error: action.error.message || 'Failed to reject funding request'
      };

    // Disbursements actions
    case fetchDisbursements.pending.type:
      return {
        ...state,
        disbursementLoading: true,
        error: null
      };
    case fetchDisbursements.fulfilled.type:
      return {
        ...state,
        disbursementLoading: false,
        disbursements: action.payload.items,
        totalDisbursements: action.payload.total,
        disbursementPage: action.payload.page
      };
    case fetchDisbursements.rejected.type:
      return {
        ...state,
        disbursementLoading: false,
        error: action.error.message || 'Failed to fetch disbursements'
      };

    case fetchDisbursementById.pending.type:
      return {
        ...state,
        disbursementLoading: true,
        error: null
      };
    case fetchDisbursementById.fulfilled.type:
      return {
        ...state,
        disbursementLoading: false,
        selectedDisbursement: action.payload
      };
    case fetchDisbursementById.rejected.type:
      return {
        ...state,
        disbursementLoading: false,
        error: action.error.message || 'Failed to fetch disbursement details'
      };

    case fetchDisbursementsByFundingRequest.pending.type:
      return {
        ...state,
        disbursementLoading: true,
        error: null
      };
    case fetchDisbursementsByFundingRequest.fulfilled.type:
      return {
        ...state,
        disbursementLoading: false,
        fundingRequestDisbursements: action.payload
      };
    case fetchDisbursementsByFundingRequest.rejected.type:
      return {
        ...state,
        disbursementLoading: false,
        error: action.error.message || 'Failed to fetch disbursements by funding request'
      };

    case createDisbursement.pending.type:
      return {
        ...state,
        disbursementLoading: true,
        error: null
      };
    case createDisbursement.fulfilled.type:
      return {
        ...state,
        disbursementLoading: false,
        fundingRequestDisbursements: [...state.fundingRequestDisbursements, action.payload]
      };
    case createDisbursement.rejected.type:
      return {
        ...state,
        disbursementLoading: false,
        error: action.error.message || 'Failed to create disbursement'
      };

    case updateDisbursementStatus.pending.type:
      return {
        ...state,
        disbursementLoading: true,
        error: null
      };
    case updateDisbursementStatus.fulfilled.type:
      return {
        ...state,
        disbursementLoading: false,
        fundingRequestDisbursements: state.fundingRequestDisbursements.map(
          disbursement => disbursement.id === action.payload.id ? action.payload : disbursement
        )
      };
    case updateDisbursementStatus.rejected.type:
      return {
        ...state,
        disbursementLoading: false,
        error: action.error.message || 'Failed to update disbursement status'
      };

    // Verification actions
    case verifyEnrollment.pending.type:
      return {
        ...state,
        verificationLoading: true,
        error: null
      };
    case verifyEnrollment.fulfilled.type:
      return {
        ...state,
        verificationLoading: false,
        enrollmentVerification: action.payload
      };
    case verifyEnrollment.rejected.type:
      return {
        ...state,
        verificationLoading: false,
        error: action.error.message || 'Failed to verify enrollment'
      };

    case fetchEnrollmentVerification.pending.type:
      return {
        ...state,
        verificationLoading: true,
        error: null
      };
    case fetchEnrollmentVerification.fulfilled.type:
      return {
        ...state,
        verificationLoading: false,
        enrollmentVerification: action.payload
      };
    case fetchEnrollmentVerification.rejected.type:
      return {
        ...state,
        verificationLoading: false,
        error: action.error.message || 'Failed to fetch enrollment verification'
      };

    case verifyStipulation.pending.type:
      return {
        ...state,
        verificationLoading: true,
        error: null
      };
    case verifyStipulation.fulfilled.type: {
      const updatedStipulations = [...state.stipulationVerifications];
      const index = updatedStipulations.findIndex(
        stipulation => stipulation.id === action.payload.id
      );
      
      if (index !== -1) {
        updatedStipulations[index] = action.payload;
      } else {
        updatedStipulations.push(action.payload);
      }
      
      return {
        ...state,
        verificationLoading: false,
        stipulationVerifications: updatedStipulations
      };
    }
    case verifyStipulation.rejected.type:
      return {
        ...state,
        verificationLoading: false,
        error: action.error.message || 'Failed to verify stipulation'
      };

    case fetchStipulationVerifications.pending.type:
      return {
        ...state,
        verificationLoading: true,
        error: null
      };
    case fetchStipulationVerifications.fulfilled.type:
      return {
        ...state,
        verificationLoading: false,
        stipulationVerifications: action.payload
      };
    case fetchStipulationVerifications.rejected.type:
      return {
        ...state,
        verificationLoading: false,
        error: action.error.message || 'Failed to fetch stipulation verifications'
      };

    // Funding Notes actions
    case addFundingNote.pending.type:
      return {
        ...state,
        notesLoading: true,
        error: null
      };
    case addFundingNote.fulfilled.type:
      return {
        ...state,
        notesLoading: false,
        fundingNotes: [...state.fundingNotes, action.payload]
      };
    case addFundingNote.rejected.type:
      return {
        ...state,
        notesLoading: false,
        error: action.error.message || 'Failed to add funding note'
      };

    case fetchFundingNotes.pending.type:
      return {
        ...state,
        notesLoading: true,
        error: null
      };
    case fetchFundingNotes.fulfilled.type:
      return {
        ...state,
        notesLoading: false,
        fundingNotes: action.payload
      };
    case fetchFundingNotes.rejected.type:
      return {
        ...state,
        notesLoading: false,
        error: action.error.message || 'Failed to fetch funding notes'
      };

    // Status summary action
    case fetchFundingStatusSummary.pending.type:
      return {
        ...state,
        summaryLoading: true,
        error: null
      };
    case fetchFundingStatusSummary.fulfilled.type:
      return {
        ...state,
        summaryLoading: false,
        statusSummary: action.payload
      };
    case fetchFundingStatusSummary.rejected.type:
      return {
        ...state,
        summaryLoading: false,
        error: action.error.message || 'Failed to fetch funding status summary'
      };

    // Filter and sort actions
    case setFundingFilters.type:
      return {
        ...state,
        fundingFilters: action.payload
      };
    case setFundingSort.type:
      return {
        ...state,
        fundingSort: action.payload
      };
    case setDisbursementFilters.type:
      return {
        ...state,
        disbursementFilters: action.payload
      };
    case setDisbursementSort.type:
      return {
        ...state,
        disbursementSort: action.payload
      };
    
    // Utility actions
    case resetFundingState.type:
      return initialState;
    case clearFundingError.type:
      return {
        ...state,
        error: null
      };

    default:
      return state;
  }
}