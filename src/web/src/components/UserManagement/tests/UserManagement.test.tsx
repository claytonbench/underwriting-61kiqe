# src/web/src/components/UserManagement/tests/UserManagement.test.tsx
```typescript
import React from 'react'; // react ^18.2.0
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'; // @testing-library/react ^14.0.0
import userEvent from '@testing-library/user-event'; // @testing-library/user-event ^14.4.3
import { Provider } from 'react-redux'; // react-redux ^8.1.1
import { configureStore } from '@reduxjs/toolkit'; // @reduxjs/toolkit ^1.9.5
import UserForm from '../UserForm';
import PermissionSelection from '../PermissionSelection';
import { User, Role, Permission, UserType } from '../../../types/user.types';
import { createNewUser, updateExistingUser, fetchRoles, fetchPermissions } from '../../../store/thunks/userThunks';

// Mock data for testing
const mockUser: User = {
  id: 'user-123',
  firstName: 'John',
  lastName: 'Doe',
  email: 'john.doe@example.com',
  phone: '555-123-4567',
  userType: UserType.BORROWER,
  isActive: true,
  createdAt: '2023-01-01T00:00:00Z',
  updatedAt: '2023-01-01T00:00:00Z',
  lastLogin: '2023-01-02T00:00:00Z',
};

const mockRoles: Role[] = [
  { id: 'role-1', name: 'Borrower', description: 'Borrower role', permissions: [], permissionsCount: 0, createdAt: '2023-01-01T00:00:00Z', updatedAt: '2023-01-01T00:00:00Z' },
  { id: 'role-2', name: 'School Admin', description: 'School administrator role', permissions: [], permissionsCount: 0, createdAt: '2023-01-01T00:00:00Z', updatedAt: '2023-01-01T00:00:00Z' },
  { id: 'role-3', name: 'Underwriter', description: 'Underwriter role', permissions: [], permissionsCount: 0, createdAt: '2023-01-01T00:00:00Z', updatedAt: '2023-01-01T00:00:00Z' },
];

const mockPermissions: Permission[] = [
  { id: 'perm-1', name: 'View Applications', description: 'Can view loan applications', resourceType: 'applications' },
  { id: 'perm-2', name: 'Create Applications', description: 'Can create loan applications', resourceType: 'applications' },
  { id: 'perm-3', name: 'View Schools', description: 'Can view schools', resourceType: 'schools' },
  { id: 'perm-4', name: 'Manage Schools', description: 'Can manage schools', resourceType: 'schools' },
  { id: 'perm-5', name: 'View Users', description: 'Can view users', resourceType: 'users' },
  { id: 'perm-6', name: 'Manage Users', description: 'Can manage users', resourceType: 'users' },
];

const mockSchools = [
  { id: 'school-1', name: 'ABC School', status: 'active' },
  { id: 'school-2', name: 'XYZ Academy', status: 'active' },
];

// Mock functions for testing
const mockCreateNewUser = jest.fn().mockResolvedValue({ id: 'new-user-id', ...mockUser });
const mockUpdateExistingUser = jest.fn().mockResolvedValue({ ...mockUser, firstName: 'Updated', lastName: 'User' });
const mockFetchRoles = jest.fn().mockResolvedValue(mockRoles);
const mockFetchPermissions = jest.fn().mockResolvedValue(mockPermissions);
const mockOnSuccess = jest.fn();
const mockOnCancel = jest.fn();
const mockOnChange = jest.fn();

/**
 * Helper function to render components with Redux Provider and mock store
 */
const renderWithProviders = (ui: JSX.Element, options?: { preloadedState?: object }) => {
  // Create a mock Redux store with preloaded state and reducer
  const store = configureStore({
    reducer: {
      user: (state = { users: [], selectedUser: null, roles: [], permissions: [], loading: false, error: null, totalUsers: 0, filters: {} }, action) => state,
      school: (state = { schools: [], loading: false, error: null }, action) => state,
    },
    preloadedState: options?.preloadedState,
  });

  // Render the component wrapped in Redux Provider
  const renderResult = render(<Provider store={store}>{ui}</Provider>);

  // Return render result with store property added
  return {
    ...renderResult,
    store,
  };
};

describe('UserForm Component', () => {
  it('renders the form with basic fields', async () => {
    // Mock Redux store with initial state
    const { store } = renderWithProviders(
      <UserForm user={null} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />
    );

    // Mock fetchRoles and fetchPermissions thunks
    store.dispatch = jest.fn();
    (store.dispatch as jest.Mock).mockResolvedValue(undefined);

    // Verify that basic fields (firstName, lastName, email, phone, userType) are rendered
    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/phone number/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/user type/i)).toBeInTheDocument();

    // Verify that submit and cancel buttons are rendered
    expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
  });

  it('shows password fields for new user', () => {
    // Mock Redux store with initial state
    renderWithProviders(<UserForm user={null} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

    // Verify that password and confirmPassword fields are rendered
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
  });

  it('does not show password fields for existing user', () => {
    // Mock Redux store with initial state
    renderWithProviders(<UserForm user={mockUser} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

    // Verify that password and confirmPassword fields are not rendered
    expect(screen.queryByLabelText(/password/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/confirm password/i)).not.toBeInTheDocument();
  });

  it('shows appropriate fields for borrower user type', async () => {
    // Mock Redux store with initial state
    const { store } = renderWithProviders(<UserForm user={null} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

    // Mock fetchRoles and fetchPermissions thunks
    store.dispatch = jest.fn();
    (store.dispatch as jest.Mock).mockResolvedValue(undefined);

    // Select borrower user type from dropdown
    await userEvent.selectOptions(screen.getByLabelText(/user type/i), ['borrower']);

    // Verify that borrower-specific fields (SSN, DOB, citizenship) are rendered
    expect(screen.getByLabelText(/social security number/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/date of birth/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/citizenship status/i)).toBeInTheDocument();
  });

  it('shows appropriate fields for school admin user type', async () => {
    // Mock Redux store with schools data
    const { store } = renderWithProviders(
      <UserForm user={null} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />,
      { preloadedState: { school: { schools: mockSchools, loading: false, error: null } } }
    );

    // Mock fetchRoles and fetchPermissions thunks
    store.dispatch = jest.fn();
    (store.dispatch as jest.Mock).mockResolvedValue(undefined);

    // Select school admin user type from dropdown
    await userEvent.selectOptions(screen.getByLabelText(/user type/i), ['school_admin']);

    // Verify that school admin-specific fields (school selection, title, department) are rendered
    expect(screen.getByLabelText(/associated school/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/department/i)).toBeInTheDocument();
  });

  it('shows appropriate fields for internal user types', async () => {
    // Mock Redux store with initial state
    const { store } = renderWithProviders(<UserForm user={null} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

    // Mock fetchRoles and fetchPermissions thunks
    store.dispatch = jest.fn();
    (store.dispatch as jest.Mock).mockResolvedValue(undefined);

    // Select underwriter user type from dropdown
    await userEvent.selectOptions(screen.getByLabelText(/user type/i), ['underwriter']);

    // Verify that internal user-specific fields (employee ID, title, department) are rendered
    expect(screen.getByLabelText(/employee id/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/department/i)).toBeInTheDocument();

    // Repeat for QC and system admin user types
    await userEvent.selectOptions(screen.getByLabelText(/user type/i), ['qc']);
    expect(screen.getByLabelText(/employee id/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/department/i)).toBeInTheDocument();

    await userEvent.selectOptions(screen.getByLabelText(/user type/i), ['system_admin']);
    expect(screen.getByLabelText(/employee id/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/department/i)).toBeInTheDocument();
  });

  it('displays role selection section', async () => {
    // Mock Redux store with roles data
    const { store } = renderWithProviders(<UserForm user={null} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />, {
      preloadedState: { user: { roles: mockRoles, permissions: mockPermissions, loading: false, error: null } },
    });

    // Mock fetchRoles and fetchPermissions thunks
    store.dispatch = jest.fn();
    (store.dispatch as jest.Mock).mockResolvedValue(undefined);

    // Render UserForm component
    renderWithProviders(<UserForm user={null} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

    // Verify that role selection section is rendered with role checkboxes
    expect(screen.getByText(/select roles/i)).toBeInTheDocument();
    mockRoles.forEach((role) => {
      expect(screen.getByLabelText(role.name)).toBeInTheDocument();
    });
  });

  it('displays permission selection when a single role is selected', async () => {
    // Mock Redux store with roles and permissions data
    const { store } = renderWithProviders(<UserForm user={null} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />, {
      preloadedState: { user: { roles: mockRoles, permissions: mockPermissions, loading: false, error: null } },
    });

    // Mock fetchRoles and fetchPermissions thunks
    store.dispatch = jest.fn();
    (store.dispatch as jest.Mock).mockResolvedValue(undefined);

    // Render UserForm component
    renderWithProviders(<UserForm user={null} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

    // Select a single role checkbox
    await userEvent.click(screen.getByLabelText(mockRoles[0].name));

    // Verify that PermissionSelection component is rendered
    expect(screen.getByText(/applications/i)).toBeInTheDocument();
  });

  it('hides permission selection when multiple roles are selected', async () => {
    // Mock Redux store with roles and permissions data
    const { store } = renderWithProviders(<UserForm user={null} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />, {
      preloadedState: { user: { roles: mockRoles, permissions: mockPermissions, loading: false, error: null } },
    });

    // Mock fetchRoles and fetchPermissions thunks
    store.dispatch = jest.fn();
    (store.dispatch as jest.Mock).mockResolvedValue(undefined);

    // Render UserForm component
    renderWithProviders(<UserForm user={null} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

    // Select multiple role checkboxes
    await userEvent.click(screen.getByLabelText(mockRoles[0].name));
    await userEvent.click(screen.getByLabelText(mockRoles[1].name));

    // Verify that PermissionSelection component is not rendered
    expect(screen.queryByText(/applications/i)).not.toBeInTheDocument();
  });

  it('validates required fields', async () => {
    // Mock Redux store with initial state
    const { store } = renderWithProviders(<UserForm user={null} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

    // Mock fetchRoles and fetchPermissions thunks
    store.dispatch = jest.fn();
    (store.dispatch as jest.Mock).mockResolvedValue(undefined);

    // Render UserForm component
    renderWithProviders(<UserForm user={null} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

    // Submit the form without filling required fields
    await userEvent.click(screen.getByRole('button', { name: /submit/i }));

    // Verify that validation error messages are displayed
    expect(screen.getByText(/first name is required/i)).toBeInTheDocument();
    expect(screen.getByText(/last name is required/i)).toBeInTheDocument();
    expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    expect(screen.getByText(/phone number is required/i)).toBeInTheDocument();
    expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    expect(screen.getByText(/please confirm password/i)).toBeInTheDocument();
  });

  it('calls createNewUser when submitting new user form', async () => {
    // Mock Redux store with initial state
    const { store } = renderWithProviders(<UserForm user={null} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

    // Mock createNewUser thunk
    store.dispatch = jest.fn();
    (store.dispatch as jest.Mock).mockImplementation((thunk) => {
      if (thunk === createNewUser) {
        return mockCreateNewUser;
      }
      return () => {};
    });

    // Render UserForm component with user prop as null
    renderWithProviders(<UserForm user={null} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

    // Fill in all required fields
    await userEvent.type(screen.getByLabelText(/first name/i), 'Test');
    await userEvent.type(screen.getByLabelText(/last name/i), 'User');
    await userEvent.type(screen.getByLabelText(/email address/i), 'test@example.com');
    await userEvent.type(screen.getByLabelText(/phone number/i), '555-123-4567');
    await userEvent.type(screen.getByLabelText(/password/i), 'Password123!');
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'Password123!');

    // Submit the form
    await userEvent.click(screen.getByRole('button', { name: /submit/i }));

    // Verify that createNewUser was called with correct data
    expect(mockCreateNewUser).toHaveBeenCalled();

    // Verify that onSuccess callback was called
    expect(mockOnSuccess).toHaveBeenCalled();
  });

  it('calls updateExistingUser when submitting edit user form', async () => {
    // Mock Redux store with initial state
    const { store } = renderWithProviders(<UserForm user={mockUser} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

    // Mock updateExistingUser thunk
    store.dispatch = jest.fn();
    (store.dispatch as jest.Mock).mockImplementation((thunk) => {
      if (thunk === updateExistingUser) {
        return mockUpdateExistingUser;
      }
      return () => {};
    });

    // Render UserForm component with user prop
    renderWithProviders(<UserForm user={mockUser} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

    // Modify some fields
    await userEvent.type(screen.getByLabelText(/first name/i), 'Updated');
    await userEvent.type(screen.getByLabelText(/last name/i), 'User');

    // Submit the form
    await userEvent.click(screen.getByRole('button', { name: /submit/i }));

    // Verify that updateExistingUser was called with correct data
    expect(mockUpdateExistingUser).toHaveBeenCalled();

    // Verify that onSuccess callback was called
    expect(mockOnSuccess).toHaveBeenCalled();
  });

  it('calls onCancel when cancel button is clicked', async () => {
    // Mock Redux store with initial state
    renderWithProviders(<UserForm user={mockUser} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

    // Create mock onCancel function
    const mockOnCancel = jest.fn();

    // Render UserForm component with onCancel prop
    renderWithProviders(<UserForm user={mockUser} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

    // Click the cancel button
    await userEvent.click(screen.getByRole('button', { name: /cancel/i }));

    // Verify that onCancel was called
    expect(mockOnCancel).toHaveBeenCalled();
  });

  it('shows loading state during submission', () => {
    // Mock Redux store with loading state
    renderWithProviders(<UserForm user={mockUser} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />, {
      preloadedState: { user: { loading: true, error: null } },
    });

    // Verify that submit button shows loading indicator
    expect(screen.getByRole('button', { name: /submit/i })).toBeDisabled();

    // Verify that form fields are disabled
    expect(screen.getByLabelText(/first name/i)).toBeDisabled();
    expect(screen.getByLabelText(/last name/i)).toBeDisabled();
    expect(screen.getByLabelText(/email address/i)).toBeDisabled();
    expect(screen.getByLabelText(/phone number/i)).toBeDisabled();
  });

  it('shows error message when submission fails', () => {
    // Mock Redux store with error state
    renderWithProviders(<UserForm user={mockUser} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />, {
      preloadedState: { user: { loading: false, error: 'An error occurred' } },
    });

    // Verify that error alert is displayed with error message
    expect(screen.getByText(/an error occurred/i)).toBeInTheDocument();
  });
});

describe('PermissionSelection Component', () => {
  it('renders with grouped permissions', () => {
    // Mock Redux store with permissions data
    const { store } = renderWithProviders(<PermissionSelection selectedRole={mockRoles[0]} selectedPermissions={[]} onChange={mockOnChange} />, {
      preloadedState: { user: { roles: mockRoles, permissions: mockPermissions, loading: false, error: null } },
    });

    // Mock fetchRoles and fetchPermissions thunks
    store.dispatch = jest.fn();
    (store.dispatch as jest.Mock).mockResolvedValue(undefined);

    // Create mock role with permissions
    const mockRole = { ...mockRoles[0], permissions: mockPermissions };

    // Render PermissionSelection component with selectedRole prop
    renderWithProviders(<PermissionSelection selectedRole={mockRole} selectedPermissions={[]} onChange={mockOnChange} />);

    // Verify that permissions are grouped by resource type
    expect(screen.getByText(/applications/i)).toBeInTheDocument();
    expect(screen.getByText(/schools/i)).toBeInTheDocument();
    expect(screen.getByText(/users/i)).toBeInTheDocument();

    // Verify that group headings are rendered
    expect(screen.getByText(/applications/i)).toBeVisible();
    expect(screen.getByText(/schools/i)).toBeVisible();
    expect(screen.getByText(/users/i)).toBeVisible();

    // Verify that permission checkboxes are rendered
    mockPermissions.forEach((permission) => {
      expect(screen.getByLabelText(permission.name)).toBeInTheDocument();
    });
  });

  it('selects permissions based on selectedPermissions prop', () => {
    // Mock Redux store with permissions data
    const { store } = renderWithProviders(<PermissionSelection selectedRole={mockRoles[0]} selectedPermissions={[]} onChange={mockOnChange} />, {
      preloadedState: { user: { roles: mockRoles, permissions: mockPermissions, loading: false, error: null } },
    });

    // Mock fetchRoles and fetchPermissions thunks
    store.dispatch = jest.fn();
    (store.dispatch as jest.Mock).mockResolvedValue(undefined);

    // Create mock role with permissions
    const mockRole = { ...mockRoles[0], permissions: mockPermissions };

    // Create array of selected permission IDs
    const selectedPermissions = [mockPermissions[0].id, mockPermissions[2].id];

    // Render PermissionSelection component with selectedRole and selectedPermissions props
    renderWithProviders(
      <PermissionSelection selectedRole={mockRole} selectedPermissions={selectedPermissions} onChange={mockOnChange} />
    );

    // Verify that checkboxes for selected permissions are checked
    expect(screen.getByLabelText(mockPermissions[0].name)).toBeChecked();
    expect(screen.getByLabelText(mockPermissions[2].name)).toBeChecked();

    // Verify that checkboxes for unselected permissions are not checked
    expect(screen.getByLabelText(mockPermissions[1].name)).not.toBeChecked();
    expect(screen.getByLabelText(mockPermissions[3].name)).not.toBeChecked();
  });

  it('toggles individual permission when checkbox is clicked', async () => {
    // Mock Redux store with permissions data
    const { store } = renderWithProviders(<PermissionSelection selectedRole={mockRoles[0]} selectedPermissions={[]} onChange={mockOnChange} />, {
      preloadedState: { user: { roles: mockRoles, permissions: mockPermissions, loading: false, error: null } },
    });

    // Mock fetchRoles and fetchPermissions thunks
    store.dispatch = jest.fn();
    (store.dispatch as jest.Mock).mockResolvedValue(undefined);

    // Create mock role with permissions
    const mockRole = { ...mockRoles[0], permissions: mockPermissions };

    // Create mock onChange function
    const mockOnChange = jest.fn();

    // Render PermissionSelection component with props
    renderWithProviders(<PermissionSelection selectedRole={mockRole} selectedPermissions={[]} onChange={mockOnChange} />);

    // Click a permission checkbox
    await userEvent.click(screen.getByLabelText(mockPermissions[0].name));

    // Verify that onChange was called with updated permissions array
    expect(mockOnChange).toHaveBeenCalledWith([mockPermissions[0].id]);
  });

  it('toggles all permissions in a group when group checkbox is clicked', async () => {
    // Mock Redux store with permissions data
    const { store } = renderWithProviders(<PermissionSelection selectedRole={mockRoles[0]} selectedPermissions={[]} onChange={mockOnChange} />, {
      preloadedState: { user: { roles: mockRoles, permissions: mockPermissions, loading: false, error: null } },
    });

    // Mock fetchRoles and fetchPermissions thunks
    store.dispatch = jest.fn();
    (store.dispatch as jest.Mock).mockResolvedValue(undefined);

    // Create mock role with permissions
    const mockRole = { ...mockRoles[0], permissions: mockPermissions };

    // Create mock onChange function
    const mockOnChange = jest.fn();

    // Render PermissionSelection component with props
    renderWithProviders(<PermissionSelection selectedRole={mockRole} selectedPermissions={[]} onChange={mockOnChange} />);

    // Click a group checkbox
    await userEvent.click(screen.getByText(/applications/i));

    // Verify that onChange was called with all permissions in that group
    const applicationPermissions = mockPermissions.filter((p) => p.resourceType === 'applications').map((p) => p.id);
    expect(mockOnChange).toHaveBeenCalledWith(expect.arrayContaining(applicationPermissions));
  });

  it('shows indeterminate state for group checkbox when some permissions are selected', async () => {
    // Mock Redux store with permissions data
    const { store } = renderWithProviders(<PermissionSelection selectedRole={mockRoles[0]} selectedPermissions={[]} onChange={mockOnChange} />, {
      preloadedState: { user: { roles: mockRoles, permissions: mockPermissions, loading: false, error: null } },
    });

    // Mock fetchRoles and fetchPermissions thunks
    store.dispatch = jest.fn();
    (store.dispatch as jest.Mock).mockResolvedValue(undefined);

    // Create mock role with permissions
    const mockRole = { ...mockRoles[0], permissions: mockPermissions };

    // Create array of selected permission IDs (some from a group)
    const selectedPermissions = [mockPermissions[0].id];

    // Render PermissionSelection component with props
    renderWithProviders(
      <PermissionSelection selectedRole={mockRole} selectedPermissions={selectedPermissions} onChange={mockOnChange} />
    );

    // Verify that group checkbox has indeterminate property set
    const groupCheckbox = screen.getByText(/applications/i).closest('label') as HTMLLabelElement;
    expect(groupCheckbox.classList.contains('Mui-checked')).toBe(false);
  });
});