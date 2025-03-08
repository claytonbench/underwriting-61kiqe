import React from 'react';
import {
  Card,
  CardHeader,
  CardContent,
  CardActions,
} from '@mui/material';
import useStyles from './styles';

/**
 * Props interface for the CustomCard component
 */
interface CardProps extends React.ComponentProps<typeof Card> {
  /** Title for the card header */
  title?: React.ReactNode;
  /** Subheader for the card header */
  subheader?: React.ReactNode;
  /** Content to be displayed in the card */
  children?: React.ReactNode;
  /** Actions to be displayed at the bottom of the card */
  actions?: React.ReactNode;
  /** Whether the card should fill the available height of its container */
  fullHeight?: boolean;
  /** Whether the card content should have padding removed */
  noPadding?: boolean;
}

/**
 * A customizable card component that wraps Material-UI's Card with additional styling and functionality.
 * Provides consistent appearance across the loan management system with options for headers,
 * content padding, and action areas.
 */
const CustomCard: React.FC<CardProps> = ({
  title,
  subheader,
  children,
  actions,
  fullHeight = false,
  noPadding = false,
  ...props
}) => {
  const classes = useStyles();

  return (
    <Card 
      className={`${classes.root} ${fullHeight ? classes.fullHeight : ''}`}
      {...props}
    >
      {(title || subheader) && (
        <CardHeader title={title} subheader={subheader} />
      )}
      <CardContent className={`${classes.content} ${noPadding ? classes.noPadding : ''}`}>
        {children}
      </CardContent>
      {actions && (
        <CardActions>
          {actions}
        </CardActions>
      )}
    </Card>
  );
};

export default CustomCard;