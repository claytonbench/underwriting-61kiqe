import { makeStyles } from '@mui/styles';
import { Theme } from '@mui/material';
import { mediaQueries } from '../../../responsive/breakpoints';

const useStyles = makeStyles((theme: Theme) => ({
  // Drag and drop area styling
  dropzone: {
    border: `2px dashed ${theme.palette.primary.main}`,
    borderRadius: theme.shape.borderRadius,
    padding: theme.spacing(3),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    textAlign: 'center',
    cursor: 'pointer',
    transition: 'border-color 0.3s ease, background-color 0.3s ease',
    backgroundColor: 'rgba(25, 118, 210, 0.04)', // Light blue background
    '&:hover': {
      borderColor: theme.palette.primary.dark,
      backgroundColor: 'rgba(25, 118, 210, 0.08)', // Slightly darker on hover
    },
    '&:focus': {
      outline: 'none',
      borderColor: theme.palette.primary.dark,
      boxShadow: `0 0 0 2px ${theme.palette.primary.light}`,
    },
    [mediaQueries.mobile]: {
      padding: theme.spacing(2),
    },
  },
  
  // Active state when dragging a file over the drop zone
  dropzoneActive: {
    borderColor: theme.palette.primary.dark,
    backgroundColor: 'rgba(25, 118, 210, 0.12)', // Slightly darker when active
  },
  
  // Disabled state
  dropzoneDisabled: {
    borderColor: theme.palette.action.disabled,
    backgroundColor: theme.palette.action.disabledBackground,
    cursor: 'not-allowed',
    '&:hover': {
      borderColor: theme.palette.action.disabled,
      backgroundColor: theme.palette.action.disabledBackground,
    },
  },
  
  // File information display
  fileInfo: {
    display: 'flex',
    alignItems: 'center',
    marginTop: theme.spacing(2),
    padding: theme.spacing(1),
    backgroundColor: theme.palette.background.paper,
    borderRadius: theme.shape.borderRadius,
    width: '100%',
  },
  
  // File icon
  fileIcon: {
    marginRight: theme.spacing(1),
    color: theme.palette.primary.main,
  },
  
  // File name
  fileName: {
    flex: 1,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  
  // Progress container
  progressContainer: {
    width: '100%',
    marginTop: theme.spacing(2),
  },
  
  // Container for action buttons
  actionsContainer: {
    display: 'flex',
    justifyContent: 'flex-end',
    marginTop: theme.spacing(2),
    gap: theme.spacing(1),
  },
  
  // Upload button
  uploadButton: {
    marginRight: theme.spacing(1),
  },
  
  // Error text
  errorText: {
    color: theme.palette.error.main,
    fontSize: '0.75rem',
    marginTop: theme.spacing(0.5),
  },
  
  // Helper text
  helperText: {
    fontSize: '0.75rem',
    color: theme.palette.text.secondary,
    marginTop: theme.spacing(0.5),
  },
}));

export default useStyles;