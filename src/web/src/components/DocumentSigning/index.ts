/**
 * Document Signing Component Module
 * 
 * This module exports components for handling document signing workflows in the 
 * loan management system. Provides access to the main DocumentSigning component
 * along with its subcomponents for document preview and signature capture functionality.
 * 
 * Implements the document signing interface as specified in the UI design requirements
 * and provides frontend implementation for the e-signature workflow.
 * 
 * @version 1.0.0
 */

// Import the main DocumentSigning component
import DocumentSigning from './DocumentSigning';

// Import subcomponents
import DocumentPreview from './DocumentPreview';
import SignatureCapture from './SignatureCapture';

// Import constants for signature canvas dimensions
import { SIGNATURE_CANVAS_WIDTH, SIGNATURE_CANVAS_HEIGHT } from './styles';

// Export the main component as default export
export default DocumentSigning;

// Named exports for subcomponents and constants
export {
  DocumentPreview,
  SignatureCapture,
  SIGNATURE_CANVAS_WIDTH,
  SIGNATURE_CANVAS_HEIGHT
};