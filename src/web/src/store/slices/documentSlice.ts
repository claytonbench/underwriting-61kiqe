import { createSlice, PayloadAction } from '@reduxjs/toolkit'; // v1.9.5
// Import internal type definitions
import {
  DocumentState,
  DocumentFilters,
  DocumentPackageFilters,
  DocumentSortField,
  DocumentPackageSortField,
  SortDirection,
} from '../../types/document.types';
import {
  fetchDocuments,
  fetchDocumentById,
  fetchDocumentPackages,
  fetchDocumentPackageById,
  uploadDocumentFile,
  getDocumentDownloadUrl,
  createNewSignatureRequest,
  fetchSignatureRequestById,
  initiateSigningSession,
  completeDocumentSignature,
  declineDocumentSignature,
  sendSignatureReminderEmail,
  fetchApplicationDocumentsList,
  fetchApplicationDocumentPackages,
  fetchPendingSignatureRequests
} from '../thunks/documentThunks';

/**
 * Initial state for the document slice
 */
const initialState: DocumentState = {
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
    search: null
  },
  documentPackageFilters: {
    package_type: null,
    status: null,
    application_id: null,
    date_range: { start: null, end: null },
    search: null
  },
  documentSort: { field: DocumentSortField.GENERATED_AT, direction: SortDirection.DESC },
  documentPackageSort: { field: DocumentPackageSortField.CREATED_AT, direction: SortDirection.DESC },
  documentPage: 1,
  documentPageSize: 10,
  documentPackagePage: 1,
  documentPackagePageSize: 10
};

/**
 * Redux slice for document management
 */
