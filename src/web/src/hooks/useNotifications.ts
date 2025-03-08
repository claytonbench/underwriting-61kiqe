/**
 * Custom React hook that provides access to notification functionality throughout the application.
 * This hook wraps the NotificationContext to provide a convenient way for components to access
 * notification state and methods.
 */

import { useContext } from 'react'; // ^18.2.0
import { NotificationContext } from '../context/NotificationContext';

/**
 * Custom hook that provides access to notification context data and methods
 * 
 * @returns NotificationContextType object containing notification state and methods
 * @throws Error if used outside of NotificationProvider
 */
export const useNotifications = () => {
  const context = useContext(NotificationContext);
  
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  
  return context;
};

export default useNotifications;