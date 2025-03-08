import React, { useState, useEffect, useMemo, useCallback } from 'react'; // react v18.2.0
import { useDispatch, useSelector } from 'react-redux'; // react-redux v8.1.0
import { useNavigate } from 'react-router-dom'; // react-router-dom v6.14.0
import { Box, Button, Typography, Tooltip, IconButton } from '@mui/material'; // mui/material v5.14.0
import { DownloadOutlined, VisibilityOutlined, DeleteOutlined, FilterAlt } from '@mui/icons-material'; // mui/icons-material v5.14.0

import Page from '../../components/common/Page';
import DataTable from '../../components/common/DataTable';
import StatusBadge from '../../components/common/StatusBadge';
import {
  DocumentType,
  DocumentStatus,
  DocumentListItem,
  DocumentFilters,
  DocumentSortField,
  DocumentSortDirection,
} from '../../types/document.types';
import { SortDirection } from '../../types/common.types';
import {
  fetchDocuments,
  getDocumentDownloadUrl,
} from '../../store/thunks/documentThunks';
import {
  setDocumentFilters,
  setDocumentSort,
  setDocumentPage,
  setDocumentPageSize,
} from '../../store/slices/documentSlice';
import { usePermissions } from '../../hooks/usePermissions';
import { formatDate } from '../../utils/formatting';

/**
 * Main component that renders the document list page
 * @returns Rendered document list page
 */
