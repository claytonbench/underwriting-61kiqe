## Introduction

This document outlines the testing strategy and practices for the loan management system. It covers all aspects of testing, including unit testing, integration testing, end-to-end testing, and specialized testing approaches for both backend and frontend components.

The loan management system requires comprehensive testing due to its critical financial nature and the need to ensure data integrity, security, and compliance with regulations. This document provides guidelines for developers, QA engineers, and other stakeholders involved in the testing process.

## Testing Strategy Overview

The loan management system employs a multi-layered testing approach to ensure quality and reliability at all levels of the application.

### Testing Pyramid

We follow the testing pyramid approach with a focus on having a solid foundation of unit tests, complemented by integration tests and end-to-end tests:

```
                    /|\
                   /  |\
                  /E2E|\
                 /-----\|\
                /       |\
               /Integration|\
              /-------------\|\
             /               |\
            /     Unit Tests   |\
           /___________________|\
```

- **Unit Tests**: Fast, focused tests that verify individual components in isolation
- **Integration Tests**: Tests that verify interactions between components
- **End-to-End Tests**: Tests that verify complete user workflows

This approach ensures a balance between test coverage, execution speed, and maintenance effort.

### Test Coverage Goals

The project has the following code coverage targets:

| Component | Overall Coverage | Critical Path Coverage |
|-----------|------------------|------------------------|
| Backend | 80% | 90% |
| Frontend | 70% | 90% |

Critical paths include:
- Loan application submission and validation
- Underwriting decision process
- Document generation and signing
- Funding disbursement

Coverage is measured using pytest-cov for the backend and Jest's coverage reporter for the frontend.

### Testing Responsibilities

| Role | Responsibilities |
|------|------------------|
| Developers | - Write and maintain unit tests<br>- Create integration tests for their components<br>- Fix issues found in testing<br>- Participate in code reviews |
| QA Engineers | - Design and implement test plans<br>- Create and maintain automated tests<br>- Execute manual test scenarios<br>- Report and track defects |
| DevOps | - Maintain test environments<br>- Configure CI/CD pipelines for testing<br>- Monitor test infrastructure<br>- Support performance testing |
| Security Team | - Conduct security assessments<br>- Review security test results<br>- Validate security controls<br>- Perform penetration testing |
| Product Owners | - Define acceptance criteria<br>- Review and approve test scenarios<br>- Participate in UAT<br>- Sign off on test results |

## Backend Testing

Backend testing focuses on the Python/Django components of the loan management system.

### Unit Testing

Unit tests for the backend are implemented using pytest and pytest-django.

**Test Organization**:
- Tests are located in a `tests` directory within each app
- Test files are named with a `test_` prefix (e.g., `test_models.py`)
- Test functions are named with a `test_` prefix (e.g., `test_calculate_loan_amount`)
- Test classes are named with a `Test` prefix (e.g., `TestLoanCalculator`)

**Example Unit Test**:
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

**Test Categories**:
We use pytest markers to categorize tests:
- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.api`: API tests
- `@pytest.mark.model`: Model tests
- `@pytest.mark.view`: View tests
- `@pytest.mark.serializer`: Serializer tests
- `@pytest.mark.permission`: Permission tests
- `@pytest.mark.service`: Service tests
- `@pytest.mark.security`: Security tests

Run specific test categories with:
```bash
pytest -m unit
pytest -m integration
```

### Model Testing

Model tests verify the behavior of Django models, including:
- Field validation
- Method behavior
- Signal handling
- QuerySet methods

**Example Model Test**:
```python
@pytest.mark.model
class TestApplication:
    def test_application_str_representation(self, application_factory):
        # Arrange
        application = application_factory()
        
        # Act/Assert
        assert str(application) == f"Application {application.id} - {application.borrower.full_name}"
    
    def test_application_status_transitions(self, application_factory):
        # Arrange
        application = application_factory(status='draft')
        
        # Act
        application.submit()
        
        # Assert
        assert application.status == 'submitted'
        assert application.submission_date is not None
