import { Breadcrumbs as MuiBreadcrumbs, Typography, Link } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { IconChevronRight, IconHome } from '@tabler/icons-react';

/**
 * Breadcrumb - Navigation breadcrumb component
 * @param {Array} items - Array of { label, to } objects
 */
export default function Breadcrumb({ items = [] }) {
  return (
    <MuiBreadcrumbs
      separator={<IconChevronRight size={14} />}
      sx={{ mb: 3 }}
    >
      <Link
        component={RouterLink}
        to="/"
        color="inherit"
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 0.5,
          textDecoration: 'none',
          '&:hover': { color: 'primary.main' }
        }}
      >
        <IconHome size={16} />
        Home
      </Link>
      
      {items.map((item, index) => {
        const isLast = index === items.length - 1;
        
        return isLast ? (
          <Typography key={item.label} color="text.primary" fontWeight={500}>
            {item.label}
          </Typography>
        ) : (
          <Link
            key={item.label}
            component={RouterLink}
            to={item.to}
            color="inherit"
            sx={{
              textDecoration: 'none',
              '&:hover': { color: 'primary.main' }
            }}
          >
            {item.label}
          </Link>
        );
      })}
    </MuiBreadcrumbs>
  );
}
