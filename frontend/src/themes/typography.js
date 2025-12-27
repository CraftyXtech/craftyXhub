import { ThemeFonts } from '@/config';

/**
 * CraftyXHub Typography
 * - Headings: Plus Jakarta Sans (bold, geometric, modern)
 * - Body: Inter (best readability)
 * - Code: JetBrains Mono (with ligatures)
 */
export default function typography() {
  return {
    fontFamily: ThemeFonts.FONT_BODY, // Default is Inter for body text
    letterSpacing: 0,

    // Display Large - Plus Jakarta Sans
    h1: {
      fontFamily: ThemeFonts.FONT_HEADING,
      fontWeight: 700,
      fontSize: '2.5rem',
      lineHeight: 1.2,
      letterSpacing: '-0.02em'
    },

    // Display Medium - Plus Jakarta Sans
    h2: {
      fontFamily: ThemeFonts.FONT_HEADING,
      fontWeight: 700,
      fontSize: '1.875rem',
      lineHeight: 1.25,
      letterSpacing: '-0.01em'
    },

    // Display Small - Plus Jakarta Sans
    h3: {
      fontFamily: ThemeFonts.FONT_HEADING,
      fontWeight: 600,
      fontSize: '1.5rem',
      lineHeight: 1.3
    },

    // Heading Large - Plus Jakarta Sans
    h4: {
      fontFamily: ThemeFonts.FONT_HEADING,
      fontWeight: 600,
      fontSize: '1.25rem',
      lineHeight: 1.35
    },

    // Heading Medium - Plus Jakarta Sans
    h5: {
      fontFamily: ThemeFonts.FONT_HEADING,
      fontWeight: 600,
      fontSize: '1.25rem',
      lineHeight: 1.4
    },

    // Heading Small - Plus Jakarta Sans
    h6: {
      fontFamily: ThemeFonts.FONT_HEADING,
      fontWeight: 600,
      fontSize: '1rem',
      lineHeight: 1.5
    },

    // Subtitle 1 - Inter
    subtitle1: {
      fontWeight: 500,
      fontSize: '1rem',
      lineHeight: 1.5
    },

    // Subtitle 2 - Inter
    subtitle2: {
      fontWeight: 500,
      fontSize: '0.875rem',
      lineHeight: 1.5
    },

    // Body 1 - Inter
    body1: {
      fontWeight: 400,
      fontSize: '1rem',
      lineHeight: 1.6
    },

    // Body 2 - Inter
    body2: {
      fontWeight: 400,
      fontSize: '0.875rem',
      lineHeight: 1.6
    },

    // Caption - Inter
    caption: {
      fontWeight: 400,
      fontSize: '0.75rem',
      lineHeight: 1.5
    },

    // Overline - Plus Jakarta Sans (for labels)
    overline: {
      fontFamily: ThemeFonts.FONT_HEADING,
      fontWeight: 600,
      fontSize: '0.75rem',
      lineHeight: 1.5,
      letterSpacing: '0.08em',
      textTransform: 'uppercase'
    },

    // Button - Plus Jakarta Sans
    button: {
      fontFamily: ThemeFonts.FONT_HEADING,
      fontWeight: 600,
      textTransform: 'none'
    }
  };
}
