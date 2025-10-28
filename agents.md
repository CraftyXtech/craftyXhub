## Source: frontend/litho/.cursor/rules/litho-styling.mdc

# CraftyXhub React Template Styling Patterns

## SCSS Architecture

### Component-Specific Styling
Each component should have its own SCSS file following this pattern:

```scss
// components/Button/Button.scss
.btn {
  // Base button styles
  display: inline-block;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  text-align: center;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  
  // Variants
  &.btn-primary {
    background-color: var(--primary-color);
    color: white;
    
    &:hover {
      background-color: var(--primary-color-dark);
    }
  }
  
  &.btn-secondary {
    background-color: var(--secondary-color);
    color: white;
    
    &:hover {
      background-color: var(--secondary-color-dark);
    }
  }
  
  // Sizes
  &.btn-sm {
    padding: 0.5rem 1rem;
    font-size: 0.75rem;
  }
  
  &.btn-lg {
    padding: 1rem 2rem;
    font-size: 1rem;
  }
  
  // States
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}
```

### Utility Classes
Create reusable utility classes in a separate utilities file:

```scss
// styles/utilities.scss
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.d-flex { display: flex; }
.d-block { display: block; }
.d-none { display: none; }

.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.justify-around { justify-content: space-around; }

.align-center { align-items: center; }
.align-start { align-items: flex-start; }
.align-end { align-items: flex-end; }

.m-0 { margin: 0; }
.mt-1 { margin-top: 0.25rem; }
.mb-2 { margin-bottom: 0.5rem; }

.p-1 { padding: 0.25rem; }
.px-2 { padding-left: 0.5rem; padding-right: 0.5rem; }
.py-3 { padding-top: 0.75rem; padding-bottom: 0.75rem; }
```

## Tailwind CSS Integration

### Custom Tailwind Configuration
Extend Tailwind with project-specific utilities:

```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        secondary: {
          500: '#64748b',
          600: '#475569',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      boxShadow: {
        'soft': '0 2px 15px 0 rgba(0, 0, 0, 0.08)',
        'medium': '0 4px 25px 0 rgba(0, 0, 0, 0.12)',
      }
    },
  },
  plugins: [],
}
```

### Component Styling with Tailwind
Use Tailwind classes for rapid prototyping and component styling:

```jsx
const Button = ({ variant = 'primary', size = 'md', children, ...props }) => {
  const baseClasses = 'inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500',
    secondary: 'bg-gray-600 hover:bg-gray-700 text-white focus:ring-gray-500',
    outline: 'border-gray-300 bg-white hover:bg-gray-50 text-gray-700 focus:ring-blue-500'
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  };
  
  return (
    <button 
      className={`${baseClasses} ${variants[variant]} ${sizes[size]}`}
      {...props}
    >
      {children}
    </button>
  );
};
```

## Bootstrap Integration

### Bootstrap Component Overrides
Override Bootstrap components with custom SCSS:

```scss
// styles/bootstrap-overrides.scss
@import '~bootstrap/scss/functions';
@import '~bootstrap/scss/variables';

// Custom button styles
.btn {
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.2s ease-in-out;
  
  &.btn-primary {
    background-color: var(--primary-color);
    border-color: var(--primary-color);
    
    &:hover {
      background-color: var(--primary-color-dark);
      border-color: var(--primary-color-dark);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
  }
}

// Custom card styles
.card {
  border: none;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.2s ease-in-out;
  
  &:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  }
}

// Custom form styles
.form-control {
  border-radius: 0.5rem;
  border: 1px solid #d1d5db;
  transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  
  &:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
}
```

### Responsive Design Patterns
Use Bootstrap's grid system with custom breakpoints:

```jsx
const ResponsiveLayout = () => {
  return (
    <div className="container-fluid">
      <div className="row">
        <div className="col-12 col-md-8 col-lg-9">
          <div className="main-content">
            {/* Main content */}
          </div>
        </div>
        <div className="col-12 col-md-4 col-lg-3">
          <div className="sidebar">
            {/* Sidebar content */}
          </div>
        </div>
      </div>
    </div>
  );
};
```

## CSS Variables and Theming

### Global CSS Variables
Define theme variables in a central location:

```scss
// styles/variables.scss
:root {
  // Colors
  --primary-color: #3b82f6;
  --primary-color-dark: #2563eb;
  --secondary-color: #64748b;
  --secondary-color-dark: #475569;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --error-color: #ef4444;
  
  // Typography
  --font-family-sans: 'Inter', system-ui, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  
  // Spacing
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  // Shadows
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  
  // Border radius
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
}
```

### Dark Mode Support
Implement dark mode with CSS variables:

```scss
// styles/dark-mode.scss
[data-theme="dark"] {
  --bg-primary: #1f2937;
  --bg-secondary: #111827;
  --text-primary: #f9fafb;
  --text-secondary: #d1d5db;
  --border-color: #374151;
}

[data-theme="light"] {
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --text-primary: #111827;
  --text-secondary: #6b7280;
  --border-color: #e5e7eb;
}

// Usage in components
.component {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}
```

## Animation and Transitions

### CSS Transitions
Add smooth transitions to interactive elements:

```scss
// styles/animations.scss
.fade-in {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.slide-in-left {
  animation: slideInLeft 0.3s ease-out;
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

// Hover effects
.card-hover {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  }
}
```

### Framer Motion Integration
Use Framer Motion for complex animations:

```jsx
import { motion } from 'framer-motion';

const AnimatedCard = ({ children, delay = 0 }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        duration: 0.5, 
        delay: delay,
        ease: "easeOut" 
      }}
      whileHover={{ 
        scale: 1.02,
        transition: { duration: 0.2 }
      }}
    >
      {children}
    </motion.div>
  );
};
```

## Best Practices

### File Organization
- Keep component styles close to components
- Use a central variables file for theme values
- Separate utility classes from component styles
- Use SCSS partials for better organization

### Performance
- Minimize CSS bundle size
- Use CSS variables for dynamic theming
- Avoid deep nesting in SCSS
- Use utility-first approach when possible

### Maintainability
- Use consistent naming conventions
- Document custom CSS classes
- Keep styles modular and reusable
- Use CSS custom properties for theming

### Accessibility
- Ensure sufficient color contrast
- Use focus indicators for interactive elements
- Support reduced motion preferences
- Test with screen readers
description:
globs:
alwaysApply: false
---

---

## Source: frontend/litho/.cursor/rules/litho-framework.mdc

# CraftyXhub React Template Framework Guide

This project uses the CraftyXhub React Template (v1.1.0) with React 18, Bootstrap 5, and SCSS. Follow these conventions and patterns when developing the frontend.

## Project Structure

The CraftyXhub template follows a component-based architecture:

