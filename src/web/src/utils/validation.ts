import { ValidationError } from '../types/common.types';
import { parsePhoneNumber, parseSSN, parseCurrency } from './formatting';

// Regular expressions for validation
const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
const PHONE_REGEX = /^\(\d{3}\) \d{3}-\d{4}$|\d{10}$/;
const SSN_REGEX = /^\d{3}-\d{2}-\d{4}$|\d{9}$/;
const ZIP_CODE_REGEX = /^\d{5}(-\d{4})?$/;
const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

/**
 * Validates that a value is not empty
 * @param value - The value to check
 * @returns True if value is not empty, false otherwise
 */
export const isRequired = (value: any): boolean => {
  if (value === null || value === undefined) {
    return false;
  }
  
  if (typeof value === 'string') {
    return value.trim() !== '';
  }
  
  if (Array.isArray(value)) {
    return value.length > 0;
  }
  
  if (typeof value === 'object') {
    return Object.keys(value).length > 0;
  }
  
  return true;
};

/**
 * Validates that a value is a valid email address
 * @param value - The email to validate
 * @returns True if value is a valid email address, false otherwise
 */
export const isEmail = (value: string): boolean => {
  if (!value || typeof value !== 'string') {
    return false;
  }
  
  return EMAIL_REGEX.test(value);
};

/**
 * Validates that a value is a valid US phone number
 * @param value - The phone number to validate
 * @returns True if value is a valid phone number, false otherwise
 */
export const isPhoneNumber = (value: string): boolean => {
  if (!value || typeof value !== 'string') {
    return false;
  }
  
  const digits = parsePhoneNumber(value);
  if (!digits) {
    return false;
  }
  
  return digits.length === 10;
};

/**
 * Validates that a value is a valid Social Security Number
 * @param value - The SSN to validate
 * @returns True if value is a valid SSN, false otherwise
 */
export const isSSN = (value: string): boolean => {
  if (!value || typeof value !== 'string') {
    return false;
  }
  
  const digits = parseSSN(value);
  if (!digits) {
    return false;
  }
  
  return digits.length === 9;
};

/**
 * Validates that a value is a valid US ZIP code
 * @param value - The ZIP code to validate
 * @returns True if value is a valid ZIP code, false otherwise
 */
export const isZipCode = (value: string): boolean => {
  if (!value || typeof value !== 'string') {
    return false;
  }
  
  return ZIP_CODE_REGEX.test(value);
};

/**
 * Validates that a value meets password complexity requirements
 * @param value - The password to validate
 * @returns True if value meets password requirements, false otherwise
 */
export const isPassword = (value: string): boolean => {
  if (!value || typeof value !== 'string') {
    return false;
  }
  
  return PASSWORD_REGEX.test(value);
};

/**
 * Validates that a value is a valid number
 * @param value - The value to validate
 * @returns True if value is a valid number, false otherwise
 */
export const isNumber = (value: any): boolean => {
  if (value === null || value === undefined || value === '') {
    return false;
  }
  
  if (typeof value === 'number') {
    return !isNaN(value);
  }
  
  if (typeof value === 'string') {
    const parsed = Number(value);
    return !isNaN(parsed);
  }
  
  return false;
};

/**
 * Validates that a value is a positive number
 * @param value - The value to validate
 * @returns True if value is a positive number, false otherwise
 */
export const isPositiveNumber = (value: any): boolean => {
  if (!isNumber(value)) {
    return false;
  }
  
  const numValue = typeof value === 'string' ? Number(value) : value;
  return numValue > 0;
};

/**
 * Validates that a value is a non-negative number (zero or positive)
 * @param value - The value to validate
 * @returns True if value is a non-negative number, false otherwise
 */
export const isNonNegativeNumber = (value: any): boolean => {
  if (!isNumber(value)) {
    return false;
  }
  
  const numValue = typeof value === 'string' ? Number(value) : value;
  return numValue >= 0;
};

/**
 * Validates that a value is a valid currency amount
 * @param value - The value to validate
 * @returns True if value is a valid currency amount, false otherwise
 */
export const isCurrency = (value: any): boolean => {
  if (value === null || value === undefined || value === '') {
    return false;
  }
  
  if (typeof value === 'number') {
    return !isNaN(value);
  }
  
  if (typeof value === 'string') {
    const parsed = parseCurrency(value);
    return parsed !== null;
  }
  
  return false;
};

/**
 * Validates that a value is a valid date string
 * @param value - The date string to validate
 * @returns True if value is a valid date, false otherwise
 */
export const isDate = (value: string): boolean => {
  if (!value || typeof value !== 'string') {
    return false;
  }
  
  const date = new Date(value);
  return !isNaN(date.getTime());
};

/**
 * Validates that a value is a date in the future
 * @param value - The date string to validate
 * @returns True if value is a future date, false otherwise
 */
export const isFutureDate = (value: string): boolean => {
  if (!isDate(value)) {
    return false;
  }
  
  const inputDate = new Date(value);
  // Strip time for date-only comparison
  inputDate.setHours(0, 0, 0, 0);
  
  const currentDate = new Date();
  currentDate.setHours(0, 0, 0, 0);
  
  return inputDate > currentDate;
};

/**
 * Validates that a date value represents a person of at least the specified age
 * @param value - The date string to validate
 * @param minAge - The minimum age required
 * @returns True if the date represents a person of at least minAge years, false otherwise
 */