```

### API Testing

API tests verify the behavior of REST API endpoints, including:
- Request validation
- Response format and content
- Authentication and authorization
- Error handling

**Example API Test**:
```python
@pytest.mark.api
class TestApplicationAPI:
    def test_list_applications_returns_user_applications_only(self, api_client, user_factory, application_factory):
        # Arrange
        user = user_factory()
        other_user = user_factory()
        user_application = application_factory(borrower=user)
        other_application = application_factory(borrower=other_user)
        api_client.force_authenticate(user=user)
        
        # Act
        response = api_client.get('/api/applications/')
        
        # Assert
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['id'] == str(user_application.id)
    
    def test_create_application_with_valid_data(self, api_client, user_factory, school_factory, program_factory):
        # Arrange
        user = user_factory()
        school = school_factory()
        program = program_factory(school=school)
        api_client.force_authenticate(user=user)
        payload = {
            'school_id': str(school.id),
            'program_id': str(program.id),
            'tuition_amount': '10000.00',
            'deposit_amount': '1000.00',
            'other_funding': '0.00',
            'requested_amount': '9000.00',
            'start_date': '2023-09-01'
        }
        
        # Act
        response = api_client.post('/api/applications/', payload)
        
        # Assert
        assert response.status_code == 201
        assert response.data['borrower']['id'] == str(user.id)
        assert response.data['school']['id'] == str(school.id)
        assert response.data['program']['id'] == str(program.id)
        assert response.data['status'] == 'draft'
```

### Service Testing

Service tests verify the behavior of business logic services, including:
- Complex calculations
- Workflow processing
- External service interactions

**Example Service Test**:
```python
@pytest.mark.service
class TestUnderwritingService:
    def test_evaluate_application_with_good_credit_score(self, application_factory, credit_info_factory):
        # Arrange
        application = application_factory()
        credit_info_factory(application=application, borrower=application.borrower, credit_score=720)
        
        # Act
        result = underwriting_service.evaluate_application(application)
        
        # Assert
        assert result['decision'] == 'approved'
        assert result['approved_amount'] == application.requested_amount
        assert result['interest_rate'] == Decimal('5.25')
    
    def test_evaluate_application_with_poor_credit_score(self, application_factory, credit_info_factory):
        # Arrange
        application = application_factory()
        credit_info_factory(application=application, borrower=application.borrower, credit_score=580)
        
        # Act
        result = underwriting_service.evaluate_application(application)
        
        # Assert
        assert result['decision'] == 'denied'
        assert 'credit_score_below_threshold' in result['reasons']
```

### Mocking Strategy

We use pytest-mock for mocking external dependencies in tests:

**Mocking External Services**:
```python
def test_docusign_integration(mocker):
    # Arrange
    mock_docusign = mocker.patch('apps.documents.docusign.DocuSignClient')
    mock_instance = mock_docusign.return_value
    mock_instance.create_envelope.return_value = {
        'envelope_id': '123-456-789',
        'status': 'sent',
        'recipients': [{'email': 'test@example.com'}]
    }
    
    document = Document.objects.create(file_path='test.pdf')
    
    # Act
    result = docusign_service.send_for_signature(document, ['test@example.com'])
    
    # Assert
    assert result['envelope_id'] == '123-456-789'
    assert result['status'] == 'sent'
    mock_instance.create_envelope.assert_called_once()
```

**Mocking Database Queries**:
```python
def test_get_pending_applications(mocker):
    # Arrange
    mock_queryset = mocker.patch('apps.applications.models.Application.objects')
    mock_queryset.filter.return_value.count.return_value = 5
    
    # Act
    count = application_service.get_pending_applications_count()
    
    # Assert
    assert count == 5
    mock_queryset.filter.assert_called_once_with(status='submitted')
```

### Test Data Management

We use several approaches for managing test data:

**Factories**:
We use FactoryBoy to create test data:
```python
# factories.py
import factory
from factory.django import DjangoModelFactory
from apps.users.models import User
from apps.applications.models import Application

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True

class ApplicationFactory(DjangoModelFactory):
    class Meta:
        model = Application
    
    borrower = factory.SubFactory(UserFactory)
    school = factory.SubFactory('apps.schools.factories.SchoolFactory')
    program = factory.SubFactory('apps.schools.factories.ProgramFactory')
    status = 'draft'
    requested_amount = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
