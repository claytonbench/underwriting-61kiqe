/**
 * Utility functions for browser storage operations in the loan management system frontend.
 * Provides a consistent interface for storing and retrieving data from localStorage and sessionStorage,
 * with specific functions for handling authentication tokens, user data, and user preferences.
 */

import { AuthTokens, AuthUser } from '../types/auth.types';

/**
 * Constants for storage keys to ensure consistency
 */
const STORAGE_KEYS = {
  AUTH_TOKENS: 'auth_tokens',
  USER_DATA: 'user_data',
  THEME_PREFERENCE: 'theme_preference',
  LANGUAGE_PREFERENCE: 'language_preference'
};

/**
 * Stores a value in localStorage with the specified key
 * 
 * @param key - Storage key
 * @param value - Value to store (will be JSON stringified)
 */
export function setItem<T>(key: string, value: T): void {
  try {
    const serializedValue = JSON.stringify(value);
    localStorage.setItem(key, serializedValue);
  } catch (error) {
    console.error('Error storing data in localStorage:', error);
  }
}

/**
 * Retrieves a value from localStorage by key
 * 
 * @param key - Storage key
 * @returns The stored value parsed from JSON or null if not found
 */
export function getItem<T>(key: string): T | null {
  try {
    const serializedValue = localStorage.getItem(key);
    if (serializedValue === null) {
      return null;
    }
    return JSON.parse(serializedValue) as T;
  } catch (error) {
    console.error('Error retrieving data from localStorage:', error);
    return null;
  }
}

/**
 * Removes an item from localStorage by key
 * 
 * @param key - Storage key
 */
export function removeItem(key: string): void {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error('Error removing data from localStorage:', error);
  }
}

/**
 * Stores a value in sessionStorage with the specified key
 * 
 * @param key - Storage key
 * @param value - Value to store (will be JSON stringified)
 */
export function setSessionItem<T>(key: string, value: T): void {
  try {
    const serializedValue = JSON.stringify(value);
    sessionStorage.setItem(key, serializedValue);
  } catch (error) {
    console.error('Error storing data in sessionStorage:', error);
  }
}

/**
 * Retrieves a value from sessionStorage by key
 * 
 * @param key - Storage key
 * @returns The stored value parsed from JSON or null if not found
 */
export function getSessionItem<T>(key: string): T | null {
  try {
    const serializedValue = sessionStorage.getItem(key);
    if (serializedValue === null) {
      return null;
    }
    return JSON.parse(serializedValue) as T;
  } catch (error) {
    console.error('Error retrieving data from sessionStorage:', error);
    return null;
  }
}

/**
 * Removes an item from sessionStorage by key
 * 
 * @param key - Storage key
 */
export function removeSessionItem(key: string): void {
  try {
    sessionStorage.removeItem(key);
  } catch (error) {
    console.error('Error removing data from sessionStorage:', error);
  }
}

/**
 * Clears all items from localStorage and sessionStorage
 */
export function clearStorage(): void {
  try {
    localStorage.clear();
    sessionStorage.clear();
  } catch (error) {
    console.error('Error clearing storage:', error);
  }
}

/**
 * Stores authentication tokens in localStorage
 * 
 * @param tokens - Authentication tokens object
 */
export function setAuthTokens(tokens: AuthTokens): void {
  setItem(STORAGE_KEYS.AUTH_TOKENS, tokens);
}

/**
 * Retrieves authentication tokens from localStorage
 * 
 * @returns The stored authentication tokens or null if not found
 */
export function getAuthTokens(): AuthTokens | null {
  return getItem<AuthTokens>(STORAGE_KEYS.AUTH_TOKENS);
}

/**
 * Removes authentication tokens from localStorage
 */
export function removeAuthTokens(): void {
  removeItem(STORAGE_KEYS.AUTH_TOKENS);
}

/**
 * Stores user data in localStorage
 * 
 * @param userData - User data object
 */
export function setUserData(userData: AuthUser): void {
  setItem(STORAGE_KEYS.USER_DATA, userData);
}

/**
 * Retrieves user data from localStorage
 * 
 * @returns The stored user data or null if not found
 */
export function getUserData(): AuthUser | null {
  return getItem<AuthUser>(STORAGE_KEYS.USER_DATA);
}

/**
 * Removes user data from localStorage
 */
export function removeUserData(): void {
  removeItem(STORAGE_KEYS.USER_DATA);
}

/**
 * Stores the user's theme preference in localStorage
 * 
 * @param theme - Theme name
 */
export function setThemePreference(theme: string): void {
  setItem(STORAGE_KEYS.THEME_PREFERENCE, theme);
}

/**
 * Retrieves the user's theme preference from localStorage
 * 
 * @returns The stored theme preference or null if not found
 */
export function getThemePreference(): string | null {
  return getItem<string>(STORAGE_KEYS.THEME_PREFERENCE);
}

/**
 * Stores the user's language preference in localStorage
 * 
 * @param language - Language code
 */
export function setLanguagePreference(language: string): void {
  setItem(STORAGE_KEYS.LANGUAGE_PREFERENCE, language);
}

/**
 * Retrieves the user's language preference from localStorage
 * 
 * @returns The stored language preference or null if not found
 */
export function getLanguagePreference(): string | null {
  return getItem<string>(STORAGE_KEYS.LANGUAGE_PREFERENCE);
}