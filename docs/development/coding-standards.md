## Introduction

This document outlines the coding standards and best practices for the loan management system. Following these standards ensures code consistency, maintainability, and quality across the project. All developers contributing to the project are expected to adhere to these standards.

The loan management system is built using Python/Django for the backend and TypeScript/React for the frontend. This document covers standards for both components, as well as general principles that apply to the entire codebase.

## General Principles

These principles apply to all code in the project, regardless of language or framework.

### Code Readability

- Write code that is easy to read and understand
- Use meaningful variable and function names
- Keep functions and methods focused on a single responsibility
- Limit function/method length (aim for < 50 lines)
- Use comments to explain why, not what (the code should be self-explanatory)
- Document complex algorithms and business logic

### Code Organization

- Follow the project's folder structure and file naming conventions
- Group related functionality together
- Separate concerns appropriately (e.g., business logic from presentation)
- Keep files focused on a single responsibility
- Limit file size (aim for < 500 lines)

### Documentation

- Document all public APIs, classes, and functions
- Include purpose, parameters, return values, and exceptions
- Keep documentation up-to-date with code changes
- Use clear, concise language in documentation
- Include examples for complex functionality

### Version Control

- Write clear, descriptive commit messages
- Use the format: `[Component] Brief description of change`
- Keep commits focused on a single logical change
- Reference issue numbers in commit messages when applicable
- Create feature branches from `develop` using the format:
  - `feature/feature-name` for new features
  - `bugfix/issue-description` for bug fixes
  - `hotfix/issue-description` for critical fixes
- Squash commits before merging when appropriate

### Code Review

- All code must be reviewed before merging
- Reviewers should check for:
  - Adherence to coding standards
  - Potential bugs or edge cases
  - Test coverage
  - Documentation completeness
  - Performance considerations
  - Security implications
- Address all review comments before merging
- Be constructive and respectful in code reviews

## Backend (Python/Django) Standards

These standards apply to all Python code in the project, including Django applications, utilities, and scripts.

### Python Style Guide

- Follow PEP 8 style guide with the following modifications:
  - Maximum line length: 100 characters
  - Use double quotes for docstrings, single quotes for strings
- Use Black for code formatting with a line length of 100
- Use isort for import sorting with the Black profile
- Follow Django's style guide for Django-specific code

### Code Formatting

- Use Black to format all Python code
  - Configuration: `black --line-length 100`
  - CI will enforce Black formatting
- Use isort to sort imports
  - Configuration: `isort --profile black --line-length 100`
  - Imports should be grouped in the following order:
    1. Standard library imports
    2. Related third-party imports
    3. Local application/library specific imports
- Format code before committing using pre-commit hooks or IDE integration

### Linting

- Use flake8 for linting Python code
- Configuration is in `.flake8` file with the following settings:
  - `max-line-length = 100`
  - `max-complexity = 15`
  - Ignored rules: E203, E231, E501, W503, F401, F403
- Fix all linting errors before committing
- CI will enforce linting rules

### Type Annotations

- Use type annotations for all function parameters and return values
- Use mypy for static type checking
- Configuration is in `setup.cfg` under the `[mypy]` section
- Type annotations should be as specific as possible
- Use typing module for complex types (List, Dict, Optional, etc.)
- Example:
  ```python
  from typing import List, Dict, Optional

  def process_applications(applications: List[Application], status: Optional[str] = None) -> Dict[str, int]:
      # Function implementation
      return result
  ```

### Django Best Practices

- Follow Django's MTV (Model-Template-View) architecture
- Organize apps by domain functionality
- Keep views focused on HTTP request/response handling
- Use services for complex business logic
- Use Django REST Framework for API endpoints
- Follow Django's security best practices
- Use Django's ORM effectively:
  - Define appropriate indexes
  - Use select_related and prefetch_related to avoid N+1 queries
  - Use QuerySet methods instead of Python loops when possible
- Use Django's form validation for data validation

### Model Design

