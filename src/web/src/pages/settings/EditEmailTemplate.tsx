import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  TextField,
  Button,
  Grid,
  FormControl,
  FormHelperText,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Typography,
  Box,
  Paper,
  Divider,
  Snackbar,
  Alert
} from '@mui/material';
import Page from '../../components/common/Page';
import LoadingOverlay from '../../components/common/Loading';
import usePermissions from '../../hooks/usePermissions';
import useForm from '../../hooks/useForm';
import {
  getNotificationTemplateById,
  createNotificationTemplate,
  updateNotificationTemplate,
  previewNotificationTemplate
} from '../../api/notifications';
import {
  INotificationTemplate,
  NotificationCategory,
  NotificationPriority
} from '../../types/notification.types';

/**
 * Converts notification category enum value to a human-readable label
 * 
 * @param category - The notification category enum value
 * @returns Human-readable label for the category
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
 * @param priority - The notification priority enum value
 * @returns Human-readable label for the priority
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
 * Component for creating or editing email notification templates
 * 
 * This page allows system administrators to create new email templates or modify existing ones.
 * It provides form fields for template details, a content editor with variable placeholders,
 * and preview functionality to test how the template will render with data.
 * 
 * @returns Rendered email template edit page
 */
const EditEmailTemplate: React.FC = () => {
  const { templateId } = useParams<{ templateId: string }>();
  const navigate = useNavigate();
  const isEditMode = !!templateId;
  
  // State
  const [loading, setLoading] = useState<boolean>(false);
  const [preview, setPreview] = useState<{ subject: string; body: string } | null>(null);
  const [notification, setNotification] = useState<{ open: boolean; message: string; type: 'success' | 'error' }>({
    open: false,
    message: '',
    type: 'success'
  });
  
  // Common template variables that can be used in templates
  const [templateVariables] = useState<{ name: string; description: string }[]>([
    { name: '{{applicant_name}}', description: "Applicant's full name" },
    { name: '{{application_id}}', description: "Application ID" },
    { name: '{{school_name}}', description: "School name" },
    { name: '{{program_name}}', description: "Program name" },
    { name: '{{approved_amount}}', description: "Approved loan amount" },
    { name: '{{document_link}}', description: "Link to documents" },
    { name: '{{start_date}}', description: "Program start date" },
    { name: '{{decision_date}}', description: "Application decision date" },
    { name: '{{due_date}}', description: "Action due date if applicable" }
  ]);
  
  // Check permissions
  const { checkPermission } = usePermissions();
  const canManageTemplates = checkPermission('notification:manage_templates');
  
  // Form validation schema
  const validationSchema = {
    name: {
      validate: (value: string) => !!value && value.trim().length > 0,
      errorMessage: 'Template name is required'
    },
    subject: {
      validate: (value: string) => !!value && value.trim().length > 0,
      errorMessage: 'Subject line is required'
    },
    bodyTemplate: {
      validate: (value: string) => !!value && value.trim().length > 0,
      errorMessage: 'Email content is required'
    }
  };
  
  // Empty template for form initialization
  const emptyTemplate: Omit<INotificationTemplate, 'id' | 'createdAt' | 'updatedAt'> = {
    name: '',
    description: '',
    subject: '',
    bodyTemplate: '',
    category: NotificationCategory.APPLICATION,
    priority: NotificationPriority.MEDIUM,
    isActive: true
  };
  
  // Initialize form
  const form = useForm(
    emptyTemplate,
    validationSchema,
    handleSubmit
  );
  
  // Fetch template data if in edit mode
  useEffect(() => {
    const fetchTemplateData = async () => {
      if (!isEditMode || !templateId) return;
      
      setLoading(true);
      try {
        const response = await getNotificationTemplateById(templateId);
        if (response.success && response.data) {
          // Update form values with template data
          Object.keys(response.data).forEach(key => {
            if (key in form.values) {
              form.setFieldValue(key, response.data[key]);
            }
          });
        } else {
          setNotification({
            open: true,
            message: response.message || 'Failed to fetch template data',
            type: 'error'
          });
        }
      } catch (error) {
        console.error('Error fetching template:', error);
        setNotification({
          open: true,
          message: 'An unexpected error occurred while fetching template data',
          type: 'error'
        });
      } finally {
        setLoading(false);
      }
    };
    
    fetchTemplateData();
  }, [templateId, isEditMode]);
  
  // Handle form submission
  async function handleSubmit(values: Record<string, any>) {
    if (!canManageTemplates) {
      setNotification({
        open: true,
        message: 'You do not have permission to manage notification templates',
        type: 'error'
      });
      return;
    }
    
    setLoading(true);
    try {
      const templateData = values as Omit<INotificationTemplate, 'id' | 'createdAt' | 'updatedAt'>;
      let response;
      
      if (isEditMode && templateId) {
        // Update existing template
        response = await updateNotificationTemplate(templateId, templateData);
      } else {
        // Create new template
        response = await createNotificationTemplate(templateData);
      }
      
      if (response.success) {
        setNotification({
          open: true,
          message: `Template ${isEditMode ? 'updated' : 'created'} successfully`,
          type: 'success'
        });
        
        // Redirect to templates list after successful submission
        setTimeout(() => {
          navigate('/settings/email-templates');
        }, 1500);
      } else {
        setNotification({
          open: true,
          message: response.message || `Failed to ${isEditMode ? 'update' : 'create'} template`,
          type: 'error'
        });
      }
    } catch (error) {
      console.error(`Error ${isEditMode ? 'updating' : 'creating'} template:`, error);
      setNotification({
        open: true,
        message: `An unexpected error occurred while ${isEditMode ? 'updating' : 'creating'} the template`,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  }
  
  // Generate template preview
  const handlePreviewClick = async () => {
    setLoading(true);
    try {
      // Sample data for preview
      const sampleData = {
        applicant_name: 'John Smith',
        application_id: 'APP-1001',
        school_name: 'ABC School',
        program_name: 'Web Development',
        approved_amount: '$10,000',
        document_link: 'https://example.com/documents/1234',
        start_date: '06/01/2023',
        decision_date: '05/15/2023',
        due_date: '05/30/2023'
      };
      
      let response;
      
      if (isEditMode && templateId) {
        // Preview existing template with sample data
        response = await previewNotificationTemplate(templateId, sampleData);
      } else {
        // Preview new template with current values and sample data
        response = await previewNotificationTemplate(
          'preview', // Special endpoint for previewing unsaved templates
          {
            template: form.values.bodyTemplate,
            subject: form.values.subject,
            sampleData
          }
        );
      }
      
      if (response.success && response.data) {
        setPreview(response.data);
      } else {
        setNotification({
          open: true,
          message: response.message || 'Failed to generate preview',
          type: 'error'
        });
      }
    } catch (error) {
      console.error('Error generating preview:', error);
      setNotification({
        open: true,
        message: 'An unexpected error occurred while generating preview',
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  // If user doesn't have permission, show unauthorized message
  if (!canManageTemplates) {
    return (
      <Page title="Unauthorized">
        <Typography variant="h6" color="error">
          You do not have permission to manage notification templates.
        </Typography>
      </Page>
    );
  }
  
  return (
    <Page
      title={`${isEditMode ? 'Edit' : 'Create'} Email Template`}
      actions={
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            onClick={() => navigate('/settings/email-templates')}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={() => form.handleSubmit()}
            disabled={loading || !form.isValid}
          >
            {isEditMode ? 'Save Changes' : 'Create Template'}
          </Button>
        </Box>
      }
    >
      <LoadingOverlay isLoading={loading} message={isEditMode ? "Loading template data..." : "Processing..."} />
      
      <Grid container spacing={3}>
        {/* Template Details */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Template Details
          </Typography>
          <Divider sx={{ mb: 2 }} />
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                name="name"
                label="Template Name"
                fullWidth
                value={form.values.name}
                onChange={form.handleChange}
                onBlur={form.handleBlur}
                error={!!form.touched.name && !!form.errors.name}
                helperText={form.touched.name && form.errors.name}
                required
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                name="subject"
                label="Subject Line"
                fullWidth
                value={form.values.subject}
                onChange={form.handleChange}
                onBlur={form.handleBlur}
                error={!!form.touched.subject && !!form.errors.subject}
                helperText={form.touched.subject && form.errors.subject}
                required
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="category-label">Category</InputLabel>
                <Select
                  labelId="category-label"
                  name="category"
                  value={form.values.category}
                  onChange={form.handleChange}
                  label="Category"
                >
                  {Object.values(NotificationCategory).map((category) => (
                    <MenuItem key={category} value={category}>
                      {getCategoryLabel(category)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="priority-label">Priority</InputLabel>
                <Select
                  labelId="priority-label"
                  name="priority"
                  value={form.values.priority}
                  onChange={form.handleChange}
                  label="Priority"
                >
                  {Object.values(NotificationPriority).map((priority) => (
                    <MenuItem key={priority} value={priority}>
                      {getPriorityLabel(priority)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                name="description"
                label="Description"
                fullWidth
                multiline
                rows={2}
                value={form.values.description}
                onChange={form.handleChange}
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    name="isActive"
                    checked={form.values.isActive}
                    onChange={form.handleChange}
                    color="primary"
                  />
                }
                label="Active"
              />
              <FormHelperText>
                Inactive templates will not be used for sending notifications
              </FormHelperText>
            </Grid>
          </Grid>
        </Grid>
        
        {/* Available Variables */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Available Variables
          </Typography>
          <Divider sx={{ mb: 2 }} />
          
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              You can use the following variables in your template. They will be replaced with actual values when the email is sent.
            </Typography>
            
            <Grid container spacing={2} sx={{ mt: 1 }}>
              {templateVariables.map((variable) => (
                <Grid item xs={12} sm={6} md={4} key={variable.name}>
                  <Paper
                    sx={{
                      p: 1,
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      backgroundColor: 'background.default'
                    }}
                  >
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 'bold' }}>
                      {variable.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {variable.description}
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Box>
        </Grid>
        
        {/* Template Content */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Template Content
          </Typography>
          <Divider sx={{ mb: 2 }} />
          
          <TextField
            name="bodyTemplate"
            label="Email Content"
            fullWidth
            multiline
            rows={10}
            value={form.values.bodyTemplate}
            onChange={form.handleChange}
            onBlur={form.handleBlur}
            error={!!form.touched.bodyTemplate && !!form.errors.bodyTemplate}
            helperText={
              (form.touched.bodyTemplate && form.errors.bodyTemplate) ||
              "Enter the email content using HTML formatting and variable placeholders."
            }
            required
          />
          
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="outlined"
              onClick={handlePreviewClick}
              disabled={loading || !form.values.bodyTemplate}
            >
              Preview
            </Button>
          </Box>
        </Grid>
        
        {/* Preview Section */}
        {preview && (
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Preview
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Paper sx={{ p: 3, bgcolor: 'background.default' }}>
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                Subject: {preview.subject}
              </Typography>
              
              <Divider sx={{ my: 1 }} />
              
              <Box
                sx={{ mt: 2 }}
                dangerouslySetInnerHTML={{ __html: preview.body }}
              />
            </Paper>
          </Grid>
        )}
      </Grid>
      
      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setNotification({ ...notification, open: false })}
          severity={notification.type}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Page>
  );
};

export default EditEmailTemplate;