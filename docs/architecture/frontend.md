# Frontend Architecture

## Overview

The Frontend Architecture for the Loan Management System is built on a modern, component-based stack with React as its foundation, enhanced with TypeScript for type safety and Redux for state management. The architecture follows a modular approach with clear separation of concerns, making it maintainable, scalable, and robust.

The UI is designed to support multiple user roles, including borrowers, co-borrowers, school administrators, underwriters, quality control personnel, and system administrators. Each role has access to specific features and workflows through a comprehensive role-based access control system.

### Architecture Principles

The frontend architecture is guided by the following principles:

1. **Component-Based Design**: The UI is composed of reusable, self-contained components that encapsulate their own logic and styling.

2. **Type Safety**: TypeScript ensures type safety throughout the application, improving code quality, developer experience, and catching errors at compile time.

3. **Centralized State Management**: Redux provides predictable state management with well-defined actions and reducers for complex application workflows.

4. **Separation of Concerns**: Clear boundaries between UI components, business logic, and data access layers enhance maintainability.

5. **Feature-Based Organization**: Code is organized by feature rather than technical type, making related code easier to locate and understand.

6. **Progressive Loading**: Code splitting and lazy loading ensure that only necessary code is loaded when needed, improving initial load times.

7. **Responsive Design**: The UI adapts to different screen sizes, with a focus on desktop while maintaining usability on tablets.

8. **Accessibility**: WCAG 2.1 AA compliance is maintained throughout the application for inclusive user experience.

### Key Design Decisions

1. **React + TypeScript**: React provides a powerful component model, while TypeScript adds static typing to catch errors early and improve developer experience.

2. **Redux + Redux Toolkit**: Redux provides predictable state management, while Redux Toolkit simplifies common Redux patterns and reduces boilerplate.

3. **Material-UI**: Provides a comprehensive component library with built-in accessibility and consistent styling according to Material Design principles.

4. **Formik + Yup**: Simplifies form management and validation, critical for the complex forms in loan applications.

5. **React Router**: Handles routing with support for nested routes and protected routes based on user roles.

6. **Axios**: Provides a robust API client with interceptors for authentication and error handling.

7. **Jest + Testing Library**: Enables comprehensive testing of components and business logic with a focus on user interactions.

## Technology Stack

### Core Technologies

- **React 18.2.0**: A JavaScript library for building user interfaces with a component-based architecture and virtual DOM for efficient rendering.

- **TypeScript 5.1.6**: A typed superset of JavaScript that compiles to plain JavaScript, providing static type checking to improve code quality and developer experience.

- **Redux 4.2.1**: A predictable state container for JavaScript apps, providing centralized state management.

- **Redux Toolkit 1.9.5**: The official, opinionated toolset for efficient Redux development, simplifying common Redux use cases and reducing boilerplate.

- **React Redux 8.1.1**: Official React bindings for Redux, allowing React components to interact with the Redux store through hooks and higher-order components.

### UI Framework

- **Material-UI 5.14.0**: A comprehensive React UI framework implementing Google's Material Design guidelines.

- **@mui/material**: Core Material-UI components for building the UI.

- **@mui/icons-material**: Material Design icons used throughout the application.

- **@mui/system**: Styling utilities and theme management for consistent design.

- **@emotion/react 11.11.1**: CSS-in-JS library used by Material-UI for styling components.

- **@emotion/styled 11.11.0**: Styled component API for Emotion, enabling component-based styling.

### Form Management

- **Formik 2.4.2**: A form management library that simplifies form state, validation, and submission handling.

- **Yup 1.2.0**: A schema validation library that integrates with Formik for robust form validation.

- **react-datepicker 4.16.0**: A flexible date picker component for form date fields.

- **react-dropzone 14.2.3**: A React hook for creating file drop zones for document uploads.

### Routing

- **React Router 6.14.1**: Declarative routing for React applications, enabling navigation between different components.

- **React Router DOM 6.14.1**: DOM bindings for React Router.

- **@reach/router 1.3.4**: Complementary routing library for accessible routing features.

### HTTP Client

- **Axios 1.4.0**: Promise-based HTTP client for making API requests with interceptors for authentication and error handling.

- **axios-retry 3.5.0**: Axios plugin adding retry capability for failed requests to improve resilience.

- **axios-case-converter 1.1.0**: Middleware for converting between camelCase and snake_case in requests/responses for seamless API integration.

### Development Tools

- **Create React App 5.0.1**: Tool to bootstrap React applications with optimal defaults.

- **Craco 7.1.0**: Configuration layer for Create React App to customize webpack config without ejecting.

- **ESLint 8.44.0**: Linting utility for JavaScript and TypeScript to maintain code quality.

- **Prettier 3.0.0**: Code formatter to ensure consistent code style.