- Use meaningful model names (singular, CamelCase)
- Define `__str__` methods for all models
- Use appropriate field types
- Define indexes for frequently queried fields
- Use model managers for custom query logic
- Define related_name for all relationships
- Use abstract base classes for common fields
- Example:
  ```python
  class Application(TimeStampedModel):
      """Represents a loan application in the system."""
      borrower = models.ForeignKey(
          'users.User',
          on_delete=models.PROTECT,
          related_name='applications',
      )
      school = models.ForeignKey(
          'schools.School',
          on_delete=models.PROTECT,
          related_name='applications',
      )
      status = models.CharField(
          max_length=20,
          choices=APPLICATION_STATUS_CHOICES,
          default=APPLICATION_STATUS_DRAFT,
          db_index=True,
      )
      
      objects = ApplicationManager()
      
      class Meta:
          ordering = ['-created_at']
          indexes = [
              models.Index(fields=['status', 'created_at']),
          ]
      
      def __str__(self) -> str:
          return f"Application {self.id} - {self.borrower.full_name}"
  ```

### API Design

- Use Django REST Framework for API endpoints
- Follow RESTful principles
- Use ViewSets and Routers when appropriate
- Use serializers for data validation and transformation
- Implement proper permission classes
- Use pagination for list endpoints
- Document APIs using docstrings or OpenAPI/Swagger
- Use consistent response formats
- Handle errors gracefully with appropriate status codes
- Example:
  ```python
  class ApplicationViewSet(viewsets.ModelViewSet):
      """ViewSet for managing loan applications."""
      serializer_class = ApplicationSerializer
      permission_classes = [IsAuthenticated, ApplicationPermission]
      filterset_class = ApplicationFilter
      pagination_class = StandardResultsSetPagination
      
      def get_queryset(self):
          """Return applications based on user role."""
          user = self.request.user
          if user.is_staff or user.has_role('underwriter'):
              return Application.objects.all()
          if user.has_role('school_admin'):
              return Application.objects.filter(school__in=user.schools.all())
          return Application.objects.filter(borrower=user)
  ```

### Testing

- Write tests for all functionality
- Aim for at least 80% code coverage
- Use pytest as the testing framework
- Organize tests by type (unit, integration, etc.)
- Use descriptive test names: `test_<function_name>_<scenario_description>`
- Use fixtures for test data
- Mock external dependencies
- Test both success and failure cases
- Test edge cases and boundary conditions
- Example:
  ```python
  @pytest.mark.unit
  def test_calculate_loan_amount_with_valid_inputs():
      # Arrange
      tuition = Decimal('10000.00')
      deposit = Decimal('1000.00')
      other_funding = Decimal('2000.00')
      
      # Act
      result = calculate_loan_amount(tuition, deposit, other_funding)
      
      # Assert
      assert result == Decimal('7000.00')
      
  @pytest.mark.unit
  def test_calculate_loan_amount_with_zero_tuition_raises_error():
      # Arrange
      tuition = Decimal('0.00')
      deposit = Decimal('1000.00')
      other_funding = Decimal('2000.00')
      
      # Act/Assert
      with pytest.raises(ValueError, match="Tuition must be greater than zero"):
          calculate_loan_amount(tuition, deposit, other_funding)
  ```

- **Test Organization**:
  - Place tests in a `tests` directory within each app
  - Group tests by test type and functionality
  - Use pytest markers to categorize tests: `@pytest.mark.unit`, `@pytest.mark.integration`
  - Create common fixtures in `conftest.py` files

- **Test Data Management**:
  - Use factories (FactoryBoy) for creating test data
  - Use fixtures for reusable test data setup
  - Clean up test data after tests complete
  - Use a separate test database

- **Mocking Strategy**:
  - Use pytest-mock for mocking
  - Mock external services and APIs
  - Use MagicMock for creating mock objects
  - Set appropriate return values and side effects for mocks

### Documentation