- **src/App.jsx**: Main application entry point and routing from [App.jsx](mdc:frontend/litho/src/App.jsx)
- **components/**: Reusable UI components organized by functionality
- **pages/**: Page-level components and layouts
- **layouts/**: Layout components (header, footer, sidebar)
- **assets/**: Static assets, images, and styles
- **utils/**: Utility functions and helpers
- **contexts/**: React context providers for global state

## Tech Stack & Dependencies

### Core Framework (from [package.json](mdc:frontend/litho/package.json))
- **React 18.2.0**: Latest React with concurrent features
- **React Router DOM 6.8.1**: Client-side routing
- **Bootstrap 5.2.3**: UI framework and components
- **Sass 1.58.3**: CSS preprocessor for styling
- **Axios 1.3.4**: HTTP client for API calls

### UI & Animation Libraries
- **Framer Motion 10.12.4**: Animation library for smooth transitions
- **React Icons 4.7.1**: Icon library with multiple icon sets
- **Reactstrap 9.1.9**: Bootstrap components for React
- **SweetAlert2 11.7.3**: Beautiful alert dialogs

### Development Tools
- **Vite 4.1.0**: Fast build tool and dev server
- **ESLint 8.35.0**: Code linting and style enforcement
- **Prettier 2.8.4**: Code formatting

## Component Architecture

### Component File Structure
Each component should follow this file organization:

```
components/
  Button/
    Button.jsx          // Main component
    Button.scss         // Component styles
    index.js            // Export file
  Card/
    Card.jsx
    Card.scss
    index.js
```

### Component Export Pattern
```javascript
// components/Button/index.js
export { default } from './Button';
```

### Base Component Structure
```jsx
import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import './ComponentName.scss';

const ComponentName = ({ 
  className,
  children,
  variant = 'default',
  size = 'md',
  ...props 
}) => {
  const componentClass = classNames(
    'component-name',
    `component-name--${variant}`,
    `component-name--${size}`,
    className
  );

  return (
    <div className={componentClass} {...props}>
      {children}
    </div>
  );
};

ComponentName.propTypes = {
  className: PropTypes.string,
  children: PropTypes.node,
  variant: PropTypes.oneOf(['default', 'primary', 'secondary']),
  size: PropTypes.oneOf(['sm', 'md', 'lg'])
};

export default ComponentName;
```

## React Patterns

### Functional Components with Hooks
Use modern React patterns with hooks:

```jsx
import React, { useState, useEffect, useCallback } from 'react';

const DataComponent = ({ apiEndpoint }) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(apiEndpoint);
      setData(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [apiEndpoint]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {data.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  );
};
```

### Custom Hooks
Create reusable hooks for common functionality:

```jsx
// hooks/useLocalStorage.js
import { useState, useEffect } from 'react';

const useLocalStorage = (key, initialValue) => {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue];
};

// hooks/useApi.js
import { useState, useEffect } from 'react';
import axios from 'axios';

const useApi = (url, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await axios(url, options);
        setData(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url, options]);

  return { data, loading, error };
};
```

## State Management

### Context API for Global State
Use React Context for application-wide state:

```jsx
// contexts/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Validate token and set user
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUser = async () => {
    try {
      const response = await axios.get('/api/auth/me');
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    const response = await axios.post('/api/auth/login', credentials);
    const { token, user: userData } = response.data;
    
    localStorage.setItem('token', token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

## API Integration

### Axios Configuration
Set up axios instance with interceptors:

```jsx
// utils/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### API Service Layer
Create service classes for API calls:

```jsx
// services/userService.js
import api from '../utils/api';

class UserService {
  static async getUsers(params = {}) {
    const response = await api.get('/users', { params });
    return response.data;
  }

  static async getUserById(id) {
    const response = await api.get(`/users/${id}`);
    return response.data;
  }

  static async createUser(userData) {
    const response = await api.post('/users', userData);
    return response.data;
  }

  static async updateUser(id, userData) {
    const response = await api.put(`/users/${id}`, userData);
    return response.data;
  }

  static async deleteUser(id) {
    const response = await api.delete(`/users/${id}`);
    return response.data;
  }
}

export default UserService;
```

## Routing and Navigation

### React Router Setup
Configure routes with protected routes:

```jsx
// App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './layouts/Layout';
import Home from './pages/Home';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Users from './pages/Users';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) return <div>Loading...</div>;
  
  return user ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route index element={<Home />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="users" element={<Users />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
```

## Form Handling

### React Hook Form Integration
Use React Hook Form for complex forms:

```jsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { Form, FormGroup, Label, Input, Button } from 'reactstrap';

const UserForm = ({ onSubmit, initialData = {} }) => {
  const { register, handleSubmit, formState: { errors }, reset } = useForm({
    defaultValues: initialData
  });

  const onFormSubmit = (data) => {
    onSubmit(data);
    reset();
  };

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormGroup>
        <Label for="name">Name</Label>
        <Input
          id="name"
          type="text"
          {...register('name', { required: 'Name is required' })}
          invalid={!!errors.name}
        />
        {errors.name && <div className="invalid-feedback">{errors.name.message}</div>}
      </FormGroup>
      
      <FormGroup>
        <Label for="email">Email</Label>
        <Input
          id="email"
          type="email"
          {...register('email', { 
            required: 'Email is required',
            pattern: {
              value: /^\S+@\S+$/i,
              message: 'Invalid email address'
            }
          })}
          invalid={!!errors.email}
        />
        {errors.email && <div className="invalid-feedback">{errors.email.message}</div>}
      </FormGroup>
      
      <Button type="submit" color="primary">Submit</Button>
    </Form>
  );
};
```

## Error Handling and Loading States

### Error Boundary Component
```jsx
// components/ErrorBoundary.jsx
import React from 'react';
import PropTypes from 'prop-types';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired
};

export default ErrorBoundary;
```

### Loading Component
```jsx
// components/Loading.jsx
import React from 'react';
import PropTypes from 'prop-types';

const Loading = ({ size = 'md', text = 'Loading...' }) => {
  const sizeClasses = {
    sm: 'spinner-border-sm',
    md: '',
    lg: 'spinner-border-lg'
  };

  return (
    <div className="d-flex justify-content-center align-items-center p-4">
      <div className={`spinner-border ${sizeClasses[size]}`} role="status">
        <span className="visually-hidden">{text}</span>
      </div>
      {text && <span className="ms-2">{text}</span>}
    </div>
  );
};

Loading.propTypes = {
  size: PropTypes.oneOf(['sm', 'md', 'lg']),
  text: PropTypes.string
};

export default Loading;
```

## Performance Optimization

### React.memo for Component Optimization
```jsx
import React from 'react';

const UserCard = React.memo(({ user, onEdit, onDelete }) => {
  console.log('UserCard rendered for:', user.name);
  
  return (
    <div className="user-card">
      <h3>{user.name}</h3>
      <p>{user.email}</p>
      <button onClick={() => onEdit(user.id)}>Edit</button>
      <button onClick={() => onDelete(user.id)}>Delete</button>
    </div>
  );
});

export default UserCard;
```

### Code Splitting with React.lazy
```jsx
import React, { Suspense, lazy } from 'react';
import Loading from './components/Loading';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Users = lazy(() => import('./pages/Users'));
const Settings = lazy(() => import('./pages/Settings'));

const App = () => {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/users" element={<Users />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
};
```

## Best Practices

### Code Organization
- Use functional components with hooks
- Keep components small and focused
- Use custom hooks for reusable logic
- Organize files by feature, not by type

### Performance
- Use React.memo for expensive components
- Implement code splitting for large applications
- Optimize images and assets
- Use lazy loading for non-critical components

### Accessibility
- Use semantic HTML elements
- Provide alt text for images
- Ensure keyboard navigation works
- Use ARIA attributes when needed

### Testing
- Write unit tests for components
- Test user interactions
- Mock API calls in tests
- Use React Testing Library

### Development Workflow
- Use ESLint and Prettier for code quality
- Follow consistent naming conventions
- Document components with PropTypes
- Use environment variables for configuration
description:
globs:
alwaysApply: false
---

---

## Source: frontend/litho/.cursor/rules/litho-components.mdc

# CraftyXhub React Template Component Development Patterns

## Component Structure and Organization

### Atomic Design Pattern
Organize components using atomic design principles:

```
components/
  atoms/           # Basic building blocks
    Button/
    Input/
    Icon/
  molecules/       # Combinations of atoms
    FormField/
    Card/
    Modal/
  organisms/       # Complex components
    Header/
    Sidebar/
    DataTable/
  templates/       # Page-level components
    Dashboard/
    UserProfile/
  pages/           # Full pages
    Home/
    Users/
```

### Component File Structure
Each component should have this consistent structure:

```
ComponentName/
  ComponentName.jsx     # Main component file
  ComponentName.scss    # Component-specific styles
  index.js              # Export file
  ComponentName.test.jsx # Unit tests
  README.md             # Component documentation
```

## Component Patterns

### Compound Components Pattern
Create components that work together as a cohesive unit:

```jsx
// components/Modal/Modal.jsx
import React, { createContext, useContext, useState } from 'react';
import classNames from 'classnames';
import './Modal.scss';

const ModalContext = createContext();

const Modal = ({ children, isOpen, onClose, size = 'md' }) => {
  if (!isOpen) return null;

  return (
    <ModalContext.Provider value={{ onClose }}>
      <div className="modal-overlay" onClick={onClose}>
        <div 
          className={classNames('modal', `modal--${size}`)}
          onClick={(e) => e.stopPropagation()}
        >
          {children}
        </div>
      </div>
    </ModalContext.Provider>
  );
};

const ModalHeader = ({ children }) => {
  const { onClose } = useContext(ModalContext);
  
  return (
    <div className="modal-header">
      <h3 className="modal-title">{children}</h3>
      <button className="modal-close" onClick={onClose}>×</button>
    </div>
  );
};

const ModalBody = ({ children }) => (
  <div className="modal-body">{children}</div>
);

const ModalFooter = ({ children }) => (
  <div className="modal-footer">{children}</div>
);

// Attach sub-components
Modal.Header = ModalHeader;
Modal.Body = ModalBody;
Modal.Footer = ModalFooter;

export default Modal;
```

### Render Props Pattern
For flexible component composition:

```jsx
// components/DataProvider/DataProvider.jsx
import React, { useState, useEffect } from 'react';

const DataProvider = ({ endpoint, children }) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(endpoint);
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [endpoint]);

  return children({ data, loading, error });
};

export default DataProvider;

// Usage
const UserList = () => (
  <DataProvider endpoint="/api/users">
    {({ data, loading, error }) => {
      if (loading) return <div>Loading...</div>;
      if (error) return <div>Error: {error.message}</div>;
      
      return (
        <ul>
          {data.map(user => (
            <li key={user.id}>{user.name}</li>
          ))}
        </ul>
      );
    }}
  </DataProvider>
);
```

### Higher-Order Components (HOC)
For cross-cutting concerns like authentication:

```jsx
// components/withAuth.jsx
import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import Loading from './Loading';

const withAuth = (WrappedComponent) => {
  return function AuthenticatedComponent(props) {
    const { user, loading } = useAuth();

    if (loading) return <Loading />;
    if (!user) return <div>Please log in to access this content.</div>;

    return <WrappedComponent {...props} user={user} />;
  };
};

export default withAuth;

// Usage
const ProtectedDashboard = withAuth(Dashboard);
```

## Form Components

### Reusable Form Field Component
```jsx
// components/FormField/FormField.jsx
import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import { FormGroup, Label, Input, FormFeedback } from 'reactstrap';
import './FormField.scss';

const FormField = ({
  label,
  type = 'text',
  name,
  value,
  onChange,
  onBlur,
  error,
  required = false,
  placeholder,
  options = [],
  className,
  ...props
}) => {
  const fieldId = `field-${name}`;
  const hasError = !!error;

  const handleChange = (e) => {
    const value = type === 'checkbox' ? e.target.checked : e.target.value;
    onChange(name, value);
  };

  const renderInput = () => {
    const inputProps = {
      id: fieldId,
      name,
      type,
      value: type === 'checkbox' ? undefined : value,
      checked: type === 'checkbox' ? value : undefined,
      onChange: handleChange,
      onBlur: () => onBlur && onBlur(name),
      placeholder,
      invalid: hasError,
      ...props
    };

    switch (type) {
      case 'select':
        return (
          <Input {...inputProps}>
            <option value="">Select {label.toLowerCase()}</option>
            {options.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Input>
        );
      
      case 'textarea':
        return <Input type="textarea" {...inputProps} />;
      
      default:
        return <Input {...inputProps} />;
    }
  };

  return (
    <FormGroup className={classNames('form-field', className)}>
      {label && (
        <Label for={fieldId}>
          {label}
          {required && <span className="text-danger">*</span>}
        </Label>
      )}
      {renderInput()}
      {hasError && <FormFeedback>{error}</FormFeedback>}
    </FormGroup>
  );
};

FormField.propTypes = {
  label: PropTypes.string,
  type: PropTypes.oneOf(['text', 'email', 'password', 'number', 'tel', 'url', 'textarea', 'select', 'checkbox']),
  name: PropTypes.string.isRequired,
  value: PropTypes.any,
  onChange: PropTypes.func.isRequired,
  onBlur: PropTypes.func,
  error: PropTypes.string,
  required: PropTypes.bool,
  placeholder: PropTypes.string,
  options: PropTypes.arrayOf(PropTypes.shape({
    value: PropTypes.any,
    label: PropTypes.string
  })),
  className: PropTypes.string
};

export default FormField;
```

### Form Container Component
```jsx
// components/Form/Form.jsx
import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Form as BootstrapForm, Button } from 'reactstrap';
import FormField from '../FormField';
import './Form.scss';

const Form = ({
  fields,
  onSubmit,
  submitLabel = 'Submit',
  loading = false,
  className,
  children
}) => {
  const [values, setValues] = useState(
    fields.reduce((acc, field) => ({ ...acc, [field.name]: field.defaultValue || '' }), {})
  );
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  const handleChange = (name, value) => {
    setValues(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const handleBlur = (name) => {
    setTouched(prev => ({ ...prev, [name]: true }));
    // Validate field on blur
    const field = fields.find(f => f.name === name);
    if (field && field.validate) {
      const error = field.validate(values[name]);
      if (error) {
        setErrors(prev => ({ ...prev, [name]: error }));
      }
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate all fields
    const newErrors = {};
    fields.forEach(field => {
      if (field.validate) {
        const error = field.validate(values[field.name]);
        if (error) newErrors[field.name] = error;
      }
    });
    
    setErrors(newErrors);
    setTouched(fields.reduce((acc, field) => ({ ...acc, [field.name]: true }), {}));
    
    if (Object.keys(newErrors).length === 0) {
      onSubmit(values);
    }
  };

  return (
    <BootstrapForm onSubmit={handleSubmit} className={className}>
      {fields.map(field => (
        <FormField
          key={field.name}
          {...field}
          value={values[field.name]}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched[field.name] ? errors[field.name] : undefined}
        />
      ))}
      {children}
      <div className="form-actions">
        <Button 
          type="submit" 
          color="primary" 
          disabled={loading}
        >
          {loading ? 'Submitting...' : submitLabel}
        </Button>
      </div>
    </BootstrapForm>
  );
};

Form.propTypes = {
  fields: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string.isRequired,
    label: PropTypes.string,
    type: PropTypes.string,
    required: PropTypes.bool,
    validate: PropTypes.func,
    defaultValue: PropTypes.any,
    options: PropTypes.array
  })).isRequired,
  onSubmit: PropTypes.func.isRequired,
  submitLabel: PropTypes.string,
  loading: PropTypes.bool,
  className: PropTypes.string,
  children: PropTypes.node
};

export default Form;
```

## Data Display Components

### Data Table Component
```jsx
// components/DataTable/DataTable.jsx
import React, { useState, useMemo } from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import { Table, Input, Button } from 'reactstrap';
import './DataTable.scss';

const DataTable = ({
  data,
  columns,
  searchable = true,
  sortable = true,
  paginated = true,
  pageSize = 10,
  className
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [currentPage, setCurrentPage] = useState(1);

  // Filter data based on search term
  const filteredData = useMemo(() => {
    if (!searchTerm) return data;
    
    return data.filter(item =>
      columns.some(column =>
        String(item[column.key]).toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  }, [data, searchTerm, columns]);

  // Sort data
  const sortedData = useMemo(() => {
    if (!sortConfig.key) return filteredData;
    
    return [...filteredData].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];
      
      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [filteredData, sortConfig]);

  // Paginate data
  const paginatedData = useMemo(() => {
    if (!paginated) return sortedData;
    
    const startIndex = (currentPage - 1) * pageSize;
    return sortedData.slice(startIndex, startIndex + pageSize);
  }, [sortedData, currentPage, pageSize, paginated]);

  const handleSort = (key) => {
    if (!sortable) return;
    
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const totalPages = Math.ceil(sortedData.length / pageSize);

  return (
    <div className={classNames('data-table', className)}>
      {searchable && (
        <div className="data-table-search">
          <Input
            type="text"
            placeholder="Search..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      )}
      
      <Table responsive>
        <thead>
          <tr>
            {columns.map(column => (
              <th
                key={column.key}
                className={sortable && column.sortable !== false ? 'sortable' : ''}
                onClick={() => handleSort(column.key)}
              >
                {column.label}
                {sortConfig.key === column.key && (
                  <span className="sort-indicator">
                    {sortConfig.direction === 'asc' ? '↑' : '↓'}
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {paginatedData.map((item, index) => (
            <tr key={item.id || index}>
              {columns.map(column => (
                <td key={column.key}>
                  {column.render ? column.render(item) : item[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </Table>
      
      {paginated && totalPages > 1 && (
        <div className="data-table-pagination">
          <Button
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(prev => prev - 1)}
          >
            Previous
          </Button>
          <span className="pagination-info">
            Page {currentPage} of {totalPages}
          </span>
          <Button
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage(prev => prev + 1)}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
};

DataTable.propTypes = {
  data: PropTypes.array.isRequired,
  columns: PropTypes.arrayOf(PropTypes.shape({
    key: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    sortable: PropTypes.bool,
    render: PropTypes.func
  })).isRequired,
  searchable: PropTypes.bool,
  sortable: PropTypes.bool,
  paginated: PropTypes.bool,
  pageSize: PropTypes.number,
  className: PropTypes.string
};

export default DataTable;
```

### Card Component
```jsx
// components/Card/Card.jsx
import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import { Card as BootstrapCard, CardBody, CardTitle, CardText, CardImg, Button } from 'reactstrap';
import './Card.scss';

const Card = ({
  title,
  subtitle,
  text,
  image,
  imageAlt,
  actions,
  className,
  children,
  ...props
}) => {
  return (
    <BootstrapCard className={classNames('custom-card', className)} {...props}>
      {image && <CardImg top src={image} alt={imageAlt} />}
      <CardBody>
        {title && <CardTitle tag="h5">{title}</CardTitle>}
        {subtitle && <CardTitle tag="h6" className="text-muted">{subtitle}</CardTitle>}
        {text && <CardText>{text}</CardText>}
        {children}
        {actions && (
          <div className="card-actions">
            {actions.map((action, index) => (
              <Button
                key={index}
                {...action}
                className={classNames('me-2', action.className)}
              >
                {action.label}
              </Button>
            ))}
          </div>
        )}
      </CardBody>
    </BootstrapCard>
  );
};

Card.propTypes = {
  title: PropTypes.string,
  subtitle: PropTypes.string,
  text: PropTypes.string,
  image: PropTypes.string,
  imageAlt: PropTypes.string,
  actions: PropTypes.arrayOf(PropTypes.shape({
    label: PropTypes.string.isRequired,
    onClick: PropTypes.func,
    color: PropTypes.string,
    className: PropTypes.string
  })),
  className: PropTypes.string,
  children: PropTypes.node
};

export default Card;
```

## Layout Components

### Grid System Component
```jsx
// components/Grid/Grid.jsx
import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import { Container, Row, Col } from 'reactstrap';
import './Grid.scss';

const Grid = ({
  container = true,
  fluid = false,
  children,
  className,
  ...props
}) => {
  const containerClass = container ? (fluid ? 'container-fluid' : 'container') : '';
  
  return (
    <div className={classNames(containerClass, className)} {...props}>
      {children}
    </div>
  );
};

const GridRow = ({ children, className, ...props }) => (
  <Row className={className} {...props}>
    {children}
  </Row>
);

const GridCol = ({
  xs, sm, md, lg, xl,
  offset,
  children,
  className,
  ...props
}) => {
  const colClasses = [];
  
  if (xs) colClasses.push(`col-${xs}`);
  if (sm) colClasses.push(`col-sm-${sm}`);
  if (md) colClasses.push(`col-md-${md}`);
  if (lg) colClasses.push(`col-lg-${lg}`);
  if (xl) colClasses.push(`col-xl-${xl}`);
  
  if (offset) {
    if (typeof offset === 'number') {
      colClasses.push(`offset-${offset}`);
    } else {
      Object.entries(offset).forEach(([breakpoint, value]) => {
        colClasses.push(`offset-${breakpoint}-${value}`);
      });
    }
  }
  
  return (
    <Col className={classNames(colClasses, className)} {...props}>
      {children}
    </Col>
  );
};

Grid.Row = GridRow;
Grid.Col = GridCol;

Grid.propTypes = {
  container: PropTypes.bool,
  fluid: PropTypes.bool,
  children: PropTypes.node,
  className: PropTypes.string
};

GridRow.propTypes = {
  children: PropTypes.node,
  className: PropTypes.string
};

GridCol.propTypes = {
  xs: PropTypes.number,
  sm: PropTypes.number,
  md: PropTypes.number,
  lg: PropTypes.number,
  xl: PropTypes.number,
  offset: PropTypes.oneOfType([PropTypes.number, PropTypes.object]),
  children: PropTypes.node,
  className: PropTypes.string
};

export default Grid;
```

## Best Practices

### Component Design
- Keep components small and focused on a single responsibility
- Use composition over inheritance
- Make components reusable with proper prop interfaces
- Provide sensible defaults for optional props

### Performance
- Use React.memo for expensive components
- Avoid unnecessary re-renders with proper key props
- Implement virtualization for large lists
- Lazy load components when appropriate

### Accessibility
- Use semantic HTML elements
- Provide proper ARIA attributes
- Ensure keyboard navigation works
- Test with screen readers

### Testing
- Write unit tests for component logic
- Test user interactions with React Testing Library
- Mock external dependencies
- Test accessibility features

### Documentation
- Document component props with PropTypes
- Provide usage examples in README files
- Document component variants and states
- Keep component APIs consistent
description:
globs:
alwaysApply: false
---

---

## Source: frontend/litho/.cursor/rules/litho-api-auth.mdc

# CraftyXhub React Template API Integration and Authentication Patterns

## Authentication Architecture

### Auth Context Provider
Implement a comprehensive authentication context:

```jsx
// contexts/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token && !isTokenExpired(token)) {
      try {
        const decoded = jwtDecode(token);
        setAuth({
          user: decoded,
          accessToken: token
        });
      } catch (error) {
        localStorage.removeItem('accessToken');
        setAuth({});
      }
    }
    setLoading(false);
  }, []);

  const login = async (credentials) => {
    try {
      const response = await axios.post('/api/auth/login', credentials);
      const { access_token, refresh_token, user } = response.data;
      
      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('refreshToken', refresh_token);
      
      setAuth({
        user,
        accessToken: access_token
      });
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.message || 'Login failed' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setAuth({});
  };

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) throw new Error('No refresh token');

      const response = await axios.post('/api/auth/refresh', {
        refresh_token: refreshToken
      });
      
      const { access_token } = response.data;
      localStorage.setItem('accessToken', access_token);
      
      setAuth(prev => ({
        ...prev,
        accessToken: access_token
      }));
      
      return access_token;
    } catch (error) {
      logout();
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ 
      auth, 
      setAuth, 
      login, 
      logout, 
      refreshToken, 
      loading,
      isAuthenticated: !!auth.accessToken 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

// Utility function to check token expiration
const isTokenExpired = (token) => {
  try {
    const decoded = jwtDecode(token);
    const currentTime = Date.now() / 1000;
    return decoded.exp < currentTime;
  } catch {
    return true;
  }
};
```

### Axios Configuration with Interceptors
Set up axios with automatic token refresh:

```jsx
// utils/axios.js
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Public axios instance
export const axiosPublic = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Private axios instance (for authenticated requests)
export const axiosPrivate = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor for private instance
axiosPrivate.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling token expiration
axiosPrivate.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error?.config;

    if (error?.response?.status === 401 && !originalRequest?.sent) {
      originalRequest.sent = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axiosPublic.post('/auth/refresh', {
            refresh_token: refreshToken
          });
          
          const { access_token } = response.data;
          localStorage.setItem('accessToken', access_token);
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          
          return axiosPrivate(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/auth/login';
      }
    }
    
    return Promise.reject(error);
  }
);
```

## Service Layer Patterns

### Base Service Class
Create a reusable base service for common CRUD operations:

```jsx
// services/BaseService.js
import { axiosPrivate } from '../utils/axios';

class BaseService {
  constructor(endpoint) {
    this.endpoint = endpoint;
  }

  async getAll(params = {}) {
    const response = await axiosPrivate.get(this.endpoint, { params });
    return response.data;
  }

  async getById(id) {
    const response = await axiosPrivate.get(`${this.endpoint}/${id}`);
    return response.data;
  }

  async create(data) {
    const response = await axiosPrivate.post(this.endpoint, data);
    return response.data;
  }

  async update(id, data) {
    const response = await axiosPrivate.put(`${this.endpoint}/${id}`, data);
    return response.data;
  }

  async delete(id) {
    const response = await axiosPrivate.delete(`${this.endpoint}/${id}`);
    return response.data;
  }

  async bulkDelete(ids) {
    const response = await axiosPrivate.post(`${this.endpoint}/bulk-delete`, { ids });
    return response.data;
  }
}

export default BaseService;
```

### User Service Implementation
```jsx
// services/UserService.js
import BaseService from './BaseService';
import { axiosPrivate } from '../utils/axios';

class UserService extends BaseService {
  constructor() {
    super('/users');
  }

  async getCurrentUser() {
    const response = await axiosPrivate.get('/users/me');
    return response.data;
  }

  async updateProfile(data) {
    const response = await axiosPrivate.put('/users/me', data);
    return response.data;
  }

  async changePassword(data) {
    const response = await axiosPrivate.post('/users/change-password', data);
    return response.data;
  }

  async uploadAvatar(file) {
    const formData = new FormData();
    formData.append('avatar', file);
    
    const response = await axiosPrivate.post('/users/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    });
    return response.data;
  }

  async searchUsers(query, filters = {}) {
    const params = { q: query, ...filters };
    const response = await axiosPrivate.get('/users/search', { params });
    return response.data;
  }

  async getUserStats(userId) {
    const response = await axiosPrivate.get(`/users/${userId}/stats`);
    return response.data;
  }
}

export const userService = new UserService();
```

### Post Service with Advanced Features
```jsx
// services/PostService.js
import BaseService from './BaseService';
import { axiosPrivate } from '../utils/axios';

class PostService extends BaseService {
  constructor() {
    super('/posts');
  }

  async getPublishedPosts(page = 1, limit = 10) {
    const params = { page, limit, status: 'published' };
    const response = await axiosPrivate.get(this.endpoint, { params });
    return response.data;
  }

  async getDraftPosts() {
    const params = { status: 'draft' };
    const response = await axiosPrivate.get(this.endpoint, { params });
    return response.data;
  }

  async publishPost(id) {
    const response = await axiosPrivate.post(`${this.endpoint}/${id}/publish`);
    return response.data;
  }

  async unpublishPost(id) {
    const response = await axiosPrivate.post(`${this.endpoint}/${id}/unpublish`);
    return response.data;
  }

  async getPostAnalytics(id) {
    const response = await axiosPrivate.get(`${this.endpoint}/${id}/analytics`);
    return response.data;
  }

  async bulkUpdateStatus(ids, status) {
    const response = await axiosPrivate.post(`${this.endpoint}/bulk-status`, {
      ids,
      status
    });
    return response.data;
  }

  async uploadImage(file) {
    const formData = new FormData();
    formData.append('image', file);
    
    const response = await axiosPrivate.post(`${this.endpoint}/upload-image`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    });
    return response.data;
  }

  async getPostsByCategory(categoryId, page = 1, limit = 10) {
    const params = { category_id: categoryId, page, limit };
    const response = await axiosPrivate.get(this.endpoint, { params });
    return response.data;
  }

  async getPostsByTag(tagId, page = 1, limit = 10) {
    const params = { tag_id: tagId, page, limit };
    const response = await axiosPrivate.get(this.endpoint, { params });
    return response.data;
  }
}

export const postService = new PostService();
```

## Data Management Hooks

### useApi Hook for Data Fetching
```jsx
// hooks/useApi.js
import { useState, useEffect, useCallback } from 'react';
import { axiosPrivate } from '../utils/axios';
import { toast } from 'react-toastify';

export const useApi = (apiFunction, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiFunction();
      setData(result);
    } catch (err) {
      setError(err.response?.data?.message || err.message);
      toast.error("Failed to load data");
    } finally {
      setLoading(false);
    }
  }, dependencies);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
};

// Usage example
const UsersList = () => {
  const { data: users, loading, error, refetch } = useApi(
    () => userService.getAll({ page: 1, limit: 10 }),
    []
  );

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {users?.map(user => (
        <div key={user.id}>{user.name}</div>
      ))}
      <button onClick={refetch}>Refresh</button>
    </div>
  );
};
```

### usePagination Hook
```jsx
// hooks/usePagination.js
import { useState, useMemo } from 'react';

export const usePagination = (data, itemsPerPage = 10) => {
  const [currentPage, setCurrentPage] = useState(1);

  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return data?.slice(startIndex, startIndex + itemsPerPage) || [];
  }, [data, currentPage, itemsPerPage]);

  const totalPages = Math.ceil((data?.length || 0) / itemsPerPage);

  const goToPage = (page) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  const goToNext = () => goToPage(currentPage + 1);
  const goToPrevious = () => goToPage(currentPage - 1);

  return {
    currentPage,
    totalPages,
    paginatedData,
    goToPage,
    goToNext,
    goToPrevious,
    hasNext: currentPage < totalPages,
    hasPrevious: currentPage > 1
  };
};
```

### useForm Hook with Validation
```jsx
// hooks/useForm.js
import { useState } from 'react';
import { toast } from 'react-toastify';

export const useForm = (initialValues, validationRules = {}) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const validateField = (name, value) => {
    const rules = validationRules[name];
    if (!rules) return '';

    if (rules.required && (!value || value.toString().trim() === '')) {
      return `${name} is required`;
    }

    if (rules.minLength && value.length < rules.minLength) {
      return `${name} must be at least ${rules.minLength} characters`;
    }

    if (rules.email && !/^\S+@\S+\.\S+$/.test(value)) {
      return 'Invalid email format';
    }

    if (rules.custom && typeof rules.custom === 'function') {
      return rules.custom(value);
    }

    return '';
  };

  const handleChange = (name, value) => {
    setValues(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleBlur = (name) => {
    const error = validateField(name, values[name]);
    setErrors(prev => ({ ...prev, [name]: error }));
  };

  const validate = () => {
    const newErrors = {};
    Object.keys(validationRules).forEach(field => {
      newErrors[field] = validateField(field, values[field]);
    });
    
    setErrors(newErrors);
    return Object.values(newErrors).every(error => !error);
  };

  const handleSubmit = async (submitFunction) => {
    if (!validate()) {
      toast.error("Please fix validation errors");
      return;
    }

    try {
      setLoading(true);
      await submitFunction(values);
      toast.success("Operation completed successfully");
    } catch (error) {
      toast.error(error.response?.data?.message || "Operation failed");
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setValues(initialValues);
    setErrors({});
  };

  return {
    values,
    errors,
    loading,
    handleChange,
    handleBlur,
    handleSubmit,
    reset,
    isValid: Object.values(errors).every(error => !error)
  };
};
```

## Protected Routes Pattern

### Route Protection Component
```jsx
// components/ProtectedRoute.jsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Loading from './Loading';

const ProtectedRoute = ({ children, requiredRole = null }) => {
  const { auth, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <Loading />;
  }

  if (!auth?.accessToken) {
    return <Navigate to="/auth/login" state={{ from: location }} replace />;
  }

  if (requiredRole && auth.user?.role !== requiredRole) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

export default ProtectedRoute;
```

### Route Configuration
```jsx
// App.jsx
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Layout from './layouts/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './pages/Dashboard';
import Users from './pages/Users';
import Posts from './pages/Posts';
import Login from './pages/auth/Login';
import Unauthorized from './pages/Unauthorized';

const router = createBrowserRouter([
  {
    path: "/auth/login",
    element: <Login />
  },
  {
    path: "/unauthorized",
    element: <Unauthorized />
  },
  {
    path: "/",
    element: (
      <ProtectedRoute>
        <Layout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Dashboard />
      },
      {
        path: "users",
        element: (
          <ProtectedRoute requiredRole="admin">
            <Users />
          </ProtectedRoute>
        )
      },
      {
        path: "posts",
        element: <Posts />
      }
    ]
  }
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
```

## Error Handling Patterns

### Global Error Handler
```jsx
// utils/errorHandler.js
import { toast } from 'react-toastify';

export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        toast.error(data.message || "Bad request");
        break;
      case 401:
        toast.error("Session expired. Please login again.");
        localStorage.removeItem('accessToken');
        window.location.href = '/auth/login';
        break;
      case 403:
        toast.error("You don't have permission to perform this action");
        break;
      case 404:
        toast.error("Resource not found");
        break;
      case 422:
        // Validation errors
        if (data.errors) {
          Object.values(data.errors).forEach(errorArray => {
            errorArray.forEach(error => toast.error(error));
          });
        } else {
          toast.error(data.message || "Validation failed");
        }
        break;
      case 500:
        toast.error("Server error. Please try again later.");
        break;
      default:
        toast.error("An unexpected error occurred");
    }
  } else if (error.request) {
    // Network error
    toast.error("Network error. Please check your connection.");
  } else {
    // Other error
    toast.error(error.message || "An unexpected error occurred");
  }
};
```

### Error Boundary Component
```jsx
// components/ErrorBoundary.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { Button } from 'reactstrap';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error,
      errorInfo
    });
    
    // Log error to service
    console.error('Error caught by boundary:', error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary text-center p-5">
          <h2 className="mb-3">Something went wrong</h2>
          <p className="text-muted mb-4">
            We're sorry, but something unexpected happened. Please try again.
          </p>
          <Button color="primary" onClick={this.handleRetry}>
            Try Again
          </Button>
          {process.env.NODE_ENV === 'development' && (
            <details className="mt-4 text-left">
              <summary>Error Details (Development)</summary>
              <pre className="mt-2 p-3 bg-light rounded">
                {this.state.error && this.state.error.toString()}
                <br />
                {this.state.errorInfo.componentStack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired
};

export default ErrorBoundary;
```

## Best Practices

### API Service Organization
- Create separate service classes for each domain
- Use consistent method naming (getAll, getById, create, update, delete)
- Implement proper error handling in services
- Use TypeScript for better type safety (when possible)
- Cache frequently accessed data

### Authentication Security
- Store JWT tokens securely (consider httpOnly cookies for production)
- Implement proper token refresh logic
- Handle token expiration gracefully
- Use HTTPS in production
- Validate tokens on both client and server

### Performance Optimization
- Implement request/response interceptors for common logic
- Use React Query or SWR for advanced caching
- Debounce search requests
- Implement pagination for large datasets
- Use loading states and skeleton screens

### Error Management
- Provide meaningful error messages to users
- Log errors for debugging
- Implement retry logic for failed requests
- Use global error boundaries
- Handle network failures gracefully
description:
globs:
alwaysApply: false
---

---

## Source: frontend/admin/.cursor/rules/dashlite-api-auth.mdc

# DashLite API Integration and Authentication Patterns

## Authentication Architecture

### Auth Context Provider
Use the existing AuthProvider pattern from your codebase:

```javascript
import { createContext, useContext, useState, useEffect } from "react";
import { jwtDecode } from "jwt-decode";
import { isTokenExpired } from "./isTokenExpired";

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token && !isTokenExpired(token)) {
      try {
        const decoded = jwtDecode(token);
        setAuth({
          user: decoded,
          accessToken: token
        });
      } catch (error) {
        localStorage.removeItem('accessToken');
        setAuth({});
      }
    }
    setLoading(false);
  }, []);

  return (
    <AuthContext.Provider value={{ auth, setAuth, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

### Axios Configuration
Set up axios instances for public and private requests:

```javascript
import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Public axios instance
export const axiosPublic = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Private axios instance (for authenticated requests)
export const axiosPrivate = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor for private instance
axiosPrivate.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling token expiration
axiosPrivate.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error?.config;

    if (error?.response?.status === 401 && !originalRequest?.sent) {
      originalRequest.sent = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axiosPublic.post('/auth/refresh', {
            refresh_token: refreshToken
          });
          
          const { access_token } = response.data;
          localStorage.setItem('accessToken', access_token);
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          
          return axiosPrivate(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/auth/login';
      }
    }
    
    return Promise.reject(error);
  }
);
```

### Custom Hooks for API

#### useAxiosPrivate Hook
```javascript
import { useEffect } from "react";
import { axiosPrivate } from "./axios";
import { useAuth } from "./useAuth";
import { useRefreshToken } from "./useRefreshToken";

const useAxiosPrivate = () => {
  const refresh = useRefreshToken();
  const { auth } = useAuth();

  useEffect(() => {
    const requestIntercept = axiosPrivate.interceptors.request.use(
      (config) => {
        if (!config.headers['Authorization']) {
          config.headers['Authorization'] = `Bearer ${auth?.accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    const responseIntercept = axiosPrivate.interceptors.response.use(
      (response) => response,
      async (error) => {
        const prevRequest = error?.config;
        if (error?.response?.status === 401 && !prevRequest?.sent) {
          prevRequest.sent = true;
          const newAccessToken = await refresh();
          prevRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
          return axiosPrivate(prevRequest);
        }
        return Promise.reject(error);
      }
    );

    return () => {
      axiosPrivate.interceptors.request.eject(requestIntercept);
      axiosPrivate.interceptors.response.eject(responseIntercept);
    };
  }, [auth, refresh]);

  return axiosPrivate;
};

export default useAxiosPrivate;
```

#### useRefreshToken Hook
```javascript
import { useAuth } from "./useAuth";
import { axiosPublic } from "./axios";

const useRefreshToken = () => {
  const { setAuth } = useAuth();

  const refresh = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      const response = await axiosPublic.post('/auth/refresh', {
        refresh_token: refreshToken
      });

      const { access_token, user } = response.data;
      localStorage.setItem('accessToken', access_token);
      
      setAuth(prev => ({
        ...prev,
        user,
        accessToken: access_token
      }));

      return access_token;
    } catch (error) {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      setAuth({});
      throw error;
    }
  };

  return refresh;
};

export default useRefreshToken;
```

## Service Layer Patterns

### Base Service Class
```javascript
class BaseService {
  constructor(endpoint) {
    this.endpoint = endpoint;
  }

  async getAll(params = {}) {
    const response = await axiosPrivate.get(this.endpoint, { params });
    return response.data;
  }

  async getById(id) {
    const response = await axiosPrivate.get(`${this.endpoint}/${id}`);
    return response.data;
  }

  async create(data) {
    const response = await axiosPrivate.post(this.endpoint, data);
    return response.data;
  }

  async update(id, data) {
    const response = await axiosPrivate.put(`${this.endpoint}/${id}`, data);
    return response.data;
  }

  async delete(id) {
    const response = await axiosPrivate.delete(`${this.endpoint}/${id}`);
    return response.data;
  }

  async bulkDelete(ids) {
    const response = await axiosPrivate.post(`${this.endpoint}/bulk-delete`, { ids });
    return response.data;
  }
}
```

### User Service Implementation
```javascript
import { axiosPrivate, axiosPublic } from "./axios";

class UserService extends BaseService {
  constructor() {
    super('/users');
  }

  async getCurrentUser() {
    const response = await axiosPrivate.get('/users/me');
    return response.data;
  }

  async updateProfile(data) {
    const response = await axiosPrivate.put('/users/me', data);
    return response.data;
  }

  async changePassword(data) {
    const response = await axiosPrivate.post('/users/change-password', data);
    return response.data;
  }

  async uploadAvatar(file) {
    const formData = new FormData();
    formData.append('avatar', file);
    
    const response = await axiosPrivate.post('/users/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    });
    return response.data;
  }

  async searchUsers(query, filters = {}) {
    const params = { q: query, ...filters };
    const response = await axiosPrivate.get('/users/search', { params });
    return response.data;
  }
}

export const userService = new UserService();
```

### Post Service with Advanced Features
```javascript
class PostService extends BaseService {
  constructor() {
    super('/posts');
  }

  async getPublishedPosts(page = 1, limit = 10) {
    const params = { page, limit, status: 'published' };
    const response = await axiosPrivate.get(this.endpoint, { params });
    return response.data;
  }

  async getDraftPosts() {
    const params = { status: 'draft' };
    const response = await axiosPrivate.get(this.endpoint, { params });
    return response.data;
  }

  async publishPost(id) {
    const response = await axiosPrivate.post(`${this.endpoint}/${id}/publish`);
    return response.data;
  }

  async unpublishPost(id) {
    const response = await axiosPrivate.post(`${this.endpoint}/${id}/unpublish`);
    return response.data;
  }

  async getPostAnalytics(id) {
    const response = await axiosPrivate.get(`${this.endpoint}/${id}/analytics`);
    return response.data;
  }

  async bulkUpdateStatus(ids, status) {
    const response = await axiosPrivate.post(`${this.endpoint}/bulk-status`, {
      ids,
      status
    });
    return response.data;
  }

  async uploadImage(file) {
    const formData = new FormData();
    formData.append('image', file);
    
    const response = await axiosPrivate.post(`${this.endpoint}/upload-image`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    });
    return response.data;
  }
}

export const postService = new PostService();
```

## Data Management Hooks

### useApi Hook for Data Fetching
```javascript
import { useState, useEffect, useCallback } from "react";
import { toast } from "react-toastify";

export const useApi = (apiFunction, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiFunction();
      setData(result);
    } catch (err) {
      setError(err.response?.data?.message || err.message);
      toast.error("Failed to load data");
    } finally {
      setLoading(false);
    }
  }, dependencies);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
};

// Usage example
const UsersList = () => {
  const { data: users, loading, error, refetch } = useApi(
    () => userService.getAll({ page: 1, limit: 10 }),
    []
  );

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {users?.map(user => (
        <div key={user.id}>{user.name}</div>
      ))}
      <button onClick={refetch}>Refresh</button>
    </div>
  );
};
```

### usePagination Hook
```javascript
import { useState, useMemo } from "react";

export const usePagination = (data, itemsPerPage = 10) => {
  const [currentPage, setCurrentPage] = useState(1);

  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return data?.slice(startIndex, startIndex + itemsPerPage) || [];
  }, [data, currentPage, itemsPerPage]);

  const totalPages = Math.ceil((data?.length || 0) / itemsPerPage);

  const goToPage = (page) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  const goToNext = () => goToPage(currentPage + 1);
  const goToPrevious = () => goToPage(currentPage - 1);

  return {
    currentPage,
    totalPages,
    paginatedData,
    goToPage,
    goToNext,
    goToPrevious,
    hasNext: currentPage < totalPages,
    hasPrevious: currentPage > 1
  };
};
```

### useForm Hook with Validation
```javascript
import { useState } from "react";
import { toast } from "react-toastify";

export const useForm = (initialValues, validationRules = {}) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const validateField = (name, value) => {
    const rules = validationRules[name];
    if (!rules) return '';

    if (rules.required && (!value || value.toString().trim() === '')) {
      return `${name} is required`;
    }

    if (rules.minLength && value.length < rules.minLength) {
      return `${name} must be at least ${rules.minLength} characters`;
    }

    if (rules.email && !/^\S+@\S+\.\S+$/.test(value)) {
      return 'Invalid email format';
    }

    if (rules.custom && typeof rules.custom === 'function') {
      return rules.custom(value);
    }

    return '';
  };

  const handleChange = (name, value) => {
    setValues(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleBlur = (name) => {
    const error = validateField(name, values[name]);
    setErrors(prev => ({ ...prev, [name]: error }));
  };

  const validate = () => {
    const newErrors = {};
    Object.keys(validationRules).forEach(field => {
      newErrors[field] = validateField(field, values[field]);
    });
    
    setErrors(newErrors);
    return Object.values(newErrors).every(error => !error);
  };

  const handleSubmit = async (submitFunction) => {
    if (!validate()) {
      toast.error("Please fix validation errors");
      return;
    }

    try {
      setLoading(true);
      await submitFunction(values);
      toast.success("Operation completed successfully");
    } catch (error) {
      toast.error(error.response?.data?.message || "Operation failed");
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setValues(initialValues);
    setErrors({});
  };

  return {
    values,
    errors,
    loading,
    handleChange,
    handleBlur,
    handleSubmit,
    reset,
    isValid: Object.values(errors).every(error => !error)
  };
};
```

## Protected Routes Pattern

### Route Protection Component
```javascript
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "@/api/useAuth";

const ProtectedRoute = ({ children, requiredRole = null }) => {
  const { auth, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center min-vh-100">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (!auth?.accessToken) {
    return <Navigate to="/auth/login" state={{ from: location }} replace />;
  }

  if (requiredRole && auth.user?.role !== requiredRole) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

export default ProtectedRoute;
```

### Route Configuration
```javascript
import { createBrowserRouter } from "react-router-dom";
import ProtectedRoute from "./ProtectedRoute";
import Dashboard from "@/pages/Dashboard";
import Users from "@/pages/Users";
import Posts from "@/pages/Posts";
import Login from "@/pages/auth/Login";

export const router = createBrowserRouter([
  {
    path: "/auth/login",
    element: <Login />
  },
  {
    path: "/",
    element: (
      <ProtectedRoute>
        <Layout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Dashboard />
      },
      {
        path: "users",
        element: (
          <ProtectedRoute requiredRole="admin">
            <Users />
          </ProtectedRoute>
        )
      },
      {
        path: "posts",
        element: <Posts />
      }
    ]
  }
]);
```

## Error Handling Patterns

### Global Error Handler
```javascript
import { toast } from "react-toastify";

export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        toast.error(data.message || "Bad request");
        break;
      case 401:
        toast.error("Session expired. Please login again.");
        localStorage.removeItem('accessToken');
        window.location.href = '/auth/login';
        break;
      case 403:
        toast.error("You don't have permission to perform this action");
        break;
      case 404:
        toast.error("Resource not found");
        break;
      case 422:
        // Validation errors
        if (data.errors) {
          Object.values(data.errors).forEach(errorArray => {
            errorArray.forEach(error => toast.error(error));
          });
        } else {
          toast.error(data.message || "Validation failed");
        }
        break;
      case 500:
        toast.error("Server error. Please try again later.");
        break;
      default:
        toast.error("An unexpected error occurred");
    }
  } else if (error.request) {
    // Network error
    toast.error("Network error. Please check your connection.");
  } else {
    // Other error
    toast.error(error.message || "An unexpected error occurred");
  }
};
```

## Best Practices

### API Service Organization
- Create separate service classes for each domain
- Use consistent method naming (getAll, getById, create, update, delete)
- Implement proper error handling in services
- Use TypeScript for better type safety
- Cache frequently accessed data

### Authentication Security
- Store JWT tokens securely (consider httpOnly cookies for production)
- Implement proper token refresh logic
- Handle token expiration gracefully
- Use HTTPS in production
- Validate tokens on both client and server

### Performance Optimization
- Implement request/response interceptors for common logic
- Use React Query or SWR for advanced caching
- Debounce search requests
- Implement pagination for large datasets
- Use loading states and skeleton screens

### Error Management
- Provide meaningful error messages to users
- Log errors for debugging
- Implement retry logic for failed requests
- Use global error boundaries
- Handle network failures gracefully
description:
globs:
alwaysApply: false
---

---

## Source: frontend/admin/.cursor/rules/dashlite-framework.mdc

# DashLite React Admin Template Framework Guide

This project uses the DashLite React Admin Template (v2.0.0) with Vite, React 18, and Bootstrap 5. Follow these conventions and patterns when developing the admin dashboard.

## Project Structure

The DashLite template follows a modular admin dashboard architecture:

- **src/App.jsx**: Main application entry point and configuration from [App.jsx](mdc:frontend/admin/src/App.jsx)
- **components/**: Reusable UI components organized by functionality
- **layout/**: Layout components (sidebar, header, footer) from [Index.jsx](mdc:frontend/admin/src/layout/Index.jsx)
- **pages/**: Page-level components organized by feature areas
- **api/**: Authentication and API service layer
- **route/**: React Router configuration and route management
- **assets/**: Static assets, styles, and images
- **utils/**: Utility functions and helpers

## Tech Stack & Dependencies

### Core Framework (from [package.json](mdc:frontend/admin/package.json))
- **React 18.3.1**: Latest React with concurrent features
- **Vite 6.1.0**: Fast build tool and dev server
- **React Router DOM 7.2.0**: Client-side routing
- **Bootstrap 5.3.3**: UI framework and components
- **Reactstrap 9.2.3**: Bootstrap components for React
- **Sass 1.56.1**: CSS preprocessor

### Admin-Specific Libraries
- **Chart.js 4.4.6**: Data visualization and charts
- **React-Chartjs-2 5.2.0**: React wrapper for Chart.js
- **React-Data-Table-Component 7.6.2**: Advanced data tables
- **React-Hook-Form 7.53.1**: Form handling and validation
- **React-Select 5.8.2**: Advanced select components
- **React-Datepicker 7.5.0**: Date and time pickers

### Rich Content & Media
- **TinyMCE 7.4.1**: Rich text editor
- **React-Dropzone 14.3.5**: File upload handling
- **React-Modal-Video 2.0.2**: Video modal components
- **React-Beautiful-DND 13.1.1**: Drag and drop functionality

### Utilities & Enhancements
- **Axios 1.10.0**: HTTP client for API calls
- **JWT-Decode 4.0.0**: JWT token handling
- **React-Toastify 10.0.6**: Toast notifications
- **SweetAlert2 11.4.8**: Beautiful alert dialogs
- **Classnames 2.5.1**: Conditional CSS class management

## Build Configuration

### Vite Setup
From [vite.config.js](mdc:frontend/admin/vite.config.js):
```javascript
export default defineConfig({
  plugins: [react()],
  css: {
    devSourcemap: true
  },
  resolve: {
    alias: {
      '@': '/src',  // Use @ for src imports
    },
  },
  build: {
    commonjsOptions: {
      transformMixedEsModules: true
    }
  },
})
```

### Tailwind Configuration
From [tailwind.config.js](mdc:frontend/admin/tailwind.config.js):
- **Custom Colors**: Primary and secondary color palettes
- **Typography**: Inter font family
- **Spacing**: Custom spacing values (18, 88)
- **Shadows**: Soft and medium shadow utilities
- **Preflight Disabled**: Prevents conflicts with Bootstrap

## Component Architecture

### Component Import Pattern
Use the centralized component exports from [Component.js](mdc:frontend/admin/src/components/Component.js):

```javascript
import {
  Block,
  BlockHead,
  BlockContent,
  BlockTitle,
  Row,
  Col,
  Button,
  Icon,
  DataTable,
  PreviewCard
} from "@/components/Component";
```

### Layout Structure
Main layout pattern from [layout/Index.jsx](mdc:frontend/admin/src/layout/Index.jsx):

```javascript
import { Outlet } from "react-router-dom";
import Sidebar from "./sidebar/Sidebar";
import Header from "./header/Header";
import Footer from "./footer/Footer";
import AppRoot from "./global/AppRoot";
import AppMain from "./global/AppMain";
import AppWrap from "./global/AppWrap";

const Layout = ({title, ...props}) => {
  return (
    <FileManagerProvider>
      <Head title={!title && 'Loading'} />
      <AppRoot>
        <AppMain>
          <Sidebar menuData={menu} fixed />
          <AppWrap>
            <Header fixed />
              <Outlet />
            <Footer />
          </AppWrap>
        </AppMain>
      </AppRoot>
    </FileManagerProvider>
  );
};
```

## DashLite Component Patterns

### Block Components (Primary Layout)
```javascript
import { Block, BlockHead, BlockContent, BlockTitle, BlockBetween } from "@/components/Component";

const PageComponent = () => {
  return (
    <Block>
      <BlockHead size="sm">
        <BlockBetween>
          <BlockHeadContent>
            <BlockTitle page>Page Title</BlockTitle>
          </BlockHeadContent>
          <BlockHeadContent>
            <Button color="primary">Action Button</Button>
          </BlockHeadContent>
        </BlockBetween>
      </BlockHead>
      <BlockContent>
        {/* Page content */}
      </BlockContent>
    </Block>
  );
};
```

### PreviewCard Pattern
```javascript
import { PreviewCard, PreviewTable, CodeBlock } from "@/components/Component";

