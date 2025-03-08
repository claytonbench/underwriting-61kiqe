# Loan Management System Frontend

Frontend application for the educational loan management system, built with React, TypeScript, and Material-UI. This application provides interfaces for borrowers, co-borrowers, school administrators, underwriters, QC personnel, and system administrators to manage the entire loan application lifecycle.

## Features

- User authentication and role-based access control
- Multi-step loan application process
- School and program management
- Underwriting workflow
- Document generation and e-signature integration
- Quality control review process
- Funding management
- Reporting and analytics
- Email notification templates
- Responsive design for various devices

## Technology Stack

- **React 18+**: Component-based UI library
- **TypeScript**: Static typing for improved code quality
- **Redux Toolkit**: State management with simplified Redux setup
- **Material-UI 5**: UI component framework
- **React Router 6**: Client-side routing
- **Formik**: Form management
- **Yup**: Schema-based form validation
- **Axios**: HTTP client for API requests
- **Auth0**: Authentication provider integration
- **Jest & Testing Library**: Unit and integration testing
- **Cypress**: End-to-end testing

## Project Structure

```
src/
├── api/                # API integration functions
├── assets/             # Static assets (images, fonts, etc.)
├── components/         # Reusable UI components
│   ├── common/         # Generic UI components
│   ├── FormElements/   # Form-specific components
│   └── [feature]/      # Feature-specific components
├── config/             # Application configuration
├── context/            # React context providers
├── hooks/              # Custom React hooks
├── layouts/            # Page layout components
├── pages/              # Page components organized by feature
├── responsive/         # Responsive design utilities
├── store/              # Redux store configuration
│   ├── actions/        # Redux actions
│   ├── reducers/       # Redux reducers
│   ├── slices/         # Redux Toolkit slices
│   └── thunks/         # Async Redux thunks
├── types/              # TypeScript type definitions
└── utils/              # Utility functions
```

## Getting Started

### Prerequisites

- Node.js 16.0.0 or later
- npm 8.0.0 or later
- Git

### Installation

1. Clone the repository
   ```bash
   git clone [repository-url]
   cd [repository-name]/src/web
   ```

2. Install dependencies
   ```bash
   npm install
   ```

3. Set up environment variables
   ```bash
   cp .env.example .env.development.local
   ```
   Edit `.env.development.local` with your local configuration.

### Development

- Start the development server
  ```bash
  npm start
  ```

- Run tests
  ```bash
  npm test
  ```

- Lint code
  ```bash
  npm run lint
  ```

- Format code
  ```bash
  npm run format
  ```

### Building for Production

```bash
npm run build
```

The build artifacts will be stored in the `build/` directory.

## Key Concepts

### Authentication and Authorization

The application uses Auth0 for authentication and implements role-based access control. User roles include:

- Borrower
- Co-Borrower
- School Administrator
- Underwriter
- Quality Control (QC)
- System Administrator

Routes are protected based on user roles, and components conditionally render UI elements based on permissions.

### State Management

Redux is used for global state management with the following structure:

- **Slices**: Feature-based state slices using Redux Toolkit
- **Thunks**: Async actions for API interactions
- **Selectors**: Memoized selectors for accessing state

### API Integration

API calls are organized by domain in the `api/` directory. Each module provides functions for interacting with specific backend endpoints.

### Form Handling

Forms are built using Formik with Yup schema validation. Complex forms (like the loan application) are broken down into steps with state persistence.

### Routing

Routing is configured in `config/routes.ts` with role-based access control. The `AppRouter` component in `pages/index.tsx` handles route rendering and authentication checks.

## Testing

### Unit and Integration Tests

Jest and React Testing Library are used for unit and integration tests. Tests are co-located with the components they test.

```bash
# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch
```

### End-to-End Tests

Cypress is used for end-to-end testing.

```bash
# Open Cypress test runner
npm run cypress:open

# Run Cypress tests headlessly
npm run cypress:run
```

## Storybook

Storybook is used for component development and documentation.

```bash
# Start Storybook
npm run storybook

# Build Storybook
npm run build-storybook
```

## Deployment

The application is deployed using Docker and AWS ECS. See the infrastructure documentation for details on the deployment process.

## Contributing

### Code Style

The project uses ESLint and Prettier for code formatting. Configuration is in `.eslintrc.js` and `.prettierrc`.

### Pull Request Process

1. Ensure all tests pass
2. Update documentation if necessary
3. Submit a pull request with a clear description of the changes

### Branch Naming Convention

- `feature/[feature-name]` for new features
- `bugfix/[bug-name]` for bug fixes
- `hotfix/[hotfix-name]` for critical fixes
- `refactor/[refactor-name]` for code refactoring

## Additional Resources

- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Redux Toolkit Documentation](https://redux-toolkit.js.org/introduction/getting-started)
- [Material-UI Documentation](https://mui.com/getting-started/usage/)
- [Formik Documentation](https://formik.org/docs/overview)
- [Auth0 React SDK Documentation](https://auth0.com/docs/quickstart/spa/react)