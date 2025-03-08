import React, { useEffect, useState, useMemo } from 'react'; // React v18.0.0
import { Grid, Typography, Box, Button, Divider } from '@mui/material'; // v5.14.0
import { 
  Dashboard as DashboardIcon, 
  School as SchoolIcon, 
  Person as PersonIcon, 
  Description as DescriptionIcon, 
  Assignment as AssignmentIcon, 
  AttachMoney as MoneyIcon 
} from '@mui/icons-material'; // v5.14.0
import { BarChart, LineChart, PieChart } from '@mui/x-charts'; // v6.0.0
import { useAuth } from '../../hooks/useAuth';
import { 
  Page, 
  PageHeader, 
  Card, 
  LoadingSpinner 
} from '../../components/common';
import { 
  getApplicationCountsByStatus,
} from '../../api/applications';
import { 
  getUnderwritingMetrics,
} from '../../api/underwriting';
import {
  getFundingStatusSummary,
} from '../../api/funding';
import {
  getQCCountsByStatus,
} from '../../api/qc';
import {
  getSchools,
} from '../../api/schools';
import {
  getUsers,
} from '../../api/users';
import { 
  ApplicationCountsByStatus,
} from '../../types/application.types';
import { 
  UnderwritingMetrics,
} from '../../types/underwriting.types';
import { 
  FundingStatusSummary,
} from '../../types/funding.types';
import { 
  QCCountsByStatus,
} from '../../types/qc.types';
import { UserType } from '../../types/auth.types';

/**
 * Main component for the system administrator dashboard
 */
const AdminDashboard: React.FC = () => {
  // Initialize state variables for dashboard metrics and loading state
  const [applicationCounts, setApplicationCounts] = useState<ApplicationCountsByStatus | null>(null);
  const [underwritingMetrics, setUnderwritingMetrics] = useState<UnderwritingMetrics | null>(null);
  const [fundingSummary, setFundingSummary] = useState<FundingStatusSummary | null>(null);
  const [qcCounts, setQCCounts] = useState<QCCountsByStatus | null>(null);
  const [schoolsCount, setSchoolsCount] = useState<number | null>(null);
  const [usersCount, setUsersCount] = useState<number | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Use useAuth hook to get current user information
  const { state } = useAuth();

  // Check if user has SYSTEM_ADMIN role, redirect if not
  const isAdmin = useMemo(() => {
    return state.user?.userType === UserType.SYSTEM_ADMIN;
  }, [state.user]);

  // Define fetchDashboardData function to load all required metrics
  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // Fetch application statistics
      const appCountsResponse = await getApplicationCountsByStatus();
      if (appCountsResponse.success && appCountsResponse.data) {
        setApplicationCounts(appCountsResponse.data);
      } else {
        console.error('Failed to fetch application counts:', appCountsResponse.message);
      }

      // Fetch underwriting metrics
      const underwritingMetricsResponse = await getUnderwritingMetrics();
      if (underwritingMetricsResponse.success && underwritingMetricsResponse.data) {
        setUnderwritingMetrics(underwritingMetricsResponse.data);
      } else {
        console.error('Failed to fetch underwriting metrics:', underwritingMetricsResponse.message);
      }

      // Fetch funding summary
      const fundingSummaryResponse = await getFundingStatusSummary();
      if (fundingSummaryResponse.success && fundingSummaryResponse.data) {
        setFundingSummary(fundingSummaryResponse.data);
      } else {
        console.error('Failed to fetch funding summary:', fundingSummaryResponse.message);
      }

      // Fetch QC counts
      const qcCountsResponse = await getQCCountsByStatus();
      if (qcCountsResponse.success && qcCountsResponse.data) {
        setQCCounts(qcCountsResponse.data);
      } else {
        console.error('Failed to fetch QC counts:', qcCountsResponse.message);
      }

      // Fetch schools count
      const schoolsResponse = await getSchools({ page: 1, page_size: 1 });
      if (schoolsResponse.success && schoolsResponse.data) {
        setSchoolsCount(schoolsResponse.data.total);
      } else {
        console.error('Failed to fetch schools count:', schoolsResponse.message);
      }

      // Fetch users count
      const usersResponse = await getUsers({ page: 1, page_size: 1 });
      if (usersResponse.success && usersResponse.data) {
        setUsersCount(usersResponse.data.total);
      } else {
        console.error('Failed to fetch users count:', usersResponse.message);
      }
    } finally {
      setLoading(false);
    }
  };

  // Use useEffect to call fetchDashboardData on component mount
  useEffect(() => {
    if (isAdmin) {
      fetchDashboardData();
    }
  }, [isAdmin]);

  // Render dashboard layout with metrics cards and charts
  return (
    <Page title="System Administrator Dashboard">
      {loading ? (
        // Show loading spinner while data is being fetched
        <LoadingSpinner label="Loading dashboard data..." />
      ) : (
        // Display dashboard content when data is loaded
        <Grid container spacing={3}>
          {/* Application Statistics */}
          <Grid item xs={12} md={6}>
            <MetricsSection title="Application Statistics">
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <StatCard
                    title="Total Applications"
                    value={applicationCounts?.total || 0}
                    icon={<DescriptionIcon />}
                    color="primary"
                  />
                </Grid>
                <Grid item xs={6}>
                  <StatCard
                    title="Approved Applications"
                    value={applicationCounts?.approved || 0}
                    icon={<AssignmentIcon />}
                    color="success"
                  />
                </Grid>
                <Grid item xs={6}>
                  <StatCard
                    title="Pending Applications"
                    value={applicationCounts?.submitted || 0}
                    icon={<AssignmentIcon />}
                    color="warning"
                  />
                </Grid>
                <Grid item xs={6}>
                  <StatCard
                    title="Denied Applications"
                    value={applicationCounts?.denied || 0}
                    icon={<AssignmentIcon />}
                    color="error"
                  />
                </Grid>
              </Grid>
            </MetricsSection>
          </Grid>

          {/* Underwriting Metrics */}
          <Grid item xs={12} md={6}>
            <MetricsSection title="Underwriting Metrics">
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <StatCard
                    title="Applications in Queue"
                    value={underwritingMetrics?.total_in_queue || 0}
                    icon={<AssignmentIcon />}
                    color="info"
                  />
                </Grid>
                <Grid item xs={6}>
                  <StatCard
                    title="Average Decision Time"
                    value={underwritingMetrics?.average_decision_time || 0}
                    icon={<AssignmentIcon />}
                    color="secondary"
                  />
                </Grid>
                <Grid item xs={6}>
                  <StatCard
                    title="Approval Rate"
                    value={underwritingMetrics?.approval_rate || 0}
                    icon={<AssignmentIcon />}
                    color="success"
                  />
                </Grid>
              </Grid>
            </MetricsSection>
          </Grid>

          {/* Funding Summary */}
          <Grid item xs={12} md={6}>
            <MetricsSection title="Funding Summary">
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <StatCard
                    title="Total Disbursed"
                    value={fundingSummary?.disbursed || 0}
                    icon={<MoneyIcon />}
                    color="success"
                  />
                </Grid>
                <Grid item xs={6}>
                  <StatCard
                    title="Pending Disbursement"
                    value={fundingSummary?.pending || 0}
                    icon={<MoneyIcon />}
                    color="warning"
                  />
                </Grid>
              </Grid>
            </MetricsSection>
          </Grid>

          {/* System Health */}
          <Grid item xs={12} md={6}>
            <MetricsSection title="System Health">
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <StatCard
                    title="Total Schools"
                    value={schoolsCount || 0}
                    icon={<SchoolIcon />}
                    color="primary"
                  />
                </Grid>
                <Grid item xs={6}>
                  <StatCard
                    title="Total Users"
                    value={usersCount || 0}
                    icon={<PersonIcon />}
                    color="info"
                  />
                </Grid>
              </Grid>
            </MetricsSection>
          </Grid>

          {/* Charts */}
          <Grid item xs={12} md={6}>
            <Card title="Application Status Distribution">
              {applicationCounts && (
                <ApplicationStatusChart data={applicationCounts} />
              )}
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card title="Underwriting Metrics">
              {underwritingMetrics && (
                <UnderwritingMetricsChart data={underwritingMetrics} />
              )}
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card title="Funding Metrics">
              {fundingSummary && (
                <FundingMetricsChart data={fundingSummary} />
              )}
            </Card>
          </Grid>
        </Grid>
      )}
    </Page>
  );
};