const ComponentPreview = () => {
  return (
    <PreviewCard>
      <PreviewTable>
        {/* Component demonstration */}
      </PreviewTable>
      <CodeBlock language="jsx">
        {/* Code example */}
      </CodeBlock>
    </PreviewCard>
  );
};
```

### DataTable Pattern
```javascript
import { DataTable, DataTableBody, DataTableHead, DataTableRow, DataTableItem } from "@/components/Component";

const TableComponent = ({ data }) => {
  return (
    <DataTable className="card-stretch">
      <DataTableBody>
        <DataTableHead className="nk-tb-head">
          <DataTableRow>
            <DataTableItem className="nk-tb-col"><span>Name</span></DataTableItem>
            <DataTableItem className="nk-tb-col"><span>Status</span></DataTableItem>
            <DataTableItem className="nk-tb-col nk-tb-col-tools">Action</DataTableItem>
          </DataTableRow>
        </DataTableHead>
        {data.map((item, idx) => (
          <DataTableRow key={idx}>
            <DataTableItem>{item.name}</DataTableItem>
            <DataTableItem>{item.status}</DataTableItem>
            <DataTableItem className="nk-tb-col-tools">
              <Button size="sm" color="primary">Edit</Button>
            </DataTableItem>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  );
};
```

## Authentication Integration

### Auth Context Usage
```javascript
import { useAuth } from "@/api/useAuth";
import { useAxiosPrivate } from "@/api/useAxiosPrivate";

const ProtectedComponent = () => {
  const { auth, setAuth } = useAuth();
  const axiosPrivate = useAxiosPrivate();
  
  // Component logic
};
```

### API Service Pattern
```javascript
import { axiosPrivate } from "@/api/axios";

export const dataService = {
  getAll: () => axiosPrivate.get('/endpoint'),
  getById: (id) => axiosPrivate.get(`/endpoint/${id}`),
  create: (data) => axiosPrivate.post('/endpoint', data),
  update: (id, data) => axiosPrivate.put(`/endpoint/${id}`, data),
  delete: (id) => axiosPrivate.delete(`/endpoint/${id}`)
};
```

## Form Handling Patterns

### React Hook Form Integration
```javascript
import { useForm, Controller } from "react-hook-form";
import { FormGroup, Label, Input, Button } from "reactstrap";
import { RSelect } from "@/components/Component";

const FormComponent = () => {
  const { control, handleSubmit, formState: { errors } } = useForm();
  
  const onSubmit = (data) => {
    // Handle form submission
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <FormGroup>
        <Label className="form-label" htmlFor="full-name">
          Full Name *
        </Label>
        <div className="form-control-wrap">
          <Input
            type="text"
            id="full-name"
            className="form-control-lg"
            placeholder="Enter full name"
          />
        </div>
      </FormGroup>
      
      <FormGroup>
        <Label className="form-label">Status</Label>
        <div className="form-control-wrap">
          <RSelect
            options={statusOptions}
            placeholder="Select status"
            className="react-select-container"
            classNamePrefix="react-select"
          />
        </div>
      </FormGroup>
      
      <Button type="submit" color="primary" size="lg">
        Save Changes
      </Button>
    </form>
  );
};
```

## Chart Integration

### Chart.js Pattern
```javascript
import { Line, Bar, Pie, Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement);

const ChartComponent = ({ data, options }) => {
  return (
    <div className="chart-container">
      <Line data={data} options={options} />
    </div>
  );
};
```

## Notification Patterns

### Toast Notifications
```javascript
import { toast } from "react-toastify";

// Success notification
toast.success("Operation completed successfully!");

// Error notification
toast.error("Something went wrong!");

// Custom notification
toast("Custom message", {
  position: "top-right",
  autoClose: 3000,
  hideProgressBar: false,
});
```

### SweetAlert2 Integration
```javascript
import Swal from "sweetalert2";

const confirmDelete = async () => {
  const result = await Swal.fire({
    title: 'Are you sure?',
    text: "You won't be able to revert this!",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, delete it!'
  });
  
  if (result.isConfirmed) {
    // Proceed with deletion
    Swal.fire('Deleted!', 'Your file has been deleted.', 'success');
  }
};
```

## Styling Conventions

### Bootstrap + Tailwind Approach
- **Bootstrap**: Use for layout, components, and utilities
- **Tailwind**: Use for custom styling and design system
- **SCSS**: Use for component-specific styling

### Class Naming Patterns
```javascript
// DashLite specific classes
className="nk-block nk-block-lg"
className="card card-bordered card-preview"
className="nk-tb nk-tb-list is-separate"

// Combined with Tailwind
className="nk-block p-4 bg-white rounded-lg shadow-soft"
```

## Performance Best Practices

### Code Splitting
```javascript
import { lazy, Suspense } from "react";

const LazyComponent = lazy(() => import("./components/HeavyComponent"));

const App = () => (
  <Suspense fallback={<div>Loading...</div>}>
    <LazyComponent />
  </Suspense>
);
```

### Memoization
```javascript
import { memo, useMemo, useCallback, useState } from "react";
import { DataTable, DataTableBody, DataTableRow } from "@/components/Component";

const OptimizedComponent = memo(({ data, onUpdate }) => {
  const processedData = useMemo(() => {
    return data.filter(item => item.active);
  }, [data]);
  
  const handleClick = useCallback((id) => {
    onUpdate(id);
  }, [onUpdate]);
  
  return (
    // Component JSX
  );
});
```

## Development Guidelines

### Import Organization
1. React and React libraries
2. Third-party libraries
3. DashLite components (using @ alias)
4. Local components and utilities
5. Styles and assets

### Component Structure
- Use functional components with hooks
- Implement proper error boundaries
- Use TypeScript-style prop validation where beneficial
- Follow DashLite's component composition patterns
- Maintain consistent spacing and indentation

### State Management
- Use React Context for global state
- Implement proper loading and error states
- Use React Hook Form for complex forms
- Cache API responses appropriately

### Security
- Validate all user inputs
- Use JWT tokens properly
- Implement proper route protection
- Sanitize data before rendering
- Follow OWASP security guidelines
description:
globs:
alwaysApply: false
---

---

## Source: frontend/admin/.cursor/rules/dashlite-styling-performance.mdc

# DashLite Styling, Performance, and Advanced Patterns

## Styling Architecture

### Bootstrap + Tailwind Integration
DashLite uses a hybrid approach with Bootstrap 5 and Tailwind CSS:

```javascript
// tailwind.config.js configuration
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        secondary: {
          500: '#64748b',
          600: '#475569',
        }
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      }
    },
  },
  // Disable preflight to avoid Bootstrap conflicts
  corePlugins: {
    preflight: false,
  },
}
```

### DashLite Class Naming Conventions

#### Core Layout Classes
```javascript
// Main layout structure
className="nk-app-root"           // Root container
className="nk-main"               // Main content area
className="nk-sidebar nk-sidebar-fixed"  // Fixed sidebar
className="nk-wrap nk-wrap-nosidebar"    // Content wrapper

