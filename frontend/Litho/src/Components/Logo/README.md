# Logo Component

A reusable Logo component for CraftyXhub that replaces all hardcoded logo implementations across the site.

## Features

- **Reusable**: Single component for all logo usage
- **Flexible**: Multiple variants for different contexts
- **Accessible**: Built-in accessibility support
- **Consistent**: Maintains brand consistency across the site
- **Performance**: Memoized for optimal re-rendering

## Usage

### Basic Usage
```jsx
import Logo from '../../Components/Logo'

// Simple logo
<Logo />
```

### With Custom Props
```jsx
// Logo with custom destination
<Logo to="/dashboard" />

// Logo with variant
<Logo variant="white" />

// Logo without Navbar.Brand wrapper
<Logo asNavbarBrand={false} />

// Logo with custom classes
<Logo className="flex items-center" />
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `to` | string | `"/"` | Link destination |
| `variant` | string | `"default"` | Logo style variant |
| `className` | string | `""` | Additional CSS classes |
| `ariaLabel` | string | `"CraftyXhub logo"` | Accessibility label |
| `asNavbarBrand` | boolean | `true` | Wrap in Navbar.Brand |

## Variants

- **`default`**: Blue logo, medium size (text-2xl)
- **`white`**: White logo for dark backgrounds
- **`large`**: Larger logo (text-3xl) for hero sections
- **`small`**: Smaller logo (text-lg) for compact spaces

## Examples

### Header Usage (with Navbar.Brand)
```jsx
<Col className="col-auto me-auto">
  <Logo />
</Col>
```

### Footer Usage (without Navbar.Brand)
```jsx
<Logo 
  asNavbarBrand={false} 
  variant="white"
  className="mb-4" 
/>
```

### Dark Background
```jsx
<Logo variant="white" />
```

### Custom Link
```jsx
<Logo to="/about" ariaLabel="Go to about page" />
```

## Migration from Old Logo

Replace hardcoded logo implementations:

### Before:
```jsx
<Link aria-label="header logo" className="flex items-center" to="/">
  <Navbar.Brand className="inline-block p-0 m-0">
    <span className="text-2xl font-bold text-fastblue tracking-wide">CraftyXhub</span>
  </Navbar.Brand>
</Link>
```

### After:
```jsx
<Logo className="flex items-center" />
```

## Files Updated

✅ **Already Updated:**
- `Pages/Home/Magazine.jsx` - Homepage
- `Pages/User/Dashboard.jsx` - User dashboard  
- `Pages/User/UserPosts.jsx` - User posts page

🔄 **Ready to Update:**
- All other user pages
- Auth pages
- Header components
- Footer components

## Benefits

1. **Maintainability**: Change logo style in one place
2. **Consistency**: Ensures uniform logo appearance
3. **Flexibility**: Easy to create variants for different contexts
4. **Performance**: Memoized component reduces re-renders
5. **Accessibility**: Built-in ARIA labels and semantic markup