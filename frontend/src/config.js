// App configuration
export const APP_CONFIG = {
  name: 'CraftyXHub',
  version: '1.0.0'
};

// API configuration
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Theme fonts
// - Plus Jakarta Sans: geometric, modern headings
// - Inter: best readability for body text
// - JetBrains Mono: ligatures for beautiful code
export const ThemeFonts = {
  FONT_HEADING: "'Plus Jakarta Sans Variable', 'Plus Jakarta Sans', sans-serif",
  FONT_BODY: "'Inter Variable', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
  FONT_MONO: "'JetBrains Mono Variable', 'Monaco', 'Consolas', monospace"
};

// Routes
export const ROUTES = {
  HOME: '/',
  ABOUT: '/about',
  CONTACT: '/contact',
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  DASHBOARD: '/dashboard'
};
