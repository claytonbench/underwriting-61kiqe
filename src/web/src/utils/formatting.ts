import { CURRENCY_FORMAT } from '../config/constants';

/**
 * Formats a number as currency with dollar sign and decimal places
 * @param value - The value to format
 * @returns Formatted currency string or empty string if value is invalid
 */
export const formatCurrency = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined || value === '') {
    return '';
  }

  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  
  if (isNaN(numValue)) {
    return '';
  }

  return new Intl.NumberFormat(CURRENCY_FORMAT.LOCALE, CURRENCY_FORMAT.OPTIONS).format(numValue);
};

/**
 * Formats a number as currency without the dollar sign
 * @param value - The value to format
 * @returns Formatted currency string without currency symbol or empty string if value is invalid
 */
export const formatCurrencyWithoutSymbol = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined || value === '') {
    return '';
  }

  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  
  if (isNaN(numValue)) {
    return '';
  }

  const options = {
    ...CURRENCY_FORMAT.OPTIONS,
    currency: 'USD',
    currencyDisplay: 'code',
  };
  
  return new Intl.NumberFormat(CURRENCY_FORMAT.LOCALE, options)
    .format(numValue)
    .replace('USD', '')
    .trim();
};

/**
 * Parses a currency string into a number
 * @param value - The currency string to parse
 * @returns Parsed number or null if parsing fails
 */
export const parseCurrency = (value: string | null | undefined): number | null => {
  if (value === null || value === undefined || value === '') {
    return null;
  }

  // Remove currency symbol, commas, and other non-numeric characters except decimal point
  const cleanedValue = value.replace(/[^0-9.-]/g, '');
  const numValue = parseFloat(cleanedValue);
  
  if (isNaN(numValue)) {
    return null;
  }

  return numValue;
};

/**
 * Formats a number as a percentage with specified decimal places
 * @param value - The value to format
 * @param decimalPlaces - Number of decimal places to include
 * @returns Formatted percentage string or empty string if value is invalid
 */
export const formatPercentage = (
  value: number | string | null | undefined, 
  decimalPlaces: number = 2
): string => {
  if (value === null || value === undefined || value === '') {
    return '';
  }

  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  
  if (isNaN(numValue)) {
    return '';
  }

  return new Intl.NumberFormat(CURRENCY_FORMAT.LOCALE, {
    style: 'percent',
    minimumFractionDigits: decimalPlaces,
    maximumFractionDigits: decimalPlaces,
  }).format(numValue);
};

/**
 * Parses a percentage string into a decimal number
 * @param value - The percentage string to parse
 * @returns Parsed decimal number or null if parsing fails
 */
export const parsePercentage = (value: string | null | undefined): number | null => {
  if (value === null || value === undefined || value === '') {
    return null;
  }

  // Remove percentage symbol, commas, and other non-numeric characters except decimal point
  const cleanedValue = value.replace(/[^0-9.-]/g, '');
  const numValue = parseFloat(cleanedValue);
  
  if (isNaN(numValue)) {
    return null;
  }

  // Convert to decimal by dividing by 100 if the string contained a % symbol
  return value.includes('%') ? numValue / 100 : numValue;
};

/**
 * Formats a string as a US phone number (XXX) XXX-XXXX
 * @param phone - The phone number string to format
 * @returns Formatted phone number string or empty string if value is invalid
 */
export const formatPhoneNumber = (phone: string | null | undefined): string => {
  if (phone === null || phone === undefined || phone === '') {
    return '';
  }

  // Remove all non-digit characters
  const digitsOnly = phone.replace(/\D/g, '');
  
  // Check if we have at least 10 digits
  if (digitsOnly.length < 10) {
    return '';
  }

  // Format as (XXX) XXX-XXXX
  return `(${digitsOnly.slice(0, 3)}) ${digitsOnly.slice(3, 6)}-${digitsOnly.slice(6, 10)}`;
};

/**
 * Parses a formatted phone number string into digits only
 * @param phone - The phone number string to parse
 * @returns Digits-only phone number or null if parsing fails
 */
export const parsePhoneNumber = (phone: string | null | undefined): string | null => {
  if (phone === null || phone === undefined || phone === '') {
    return null;
  }

  // Remove all non-digit characters
  const digitsOnly = phone.replace(/\D/g, '');
  
  // Check if we have at least 10 digits
  if (digitsOnly.length < 10) {
    return null;
  }

  return digitsOnly;
};

/**
 * Formats a string as a Social Security Number XXX-XX-XXXX
 * @param ssn - The SSN string to format
 * @returns Formatted SSN string or empty string if value is invalid
 */
export const formatSSN = (ssn: string | null | undefined): string => {
  if (ssn === null || ssn === undefined || ssn === '') {
    return '';
  }

  // Remove all non-digit characters
  const digitsOnly = ssn.replace(/\D/g, '');
  
  // Check if we have 9 digits for SSN
  if (digitsOnly.length !== 9) {
    return '';
  }

  // Format as XXX-XX-XXXX
  return `${digitsOnly.slice(0, 3)}-${digitsOnly.slice(3, 5)}-${digitsOnly.slice(5, 9)}`;
};

