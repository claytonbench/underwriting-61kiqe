import React from 'react'; // version: ^18.2.0
import { render, screen, fireEvent, waitFor } from '@testing-library/react'; // version: ^14.0.0
import { jest } from '@testing-library/jest-dom'; // version: ^29.5.0
import { Provider } from 'react-redux'; // version: ^8.1.1
import { configureStore } from '@reduxjs/toolkit'; // version: ^1.9.5

import SchoolForm from '../SchoolForm';
import ProgramForm from '../ProgramForm';
import SchoolAdminForm from '../SchoolAdminForm';
import { School, SchoolStatus, Program, ProgramStatus, SchoolContact } from '../../types/school.types';
import { createSchool, updateSchool, createProgram, updateProgram, createSchoolContact, updateSchoolContact } from '../../store/actions/schoolActions';

// Mock Redux actions
jest.mock('../../store/actions/schoolActions', () => ({
  createSchool: jest.fn((schoolData) => (dispatch) => Promise.resolve({ type: 'school/createSchool/fulfilled', payload: { ...schoolData, id: 'new-school-id' } })),
  updateSchool: jest.fn((schoolId, schoolData) => (dispatch) => Promise.resolve({ type: 'school/updateSchool/fulfilled', payload: { id: schoolId, ...schoolData } })),
  createProgram: jest.fn((programData) => (dispatch) => Promise.resolve({ type: 'program/createProgram/fulfilled', payload: { ...programData, id: 'new-program-id' } })),
  updateProgram: jest.fn((programId, programData) => (dispatch) => Promise.resolve({ type: 'program/updateProgram/fulfilled', payload: { id: programId, ...programData } })),
  createSchoolContact: jest.fn((contactData) => (dispatch) => Promise.resolve({ type: 'contact/createSchoolContact/fulfilled', payload: { ...contactData, id: 'new-contact-id' } })),
  updateSchoolContact: jest.fn((contactId, contactData) => (dispatch) => Promise.resolve({ type: 'contact/updateSchoolContact/fulfilled', payload: { id: contactId, ...contactData } })),
}));

// Mock data
const mockSchool: School = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  name: 'Test School',
  legal_name: 'Test School Legal Name',
  tax_id: '12-3456789',
  address_line1: '123 Test Street',
  address_line2: 'Suite 100',
  city: 'Test City',
  state: 'CA',
  zip_code: '12345',
  phone: '(555) 123-4567',
  website: 'https://testschool.edu',
  status: SchoolStatus.ACTIVE,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
};

const mockProgram: Program = {
  id: '223e4567-e89b-12d3-a456-426614174000',
  school_id: '123e4567-e89b-12d3-a456-426614174000',
  name: 'Test Program',
  description: 'A test program description',
  duration_hours: 480,
  duration_weeks: 12,
  status: ProgramStatus.ACTIVE,
  current_tuition: 10000,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
};

const mockContact: SchoolContact = {
  id: '323e4567-e89b-12d3-a456-426614174000',
  school_id: '123e4567-e89b-12d3-a456-426614174000',
  first_name: 'John',
  last_name: 'Doe',
  title: 'School Administrator',
  email: 'john.doe@testschool.edu',
  phone: '(555) 987-6543',
  is_primary: true,
  can_sign_documents: true,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
};

// Helper function to render components with Redux store
const renderWithRedux = (
  ui: React.ReactElement,
  initialState: object = {}
) => {
  const store = configureStore({
    reducer: (state = initialState, action) => state,
    middleware: (getDefaultMiddleware) => getDefaultMiddleware({
      serializableCheck: false,
    }),
  });
  return {
    ...render(<Provider store={store}>{ui}</Provider>),
    store,
  };
};

