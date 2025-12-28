import { useState } from 'react';
import {
  Box,
  TextField,
  InputAdornment,
  Typography,
  Card,
  CardContent,
  List,
  ListItemButton,
  ListItemText,
  Chip,
  Stack,
  Avatar
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { IconSearch } from '@tabler/icons-react';
import { motion } from 'framer-motion';

const MotionCard = motion.create(Card);

// Sample categories (will be replaced with API data)
const sampleCategories = [
  { slug: 'design', name: 'Design', count: 12 },
  { slug: 'technology', name: 'Technology', count: 18 },
  { slug: 'startups', name: 'Startups', count: 8 },
  { slug: 'productivity', name: 'Productivity', count: 6 },
  { slug: 'marketing', name: 'Marketing', count: 10 }
];

// Sample popular posts (will be replaced with API data)
const samplePopularPosts = [
  {
    id: 1,
    slug: 'design-systems-2024',
    title: 'Building Design Systems That Scale',
    featured_image: 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=100&h=100&fit=crop'
  },
  {
    id: 2,
    slug: 'startup-mistakes',
    title: '10 Common Startup Mistakes to Avoid',
    featured_image: 'https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=100&h=100&fit=crop'
  },
  {
    id: 3,
    slug: 'remote-work-tips',
    title: 'Remote Work: A Complete Guide',
    featured_image: 'https://images.unsplash.com/photo-1587614382346-4ec70e388b28?w=100&h=100&fit=crop'
  }
];

/**
 * Blog Sidebar - Search, Categories, Popular Posts
 */
export default function Sidebar({ 
  categories = sampleCategories,
  popularPosts = samplePopularPosts,
  activeCategory = null,
  onSearch = () => {}
}) {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    onSearch(searchQuery);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      {/* Search */}
      <MotionCard
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4 }}
        variant="outlined"
      >
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
            Search
          </Typography>
          <form onSubmit={handleSearch}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search articles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              slotProps={{
                input: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <IconSearch size={18} />
                    </InputAdornment>
                  )
                }
              }}
            />
          </form>
        </CardContent>
      </MotionCard>

      {/* Categories */}
      <MotionCard
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
        variant="outlined"
      >
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
            Categories
          </Typography>
          <List disablePadding>
            {categories.map((cat) => (
              <ListItemButton
                key={cat.slug}
                component={RouterLink}
                to={`/blog/category/${cat.slug}`}
                selected={activeCategory === cat.slug}
                sx={{
                  borderRadius: 1,
                  mb: 0.5,
                  '&.Mui-selected': {
                    bgcolor: 'primary.main',
                    color: 'white',
                    '&:hover': { bgcolor: 'primary.dark' }
                  }
                }}
              >
                <ListItemText primary={cat.name} />
                <Chip
                  label={cat.count}
                  size="small"
                  sx={{
                    minWidth: 28,
                    height: 22,
                    bgcolor: activeCategory === cat.slug ? 'rgba(255,255,255,0.2)' : 'grey.100'
                  }}
                />
              </ListItemButton>
            ))}
          </List>
        </CardContent>
      </MotionCard>

      {/* Popular Posts */}
      <MotionCard
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
        variant="outlined"
      >
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
            Popular Posts
          </Typography>
          <Stack spacing={2}>
            {popularPosts.map((post) => (
              <Box
                key={post.id}
                component={RouterLink}
                to={`/blog/${post.slug}`}
                sx={{
                  display: 'flex',
                  gap: 2,
                  textDecoration: 'none',
                  color: 'inherit',
                  '&:hover': { '& .post-title': { color: 'primary.main' } }
                }}
              >
                <Avatar
                  src={post.featured_image}
                  variant="rounded"
                  sx={{ width: 60, height: 60 }}
                />
                <Typography
                  className="post-title"
                  variant="body2"
                  sx={{
                    fontWeight: 500,
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                    transition: 'color 0.2s'
                  }}
                >
                  {post.title}
                </Typography>
              </Box>
            ))}
          </Stack>
        </CardContent>
      </MotionCard>
    </Box>
  );
}