const DocumentList: React.FC = () => {
  // Initialize navigation with useNavigate hook
  const navigate = useNavigate();

  // Initialize Redux dispatch with useDispatch hook
  const dispatch = useDispatch();

  // Get document state from Redux store using useSelector hook
  const {
    documents,
    loading,
    totalDocuments,
    documentFilters,
    documentSort,
    documentPage,
    documentPageSize,
  } = useSelector((state: any) => state.document);

  // Get user permissions using usePermissions hook
  const { checkPermission } = usePermissions();

  // Define table columns configuration with appropriate headers and cell renderers
  const columns = useMemo(
    () => [
      {
        field: 'document_type',
        headerName: 'Document Type',
        width: 200,
        sortable: true,
        render: (type: DocumentType) => renderDocumentTypeCell(type),
      },
      {
        field: 'file_name',
        headerName: 'File Name',
        width: 300,
        sortable: true,
      },
      {
        field: 'status',
        headerName: 'Status',
        width: 150,
        sortable: true,
        render: (status: DocumentStatus) => renderStatusCell(status),
      },
      {
        field: 'generated_at',
        headerName: 'Generated At',
        width: 150,
        sortable: true,
        render: (dateString: string) => renderDateCell(dateString),
      },
      {
        field: 'borrower_name',
        headerName: 'Borrower',
        width: 200,
        sortable: true,
      },
      {
        field: 'school_name',
        headerName: 'School',
        width: 200,
        sortable: true,
      },
    ],
    []
  );

  // Define table actions for view, download, and delete operations
  const actions = useMemo(
    () => [
      {
        icon: <VisibilityOutlined />,
        label: 'View',
        onClick: (document: DocumentListItem) => handleViewDocument(document),
        isVisible: () => checkPermission('document:view'),
      },
      {
        icon: <DownloadOutlined />,
        label: 'Download',
        onClick: (document: DocumentListItem) => handleDownloadDocument(document),
        isVisible: () => checkPermission('document:download'),
      },
      {
        icon: <DeleteOutlined />,
        label: 'Delete',
        onClick: (document: DocumentListItem) => {
          // Implement delete logic here
          console.log('Delete document:', document);
        },
        isVisible: () => checkPermission('document:delete'),
      },
    ],
    [checkPermission]
  );

  // Define filter options for document type and status
  const filterConfig = useMemo(
    () => [
      {
        field: 'document_type',
        label: 'Document Type',
        type: 'select',
        options: Object.values(DocumentType).map((type) => ({
          value: type,
          label: type.replace(/_/g, ' '),
        })),
      },
      {
        field: 'status',
        label: 'Status',
        type: 'select',
        options: Object.values(DocumentStatus).map((status) => ({
          value: status,
          label: status.replace(/_/g, ' '),
        })),
      },
    ],
    []
  );

  /**
   * Handles page change events from the DataTable pagination
   * @param page The new page number
   * @returns void No return value
   */
  const handlePageChange = useCallback(
    (page: number) => {
      dispatch(setDocumentPage(page));
    },
    [dispatch]
  );

  /**
   * Handles page size change events from the DataTable pagination
   * @param pageSize The new page size
   * @returns void No return value
   */
  const handlePageSizeChange = useCallback(
    (pageSize: number) => {
      dispatch(setDocumentPageSize(pageSize));
    },
    [dispatch]
  );

  /**
   * Handles sort change events from the DataTable
   * @param field The field to sort by
   * @param direction The sort direction
   * @returns void No return value
   */
  const handleSortChange = useCallback(
    (field: string, direction: SortDirection) => {
      dispatch(
        setDocumentSort({
          field: field as DocumentSortField,
          direction,
        })
      );
    },
    [dispatch]
  );

  /**
   * Handles filter change events from the DataTable
   * @param filters The new filter options
   * @returns void No return value
   */
  const handleFilterChange = useCallback(
    (filters: any) => {
      const documentFilters: DocumentFilters = {
        document_type: filters.document_type || null,
        status: filters.status || null,
        application_id: filters.application_id || null,
        package_id: filters.package_id || null,
        date_range: filters.date_range || { start: null, end: null },
        search: filters.search || null,
      };
      dispatch(setDocumentFilters(documentFilters));
    },
    [dispatch]
  );

  /**
   * Handles view document action
   * @param document The document to view
   * @returns void No return value
   */
  const handleViewDocument = useCallback(
    (document: DocumentListItem) => {
      navigate(`/documents/${document.id}`);
    },
    [navigate]
  );

  /**
   * Handles download document action
   * @param document The document to download
   * @returns void No return value
   */
  const handleDownloadDocument = useCallback(
    (document: DocumentListItem) => {
      dispatch(getDocumentDownloadUrl(document.id)).then((action: any) => {
        if (action.payload && action.payload.download_url) {
          window.open(action.payload.download_url, '_blank');
        }
      });
    },
    [dispatch]
  );

  /**
   * Renders the document type cell with appropriate formatting
   * @param type The document type
   * @returns Rendered document type cell
   */
  const renderDocumentTypeCell = useCallback((type: DocumentType) => {
    const formattedType = type.replace(/_/g, ' ');
    return <Typography>{formattedType}</Typography>;
  }, []);

  /**
   * Renders the document status cell with StatusBadge
   * @param status The document status
   * @returns Rendered status cell with StatusBadge
   */
  const renderStatusCell = useCallback((status: DocumentStatus) => {
    return <StatusBadge status={status} />;
  }, []);

  /**
   * Renders a date cell with formatted date
   * @param dateString The date string
   * @returns Rendered date cell
   */
  const renderDateCell = useCallback((dateString: string) => {
    return <Typography>{formatDate(dateString)}</Typography>;
  }, []);

  // Fetch documents on component mount and when filters, sort, or pagination changes
  useEffect(() => {
    dispatch(
      fetchDocuments({
        page: documentPage,
        pageSize: documentPageSize,
        filters: documentFilters,
        sort: documentSort,
      })
    );
  }, [dispatch, documentPage, documentPageSize, documentFilters, documentSort]);

  // Render Page component with appropriate title and actions
  return (
    <Page
      title="Documents"
      description="View and manage all documents in the system"
      actions={
        <Tooltip title="Filter Documents">
          <IconButton color="primary">
            <FilterAlt />
          </IconButton>
        </Tooltip>
      }
    >
      {/* Render DataTable component with documents data, columns, actions, and event handlers */}
      <DataTable
        data={documents}
        columns={columns}
        loading={loading}
        emptyStateMessage="No documents found"
        actions={actions}
        pagination
        page={documentPage}
        pageSize={documentPageSize}
        totalItems={totalDocuments}
        onPageChange={handlePageChange}
        onPageSizeChange={handlePageSizeChange}
        sorting
        sortField={documentSort?.field}
        sortDirection={documentSort?.direction}
        onSortChange={handleSortChange}
        filtering
        filterOptions={documentFilters}
        filterConfig={filterConfig}
        onFilterChange={handleFilterChange}
      />
    </Page>
  );
};

export default DocumentList;