import { format, parse, isValid, isFuture, isPast, addDays, differenceInDays, parseISO } from 'date-fns'; // date-fns v2.30.0
import { DATE_FORMATS } from '../config/constants';

/**
 * Formats a date object or string into a specified format
 * @param date Date object or string to format
 * @param formatString Format string to use
 * @returns Formatted date string or empty string if date is invalid
 */
export const formatDate = (date: Date | string | null | undefined, formatString: string): string => {
  if (date === null || date === undefined || date === '') {
    return '';
  }

  let dateObj: Date;
  if (typeof date === 'string') {
    // Try to parse ISO format first
    dateObj = parseISO(date);
    
    // If not valid, try to parse with the provided format
    if (!isValid(dateObj)) {
      try {
        dateObj = parse(date, formatString, new Date());
      } catch (e) {
        return '';
      }
    }
  } else {
    dateObj = date;
  }

  if (!isValid(dateObj)) {
    return '';
  }

  try {
    return format(dateObj, formatString);
  } catch (e) {
    return '';
  }
};

/**
 * Formats a date for display in the UI using the standard display format (MM/DD/YYYY)
 * @param date Date to format
 * @returns Date formatted as MM/DD/YYYY or empty string if invalid
 */
export const formatDateForDisplay = (date: Date | string | null | undefined): string => {
  return formatDate(date, DATE_FORMATS.DISPLAY);
};

/**
 * Formats a date and time for display in the UI (MM/DD/YYYY hh:mm A)
 * @param date Date to format
 * @returns Date and time formatted as MM/DD/YYYY hh:mm A or empty string if invalid
 */
export const formatDateTimeForDisplay = (date: Date | string | null | undefined): string => {
  return formatDate(date, DATE_FORMATS.TIMESTAMP);
};

/**
 * Formats a date for API requests using ISO format (YYYY-MM-DD)
 * @param date Date to format
 * @returns Date formatted as YYYY-MM-DD or empty string if invalid
 */
export const formatDateForAPI = (date: Date | string | null | undefined): string => {
  return formatDate(date, DATE_FORMATS.API);
};

/**
 * Formats a date as an ISO 8601 string for API requests
 * @param date Date to format
 * @returns ISO 8601 formatted date string or empty string if invalid
 */
export const formatISODateTime = (date: Date | string | null | undefined): string => {
  const dateObj = getValidDateObject(date);
  if (!dateObj) {
    return '';
  }

  return dateObj.toISOString();
};

/**
 * Parses a date string with the specified format into a Date object
 * @param dateString Date string to parse
 * @param formatString Format string to use for parsing
 * @returns Parsed Date object or null if parsing fails
 */
export const parseDate = (dateString: string | null | undefined, formatString: string): Date | null => {
  if (dateString === null || dateString === undefined || dateString === '') {
    return null;
  }

  try {
    const parsed = parse(dateString, formatString, new Date());
    if (isValid(parsed)) {
      return parsed;
    }
  } catch (e) {
    // Parsing failed
  }

  return null;
};

/**
 * Parses a display-formatted date string (MM/DD/YYYY) into a Date object
 * @param dateString Date string to parse
 * @returns Parsed Date object or null if parsing fails
 */
export const parseDateFromDisplay = (dateString: string | null | undefined): Date | null => {
  return parseDate(dateString, DATE_FORMATS.DISPLAY);
};

/**
 * Parses an API-formatted date string (YYYY-MM-DD) into a Date object
 * @param dateString Date string to parse
 * @returns Parsed Date object or null if parsing fails
 */
export const parseDateFromAPI = (dateString: string | null | undefined): Date | null => {
  return parseDate(dateString, DATE_FORMATS.API);
};

/**
 * Checks if a value is a valid date
 * @param date Value to check
 * @returns True if the date is valid, false otherwise
 */
export const isValidDate = (date: Date | string | null | undefined): boolean => {
  if (date === null || date === undefined || date === '') {
    return false;
  }

  if (typeof date === 'string') {
    // Try to parse as ISO first
    const parsedISO = parseISO(date);
    if (isValid(parsedISO)) {
      return true;
    }
    
    // Try common formats
    try {
      const parsedDisplay = parse(date, DATE_FORMATS.DISPLAY, new Date());
      if (isValid(parsedDisplay)) {
        return true;
      }
      
      const parsedAPI = parse(date, DATE_FORMATS.API, new Date());
      return isValid(parsedAPI);
    } catch (e) {
      return false;
    }
  }

  return isValid(date);
};

