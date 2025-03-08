import React from 'react';
import { Grid, Typography, Card, CardContent, Button, Box } from '@mui/material';

import useStyles from './styles';
import { CreditInformation, CreditScoreTier } from '../../types/underwriting.types';
import { formatCurrency, formatPercentage } from '../../utils/formatting';

/**
 * Props interface for the CreditInfo component
 */
interface CreditInfoProps {
  borrowerCredit: CreditInformation | null;
  coBorrowerCredit?: CreditInformation | null;
  onViewCreditReport?: (creditInfo: CreditInformation) => void;
}

/**
 * CreditInfo component displays credit information for borrowers and co-borrowers
 * in the loan application review interface. It shows credit scores with color-coding
 * based on credit tiers, debt-to-income ratios, and monthly debt amounts.
 */
const CreditInfo: React.FC<CreditInfoProps> = ({
  borrowerCredit,
  coBorrowerCredit,
  onViewCreditReport
}) => {
  const classes = useStyles();

  // Helper function to get appropriate CSS class based on credit tier
  const getCreditScoreClass = (tier: CreditScoreTier) => {
    switch (tier) {
      case CreditScoreTier.EXCELLENT:
        return classes.creditScoreExcellent;
      case CreditScoreTier.GOOD:
        return classes.creditScoreGood;
      case CreditScoreTier.FAIR:
        return classes.creditScoreFair;
      default:
        return classes.creditScorePoor;
    }
  };

  // Helper function to get appropriate CSS class based on debt-to-income ratio
  const getMetricClass = (ratio: number) => {
    if (ratio < 0.36) {
      return classes.metricGood;
    } else if (ratio < 0.43) {
      return classes.metricWarning;
    } else {
      return classes.metricDanger;
    }
  };

  // Render credit information for a single borrower
  const renderCreditInfo = (creditInfo: CreditInformation | null, title: string) => (
    <Card>
      <CardContent>
        <Typography variant="subtitle1" gutterBottom>{title}</Typography>
        {creditInfo ? (
          <>
            {/* Credit Score */}
            <div className={classes.creditScoreContainer}>
              <span className={`${classes.creditScore} ${getCreditScoreClass(creditInfo.credit_tier)}`}>
                {creditInfo.credit_score}
              </span>
              <Typography variant="body1">Credit Score</Typography>
            </div>
            
            {/* Debt-to-Income Ratio */}
            <div className={classes.financialMetric}>
              <Typography variant="body2" className={classes.metricLabel}>
                Debt-to-Income:
              </Typography>
              <Typography variant="body1" className={getMetricClass(creditInfo.debt_to_income_ratio)}>
                {formatPercentage(creditInfo.debt_to_income_ratio)}
              </Typography>
            </div>
            
            {/* Monthly Debt */}
            <div className={classes.financialMetric}>
              <Typography variant="body2" className={classes.metricLabel}>
                Monthly Debt:
              </Typography>
              <Typography variant="body1">
                {formatCurrency(creditInfo.monthly_debt)}
              </Typography>
            </div>
            
            {/* View Credit Report Button */}
            {onViewCreditReport && (
              <Box mt={2}>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => onViewCreditReport(creditInfo)}
                >
                  View Credit Report
                </Button>
              </Box>
            )}
          </>
        ) : (
          <Typography color="textSecondary">Credit information not available</Typography>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Grid container spacing={2}>
      {/* Borrower Credit Information */}
      <Grid item xs={12} md={coBorrowerCredit ? 6 : 12}>
        {renderCreditInfo(borrowerCredit, "Primary Borrower")}
      </Grid>

      {/* Co-Borrower Credit Information (if available) */}
      {coBorrowerCredit && (
        <Grid item xs={12} md={6}>
          {renderCreditInfo(coBorrowerCredit, "Co-Borrower")}
        </Grid>
      )}
    </Grid>
  );
};

export default CreditInfo;