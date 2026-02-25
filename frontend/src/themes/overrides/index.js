/**
 * MUI Component Overrides
 * Linear.app-inspired dense, compact styling
 * Based on 8px spacing grid with 4px sub-grid for tight areas
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
      defaultProps: {
        disableElevation: true,
      },
      styleOverrides: {
        root: {
          borderRadius: 6,
          fontWeight: 600,
          fontSize: 13,
          textTransform: 'none',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none'
          }
        },
        sizeSmall: {
          padding: '4px 12px',
          fontSize: 12,
        },
        sizeMedium: {
          padding: '6px 16px',
        },
        sizeLarge: {
          padding: '8px 20px',
          fontSize: 14,
        },
        outlined: {
          borderWidth: 1,
          '&:hover': {
            borderWidth: 1
          }
        }
      }
    },

    MuiIconButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
        },
        sizeSmall: {
          padding: 4,
        },
        sizeMedium: {
          padding: 6,
        },
      }
    },

    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: 'none',
          border: `1px solid ${theme.palette.divider}`,
        }
      }
    },

    MuiCardContent: {
      styleOverrides: {
        root: {
          padding: 16,
          '&:last-child': {
            paddingBottom: 16
          }
        }
      }
    },

    MuiTextField: {
      defaultProps: {
        size: 'small',
      },
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 6,
            fontSize: 13,
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: theme.palette.primary.main
            }
          },
          '& .MuiInputLabel-root': {
            fontSize: 13,
          },
          '& .MuiInputBase-input': {
            padding: '8px 12px',
          },
          '& .MuiInputBase-inputMultiline': {
            padding: 0,
          },
        }
      }
    },

    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          fontSize: 13,
        },
        input: {
          padding: '8px 12px',
        },
        notchedOutline: {
          borderWidth: 1,
        },
      }
    },

    MuiInputLabel: {
      styleOverrides: {
        root: {
          fontSize: 13,
        },
        sizeSmall: {
          fontSize: 13,
        },
      }
    },

    MuiSelect: {
      defaultProps: {
        size: 'small',
      },
      styleOverrides: {
        select: {
          fontSize: 13,
          padding: '8px 12px',
        },
      }
    },

    MuiMenuItem: {
      styleOverrides: {
        root: {
          fontSize: 13,
          minHeight: 32,
          padding: '4px 12px',
        },
      }
    },

    MuiFormControl: {
      styleOverrides: {
        root: {
          '& .MuiInputLabel-root': {
            fontSize: 13,
          },
        },
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
          minHeight: 48,
          '@media (min-width: 600px)': {
            minHeight: 48
          }
        }
      }
    },

    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          fontWeight: 500,
          fontSize: 12,
          height: 24,
        },
        sizeSmall: {
          height: 20,
          fontSize: 11,
        },
        label: {
          paddingLeft: 8,
          paddingRight: 8,
        },
        labelSmall: {
          paddingLeft: 6,
          paddingRight: 6,
        },
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
          paddingLeft: 16,
          paddingRight: 16,
          '@media (min-width: 600px)': {
            paddingLeft: 24,
            paddingRight: 24
          }
        }
      }
    },

    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          fontSize: 13,
          padding: '4px 12px',
        },
      }
    },

    MuiTypography: {
      styleOverrides: {
        h5: {
          fontSize: '1.125rem',
          fontWeight: 600,
        },
        h6: {
          fontSize: '0.9375rem',
          fontWeight: 600,
        },
        subtitle1: {
          fontSize: 14,
        },
        subtitle2: {
          fontSize: 13,
        },
        body1: {
          fontSize: 14,
        },
        body2: {
          fontSize: 13,
        },
        caption: {
          fontSize: 12,
        },
      },
    },

    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRadius: 0,
        },
      },
    },

    MuiDivider: {
      styleOverrides: {
        root: {
          borderColor: theme.palette.divider,
        },
      },
    },

    MuiSlider: {
      styleOverrides: {
        root: {
          height: 4,
        },
        thumb: {
          width: 12,
          height: 12,
        },
        markLabel: {
          fontSize: 10,
        },
      },
    },

    MuiDialogTitle: {
      styleOverrides: {
        root: {
          fontSize: 15,
          fontWeight: 600,
          padding: '16px 20px 8px',
        },
      },
    },

    MuiDialogContent: {
      styleOverrides: {
        root: {
          padding: '12px 20px',
        },
      },
    },

    MuiDialogActions: {
      styleOverrides: {
        root: {
          padding: '8px 20px 16px',
        },
      },
    },

    MuiTableCell: {
      styleOverrides: {
        root: {
          fontSize: 13,
          padding: '8px 16px',
        },
        head: {
          fontWeight: 600,
          fontSize: 12,
          textTransform: 'uppercase',
          letterSpacing: 0.5,
          color: theme.palette.text.secondary,
        },
      },
    },

    MuiTableRow: {
      styleOverrides: {
        root: {
          '&:last-child td': {
            borderBottom: 0,
          },
        },
      },
    },

    MuiFormControlLabel: {
      styleOverrides: {
        root: {
          marginLeft: -8,
        },
        label: {
          fontSize: 13,
        },
      },
    },

    MuiSwitch: {
      styleOverrides: {
        root: {
          padding: 6,
        },
      },
    },
  };
}
