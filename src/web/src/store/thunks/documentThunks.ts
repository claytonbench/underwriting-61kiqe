import { createAsyncThunk } from '@reduxjs/toolkit'; // v1.9.5

// Import internal type definitions
import {
  Document,
  DocumentPackage,
  DocumentListItem,
  DocumentPackageListItem,
  DocumentFilters,
  DocumentPackageFilters,
  DocumentSort,
  DocumentPackageSort,
  DocumentUploadRequest,
  SignatureRequest,
  SignatureRequestCreateRequest,
  DocumentSigningSession,
  DocumentSigningResult,
} from '../../types/document.types';
import {
  UUID,
  PaginatedResponse,
} from '../../types/common.types';

// Import API client functions for document operations
import {
  getDocuments,
  getDocument,
  getDocumentPackages,
  getDocumentPackage,
  uploadDocument,
  downloadDocument,
  createSignatureRequest,
  getSignatureRequest,
  getSigningSession,
  completeSignature,
  declineSignature,
  sendSignatureReminder,
  getApplicationDocuments,
  getApplicationDocumentPackages,
  getPendingSignatures,
  generateDocumentPackage,
} from '../../api/documents';

// Import the RootState type for accessing the Redux store state
import { RootState } from '../rootReducer';

/**
 * Async thunk for fetching a paginated list of documents with optional filtering and sorting
 */
export const fetchDocuments = createAsyncThunk<PaginatedResponse<DocumentListItem>, { page?: number; pageSize?: number; filters?: DocumentFilters; sort?: DocumentSort }>(
  'documents/fetchDocuments',
  async ({ page = 1, pageSize = 10, filters, sort }) => {
    // Call getDocuments API function with extracted parameters
    const response = await getDocuments({ page, page_size: pageSize, filters, sort });

    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch documents');
    }

    // Return the paginated document list response
    return response.data;
  }
);

/**
 * Async thunk for fetching a single document by ID
 */
export const fetchDocumentById = createAsyncThunk<Document, UUID>(
  'documents/fetchDocumentById',
  async (documentId) => {
    // Call getDocument API function with the document ID
    const response = await getDocument(documentId);

    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch document');
    }

    // Return the document data response
    return response.data;
  }
);

/**
 * Async thunk for fetching a paginated list of document packages with optional filtering and sorting
 */
export const fetchDocumentPackages = createAsyncThunk<PaginatedResponse<DocumentPackageListItem>, { page?: number; pageSize?: number; filters?: DocumentPackageFilters; sort?: DocumentPackageSort }>(
  'documents/fetchDocumentPackages',
  async ({ page = 1, pageSize = 10, filters, sort }) => {
    // Call getDocumentPackages API function with extracted parameters
    const response = await getDocumentPackages({ page, page_size: pageSize, filters, sort });

    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch document packages');
    }

    // Return the paginated document package list response
    return response.data;
  }
);

/**
 * Async thunk for fetching a single document package by ID
 */
export const fetchDocumentPackageById = createAsyncThunk<DocumentPackage, UUID>(
  'documents/fetchDocumentPackageById',
  async (packageId) => {
    // Call getDocumentPackage API function with the package ID
    const response = await getDocumentPackage(packageId);

    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch document package');
    }

    // Return the document package data response
    return response.data;
  }
);

/**
 * Async thunk for uploading a document file
 */
export const uploadDocumentFile = createAsyncThunk<Document, DocumentUploadRequest>(
  'documents/uploadDocumentFile',
  async (uploadRequest) => {
    // Call uploadDocument API function with the upload request data
    const response = await uploadDocument(uploadRequest);

    if (!response.success) {
      throw new Error(response.message || 'Failed to upload document');
    }

    // Return the uploaded document data response
    return response.data;
  }
);

/**
 * Async thunk for getting a download URL for a document
 */
export const getDocumentDownloadUrl = createAsyncThunk<{ download_url: string }, UUID>(
  'documents/getDocumentDownloadUrl',
  async (documentId) => {
    // Call downloadDocument API function with the document ID
    const response = await downloadDocument(documentId);

    if (!response.success) {
      throw new Error(response.message || 'Failed to get document download URL');
    }

    // Return the download URL response
    return response.data;
  }
);

/**
 * Async thunk for creating a new signature request for a document
 */
