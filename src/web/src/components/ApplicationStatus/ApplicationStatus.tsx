import React from 'react';
import { Typography, Box, Grid, Divider } from '@mui/material';

// Import styling
import useStyles from './styles';

// Import components
import StatusTimeline from './StatusTimeline';
import RequiredActions from './RequiredActions';
import CustomCard from '../common/Card';
import StatusBadge from '../common/StatusBadge';

// Import types
import { 
  ApplicationDetail, 
  ApplicationRequiredAction 
} from '../../types/application.types';

// Import utilities
import { formatCurrency } from '../../utils/formatting';
import { formatDate } from '../../utils/date';

/**
 * Interface defining the props for the ApplicationStatus component
 */
export interface ApplicationStatusProps {
  /**
   * Detailed information about the loan application
   */
  applicationDetail: ApplicationDetail;
  /**
   * Array of required actions for the application
   */
  requiredActions: ApplicationRequiredAction[];
  /**
   * Callback function triggered when an action button is clicked
   * @param actionType - Type of action being performed
   * @param data - Additional data for the action
   */
  onAction: (actionType: string, data?: any) => void;
  /**
   * Optional CSS class name to apply to the component
   */
  className?: string;
}

/**
 * Component that displays the status and details of a loan application,
 * including application details, status timeline, and required actions.
 * Serves as a container for the StatusTimeline and RequiredActions components.
 */
const ApplicationStatus: React.FC<ApplicationStatusProps> = ({ 
  applicationDetail, 
  requiredActions, 
  onAction, 
  className 
}) => {
  const classes = useStyles();
  const { application, loan_details, school, program, status_history } = applicationDetail;

  return (
    <Box className={`${classes.root} ${className || ''}`} aria-label="Application status and details">
      <Grid container spacing={3}>
        {/* Application Details Section */}
        <Grid item xs={12}>
          <CustomCard title="Application Details">
            <Box className={classes.statusBadge} aria-live="polite">
              <StatusBadge status={application.status} />
            </Box>

            <div className={classes.detailsGrid}>
              <div className={classes.detailItem}>
                <Typography variant="body2" className={classes.detailLabel}>
                  School
                </Typography>
                <Typography variant="body1" className={classes.detailValue}>
                  {school.name}
                </Typography>
              </div>

              <div className={classes.detailItem}>
                <Typography variant="body2" className={classes.detailLabel}>
                  Program
                </Typography>
                <Typography variant="body1" className={classes.detailValue}>
                  {program.name}
                </Typography>
              </div>

              <div className={classes.detailItem}>
                <Typography variant="body2" className={classes.detailLabel}>
                  Requested Amount
                </Typography>
                <Typography variant="body1" className={classes.detailValue}>
                  {formatCurrency(loan_details.requested_amount)}
                </Typography>
              </div>

              <div className={classes.detailItem}>
                <Typography variant="body2" className={classes.detailLabel}>
                  Approved Amount
                </Typography>
                <Typography variant="body1" className={classes.detailValue}>
                  {loan_details.approved_amount ? formatCurrency(loan_details.approved_amount) : 'Pending'}
                </Typography>
              </div>

              <div className={classes.detailItem}>
                <Typography variant="body2" className={classes.detailLabel}>
                  Submission Date
                </Typography>
                <Typography variant="body1" className={classes.detailValue}>
                  {application.submission_date ? formatDate(application.submission_date, 'MM/dd/yyyy') : 'Not submitted'}
                </Typography>
              </div>

              <div className={classes.detailItem}>
                <Typography variant="body2" className={classes.detailLabel}>
                  Last Updated
                </Typography>
                <Typography variant="body1" className={classes.detailValue}>
                  {formatDate(application.last_updated, 'MM/dd/yyyy')}
                </Typography>
              </div>
            </div>
          </CustomCard>
        </Grid>

        {/* Application Timeline Section */}
        <Grid item xs={12}>
          <StatusTimeline 
            statusHistory={status_history} 
            currentStatus={application.status} 
            className={classes.timelineSection}
          />
        </Grid>

        {/* Required Actions Section */}
        <Grid item xs={12}>
          <RequiredActions 
            actions={requiredActions} 
            onAction={onAction} 
            className={classes.actionsSection}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default ApplicationStatus;