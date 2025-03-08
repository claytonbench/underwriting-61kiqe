import QCReviewComponent from './QCReview';
import DocumentVerificationComponent from './DocumentVerification';
import StipulationVerification from './StipulationVerification';
import ChecklistItem from './ChecklistItem';

/**
 * Exports the main QC review component for use in the loan management system.
 * @component
 */
export default QCReviewComponent;

/**
 * Exports the DocumentVerification component for verifying documents during QC review.
 * @component
 */
export { DocumentVerificationComponent };

/**
 * Exports the StipulationVerification component for verifying stipulations during QC review.
 * @component
 */
export { StipulationVerification };

/**
 * Exports the ChecklistItem component for checklist items in the QC review process.
 * @component
 */
export { ChecklistItem };