/**
 * Reusable component for displaying a statistic card with icon
 */
const StatCard: React.FC<{
  title: string;
  value: number;
  icon: React.ReactNode;
  color: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  onClick?: () => void;
}> = ({ title, value, icon, color, onClick }) => (
  <Card
    onClick={onClick}
    style={{ cursor: onClick ? 'pointer' : 'default' }}
  >
    <Box display="flex" alignItems="center" justifyContent="space-between">
      <Box>
        <Typography variant="h6">{title}</Typography>
        <Typography variant="h5">{value}</Typography>
      </Box>
      {React.cloneElement(icon as React.ReactElement, { style: { fontSize: 40, color } })}
    </Box>
  </Card>
);

/**
 * Component for displaying a section of related metrics
 */
const MetricsSection: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <Card title={title}>
    {children}
  </Card>
);

/**
 * Component for displaying application status distribution chart
 */
const ApplicationStatusChart: React.FC<{ data: ApplicationCountsByStatus }> = ({ data }) => {
  const chartData = useMemo(() => {
    return [
      { label: 'Approved', value: data.approved },
      { label: 'Denied', value: data.denied },
      { label: 'In Review', value: data.in_review },
      { label: 'Submitted', value: data.submitted },
      { label: 'Draft', value: data.draft },
    ];
  }, [data]);

  return (
    <PieChart
      series={[{
        data: chartData,
        highlightScope: { faded: 'global', highlighted: 'item' },
        fadedOpacity: 0.3,
      }]}
      width={400}
      height={200}
    />
  );
};

/**
 * Component for displaying underwriting metrics chart
 */
const UnderwritingMetricsChart: React.FC<{ data: UnderwritingMetrics }> = ({ data }) => {
  const chartData = useMemo(() => {
    return [
      { label: 'Approval Rate', value: data.approval_rate },
      { label: 'Decision Time', value: data.average_decision_time },
    ];
  }, [data]);

  return (
    <BarChart
      series={[{ dataKey: 'value', label: 'Value' }]}
      xAxis={[{ dataKey: 'label', label: 'Metric' }]}
      dataset={chartData}
      width={400}
      height={200}
    />
  );
};

/**
 * Component for displaying funding metrics chart
 */
const FundingMetricsChart: React.FC<{ data: FundingStatusSummary }> = ({ data }) => {
  const chartData = useMemo(() => {
    return [
      { label: 'Disbursed', value: data.disbursed },
      { label: 'Pending', value: data.pending },
    ];
  }, [data]);

  return (
    <LineChart
      series={[{ dataKey: 'value', label: 'Value' }]}
      xAxis={[{ dataKey: 'label', label: 'Status' }]}
      dataset={chartData}
      width={400}
      height={200}
    />
  );
};

export default AdminDashboard;