// Block system (primary layout)
className="nk-block nk-block-lg"         // Large content block
className="nk-block-head nk-block-head-sm"  // Block header
className="nk-block-between"             // Space between elements
className="nk-block-head-content"       // Header content wrapper
```

#### Card and Content Classes
```javascript
// Card components
className="card card-bordered card-preview"    // Standard card with border
className="card card-stretch"                  // Full height card
className="card-inner card-inner-lg"          // Card content with padding

// Content areas
className="nk-content nk-content-fluid"       // Fluid content area
className="nk-content-inner"                  // Inner content wrapper
className="nk-content-body"                   // Main content body
```

#### Table Classes
```javascript
// Data table structure
className="nk-tb-list nk-tb-ulist"           // Table list container
className="nk-tb-item"                       // Table row
className="nk-tb-col"                        // Table column
className="nk-tb-col-tools"                  // Action column
className="nk-tb-col-check"                  // Checkbox column

// Table responsive classes
className="table-responsive table-middle"     // Responsive table wrapper
```

### Component Styling Patterns

#### Button Styling
```javascript
import { Button } from "reactstrap";
import { Icon } from "@/components/Component";

const StyledButtons = () => {
  return (
    <>
      {/* Primary button with icon */}
      <Button color="primary" size="md">
        <Icon name="plus" />
        <span>Add New</span>
      </Button>
      
      {/* Icon-only button */}
      <Button className="btn-icon btn-trigger" size="sm">
        <Icon name="more-h" />
      </Button>
      
      {/* Outline button */}
      <Button outline color="primary">
        Secondary Action
      </Button>
      
      {/* Button with custom DashLite classes */}
      <Button className="btn-dim btn-outline-light">
        <Icon name="eye" />
        <span>Preview</span>
      </Button>
    </>
  );
};
```

#### Form Styling
```javascript
import { FormGroup, Label, Input } from "reactstrap";
import { RSelect } from "@/components/Component";

