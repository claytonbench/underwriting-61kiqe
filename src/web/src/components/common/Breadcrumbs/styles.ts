import { makeStyles } from '@mui/styles'; // v5.14.0
import { Theme } from '@mui/material'; // v5.14.0

/**
 * Custom hook that generates CSS classes for the Breadcrumbs component
 * Provides consistent styling with accessibility and responsiveness in mind
 */
const useStyles = makeStyles((theme: Theme) => ({
  // Container for the breadcrumbs navigation
  root: {
    display: 'flex',
    alignItems: 'center',
    padding: theme.spacing(1, 0),
    margin: theme.spacing(1, 0),
    color: theme.palette.text.primary,
    '& ol': {
      display: 'flex',
      flexWrap: 'wrap',
      alignItems: 'center',
      padding: 0,
      margin: 0,
      listStyle: 'none',
    },
    [theme.breakpoints.down('sm')]: {
      padding: theme.spacing(0.75, 0),
      margin: theme.spacing(0.5, 0),
      fontSize: '0.85rem',
    },
  },
  
  // Styles for clickable breadcrumb links
  link: {
    display: 'inline-flex',
    alignItems: 'center',
    color: theme.palette.primary.main,
    textDecoration: 'none',
    fontWeight: 400,
    transition: 'color 0.2s ease, text-decoration 0.2s ease',
    '&:hover': {
      textDecoration: 'underline',
      color: theme.palette.primary.dark,
    },
    '&:focus': {
      outline: `2px solid ${theme.palette.primary.main}`,
      outlineOffset: '2px',
      borderRadius: '2px',
    },
  },
  
  // Styles for the current/active page breadcrumb (the last item)
  currentPage: {
    display: 'inline-flex',
    alignItems: 'center',
    color: theme.palette.text.primary,
    fontWeight: 500,
    pointerEvents: 'none',
    [theme.breakpoints.down('sm')]: {
      maxWidth: '180px',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap',
    },
  },
  
  // Styles for icons (home and separator)
  icon: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: theme.palette.text.secondary,
    marginRight: theme.spacing(0.5),
    marginLeft: theme.spacing(0.5),
    '& svg': {
      fontSize: '1.25rem',
      [theme.breakpoints.down('sm')]: {
        fontSize: '1rem',
      },
    },
  },
  
  // Styles specifically for the home icon
  homeIcon: {
    marginRight: theme.spacing(0.5),
    color: theme.palette.primary.main,
  },
  
  // Styles for breadcrumb items container
  itemsContainer: {
    display: 'flex',
    alignItems: 'center',
    flexWrap: 'wrap',
  },
  
  // Separator styles
  separator: {
    display: 'flex',
    alignItems: 'center',
    color: theme.palette.text.secondary,
    margin: theme.spacing(0, 0.5),
    userSelect: 'none',
  },
  
  // Screen reader only text (for accessibility)
  srOnly: {
    position: 'absolute',
    width: '1px',
    height: '1px',
    padding: '0',
    margin: '-1px',
    overflow: 'hidden',
    clip: 'rect(0, 0, 0, 0)',
    whiteSpace: 'nowrap',
    borderWidth: '0',
  },
}));

export default useStyles;