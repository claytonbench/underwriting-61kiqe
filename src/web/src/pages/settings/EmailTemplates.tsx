import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

// Material UI components
import { 
  Button, 
  Box, 
  Typography, 
  Chip, 
  IconButton, 
  Tooltip, 
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Snackbar,
  Alert
} from '@mui/material';

// Material UI icons
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';

// Custom components
import Page from '../../components/common/Page';
import DataTable from '../../components/common/DataTable';
import LoadingOverlay from '../../components/common/Loading';

// Hooks and API functions
import usePermissions from '../../hooks/usePermissions';
import { getNotificationTemplates, deleteNotificationTemplate } from '../../api/notifications';

// Types
import { INotificationTemplate, NotificationCategory, NotificationPriority } from '../../types/notification.types';

/**
 * Converts notification category enum value to a human-readable label
 * 
 * @param category - NotificationCategory enum value
 * @returns Human-readable label
 */
const getCategoryLabel = (category: NotificationCategory): string => {
  switch (category) {
    case NotificationCategory.APPLICATION:
      return 'Application';
    case NotificationCategory.DOCUMENT:
      return 'Document';
    case NotificationCategory.FUNDING:
      return 'Funding';
    case NotificationCategory.SYSTEM:
      return 'System';
    default:
      return category;
  }
};

/**
 * Converts notification priority enum value to a human-readable label
 * 
 * @param priority - NotificationPriority enum value
 * @returns Human-readable label
 */
const getPriorityLabel = (priority: NotificationPriority): string => {
  switch (priority) {
    case NotificationPriority.URGENT:
      return 'Urgent';
    case NotificationPriority.HIGH:
      return 'High';
    case NotificationPriority.MEDIUM:
      return 'Medium';
    case NotificationPriority.LOW:
      return 'Low';
    default:
      return priority;
  }
};

/**
 * Formats a date string into a human-readable format
 * 
 * @param dateString - ISO date string to format
 * @returns Formatted date string
 */
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

/**
 * Email Templates Management Page
 * 
 * Displays and allows management of email notification templates used throughout
 * the loan management system. System administrators can view, create, edit, and
 * delete email templates used for various notifications.
 */
