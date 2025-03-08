import React from 'react';
import { 
  Stepper, 
  Step, 
  StepLabel, 
  StepConnector, 
  Box, 
  Typography 
} from '@mui/material';
import { 
  CheckCircle, 
  RadioButtonUnchecked 
} from '@mui/icons-material';
import useStyles from './styles';

/**
 * Props interface for the CustomStepper component
 */
interface StepperProps {
  /** Current active step index (zero-based) */
  activeStep: number;
  /** Array of step labels to display */
  steps: string[];
  /** Optional array of step descriptions */
  descriptions?: string[];
  /** Orientation of the stepper */
  orientation?: 'horizontal' | 'vertical';
  /** Whether to place the label under the step icon */
  alternativeLabel?: boolean;
}

/**
 * Props interface for the custom step icon component
 */
interface CustomStepIconProps {
  /** Whether the step is active */
  active: boolean;
  /** Whether the step is completed */
  completed: boolean;
  /** Icon to display for the step */
  icon: React.ReactNode;
}

/**
 * Custom icon component for stepper steps
 * Displays different icons based on step status
 */
const CustomStepIcon: React.FC<CustomStepIconProps> = (props) => {
  const { active, completed, icon } = props;
  const classes = useStyles();
  
  if (completed) {
    return (
      <Box 
        className={`${classes.stepIcon} ${classes.completedStepIcon}`}
        aria-label={`Completed step ${icon}`}
      >
        <CheckCircle fontSize="small" />
      </Box>
    );
  }
  
  if (active) {
    return (
      <Box 
        className={`${classes.stepIcon} ${classes.activeStepIcon}`}
        aria-label={`Current step ${icon}`}
      >
        <RadioButtonUnchecked fontSize="small" />
      </Box>
    );
  }
  
  return (
    <Box 
      className={`${classes.stepIcon} ${classes.pendingStepIcon}`}
      aria-label={`Pending step ${icon}`}
    >
      <RadioButtonUnchecked fontSize="small" />
    </Box>
  );
};

/**
 * A customized stepper component for displaying progress through multi-step processes.
 * Extends Material-UI's Stepper to provide a consistent, branded step indicator
 * that supports active, completed, and pending step states with appropriate visual indicators.
 */
const CustomStepper: React.FC<StepperProps> = (props) => {
  const { 
    activeStep, 
    steps, 
    descriptions, 
    orientation = 'horizontal', 
    alternativeLabel = true 
  } = props;
  
  const classes = useStyles();
  
  return (
    <Box className={classes.root}>
      <Stepper
        activeStep={activeStep}
        alternativeLabel={alternativeLabel}
        orientation={orientation}
        connector={
          <StepConnector 
            classes={{
              root: classes.connector,
              completed: classes.completedConnector,
              active: classes.activeConnector,
              line: classes.pendingConnector, // Default state
            }}
          />
        }
        className={orientation === 'vertical' ? classes.verticalStepper : ''}
      >
        {steps.map((label, index) => {
          const stepProps: { completed?: boolean } = {};
          const labelProps: { optional?: React.ReactNode } = {};
          
          // Mark step as completed if it's before the active step
          if (index < activeStep) {
            stepProps.completed = true;
          }
          
          // Add description if provided
          if (descriptions && descriptions[index]) {
            labelProps.optional = (
              <Typography 
                variant="caption" 
                className={classes.stepDescription}
                aria-hidden="true"
              >
                {descriptions[index]}
              </Typography>
            );
          }
          
          // Determine label class based on step status
          let labelClass = '';
          if (index < activeStep) {
            labelClass = classes.completedStepLabel;
          } else if (index === activeStep) {
            labelClass = classes.activeStepLabel;
          } else {
            labelClass = classes.pendingStepLabel;
          }
          
          return (
            <Step key={label} {...stepProps}>
              <StepLabel
                StepIconComponent={CustomStepIcon}
                className={classes.stepContainer}
                classes={{ label: `${classes.stepLabel} ${labelClass}` }}
                {...labelProps}
                optional={labelProps.optional}
                aria-current={index === activeStep ? 'step' : undefined}
              >
                {label}
              </StepLabel>
            </Step>
          );
        })}
      </Stepper>
    </Box>
  );
};

export default CustomStepper;