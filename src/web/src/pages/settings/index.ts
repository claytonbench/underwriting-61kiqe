// A barrel file that exports all settings-related page components from the settings directory.
// This file simplifies imports by allowing consumers to import multiple settings components from a single path.

// Import the EmailTemplates component from its file
import EmailTemplates from './EmailTemplates';
// Import the EditEmailTemplate component from its file
import EditEmailTemplate from './EditEmailTemplate';
// Import the ProfileSettings component from its file
import ProfileSettings from './ProfileSettings';
// Import the SystemSettings component from its file
import SystemSettings from './SystemSettings';

// Export the EmailTemplates component as a named export
export { EmailTemplates };
// Export the EditEmailTemplate component as a named export
export { EditEmailTemplate };
// Export the ProfileSettings component as a named export
export { ProfileSettings };
// Export the SystemSettings component as a named export
export { SystemSettings };