```

**Fixtures**:
We use pytest fixtures for common test data:
```python
# conftest.py
import pytest
from apps.users.factories import UserFactory
from apps.applications.factories import ApplicationFactory

@pytest.fixture
def user():
    return UserFactory()

@pytest.fixture
def application(user):
    return ApplicationFactory(borrower=user)
```

**Database Isolation**:
We use pytest-django's database isolation to ensure tests don't interfere with each other:
```python
@pytest.mark.django_db
def test_create_application(user):
    # This test will run in its own transaction
    application = Application.objects.create(borrower=user, status='draft')
    assert Application.objects.count() == 1
```

### Running Backend Tests

To run backend tests:

```bash
# Navigate to the backend directory
cd src/backend

# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest apps/applications/tests/test_models.py

# Run specific test function
pytest apps/applications/tests/test_models.py::test_application_status_transitions

# Run tests by marker
pytest -m unit
pytest -m "not slow"
```

Test configuration is defined in `pytest.ini`.

## Frontend Testing

Frontend testing focuses on the React/TypeScript components of the loan management system.

### Unit Testing

Unit tests for the frontend are implemented using Jest and React Testing Library.

**Test Organization**:
- Tests are located in a `tests` directory within each component folder
- Test files are named with a `.test.tsx` extension (e.g., `ApplicationForm.test.tsx`)

**Example Unit Test**:
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

**Testing Best Practices**:
- Test behavior, not implementation details
- Use `render`, `screen`, and `fireEvent` from React Testing Library
- Use `userEvent` for more realistic user interactions
- Test accessibility with appropriate queries (`getByRole`)
- Test error states and loading states

### Component Testing

Component tests verify the behavior of React components, including:
- Rendering with different props
- User interactions
- State changes
- Event handling

**Example Component Test**:
```typescript
// ApplicationStatus/tests/ApplicationStatus.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import { ApplicationStatus } from '../ApplicationStatus';
import { Application } from 'types/application.types';

describe('ApplicationStatus', () => {
  const mockApplication: Application = {
    id: 'app-123',
    status: 'approved',
    submissionDate: '2023-05-01T12:00:00Z',
    borrower: {
      id: 'user-123',
      firstName: 'John',
      lastName: 'Doe',
      email: 'john@example.com'
    },
    school: {
      id: 'school-123',
      name: 'Test School'
    },
    program: {
      id: 'program-123',
      name: 'Test Program'
    },
    requestedAmount: 10000,
    approvedAmount: 10000
  };

  it('should display the application status', () => {
    render(<ApplicationStatus application={mockApplication} />);
    
    expect(screen.getByText(/approved/i)).toBeInTheDocument();
    expect(screen.getByText(/test school/i)).toBeInTheDocument();
    expect(screen.getByText(/test program/i)).toBeInTheDocument();
    expect(screen.getByText(/\\$10,000/i)).toBeInTheDocument();
  });

  it('should display the timeline with completed steps', () => {
    render(<ApplicationStatus application={mockApplication} />);
    
    const timelineSteps = screen.getAllByRole('listitem');
    expect(timelineSteps.length).toBeGreaterThan(0);
    
    expect(screen.getByText(/application submitted/i)).toBeInTheDocument();
    expect(screen.getByText(/application approved/i)).toBeInTheDocument();
  });
});
```

### Redux Testing

Redux tests verify the behavior of Redux state management, including:
- Action creators
- Reducers
- Selectors
- Async thunks

**Example Redux Test**:
```typescript
// store/slices/applicationSlice.test.ts
import applicationReducer, {
  setCurrentApplication,
  clearCurrentApplication,
  fetchApplications
} from '../applicationSlice';
import { configureStore } from '@reduxjs/toolkit';
import { applicationApi } from 'api/applications';

// Mock the API
jest.mock('api/applications');

