import { createReducer, ActionReducerMapBuilder, PayloadAction } from '@reduxjs/toolkit'; // v1.9.5
import {
  DOCUMENT_ACTION_TYPES
} from '../actions/documentActions';
import {
  DocumentState,
  DocumentFilters,
  DocumentPackageFilters,
  DocumentSort,
  DocumentPackageSort
} from '../../types/document.types';

/**
 * Creates the initial state for the document reducer
 * @returns Initial document state object
 */
const initialDocumentState = (): DocumentState => {
  return {
    documents: [],
    documentPackages: [],
    selectedDocument: null,
    selectedDocumentPackage: null,
    pendingSignatures: [],
    loading: false,
    error: null,
    totalDocuments: 0,
    totalDocumentPackages: 0,
    documentFilters: {
      document_type: null,
      status: null,
      application_id: null,
      package_id: null,
      date_range: { start: null, end: null },
      search: null,
    },
    documentPackageFilters: {
      package_type: null,
      status: null,
      application_id: null,
      date_range: { start: null, end: null },
      search: null,
    },
    documentSort: null,
    documentPackageSort: null,
    documentPage: 1,
    documentPageSize: 10,
    documentPackagePage: 1,
    documentPackagePageSize: 10,
  };
};

/**
 * Document reducer for managing document-related state in the loan management system
 */
