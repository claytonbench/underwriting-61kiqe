/**
 * Document Management API Client
 * 
 * Provides functions for interacting with the document management API endpoints,
 * including retrieving, uploading, downloading documents, managing document packages,
 * and handling e-signature workflows.
 * 
 * @version 1.0.0
 */

import { AxiosError } from 'axios'; // ^1.4.0
import { apiClient, handleApiError } from '../config/api';
import { API_ENDPOINTS } from '../config/constants';
import { 
  UUID, 
  ApiResponse, 
  PaginatedResponse,
} from '../types/common.types';
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
} from '../types/document.types';

/**
 * Retrieves a paginated list of documents with optional filtering and sorting
 * 
 * @param options - Pagination, filtering, and sorting options
 * @returns Promise resolving to paginated document list
 */
export async function getDocuments({
  page = 1,
  page_size = 10,
  filters,
  sort
}: {
  page?: number;
  page_size?: number;
  filters?: DocumentFilters;
  sort?: DocumentSort;
}): Promise<ApiResponse<PaginatedResponse<DocumentListItem>>> {
  try {
    // Construct query parameters
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('page_size', page_size.toString());
    
    // Add filters if provided
    if (filters) {
      if (filters.document_type) params.append('document_type', filters.document_type);
      if (filters.status) params.append('status', filters.status);
      if (filters.application_id) params.append('application_id', filters.application_id);
      if (filters.package_id) params.append('package_id', filters.package_id);
      if (filters.search) params.append('search', filters.search);
      if (filters.date_range) {
        if (filters.date_range.start) params.append('date_from', filters.date_range.start);
        if (filters.date_range.end) params.append('date_to', filters.date_range.end);
      }
    }
    
    // Add sorting if provided
    if (sort) {
      params.append('sort_by', sort.field);
      params.append('sort_direction', sort.direction);
    }
    
    // Make API request
    const response = await apiClient.get(`${API_ENDPOINTS.DOCUMENTS.BASE}/list`, { params });
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
}

/**
 * Retrieves a single document by ID
 * 
 * @param id - Document ID
 * @returns Promise resolving to document data
 */
export async function getDocument(id: UUID): Promise<ApiResponse<Document>> {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.DOCUMENTS.BY_ID(id)}`);
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
}

/**
 * Retrieves a paginated list of document packages with optional filtering and sorting
 * 
 * @param options - Pagination, filtering, and sorting options
 * @returns Promise resolving to paginated document package list
 */
export async function getDocumentPackages({
  page = 1,
  page_size = 10,
  filters,
  sort
}: {
  page?: number;
  page_size?: number;
  filters?: DocumentPackageFilters;
  sort?: DocumentPackageSort;
}): Promise<ApiResponse<PaginatedResponse<DocumentPackageListItem>>> {
  try {
    // Construct query parameters
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('page_size', page_size.toString());
    
    // Add filters if provided
    if (filters) {
      if (filters.package_type) params.append('package_type', filters.package_type);
      if (filters.status) params.append('status', filters.status);
      if (filters.application_id) params.append('application_id', filters.application_id);
      if (filters.search) params.append('search', filters.search);
      if (filters.date_range) {
        if (filters.date_range.start) params.append('date_from', filters.date_range.start);
        if (filters.date_range.end) params.append('date_to', filters.date_range.end);
      }
    }
    
    // Add sorting if provided
    if (sort) {
      params.append('sort_by', sort.field);
      params.append('sort_direction', sort.direction);
    }
    
    // Make API request
    const response = await apiClient.get(`${API_ENDPOINTS.DOCUMENTS.BASE}/packages`, { params });
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
}

/**
 * Retrieves a single document package by ID
 * 
 * @param id - Document package ID
 * @returns Promise resolving to document package data
 */
export async function getDocumentPackage(id: UUID): Promise<ApiResponse<DocumentPackage>> {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.DOCUMENTS.BASE}/packages/${id}`);
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
}

/**
 * Uploads a document file
 * 
 * @param uploadRequest - Document upload request data
 * @returns Promise resolving to the uploaded document data
 */