export const isMinimumAge = (value: string, minAge: number): boolean => {
  if (!isDate(value)) {
    return false;
  }
  
  const birthDate = new Date(value);
  const today = new Date();
  
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  
  return age >= minAge;
};

/**
 * Validates that a value is a valid US state code
 * @param value - The state code to validate
 * @returns True if value is a valid state code, false otherwise
 */
export const isValidState = (value: string): boolean => {
  if (!value || typeof value !== 'string') {
    return false;
  }
  
  const validStates = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
    'DC', 'AS', 'GU', 'MP', 'PR', 'VI'
  ];
  
  return validStates.includes(value.toUpperCase());
};

/**
 * Validates that a string has at least the specified minimum length
 * @param value - The string to validate
 * @param minLength - The minimum required length
 * @returns True if value has at least minLength characters, false otherwise
 */
export const isMinLength = (value: string, minLength: number): boolean => {
  if (!value || typeof value !== 'string') {
    return false;
  }
  
  return value.length >= minLength;
};

/**
 * Validates that a string does not exceed the specified maximum length
 * @param value - The string to validate
 * @param maxLength - The maximum allowed length
 * @returns True if value has at most maxLength characters, false otherwise
 */
export const isMaxLength = (value: string, maxLength: number): boolean => {
  if (value === null || value === undefined) {
    return true; // Null or undefined is valid (no length to check)
  }
  
  if (typeof value !== 'string') {
    return false;
  }
  
  return value.length <= maxLength;
};

/**
 * Validates that a loan amount is valid based on tuition, deposit, and other funding
 * @param loanAmount - The requested loan amount
 * @param tuitionAmount - The total tuition amount
 * @param depositAmount - The deposit amount
 * @param otherFunding - The amount from other funding sources
 * @returns True if loan amount is valid, false otherwise
 */
export const isValidLoanAmount = (
  loanAmount: number,
  tuitionAmount: number,
  depositAmount: number,
  otherFunding: number
): boolean => {
  if (!isNumber(loanAmount) || !isNumber(tuitionAmount) || 
      !isNumber(depositAmount) || !isNumber(otherFunding)) {
    return false;
  }
  
  const maxAllowedAmount = tuitionAmount - depositAmount - otherFunding;
  
  return loanAmount <= maxAllowedAmount && loanAmount > 0;
};

/**
 * Validates a single form field against a validation rule
 * @param fieldName - The name of the field being validated
 * @param value - The value to validate
 * @param validationFn - The validation function to apply
 * @param errorMessage - The error message to display if validation fails
 * @param allValues - Optional object containing all form values for cross-field validation
 * @returns ValidationError object if validation fails, null if validation passes
 */
export const validateField = (
  fieldName: string,
  value: any,
  validationFn: (value: any, allValues?: Record<string, any>) => boolean,
  errorMessage: string,
  allValues?: Record<string, any>
): ValidationError | null => {
  const isValid = validationFn(value, allValues);
  
  if (isValid) {
    return null;
  }
  
  return {
    field: fieldName,
    message: errorMessage
  };
};

/**
 * Validates an entire form against a validation schema
 * @param values - Object containing all form values
 * @param validationSchema - Object mapping field names to validation rules
 * @returns Array of validation errors, empty if all validations pass
 */
export const validateForm = (
  values: Record<string, any>,
  validationSchema: Record<string, { validate: Function, errorMessage: string }>
): ValidationError[] => {
  const errors: ValidationError[] = [];
  
  for (const fieldName in validationSchema) {
    if (Object.prototype.hasOwnProperty.call(validationSchema, fieldName)) {
      const { validate, errorMessage } = validationSchema[fieldName];
      const value = values[fieldName];
      
      const error = validateField(fieldName, value, validate, errorMessage, values);
      if (error) {
        errors.push(error);
      }
    }
  }
  
  return errors;
};

/**
 * Calculates the strength of a password on a scale of 0-100
 * @param password - The password to evaluate
 * @returns Password strength score (0-100)
 */
export const getPasswordStrength = (password: string): number => {
  if (!password || typeof password !== 'string') {
    return 0;
  }
  
  let score = 0;
  
  // Length contribution (up to 30 points)
  if (password.length >= 12) {
    score += 30;
  } else if (password.length >= 8) {
    score += 20;
  } else if (password.length >= 6) {
    score += 10;
  } else {
    score += 5;
  }
  
  // Character composition (up to 60 points)
  const hasLowercase = /[a-z]/.test(password);
  const hasUppercase = /[A-Z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChars = /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password);
  
  if (hasLowercase) score += 10;
  if (hasUppercase) score += 15;
  if (hasNumbers) score += 15;
  if (hasSpecialChars) score += 20;
  
  // Character variety (up to 20 points)
  const variety = (hasLowercase ? 1 : 0) + 
                 (hasUppercase ? 1 : 0) + 
                 (hasNumbers ? 1 : 0) + 
                 (hasSpecialChars ? 1 : 0);
  
  score += variety * 5;
  
  // Deduct for common patterns or sequences (up to -30 points)
  const sequences = ['123', 'abc', 'qwe', 'asdf'];
  for (const seq of sequences) {
    if (password.toLowerCase().includes(seq)) {
      score -= 10;
    }
  }
  
  const repeats = /(.)\1{2,}/;  // Same character repeated 3+ times
  if (repeats.test(password)) {
    score -= 10;
  }
  
  // Ensure score is between 0 and 100
  return Math.max(0, Math.min(100, score));
};