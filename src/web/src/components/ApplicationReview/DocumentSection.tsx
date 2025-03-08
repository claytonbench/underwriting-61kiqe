import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import GetAppIcon from '@mui/icons-material/GetApp';

import useStyles from './styles';
import { Document, DocumentType, DocumentStatus } from '../../types/document.types';
import { LoanApplication } from '../../types/application.types';
import { getApplicationDocuments, downloadDocument } from '../../api/documents';
import { formatDate } from '../../utils/date';

interface DocumentSectionProps {
  application: LoanApplication;
  readOnly?: boolean;
}

const DocumentSection: React.FC<DocumentSectionProps> = ({ application, readOnly = false }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [downloadingDocId, setDownloadingDocId] = useState<string | null>(null);
  
  const classes = useStyles();
  
  // Format document type for display (e.g., "commitment_letter" → "Commitment Letter")
  const formatDocumentType = (type: string): string => {
    return type
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  };

  // Get status style class based on document status
  const getStatusClass = (status: string): string => {
    switch (status) {
      case DocumentStatus.COMPLETED:
        return classes.statusSigned;
      case DocumentStatus.GENERATED:
      case DocumentStatus.DRAFT:
        return classes.statusUploaded;
      case DocumentStatus.EXPIRED:
      case DocumentStatus.REJECTED:
      case DocumentStatus.ERROR:
        return classes.statusMissing;
      case DocumentStatus.PENDING_SIGNATURE:
      case DocumentStatus.PARTIALLY_SIGNED:
      default:
        return '';
    }
  };

  // Format status for display (e.g., "pending_signature" → "Pending Signature")
  const formatStatus = (status: string): string => {
    return status
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  };
  
  // Fetch documents when the component mounts or when the application changes
  const fetchDocuments = useCallback(async () => {
    if (!application?.id) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await getApplicationDocuments(application.id);
      if (response.success) {
        setDocuments(response.data || []);
      } else {
        setError(response.message || 'Failed to fetch documents');
      }
    } catch (err) {
      setError('An unexpected error occurred while fetching documents');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [application?.id]);
  
  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);
  
  // Handle document viewing (opens in new tab)
  const handleViewDocument = useCallback(async (document: Document) => {
    if (document.status === DocumentStatus.ERROR) {
      console.error('Cannot view document with error status');
      return;
    }
    
    if (document.download_url) {
      window.open(document.download_url, '_blank');
    } else {
      try {
        const response = await downloadDocument(document.id);
        if (response.success && response.data?.download_url) {
          window.open(response.data.download_url, '_blank');
        }
      } catch (err) {
        console.error('Error viewing document:', err);
      }
    }
  }, []);
  
  // Handle document download
  const handleDownloadDocument = useCallback(async (document: Document) => {
    if (document.status === DocumentStatus.ERROR) {
      console.error('Cannot download document with error status');
      return;
    }
    
    setDownloadingDocId(document.id);
    
    try {
      const response = await downloadDocument(document.id);
      if (response.success && response.data?.download_url) {
        // Create a temporary anchor element and trigger download
        const link = document.createElement('a');
        link.href = response.data.download_url;
        link.setAttribute('download', document.file_name);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (err) {
      console.error('Error downloading document:', err);
    } finally {
      setDownloadingDocId(null);
    }
  }, []);
  
  // Render loading state
  if (loading) {
    return (
      <Card>
        <CardHeader title="Documents" />
        <CardContent className={classes.loadingContainer}>
          <CircularProgress />
          <Typography variant="body2" style={{ marginTop: 16 }}>
            Loading documents...
          </Typography>
        </CardContent>
      </Card>
    );
  }
  
  // Render error state
  if (error) {
    return (
      <Card>
        <CardHeader title="Documents" />
        <CardContent>
          <div className={classes.errorContainer}>
            <Typography variant="body1">{error}</Typography>
            <Button 
              variant="outlined" 
              color="primary" 
              onClick={fetchDocuments} 
              style={{ marginTop: 16 }}
            >
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  // Render empty state
  if (documents.length === 0) {
    return (
      <Card>
        <CardHeader title="Documents" />
        <CardContent>
          <Typography variant="body1" align="center" style={{ padding: 24 }}>
            No documents have been uploaded for this application.
          </Typography>
        </CardContent>
      </Card>
    );
  }
  
  // Render document table
  return (
    <Card>
      <CardHeader title="Documents" />
      <CardContent>
        <TableContainer>
          <Table className={classes.documentTable}>
            <TableHead>
              <TableRow>
                <TableCell>Type</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {documents.map((document) => (
                <TableRow key={document.id}>
                  <TableCell>{formatDocumentType(document.document_type)}</TableCell>
                  <TableCell>{document.file_name}</TableCell>
                  <TableCell>
                    <Chip 
                      label={formatStatus(document.status)}
                      className={getStatusClass(document.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{formatDate(document.generated_at, 'MM/DD/YYYY')}</TableCell>
                  <TableCell>
                    <div className={classes.documentActions}>
                      <Button
                        size="small"
                        startIcon={<VisibilityIcon />}
                        onClick={() => handleViewDocument(document)}
                        disabled={readOnly || document.status === DocumentStatus.ERROR}
                      >
                        View
                      </Button>
                      <Button
                        size="small"
                        startIcon={
                          downloadingDocId === document.id ? (
                            <CircularProgress size={20} />
                          ) : (
                            <GetAppIcon />
                          )
                        }
                        onClick={() => handleDownloadDocument(document)}
                        disabled={
                          downloadingDocId === document.id || 
                          readOnly || 
                          document.status === DocumentStatus.ERROR
                        }
                      >
                        Download
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
};

export default DocumentSection;