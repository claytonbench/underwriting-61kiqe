import { createAction } from '@reduxjs/toolkit'; // v1.9.5
import {
  DocumentType, 
  DocumentStatus, 
  DocumentPackageType, 
  DocumentPackageStatus, 
  SignatureRequestStatus, 
  DocumentFilters, 
  DocumentPackageFilters, 
  DocumentSort, 
  DocumentPackageSort
} from '../../types/document.types';
import { UUID } from '../../types/common.types';

/**
 * Defines all document management action types
 */
export enum DOCUMENT_ACTION_TYPES {
  SET_DOCUMENT_FILTERS = 'documents/setDocumentFilters',
  SET_DOCUMENT_SORT = 'documents/setDocumentSort',
  SET_DOCUMENT_PACKAGE_FILTERS = 'documents/setDocumentPackageFilters',
  SET_DOCUMENT_PACKAGE_SORT = 'documents/setDocumentPackageSort',
  RESET_DOCUMENT_STATE = 'documents/resetDocumentState',
  CLEAR_DOCUMENT_ERROR = 'documents/clearDocumentError',
  FETCH_DOCUMENTS = 'documents/fetchDocuments',
  FETCH_DOCUMENT_BY_ID = 'documents/fetchDocumentById',
  FETCH_DOCUMENT_PACKAGES = 'documents/fetchDocumentPackages',
  FETCH_DOCUMENT_PACKAGE_BY_ID = 'documents/fetchDocumentPackageById',
  UPLOAD_DOCUMENT_FILE = 'documents/uploadDocumentFile',
  GET_DOCUMENT_DOWNLOAD_URL = 'documents/getDocumentDownloadUrl',
  CREATE_SIGNATURE_REQUEST = 'documents/createSignatureRequest',
  FETCH_SIGNATURE_REQUEST = 'documents/fetchSignatureRequest',
  INITIATE_SIGNING_SESSION = 'documents/initiateSigningSession',
  COMPLETE_DOCUMENT_SIGNATURE = 'documents/completeDocumentSignature',
  DECLINE_DOCUMENT_SIGNATURE = 'documents/declineDocumentSignature',
  SEND_SIGNATURE_REMINDER = 'documents/sendSignatureReminder',
  FETCH_APPLICATION_DOCUMENTS = 'documents/fetchApplicationDocuments',
  FETCH_APPLICATION_DOCUMENT_PACKAGES = 'documents/fetchApplicationDocumentPackages',
  FETCH_PENDING_SIGNATURE_REQUESTS = 'documents/fetchPendingSignatureRequests'
}

/**
 * Creates an action to set document filtering options
 * @param filters The filter criteria to apply to documents
 */
export const setDocumentFilters = createAction<DocumentFilters>(
  DOCUMENT_ACTION_TYPES.SET_DOCUMENT_FILTERS
);

/**
 * Creates an action to set document sorting options
 * @param sort The sort criteria to apply to documents, or null to clear sorting
 */
export const setDocumentSort = createAction<DocumentSort | null>(
  DOCUMENT_ACTION_TYPES.SET_DOCUMENT_SORT
);

/**
 * Creates an action to set document package filtering options
 * @param filters The filter criteria to apply to document packages
 */
export const setDocumentPackageFilters = createAction<DocumentPackageFilters>(
  DOCUMENT_ACTION_TYPES.SET_DOCUMENT_PACKAGE_FILTERS
);

/**
 * Creates an action to set document package sorting options
 * @param sort The sort criteria to apply to document packages, or null to clear sorting
 */
export const setDocumentPackageSort = createAction<DocumentPackageSort | null>(
  DOCUMENT_ACTION_TYPES.SET_DOCUMENT_PACKAGE_SORT
);

/**
 * Creates an action to reset the document state to initial values
 */
export const resetDocumentState = createAction(
  DOCUMENT_ACTION_TYPES.RESET_DOCUMENT_STATE
);

/**
 * Creates an action to clear any document-related errors
 */
export const clearDocumentError = createAction(
  DOCUMENT_ACTION_TYPES.CLEAR_DOCUMENT_ERROR
);