/**
 * Helper function to get a valid Date object from various inputs
 * @param date Date input
 * @returns Valid Date object or null
 */
const getValidDateObject = (date: Date | string | null | undefined): Date | null => {
  if (date === null || date === undefined || date === '') {
    return null;
  }

  if (typeof date === 'string') {
    // Try to parse as ISO first
    const parsedISO = parseISO(date);
    if (isValid(parsedISO)) {
      return parsedISO;
    }
    
    // Try common formats
    try {
      const parsedDisplay = parse(date, DATE_FORMATS.DISPLAY, new Date());
      if (isValid(parsedDisplay)) {
        return parsedDisplay;
      }
      
      const parsedAPI = parse(date, DATE_FORMATS.API, new Date());
      if (isValid(parsedAPI)) {
        return parsedAPI;
      }
    } catch (e) {
      return null;
    }
  }

  return isValid(date as Date) ? date as Date : null;
};

/**
 * Checks if a date is in the future
 * @param date Date to check
 * @returns True if the date is in the future, false otherwise
 */
export const isFutureDate = (date: Date | string | null | undefined): boolean => {
  const dateObj = getValidDateObject(date);
  if (!dateObj) {
    return false;
  }
  
  return isFuture(dateObj);
};

/**
 * Checks if a date is in the past
 * @param date Date to check
 * @returns True if the date is in the past, false otherwise
 */
export const isPastDate = (date: Date | string | null | undefined): boolean => {
  const dateObj = getValidDateObject(date);
  if (!dateObj) {
    return false;
  }
  
  return isPast(dateObj);
};

/**
 * Calculates an expiration date based on a start date and number of days
 * @param startDate Starting date
 * @param days Number of days to add
 * @returns Calculated expiration date or null if startDate is invalid
 */
export const calculateExpirationDate = (
  startDate: Date | string | null | undefined,
  days: number
): Date | null => {
  const dateObj = getValidDateObject(startDate);
  if (!dateObj) {
    return null;
  }
  
  return addDays(dateObj, days);
};

/**
 * Checks if a date has expired (is in the past)
 * @param expirationDate Date to check
 * @returns True if the date has expired, false otherwise
 */
export const isExpired = (expirationDate: Date | string | null | undefined): boolean => {
  if (!isValidDate(expirationDate)) {
    return true; // Consider invalid dates as expired
  }

  return isPastDate(expirationDate);
};

/**
 * Calculates the number of days until a date expires
 * @param expirationDate Expiration date
 * @returns Number of days until expiration or null if date is invalid
 */
export const getDaysUntilExpiration = (
  expirationDate: Date | string | null | undefined
): number | null => {
  const dateObj = getValidDateObject(expirationDate);
  if (!dateObj) {
    return null;
  }
  
  const today = new Date();
  return differenceInDays(dateObj, today);
};

/**
 * Formats a date range for display (MM/DD/YYYY - MM/DD/YYYY)
 * @param startDate Start date of the range
 * @param endDate End date of the range
 * @returns Formatted date range or empty string if dates are invalid
 */
export const formatDateRange = (
  startDate: Date | string | null | undefined,
  endDate: Date | string | null | undefined
): string => {
  const formattedStartDate = formatDateForDisplay(startDate);
  const formattedEndDate = formatDateForDisplay(endDate);

  if (formattedStartDate && formattedEndDate) {
    return `${formattedStartDate} - ${formattedEndDate}`;
  } else if (formattedStartDate) {
    return formattedStartDate;
  } else if (formattedEndDate) {
    return formattedEndDate;
  }

  return '';
};

/**
 * Formats a date range for API requests (YYYY-MM-DD to YYYY-MM-DD)
 * @param startDate Start date of the range
 * @param endDate End date of the range
 * @returns Object with formatted start and end dates for API
 */
export const getDateRangeForAPI = (
  startDate: Date | string | null | undefined,
  endDate: Date | string | null | undefined
): { start: string | null; end: string | null } => {
  const formattedStartDate = formatDateForAPI(startDate);
  const formattedEndDate = formatDateForAPI(endDate);

  return {
    start: formattedStartDate || null,
    end: formattedEndDate || null,
  };
};