- Use docstrings for all modules, classes, and functions
- Follow Google-style docstring format
- Include purpose, parameters, return values, and exceptions
- Document complex algorithms and business logic
- Example:
  ```python
  def calculate_loan_amount(tuition: Decimal, deposit: Decimal, other_funding: Decimal) -> Decimal:
      """Calculate the loan amount based on tuition, deposit, and other funding.
      
      Args:
          tuition: The total tuition amount
          deposit: The deposit amount paid by the borrower
          other_funding: Amount from other funding sources
          
      Returns:
          The calculated loan amount (tuition - deposit - other_funding)
          
      Raises:
          ValueError: If tuition is zero or negative
          ValueError: If calculated loan amount is negative
      """
      if tuition <= 0:
          raise ValueError("Tuition must be greater than zero")
          
      loan_amount = tuition - deposit - other_funding
      
      if loan_amount < 0:
          raise ValueError("Calculated loan amount cannot be negative")
          
      return loan_amount
  ```

## Frontend (TypeScript/React) Standards

These standards apply to all TypeScript and React code in the project.

### TypeScript Style Guide

- Use TypeScript for all frontend code
- Follow the ESLint configuration defined in `.eslintrc.js`
- Use Prettier for code formatting with configuration in `.prettierrc`
- Use strong typing with interfaces and types
- Avoid using `any` type when possible
- Use functional components with hooks instead of class components
- Use async/await for asynchronous code instead of promises

### Code Formatting

- Use Prettier to format all TypeScript/JavaScript code
- Configuration is in `.prettierrc` with the following settings:
  - `printWidth: 100`
  - `tabWidth: 2`
  - `useTabs: false`
  - `semi: true`
  - `singleQuote: true`
  - `jsxSingleQuote: false`
  - `trailingComma: 'es5'`
  - `bracketSpacing: true`
  - `bracketSameLine: false`
  - `arrowParens: 'avoid'`
  - `endOfLine: 'lf'`
- Format code before committing using pre-commit hooks or IDE integration
- CI will enforce Prettier formatting

### Linting

- Use ESLint for linting TypeScript/JavaScript code
- Configuration is in `.eslintrc.js`
- Key rules include:
  - No console statements (except warn and error)
  - No unused variables
  - React hooks rules
  - Import ordering
  - Accessibility (jsx-a11y) rules
- Fix all linting errors before committing
- CI will enforce linting rules

### Type Definitions

- Define interfaces and types in dedicated files
- Use descriptive names for types and interfaces
- Export types from a central location when shared
- Use TypeScript's utility types when appropriate (Partial, Pick, Omit, etc.)
- Example:
  ```typescript
  // types/application.types.ts
  export interface Application {
    id: string;
    borrower: User;
    school: School;
    program: Program;
    status: ApplicationStatus;
    submissionDate: string;
    requestedAmount: number;
    approvedAmount?: number;
  }
  
  export type ApplicationStatus = 
    | 'draft'
    | 'submitted'
    | 'in_review'
    | 'approved'
    | 'denied'
    | 'revision_requested';
  
  export interface ApplicationFormData {
    schoolId: string;
    programId: string;
    tuitionAmount: number;
    depositAmount: number;
    otherFunding: number;
    requestedAmount: number;
    startDate: string;
  }
  ```

### React Best Practices

- Use functional components with hooks
- Keep components focused on a single responsibility
- Use proper component composition
- Avoid prop drilling (use context or state management)
- Use React.memo for performance optimization when appropriate
- Use custom hooks to share logic between components
- Follow the React component file structure:
  ```
  ComponentName/
    ├── ComponentName.tsx
    ├── styles.ts
    ├── index.ts
    └── tests/
        └── ComponentName.test.tsx
  ```