export const documentSlice = createSlice({
  name: 'document',
  initialState,
  reducers: {
    /**
     * Sets filters for document list
     * @param state The current state
     * @param action The action containing the document filters
     */
    setDocumentFilters: (state: DocumentState, action: PayloadAction<DocumentFilters>) => {
      state.documentFilters = action.payload;
      state.documentPage = 1; // Reset to first page with new filters
    },
    /**
     * Sets filters for document package list
     * @param state The current state
     * @param action The action containing the document package filters
     */
    setDocumentPackageFilters: (state: DocumentState, action: PayloadAction<DocumentPackageFilters>) => {
      state.documentPackageFilters = action.payload;
      state.documentPackagePage = 1; // Reset to first page with new filters
    },
    /**
     * Sets sort options for document list
     * @param state The current state
     * @param action The action containing the document sort options
     */
    setDocumentSort: (state: DocumentState, action: PayloadAction<{ field: DocumentSortField; direction: SortDirection }>) => {
      state.documentSort = action.payload;
    },
    /**
     * Sets sort options for document package list
     * @param state The current state
     * @param action The action containing the document package sort options
     */
    setDocumentPackageSort: (state: DocumentState, action: PayloadAction<{ field: DocumentPackageSortField; direction: SortDirection }>) => {
      state.documentPackageSort = action.payload;
    },
    /**
     * Sets current page number for document list
     * @param state The current state
     * @param action The action containing the document page number
     */
    setDocumentPage: (state: DocumentState, action: PayloadAction<number>) => {
      state.documentPage = action.payload;
    },
    /**
     * Sets page size for document list
     * @param state The current state
     * @param action The action containing the document page size
     */
    setDocumentPageSize: (state: DocumentState, action: PayloadAction<number>) => {
      state.documentPageSize = action.payload;
      state.documentPage = 1; // Reset to first page with new page size
    },
    /**
     * Sets current page number for document package list
     * @param state The current state
     * @param action The action containing the document package page number
     */
    setDocumentPackagePage: (state: DocumentState, action: PayloadAction<number>) => {
      state.documentPackagePage = action.payload;
    },
    /**
     * Sets page size for document package list
     * @param state The current state
     * @param action The action containing the document package page size
     */
    setDocumentPackagePageSize: (state: DocumentState, action: PayloadAction<number>) => {
      state.documentPackagePageSize = action.payload;
      state.documentPackagePage = 1; // Reset to first page with new page size
    },
    /**
     * Clears the currently selected document
     * @param state The current state
     */
    clearSelectedDocument: (state: DocumentState) => {
      state.selectedDocument = null;
    },
    /**
     * Clears the currently selected document package
     * @param state The current state
     */
    clearSelectedDocumentPackage: (state: DocumentState) => {
      state.selectedDocumentPackage = null;
    },
    /**
     * Resets the document state to initial values
     * @param state The current state
     */
    resetDocumentState: (state: DocumentState) => {
      state.documents= [];
      state.documentPackages= [];
      state.selectedDocument= null;
      state.selectedDocumentPackage= null;
      state.pendingSignatures= [];
      state.loading= false;
      state.error= null;
      state.totalDocuments= 0;
      state.totalDocumentPackages= 0;
      state.documentFilters= {
        document_type: null,
        status: null,
        application_id: null,
        package_id: null,
        date_range: { start: null, end: null },
        search: null,
      };
      state.documentPackageFilters= {
        package_type: null,
        status: null,
        application_id: null,
        date_range: { start: null, end: null },
        search: null,
      };
      state.documentSort= { field: DocumentSortField.GENERATED_AT, direction: SortDirection.DESC };
      state.documentPackageSort= { field: DocumentPackageSortField.CREATED_AT, direction: SortDirection.DESC };
      state.documentPage= 1;
      state.documentPageSize= 10;
      state.documentPackagePage= 1;
      state.documentPackagePageSize= 10;
    },
  },
  extraReducers: (builder) => {
    builder
      // Handle fetchDocuments async thunk results
      .addCase(fetchDocuments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDocuments.fulfilled, (state, action) => {
        state.documents = action.payload.results;
        state.totalDocuments = action.payload.total;
        state.loading = false;
      })
      .addCase(fetchDocuments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch documents';
      })
      // Handle fetchDocumentById async thunk results
      .addCase(fetchDocumentById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDocumentById.fulfilled, (state, action) => {
        state.selectedDocument = action.payload;
        state.loading = false;
      })
      .addCase(fetchDocumentById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch document';
      })
      // Handle fetchDocumentPackages async thunk results
      .addCase(fetchDocumentPackages.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDocumentPackages.fulfilled, (state, action) => {
        state.documentPackages = action.payload.results;
        state.totalDocumentPackages = action.payload.total;
        state.loading = false;
      })
      .addCase(fetchDocumentPackages.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch document packages';
      })
      // Handle fetchDocumentPackageById async thunk results
      .addCase(fetchDocumentPackageById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDocumentPackageById.fulfilled, (state, action) => {
        state.selectedDocumentPackage = action.payload;
        state.loading = false;
      })
      .addCase(fetchDocumentPackageById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch document package';
      })
      // Handle uploadDocumentFile async thunk results
      .addCase(uploadDocumentFile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(uploadDocumentFile.fulfilled, (state, action) => {
        state.documents = [...state.documents, action.payload];
        state.loading = false;
      })
      .addCase(uploadDocumentFile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to upload document';
      })
      // Handle getDocumentDownloadUrl async thunk results
      .addCase(getDocumentDownloadUrl.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getDocumentDownloadUrl.fulfilled, (state, action) => {
        if (state.selectedDocument) {
          state.selectedDocument.download_url = action.payload.download_url;
        }
        state.loading = false;
      })
      .addCase(getDocumentDownloadUrl.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to get document download URL';
      })
      // Handle fetchPendingSignatureRequests async thunk results
      .addCase(fetchPendingSignatureRequests.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPendingSignatureRequests.fulfilled, (state, action) => {
        state.pendingSignatures = action.payload;
        state.loading = false;
      })
      .addCase(fetchPendingSignatureRequests.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch pending signature requests';
      })
      // Handle fetchApplicationDocumentsList async thunk results
      .addCase(fetchApplicationDocumentsList.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchApplicationDocumentsList.fulfilled, (state, action) => {
        state.documents = action.payload;
        state.loading = false;
      })
      .addCase(fetchApplicationDocumentsList.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch application documents';
      })
      // Handle fetchApplicationDocumentPackages async thunk results
      .addCase(fetchApplicationDocumentPackages.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchApplicationDocumentPackages.fulfilled, (state, action) => {
        state.documentPackages = action.payload;
        state.loading = false;
      })
      .addCase(fetchApplicationDocumentPackages.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch application document packages';
      })
      // Handle createNewSignatureRequest async thunk results
      .addCase(createNewSignatureRequest.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createNewSignatureRequest.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(createNewSignatureRequest.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to create signature request';
      })
      // Handle fetchSignatureRequestById async thunk results
      .addCase(fetchSignatureRequestById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSignatureRequestById.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(fetchSignatureRequestById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch signature request';
      })
      // Handle initiateSigningSession async thunk results
      .addCase(initiateSigningSession.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(initiateSigningSession.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(initiateSigningSession.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to initiate signing session';
      })
      // Handle completeDocumentSignature async thunk results
      .addCase(completeDocumentSignature.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(completeDocumentSignature.fulfilled, (state, action) => {
        state.loading = false;
        const signatureRequestId = action.meta.arg;
        state.pendingSignatures = state.pendingSignatures.filter(
          (sig) => sig.id !== signatureRequestId
        );
      })
      .addCase(completeDocumentSignature.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to complete document signature';
      })
      // Handle declineDocumentSignature async thunk results
      .addCase(declineDocumentSignature.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(declineDocumentSignature.fulfilled, (state, action) => {
        state.loading = false;
        const signatureRequestId = action.meta.arg.signatureRequestId;
        state.pendingSignatures = state.pendingSignatures.filter(
          (sig) => sig.id !== signatureRequestId
        );
      })
      .addCase(declineDocumentSignature.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to decline document signature';
      })
      // Handle sendSignatureReminderEmail async thunk results
      .addCase(sendSignatureReminderEmail.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(sendSignatureReminderEmail.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(sendSignatureReminderEmail.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to send signature reminder';
      });
  },
});

// Extract action creators from the slice
export const {
  setDocumentFilters,
  setDocumentPackageFilters,
  setDocumentSort,
  setDocumentPackageSort,
  setDocumentPage,
  setDocumentPageSize,
  setDocumentPackagePage,
  setDocumentPackagePageSize,
  clearSelectedDocument,
  clearSelectedDocumentPackage,
  resetDocumentState,
} = documentSlice.actions;

// Export the reducer
export default documentSlice.reducer;