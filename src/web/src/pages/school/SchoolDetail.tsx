import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  Grid,
  Typography,
  Button,
  Chip,
  Divider,
  Card,
  CardContent,
  CardHeader,
  Box,
  Tab,
  Tabs,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Edit,
  Add,
  ArrowBack,
  School,
  Person,
  Description,
  Phone,
  Language,
  LocationOn,
  Email
} from '@mui/icons-material';

// Internal imports
import Page from '../../components/common/Page';
import DataTable from '../../components/common/DataTable';
import {
  fetchSchoolById,
  fetchProgramsBySchool,
  fetchSchoolContacts,
  selectSelectedSchool,
  selectPrograms,
  selectSchoolLoading,
  selectSchoolError
} from '../../store/slices/schoolSlice';
import {
  formatCurrency,
  formatPhoneNumber
} from '../../utils/formatting';
import { SchoolStatus, ProgramStatus, Program } from '../../types/school.types';

/**
 * SchoolDetail component displays detailed information about a school entity,
 * including its basic information, programs, contacts, and documents.
 * It provides actions to edit the school, add programs, and manage school contacts.
 *
 * @returns JSX.Element - Rendered school detail page
 */
const SchoolDetail: React.FC = () => {
  // Get the schoolId from URL parameters
  const { schoolId } = useParams<{ schoolId: string }>();
  
  // Redux hooks
  const dispatch = useDispatch();
  const school = useSelector(selectSelectedSchool);
  const programs = useSelector(selectPrograms);
  const loading = useSelector(selectSchoolLoading);
  const error = useSelector(selectSchoolError);
  
  // Local state
  const [activeTab, setActiveTab] = useState(0);
  
  // Navigation
  const navigate = useNavigate();

  // Fetch school details and related data when component mounts or schoolId changes
  useEffect(() => {
    if (schoolId) {
      dispatch(fetchSchoolById(schoolId));
      dispatch(fetchProgramsBySchool({ 
        schoolId, 
        page: 1, 
        pageSize: 100, 
        filters: { school_id: schoolId, status: null, name: null } 
      }));
      dispatch(fetchSchoolContacts(schoolId));
    }
  }, [dispatch, schoolId]);

  /**
   * Handles tab selection changes
   */
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  /**
   * Navigates to the school edit page
   */
  const handleEditSchool = () => {
    navigate(`/schools/edit/${schoolId}`);
  };

  /**
   * Navigates to the new program page with the school pre-selected
   */
  const handleAddProgram = () => {
    navigate(`/programs/new?schoolId=${schoolId}`);
  };

  /**
   * Navigates to the program detail page when a program row is clicked
   */
  const handleProgramClick = (program: Program) => {
    navigate(`/programs/${program.id}`);
  };

  /**
   * Navigates back to the school list page
   */
  const handleBackToList = () => {
    navigate('/schools');
  };

  /**
   * Returns a styled Chip component for displaying status
   * @param status - The status value to display
   * @returns JSX.Element - A Chip component with appropriate styling
   */
  const getStatusChip = (status: SchoolStatus | ProgramStatus): JSX.Element => {
    let color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' = 'default';
    
    switch(status) {
      case SchoolStatus.ACTIVE:
      case ProgramStatus.ACTIVE:
        color = 'success';
        break;
      case SchoolStatus.INACTIVE:
      case ProgramStatus.INACTIVE:
        color = 'error';
        break;
      case SchoolStatus.PENDING:
        color = 'warning';
        break;
      case SchoolStatus.REJECTED:
        color = 'error';
        break;
      default:
        color = 'default';
    }
    
    return (
      <Chip 
        label={status.replace('_', ' ').toUpperCase()} 
        color={color} 
        size="small" 
      />
    );
  };

  /**
   * Renders the school information section
   * @returns JSX.Element | null - The rendered school information or null if school data is not loaded
   */
  const renderSchoolInfo = (): JSX.Element | null => {
    if (!school) return null;
    
    return (
      <Card sx={{ mb: 3 }}>
        <CardHeader 
          title={
            <Box display="flex" alignItems="center" gap={1}>
              <School color="primary" />
              <Typography variant="h6">School Information</Typography>
            </Box>
          }
          action={
            <Tooltip title="Edit School">
              <IconButton onClick={handleEditSchool} aria-label="Edit school">
                <Edit />
              </IconButton>
            </Tooltip>
          }
        />
        <Divider />
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="textSecondary">
                School Name
              </Typography>
              <Typography variant="body1">{school.name}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="textSecondary">
                Status
              </Typography>
              {getStatusChip(school.status)}
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="textSecondary">
                Legal Name
              </Typography>
              <Typography variant="body1">{school.legal_name}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="textSecondary">
                Tax ID
              </Typography>
              <Typography variant="body1">{school.tax_id}</Typography>
            </Grid>
            
            <Grid item xs={12}>
              <Divider sx={{ my: 1 }} />
            </Grid>
            
            <Grid item xs={12}>
              <Box display="flex" alignItems="center" gap={1}>
                <LocationOn color="primary" fontSize="small" />
                <Typography variant="subtitle2" color="textSecondary">
                  Address
                </Typography>
              </Box>
              <Typography variant="body1">{school.address_line1}</Typography>
              {school.address_line2 && (
                <Typography variant="body1">{school.address_line2}</Typography>
              )}
              <Typography variant="body1">
                {school.city}, {school.state} {school.zip_code}
              </Typography>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <Box display="flex" alignItems="center" gap={1}>
                <Phone color="primary" fontSize="small" />
                <Typography variant="subtitle2" color="textSecondary">
                  Phone
                </Typography>
              </Box>
              <Typography variant="body1">{formatPhoneNumber(school.phone)}</Typography>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <Box display="flex" alignItems="center" gap={1}>
                <Language color="primary" fontSize="small" />
                <Typography variant="subtitle2" color="textSecondary">
                  Website
                </Typography>
              </Box>
              <Typography variant="body1">
                <a href={school.website} target="_blank" rel="noopener noreferrer">
                  {school.website}
                </a>
              </Typography>
            </Grid>
            
            {school.application_count !== undefined && (
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" color="textSecondary">
                  Total Applications
                </Typography>
                <Typography variant="body1">{school.application_count}</Typography>
              </Grid>
            )}
          </Grid>
        </CardContent>
      </Card>
    );
  };

  /**
   * Renders the programs tab content
   * @returns JSX.Element - The rendered programs tab content
   */
  const renderProgramsTab = (): JSX.Element => {
    const columns = [
      {
        field: 'name',
        headerName: 'Program Name',
        sortable: true,
        width: '30%',
      },
      {
        field: 'duration_weeks',
        headerName: 'Duration (Weeks)',
        sortable: true,
        width: '15%',
      },
      {
        field: 'current_tuition',
        headerName: 'Tuition',
        sortable: true,
        width: '15%',
        render: (value: number) => formatCurrency(value),
      },
      {
        field: 'status',
        headerName: 'Status',
        sortable: true,
        width: '15%',
        render: (value: ProgramStatus) => getStatusChip(value),
      },
      {
        field: 'created_at',
        headerName: 'Created',
        sortable: true,
        width: '15%',
        render: (value: string) => new Date(value).toLocaleDateString(),
      },
    ];
    
    const programActions = [
      {
        icon: <Edit />,
        label: 'Edit Program',
        onClick: (program: Program) => navigate(`/programs/edit/${program.id}`),
        color: 'primary',
      },
    ];
    
    return (
      <Box>
        <Box display="flex" justifyContent="flex-end" mb={2}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<Add />}
            onClick={handleAddProgram}
          >
            Add Program
          </Button>
        </Box>
        <DataTable
          data={programs}
          columns={columns}
          loading={loading}
          actions={programActions}
          emptyStateMessage="No programs found for this school"
          onRowClick={handleProgramClick}
        />
      </Box>
    );
  };

  /**
   * Renders the contacts tab content
   * @returns JSX.Element - The rendered contacts tab content
   */
  const renderContactsTab = (): JSX.Element => {
    const columns = [
      {
        field: 'first_name',
        headerName: 'First Name',
        sortable: true,
        width: '15%',
      },
      {
        field: 'last_name',
        headerName: 'Last Name',
        sortable: true,
        width: '15%',
      },
      {
        field: 'title',
        headerName: 'Title',
        sortable: true,
        width: '15%',
      },
      {
        field: 'email',
        headerName: 'Email',
        sortable: true,
        width: '20%',
      },
      {
        field: 'phone',
        headerName: 'Phone',
        sortable: true,
        width: '15%',
        render: (value: string) => formatPhoneNumber(value),
      },
      {
        field: 'is_primary',
        headerName: 'Primary Contact',
        sortable: true,
        width: '10%',
        render: (value: boolean) => value ? 'Yes' : 'No',
      },
    ];
    
    const contactActions = [
      {
        icon: <Edit />,
        label: 'Edit Contact',
        onClick: (contact: any) => navigate(`/schools/${schoolId}/contacts/edit/${contact.id}`),
        color: 'primary',
      },
      {
        icon: <Person />,
        label: 'View Contact Details',
        onClick: (contact: any) => navigate(`/schools/${schoolId}/contacts/${contact.id}`),
        color: 'info',
      },
    ];
    
    return (
      <Box>
        <Box display="flex" justifyContent="flex-end" mb={2}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<Add />}
            onClick={() => navigate(`/schools/${schoolId}/contacts/new`)}
          >
            Add Contact
          </Button>
        </Box>
        <DataTable
          data={school?.contacts || []}
          columns={columns}
          loading={loading}
          actions={contactActions}
          emptyStateMessage="No contacts found for this school"
        />
      </Box>
    );
  };

  /**
   * Renders the documents tab content
   * @returns JSX.Element - The rendered documents tab content
   */
  const renderDocumentsTab = (): JSX.Element => {
    const columns = [
      {
        field: 'file_name',
        headerName: 'Document Name',
        sortable: true,
        width: '25%',
      },
      {
        field: 'document_type',
        headerName: 'Document Type',
        sortable: true,
        width: '20%',
        render: (value: string) => value.replace('_', ' ').toUpperCase(),
      },
      {
        field: 'uploaded_at',
        headerName: 'Upload Date',
        sortable: true,
        width: '15%',
        render: (value: string) => new Date(value).toLocaleDateString(),
      },
      {
        field: 'status',
        headerName: 'Status',
        sortable: true,
        width: '15%',
        render: (value: string) => (
          <Chip
            label={value.toUpperCase()}
            color={value === 'active' ? 'success' : 'default'}
            size="small"
          />
        ),
      },
    ];
    
    const documentActions = [
      {
        icon: <Description />,
        label: 'View Document',
        onClick: (document: any) => {
          if (document.download_url) {
            window.open(document.download_url, '_blank');
          }
        },
        isDisabled: (document: any) => !document.download_url,
        color: 'primary',
      },
    ];
    
    return (
      <Box>
        <Box display="flex" justifyContent="flex-end" mb={2}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<Add />}
            onClick={() => navigate(`/schools/${schoolId}/documents/upload`)}
          >
            Upload Document
          </Button>
        </Box>
        <DataTable
          data={school?.documents || []}
          columns={columns}
          loading={loading}
          actions={documentActions}
          emptyStateMessage="No documents found for this school"
        />
      </Box>
    );
  };

  // If there's an error, render an error message
  if (error) {
    return (
      <Page title="School Detail">
        <Typography color="error" variant="h6">
          Error loading school: {error}
        </Typography>
        <Button
          variant="contained"
          startIcon={<ArrowBack />}
          onClick={handleBackToList}
          sx={{ mt: 2 }}
        >
          Back to School List
        </Button>
      </Page>
    );
  }

  return (
    <Page
      title={school ? school.name : 'School Detail'}
      description={school ? `${school.city}, ${school.state}` : ''}
      actions={
        <>
          <Button
            variant="outlined"
            startIcon={<ArrowBack />}
            onClick={handleBackToList}
            sx={{ mr: 1 }}
          >
            Back to List
          </Button>
          <Button
            variant="contained"
            startIcon={<Edit />}
            onClick={handleEditSchool}
            disabled={!school}
          >
            Edit School
          </Button>
        </>
      }
    >
      {loading && !school ? (
        <Typography>Loading school details...</Typography>
      ) : !school ? (
        <Typography>School not found</Typography>
      ) : (
        <>
          {renderSchoolInfo()}
          
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              aria-label="School detail tabs"
            >
              <Tab label="Programs" id="tab-programs" aria-controls="tabpanel-programs" />
              <Tab label="Contacts" id="tab-contacts" aria-controls="tabpanel-contacts" />
              <Tab label="Documents" id="tab-documents" aria-controls="tabpanel-documents" />
            </Tabs>
          </Box>
          
          <Box role="tabpanel" hidden={activeTab !== 0} id="tabpanel-programs" aria-labelledby="tab-programs">
            {activeTab === 0 && renderProgramsTab()}
          </Box>
          
          <Box role="tabpanel" hidden={activeTab !== 1} id="tabpanel-contacts" aria-labelledby="tab-contacts">
            {activeTab === 1 && renderContactsTab()}
          </Box>
          
          <Box role="tabpanel" hidden={activeTab !== 2} id="tabpanel-documents" aria-labelledby="tab-documents">
            {activeTab === 2 && renderDocumentsTab()}
          </Box>
        </>
      )}
    </Page>
  );
};

export default SchoolDetail;