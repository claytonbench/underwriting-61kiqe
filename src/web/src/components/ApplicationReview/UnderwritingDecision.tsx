import React from 'react'; // ^18.2.0
import {
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Chip,
  List,
  ListItem,
  ListItemText,
  Box
} from '@mui/material'; // ^5.14.0
import useStyles from './styles';
import { StatusBadge } from '../common';
import {
  UnderwritingDecision as UnderwritingDecisionEnum,
  UnderwritingDecisionData,
  DecisionReason,
  Stipulation
} from '../../types/underwriting.types';
import { formatCurrency, formatPercentage, formatDateForDisplay } from '../../utils/formatting';

/**
 * Interface defining the props for the UnderwritingDecisionDisplay component
 */
interface UnderwritingDecisionProps {
  /**
   * The underwriting decision data to display
   */
  decision: UnderwritingDecisionData | null;
  /**
   * Whether the component should be in read-only mode
   */
  readOnly?: boolean;
}

/**
 * Converts an underwriting decision enum value to a human-readable text
 * @param decision The underwriting decision enum value
 * @returns Human-readable decision text
 */
const getDecisionStatusText = (decision: UnderwritingDecisionEnum): string => {
  switch (decision) {
    case UnderwritingDecisionEnum.APPROVE:
      return 'Approved';
    case UnderwritingDecisionEnum.DENY:
      return 'Denied';
    case UnderwritingDecisionEnum.REVISE:
      return 'Revision Requested';
    default:
      return 'Unknown';
  }
};

/**
 * Component that displays underwriting decision information
 * @param props The props for the component
 * @returns A JSX element that displays the underwriting decision information
 */
const UnderwritingDecisionDisplay: React.FC<UnderwritingDecisionProps> = (props) => {
  // Destructure decision and readOnly from props
  const { decision, readOnly } = props;

  // Get CSS classes using useStyles hook
  const classes = useStyles();

  // If decision is null, render a message indicating no decision has been made
  if (!decision) {
    return (
      <Typography variant="body1">
        No underwriting decision has been made for this application.
      </Typography>
    );
  }

  // Render a Card component with decision information
  return (
    <Card className={`${classes.decisionCard} ${
      decision.decision === UnderwritingDecisionEnum.APPROVE ? classes.decisionApproved :
      decision.decision === UnderwritingDecisionEnum.DENY ? classes.decisionDenied :
      decision.decision === UnderwritingDecisionEnum.REVISE ? classes.decisionRevise :
      ''
    }`}>
      {/* Render CardHeader with 'Underwriting Decision' title and decision status badge */}
      <CardHeader
        title="Underwriting Decision"
        action={
          <StatusBadge status={getDecisionStatusText(decision.decision)} />
        }
        className={classes.decisionHeader}
        titleTypographyProps={{ variant: 'h6', className: classes.decisionTitle }}
      />
      <CardContent>
        {/* If decision is APPROVE, render approved amount, interest rate, and term */}
        {decision.decision === UnderwritingDecisionEnum.APPROVE && (
          <>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2">Approved Amount:</Typography>
                <Typography variant="body1">
                  {decision.approved_amount ? formatCurrency(decision.approved_amount) : 'N/A'}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2">Interest Rate:</Typography>
                <Typography variant="body1">
                  {decision.interest_rate ? formatPercentage(decision.interest_rate / 100) : 'N/A'}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2">Term (Months):</Typography>
                <Typography variant="body1">
                  {decision.term_months ? decision.term_months : 'N/A'}
                </Typography>
              </Grid>
            </Grid>
            <Divider style={{ margin: '16px 0' }} />
          </>
        )}

        {/* Render decision date and underwriter name */}
        <Typography variant="subtitle2">Decision Date:</Typography>
        <Typography variant="body1">
          {formatDateForDisplay(decision.decision_date)}
        </Typography>
        <Typography variant="subtitle2">Underwriter:</Typography>
        <Typography variant="body1">
          {/* TODO: Replace with actual underwriter name */}
          Underwriter Name
        </Typography>

        {/* If decision has comments, render them */}
        {decision.comments && (
          <>
            <Divider style={{ margin: '16px 0' }} />
            <Typography variant="subtitle2">Comments:</Typography>
            <Typography variant="body1">{decision.comments}</Typography>
          </>
        )}

        {/* If decision has reasons, render them in a list */}
        {decision.reasons && decision.reasons.length > 0 && (
          <>
            <Divider style={{ margin: '16px 0' }} />
            <Typography variant="subtitle2">Decision Reasons:</Typography>
            <List className={classes.stipulationList}>
              {decision.reasons.map((reason: DecisionReason) => (
                <ListItem key={reason.id} className={classes.stipulationItem}>
                  <ListItemText
                    primary={reason.description}
                    secondary={reason.reason_code}
                  />
                </ListItem>
              ))}
            </List>
          </>
        )}

        {/* If decision has stipulations, render them in a list with status indicators */}
        {decision.stipulations && decision.stipulations.length > 0 && (
          <>
            <Divider style={{ margin: '16px 0' }} />
            <Typography variant="subtitle2">Stipulations:</Typography>
            <List className={classes.stipulationList}>
              {decision.stipulations.map((stipulation: Stipulation) => (
                <ListItem key={stipulation.id} className={classes.stipulationItem}>
                  <ListItemText
                    primary={stipulation.description}
                    secondary={`Due Date: ${formatDateForDisplay(stipulation.required_by_date)}`}
                  />
                  <Chip
                    label={stipulation.status}
                    className={classes.stipulationStatus}
                    size="small"
                  />
                </ListItem>
              ))}
            </List>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default UnderwritingDecisionDisplay;