const StyledForm = () => {
  return (
    <form className="form-validate is-alter">
      <div className="row g-gs">
        <div className="col-md-6">
          <FormGroup>
            <Label className="form-label" htmlFor="full-name">
              Full Name *
            </Label>
            <div className="form-control-wrap">
              <Input
                type="text"
                id="full-name"
                className="form-control-lg"
                placeholder="Enter full name"
              />
            </div>
          </FormGroup>
        </div>
        
        <div className="col-md-6">
          <FormGroup>
            <Label className="form-label">Status</Label>
            <div className="form-control-wrap">
              <RSelect
                options={statusOptions}
                placeholder="Select status"
                className="react-select-container"
                classNamePrefix="react-select"
              />
            </div>
          </FormGroup>
        </div>
      </div>
      
      {/* Form actions */}
      <div className="form-group">
        <Button type="submit" color="primary" size="lg">
          Save Changes
        </Button>
        <Button type="button" className="btn-dim ms-2">
          Cancel
        </Button>
      </div>
    </form>
  );
};
```

#### Status and Badge Styling
```javascript
import { Badge } from "reactstrap";

const StatusComponents = () => {
  return (
    <>
      {/* Status badges */}
      <Badge color="success" pill>Active</Badge>
      <Badge color="warning" pill>Pending</Badge>
      <Badge color="danger" pill>Suspended</Badge>
      
      {/* DashLite status classes */}
      <span className="tb-status text-success">Published</span>
      <span className="tb-status text-warning">Draft</span>
      <span className="tb-status text-danger">Archived</span>
      
      {/* Dot indicators */}
      <span className="dot dot-success"></span>
      <span className="dot dot-warning"></span>
      <span className="dot dot-danger"></span>
    </>
  );
};
```

## Performance Optimization

### Code Splitting and Lazy Loading
```javascript
import { lazy, Suspense } from "react";
import { Spinner } from "reactstrap";

const LazyComponent = lazy(() => import("@/pages/DataVisualization"));
const FileManager = lazy(() => import("@/pages/app/FileManager"));
const Calendar = lazy(() => import("@/pages/app/Calendar"));

// Loading component
const PageLoader = () => (
  <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
    <Spinner color="primary" />
  </div>
);

// Route with lazy loading
const AppRoutes = () => {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/data" element={<DataVisualization />} />
        <Route path="/files" element={<FileManager />} />
        <Route path="/calendar" element={<Calendar />} />
      </Routes>
    </Suspense>
  );
};
```

### React Performance Patterns
```javascript
import { memo, useMemo, useCallback, useState } from "react";
import { DataTable, DataTableBody, DataTableRow } from "@/components/Component";