export const createNewSignatureRequest = createAsyncThunk<{ signature_request_id: UUID; status: string; signing_url: string | null }, SignatureRequestCreateRequest>(
  'documents/createNewSignatureRequest',
  async (requestData) => {
    // Call createSignatureRequest API function with the request data
    const response = await createSignatureRequest(requestData);

    if (!response.success) {
      throw new Error(response.message || 'Failed to create signature request');
    }

    // Return the signature request creation response
    return response.data;
  }
);

/**
 * Async thunk for fetching a signature request by ID
 */
export const fetchSignatureRequestById = createAsyncThunk<SignatureRequest, UUID>(
  'documents/fetchSignatureRequestById',
  async (signatureRequestId) => {
    // Call getSignatureRequest API function with the signature request ID
    const response = await getSignatureRequest(signatureRequestId);

    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch signature request');
    }

    // Return the signature request data response
    return response.data;
  }
);

/**
 * Async thunk for initiating a document signing session
 */
export const initiateSigningSession = createAsyncThunk<DocumentSigningSession, UUID>(
  'documents/initiateSigningSession',
  async (signatureRequestId) => {
    // Call getSigningSession API function with the signature request ID
    const response = await getSigningSession(signatureRequestId);

    if (!response.success) {
      throw new Error(response.message || 'Failed to initiate signing session');
    }

    // Return the document signing session data response
    return response.data;
  }
);

/**
 * Async thunk for completing a document signature
 */
export const completeDocumentSignature = createAsyncThunk<DocumentSigningResult, UUID>(
  'documents/completeDocumentSignature',
  async (signatureRequestId) => {
    // Call completeSignature API function with the signature request ID
    const response = await completeSignature(signatureRequestId);

    if (!response.success) {
      throw new Error(response.message || 'Failed to complete document signature');
    }

    // Return the document signing result response
    return response.data;
  }
);

/**
 * Async thunk for declining a document signature
 */
export const declineDocumentSignature = createAsyncThunk<DocumentSigningResult, { signatureRequestId: UUID; reason: string }>(
  'documents/declineDocumentSignature',
  async ({ signatureRequestId, reason }) => {
    // Call declineSignature API function with the signature request ID and reason
    const response = await declineSignature({ signatureRequestId, reason });

    if (!response.success) {
      throw new Error(response.message || 'Failed to decline document signature');
    }

    // Return the document signing result response
    return response.data;
  }
);

/**
 * Async thunk for sending a signature reminder email
 */
export const sendSignatureReminderEmail = createAsyncThunk<{ success: boolean }, UUID>(
  'documents/sendSignatureReminderEmail',
  async (signatureRequestId) => {
    // Call sendSignatureReminder API function with the signature request ID
    const response = await sendSignatureReminder(signatureRequestId);

    if (!response.success) {
      throw new Error(response.message || 'Failed to send signature reminder');
    }

    // Return the success response
    return response.data;
  }
);

/**
 * Async thunk for fetching documents for an application
 */
export const fetchApplicationDocumentsList = createAsyncThunk<Document[], UUID>(
  'documents/fetchApplicationDocumentsList',
  async (applicationId) => {
    // Call getApplicationDocuments API function with the application ID
    const response = await getApplicationDocuments(applicationId);

    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch application documents');
    }

    // Return the application documents response
    return response.data;
  }
);

/**
 * Async thunk for fetching document packages for an application
 */
export const fetchApplicationDocumentPackages = createAsyncThunk<DocumentPackage[], UUID>(
  'documents/fetchApplicationDocumentPackages',
  async (applicationId) => {
    // Call getApplicationDocumentPackages API function with the application ID
    const response = await getApplicationDocumentPackages(applicationId);

    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch application document packages');
    }

    // Return the application document packages response
    return response.data;
  }
);

/**
 * Async thunk for fetching pending signature requests for the current user
 */
export const fetchPendingSignatureRequests = createAsyncThunk<SignatureRequest[], void>(
  'documents/fetchPendingSignatureRequests',
  async () => {
    // Call getPendingSignatures API function
    const response = await getPendingSignatures();

    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch pending signature requests');
    }

    // Return the pending signature requests response
    return response.data;
  }
);

/**
 * Async thunk for generating a document package for an application
 */
export const generateNewDocumentPackage = createAsyncThunk<DocumentPackage, { applicationId: UUID; packageType: string }>(
  'documents/generateNewDocumentPackage',
  async ({ applicationId, packageType }) => {
    // Call generateDocumentPackage API function with the application ID and package type
    const response = await generateDocumentPackage({ applicationId, packageType });

    if (!response.success) {
      throw new Error(response.message || 'Failed to generate document package');
    }

    // Return the generated document package response
    return response.data;
  }
);