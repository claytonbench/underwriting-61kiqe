import { createTheme, ThemeOptions, PaletteOptions } from '@mui/material'; // v5.14.0
import { THEME } from '../config/constants';
import { breakpoints } from '../responsive/breakpoints';

/**
 * Base color palette configuration that matches the design system specifications
 */
const palette = {
  primary: {
    main: '#1976D2',
    light: '#42a5f5',
    dark: '#1565c0',
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#388E3C',
    light: '#4caf50',
    dark: '#2e7d32',
    contrastText: '#ffffff',
  },
  error: {
    main: '#D32F2F',
    light: '#ef5350',
    dark: '#c62828',
    contrastText: '#ffffff',
  },
  warning: {
    main: '#FFA000',
    light: '#ffb74d',
    dark: '#f57c00',
    contrastText: '#000000',
  },
  info: {
    main: '#0288D1',
    light: '#03a9f4',
    dark: '#01579b',
    contrastText: '#ffffff',
  },
  success: {
    main: '#388E3C',
    light: '#4caf50',
    dark: '#2e7d32',
    contrastText: '#ffffff',
  },
  background: {
    default: '#F5F5F5',
    paper: '#FFFFFF',
  },
  text: {
    primary: '#212121',
    secondary: '#757575',
  },
};

/**
 * Typography configuration that follows the design system specifications
 */
const typography = {
  fontFamily: 'Roboto, sans-serif',
  h1: {
    fontSize: '2.5rem', // 40px
    fontWeight: 500,
    lineHeight: 1.2,
  },
  h2: {
    fontSize: '2rem', // 32px
    fontWeight: 500,
    lineHeight: 1.2,
  },
  h3: {
    fontSize: '1.75rem', // 28px
    fontWeight: 500,
    lineHeight: 1.2,
  },
  h4: {
    fontSize: '1.5rem', // 24px
    fontWeight: 500,
    lineHeight: 1.2,
  },
  h5: {
    fontSize: '1.25rem', // 20px
    fontWeight: 500,
    lineHeight: 1.2,
  },
  h6: {
    fontSize: '1rem', // 16px
    fontWeight: 500,
    lineHeight: 1.2,
  },
  body1: {
    fontSize: '1rem', // 16px
    lineHeight: 1.5,
  },
  body2: {
    fontSize: '0.875rem', // 14px
    lineHeight: 1.5,
  },
  button: {
    textTransform: 'none',
    fontWeight: 500,
  },
  caption: {
    fontSize: '0.75rem', // 12px
    lineHeight: 1.5,
  },
};

/**
 * Creates and returns a Material-UI theme based on the specified mode (light or dark)
 * 
 * @param mode - The theme mode ('light' or 'dark')
 * @returns A configured Material-UI theme object
 */
export const getTheme = (mode: string) => {
  // Create palette options based on mode
  const paletteOptions: PaletteOptions = {
    ...palette,
    mode: mode === THEME.DARK ? 'dark' : 'light',
  };

  // Modify background and text colors for dark mode
  if (mode === THEME.DARK) {
    paletteOptions.background = {
      default: '#121212',
      paper: '#1e1e1e',
    };
    paletteOptions.text = {
      primary: '#ffffff',
      secondary: '#b0b0b0',
    };
  }

  // Define theme options
  const themeOptions: ThemeOptions = {
    palette: paletteOptions,
    typography,
    breakpoints: {
      values: {
        xs: 0,
        sm: breakpoints.sm,
        md: breakpoints.md,
        lg: breakpoints.lg,
        xl: breakpoints.xl,
      },
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: '4px',
            padding: '8px 16px',
            boxShadow: 'none',
            '&:focus-visible': {
              outline: '2px solid',
              outlineColor: mode === THEME.DARK ? '#ffffff' : palette.primary.main,
              outlineOffset: '2px',
            },
          },
          contained: {
            boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1)',
            '&:hover': {
              boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.1)',
            },
          },
          sizeSmall: {
            padding: '4px 8px',
            fontSize: '0.8125rem',
          },
          sizeLarge: {
            padding: '10px 20px',
            fontSize: '1rem',
          },
        },
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            marginBottom: '16px',
            '& .MuiOutlinedInput-root': {
              '&:hover .MuiOutlinedInput-notchedOutline': {
                borderColor: mode === THEME.DARK ? '#ffffff' : palette.primary.main,
              },
              '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                borderWidth: '2px',
              },
            },
          },
        },
      },
      MuiInputLabel: {
        styleOverrides: {
          root: {
            fontSize: '0.875rem',
            marginBottom: '4px',
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.1)',
            borderRadius: '8px',
            padding: '16px',
            [`@media (max-width: ${breakpoints.sm}px)`]: {
              padding: '12px',
            },
          },
        },
      },
      MuiCardHeader: {
        styleOverrides: {
          root: {
            padding: '16px 16px 8px',
          },
          title: {
            fontSize: '1.25rem',
            fontWeight: 500,
          },
        },
      },
      MuiCardContent: {
        styleOverrides: {
          root: {
            padding: '16px',
            '&:last-child': {
              paddingBottom: '16px',
            },
          },
        },
      },
      MuiTableCell: {
        styleOverrides: {
          head: {
            fontWeight: 600,
            backgroundColor: mode === THEME.DARK ? '#2e2e2e' : '#f5f5f5',
            color: mode === THEME.DARK ? '#ffffff' : '#212121',
          },
          root: {
            padding: '12px 16px',
            [`@media (max-width: ${breakpoints.sm}px)`]: {
              padding: '8px 12px',
            },
          },
        },
      },
      MuiTableRow: {
        styleOverrides: {
          root: {
            '&:nth-of-type(even)': {
              backgroundColor: mode === THEME.DARK ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.02)',
            },
            '&:hover': {
              backgroundColor: mode === THEME.DARK ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.04)',
            },
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: '16px',
            fontWeight: 500,
          },
        },
      },
      MuiDialog: {
        styleOverrides: {
          paper: {
            borderRadius: '8px',
            boxShadow: '0px 4px 20px rgba(0, 0, 0, 0.15)',
          },
        },
      },
      MuiDialogTitle: {
        styleOverrides: {
          root: {
            fontSize: '1.25rem',
            fontWeight: 500,
          },
        },
      },
      MuiTab: {
        styleOverrides: {
          root: {
            fontWeight: 500,
            textTransform: 'none',
            '&.Mui-selected': {
              fontWeight: 600,
            },
            '&:focus-visible': {
              outline: '2px solid',
              outlineColor: mode === THEME.DARK ? '#ffffff' : palette.primary.main,
              outlineOffset: '2px',
            },
          },
        },
      },
      // Ensure proper focus visibility for accessibility
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            // Improve focus visibility for keyboard navigation
            '& :focus-visible': {
              outline: '2px solid',
              outlineColor: mode === THEME.DARK ? '#ffffff' : palette.primary.main,
              outlineOffset: '2px',
            },
            // Ensure consistent line height for readability
            lineHeight: 1.5,
          },
        },
      },
    },
  };

  return createTheme(themeOptions);
};

// Create and export predefined light and dark themes
export const lightTheme = getTheme(THEME.LIGHT);
export const darkTheme = getTheme(THEME.DARK);