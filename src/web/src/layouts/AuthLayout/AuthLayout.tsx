import React, { ReactNode } from 'react';
import {
  Box,
  Container,
  Paper,
  Card,
  CardContent,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material'; // v5.14.0
import useStyles from './styles';
import logo from '../../assets/images/logo.svg';

/**
 * Props for the AuthLayout component
 */
interface AuthLayoutProps {
  /**
   * Optional title to display at the top of the authentication form
   */
  title?: string;
  
  /**
   * Optional subtitle to display below the title
   */
  subtitle?: string;
  
  /**
   * Content to render inside the authentication layout (typically a form)
   */
  children: ReactNode;
}

/**
 * Layout component for authentication pages that provides a consistent, branded appearance
 * Used for login, registration, password reset, and other auth-related pages
 */
const AuthLayout: React.FC<AuthLayoutProps> = ({ 
  title, 
  subtitle, 
  children 
}) => {
  const theme = useTheme();
  const classes = useStyles();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // Generate unique IDs for ARIA attributes if titles exist
  const titleId = title ? 'auth-title' : undefined;
  const subtitleId = subtitle ? 'auth-subtitle' : undefined;

  return (
    <Box component="main" className={classes.root}>
      <Paper className={classes.paper} elevation={0}>
        <Container className={classes.container}>
          {/* Logo section */}
          <img 
            src={logo} 
            alt="Loan Management System" 
            className={classes.logo}
          />
          
          {/* Card container for authentication content */}
          <Card 
            className={classes.card} 
            aria-labelledby={titleId}
            aria-describedby={subtitleId}
          >
            <CardContent className={classes.cardContent}>
              {/* Title and subtitle section if provided */}
              {title && (
                <Typography 
                  variant="h5" 
                  component="h1" 
                  id={titleId}
                  className={classes.title}
                >
                  {title}
                </Typography>
              )}
              
              {subtitle && (
                <Typography 
                  variant="body1" 
                  id={subtitleId}
                  className={classes.subtitle}
                >
                  {subtitle}
                </Typography>
              )}
              
              {/* Children content (authentication form) */}
              {children}
            </CardContent>
          </Card>
        </Container>
      </Paper>
    </Box>
  );
};

export default AuthLayout;