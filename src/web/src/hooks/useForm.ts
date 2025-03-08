import { useState, useEffect, useCallback, useRef } from 'react';
import { ValidationError } from '../types/common.types';
import { validateField, validateForm } from '../utils/validation';

/**
 * Interface defining the form state and handlers returned by useForm
 */
export interface FormState {
  // Form state
  values: Record<string, any>;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
  isValid: boolean;
  
  // Form handlers
  handleChange: (e: React.ChangeEvent<any>) => void;
  handleBlur: (e: React.FocusEvent<any>) => void;
  handleSubmit: (e?: React.FormEvent) => Promise<void>;
  resetForm: () => void;
  setFieldValue: (field: string, value: any) => void;
  setFieldError: (field: string, error: string) => void;
  validateField: (field: string) => boolean;
  validateAllFields: () => boolean;
}

/**
 * Custom hook for form state management and validation
 * 
 * Provides a Formik-like API for managing form state, validation, and submission.
 * Supports field-level validation, form-level validation, error tracking, and 
 * submission handling with comprehensive error management.
 * 
 * @param initialValues - Initial form values
 * @param validationSchema - Schema for form validation with validate functions and error messages
 * @param onSubmit - Function to call on form submission
 * @returns Form state and handlers
 */
const useForm = (
  initialValues: Record<string, any>,
  validationSchema: Record<string, { validate: Function, errorMessage: string }>,
  onSubmit: (values: Record<string, any>) => void | Promise<void>
): FormState => {
  // Initialize form state
  const [values, setValues] = useState<Record<string, any>>(initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [isValid, setIsValid] = useState<boolean>(true);
  
  // Create a ref to store the current validation schema
  const validationSchemaRef = useRef(validationSchema);
  
  // Update the validation schema ref when it changes
  useEffect(() => {
    validationSchemaRef.current = validationSchema;
  }, [validationSchema]);

  /**
   * Sets a value in an object, supporting dot notation for nested properties
   * @param obj - The object to update
   * @param path - The path to the property (e.g., "address.city")
   * @param value - The new value
   * @returns A new object with the updated property
   */
  const setNestedValue = (obj: Record<string, any>, path: string, value: any): Record<string, any> => {
    if (!path.includes('.')) {
      return { ...obj, [path]: value };
    }

    const parts = path.split('.');
    const [first, ...rest] = parts;
    const restPath = rest.join('.');

    return {
      ...obj,
      [first]: setNestedValue(obj[first] || {}, restPath, value)
    };
  };

  /**
   * Gets a value from an object, supporting dot notation for nested properties
   * @param obj - The object to get the value from
   * @param path - The path to the property (e.g., "address.city")
   * @returns The value at the specified path
   */
  const getNestedValue = (obj: Record<string, any>, path: string): any => {
    if (!path.includes('.')) {
      return obj[path];
    }

    const parts = path.split('.');
    const [first, ...rest] = parts;
    const restPath = rest.join('.');

    if (!obj[first]) {
      return undefined;
    }

    return getNestedValue(obj[first], restPath);
  };

  /**
   * Validates a single form field
   * 
   * @param field - The field name to validate
   * @returns True if validation passes, false otherwise
   */
  const validateFieldInternal = useCallback((field: string): boolean => {
    const schema = validationSchemaRef.current[field];
    if (!schema) return true;

    const fieldValue = getNestedValue(values, field);
    
    const validationError = validateField(
      field,
      fieldValue,
      schema.validate,
      schema.errorMessage,
      values
    );

    setErrors(prevErrors => ({
      ...prevErrors,
      [field]: validationError ? validationError.message : ''
    }));

    return !validationError;
  }, [values]);

  /**
   * Validates all fields in the form
   * 
   * @returns True if all validations pass, false otherwise
   */
  const validateAllFields = useCallback((): boolean => {
    const validationErrors = validateForm(values, validationSchemaRef.current);
    
    const errorsMap: Record<string, string> = {};
    validationErrors.forEach(error => {
      errorsMap[error.field] = error.message;
    });
    
    setErrors(errorsMap);
    const isFormValid = validationErrors.length === 0;
    setIsValid(isFormValid);
    
    return isFormValid;
  }, [values]);

  /**
   * Handles input field changes
   * 
   * @param e - The change event
   */
  const handleChange = useCallback((e: React.ChangeEvent<any>): void => {
    const { name, value, type, checked } = e.target;
    
    // Skip if the input doesn't have a name
    if (!name) return;
    
    const fieldValue = type === 'checkbox' ? checked : value;
    
    setValues(prevValues => setNestedValue(prevValues, name, fieldValue));
    
    // Clear error if field was previously invalid
    if (errors[name]) {
      setErrors(prevErrors => ({
        ...prevErrors,
        [name]: ''
      }));
    }
    
    // If field has been touched, validate on change
    if (touched[name]) {
      validateFieldInternal(name);
    }
  }, [errors, touched, validateFieldInternal]);

  /**
   * Handles input field blur events
   * 
   * @param e - The blur event
   */
  const handleBlur = useCallback((e: React.FocusEvent<any>): void => {
    const { name } = e.target;
    
    // Skip if the input doesn't have a name
    if (!name) return;
    
    setTouched(prevTouched => ({
      ...prevTouched,
      [name]: true
    }));
    
    validateFieldInternal(name);
  }, [validateFieldInternal]);

  /**
   * Programmatically sets a field's value
   * 
   * @param field - The field name (supports dot notation for nested fields)
   * @param value - The new value
   */
  const setFieldValue = useCallback((field: string, value: any): void => {
    setValues(prevValues => setNestedValue(prevValues, field, value));
    
    // Clear error if field was previously invalid
    if (errors[field]) {
      setErrors(prevErrors => ({
        ...prevErrors,
        [field]: ''
      }));
    }
    
    // If field has been touched, validate on change
    if (touched[field]) {
      validateFieldInternal(field);
    }
  }, [errors, touched, validateFieldInternal]);

  /**
   * Programmatically sets a field's error
   * 
   * @param field - The field name
   * @param error - The error message
   */
  const setFieldError = useCallback((field: string, error: string): void => {
    setErrors(prevErrors => ({
      ...prevErrors,
      [field]: error
    }));
    
    if (error) {
      setIsValid(false);
    } else {
      // Recalculate isValid by checking if any errors exist
      setErrors(prevErrors => {
        const updatedErrors = { ...prevErrors, [field]: error };
        const hasErrors = Object.values(updatedErrors).some(errMsg => !!errMsg);
        setIsValid(!hasErrors);
        return updatedErrors;
      });
    }
  }, []);

  /**
   * Resets the form to its initial state
   */
  const resetForm = useCallback((): void => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
    setIsValid(true);
  }, [initialValues]);

  /**
   * Handles form submission
   * 
   * @param e - Optional form event
   */
  const handleSubmit = useCallback(async (e?: React.FormEvent): Promise<void> => {
    if (e) {
      e.preventDefault();
    }
    
    setIsSubmitting(true);
    
    // Validate all fields before submission
    const isFormValid = validateAllFields();
    
    // Mark all fields as touched during submission
    const allTouched: Record<string, boolean> = {};
    Object.keys(validationSchemaRef.current).forEach(field => {
      allTouched[field] = true;
    });
    setTouched(prevTouched => ({
      ...prevTouched,
      ...allTouched
    }));
    
    if (isFormValid) {
      try {
        await onSubmit(values);
      } catch (error) {
        console.error('Form submission error:', error);
      }
    }
    
    setIsSubmitting(false);
  }, [values, validateAllFields, onSubmit]);

  // Return form state and handlers
  return {
    // Form state
    values,
    errors,
    touched,
    isSubmitting,
    isValid,
    
    // Form handlers
    handleChange,
    handleBlur,
    handleSubmit,
    resetForm,
    setFieldValue,
    setFieldError,
    validateField: validateFieldInternal,
    validateAllFields
  };
};

export default useForm;