const TableRow = memo(({ item, onEdit, onDelete }) => {
  const handleEdit = useCallback(() => {
    onEdit(item.id);
  }, [item.id, onEdit]);

  const handleDelete = useCallback(() => {
    onDelete(item.id);
  }, [item.id, onDelete]);

  return (
    <DataTableRow>
      <DataTableItem>{item.name}</DataTableItem>
      <DataTableItem>
        <Button size="sm" onClick={handleEdit}>Edit</Button>
        <Button size="sm" color="danger" onClick={handleDelete}>Delete</Button>
      </DataTableItem>
    </DataTableRow>
  );
});

const OptimizedDataTable = ({ data }) => {
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  const sortedData = useMemo(() => {
    if (!sortConfig.key) return data;
    
    return [...data].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];
      
      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [data, sortConfig]);

  const handleEdit = useCallback((id) => {
    // Edit logic
  }, []);

  const handleDelete = useCallback((id) => {
    // Delete logic
  }, []);

  return (
    <DataTable>
      <DataTableBody>
        {sortedData.map(item => (
          <TableRow
            key={item.id}
            item={item}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        ))}
      </DataTableBody>
    </DataTable>
  );
};
```

### Virtual Scrolling for Large Lists
```javascript
import { FixedSizeList as List } from "react-window";
import { DataTableRow, DataTableItem } from "@/components/Component";

const VirtualizedList = ({ items, height = 400 }) => {
  const Row = ({ index, style }) => {
    const item = items[index];
    
    return (
      <div style={style}>
        <DataTableRow>
          <DataTableItem>{item.name}</DataTableItem>
          <DataTableItem>{item.email}</DataTableItem>
          <DataTableItem>{item.status}</DataTableItem>
        </DataTableRow>
      </div>
    );
  };

  return (
    <div className="card card-bordered">
      <List
        height={height}
        itemCount={items.length}
        itemSize={60}
        width="100%"
      >
        {Row}
      </List>
    </div>
  );
};
```

## Advanced Component Patterns

### Compound Components Pattern
```javascript
import { createContext, useContext } from "react";

const ModalContext = createContext();

const Modal = ({ children, isOpen, toggle }) => {
  return (
    <ModalContext.Provider value={{ isOpen, toggle }}>
      <div className={`modal ${isOpen ? 'show' : ''}`}>
        <div className="modal-dialog modal-dialog-centered">
          <div className="modal-content">
            {children}
          </div>
        </div>
      </div>
    </ModalContext.Provider>
  );
};

const ModalHeader = ({ children }) => {
  const { toggle } = useContext(ModalContext);
  
  return (
    <div className="modal-header">
      <h4 className="modal-title">{children}</h4>
      <button type="button" className="btn-close" onClick={toggle} />
    </div>
  );
};

const ModalBody = ({ children }) => (
  <div className="modal-body">{children}</div>
);

const ModalFooter = ({ children }) => (
  <div className="modal-footer">{children}</div>
);

// Usage
const UserModal = () => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <Modal isOpen={isOpen} toggle={() => setIsOpen(!isOpen)}>
      <ModalHeader>Add User</ModalHeader>
      <ModalBody>
        {/* Form content */}
      </ModalBody>
      <ModalFooter>
        <Button color="primary">Save</Button>
        <Button onClick={() => setIsOpen(false)}>Cancel</Button>
      </ModalFooter>
    </Modal>
  );
};

// Export compound component
Modal.Header = ModalHeader;
Modal.Body = ModalBody;
Modal.Footer = ModalFooter;
export default Modal;
```

### Render Props Pattern
```javascript
const DataProvider = ({ children, endpoint }) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(endpoint);
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [endpoint]);

  return children({ data, loading, error });
};

// Usage
const UsersList = () => {
  return (
    <DataProvider endpoint="/api/users">
      {({ data, loading, error }) => {
        if (loading) return <Spinner />;
        if (error) return <Alert color="danger">{error}</Alert>;
        
        return (
          <div>
            <Button onClick={refetch} className="mb-3">
              Refresh
            </Button>
            <DataTable>
              {data.map(user => (
                <DataTableRow key={user.id}>
                  <DataTableItem>{user.name}</DataTableItem>
                  <DataTableItem>{user.email}</DataTableItem>
                </DataTableRow>
              ))}
            </DataTable>
          </div>
        );
      }}
    </DataProvider>
  );
};
```

## Chart and Visualization Patterns

### Chart.js Integration with DashLite Styling
```javascript
import { Line, Bar, Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement, BarElement } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement, BarElement);