const documentReducer = createReducer(initialDocumentState(), (builder: ActionReducerMapBuilder<DocumentState>) => {
  builder
    // Handle standard actions
    .addCase(DOCUMENT_ACTION_TYPES.SET_DOCUMENT_FILTERS, (state, action: PayloadAction<DocumentFilters>) => {
      state.documentFilters = action.payload;
    })
    .addCase(DOCUMENT_ACTION_TYPES.SET_DOCUMENT_SORT, (state, action: PayloadAction<DocumentSort | null>) => {
      state.documentSort = action.payload;
    })
    .addCase(DOCUMENT_ACTION_TYPES.SET_DOCUMENT_PACKAGE_FILTERS, (state, action: PayloadAction<DocumentPackageFilters>) => {
      state.documentPackageFilters = action.payload;
    })
    .addCase(DOCUMENT_ACTION_TYPES.SET_DOCUMENT_PACKAGE_SORT, (state, action: PayloadAction<DocumentPackageSort | null>) => {
      state.documentPackageSort = action.payload;
    })
    .addCase(DOCUMENT_ACTION_TYPES.RESET_DOCUMENT_STATE, () => initialDocumentState())
    .addCase(DOCUMENT_ACTION_TYPES.CLEAR_DOCUMENT_ERROR, (state) => {
      state.error = null;
    })
    
    // -- Fetch documents --
    .addMatcher(
      (action) => action.type === 'documents/fetchDocuments/pending',
      (state) => {
        state.loading = true;
        state.error = null;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/fetchDocuments/fulfilled',
      (state, action) => {
        state.loading = false;
        state.documents = action.payload.results;
        state.totalDocuments = action.payload.total;
        state.documentPage = action.payload.page;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/fetchDocuments/rejected',
      (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch documents';
      }
    )
    
    // -- Fetch document by ID --
    .addMatcher(
      (action) => action.type === 'documents/fetchDocumentById/pending',
      (state) => {
        state.loading = true;
        state.error = null;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/fetchDocumentById/fulfilled',
      (state, action) => {
        state.loading = false;
        state.selectedDocument = action.payload;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/fetchDocumentById/rejected',
      (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch document';
      }
    )
    
    // -- Fetch document packages --
    .addMatcher(
      (action) => action.type === 'documents/fetchDocumentPackages/pending',
      (state) => {
        state.loading = true;
        state.error = null;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/fetchDocumentPackages/fulfilled',
      (state, action) => {
        state.loading = false;
        state.documentPackages = action.payload.results;
        state.totalDocumentPackages = action.payload.total;
        state.documentPackagePage = action.payload.page;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/fetchDocumentPackages/rejected',
      (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch document packages';
      }
    )
    
    // -- Fetch document package by ID --
    .addMatcher(
      (action) => action.type === 'documents/fetchDocumentPackageById/pending',
      (state) => {
        state.loading = true;
        state.error = null;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/fetchDocumentPackageById/fulfilled',
      (state, action) => {
        state.loading = false;
        state.selectedDocumentPackage = action.payload;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/fetchDocumentPackageById/rejected',
      (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch document package';
      }
    )
    
    // -- Upload document file --
    .addMatcher(
      (action) => action.type === 'documents/uploadDocumentFile/pending',
      (state) => {
        state.loading = true;
        state.error = null;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/uploadDocumentFile/fulfilled',
      (state, action) => {
        state.loading = false;
        // Add the newly uploaded document to the documents array
        state.documents = [...state.documents, action.payload];
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/uploadDocumentFile/rejected',
      (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to upload document';
      }
    )
    
    // -- Get document download URL --
    .addMatcher(
      (action) => action.type === 'documents/getDocumentDownloadUrl/pending',
      (state) => {
        state.loading = true;
        state.error = null;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/getDocumentDownloadUrl/fulfilled',
      (state, action) => {
        state.loading = false;
        // Update the selected document with the download URL if it exists
        if (state.selectedDocument) {
          state.selectedDocument.download_url = action.payload;
        }
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/getDocumentDownloadUrl/rejected',
      (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to get document download URL';
      }
    )
    
    // -- Fetch pending signature requests --
    .addMatcher(
      (action) => action.type === 'documents/fetchPendingSignatureRequests/pending',
      (state) => {
        state.loading = true;
        state.error = null;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/fetchPendingSignatureRequests/fulfilled',
      (state, action) => {
        state.loading = false;
        state.pendingSignatures = action.payload;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/fetchPendingSignatureRequests/rejected',
      (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch pending signature requests';
      }
    )
    
    // -- Fetch application documents list --
    .addMatcher(
      (action) => action.type === 'documents/fetchApplicationDocumentsList/pending',
      (state) => {
        state.loading = true;
        state.error = null;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/fetchApplicationDocumentsList/fulfilled',
      (state, action) => {
        state.loading = false;
        state.documents = action.payload;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/fetchApplicationDocumentsList/rejected',
      (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch application documents';
      }
    )
    
    // -- Fetch application document packages --
    .addMatcher(
      (action) => action.type === 'documents/fetchApplicationDocumentPackages/pending',
      (state) => {
        state.loading = true;
        state.error = null;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/fetchApplicationDocumentPackages/fulfilled',
      (state, action) => {
        state.loading = false;
        state.documentPackages = action.payload;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/fetchApplicationDocumentPackages/rejected',
      (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch application document packages';
      }
    )
    
    // -- Create new signature request --
    .addMatcher(
      (action) => action.type === 'documents/createNewSignatureRequest/pending',
      (state) => {
        state.loading = true;
        state.error = null;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/createNewSignatureRequest/fulfilled',
      (state) => {
        state.loading = false;
        // We don't need to update state here, just indicate success through loading state
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/createNewSignatureRequest/rejected',
      (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to create signature request';
      }
    )
    
    // -- Fetch signature request by ID --
    .addMatcher(
      (action) => action.type === 'documents/fetchSignatureRequestById/pending',
      (state) => {
        state.loading = true;
        state.error = null;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/fetchSignatureRequestById/fulfilled',
      (state) => {
        state.loading = false;
        // Signature request data might be needed elsewhere in the app, but not in this state slice
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/fetchSignatureRequestById/rejected',
      (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch signature request';
      }
    )
    
    // -- Initiate signing session --
    .addMatcher(
      (action) => action.type === 'documents/initiateSigningSession/pending',
      (state) => {
        state.loading = true;
        state.error = null;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/initiateSigningSession/fulfilled',
      (state) => {
        state.loading = false;
        // Signing session data might be needed elsewhere in the app, but not in this state slice
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/initiateSigningSession/rejected',
      (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to initiate signing session';
      }
    )
    
    // -- Complete document signature --
    .addMatcher(
      (action) => action.type === 'documents/completeDocumentSignature/pending',
      (state) => {
        state.loading = true;
        state.error = null;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/completeDocumentSignature/fulfilled',
      (state, action) => {
        state.loading = false;
        // Remove the completed signature request from pendingSignatures
        const signatureRequestId = action.meta.arg;
        state.pendingSignatures = state.pendingSignatures.filter(
          (sig) => sig.id !== signatureRequestId
        );
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/completeDocumentSignature/rejected',
      (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to complete document signature';
      }
    )
    
    // -- Decline document signature --
    .addMatcher(
      (action) => action.type === 'documents/declineDocumentSignature/pending',
      (state) => {
        state.loading = true;
        state.error = null;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/declineDocumentSignature/fulfilled',
      (state, action) => {
        state.loading = false;
        // Remove the declined signature request from pendingSignatures
        const signatureRequestId = action.meta.arg.id;
        state.pendingSignatures = state.pendingSignatures.filter(
          (sig) => sig.id !== signatureRequestId
        );
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/declineDocumentSignature/rejected',
      (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to decline document signature';
      }
    )
    
    // -- Send signature reminder email --
    .addMatcher(
      (action) => action.type === 'documents/sendSignatureReminderEmail/pending',
      (state) => {
        state.loading = true;
        state.error = null;
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/sendSignatureReminderEmail/fulfilled',
      (state) => {
        state.loading = false;
        // No state changes needed, just indicate success through loading state
      }
    )
    .addMatcher(
      (action) => action.type === 'documents/sendSignatureReminderEmail/rejected',
      (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to send signature reminder';
      }
    );
});

export default documentReducer;