export async function uploadDocument(uploadRequest: DocumentUploadRequest): Promise<ApiResponse<Document>> {
  try {
    // Create FormData object for file upload
    const formData = new FormData();
    formData.append('file', uploadRequest.file);
    formData.append('application_id', uploadRequest.application_id);
    formData.append('document_type', uploadRequest.document_type);
    
    // Make API request with FormData
    const response = await apiClient.post(API_ENDPOINTS.DOCUMENTS.UPLOAD, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
}

/**
 * Gets a download URL for a document
 * 
 * @param id - Document ID
 * @returns Promise resolving to an object containing the download URL
 */
export async function downloadDocument(id: UUID): Promise<ApiResponse<{ download_url: string }>> {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.DOCUMENTS.DOWNLOAD(id)}`);
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
}

/**
 * Creates a new signature request for a document
 * 
 * @param requestData - Signature request creation data
 * @returns Promise resolving to the created signature request data
 */
export async function createSignatureRequest(
  requestData: SignatureRequestCreateRequest
): Promise<ApiResponse<{ signature_request_id: UUID; status: string; signing_url: string | null }>> {
  try {
    const response = await apiClient.post(API_ENDPOINTS.DOCUMENTS.SIGNATURE_REQUEST, requestData);
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
}

/**
 * Retrieves a signature request by ID
 * 
 * @param id - Signature request ID
 * @returns Promise resolving to the signature request data
 */
export async function getSignatureRequest(id: UUID): Promise<ApiResponse<SignatureRequest>> {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.DOCUMENTS.SIGNATURE_STATUS(id)}`);
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
}

/**
 * Initiates a document signing session
 * 
 * @param signatureRequestId - Signature request ID
 * @returns Promise resolving to the document signing session data
 */
export async function getSigningSession(signatureRequestId: UUID): Promise<ApiResponse<DocumentSigningSession>> {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.DOCUMENTS.BASE}/signatures/${signatureRequestId}/session`);
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
}

/**
 * Completes a document signature
 * 
 * @param signatureRequestId - Signature request ID
 * @returns Promise resolving to the document signing result
 */
export async function completeSignature(signatureRequestId: UUID): Promise<ApiResponse<DocumentSigningResult>> {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.DOCUMENTS.BASE}/signatures/${signatureRequestId}/complete`);
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
}

/**
 * Declines a document signature
 * 
 * @param options - Signature request ID and decline reason
 * @returns Promise resolving to the document signing result
 */
export async function declineSignature({
  signatureRequestId,
  reason
}: {
  signatureRequestId: UUID;
  reason: string;
}): Promise<ApiResponse<DocumentSigningResult>> {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.DOCUMENTS.BASE}/signatures/${signatureRequestId}/decline`, {
      reason
    });
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
}

/**
 * Sends a signature reminder email
 * 
 * @param signatureRequestId - Signature request ID
 * @returns Promise resolving to a success response
 */
export async function sendSignatureReminder(signatureRequestId: UUID): Promise<ApiResponse<{ success: boolean }>> {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.DOCUMENTS.BASE}/signatures/${signatureRequestId}/remind`);
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
}

/**
 * Retrieves documents for an application
 * 
 * @param applicationId - Application ID
 * @returns Promise resolving to array of application documents
 */
export async function getApplicationDocuments(applicationId: UUID): Promise<ApiResponse<Document[]>> {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.APPLICATIONS.DOCUMENTS(applicationId)}`);
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
}

/**
 * Retrieves document packages for an application
 * 
 * @param applicationId - Application ID
 * @returns Promise resolving to array of application document packages
 */
export async function getApplicationDocumentPackages(applicationId: UUID): Promise<ApiResponse<DocumentPackage[]>> {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.APPLICATIONS.BY_ID(applicationId)}/document-packages`);
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
}

/**
 * Retrieves pending signature requests for the current user
 * 
 * @returns Promise resolving to array of pending signature requests
 */
export async function getPendingSignatures(): Promise<ApiResponse<SignatureRequest[]>> {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.DOCUMENTS.BASE}/signatures/pending`);
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
}

/**
 * Generates a document package for an application
 * 
 * @param options - Application ID and package type
 * @returns Promise resolving to the generated document package
 */
export async function generateDocumentPackage({
  applicationId,
  packageType
}: {
  applicationId: UUID;
  packageType: string;
}): Promise<ApiResponse<DocumentPackage>> {
  try {
    const response = await apiClient.post(API_ENDPOINTS.DOCUMENTS.GENERATE, {
      application_id: applicationId,
      package_type: packageType
    });
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
}