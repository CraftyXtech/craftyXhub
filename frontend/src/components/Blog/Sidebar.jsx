import { useState, useEffect } from 'react';
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
  Stack,
  Avatar,
  Button,
  Divider
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { IconSearch, IconArrowLeft, IconChevronRight } from '@tabler/icons-react';
import { motion } from 'framer-motion';
import { getCategories } from '@/api/services/categoryService';
import { axiosPublic } from '@/api/axios';

const MotionCard = motion.create(Card);

/**
 * Blog Sidebar - Search, Sibling Subcategories (contextual), Popular Posts
 * @param {object} category - Current category object with parent info
 * @param {string} activeCategory - Current category slug
 */
export default function Sidebar({ 
  category = null,
  activeCategory = null,
  onSearch = () => {}
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [siblingCategories, setSiblingCategories] = useState([]);
  const [parentCategory, setParentCategory] = useState(null);
  const [popularPosts, setPopularPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch sibling subcategories and popular posts
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch all categories to find siblings
        const catData = await getCategories();
        const allCategories = catData.categories || [];
        
        // Determine parent and siblings based on current category
        if (category?.isSubcategory && category?.parent) {
          // Current is a subcategory - find parent and siblings
          const parent = allCategories.find(c => c.id === category.parent.id);
          setParentCategory(parent || category.parent);
          
          // Siblings are other subcategories of the same parent
          const siblings = parent?.subcategories?.filter(sub => sub.id !== category.id) || [];
          setSiblingCategories(siblings);
        } else if (category && !category.isSubcategory) {
          // Current is a main category - show its subcategories
          const current = allCategories.find(c => c.id === category.id);
          setParentCategory(null);
          setSiblingCategories(current?.subcategories || category.subcategories || []);
        } else {
          setSiblingCategories([]);
          setParentCategory(null);
        }
        
        // Fetch popular posts
        try {
          const postsResponse = await axiosPublic.get('/posts/', {
            params: { page: 1, page_size: 3, status: 'published' }
          });
          setPopularPosts(postsResponse.data.posts || []);
        } catch (err) {
          console.error('Failed to fetch popular posts:', err);
        }
      } catch (err) {
        console.error('Failed to fetch sidebar data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [category]);

  const handleSearch = (e) => {
    e.preventDefault();
    onSearch(searchQuery);
  };

  // Determine section title
  const getSectionTitle = () => {
    if (category?.isSubcategory && parentCategory) {
      return `More in ${parentCategory.name}`;
    }
    if (category && !category.isSubcategory) {
      return 'Subcategories';
    }
    return 'Categories';
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

      {/* Sibling Categories / Subcategories */}
      {(siblingCategories.length > 0 || parentCategory) && (
        <MotionCard
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          variant="outlined"
        >
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              {getSectionTitle()}
            </Typography>
            
            <List disablePadding>
              {siblingCategories.map((cat) => (
                <ListItemButton
                  key={cat.slug}
                  component={RouterLink}
                  to={`/category/${cat.slug}`}
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
                  <IconChevronRight size={16} style={{ marginRight: 8, opacity: 0.6 }} />
                  <ListItemText primary={cat.name} />
                </ListItemButton>
              ))}
            </List>

            {/* Back to parent link for subcategories */}
            {parentCategory && (
              <>
                <Divider sx={{ my: 2 }} />
                <Button
                  component={RouterLink}
                  to={`/category/${parentCategory.slug}`}
                  startIcon={<IconArrowLeft size={16} />}
                  fullWidth
                  sx={{
                    justifyContent: 'flex-start',
                    color: 'primary.main',
                    fontWeight: 500
                  }}
                >
                  All {parentCategory.name}
                </Button>
              </>
            )}
          </CardContent>
        </MotionCard>
      )}

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
            {popularPosts.length > 0 ? (
              popularPosts.map((post) => (
                <Box
                  key={post.id || post.uuid}
                  component={RouterLink}
                  to={`/post/${post.slug}`}
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
                    sx={{ width: 60, height: 60, bgcolor: 'grey.200' }}
                  >
                    {post.title?.[0]}
                  </Avatar>
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
              ))
            ) : (
              <Typography variant="body2" color="text.secondary">
                No posts yet
              </Typography>
            )}
          </Stack>
        </CardContent>
      </MotionCard>
    </Box>
  );
}
