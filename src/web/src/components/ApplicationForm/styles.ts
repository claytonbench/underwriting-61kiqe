import { makeStyles } from '@mui/styles'; // @mui/styles ^5.14.0
import { Theme } from '@mui/material'; // @mui/material ^5.14.0
import { mediaQueries } from '../../responsive/breakpoints';

const useStyles = makeStyles((theme: Theme) => ({
  // Base styles for the form container
  formContainer: {
    width: '100%',
    maxWidth: '800px',
    margin: '0 auto',
    padding: theme.spacing(3),
    [mediaQueries.mobile]: {
      padding: theme.spacing(2),
    },
  },

  // Styles for the Paper component containing the form
  formPaper: {
    padding: theme.spacing(3),
    marginBottom: theme.spacing(3),
    borderRadius: '8px',
    [mediaQueries.mobile]: {
      padding: theme.spacing(2),
    },
  },

  // Styles for each form section
  formSection: {
    marginBottom: theme.spacing(4),
  },

  // Styles for section titles
  sectionTitle: {
    marginBottom: theme.spacing(2),
    color: theme.palette.primary.main,
    fontWeight: 500,
  },

  // Styles for rows of form fields
  fieldRow: {
    marginBottom: theme.spacing(2),
  },

  // Styles for the container of navigation buttons
  buttonContainer: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: theme.spacing(3),
    [mediaQueries.mobile]: {
      flexDirection: 'column',
      alignItems: 'center',
    },
  },

  // Styles for the back button
  backButton: {
    marginRight: theme.spacing(1),
    [mediaQueries.mobile]: {
      margin: theme.spacing(1, 0),
      width: '100%',
    },
  },

  // Styles for the next/submit button
  nextButton: {
    marginLeft: theme.spacing(1),
    [mediaQueries.mobile]: {
      margin: theme.spacing(1, 0),
      width: '100%',
    },
  },

  // Styles for the save draft button
  saveButton: {
    marginLeft: theme.spacing(1),
    [mediaQueries.mobile]: {
      margin: theme.spacing(1, 0),
      width: '100%',
    },
  },

  // Styles for radio button groups
  radioGroup: {
    marginBottom: theme.spacing(2),
  },

  // Styles for form control elements
  formControl: {
    marginBottom: theme.spacing(2),
    width: '100%',
  },

  // Styles for form helper text
  formHelperText: {
    marginTop: theme.spacing(0.5),
  },

  // Styles for error messages
  errorText: {
    color: theme.palette.error.main,
  },

  // Responsive styles for mobile devices
  mobileFormContainer: {
    padding: theme.spacing(2),
  },

  // Responsive styles for button container on mobile
  mobileButtonContainer: {
    flexDirection: 'column',
    alignItems: 'center',
  },

  // Responsive styles for buttons on mobile
  mobileButton: {
    margin: theme.spacing(1, 0),
    width: '100%',
  },
}));

export default useStyles;