- Example component:
  ```typescript
  // ApplicationForm/ApplicationForm.tsx
  import React, { useState } from 'react';
  import { useFormik } from 'formik';
  import { ApplicationFormData } from 'types/application.types';
  import { applicationValidationSchema } from './validation';
  import { useStyles } from './styles';
  
  interface ApplicationFormProps {
    initialValues?: Partial<ApplicationFormData>;
    onSubmit: (values: ApplicationFormData) => void;
    isLoading?: boolean;
  }
  
  export const ApplicationForm: React.FC<ApplicationFormProps> = ({
    initialValues = {},
    onSubmit,
    isLoading = false,
  }) => {
    const classes = useStyles();
    const formik = useFormik({
      initialValues: {
        schoolId: '',
        programId: '',
        tuitionAmount: 0,
        depositAmount: 0,
        otherFunding: 0,
        requestedAmount: 0,
        startDate: '',
        ...initialValues,
      },
      validationSchema: applicationValidationSchema,
      onSubmit,
    });
    
    // Component implementation
    
    return (
      <form onSubmit={formik.handleSubmit} className={classes.form}>
        {/* Form fields */}
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Submitting...' : 'Submit'}
        </Button>
      </form>
    );
  };
  ```

### State Management

- Use Redux with Redux Toolkit for global state management
- Use React Context for theme, authentication, and other app-wide concerns
- Use local component state for UI-specific state
- Follow the Redux Toolkit pattern with slices
- Use createAsyncThunk for async actions
- Use selectors for accessing state
- Example:
  ```typescript
  // store/slices/applicationSlice.ts
  import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
  import { Application, ApplicationFormData } from 'types/application.types';
  import { applicationApi } from 'api/applications';
  
  interface ApplicationState {
    applications: Application[];
    currentApplication: Application | null;
    loading: boolean;
    error: string | null;
  }
  
  const initialState: ApplicationState = {
    applications: [],
    currentApplication: null,
    loading: false,
    error: null,
  };
  
  export const fetchApplications = createAsyncThunk(
    'applications/fetchApplications',
    async (_, { rejectWithValue }) => {
      try {
        const response = await applicationApi.getApplications();
        return response.data;
      } catch (error) {
        return rejectWithValue(error.response?.data?.message || 'Failed to fetch applications');
      }
    }
  );
  
  const applicationSlice = createSlice({
    name: 'applications',
    initialState,
    reducers: {
      setCurrentApplication: (state, action: PayloadAction<Application>) => {
        state.currentApplication = action.payload;
      },
      clearCurrentApplication: (state) => {
        state.currentApplication = null;
      },
    },
    extraReducers: (builder) => {
      builder
        .addCase(fetchApplications.pending, (state) => {
          state.loading = true;
          state.error = null;
        })
        .addCase(fetchApplications.fulfilled, (state, action) => {
          state.applications = action.payload;
          state.loading = false;
        })
        .addCase(fetchApplications.rejected, (state, action) => {
          state.loading = false;
          state.error = action.payload as string;
        });
    },
  });
  
  export const { setCurrentApplication, clearCurrentApplication } = applicationSlice.actions;
  export default applicationSlice.reducer;
  ```

### API Integration

- Use Axios for API requests
- Create API service modules for each resource
- Handle errors consistently
- Use TypeScript types for request and response data
- Implement request/response interceptors for common concerns
- Example:
  ```typescript
  // api/applications.ts
  import axios from 'axios';
  import { Application, ApplicationFormData } from 'types/application.types';
  import { API_BASE_URL } from 'config/constants';
  
  const API_PATH = `${API_BASE_URL}/applications`;
  
  export const applicationApi = {
    getApplications: () => {
      return axios.get<Application[]>(API_PATH);
    },
    
    getApplication: (id: string) => {
      return axios.get<Application>(`${API_PATH}/${id}`);
    },
    
    createApplication: (data: ApplicationFormData) => {
      return axios.post<Application>(API_PATH, data);
    },
    
    updateApplication: (id: string, data: Partial<ApplicationFormData>) => {
      return axios.put<Application>(`${API_PATH}/${id}`, data);
    },
    
    deleteApplication: (id: string) => {
      return axios.delete(`${API_PATH}/${id}`);
    },
  };
  ```

### Testing