describe('SchoolForm', () => {
  it('renders correctly with empty form', () => {
    renderWithRedux(<SchoolForm school={null} onSubmitSuccess={() => {}} onCancel={() => {}} />);
    expect(screen.getByLabelText('School Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Legal Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Tax ID')).toBeInTheDocument();
    expect(screen.getByLabelText('Street Address')).toBeInTheDocument();
    expect(screen.getByLabelText('City')).toBeInTheDocument();
    expect(screen.getByLabelText('State')).toBeInTheDocument();
    expect(screen.getByLabelText('ZIP Code')).toBeInTheDocument();
    expect(screen.getByLabelText('Phone Number')).toBeInTheDocument();
    expect(screen.getByLabelText('Website URL')).toBeInTheDocument();
    expect(screen.getByLabelText('School Status')).toBeInTheDocument();
  });

  it('renders correctly with school data for editing', () => {
    renderWithRedux(<SchoolForm school={mockSchool} onSubmitSuccess={() => {}} onCancel={() => {}} />);
    expect(screen.getByLabelText('School Name')).toHaveValue(mockSchool.name);
    expect(screen.getByLabelText('Legal Name')).toHaveValue(mockSchool.legal_name);
    expect(screen.getByLabelText('Tax ID')).toHaveValue(mockSchool.tax_id);
    expect(screen.getByLabelText('Street Address')).toHaveValue(mockSchool.address_line1);
    expect(screen.getByLabelText('City')).toHaveValue(mockSchool.city);
    expect(screen.getByLabelText('State')).toHaveValue(mockSchool.state);
    expect(screen.getByLabelText('ZIP Code')).toHaveValue(mockSchool.zip_code);
    expect(screen.getByLabelText('Phone Number')).toHaveValue(mockSchool.phone);
    expect(screen.getByLabelText('Website URL')).toHaveValue(mockSchool.website);
    expect(screen.getByLabelText('School Status')).toHaveValue(mockSchool.status);
  });

  it('validates required fields', async () => {
    renderWithRedux(<SchoolForm school={null} onSubmitSuccess={() => {}} onCancel={() => {}} />);
    fireEvent.click(screen.getByText('Submit'));
    await waitFor(() => {
      expect(screen.getByText('School name is required')).toBeInTheDocument();
      expect(screen.getByText('Legal name is required')).toBeInTheDocument();
      expect(screen.getByText('Tax ID is required')).toBeInTheDocument();
      expect(screen.getByText('Street address is required')).toBeInTheDocument();
      expect(screen.getByText('City is required')).toBeInTheDocument();
    });
  });

  it('validates email format', async () => {
    renderWithRedux(<SchoolForm school={null} onSubmitSuccess={() => {}} onCancel={() => {}} />);
    fireEvent.change(screen.getByLabelText('Website URL'), { target: { value: 'invalid-email' } });
    fireEvent.blur(screen.getByLabelText('Website URL'));
    fireEvent.click(screen.getByText('Submit'));
    await waitFor(() => {
      expect(screen.getByText('Valid website URL is required')).toBeInTheDocument();
    });
  });

  it('validates phone number format', async () => {
    renderWithRedux(<SchoolForm school={null} onSubmitSuccess={() => {}} onCancel={() => {}} />);
    fireEvent.change(screen.getByLabelText('Phone Number'), { target: { value: '123456789' } });
    fireEvent.blur(screen.getByLabelText('Phone Number'));
    fireEvent.click(screen.getByText('Submit'));
    await waitFor(() => {
      expect(screen.getByText('Valid phone number is required')).toBeInTheDocument();
    });
  });

  it('submits form for new school creation', async () => {
    const onSubmitSuccess = jest.fn();
    renderWithRedux(<SchoolForm school={null} onSubmitSuccess={onSubmitSuccess} onCancel={() => {}} />);
    fireEvent.change(screen.getByLabelText('School Name'), { target: { value: 'New School' } });
    fireEvent.change(screen.getByLabelText('Legal Name'), { target: { value: 'New School Legal' } });
    fireEvent.change(screen.getByLabelText('Tax ID'), { target: { value: '12-1234567' } });
    fireEvent.change(screen.getByLabelText('Street Address'), { target: { value: 'New Address' } });
    fireEvent.change(screen.getByLabelText('City'), { target: { value: 'New City' } });
    fireEvent.change(screen.getByLabelText('State'), { target: { value: 'CA' } });
    fireEvent.change(screen.getByLabelText('ZIP Code'), { target: { value: '90210' } });
    fireEvent.change(screen.getByLabelText('Phone Number'), { target: { value: '(555) 555-5555' } });
    fireEvent.change(screen.getByLabelText('Website URL'), { target: { value: 'http://new.school.com' } });
    fireEvent.click(screen.getByText('Submit'));
    await waitFor(() => {
      expect(createSchool).toHaveBeenCalledWith({
        name: 'New School',
        legal_name: 'New School Legal',
        tax_id: '12-1234567',
        address_line1: 'New Address',
        address_line2: '',
        city: 'New City',
        state: 'CA',
        zip_code: '90210',
        phone: '(555) 555-5555',
        website: 'http://new.school.com',
        status: SchoolStatus.ACTIVE,
      });
      expect(onSubmitSuccess).toHaveBeenCalled();
    });
  });

  it('submits form for school update', async () => {
    const onSubmitSuccess = jest.fn();
    renderWithRedux(<SchoolForm school={mockSchool} onSubmitSuccess={onSubmitSuccess} onCancel={() => {}} />);
    fireEvent.change(screen.getByLabelText('School Name'), { target: { value: 'Updated School' } });
    fireEvent.click(screen.getByText('Submit'));
    await waitFor(() => {
      expect(updateSchool).toHaveBeenCalledWith(mockSchool.id, {
        name: 'Updated School',
        legal_name: mockSchool.legal_name,
        tax_id: mockSchool.tax_id,
        address_line1: mockSchool.address_line1,
        address_line2: mockSchool.address_line2,
        city: mockSchool.city,
        state: mockSchool.state,
        zip_code: mockSchool.zip_code,
        phone: mockSchool.phone,
        website: mockSchool.website,
        status: mockSchool.status,
      });
      expect(onSubmitSuccess).toHaveBeenCalled();
    });
  });

  it('handles cancel button click', () => {
    const onCancel = jest.fn();
    renderWithRedux(<SchoolForm school={mockSchool} onSubmitSuccess={() => {}} onCancel={onCancel} />);
    fireEvent.click(screen.getByText('Cancel'));
    expect(onCancel).toHaveBeenCalled();
  });
});

