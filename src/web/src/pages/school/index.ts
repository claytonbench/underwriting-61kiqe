// A barrel file that exports all school-related page components, providing a centralized entry point for importing school management pages throughout the application.
// This simplifies imports by allowing consumers to import from a single path rather than individual component files.

// Import SchoolList component for displaying schools
import SchoolList from './SchoolList';
// Import SchoolDetail component for viewing school details
import SchoolDetail from './SchoolDetail';
// Import SchoolNew component for creating schools
import SchoolNew from './SchoolNew';
// Import SchoolEdit component for editing schools
import SchoolEdit from './SchoolEdit';
// Import ProgramList component for displaying programs
import ProgramList from './ProgramList';
// Import ProgramDetail component for viewing program details
import ProgramDetail from './ProgramDetail';
// Import ProgramNew component for creating programs
import ProgramNew from './ProgramNew';
// Import ProgramEdit component for editing programs
import ProgramEdit from './ProgramEdit';
// Import SchoolAdminDashboard component for school administrators
import SchoolAdminDashboard from './SchoolAdminDashboard';

// Export SchoolList component for displaying schools
export { SchoolList };
// Export SchoolDetail component for viewing school details
export { SchoolDetail };
// Export SchoolNew component for creating schools
export { SchoolNew };
// Export SchoolEdit component for editing schools
export { SchoolEdit };
// Export ProgramList component for displaying programs
export { ProgramList };
// Export ProgramDetail component for viewing program details
export { ProgramDetail };
// Export ProgramNew component for creating programs
export { ProgramNew };
// Export ProgramEdit component for editing programs
export { ProgramEdit };
// Export SchoolAdminDashboard component for school administrators
export { SchoolAdminDashboard };