describe('applicationSlice', () => {
  const initialState = {
    applications: [],
    currentApplication: null,
    loading: false,
    error: null
  };

  it('should handle initial state', () => {
    expect(applicationReducer(undefined, { type: 'unknown' })).toEqual(initialState);
  });

  it('should handle setCurrentApplication', () => {
    const mockApplication = { id: 'app-123', status: 'draft' };
    const actual = applicationReducer(
      initialState,
      setCurrentApplication(mockApplication)
    );
    expect(actual.currentApplication).toEqual(mockApplication);
  });

  it('should handle clearCurrentApplication', () => {
    const startState = {
      ...initialState,
      currentApplication: { id: 'app-123', status: 'draft' }
    };
    const actual = applicationReducer(startState, clearCurrentApplication());
    expect(actual.currentApplication).toBeNull();
  });

  it('should handle fetchApplications.pending', () => {
    const actual = applicationReducer(
      initialState,
      { type: fetchApplications.pending.type }
    );
    expect(actual.loading).toBe(true);
    expect(actual.error).toBeNull();
  });

  it('should handle fetchApplications.fulfilled', () => {
    const mockApplications = [{ id: 'app-123', status: 'draft' }];
    const actual = applicationReducer(
      { ...initialState, loading: true },
      { type: fetchApplications.fulfilled.type, payload: mockApplications }
    );
    expect(actual.loading).toBe(false);
    expect(actual.applications).toEqual(mockApplications);
  });

  it('should handle fetchApplications.rejected', () => {
    const errorMessage = 'Failed to fetch';
    const actual = applicationReducer(
      { ...initialState, loading: true },
      { type: fetchApplications.rejected.type, payload: errorMessage }
    );
    expect(actual.loading).toBe(false);
    expect(actual.error).toBe(errorMessage);
  });

  it('should fetch applications successfully', async () => {
    // Arrange
    const mockApplications = [{ id: 'app-123', status: 'draft' }];
    applicationApi.getApplications.mockResolvedValue({
      data: mockApplications
    });

    const store = configureStore({
      reducer: { applications: applicationReducer }
    });

    // Act
    await store.dispatch(fetchApplications());

    // Assert
    const state = store.getState().applications;
    expect(state.applications).toEqual(mockApplications);
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
  });
});
```

### API Integration Testing

API integration tests verify the behavior of API service modules, including:
- Request formatting
- Response handling
- Error handling

**Example API Integration Test**:
```typescript
// api/applications.test.ts
import axios from 'axios';
import { applicationApi } from '../applications';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('applicationApi', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should get applications', async () => {
    // Arrange
    const mockApplications = [{ id: 'app-123', status: 'draft' }];
    mockedAxios.get.mockResolvedValue({ data: mockApplications });

    // Act
    const result = await applicationApi.getApplications();

    // Assert
    expect(result.data).toEqual(mockApplications);
    expect(mockedAxios.get).toHaveBeenCalledWith(expect.stringContaining('/applications'));
  });

  it('should create an application', async () => {
    // Arrange
    const mockApplication = { id: 'app-123', status: 'draft' };
    const formData = {
      schoolId: 'school-1',
      programId: 'program-1',
      tuitionAmount: 10000,
      depositAmount: 1000,
      otherFunding: 0,
      requestedAmount: 9000,
      startDate: '2023-09-01'
    };
    mockedAxios.post.mockResolvedValue({ data: mockApplication });

    // Act
    const result = await applicationApi.createApplication(formData);

    // Assert
    expect(result.data).toEqual(mockApplication);
    expect(mockedAxios.post).toHaveBeenCalledWith(
      expect.stringContaining('/applications'),
      formData
    );
  });

  it('should handle API errors', async () => {
    // Arrange
    const errorMessage = 'Network Error';
    mockedAxios.get.mockRejectedValue(new Error(errorMessage));

    // Act & Assert
    await expect(applicationApi.getApplications()).rejects.toThrow(errorMessage);
  });
});
```

### Mocking Strategy

We use Jest's mocking capabilities for mocking dependencies in frontend tests:

**Mocking Modules**:
```typescript
// Mock entire module
jest.mock('api/applications');