- **Husky 8.0.3**: Git hooks tool for running linters and tests before commits.

- **lint-staged 13.2.3**: Run linters on staged git files for pre-commit quality checks.

- **Jest 29.6.1**: JavaScript testing framework for unit and integration tests.

- **@testing-library/react 14.0.0**: React testing utilities encouraging good testing practices.

- **Cypress 12.17.1**: End-to-end testing framework for testing the application as a user would.

- **Storybook 7.1.0**: Development environment for UI components with isolated component development and documentation.

## Application Structure

### Directory Structure

The frontend codebase follows a feature-based organization with shared components and utilities:

```
src/
│
├── assets/               # Static assets like images, fonts, etc.
│
├── components/           # Shared components used across features
│   ├── common/           # General UI components
│   ├── forms/            # Reusable form components
│   ├── layout/           # Layout components (Header, Footer, etc.)
│   └── data-display/     # Tables, cards, and other data display components
│
├── config/               # Configuration files
│   ├── constants.ts      # Application constants
│   ├── routes.ts         # Route definitions
│   └── theme.ts          # Material-UI theme configuration
│
├── features/             # Feature-based modules
│   ├── auth/             # Authentication feature
│   ├── users/            # User management
│   ├── schools/          # School and program management
│   ├── applications/     # Loan application
│   ├── underwriting/     # Underwriting process
│   ├── documents/        # Document management
│   ├── funding/          # Funding process
│   └── reports/          # Reporting and analytics
│
├── hooks/                # Custom React hooks
│
├── pages/                # Page components for each route
│
├── services/             # API services and other external integrations
│   ├── api/              # API client and services
│   ├── auth/             # Authentication service
│   └── storage/          # Local storage service
│
├── store/                # Redux store configuration
│   ├── index.ts          # Store setup and middleware
│   ├── rootReducer.ts    # Root reducer combining all feature reducers
│   └── slices/           # Redux slices for different features
│
├── types/                # TypeScript type definitions
│
├── utils/                # Utility functions
│   ├── formatting.ts     # Data formatting utilities
│   ├── validation.ts     # Validation helpers
│   └── testing.ts        # Test utilities
│
├── App.tsx               # Root App component
├── index.tsx             # Application entry point
└── setupTests.ts         # Test setup
```

### Code Organization

The codebase is organized following these patterns:

1. **Feature-based Organization**: Code is grouped by feature rather than type, making it easier to locate related code and understand the application structure.

2. **Component Colocation**: Components are placed close to where they're used. Shared components go in the common directory, while feature-specific components stay in their feature folder.

3. **Barrel Files**: Each directory contains an index.ts file that exports its contents, simplifying imports and providing a clean public API.

4. **Type Colocations**: TypeScript interfaces and types are defined close to where they're used, with shared types in the types directory.

5. **Container/Presentation Pattern**: Components are separated into container components (dealing with data and logic) and presentational components (focused on UI rendering).

### Naming Conventions

The codebase follows consistent naming conventions:

1. **Files and Directories**:
   - React components: PascalCase (e.g., `UserProfile.tsx`)
   - Utility files: camelCase (e.g., `formatCurrency.ts`)
   - Test files: ComponentName.test.tsx or utilityName.test.ts
   - Story files: ComponentName.stories.tsx

2. **Components**:
   - Component names: PascalCase (e.g., `ApplicationForm`)
   - Component props interfaces: `ComponentNameProps` (e.g., `interface ButtonProps`)

3. **Redux**:
   - Slice files: camelCase with feature name (e.g., `authSlice.ts`)
   - Actions: camelCase verb + noun (e.g., `fetchUser`, `updateProfile`)
   - Selectors: `select` + entity (e.g., `selectUser`, `selectApplicationById`)

4. **Hooks**:
   - Custom hooks: `use` + descriptive name (e.g., `useAuth`, `usePagination`)

5. **Constants**:
   - Constant values: UPPER_SNAKE_CASE (e.g., `MAX_FILE_SIZE`)
   - Enums: PascalCase with values in PascalCase (e.g., `enum UserRole { Admin, Borrower }`)

## Component Architecture

### Component Hierarchy

The application's component hierarchy follows a nested structure with layout components at the top level:

```
App
├── AuthProvider
│   └── ThemeProvider
│       └── Router
│           ├── PrivateRoute
│           │   ├── DashboardLayout
│           │   │   ├── Navbar
│           │   │   ├── Sidebar
│           │   │   └── PageContent (varies by route)
│           │   │       └── Feature-specific components
│           │   └── MinimalLayout
│           │       └── PageContent (varies by route)
│           └── PublicRoute
│               └── AuthLayout
│                   └── AuthPages (Login, Register, etc.)
└── ErrorBoundary