- Write tests for all components and utilities
- Aim for at least 70% code coverage
- Use Jest and React Testing Library
- Test component rendering and interactions
- Mock API calls and external dependencies
- Use descriptive test names: `should <expected behavior> when <condition>`
- Example:
  ```typescript
  // ApplicationForm/tests/ApplicationForm.test.tsx
  import React from 'react';
  import { render, screen, fireEvent, waitFor } from '@testing-library/react';
  import { ApplicationForm } from '../ApplicationForm';
  
  describe('ApplicationForm', () => {
    const mockSubmit = jest.fn();
    
    beforeEach(() => {
      mockSubmit.mockClear();
    });
    
    it('should render the form with empty values by default', () => {
      render(<ApplicationForm onSubmit={mockSubmit} />);
      
      expect(screen.getByLabelText(/school/i)).toHaveValue('');
      expect(screen.getByLabelText(/program/i)).toHaveValue('');
      expect(screen.getByLabelText(/tuition amount/i)).toHaveValue('0');
      expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
    });
    
    it('should call onSubmit with form values when submitted', async () => {
      render(<ApplicationForm onSubmit={mockSubmit} />);
      
      fireEvent.change(screen.getByLabelText(/school/i), { target: { value: 'school-1' } });
      fireEvent.change(screen.getByLabelText(/program/i), { target: { value: 'program-1' } });
      fireEvent.change(screen.getByLabelText(/tuition amount/i), { target: { value: '10000' } });
      
      fireEvent.click(screen.getByRole('button', { name: /submit/i }));
      
      await waitFor(() => {
        expect(mockSubmit).toHaveBeenCalledWith({
          schoolId: 'school-1',
          programId: 'program-1',
          tuitionAmount: 10000,
          depositAmount: 0,
          otherFunding: 0,
          requestedAmount: 0,
          startDate: '',
        });
      });
    });
  });
  ```

- **Component Testing Best Practices**:
  - Test behavior, not implementation details
  - Use `render`, `screen`, and `fireEvent` from React Testing Library
  - Use `userEvent` for more realistic user interactions
  - Test accessibility with appropriate queries (`getByRole`)
  - Mock API calls and external dependencies
  - Test error states and loading states

- **Redux Testing**:
  - Test slices, reducers, and selectors independently
  - Test async thunks with mock API responses
  - Use redux-mock-store for testing connected components

- **Test Organization**:
  - Place tests in a `tests` directory within each component folder
  - Name test files with `.test.tsx` or `.spec.tsx` extension
  - Group related tests with `describe` blocks
  - Use clear test names that describe behavior

### Accessibility

- Follow WCAG 2.1 AA standards
- Use semantic HTML elements
- Include proper ARIA attributes when needed
- Ensure keyboard navigation works for all interactive elements
- Maintain sufficient color contrast
- Provide text alternatives for non-text content
- Test with screen readers
- Use the jsx-a11y ESLint plugin to catch common accessibility issues
- Example:
  ```typescript
  // Accessible form field
  <div>
    <label htmlFor="name-input" id="name-label">Full Name</label>
    <input
      id="name-input"
      aria-labelledby="name-label"
      aria-required="true"
      type="text"
      value={name}
      onChange={handleNameChange}
    />
    {nameError && (
      <div role="alert" className="error-message">
        {nameError}
      </div>
    )}
  </div>
  ```

## Database Standards

These standards apply to database design, migrations, and queries.

### Database Design

- Use meaningful table and column names
- Follow Django's naming conventions for tables and fields
- Use appropriate data types for columns
- Define proper indexes for frequently queried fields
- Use foreign keys to enforce referential integrity
- Normalize data to appropriate level (usually 3NF)
- Use Django migrations for schema changes

### Migrations

- Create migrations using Django's migration framework
- Review migrations before applying them
- Test migrations on development before applying to production
- Keep migrations small and focused
- Include data migrations when necessary
- Document complex migrations
- Never modify applied migrations
- Example:
  ```python
  # migrations/0002_add_application_status_index.py
  from django.db import migrations, models
  
  class Migration(migrations.Migration):
      dependencies = [
          ('applications', '0001_initial'),
      ]
      
      operations = [
          migrations.AddIndex(
              model_name='application',
              index=models.Index(fields=['status', 'created_at'], name='app_status_created_idx'),
          ),
      ]
  ```