const DashboardCharts = ({ data }) => {
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          boxWidth: 12,
          padding: 20,
          font: {
            size: 13
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        }
      },
      y: {
        grid: {
          borderDash: [3, 3],
          color: '#e5e9f2'
        }
      }
    }
  };

  return (
    <div className="row g-gs">
      <div className="col-lg-8">
        <div className="card card-bordered h-100">
          <div className="card-inner">
            <div className="card-title-group">
              <div className="card-title">
                <h6 className="title">Sales Overview</h6>
              </div>
              <div className="card-tools">
                <div className="dropdown">
                  <Button 
                    className="btn-outline-light btn-white btn-dim btn-sm dropdown-toggle"
                    data-bs-toggle="dropdown"
                  >
                    Last 30 Days
                  </Button>
                </div>
              </div>
            </div>
            <div className="nk-chart-canvas" style={{ height: '300px' }}>
              <Line data={data.lineChart} options={chartOptions} />
            </div>
          </div>
        </div>
      </div>
      
      <div className="col-lg-4">
        <div className="card card-bordered h-100">
          <div className="card-inner">
            <div className="card-title-group">
              <div className="card-title">
                <h6 className="title">Traffic Sources</h6>
              </div>
            </div>
            <div className="nk-chart-canvas" style={{ height: '250px' }}>
              <Doughnut data={data.doughnutChart} options={chartOptions} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
```

## File Upload and Media Handling

### Advanced File Upload Component
```javascript
import { useDropzone } from "react-dropzone";
import { useState } from "react";
import { toast } from "react-toastify";

const FileUpload = ({ onUpload, accept = "image/*", maxSize = 5242880 }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif']
    },
    maxSize,
    onDrop: async (acceptedFiles, rejectedFiles) => {
      if (rejectedFiles.length > 0) {
        toast.error("Some files were rejected. Check file type and size.");
        return;
      }

      setUploading(true);
      try {
        const uploadPromises = acceptedFiles.map(file => {
          const formData = new FormData();
          formData.append('file', file);
          return onUpload(formData);
        });

        const results = await Promise.all(uploadPromises);
        setUploadedFiles(prev => [...prev, ...results]);
        toast.success("Files uploaded successfully!");
      } catch (error) {
        toast.error("Upload failed. Please try again.");
      } finally {
        setUploading(false);
      }
    }
  });

  return (
    <div className="card card-bordered">
      <div className="card-inner">
        <div 
          {...getRootProps()} 
          className={`dropzone ${isDragActive ? 'dropzone-active' : ''}`}
          style={{
            border: '2px dashed #e5e9f2',
            borderRadius: '6px',
            padding: '40px',
            textAlign: 'center',
            cursor: 'pointer'
          }}
        >
          <input {...getInputProps()} />
          <div className="dz-message">
            <span className="dz-message-text">
              {isDragActive ? (
                <p>Drop the files here...</p>
              ) : (
                <>
                  <p>Drag & drop files here, or click to select</p>
                  <span className="dz-message-or">or</span>
                  <Button color="primary" disabled={uploading}>
                    {uploading ? "Uploading..." : "Browse Files"}
                  </Button>
                </>
              )}
            </span>
          </div>
        </div>
        
        {uploadedFiles.length > 0 && (
          <div className="mt-3">
            <h6>Uploaded Files:</h6>
            <ul className="list-group">
              {uploadedFiles.map((file, index) => (
                <li key={index} className="list-group-item d-flex justify-content-between">
                  <span>{file.name}</span>
                  <Badge color="success">Uploaded</Badge>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};
```

## Best Practices

### Styling Guidelines
- Use DashLite's class naming conventions consistently
- Combine Bootstrap utilities with Tailwind for enhanced styling
- Maintain consistent spacing using DashLite's spacing system
- Use semantic class names for better maintainability

### Performance Optimization
- Implement code splitting for large components
- Use React.memo() for expensive components
- Optimize re-renders with useCallback and useMemo
- Implement virtual scrolling for large datasets
- Use proper caching strategies

### Component Architecture
- Follow compound component patterns for complex UI
- Use render props for data sharing
- Implement proper error boundaries
- Create reusable hooks for common functionality
- Maintain consistent prop interfaces

### Development Workflow
- Use TypeScript for better type safety
- Implement proper error handling
- Create comprehensive test suites
- Use Storybook for component documentation
- Follow accessibility guidelines (WCAG)
description:
globs:
alwaysApply: false
---

---

## Source: api/.cursor/rules/fastapi-framework.mdc

# FastAPI Framework Guide - CraftyXhub API

This project uses FastAPI with async/await patterns, SQLAlchemy 2.0, and PostgreSQL. Follow these conventions and patterns when developing the API.

## Project Structure

The FastAPI application follows a clean architecture pattern:

- **main.py**: Application entry point and configuration from [main.py](mdc:api/main.py)
- **routers/**: API endpoints organized by version (v1) and domain
- **models/**: SQLAlchemy ORM models for database tables
- **schemas/**: Pydantic models for request/response validation
- **services/**: Business logic layer separated by domain
- **core/**: Configuration, settings, and utilities from [config.py](mdc:api/core/config.py)
- **database/**: Database connection and session management
- **utils/**: Shared utility functions

## FastAPI Application Configuration

### Application Factory Pattern
```python
from fastapi import FastAPI
from routers.v1 import router as v1_router

def create_application() -> FastAPI:
    app = FastAPI(
        title="CraftyXhub API",
        description="CraftyXhub Content Management API", 
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        contact={
            "name": "CraftyXhub Support",
            "email": "support@craftyhub.com",
        }
    )
    
    include_routers(app)
    return app

app = create_application()
```

### Router Organization
Use versioned routers as shown in [v1/__init__.py](mdc:api/routers/v1/__init__.py):
```python
from fastapi import APIRouter

router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(profile_router) 
router.include_router(post_router)
```

## Key Dependencies & Stack

### Core Framework (from [requirements.txt](mdc:api/requirements.txt))
- **FastAPI 0.116.0**: Modern async web framework
- **Uvicorn 0.35.0**: ASGI server for development and production
- **Pydantic 2.11.7**: Data validation and serialization
- **SQLAlchemy 2.0.41**: Async ORM with modern patterns
- **AsyncPG 0.30.0**: Async PostgreSQL driver
- **Alembic 1.16.3**: Database migrations

### Authentication & Security
- **PyJWT 2.10.1**: JWT token handling
- **Passlib[bcrypt] 1.7.4**: Password hashing
- **Python-JOSE 3.3.0**: JWT signing and verification
- **Python-multipart**: File upload support

### Development & Testing
- **Pytest 8.3.3**: Testing framework
- **Pytest-asyncio 0.23.8**: Async test support
- **HTTPx 0.27.2**: Async HTTP client for testing

## Database Patterns

### SQLAlchemy 2.0 Async Pattern
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def get_user_by_id(session: AsyncSession, user_id: int) -> User:
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()
```

### Base Model Pattern
Use the base table from [models/base.py](mdc:api/models/base.py):
```python
class BaseTable(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Many-to-Many Relationships
```python
post_tags = Table(
    'post_tags', Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)
```

## Pydantic Schema Patterns

### Base Schema Configuration
Use the base schema from [schemas/base.py](mdc:api/schemas/base.py):
```python
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True  # SQLAlchemy 2.0 compatibility
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime] = None
```

### Enum Patterns
```python
class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published" 
    ARCHIVED = "archived"
```

## Router & Endpoint Patterns

### Router Structure
```python
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from database.connection import get_db_session
from services.domain.service import DomainService
from schemas.domain import CreateSchema, UpdateSchema, ResponseSchema
from models.domain import DomainModel

router = APIRouter(prefix="/domain", tags=["domain"])

@router.post("/", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: CreateSchema,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new item with comprehensive error handling."""
    try:
        result = await DomainService.create(session, item_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

## Service Layer Pattern

### Business Logic Separation
```python
class AuthService:
    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
        result = await session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
```

## Configuration Management

### Environment-based Settings
Use the pattern from [core/config.py](mdc:api/core/config.py):
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    database_username: str = os.getenv("DB_USER", "postgres")
    database_password: str = os.getenv("DB_PASSWORD", "root")
    
    DATABASE_URL = f'postgresql+asyncpg://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}'

settings = Settings()
```

## Error Handling

### HTTP Exception Patterns
```python
from fastapi import HTTPException, status

# Bad Request
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Email already registered"
)

# Unauthorized
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
    headers={"WWW-Authenticate": "Bearer"}
)

# Not Found
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found"
)
```

## API Versioning

### Version Prefix Pattern
```python
# v1 router
router = APIRouter(prefix="/v1")

# Main app includes versioned routers
app.include_router(v1_router)
```

## Health Check & Monitoring

### Health Endpoint Pattern
```python
@app.get("/health", tags=["Health"])
async def health_check():
    db_healthy = await db_health_check()
    return {
        "status": "Healthy" if db_healthy else "unhealthy",
        "version": "1.0.0",
        "environment": "development",
        "database": "connected" if db_healthy else "disconnected"
    }
```

## Development Best Practices

### Async/Await Patterns
- Always use `async def` for route handlers
- Use `await` with database operations
- Leverage AsyncSession for database interactions
- Use async context managers where appropriate

### Type Hints
- Use comprehensive type hints for all functions
- Leverage Pydantic models for request/response validation
- Use Optional[] for nullable fields
- Import from typing for complex types

### Database Sessions
- Always use dependency injection for database sessions
- Never commit transactions in route handlers - delegate to services
- Use try/except blocks for database operations
- Always close sessions properly (handled by FastAPI dependencies)

### Security
- Use JWT tokens for authentication
- Hash passwords with bcrypt
- Validate all input data with Pydantic
- Use dependency injection for authentication
- Implement proper CORS settings
- Use environment variables for sensitive data

### Testing
- Use pytest with async support
- Create test database fixtures
- Test both success and error cases
- Use HTTPx for async API testing
description:
globs:
alwaysApply: false
---

---

## Source: api/.cursor/rules/fastapi-models-schemas.mdc

# FastAPI SQLAlchemy Models and Pydantic Schemas Patterns

## SQLAlchemy Model Patterns

### Base Model Structure
Always inherit from the base table pattern in [models/base.py](mdc:api/models/base.py):

```python
import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import BaseTable

class DomainModel(BaseTable):
    __tablename__ = "domain_items"
    
    # Inherited from BaseTable:
    # id = Column(Integer, primary_key=True, autoincrement=True)
    # uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    # created_at = Column(DateTime(timezone=True), server_default=func.now())
    # updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Domain-specific fields
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="items")
    category = relationship("Category", back_populates="items")
```

### Common Column Types and Patterns

#### String Fields
```python
# Short text with length limit
name = Column(String(100), nullable=False, index=True)

# Email with unique constraint
email = Column(String(255), unique=True, nullable=False, index=True)

# Optional text field
description = Column(Text, nullable=True)

# Enum field
from sqlalchemy import Enum
status = Column(Enum("draft", "published", "archived", name="post_status"), 
                default="draft", nullable=False)
```

#### Numeric Fields
```python
# Auto-incrementing primary key (inherited from BaseTable)
id = Column(Integer, primary_key=True, autoincrement=True)

# Foreign key
user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

# Decimal for prices
from sqlalchemy import Numeric
price = Column(Numeric(10, 2), nullable=True)

# Float for ratings
rating = Column(Float, default=0.0)
```

#### Boolean and Datetime Fields
```python
# Boolean with default
is_published = Column(Boolean, default=False, nullable=False)
is_featured = Column(Boolean, default=False)

# Timestamps (inherited from BaseTable)
created_at = Column(DateTime(timezone=True), server_default=func.now())
updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Custom datetime field
published_at = Column(DateTime(timezone=True), nullable=True)
```

### Relationship Patterns

#### One-to-Many Relationships
```python
# Parent model (One side)
class User(BaseTable):
    __tablename__ = "users"
    
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")

# Child model (Many side)
class Post(BaseTable):
    __tablename__ = "posts"
    
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="posts")
```

#### Many-to-Many Relationships
```python
# Association table (defined in base.py or relevant model file)
post_tags = Table(
    'post_tags', BaseTable.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

# Models with many-to-many relationship
class Post(BaseTable):
    __tablename__ = "posts"
    
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")

class Tag(BaseTable):
    __tablename__ = "tags"
    
    posts = relationship("Post", secondary=post_tags, back_populates="tags")
```

#### Self-Referential Relationships
```python
class Comment(BaseTable):
    __tablename__ = "comments"
    
    content = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    
    # Self-referential relationship
    parent = relationship("Comment", remote_side="Comment.id", back_populates="replies")
    replies = relationship("Comment", back_populates="parent", cascade="all, delete-orphan")
```

### Index and Constraint Patterns

#### Database Indexes
```python
class Post(BaseTable):
    __tablename__ = "posts"
    
    title = Column(String(255), nullable=False, index=True)  # Single column index
    slug = Column(String(255), unique=True, nullable=False)  # Unique constraint
    author_id = Column(Integer, ForeignKey("users.id"), index=True)  # FK index
    
    # Composite index
    __table_args__ = (
        Index('ix_post_author_status', 'author_id', 'status'),
        Index('ix_post_created_status', 'created_at', 'status'),
    )
```

## Pydantic Schema Patterns

### Base Schema Configuration
Always use the base schema from [schemas/base.py](mdc:api/schemas/base.py):

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from schemas.base import BaseSchema, TimestampMixin

class DomainBase(BaseSchema):
    """Base schema with common configuration."""
    title: str = Field(..., min_length=1, max_length=255, description="Item title")
    description: Optional[str] = Field(None, description="Item description")
    is_active: bool = Field(default=True, description="Whether item is active")
```

### CRUD Schema Patterns

#### Create Schemas (Input)
```python
class PostCreate(BaseModel):
    """Schema for creating new posts."""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    is_published: bool = Field(default=False)
    category_id: Optional[int] = Field(None, gt=0)
    tags: List[str] = Field(default=[], max_items=10)
    
    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty or only whitespace')
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v):
        return [tag.strip().lower() for tag in v if tag.strip()]
```

#### Update Schemas (Partial Input)
```python
class PostUpdate(BaseModel):
    """Schema for updating existing posts."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    is_published: Optional[bool] = None
    category_id: Optional[int] = Field(None, gt=0)
    tags: Optional[List[str]] = Field(None, max_items=10)
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty or only whitespace')
        return v.strip() if v else v
```

#### Response Schemas (Output)
```python
class PostResponse(BaseSchema, TimestampMixin):
    """Schema for post responses."""
    id: int
    uuid: str
    title: str
    content: str
    excerpt: Optional[str]
    is_published: bool
    slug: str
    
    # Nested relationships
    author: "UserResponse"
    category: Optional["CategoryResponse"]
    tags: List["TagResponse"]
    
    # Computed fields
    @validator('excerpt', pre=True, always=True)
    def generate_excerpt(cls, v, values):
        if v:
            return v
        content = values.get('content', '')
        return content[:200] + '...' if len(content) > 200 else content

# Enable forward references
PostResponse.model_rebuild()
```

### Validation Patterns

#### Custom Validators
```python
from pydantic import validator, root_validator
import re

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Za-z]', v) or not re.search(r'\d', v):
            raise ValueError('Password must contain both letters and numbers')
        return v
    
    @root_validator
    def validate_passwords_match(cls, values):
        password = values.get('password')
        confirm_password = values.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValueError('Passwords do not match')
        return values
```

#### Field Validation with Dependencies
```python
class PostCreate(BaseModel):
    title: str
    content: str
    is_published: bool = False
    publish_date: Optional[datetime] = None
    
    @root_validator
    def validate_publish_date(cls, values):
        is_published = values.get('is_published')
        publish_date = values.get('publish_date')
        
        if is_published and not publish_date:
            values['publish_date'] = datetime.utcnow()
        elif not is_published:
            values['publish_date'] = None
            
        return values
```

### Nested Schema Patterns

#### Simple Nested Schemas
```python
class CategoryResponse(BaseSchema):
    id: int
    name: str
    slug: str

class PostResponse(BaseSchema, TimestampMixin):
    id: int
    title: str
    category: Optional[CategoryResponse]  # Nested schema
```

#### Complex Nested with Lists
```python
class PostWithComments(PostResponse):
    comments: List["CommentResponse"] = []
    
    class Config:
        # Limit depth to prevent infinite recursion
        max_anystr_length = 1000

class CommentResponse(BaseSchema, TimestampMixin):
    id: int
    content: str
    author: "UserResponse"
    replies: List["CommentResponse"] = []

# Enable forward references
PostWithComments.model_rebuild()
CommentResponse.model_rebuild()
```

### Enum Schema Patterns

#### Using Enums from Base
```python
from schemas.base import PostStatus, CommentStatus

class PostCreate(BaseModel):
    title: str
    content: str
    status: PostStatus = PostStatus.DRAFT

class CommentCreate(BaseModel):
    content: str
    post_id: int
    status: CommentStatus = CommentStatus.PENDING
```

### Response Model Patterns

#### Pagination Response
```python
from typing import Generic, TypeVar

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int
    
    @validator('pages', pre=True, always=True)
    def calculate_pages(cls, v, values):
        total = values.get('total', 0)
        per_page = values.get('per_page', 20)
        return (total + per_page - 1) // per_page if per_page > 0 else 0

# Usage
PaginatedPostResponse = PaginatedResponse[PostResponse]
```

#### API Response Wrapper
```python
class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None
    errors: Optional[List[str]] = None

# Usage
@router.get("/posts/{post_id}")
async def get_post(post_id: int) -> APIResponse[PostResponse]:
    pass
```

## Best Practices

### Model Design
- Always inherit from BaseTable for consistent timestamps and UUIDs
- Use appropriate column types and constraints
- Add indexes for frequently queried fields
- Use relationships instead of manual joins
- Implement proper cascade behavior for relationships

### Schema Design
- Separate Create, Update, and Response schemas
- Use comprehensive validation with custom validators
- Include helpful field descriptions
- Implement proper nested schema handling
- Use enums for constrained string values

### Performance Considerations
- Add database indexes for query performance
- Use lazy loading for relationships when appropriate
- Implement pagination for list endpoints
- Use select_related/joinedload for eager loading
- Consider caching for frequently accessed data

### Security
- Never expose password fields in response schemas
- Validate all input data thoroughly
- Use proper field constraints and limits
- Sanitize user input to prevent injection attacks
- Implement proper authorization checks in services
description:
globs:
alwaysApply: false
---

---

## Source: api/.cursor/rules/fastapi-routers.mdc

# FastAPI Router and Endpoint Development Patterns

## Router Structure Template

Every FastAPI router should follow this pattern based on [auth.py](mdc:api/routers/v1/auth.py):

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from database.connection import get_db_session
from services.domain.service import DomainService
from schemas.domain import CreateSchema, UpdateSchema, ResponseSchema
from models.domain import DomainModel

router = APIRouter(prefix="/domain", tags=["domain"])

@router.post("/", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: CreateSchema,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new item with comprehensive error handling."""
    try:
        result = await DomainService.create(session, item_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

## Endpoint Patterns

### CRUD Operations Template

#### Create (POST)
```python
@router.post("/", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: CreateSchema,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)  # If authentication required
):
    """
    Create a new item.
    
    - **item_data**: Item creation data
    - **Returns**: Created item with ID and timestamps
    """
    # Validation
    existing_item = await DomainService.get_by_unique_field(session, item_data.unique_field)
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item with this field already exists"
        )
    
    # Business logic
    result = await DomainService.create(session, item_data, current_user.id)
    return result
```

#### Read (GET) - List with Pagination
```python
@router.get("/", response_model=List[ResponseSchema])
async def get_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of items to return"),
    search: Optional[str] = Query(None, description="Search term"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Retrieve items with pagination and filtering.
    
    - **skip**: Number of items to skip for pagination
    - **limit**: Maximum number of items to return (1-100)
    - **search**: Optional search term
    - **status_filter**: Optional status filter
    """
    items = await DomainService.get_many(
        session, 
        skip=skip, 
        limit=limit, 
        search=search,
        status_filter=status_filter
    )
    return items
```

#### Read (GET) - Single Item
```python
@router.get("/{item_id}", response_model=ResponseSchema)
async def get_item(
    item_id: int = Path(..., gt=0, description="Item ID"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Retrieve a single item by ID.
    
    - **item_id**: Unique identifier for the item
    """
    item = await DomainService.get_by_id(session, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return item
```

#### Update (PUT/PATCH)
```python
@router.put("/{item_id}", response_model=ResponseSchema)
async def update_item(
    item_id: int = Path(..., gt=0),
    item_data: UpdateSchema = Body(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing item.
    
    - **item_id**: Unique identifier for the item
    - **item_data**: Updated item data
    """
    # Check existence
    existing_item = await DomainService.get_by_id(session, item_id)
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Authorization check
    if existing_item.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this item"
        )
    
    # Update
    updated_item = await DomainService.update(session, item_id, item_data)
    return updated_item
```

#### Delete (DELETE)
```python
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int = Path(..., gt=0),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an item.
    
    - **item_id**: Unique identifier for the item
    """
    existing_item = await DomainService.get_by_id(session, item_id)
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Authorization
    if existing_item.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this item"
        )
    
    await DomainService.delete(session, item_id)
```

## Authentication Patterns

### Public Endpoints
```python
@router.get("/public")
async def public_endpoint(session: AsyncSession = Depends(get_db_session)):
    """Public endpoint that doesn't require authentication."""
    pass
```

### Protected Endpoints
```python
@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Protected endpoint requiring valid JWT token."""
    pass
```

### Admin-Only Endpoints
```python
@router.get("/admin")
async def admin_endpoint(
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Admin-only endpoint requiring admin privileges."""
    pass
```

## Request Validation Patterns

### Query Parameters
```python
@router.get("/search")
async def search_items(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    category: Optional[str] = Query(None, regex="^[a-zA-Z0-9_-]+$"),
    sort_by: str = Query("created_at", regex="^(created_at|updated_at|name)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page")
):
    pass
```

### Path Parameters
```python
@router.get("/users/{user_id}/posts/{post_id}")
async def get_user_post(
    user_id: int = Path(..., gt=0, description="User ID"),
    post_id: int = Path(..., gt=0, description="Post ID"),
    session: AsyncSession = Depends(get_db_session)
):
    pass
```

### Request Body with Validation
```python
from pydantic import Field

class CreatePostRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tags: List[str] = Field(default=[], max_items=10)
    is_published: bool = Field(default=False)

@router.post("/posts")
async def create_post(
    post_data: CreatePostRequest,
    session: AsyncSession = Depends(get_db_session)
):
    pass
```

## Error Handling Patterns

### Standard HTTP Exceptions
```python
# 400 - Bad Request
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid input data"
)

# 401 - Unauthorized
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authentication required",
    headers={"WWW-Authenticate": "Bearer"}
)

# 403 - Forbidden
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Insufficient permissions"
)

# 404 - Not Found
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found"
)

# 409 - Conflict
raise HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Resource already exists"
)

# 422 - Unprocessable Entity (automatic from Pydantic validation)
# 500 - Internal Server Error (automatic from unhandled exceptions)
```

### Custom Exception Details
```python
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_file_type",
                "message": "Only JPEG and PNG files are allowed",
                "allowed_types": ["image/jpeg", "image/png"]
            }
        )
```

## Response Patterns

### Standard Success Responses
```python
# 200 - OK (default for GET, PUT, PATCH)
return {"data": result}

# 201 - Created (POST)
@router.post("/", status_code=status.HTTP_201_CREATED)

# 204 - No Content (DELETE)
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
```

### Pagination Response
```python
@router.get("/items")
async def get_items(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    items, total = await DomainService.get_paginated(page, per_page)
    
    return {
        "items": items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }
```

## File Upload Patterns

### Single File Upload
```python
from fastapi import File, UploadFile

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(..., description="File to upload"),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    # Validate file
    if file.size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large"
        )
    
    # Save file
    file_path = await FileService.save_upload(file, current_user.id)
    return {"file_path": file_path}
```

### Multiple File Upload
```python
@router.post("/upload-multiple")
async def upload_files(
    files: List[UploadFile] = File(..., description="Files to upload"),
    current_user: User = Depends(get_current_active_user)
):
    if len(files) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 files allowed"
        )
    
    file_paths = []
    for file in files:
        path = await FileService.save_upload(file, current_user.id)
        file_paths.append(path)
    
    return {"file_paths": file_paths}
