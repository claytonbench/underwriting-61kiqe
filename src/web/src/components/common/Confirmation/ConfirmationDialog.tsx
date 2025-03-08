import React from 'react'; // ^18.2.0
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button
} from '@mui/material'; // ^5.14.0
import useStyles from './styles';
import { LoadingSpinner } from '../Loading';

/**
 * Props interface for the ConfirmationDialog component
 */
interface ConfirmationDialogProps {
  /**
   * Controls whether the dialog is displayed
   */
  open: boolean;
  /**
   * Title text for the dialog
   */
  title: string;
  /**
   * Message text explaining what the user is confirming
   */
  message: string;
  /**
   * Text for the confirm button
   * @default "Confirm"
   */
  confirmLabel?: string;
  /**
   * Text for the cancel button
   * @default "Cancel"
   */
  cancelLabel?: string;
  /**
   * Callback function when the confirm button is clicked
   */
  onConfirm: () => void;
  /**
   * Callback function when the cancel button is clicked or dialog is dismissed
   */
  onCancel: () => void;
  /**
   * Whether the confirm action is in a loading state
   * @default false
   */
  loading?: boolean;
  /**
   * Whether to disable closing the dialog when clicking outside
   * @default false
   */
  disableBackdropClick?: boolean;
}

/**
 * A dialog component that prompts users to confirm or cancel an action
 * 
 * This component displays a modal dialog with a title, descriptive message,
 * and action buttons to confirm or cancel a potentially destructive operation.
 * Provides feedback through loading states and prevents accidental actions.
 * 
 * @param props - Component props
 * @returns The rendered confirmation dialog component
 */
const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  open,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  onConfirm,
  onCancel,
  loading = false,
  disableBackdropClick = false
}) => {
  const { dialogContent, dialogActions, confirmButton, cancelButton, loadingWrapper } = useStyles();

  /**
   * Handles dialog close events (backdrop click, escape key)
   * Only closes if disableBackdropClick is false
   */
  const handleClose = (event: object, reason: string) => {
    if (disableBackdropClick && (reason === 'backdropClick' || reason === 'escapeKeyDown')) {
      return;
    }
    onCancel();
  };

  /**
   * Handles the confirm button click
   */
  const handleConfirm = () => {
    onConfirm();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      aria-labelledby="confirmation-dialog-title"
      aria-describedby="confirmation-dialog-description"
      data-testid="confirmation-dialog"
    >
      <DialogTitle id="confirmation-dialog-title">{title}</DialogTitle>
      
      <DialogContent className={dialogContent}>
        <DialogContentText id="confirmation-dialog-description">
          {message}
        </DialogContentText>
      </DialogContent>
      
      <DialogActions className={dialogActions}>
        <Button
          className={cancelButton}
          onClick={onCancel}
          color="primary"
          variant="outlined"
          disabled={loading}
          data-testid="cancel-button"
        >
          {cancelLabel}
        </Button>
        
        <Button
          className={confirmButton}
          onClick={handleConfirm}
          color="error"
          variant="contained"
          disabled={loading}
          data-testid="confirm-button"
        >
          {loading ? (
            <div className={loadingWrapper}>
              <LoadingSpinner size={20} color="inherit" />
              {confirmLabel}
            </div>
          ) : (
            confirmLabel
          )}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConfirmationDialog;