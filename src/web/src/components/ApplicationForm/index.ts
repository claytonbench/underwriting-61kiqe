import ApplicationFormContainer from './ApplicationFormContainer';
import BorrowerInfoStep from './BorrowerInfoStep';
import EmploymentInfoStep from './EmploymentInfoStep';
import CoBorrowerInfoStep from './CoBorrowerInfoStep';
import LoanDetailsStep from './LoanDetailsStep';
import ReviewSubmitStep from './ReviewSubmitStep';

/**
 * Exports the main container component for the multi-step loan application form process.
 * This component orchestrates the different form steps, handles navigation, manages form state, and handles form submission.
 */
export { ApplicationFormContainer };

/**
 * Exports the component for the first step of the application form, which collects borrower information.
 * This includes personal details, contact information, citizenship status, address, and housing details.
 */
export { BorrowerInfoStep };

/**
 * Exports the component for the second step of the application form, which collects employment information.
 * This includes employment type, employer details, occupation, income information, and other financial data.
 */
export { EmploymentInfoStep };

/**
 * Exports the component for the third step of the application form, which collects co-borrower information.
 * This step is conditional and only rendered if the applicant indicates they have a co-borrower.
 */
export { CoBorrowerInfoStep };

/**
 * Exports the component for the fourth step of the application form, which collects loan details.
 * This includes school and program selection, start and completion dates, tuition amount, and requested loan amount.
 */
export { LoanDetailsStep };

/**
 * Exports the component for the final step of the application form, which allows the applicant to review all information
 * and submit the application. This step also includes terms and conditions acceptance.
 */
export { ReviewSubmitStep };