// Mock specific functions
jest.mock('utils/formatting', () => ({
  formatCurrency: jest.fn((value) => `$${value}`),
  formatDate: jest.fn((date) => '01/01/2023')
}));
```

**Mocking Hooks**:
```typescript
// Mock custom hook
jest.mock('hooks/useAuth', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    user: { id: 'user-123', email: 'test@example.com' },
    login: jest.fn(),
    logout: jest.fn()
  })
}));
```

**Mocking Context**:
```typescript
// Provide mock context in tests
const mockAuthContext = {
  isAuthenticated: true,
  user: { id: 'user-123', email: 'test@example.com' },
  login: jest.fn(),
  logout: jest.fn()
};

render(
  <AuthContext.Provider value={mockAuthContext}>
    <ComponentUnderTest />
  </AuthContext.Provider>
);
```

**Mock Service Worker**:
For more complex API mocking, we use Mock Service Worker (MSW):
```typescript
// setupTests.ts
import { setupServer } from 'msw/node';
import { rest } from 'msw';

const server = setupServer(
  rest.get('/api/applications', (req, res, ctx) => {
    return res(ctx.json([{ id: 'app-123', status: 'draft' }]));
  }),
  rest.post('/api/applications', (req, res, ctx) => {
    return res(ctx.status(201), ctx.json({ id: 'app-123', status: 'draft' }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### Running Frontend Tests

To run frontend tests:

```bash
# Navigate to the frontend directory
cd src/web

# Run all tests
yarn test

# Run with coverage
yarn test --coverage

# Run specific test file
yarn test src/components/ApplicationForm/tests/ApplicationForm.test.tsx

# Run tests in watch mode
yarn test --watch
```

Test configuration is defined in `jest.config.ts` and package.json's jest section.

## End-to-End Testing

End-to-end (E2E) tests verify complete user workflows across the entire application.

### Cypress Setup

We use Cypress for end-to-end testing. Cypress tests are located in the `src/web/cypress` directory.

**Directory Structure**:
```
cypress/
├── e2e/
│   ├── login.cy.ts
│   ├── application_submission.cy.ts
│   ├── document_signing.cy.ts
│   └── ...
├── fixtures/
│   ├── users.json
│   ├── schools.json
│   └── ...
├── support/
│   ├── commands.ts
│   └── e2e.ts
└── tsconfig.json
```

**Configuration**:
Cypress is configured in `cypress.config.ts`:
```typescript
import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/e2e.ts',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: true,
  },
});
```

### Test Scenarios

E2E tests cover key user workflows:

**Example E2E Test**:
```typescript
// cypress/e2e/application_submission.cy.ts
describe('Application Submission', () => {
  beforeEach(() => {
    // Login as borrower
    cy.login('borrower@example.com', 'password123');
    
    // Navigate to new application page
    cy.visit('/applications/new');
  });

  it('should allow a borrower to submit a loan application', () => {
    // Step 1: Select school and program
    cy.get('[data-testid=school-select]').click();
    cy.contains('ABC School').click();
    
    cy.get('[data-testid=program-select]').click();
    cy.contains('Web Development').click();
    
    cy.get('[data-testid=next-button]').click();
    
    // Step 2: Enter borrower information
    cy.get('[data-testid=address-line1]').type('123 Main St');
    cy.get('[data-testid=city]').type('Anytown');
    cy.get('[data-testid=state-select]').click();
    cy.contains('California').click();
    cy.get('[data-testid=zip-code]').type('12345');
    
    cy.get('[data-testid=next-button]').click();
    
    // Step 3: Enter employment information
    cy.get('[data-testid=employer-name]').type('Tech Company');
    cy.get('[data-testid=occupation]').type('Software Developer');
    cy.get('[data-testid=annual-income]').type('85000');
    cy.get('[data-testid=years-employed]').type('3');
    
    cy.get('[data-testid=next-button]').click();
    
    // Step 4: Enter loan details
    cy.get('[data-testid=tuition-amount]').should('have.value', '10000');
    cy.get('[data-testid=deposit-amount]').type('1000');
    cy.get('[data-testid=requested-amount]').should('have.value', '9000');
    cy.get('[data-testid=start-date]').type('2023-09-01');
    
    cy.get('[data-testid=next-button]').click();
    
    // Step 5: Review and submit
    cy.get('[data-testid=terms-checkbox]').check();
    cy.get('[data-testid=submit-button]').click();
    
    // Verify success
    cy.contains('Application Submitted Successfully').should('be.visible');
    cy.url().should('include', '/applications/');
  });
});
```

**Custom Commands**:
We extend Cypress with custom commands for common operations:
```typescript
// cypress/support/commands.ts
declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>;
      uploadDocument(filePath: string, fileType: string): Chainable<void>;
    }
  }
}

Cypress.Commands.add('login', (email, password) => {
  cy.visit('/login');
  cy.get('[data-testid=email]').type(email);
  cy.get('[data-testid=password]').type(password);
  cy.get('[data-testid=login-button]').click();
  cy.url().should('include', '/dashboard');
});

Cypress.Commands.add('uploadDocument', (filePath, fileType) => {
  cy.get(`[data-testid=${fileType}-upload]`).attachFile(filePath);
  cy.contains('Upload Successful').should('be.visible');
});
```

### Test Data Management

E2E tests require consistent test data:

**Fixtures**:
We use Cypress fixtures for test data:
```json
// cypress/fixtures/users.json
{
  "borrower": {
    "email": "borrower@example.com",
    "password": "password123",
    "firstName": "John",
    "lastName": "Doe"
  },
  "schoolAdmin": {
    "email": "admin@school.edu",
    "password": "password123",
    "firstName": "Sarah",
    "lastName": "Johnson"
  }
}
```

**Seeding Data**:
We seed the test database before running E2E tests:
```typescript
// cypress/support/e2e.ts
before(() => {
  // Seed the database with test data
  cy.request('POST', '/api/test/seed', {
    seedFile: 'e2e-seed.json'
  });
});

after(() => {
  // Clean up test data
  cy.request('POST', '/api/test/cleanup');
});
```

**Test Environment**:
E2E tests run against a dedicated test environment with:
- Isolated database
- Mocked external services
- Predictable test data

### Running E2E Tests

To run E2E tests:

```bash
# Start the application in test mode
yarn start:test

# In another terminal, run Cypress tests
yarn cypress:run

# Or open Cypress UI
yarn cypress:open

# Run specific test file
yarn cypress:run --spec "cypress/e2e/application_submission.cy.ts"
```

E2E tests are also run in the CI/CD pipeline against the deployed staging environment.

## Specialized Testing

In addition to functional testing, we perform specialized testing to ensure security, accessibility, and compliance.

### Security Testing

Security testing ensures the application is protected against common vulnerabilities.

**Static Application Security Testing (SAST)**:
We use automated tools to scan code for security issues:
- Bandit for Python code
- ESLint security plugins for JavaScript/TypeScript
- Dependency scanning with Safety and npm audit

**Dynamic Application Security Testing (DAST)**:
We perform dynamic security testing against running applications:
- OWASP ZAP for vulnerability scanning
- Penetration testing by security team

**Security Test Cases**:
- Authentication bypass attempts
- Authorization control testing
- Input validation and sanitization
- SQL injection prevention
- Cross-site scripting (XSS) prevention
- Cross-site request forgery (CSRF) protection
- Sensitive data exposure prevention

**Example Security Test**:
```python
@pytest.mark.security
def test_unauthorized_user_cannot_access_applications():
    # Arrange
    client = APIClient()
    user = UserFactory()
    other_user = UserFactory()
    application = ApplicationFactory(borrower=other_user)
    client.force_authenticate(user=user)
    
    # Act
    response = client.get(f'/api/applications/{application.id}/')
    
    # Assert
    assert response.status_code == 403
```

### Accessibility Testing

Accessibility testing ensures the application is usable by people with disabilities.

**Automated Testing**:
We use automated tools to check for accessibility issues:
- axe-core for automated accessibility testing
- ESLint jsx-a11y plugin for catching common issues
- Lighthouse for accessibility audits

**Manual Testing**:
We perform manual accessibility testing:
- Keyboard navigation testing
- Screen reader testing
- Color contrast verification
- Focus management verification

**Example Accessibility Test**: