import React, { useState, useEffect } from 'react';
import {
  Grid,
  Typography,
  TextField,
  Button,
  Divider,
  Paper,
  Box,
  Alert,
  Tabs,
  Tab,
  Switch,
  FormControlLabel,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  FormHelperText
} from '@mui/material';
import { useSnackbar } from 'notistack';

import Page from '../../components/common/Page';
import useAuth from '../../hooks/useAuth';
import usePermissions from '../../hooks/usePermissions';
import LoadingOverlay from '../../components/common/Loading/LoadingOverlay';

// Interface for TabPanel props
interface TabPanelProps {
  children: React.ReactNode;
  value: number;
  index: number;
}

// System settings data structure
interface SystemSettingsData {
  security: SecuritySettings;
  notifications: NotificationSettings;
  defaults: DefaultSettings;
  integrations: IntegrationSettings;
}

// Security settings interface
interface SecuritySettings {
  passwordMinLength: number;
  passwordRequireUppercase: boolean;
  passwordRequireLowercase: boolean;
  passwordRequireNumbers: boolean;
  passwordRequireSpecial: boolean;
  passwordExpiryDays: number;
  sessionTimeoutMinutes: number;
  mfaEnabled: boolean;
  mfaRequiredForRoles: string[];
  loginAttempts: number;
  lockoutDurationMinutes: number;
}

// Notification settings interface
interface NotificationSettings {
  emailFromAddress: string;
  emailFromName: string;
  emailFooterText: string;
  emailLogoUrl: string;
  systemNotificationsEnabled: boolean;
  applicationNotificationsEnabled: boolean;
  documentNotificationsEnabled: boolean;
  fundingNotificationsEnabled: boolean;
}

// Default values interface
interface DefaultSettings {
  defaultPageSize: number;
  defaultCurrency: string;
  defaultLanguage: string;
  defaultDateFormat: string;
  defaultTimeFormat: string;
  defaultTimezone: string;
  documentExpirationDays: number;
  applicationRetentionDays: number;
}

// Integration settings interface
interface IntegrationSettings {
  docusignEnabled: boolean;
  docusignEnvironment: string;
  sendgridEnabled: boolean;
  sendgridEnvironment: string;
  s3Enabled: boolean;
  s3Region: string;
  s3BucketName: string;
}

// TabPanel component
const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

/**
 * System Settings page component that provides system administrators with an interface
 * to configure system-wide settings for the loan management application.
 * 
 * This page includes configurations for:
 * - Security settings (password policies, session timeouts, MFA)
 * - Notification settings (email configuration, notifications preferences)
 * - Default values (date formats, currencies, application settings)
 * - Integration settings (external service configurations)
 * 
 * The page is only accessible to users with system administration permissions.
 */
const SystemSettings: React.FC = () => {
  // Tab state
  const [activeTab, setActiveTab] = useState(0);
  
  // Settings state
  const [settings, setSettings] = useState<SystemSettingsData | null>(null);
  
  // Loading states
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  
  // Error state
  const [error, setError] = useState<string | null>(null);
  
  // Auth and permissions
  const { state: authState } = useAuth();
  const { checkPermission } = usePermissions();
  const hasAdminPermission = checkPermission('system:settings:manage');
  
  // Notifications
  const { enqueueSnackbar } = useSnackbar();

  // Handle tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Fetch settings on component mount
  useEffect(() => {
    const fetchSettings = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // This would be an actual API call in a real implementation
        // For this exercise, we'll simulate a successful API response with mock data
        const mockResponse: SystemSettingsData = {
          security: {
            passwordMinLength: 12,
            passwordRequireUppercase: true,
            passwordRequireLowercase: true,
            passwordRequireNumbers: true,
            passwordRequireSpecial: true,
            passwordExpiryDays: 90,
            sessionTimeoutMinutes: 30,
            mfaEnabled: true,
            mfaRequiredForRoles: ['SystemAdministrator', 'Underwriter', 'QualityControl'],
            loginAttempts: 5,
            lockoutDurationMinutes: 30
          },
          notifications: {
            emailFromAddress: 'no-reply@loansystem.com',
            emailFromName: 'Loan Management System',
            emailFooterText: 'This is an automated message from the Loan Management System.',
            emailLogoUrl: 'https://assets.loansystem.com/logo.png',
            systemNotificationsEnabled: true,
            applicationNotificationsEnabled: true,
            documentNotificationsEnabled: true,
            fundingNotificationsEnabled: true
          },
          defaults: {
            defaultPageSize: 10,
            defaultCurrency: 'USD',
            defaultLanguage: 'en-US',
            defaultDateFormat: 'MM/DD/YYYY',
            defaultTimeFormat: 'h:mm A',
            defaultTimezone: 'America/New_York',
            documentExpirationDays: 90,
            applicationRetentionDays: 365
          },
          integrations: {
            docusignEnabled: true,
            docusignEnvironment: 'production',
            sendgridEnabled: true,
            sendgridEnvironment: 'production',
            s3Enabled: true,
            s3Region: 'us-east-1',
            s3BucketName: 'loan-documents-production'
          }
        };
        
        // Simulate API delay
        setTimeout(() => {
          setSettings(mockResponse);
          setIsLoading(false);
        }, 1000);
      } catch (err) {
        setError('Failed to load settings. Please try again.');
        setIsLoading(false);
        console.error('Error fetching settings:', err);
      }
    };
    
    if (hasAdminPermission) {
      fetchSettings();
    } else {
      setIsLoading(false);
    }
  }, [hasAdminPermission]);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!settings) return;
    
    setIsSaving(true);
    setError(null);
    
    try {
      // This would be an actual API call in a real implementation
      // For this exercise, we'll simulate a successful API response
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      enqueueSnackbar('Settings saved successfully', { variant: 'success' });
      setIsSaving(false);
    } catch (err) {
      setError('Failed to save settings. Please try again.');
      setIsSaving(false);
      console.error('Error saving settings:', err);
    }
  };

  // Handle input changes for security settings
  const handleSecurityChange = (field: keyof SecuritySettings, value: any) => {
    if (!settings) return;
    
    setSettings({
      ...settings,
      security: {
        ...settings.security,
        [field]: value
      }
    });
  };

  // Handle input changes for notification settings
  const handleNotificationChange = (field: keyof NotificationSettings, value: any) => {
    if (!settings) return;
    
    setSettings({
      ...settings,
      notifications: {
        ...settings.notifications,
        [field]: value
      }
    });
  };

  // Handle input changes for default settings
  const handleDefaultsChange = (field: keyof DefaultSettings, value: any) => {
    if (!settings) return;
    
    setSettings({
      ...settings,
      defaults: {
        ...settings.defaults,
        [field]: value
      }
    });
  };

  // Handle input changes for integration settings
  const handleIntegrationChange = (field: keyof IntegrationSettings, value: any) => {
    if (!settings) return;
    
    setSettings({
      ...settings,
      integrations: {
        ...settings.integrations,
        [field]: value
      }
    });
  };

  // If user doesn't have permission to manage settings
  if (!hasAdminPermission) {
    return (
      <Page title="System Settings">
        <Alert severity="error">
          You do not have permission to access system settings. Please contact your administrator.
        </Alert>
      </Page>
    );
  }

  return (
    <Page title="System Settings" description="Configure system-wide settings for the loan management system">
      <LoadingOverlay isLoading={isLoading} message="Loading settings..." />
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {settings && (
        <Box component="form" onSubmit={handleSubmit}>
          <Paper sx={{ mb: 3 }}>
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              indicatorColor="primary"
              textColor="primary"
              variant="fullWidth"
              aria-label="Settings tabs"
            >
              <Tab label="Security" id="settings-tab-0" aria-controls="settings-tabpanel-0" />
              <Tab label="Notifications" id="settings-tab-1" aria-controls="settings-tabpanel-1" />
              <Tab label="Default Values" id="settings-tab-2" aria-controls="settings-tabpanel-2" />
              <Tab label="Integrations" id="settings-tab-3" aria-controls="settings-tabpanel-3" />
            </Tabs>
            
            {/* Security Settings Tab */}
            <TabPanel value={activeTab} index={0}>
              <Typography variant="h6" gutterBottom>
                Password Policy
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Minimum Password Length"
                    type="number"
                    value={settings.security.passwordMinLength}
                    onChange={(e) => handleSecurityChange('passwordMinLength', parseInt(e.target.value))}
                    inputProps={{ min: 8, max: 32 }}
                    helperText="Minimum number of characters required"
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Password Expiry (Days)"
                    type="number"
                    value={settings.security.passwordExpiryDays}
                    onChange={(e) => handleSecurityChange('passwordExpiryDays', parseInt(e.target.value))}
                    inputProps={{ min: 0, max: 365 }}
                    helperText="Number of days before password expires (0 for never)"
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.security.passwordRequireUppercase}
                        onChange={(e) => handleSecurityChange('passwordRequireUppercase', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Require Uppercase Letters"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.security.passwordRequireLowercase}
                        onChange={(e) => handleSecurityChange('passwordRequireLowercase', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Require Lowercase Letters"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.security.passwordRequireNumbers}
                        onChange={(e) => handleSecurityChange('passwordRequireNumbers', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Require Numbers"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.security.passwordRequireSpecial}
                        onChange={(e) => handleSecurityChange('passwordRequireSpecial', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Require Special Characters"
                  />
                </Grid>
              </Grid>

              <Divider sx={{ my: 3 }} />
              
              <Typography variant="h6" gutterBottom>
                Session Management
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Session Timeout (Minutes)"
                    type="number"
                    value={settings.security.sessionTimeoutMinutes}
                    onChange={(e) => handleSecurityChange('sessionTimeoutMinutes', parseInt(e.target.value))}
                    inputProps={{ min: 5, max: 240 }}
                    helperText="Minutes of inactivity before automatic logout"
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Max Login Attempts"
                    type="number"
                    value={settings.security.loginAttempts}
                    onChange={(e) => handleSecurityChange('loginAttempts', parseInt(e.target.value))}
                    inputProps={{ min: 3, max: 10 }}
                    helperText="Number of failed attempts before lockout"
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Account Lockout Duration (Minutes)"
                    type="number"
                    value={settings.security.lockoutDurationMinutes}
                    onChange={(e) => handleSecurityChange('lockoutDurationMinutes', parseInt(e.target.value))}
                    inputProps={{ min: 15, max: 1440 }}
                    helperText="Minutes before locked account can be accessed again"
                    margin="normal"
                  />
                </Grid>
              </Grid>

              <Divider sx={{ my: 3 }} />
              
              <Typography variant="h6" gutterBottom>
                Multi-Factor Authentication
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.security.mfaEnabled}
                        onChange={(e) => handleSecurityChange('mfaEnabled', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Enable Multi-Factor Authentication"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControl fullWidth margin="normal" disabled={!settings.security.mfaEnabled}>
                    <InputLabel id="mfa-required-roles-label">Required Roles for MFA</InputLabel>
                    <Select
                      labelId="mfa-required-roles-label"
                      multiple
                      value={settings.security.mfaRequiredForRoles}
                      onChange={(e) => handleSecurityChange('mfaRequiredForRoles', e.target.value)}
                      renderValue={(selected) => (selected as string[]).join(', ')}
                    >
                      <MenuItem value="SystemAdministrator">System Administrator</MenuItem>
                      <MenuItem value="Underwriter">Underwriter</MenuItem>
                      <MenuItem value="QualityControl">Quality Control</MenuItem>
                      <MenuItem value="SchoolAdministrator">School Administrator</MenuItem>
                      <MenuItem value="Borrower">Borrower</MenuItem>
                      <MenuItem value="CoBorrower">Co-Borrower</MenuItem>
                    </Select>
                    <FormHelperText>Select roles that require MFA</FormHelperText>
                  </FormControl>
                </Grid>
              </Grid>
            </TabPanel>
            
            {/* Notifications Settings Tab */}
            <TabPanel value={activeTab} index={1}>
              <Typography variant="h6" gutterBottom>
                Email Configuration
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="From Email Address"
                    type="email"
                    value={settings.notifications.emailFromAddress}
                    onChange={(e) => handleNotificationChange('emailFromAddress', e.target.value)}
                    helperText="Default sender email address"
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="From Name"
                    value={settings.notifications.emailFromName}
                    onChange={(e) => handleNotificationChange('emailFromName', e.target.value)}
                    helperText="Default sender name"
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Email Footer Text"
                    multiline
                    rows={3}
                    value={settings.notifications.emailFooterText}
                    onChange={(e) => handleNotificationChange('emailFooterText', e.target.value)}
                    helperText="Default text to appear at the bottom of all emails"
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Email Logo URL"
                    value={settings.notifications.emailLogoUrl}
                    onChange={(e) => handleNotificationChange('emailLogoUrl', e.target.value)}
                    helperText="URL for logo image in emails"
                    margin="normal"
                  />
                </Grid>
              </Grid>

              <Divider sx={{ my: 3 }} />
              
              <Typography variant="h6" gutterBottom>
                Notification Preferences
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.notifications.systemNotificationsEnabled}
                        onChange={(e) => handleNotificationChange('systemNotificationsEnabled', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="System Notifications"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.notifications.applicationNotificationsEnabled}
                        onChange={(e) => handleNotificationChange('applicationNotificationsEnabled', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Application Notifications"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.notifications.documentNotificationsEnabled}
                        onChange={(e) => handleNotificationChange('documentNotificationsEnabled', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Document Notifications"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.notifications.fundingNotificationsEnabled}
                        onChange={(e) => handleNotificationChange('fundingNotificationsEnabled', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Funding Notifications"
                  />
                </Grid>
              </Grid>
            </TabPanel>
            
            {/* Default Values Tab */}
            <TabPanel value={activeTab} index={2}>
              <Typography variant="h6" gutterBottom>
                Display Settings
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Default Page Size"
                    type="number"
                    value={settings.defaults.defaultPageSize}
                    onChange={(e) => handleDefaultsChange('defaultPageSize', parseInt(e.target.value))}
                    inputProps={{ min: 5, max: 100 }}
                    helperText="Number of items per page in lists"
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel id="currency-label">Default Currency</InputLabel>
                    <Select
                      labelId="currency-label"
                      value={settings.defaults.defaultCurrency}
                      onChange={(e) => handleDefaultsChange('defaultCurrency', e.target.value)}
                    >
                      <MenuItem value="USD">USD - US Dollar</MenuItem>
                      <MenuItem value="CAD">CAD - Canadian Dollar</MenuItem>
                      <MenuItem value="EUR">EUR - Euro</MenuItem>
                      <MenuItem value="GBP">GBP - British Pound</MenuItem>
                    </Select>
                    <FormHelperText>Default currency for monetary values</FormHelperText>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel id="language-label">Default Language</InputLabel>
                    <Select
                      labelId="language-label"
                      value={settings.defaults.defaultLanguage}
                      onChange={(e) => handleDefaultsChange('defaultLanguage', e.target.value)}
                    >
                      <MenuItem value="en-US">English (US)</MenuItem>
                      <MenuItem value="en-GB">English (UK)</MenuItem>
                      <MenuItem value="es-ES">Spanish</MenuItem>
                      <MenuItem value="fr-FR">French</MenuItem>
                    </Select>
                    <FormHelperText>Default language for the application</FormHelperText>
                  </FormControl>
                </Grid>
              </Grid>

              <Divider sx={{ my: 3 }} />
              
              <Typography variant="h6" gutterBottom>
                Date and Time Settings
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel id="date-format-label">Default Date Format</InputLabel>
                    <Select
                      labelId="date-format-label"
                      value={settings.defaults.defaultDateFormat}
                      onChange={(e) => handleDefaultsChange('defaultDateFormat', e.target.value)}
                    >
                      <MenuItem value="MM/DD/YYYY">MM/DD/YYYY</MenuItem>
                      <MenuItem value="DD/MM/YYYY">DD/MM/YYYY</MenuItem>
                      <MenuItem value="YYYY-MM-DD">YYYY-MM-DD</MenuItem>
                      <MenuItem value="MMM D, YYYY">MMM D, YYYY</MenuItem>
                    </Select>
                    <FormHelperText>Default format for date display</FormHelperText>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel id="time-format-label">Default Time Format</InputLabel>
                    <Select
                      labelId="time-format-label"
                      value={settings.defaults.defaultTimeFormat}
                      onChange={(e) => handleDefaultsChange('defaultTimeFormat', e.target.value)}
                    >
                      <MenuItem value="h:mm A">12-hour (1:30 PM)</MenuItem>
                      <MenuItem value="HH:mm">24-hour (13:30)</MenuItem>
                    </Select>
                    <FormHelperText>Default format for time display</FormHelperText>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel id="timezone-label">Default Timezone</InputLabel>
                    <Select
                      labelId="timezone-label"
                      value={settings.defaults.defaultTimezone}
                      onChange={(e) => handleDefaultsChange('defaultTimezone', e.target.value)}
                    >
                      <MenuItem value="America/New_York">Eastern Time (ET)</MenuItem>
                      <MenuItem value="America/Chicago">Central Time (CT)</MenuItem>
                      <MenuItem value="America/Denver">Mountain Time (MT)</MenuItem>
                      <MenuItem value="America/Los_Angeles">Pacific Time (PT)</MenuItem>
                      <MenuItem value="UTC">UTC</MenuItem>
                    </Select>
                    <FormHelperText>Default timezone for date/time display</FormHelperText>
                  </FormControl>
                </Grid>
              </Grid>

              <Divider sx={{ my: 3 }} />
              
              <Typography variant="h6" gutterBottom>
                Application Settings
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Document Expiration Days"
                    type="number"
                    value={settings.defaults.documentExpirationDays}
                    onChange={(e) => handleDefaultsChange('documentExpirationDays', parseInt(e.target.value))}
                    inputProps={{ min: 30, max: 180 }}
                    helperText="Days before documents expire"
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Application Retention Days"
                    type="number"
                    value={settings.defaults.applicationRetentionDays}
                    onChange={(e) => handleDefaultsChange('applicationRetentionDays', parseInt(e.target.value))}
                    inputProps={{ min: 90, max: 3650 }}
                    helperText="Days to retain applications"
                    margin="normal"
                  />
                </Grid>
              </Grid>
            </TabPanel>
            
            {/* Integrations Tab */}
            <TabPanel value={activeTab} index={3}>
              <Typography variant="h6" gutterBottom>
                DocuSign Integration
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.integrations.docusignEnabled}
                        onChange={(e) => handleIntegrationChange('docusignEnabled', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Enable DocuSign Integration"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal" disabled={!settings.integrations.docusignEnabled}>
                    <InputLabel id="docusign-env-label">DocuSign Environment</InputLabel>
                    <Select
                      labelId="docusign-env-label"
                      value={settings.integrations.docusignEnvironment}
                      onChange={(e) => handleIntegrationChange('docusignEnvironment', e.target.value)}
                    >
                      <MenuItem value="demo">Demo/Sandbox</MenuItem>
                      <MenuItem value="production">Production</MenuItem>
                    </Select>
                    <FormHelperText>Select DocuSign environment</FormHelperText>
                  </FormControl>
                </Grid>
              </Grid>

              <Divider sx={{ my: 3 }} />
              
              <Typography variant="h6" gutterBottom>
                SendGrid Integration
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.integrations.sendgridEnabled}
                        onChange={(e) => handleIntegrationChange('sendgridEnabled', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Enable SendGrid Integration"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal" disabled={!settings.integrations.sendgridEnabled}>
                    <InputLabel id="sendgrid-env-label">SendGrid Environment</InputLabel>
                    <Select
                      labelId="sendgrid-env-label"
                      value={settings.integrations.sendgridEnvironment}
                      onChange={(e) => handleIntegrationChange('sendgridEnvironment', e.target.value)}
                    >
                      <MenuItem value="test">Test</MenuItem>
                      <MenuItem value="production">Production</MenuItem>
                    </Select>
                    <FormHelperText>Select SendGrid environment</FormHelperText>
                  </FormControl>
                </Grid>
              </Grid>

              <Divider sx={{ my: 3 }} />
              
              <Typography variant="h6" gutterBottom>
                AWS S3 Storage
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.integrations.s3Enabled}
                        onChange={(e) => handleIntegrationChange('s3Enabled', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Enable S3 Storage Integration"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="S3 Region"
                    value={settings.integrations.s3Region}
                    onChange={(e) => handleIntegrationChange('s3Region', e.target.value)}
                    disabled={!settings.integrations.s3Enabled}
                    helperText="AWS region for S3 bucket"
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="S3 Bucket Name"
                    value={settings.integrations.s3BucketName}
                    onChange={(e) => handleIntegrationChange('s3BucketName', e.target.value)}
                    disabled={!settings.integrations.s3Enabled}
                    helperText="S3 bucket for document storage"
                    margin="normal"
                  />
                </Grid>
              </Grid>
            </TabPanel>
          </Paper>
          
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              color="primary"
              type="submit"
              disabled={isSaving}
              sx={{ ml: 1 }}
            >
              {isSaving ? 'Saving...' : 'Save Settings'}
            </Button>
          </Box>
          
          <LoadingOverlay isLoading={isSaving} message="Saving settings..." />
        </Box>
      )}
    </Page>
  );
};

export default SystemSettings;