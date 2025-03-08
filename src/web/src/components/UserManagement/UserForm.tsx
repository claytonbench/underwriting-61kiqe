import React, { useState, useEffect } from 'react'; // react ^18.2.0
import { useDispatch, useSelector } from 'react-redux'; // react-redux ^8.1.1
import { useForm, Controller } from 'react-hook-form'; // react-hook-form ^7.45.1
import { yupResolver } from '@hookform/resolvers/yup'; // @hookform/resolvers/yup ^3.1.1
import * as yup from 'yup'; // yup ^1.2.0
import {
  TextField,
  Button,
  Grid,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Switch,
  FormControlLabel,
  Divider,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Tabs,
  Tab,
  Alert,
} from '@mui/material'; // @mui/material ^5.14.0
import {
  User,
  UserCreateRequest,
  UserUpdateRequest,
  Role,
  Permission,
  SchoolAdminProfileCreateRequest,
  InternalUserProfileCreateRequest,
  BorrowerProfileCreateRequest,
} from '../../types/user.types';
import { UserType } from '../../types/auth.types';
import {
  selectRoles,
  selectPermissions,
  selectUserLoading,
  selectUserError,
} from '../../store/slices/userSlice';
import {
  createNewUser,
  updateExistingUser,
  fetchRoles,
  fetchPermissions,
} from '../../store/thunks/userThunks';
import { selectSchools } from '../../store/slices/schoolSlice';
import { fetchSchools } from '../../store/thunks/schoolThunks';
import useStyles from './styles';
import PermissionSelection from './PermissionSelection';
import { PhoneField, SSNField, DateField, AddressFields } from '../FormElements';

/**
 * Interface defining the props for the UserForm component.
 */
interface UserFormProps {
  user: User | null;
  onSuccess: () => void;
  onCancel: () => void;
}

/**
 * Interface defining the structure for form data.
 */
interface FormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  password?: string;
  confirmPassword?: string;
  userType: UserType;
  isActive: boolean;
  roleIds: string[];
  selectedPermissions: string[];
  profileData: Record<string, any>;
}

/**
 * Component for creating or editing users with different user types and roles
 */
const UserForm: React.FC<UserFormProps> = ({ user, onSuccess, onCancel }) => {
  const classes = useStyles();
  const dispatch = useDispatch();

  // Local state for managing active tab and selected permissions
  const [activeTab, setActiveTab] = useState(0);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([]);

  // Selectors to get data from Redux store
  const roles = useSelector(selectRoles);
  const permissions = useSelector(selectPermissions);
  const schools = useSelector(selectSchools);
  const isLoading = useSelector(selectUserLoading);
  const error = useSelector(selectUserError);

  // Determine if it's a new user or an existing user
  const isNewUser = !user;

  // Define default values for the form
  const defaultValues: FormData = {
    firstName: user?.firstName || '',
    lastName: user?.lastName || '',
    email: user?.email || '',
    phone: user?.phone || '',
    password: '',
    confirmPassword: '',
    userType: user?.userType || UserType.BORROWER,
    isActive: user?.isActive !== undefined ? user.isActive : true,
    roleIds: user?.roles?.map((role) => role.id) || [],
    selectedPermissions: [],
    profileData: {},
  };

  // Define the validation schema using Yup
  const validationSchema: yup.ObjectSchema<FormData> = yup.object().shape({
    firstName: yup.string().required('First name is required'),
    lastName: yup.string().required('Last name is required'),
    email: yup.string().email('Invalid email address').required('Email is required'),
    phone: yup.string().required('Phone number is required'),
    password: yup.string().when('isNewUser', {
      is: true,
      then: () => yup.string().required('Password is required').min(8, 'Password must be at least 8 characters'),
      otherwise: () => yup.string().notRequired(),
    }),
    confirmPassword: yup.string().when('isNewUser', {
      is: true,
      then: () => yup.string().required('Please confirm password').oneOf([yup.ref('password')], 'Passwords must match'),
      otherwise: ()