const EmailTemplates: React.FC = () => {
  const navigate = useNavigate();
  const { checkPermission } = usePermissions();
  
  // State for template data and UI state
  const [templates, setTemplates] = useState<INotificationTemplate[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // State for delete confirmation dialog
  const [deleteDialogOpen, setDeleteDialogOpen] = useState<boolean>(false);
  const [templateToDelete, setTemplateToDelete] = useState<INotificationTemplate | null>(null);
  
  // State for notification feedback
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  }>({
    open: false,
    message: '',
    severity: 'success'
  });

  // Check if the user has permission to manage templates
  const canManageTemplates = checkPermission('notification:manage_templates');

  /**
   * Fetches email templates from the API
   */
  const fetchTemplates = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await getNotificationTemplates();
      
      if (response.success && response.data) {
        setTemplates(response.data);
      } else {
        setError(response.message || 'Failed to fetch notification templates');
      }
    } catch (err) {
      setError('An unexpected error occurred while fetching templates');
      console.error('Template fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load templates when component mounts
  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  /**
   * Handles creation of a new template
   */
  const handleCreateTemplate = () => {
    navigate('/settings/email-templates/create');
  };

  /**
   * Handles editing an existing template
   */
  const handleEditTemplate = (template: INotificationTemplate) => {
    navigate(`/settings/email-templates/edit/${template.id}`);
  };

  /**
   * Handles previewing a template
   */
  const handlePreviewTemplate = (template: INotificationTemplate) => {
    navigate(`/settings/email-templates/preview/${template.id}`);
  };

  /**
   * Opens delete confirmation dialog
   */
  const handleDeleteConfirmation = (template: INotificationTemplate) => {
    setTemplateToDelete(template);
    setDeleteDialogOpen(true);
  };

  /**
   * Handles actual deletion after confirmation
   */
  const handleDeleteTemplate = async () => {
    if (!templateToDelete) return;
    
    setLoading(true);
    try {
      const response = await deleteNotificationTemplate(templateToDelete.id);
      
      if (response.success) {
        setTemplates(prev => prev.filter(t => t.id !== templateToDelete.id));
        setNotification({
          open: true,
          message: 'Template deleted successfully',
          severity: 'success'
        });
      } else {
        setNotification({
          open: true,
          message: response.message || 'Failed to delete template',
          severity: 'error'
        });
      }
    } catch (err) {
      setNotification({
        open: true,
        message: 'An unexpected error occurred',
        severity: 'error'
      });
      console.error('Template delete error:', err);
    } finally {
      setLoading(false);
      setDeleteDialogOpen(false);
      setTemplateToDelete(null);
    }
  };

  /**
   * Handles closing the notification
   */
  const handleCloseNotification = () => {
    setNotification(prev => ({
      ...prev,
      open: false
    }));
  };

  // DataTable column configuration
  const columns = [
    {
      field: 'name',
      headerName: 'Template Name',
      width: '25%',
      sortable: true
    },
    {
      field: 'category',
      headerName: 'Category',
      width: '15%',
      sortable: true,
      render: (value: NotificationCategory) => (
        <Chip 
          label={getCategoryLabel(value)}
          color="primary"
          variant="outlined"
          size="small"
        />
      )
    },
    {
      field: 'priority',
      headerName: 'Priority',
      width: '15%',
      sortable: true,
      render: (value: NotificationPriority) => {
        let color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' = 'default';
        
        switch (value) {
          case NotificationPriority.URGENT:
            color = 'error';
            break;
          case NotificationPriority.HIGH:
            color = 'warning';
            break;
          case NotificationPriority.MEDIUM:
            color = 'info';
            break;
          case NotificationPriority.LOW:
            color = 'success';
            break;
        }
        
        return (
          <Chip 
            label={getPriorityLabel(value)}
            color={color}
            size="small"
          />
        );
      }
    },
    {
      field: 'isActive',
      headerName: 'Status',
      width: '10%',
      sortable: true,
      render: (value: boolean) => (
        <Chip 
          label={value ? 'Active' : 'Inactive'}
          color={value ? 'success' : 'default'}
          size="small"
        />
      )
    },
    {
      field: 'updatedAt',
      headerName: 'Last Modified',
      width: '15%',
      sortable: true,
      render: (value: string) => formatDate(value)
    },
    {
      field: 'subject',
      headerName: 'Subject',
      width: '20%',
      sortable: true
    }
  ];

  // Row actions for DataTable
  const actions = canManageTemplates ? [
    {
      icon: <VisibilityIcon />,
      label: 'Preview Template',
      onClick: handlePreviewTemplate,
      color: 'info' as const
    },
    {
      icon: <EditIcon />,
      label: 'Edit Template',
      onClick: handleEditTemplate,
      color: 'primary' as const
    },
    {
      icon: <DeleteIcon />,
      label: 'Delete Template',
      onClick: handleDeleteConfirmation,
      color: 'error' as const
    }
  ] : [
    {
      icon: <VisibilityIcon />,
      label: 'Preview Template',
      onClick: handlePreviewTemplate,
      color: 'info' as const
    }
  ];

  return (
    <Page
      title="Email Template Management"
      description="Create and manage email notification templates"
      actions={canManageTemplates && (
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleCreateTemplate}
        >
          Add Template
        </Button>
      )}
    >
      {loading && <LoadingOverlay isLoading={loading} />}
      
      {error && (
        <Box sx={{ mb: 3 }}>
          <Alert severity="error">{error}</Alert>
        </Box>
      )}

      <DataTable
        data={templates}
        columns={columns}
        actions={actions}
        loading={loading}
        emptyStateMessage="No email templates found. Create one to get started."
        pagination={templates.length > 10}
        pageSize={10}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-description"
      >
        <DialogTitle id="delete-dialog-title">
          Delete Template
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-dialog-description">
            Are you sure you want to delete the template "{templateToDelete?.name}"? 
            This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDeleteTemplate} color="error" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success/Error Notifications */}
      <Snackbar 
        open={notification.open} 
        autoHideDuration={6000} 
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseNotification} 
          severity={notification.severity}
          variant="filled"
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Page>
  );
};

export default EmailTemplates;