### Query Optimization

- Use Django's ORM effectively
- Use `select_related` and `prefetch_related` to avoid N+1 queries
- Use `values` and `values_list` for simple data retrieval
- Use `only` and `defer` to limit retrieved fields when appropriate
- Use `bulk_create` and `bulk_update` for batch operations
- Use query annotations and aggregations for complex calculations
- Monitor and optimize slow queries
- Example:
  ```python
  # Inefficient
  applications = Application.objects.filter(status='approved')
  for application in applications:
      print(application.borrower.email)  # N+1 query problem
  
  # Efficient
  applications = Application.objects.filter(status='approved').select_related('borrower')
  for application in applications:
      print(application.borrower.email)  # No additional query
  ```

## Security Standards

These standards help ensure the security of the application.

### Authentication and Authorization

- Use Auth0 for authentication
- Implement proper role-based access control
- Validate permissions for all operations
- Use secure password storage (handled by Auth0)
- Implement proper session management
- Use JWT tokens with appropriate expiration
- Validate tokens on every request
- Example:
  ```python
  # permissions.py
  from rest_framework import permissions
  
  class ApplicationPermission(permissions.BasePermission):
      """Permission class for application resources."""
      
      def has_permission(self, request, view):
          # Allow authenticated users to list and create
          return request.user.is_authenticated
      
      def has_object_permission(self, request, view, obj):
          user = request.user
          
          # Staff and underwriters can access all applications
          if user.is_staff or user.has_role('underwriter'):
              return True
              
          # School admins can access applications for their schools
          if user.has_role('school_admin') and obj.school in user.schools.all():
              return True
              
          # Borrowers can access their own applications
          return obj.borrower == user
  ```

### Data Protection

- Encrypt sensitive data at rest
- Use HTTPS for all communications
- Implement proper input validation
- Sanitize user inputs to prevent injection attacks
- Use parameterized queries to prevent SQL injection
- Implement proper error handling to avoid information leakage
- Follow the principle of least privilege
- Example:
  ```python
  # models.py
  from django.db import models
  from utils.encryption import encrypt_field, decrypt_field
  
  class BorrowerProfile(models.Model):
      user = models.OneToOneField('users.User', on_delete=models.CASCADE)
      _ssn = models.CharField(max_length=255, db_column='ssn')  # Encrypted in DB
      
      @property
      def ssn(self):
          """Decrypt SSN when accessed."""
          return decrypt_field(self._ssn)
      
      @ssn.setter
      def ssn(self, value):
          """Encrypt SSN when set."""
          self._ssn = encrypt_field(value)
  ```

### Security Headers

- Implement proper security headers:
  - Content-Security-Policy
  - X-Content-Type-Options
  - X-Frame-Options
  - X-XSS-Protection
  - Strict-Transport-Security
- Use Django's security middleware
- Configure proper CORS settings
- Example:
  ```python
  # settings/base.py
  MIDDLEWARE = [
      # ...
      'django.middleware.security.SecurityMiddleware',
      # ...
  ]
  
  SECURE_BROWSER_XSS_FILTER = True
  SECURE_CONTENT_TYPE_NOSNIFF = True
  X_FRAME_OPTIONS = 'DENY'
  SECURE_HSTS_SECONDS = 31536000  # 1 year
  SECURE_HSTS_INCLUDE_SUBDOMAINS = True
  SECURE_HSTS_PRELOAD = True
  
  # In production
  SECURE_SSL_REDIRECT = True
  SESSION_COOKIE_SECURE = True
  CSRF_COOKIE_SECURE = True
  ```

### Dependency Management