describe('ProgramForm', () => {
  it('renders correctly with empty form', () => {
    renderWithRedux(<ProgramForm schoolId="123" program={null} onSuccess={() => {}} onCancel={() => {}} />);
    expect(screen.getByLabelText('Program Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Description')).toBeInTheDocument();
    expect(screen.getByLabelText('Duration (hours)')).toBeInTheDocument();
    expect(screen.getByLabelText('Duration (weeks)')).toBeInTheDocument();
    expect(screen.getByLabelText('Tuition Amount')).toBeInTheDocument();
  });

  it('renders correctly with program data for editing', () => {
    renderWithRedux(<ProgramForm schoolId="123" program={mockProgram} onSuccess={() => {}} onCancel={() => {}} />);
    expect(screen.getByLabelText('Program Name')).toHaveValue(mockProgram.name);
    expect(screen.getByLabelText('Description')).toHaveValue(mockProgram.description);
    expect(screen.getByLabelText('Duration (hours)')).toHaveValue(String(mockProgram.duration_hours));
    expect(screen.getByLabelText('Duration (weeks)')).toHaveValue(String(mockProgram.duration_weeks));
    expect(screen.getByLabelText('Tuition Amount')).toHaveValue(String(mockProgram.current_tuition));
  });

  it('validates required fields', async () => {
    renderWithRedux(<ProgramForm schoolId="123" program={null} onSuccess={() => {}} onCancel={() => {}} />);
    fireEvent.click(screen.getByText('Create Program'));
    await waitFor(() => {
      expect(screen.getByText('Program name is required')).toBeInTheDocument();
      expect(screen.getByText('Program description is required')).toBeInTheDocument();
      expect(screen.getByText('Duration hours must be a positive number')).toBeInTheDocument();
      expect(screen.getByText('Duration weeks must be a positive number')).toBeInTheDocument();
      expect(screen.getByText('Valid tuition amount is required')).toBeInTheDocument();
    });
  });

  it('validates numeric fields', async () => {
    renderWithRedux(<ProgramForm schoolId="123" program={null} onSuccess={() => {}} onCancel={() => {}} />);
    fireEvent.change(screen.getByLabelText('Duration (hours)'), { target: { value: 'abc' } });
    fireEvent.change(screen.getByLabelText('Duration (weeks)'), { target: { value: 'def' } });
    fireEvent.change(screen.getByLabelText('Tuition Amount'), { target: { value: 'ghi' } });
    fireEvent.click(screen.getByText('Create Program'));
    await waitFor(() => {
      expect(screen.getByText('Duration hours must be a positive number')).toBeInTheDocument();
      expect(screen.getByText('Duration weeks must be a positive number')).toBeInTheDocument();
      expect(screen.getByText('Valid tuition amount is required')).toBeInTheDocument();
    });
  });

  it('submits form for new program creation', async () => {
    const onSuccess = jest.fn();
    renderWithRedux(<ProgramForm schoolId="123" program={null} onSuccess={onSuccess} onCancel={() => {}} />);
    fireEvent.change(screen.getByLabelText('Program Name'), { target: { value: 'New Program' } });
    fireEvent.change(screen.getByLabelText('Description'), { target: { value: 'New Description' } });
    fireEvent.change(screen.getByLabelText('Duration (hours)'), { target: { value: '100' } });
    fireEvent.change(screen.getByLabelText('Duration (weeks)'), { target: { value: '10' } });
    fireEvent.change(screen.getByLabelText('Tuition Amount'), { target: { value: '1000' } });
    fireEvent.click(screen.getByText('Create Program'));
    await waitFor(() => {
      expect(createProgram).toHaveBeenCalledWith({
        school_id: '123',
        name: 'New Program',
        description: 'New Description',
        duration_hours: 100,
        duration_weeks: 10,
        status: ProgramStatus.ACTIVE,
        tuition_amount: 1000,
        effective_date: expect.any(Date)
      });
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it('submits form for program update', async () => {
    const onSuccess = jest.fn();
    renderWithRedux(<ProgramForm schoolId="123" program={mockProgram} onSuccess={onSuccess} onCancel={() => {}} />);
    fireEvent.change(screen.getByLabelText('Program Name'), { target: { value: 'Updated Program' } });
    fireEvent.click(screen.getByText('Update Program'));
    await waitFor(() => {
      expect(updateProgram).toHaveBeenCalledWith(mockProgram.id, {
        name: 'Updated Program',
        description: mockProgram.description,
        duration_hours: mockProgram.duration_hours,
        duration_weeks: mockProgram.duration_weeks,
        status: mockProgram.status,
      });
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it('handles cancel button click', () => {
    const onCancel = jest.fn();
    renderWithRedux(<ProgramForm schoolId="123" program={mockProgram} onSuccess={() => {}} onCancel={onCancel} />);
    fireEvent.click(screen.getByText('Cancel'));
    expect(onCancel).toHaveBeenCalled();
  });
});

describe('SchoolAdminForm', () => {
  it('renders correctly with empty form', () => {
    renderWithRedux(<SchoolAdminForm schoolId="123" contact={null} onSubmitSuccess={() => {}} onCancel={() => {}} />);
    expect(screen.getByLabelText('First Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Last Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Title')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Phone')).toBeInTheDocument();
  });

  it('renders correctly with contact data for editing', () => {
    renderWithRedux(<SchoolAdminForm schoolId="123" contact={mockContact} onSubmitSuccess={() => {}} onCancel={() => {}} />);
    expect(screen.getByLabelText('First Name')).toHaveValue(mockContact.first_name);
    expect(screen.getByLabelText('Last Name')).toHaveValue(mockContact.last_name);
    expect(screen.getByLabelText('Title')).toHaveValue(mockContact.title);
    expect(screen.getByLabelText('Email')).toHaveValue(mockContact.email);
    expect(screen.getByLabelText('Phone')).toHaveValue(mockContact.phone);
  });

  it('validates required fields', async () => {
    renderWithRedux(<SchoolAdminForm schoolId="123" contact={null} onSubmitSuccess={() => {}} onCancel={() => {}} />);
    fireEvent.click(screen.getByText('Add Administrator'));
    await waitFor(() => {
      expect(screen.getByText('First name is required')).toBeInTheDocument();
      expect(screen.getByText('Last name is required')).toBeInTheDocument();
      expect(screen.getByText('Title is required')).toBeInTheDocument();
      expect(screen.getByText('Valid email address is required')).toBeInTheDocument();
      expect(screen.getByText('Valid phone number is required in format (XXX) XXX-XXXX')).toBeInTheDocument();
    });
  });

  it('validates email format', async () => {
    renderWithRedux(<SchoolAdminForm schoolId="123" contact={null} onSubmitSuccess={() => {}} onCancel={() => {}} />);
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'invalid-email' } });
    fireEvent.blur(screen.getByLabelText('Email'));
    fireEvent.click(screen.getByText('Add Administrator'));
    await waitFor(() => {
      expect(screen.getByText('Valid email address is required')).toBeInTheDocument();
    });
  });

  it('validates phone number format', async () => {
    renderWithRedux(<SchoolAdminForm schoolId="123" contact={null} onSubmitSuccess={() => {}} onCancel={() => {}} />);
    fireEvent.change(screen.getByLabelText('Phone'), { target: { value: '123456789' } });
    fireEvent.blur(screen.getByLabelText('Phone'));
    fireEvent.click(screen.getByText('Add Administrator'));
    await waitFor(() => {
      expect(screen.getByText('Valid phone number is required in format (XXX) XXX-XXXX')).toBeInTheDocument();
    });
  });

  it('submits form for new contact creation', async () => {
    const onSubmitSuccess = jest.fn();
    renderWithRedux(<SchoolAdminForm schoolId="123" contact={null} onSubmitSuccess={onSubmitSuccess} onCancel={() => {}} />);
    fireEvent.change(screen.getByLabelText('First Name'), { target: { value: 'New' } });
    fireEvent.change(screen.getByLabelText('Last Name'), { target: { value: 'Contact' } });
    fireEvent.change(screen.getByLabelText('Title'), { target: { value: 'New Title' } });
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'new@example.com' } });
    fireEvent.change(screen.getByLabelText('Phone'), { target: { value: '(123) 456-7890' } });
    fireEvent.click(screen.getByLabelText('Primary Contact'));
    fireEvent.click(screen.getByLabelText('Can Sign Documents'));
    fireEvent.click(screen.getByText('Add Administrator'));
    await waitFor(() => {
      expect(createSchoolContact).toHaveBeenCalledWith({
        school_id: '123',
        first_name: 'New',
        last_name: 'Contact',
        title: 'New Title',
        email: 'new@example.com',
        phone: '(123) 456-7890',
        is_primary: true,
        can_sign_documents: true,
      });
      expect(onSubmitSuccess).toHaveBeenCalled();
    });
  });

  it('submits form for contact update', async () => {
    const onSubmitSuccess = jest.fn();
    renderWithRedux(<SchoolAdminForm schoolId="123" contact={mockContact} onSubmitSuccess={onSubmitSuccess} onCancel={() => {}} />);
    fireEvent.change(screen.getByLabelText('First Name'), { target: { value: 'Updated' } });
    fireEvent.click(screen.getByText('Save Changes'));
    await waitFor(() => {
      expect(updateSchoolContact).toHaveBeenCalledWith(mockContact.id, {
        first_name: 'Updated',
        last_name: mockContact.last_name,
        title: mockContact.title,
        email: mockContact.email,
        phone: mockContact.phone,
        is_primary: mockContact.is_primary,
        can_sign_documents: mockContact.can_sign_documents,
      });
      expect(onSubmitSuccess).toHaveBeenCalled();
    });
  });

  it('handles cancel button click', () => {
    const onCancel = jest.fn();
    renderWithRedux(<SchoolAdminForm schoolId="123" contact={mockContact} onSubmitSuccess={() => {}} onCancel={onCancel} />);
    fireEvent.click(screen.getByText('Cancel'));
    expect(onCancel).toHaveBeenCalled();
  });
});