/**
 * Parses a formatted SSN string into digits only
 * @param ssn - The SSN string to parse
 * @returns Digits-only SSN or null if parsing fails
 */
export const parseSSN = (ssn: string | null | undefined): string | null => {
  if (ssn === null || ssn === undefined || ssn === '') {
    return null;
  }

  // Remove all non-digit characters
  const digitsOnly = ssn.replace(/\D/g, '');
  
  // Check if we have 9 digits for SSN
  if (digitsOnly.length !== 9) {
    return null;
  }

  return digitsOnly;
};

/**
 * Formats a string as a ZIP code (5 digits or ZIP+4)
 * @param zipCode - The ZIP code string to format
 * @returns Formatted ZIP code string or empty string if value is invalid
 */
export const formatZipCode = (zipCode: string | null | undefined): string => {
  if (zipCode === null || zipCode === undefined || zipCode === '') {
    return '';
  }

  // Remove all non-digit characters
  const digitsOnly = zipCode.replace(/\D/g, '');
  
  // Check if we have at least 5 digits
  if (digitsOnly.length < 5) {
    return '';
  }

  // Format as XXXXX or XXXXX-XXXX (ZIP+4)
  if (digitsOnly.length === 5) {
    return digitsOnly;
  } else if (digitsOnly.length >= 9) {
    return `${digitsOnly.slice(0, 5)}-${digitsOnly.slice(5, 9)}`;
  } else {
    return digitsOnly.slice(0, 5);
  }
};

/**
 * Truncates text to a specified length and adds ellipsis if needed
 * @param text - The text to truncate
 * @param maxLength - Maximum length before truncation
 * @returns Truncated text with ellipsis or original text if shorter than maxLength
 */
export const truncateText = (text: string | null | undefined, maxLength: number): string => {
  if (text === null || text === undefined || text === '') {
    return '';
  }

  if (text.length <= maxLength) {
    return text;
  }

  return `${text.slice(0, maxLength - 3)}...`;
};

/**
 * Capitalizes the first letter of a string
 * @param text - The text to capitalize
 * @returns String with first letter capitalized or empty string if value is invalid
 */
export const capitalizeFirstLetter = (text: string | null | undefined): string => {
  if (text === null || text === undefined || text === '') {
    return '';
  }

  return text.charAt(0).toUpperCase() + text.slice(1);
};

/**
 * Formats first, middle, and last name into a full name
 * @param firstName - First name
 * @param lastName - Last name
 * @param middleName - Optional middle name
 * @returns Formatted full name or empty string if both first and last names are invalid
 */
export const formatFullName = (
  firstName: string | null | undefined,
  lastName: string | null | undefined,
  middleName?: string | null | undefined
): string => {
  if (
    (firstName === null || firstName === undefined || firstName === '') &&
    (lastName === null || lastName === undefined || lastName === '')
  ) {
    return '';
  }

  const first = firstName || '';
  const middle = middleName ? ` ${middleName}` : '';
  const last = lastName ? ` ${lastName}` : '';

  return `${first}${middle}${last}`;
};

/**
 * Formats address components into a single address string
 * @param address - Object containing address components
 * @returns Formatted address string or empty string if address is invalid
 */
export const formatAddress = (address: {
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  zip_code?: string;
} | null | undefined): string => {
  if (address === null || address === undefined) {
    return '';
  }

  const { address_line1, address_line2, city, state, zip_code } = address;
  
  let formattedAddress = '';
  
  if (address_line1) {
    formattedAddress += address_line1;
  }
  
  if (address_line2) {
    formattedAddress += formattedAddress ? `\n${address_line2}` : address_line2;
  }
  
  const cityStateZip = [
    city,
    state,
    zip_code
  ].filter(Boolean).join(', ');
  
  if (cityStateZip) {
    formattedAddress += formattedAddress ? `\n${cityStateZip}` : cityStateZip;
  }
  
  return formattedAddress;
};

/**
 * Formats a file size in bytes to a human-readable format
 * @param bytes - The file size in bytes
 * @returns Human-readable file size (e.g., '2.5 MB')
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0 || isNaN(bytes)) return '0 Bytes';
  
  const units = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  
  // For bytes, don't show decimal places
  if (i === 0) {
    return `${bytes} ${units[i]}`;
  }
  
  // For KB, show 0 decimal places
  if (i === 1) {
    return `${(bytes / Math.pow(1024, i)).toFixed(0)} ${units[i]}`;
  }
  
  // For larger units, show 1 decimal place
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
};

/**
 * Formats a number with thousand separators
 * @param value - The value to format
 * @returns Number formatted with commas or empty string if value is invalid
 */
export const formatNumberWithCommas = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined || value === '') {
    return '';
  }

  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  
  if (isNaN(numValue)) {
    return '';
  }

  return new Intl.NumberFormat(CURRENCY_FORMAT.LOCALE).format(numValue);
};