```

## Best Practices

### Documentation
- Always include comprehensive docstrings
- Use Pydantic Field descriptions
- Add example values in schema definitions
- Document all possible error responses

### Performance
- Use async/await consistently
- Implement proper pagination for list endpoints
- Use database indexing for frequently queried fields
- Cache frequently accessed data

### Security
- Validate all input parameters
- Use dependency injection for authentication
- Implement proper authorization checks
- Sanitize file uploads
- Use HTTPS in production

### Error Messages
- Provide clear, actionable error messages
- Include error codes for programmatic handling
- Don't expose internal system details
- Use consistent error response format
description:
globs:
alwaysApply: false
---

---

## Source: api/.cursor/rules/fastapi-services-testing.mdc

# FastAPI Services Layer, Testing, and Advanced Patterns

## Service Layer Architecture

### Service Class Structure
Follow the existing pattern from your auth service for all business logic:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import Optional, List
from models.domain import DomainModel
from schemas.domain import DomainCreate, DomainUpdate

class DomainService:
    """Service class for domain-specific business logic."""
    
    @staticmethod
    async def create(session: AsyncSession, data: DomainCreate, user_id: int) -> DomainModel:
        """Create a new domain item."""
        db_item = DomainModel(
            **data.dict(),
            owner_id=user_id
        )
        session.add(db_item)
        await session.commit()
        await session.refresh(db_item)
        return db_item
    
    @staticmethod
    async def get_by_id(session: AsyncSession, item_id: int) -> Optional[DomainModel]:
        """Get domain item by ID with relationships."""
        result = await session.execute(
            select(DomainModel)
            .options(selectinload(DomainModel.owner))
            .where(DomainModel.id == item_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_many(
        session: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        owner_id: Optional[int] = None
    ) -> List[DomainModel]:
        """Get multiple domain items with filtering."""
        query = select(DomainModel).options(selectinload(DomainModel.owner))
        
        # Apply filters
        if search:
            query = query.where(DomainModel.title.ilike(f"%{search}%"))
        if owner_id:
            query = query.where(DomainModel.owner_id == owner_id)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update(session: AsyncSession, item_id: int, data: DomainUpdate) -> Optional[DomainModel]:
        """Update domain item."""
        update_data = data.dict(exclude_unset=True)
        if not update_data:
            return await DomainService.get_by_id(session, item_id)
        
        await session.execute(
            update(DomainModel)
            .where(DomainModel.id == item_id)
            .values(**update_data)
        )
        await session.commit()
        return await DomainService.get_by_id(session, item_id)
    
    @staticmethod
    async def delete(session: AsyncSession, item_id: int) -> bool:
        """Delete domain item."""
        result = await session.execute(
            delete(DomainModel).where(DomainModel.id == item_id)
        )
        await session.commit()
        return result.rowcount > 0
```

### Advanced Query Patterns

#### Complex Filtering Service
```python
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta

class PostService:
    @staticmethod
    async def search_posts(
        session: AsyncSession,
        query: Optional[str] = None,
        category_ids: Optional[List[int]] = None,
        tags: Optional[List[str]] = None,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        author_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Post], int]:
        """Advanced search with multiple filters."""
        
        # Base query
        base_query = select(Post).options(
            selectinload(Post.author),
            selectinload(Post.category),
            selectinload(Post.tags)
        )
        
        # Count query for pagination
        count_query = select(func.count(Post.id))
        
        # Build filters
        filters = []
        
        if query:
            search_filter = or_(
                Post.title.ilike(f"%{query}%"),
                Post.content.ilike(f"%{query}%")
            )
            filters.append(search_filter)
        
        if category_ids:
            filters.append(Post.category_id.in_(category_ids))
        
        if status:
            filters.append(Post.status == status)
        
        if date_from:
            filters.append(Post.created_at >= date_from)
        
        if date_to:
            filters.append(Post.created_at <= date_to)
        
        if author_id:
            filters.append(Post.author_id == author_id)
        
        # Apply filters to both queries
        if filters:
            combined_filter = and_(*filters)
            base_query = base_query.where(combined_filter)
            count_query = count_query.where(combined_filter)
        
        # Execute count query
        count_result = await session.execute(count_query)
        total = count_result.scalar()
        
        # Execute main query with pagination
        main_query = base_query.offset(skip).limit(limit).order_by(Post.created_at.desc())
        result = await session.execute(main_query)
        items = result.scalars().all()
        
        return items, total
```

#### Aggregation Service
```python
class AnalyticsService:
    @staticmethod
    async def get_post_statistics(session: AsyncSession, author_id: Optional[int] = None):
        """Get post statistics with aggregations."""
        base_query = select(
            func.count(Post.id).label('total_posts'),
            func.count(Post.id).filter(Post.status == 'published').label('published_posts'),
            func.count(Post.id).filter(Post.status == 'draft').label('draft_posts'),
            func.avg(func.length(Post.content)).label('avg_content_length'),
            func.max(Post.created_at).label('latest_post_date')
        )
        
        if author_id:
            base_query = base_query.where(Post.author_id == author_id)
        
        result = await session.execute(base_query)
        return result.first()
```

### Error Handling in Services

#### Custom Service Exceptions
```python
class ServiceException(Exception):
    """Base exception for service layer."""
    pass

class NotFoundError(ServiceException):
    """Resource not found exception."""
    pass

class ValidationError(ServiceException):
    """Business logic validation error."""
    pass

class PermissionError(ServiceException):
    """Permission denied exception."""
    pass

# Usage in service
class PostService:
    @staticmethod
    async def publish_post(session: AsyncSession, post_id: int, user_id: int) -> Post:
        """Publish a post with business logic validation."""
        post = await PostService.get_by_id(session, post_id)
        if not post:
            raise NotFoundError(f"Post with ID {post_id} not found")
        
        if post.author_id != user_id:
            raise PermissionError("Only the author can publish their posts")
        
        if not post.content or len(post.content.strip()) < 100:
            raise ValidationError("Post content must be at least 100 characters to publish")
        
        post.status = "published"
        post.published_at = datetime.utcnow()
        await session.commit()
        return post
```

## Testing Patterns

### Test Configuration
```python
# conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.connection import get_db_session
from main import app
from core.config import settings

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@localhost/test_db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
async def test_session(test_engine):
    """Create test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture(scope="function")
async def client(test_session):
    """Create test client with dependency override."""
    async def override_get_db():
        yield test_session
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()
```

### Service Layer Testing
```python
# test_post_service.py
import pytest
from services.post.post import PostService
from schemas.post import PostCreate, PostUpdate
from models.user import User
from models.post import Post

class TestPostService:
    @pytest.mark.asyncio
    async def test_create_post(self, test_session, sample_user):
        """Test post creation."""
        post_data = PostCreate(
            title="Test Post",
            content="This is a test post content.",
            is_published=False
        )
        
        post = await PostService.create(test_session, post_data, sample_user.id)
        
        assert post.id is not None
        assert post.title == "Test Post"
        assert post.author_id == sample_user.id
        assert post.is_published is False
    
    @pytest.mark.asyncio
    async def test_get_post_by_id(self, test_session, sample_post):
        """Test getting post by ID."""
        post = await PostService.get_by_id(test_session, sample_post.id)
        
        assert post is not None
        assert post.id == sample_post.id
        assert post.title == sample_post.title
    
    @pytest.mark.asyncio
    async def test_get_post_not_found(self, test_session):
        """Test getting non-existent post."""
        post = await PostService.get_by_id(test_session, 99999)
        assert post is None
    
    @pytest.mark.asyncio
    async def test_update_post(self, test_session, sample_post):
        """Test post update."""
        update_data = PostUpdate(title="Updated Title")
        
        updated_post = await PostService.update(test_session, sample_post.id, update_data)
        
        assert updated_post.title == "Updated Title"
        assert updated_post.content == sample_post.content  # Unchanged
    
    @pytest.mark.asyncio
    async def test_search_posts_with_filters(self, test_session, sample_posts):
        """Test searching posts with filters."""
        posts, total = await PostService.search_posts(
            test_session,
            query="test",
            status="published",
            skip=0,
            limit=10
        )
        
        assert isinstance(posts, list)
        assert total >= 0
        for post in posts:
            assert "test" in post.title.lower() or "test" in post.content.lower()
            assert post.status == "published"

# Fixtures
@pytest.fixture
async def sample_user(test_session):
    """Create a sample user for testing."""
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        password="hashed_password"
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user

@pytest.fixture
async def sample_post(test_session, sample_user):
    """Create a sample post for testing."""
    post = Post(
        title="Sample Post",
        content="This is sample content.",
        author_id=sample_user.id,
        status="draft"
    )
    test_session.add(post)
    await test_session.commit()
    await test_session.refresh(post)
    return post
```

### API Endpoint Testing
```python
# test_post_endpoints.py
import pytest
from httpx import AsyncClient

class TestPostEndpoints:
    @pytest.mark.asyncio
    async def test_create_post(self, client: AsyncClient, auth_headers):
        """Test POST /v1/posts endpoint."""
        post_data = {
            "title": "New Post",
            "content": "This is new post content.",
            "is_published": False
        }
        
        response = await client.post(
            "/v1/posts",
            json=post_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Post"
        assert data["is_published"] is False
        assert "id" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_get_posts_pagination(self, client: AsyncClient):
        """Test GET /v1/posts with pagination."""
        response = await client.get("/v1/posts?skip=0&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
    
    @pytest.mark.asyncio
    async def test_get_post_by_id(self, client: AsyncClient, sample_post):
        """Test GET /v1/posts/{id} endpoint."""
        response = await client.get(f"/v1/posts/{sample_post.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_post.id
        assert data["title"] == sample_post.title
    
    @pytest.mark.asyncio
    async def test_get_post_not_found(self, client: AsyncClient):
        """Test 404 for non-existent post."""
        response = await client.get("/v1/posts/99999")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_post_unauthorized(self, client: AsyncClient, sample_post):
        """Test updating post without authentication."""
        update_data = {"title": "Updated Title"}
        
        response = await client.put(
            f"/v1/posts/{sample_post.id}",
            json=update_data
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_delete_post(self, client: AsyncClient, sample_post, auth_headers):
        """Test DELETE /v1/posts/{id} endpoint."""
        response = await client.delete(
            f"/v1/posts/{sample_post.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify post is deleted
        get_response = await client.get(f"/v1/posts/{sample_post.id}")
        assert get_response.status_code == 404

@pytest.fixture
async def auth_headers(client: AsyncClient, sample_user):
    """Create authentication headers for testing."""
    login_data = {
        "username": sample_user.email,
        "password": "testpassword"
    }
    
    response = await client.post("/v1/auth/login", data=login_data)
    token_data = response.json()
    
    return {"Authorization": f"Bearer {token_data['access_token']}"}
```

## Advanced Patterns

### Background Tasks
```python
from fastapi import BackgroundTasks
from services.email.email_service import EmailService
from services.notification.notification_service import NotificationService

class PostService:
    @staticmethod
    async def publish_post_with_notifications(
        session: AsyncSession, 
        post_id: int, 
        user_id: int,
        background_tasks: BackgroundTasks
    ) -> Post:
        """Publish post and trigger background tasks."""
        post = await PostService.publish_post(session, post_id, user_id)
        
        # Add background tasks
        background_tasks.add_task(
            EmailService.send_publication_notification,
            post.author.email,
            post.title
        )
        
        background_tasks.add_task(
            NotificationService.notify_subscribers,
            post.id,
            post.author_id
        )
        
        return post
```

### Caching Patterns
```python
import redis.asyncio as redis
import json
from typing import Optional

class CacheService:
    def __init__(self):
        self.redis = redis.from_url("redis://localhost:6379")
    
    async def get(self, key: str) -> Optional[dict]:
        """Get cached data."""
        cached = await self.redis.get(key)
        return json.loads(cached) if cached else None
    
    async def set(self, key: str, value: dict, expire: int = 3600):
        """Set cached data with expiration."""
        await self.redis.set(key, json.dumps(value), ex=expire)
    
    async def delete(self, key: str):
        """Delete cached data."""
        await self.redis.delete(key)

# Usage in service
class PostService:
    cache = CacheService()
    
    @staticmethod
    async def get_popular_posts(session: AsyncSession, limit: int = 10):
        """Get popular posts with caching."""
        cache_key = f"popular_posts:{limit}"
        
        # Try cache first
        cached_posts = await PostService.cache.get(cache_key)
        if cached_posts:
            return cached_posts
        
        # Query database
        result = await session.execute(
            select(Post)
            .where(Post.status == "published")
            .order_by(Post.view_count.desc())
            .limit(limit)
        )
        posts = result.scalars().all()
        
        # Cache results
        posts_data = [PostResponse.from_orm(post).dict() for post in posts]
        await PostService.cache.set(cache_key, posts_data, expire=1800)  # 30 min
        
        return posts_data
```

### File Upload Service
```python
import aiofiles
import os
from pathlib import Path
from fastapi import UploadFile

class FileService:
    UPLOAD_DIR = Path("uploads")
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx"}
    
    @staticmethod
    async def save_upload(file: UploadFile, user_id: int) -> str:
        """Save uploaded file with validation."""
        # Validate file size
        if file.size > FileService.MAX_FILE_SIZE:
            raise ValidationError("File too large")
        
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in FileService.ALLOWED_EXTENSIONS:
            raise ValidationError(f"File type {file_ext} not allowed")
        
        # Create user directory
        user_dir = FileService.UPLOAD_DIR / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = int(datetime.utcnow().timestamp())
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = user_dir / safe_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return str(file_path)
    
    @staticmethod
    async def delete_file(file_path: str) -> bool:
        """Delete file from filesystem."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
        return False
```

## Best Practices

### Service Organization
- One service class per domain/model
- Use static methods for stateless operations
- Separate read and write operations when beneficial
- Implement proper error handling with custom exceptions
- Use type hints for all method parameters and returns

### Database Operations
- Always use async/await with database operations
- Use selectinload for eager loading relationships
- Implement proper transaction handling
- Use bulk operations for large datasets
- Add proper indexes for query performance

### Testing Strategy
- Test services independently from API endpoints
- Use fixtures for common test data
- Test both success and error scenarios
- Mock external dependencies
- Implement integration tests for critical flows

### Performance Optimization
- Implement caching for frequently accessed data
- Use background tasks for non-critical operations
- Implement proper pagination for large datasets
- Use database connection pooling
- Monitor query performance and optimize slow queries
description:
globs:
alwaysApply: false
---
