import { makeStyles } from '@mui/styles'; // v5.14.0
import { Theme } from '@mui/material'; // v5.14.0
import { mobile, tablet } from '../../responsive/breakpoints';

/**
 * Standard dimensions for signature canvas
 */
export const SIGNATURE_CANVAS_WIDTH = 400;
export const SIGNATURE_CANVAS_HEIGHT = 200;

/**
 * Custom styles for the DocumentSigning component and its children
 * Implements UI design requirements for document signing interface
 */
const useStyles = makeStyles<Theme>((theme) => ({
  // Main container
  root: {
    padding: theme.spacing(3),
    margin: theme.spacing(2, 0),
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing(3),
  },
  
  // Stepper container for multi-step flow
  stepperContainer: {
    marginBottom: theme.spacing(4),
  },
  
  // Document preview area
  documentPreviewContainer: {
    width: '100%',
    height: '600px',
    border: `1px solid ${theme.palette.divider}`,
    borderRadius: '4px',
    overflow: 'auto',
    backgroundColor: '#f5f5f5',
    [mobile]: {
      height: '400px',
    },
    [tablet]: {
      height: '500px',
    },
  },
  
  // Signature capture area
  signatureContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: theme.spacing(2),
    padding: theme.spacing(3),
  },
  
  // Canvas for signature drawing
  signatureCanvas: {
    border: `1px solid ${theme.palette.divider}`,
    borderRadius: '4px',
    backgroundColor: '#ffffff',
    cursor: 'crosshair',
    touchAction: 'none', // Prevents touch scrolling while signing
    [mobile]: {
      width: '100%',
      maxWidth: '300px',
      height: '150px',
    },
  },
  
  // Container to display captured signature
  signaturePreview: {
    width: '100%',
    maxWidth: SIGNATURE_CANVAS_WIDTH,
    border: `1px solid ${theme.palette.divider}`,
    borderRadius: '4px',
    padding: theme.spacing(2),
    backgroundColor: '#ffffff',
    marginTop: theme.spacing(2),
  },
  
  // Container for navigation buttons
  navigationButtons: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: theme.spacing(3),
    [mobile]: {
      flexDirection: 'column',
      gap: theme.spacing(2),
    },
  },
  
  // Container for grouped buttons
  buttonGroup: {
    display: 'flex',
    gap: theme.spacing(2),
    [mobile]: {
      width: '100%',
      justifyContent: 'center',
    },
  },
  
  // Document page navigation controls
  pageNavigation: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: theme.spacing(2),
    marginTop: theme.spacing(2),
  },
  
  // Instruction text styling
  instructions: {
    marginBottom: theme.spacing(2),
    textAlign: 'center',
  },
}));

export default useStyles;