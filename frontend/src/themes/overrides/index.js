/**
 * MUI Component Overrides
 * Custom styling for consistent premium look
 */
export default function componentOverrides(theme) {
  return {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollBehavior: 'smooth'
        },
        a: {
          textDecoration: 'none',
          color: 'inherit'
        }
      }
    },

    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '10px 24px',
          fontWeight: 600,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none'
          }
        },
        contained: {
          '&:hover': {
            transform: 'translateY(-1px)',
            transition: 'transform 0.2s ease'
          }
        },
        outlined: {
          borderWidth: 2,
          '&:hover': {
            borderWidth: 2
          }
        }
      }
    },

    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: theme.shadows[2],
          transition: 'box-shadow 0.3s ease, transform 0.3s ease',
          '&:hover': {
            boxShadow: theme.shadows[6]
          }
        }
      }
    },

    MuiCardContent: {
      styleOverrides: {
        root: {
          padding: 24,
          '&:last-child': {
            paddingBottom: 24
          }
        }
      }
    },

    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: theme.palette.primary.main
            }
          }
        }
      }
    },

    MuiLink: {
      styleOverrides: {
        root: {
          textDecoration: 'none',
          color: theme.palette.primary.main,
          transition: 'color 0.2s ease',
          '&:hover': {
            color: theme.palette.primary.dark
          }
        }
      }
    },

    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: 'none',
          borderBottom: `1px solid ${theme.palette.divider}`
        }
      }
    },

    MuiToolbar: {
      styleOverrides: {
        root: {
          minHeight: 72,
          '@media (min-width: 600px)': {
            minHeight: 72
          }
        }
      }
    },

    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          fontWeight: 500
        }
      }
    },

    MuiAvatar: {
      styleOverrides: {
        root: {
          fontWeight: 600
        }
      }
    },

    MuiContainer: {
      styleOverrides: {
        root: {
          paddingLeft: 24,
          paddingRight: 24,
          '@media (min-width: 600px)': {
            paddingLeft: 32,
            paddingRight: 32
          }
        }
      }
    }
  };
}