- Regularly update dependencies
- Use dependabot for automated updates
- Scan dependencies for vulnerabilities
- Pin dependency versions
- Review security advisories for used packages
- Example:
  ```
  # requirements.txt
  Django==4.2.1
  djangorestframework==3.14.0
  psycopg2-binary==2.9.6
  pyjwt==2.6.0
  cryptography==40.0.2
  ```

## Performance Standards

These standards help ensure the application performs well under load.

### Backend Performance

- Optimize database queries
- Use caching appropriately
- Implement pagination for list endpoints
- Use asynchronous processing for long-running tasks
- Optimize file uploads and downloads
- Monitor and optimize API response times
- Example:
  ```python
  # views.py
  from django.utils.decorators import method_decorator
  from django.views.decorators.cache import cache_page
  
  class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
      queryset = School.objects.all()
      serializer_class = SchoolSerializer
      
      @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
      def list(self, request, *args, **kwargs):
          return super().list(request, *args, **kwargs)
  ```

### Frontend Performance

- Use code splitting to reduce bundle size
- Implement lazy loading for components
- Optimize images and assets
- Minimize re-renders
- Use memoization for expensive calculations
- Implement virtualization for long lists
- Example:
  ```typescript
  // Lazy loading components
  import React, { lazy, Suspense } from 'react';
  
  const Dashboard = lazy(() => import('./pages/Dashboard'));
  const ApplicationForm = lazy(() => import('./pages/ApplicationForm'));
  
  const App: React.FC = () => {
    return (
      <Router>
        <Suspense fallback={<div>Loading...</div>}>
          <Switch>
            <Route path="/dashboard" component={Dashboard} />
            <Route path="/applications/new" component={ApplicationForm} />
            {/* Other routes */}
          </Switch>
        </Suspense>
      </Router>
    );
  };
  ```

### Caching Strategy

- Use Redis for caching
- Cache frequently accessed data
- Implement proper cache invalidation
- Use ETags for API responses
- Implement browser caching for static assets
- Use CDN for static content delivery
- Example:
  ```python
  # services.py
  from django.core.cache import cache
  
  def get_school_programs(school_id):
      cache_key = f'school_programs_{school_id}'
      programs = cache.get(cache_key)
      
      if programs is None:
          programs = Program.objects.filter(school_id=school_id).values('id', 'name', 'tuition_amount')
          cache.set(cache_key, list(programs), 60 * 60)  # Cache for 1 hour
          
      return programs
  ```

## Tooling and Automation

These tools and automation processes help enforce coding standards.

### Code Formatting Tools

- **Backend**:
  - Black: `black --line-length 100 .`
  - isort: `isort --profile black --line-length 100 .`

- **Frontend**:
  - Prettier: `prettier --write "src/**/*.{ts,tsx,js,jsx,json,css,scss}"`

These tools can be run manually or integrated into your IDE.

### Linting Tools

- **Backend**:
  - flake8: `flake8 .`
  - mypy: `mypy .`

- **Frontend**:
  - ESLint: `eslint "src/**/*.{ts,tsx,js,jsx}"`
  - TypeScript: `tsc --noEmit`

These tools can be run manually or integrated into your IDE.

### Pre-commit Hooks

Pre-commit hooks automatically check code before committing:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        args: [--line-length=100]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black, --line-length=100]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v2.8.8
    hooks:
      - id: prettier
        types_or: [javascript, typescript, jsx, tsx, json, css]

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.40.0
    hooks:
      - id: eslint
        types_or: [javascript, typescript, jsx, tsx]
        additional_dependencies:
          - eslint@8.40.0
          - typescript@5.0.4
          - '@typescript-eslint/eslint-plugin@5.59.6'
          - '@typescript-eslint/parser@5.59.6'
          - eslint-plugin-react@7.32.2
          - eslint-plugin-react-hooks@4.6.0
          - eslint-plugin-jsx-a11y@6.7.1
          - eslint-plugin-import@2.27.5
          - eslint-config-prettier@8.8.0
```

Install pre-commit hooks with:
```bash
pip install pre-commit
pre-commit install