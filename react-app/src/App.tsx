import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { motion } from 'framer-motion';

import HomePage from './pages/HomePage';
import SummaryPage from './pages/SummaryPage';
import { AppProvider, useApp } from './context/AppContext';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#4285f4',
      light: '#66a6ff',
      dark: '#005ecb',
    },
    secondary: {
      main: '#34a853',
      light: '#6abf69',
      dark: '#00791b',
    },
    background: {
      default: '#ffffff',
      paper: '#ffffff',
    },
    text: {
      primary: '#202124',
      secondary: '#5f6368',
    },
  },
  typography: {
    fontFamily: '"Google Sans", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.125rem',
      fontWeight: 400,
      color: '#202124',
    },
    h2: {
      fontSize: '1.5rem',
      fontWeight: 400,
      color: '#202124',
    },
    body1: {
      fontSize: '0.875rem',
      color: '#202124',
    },
    body2: {
      fontSize: '0.75rem',
      color: '#5f6368',
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: '24px',
          padding: '8px 24px',
          fontSize: '14px',
          fontWeight: 500,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: '24px',
            backgroundColor: '#f8f9fa',
            border: '1px solid #f8f9fa',
            '&:hover': {
              backgroundColor: '#fff',
              boxShadow: '0 1px 6px rgba(32,33,36,.28)',
            },
            '&.Mui-focused': {
              backgroundColor: '#fff',
              boxShadow: '0 1px 6px rgba(32,33,36,.28)',
            },
            '& fieldset': {
              border: 'none',
            },
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
          borderRadius: '8px',
          border: '1px solid #dadce0',
          '&:hover': {
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
          },
        },
      },
    },
  },
});

function AppContent() {
  const { currentPage } = useApp();

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {currentPage === 'home' && <HomePage />}
      {currentPage === 'summary' && <SummaryPage />}
    </motion.div>
  );
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppProvider>
        <AppContent />
      </AppProvider>
    </ThemeProvider>
  );
}

export default App;
