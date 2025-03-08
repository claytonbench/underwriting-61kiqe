import React from 'react'; // react ^18.2.0
import { ApplicationReview as ApplicationReviewComponent, ApplicationReviewProps } from './ApplicationReview';
import { CreditInfo as CreditInfoComponent, CreditInfoProps } from './CreditInfo';
import { DocumentSection as DocumentSectionComponent, DocumentSectionProps } from './DocumentSection';
import { UnderwritingDecisionDisplay as UnderwritingDecisionDisplayComponent, UnderwritingDecisionProps } from './UnderwritingDecision';

/**
 * Exports the main ApplicationReview component for use throughout the application.
 * This component provides underwriters with a comprehensive view of application data and supporting documents.
 */
const ApplicationReview: React.FC<ApplicationReviewProps> = ApplicationReviewComponent;

/**
 * Exports the CreditInfo component for displaying credit information.
 * This component displays credit scores, debt-to-income ratios, and monthly debt amounts for borrowers and co-borrowers.
 */
const CreditInfo: React.FC<CreditInfoProps> = CreditInfoComponent;

/**
 * Exports the DocumentSection component for displaying application documents.
 * This component displays a list of documents associated with the application, their status, and actions to view or download them.
 */
const DocumentSection: React.FC<DocumentSectionProps> = DocumentSectionComponent;

/**
 * Exports the UnderwritingDecisionDisplay component for displaying underwriting decisions.
 * This component displays the underwriting decision, approved loan amount, interest rate, term, and any stipulations or comments.
 */
const UnderwritingDecisionDisplay: React.FC<UnderwritingDecisionProps> = UnderwritingDecisionDisplayComponent;

export default ApplicationReview;
export { CreditInfo, DocumentSection, UnderwritingDecisionDisplay };