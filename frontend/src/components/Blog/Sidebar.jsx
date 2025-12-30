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
  Divider,
  Skeleton
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { IconSearch, IconArrowLeft, IconChevronRight } from '@tabler/icons-react';
import { motion } from 'framer-motion';
import { getCategories } from '@/api/services/categoryService';
import { getSuggestedUsers, followUser } from '@/api/services/userService';
import { axiosPublic } from '@/api/axios';

const MotionCard = motion.create(Card);

/**
 * Blog Sidebar - Search, Sibling Subcategories (contextual), Who to Follow, Popular Posts
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
  const [suggestedUsers, setSuggestedUsers] = useState([]);
  const [loadingUsers, setLoadingUsers] = useState(true);

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
        
        // Fetch trending posts (last 7 days, ordered by views + likes)
        try {
          const postsResponse = await axiosPublic.get('/posts/trending/', {
            params: { limit: 4 }
          });
          setPopularPosts(postsResponse.data.posts || postsResponse.data || []);
        } catch (err) {
          console.error('Failed to fetch popular posts:', err);
        }

        // Fetch suggested users
        try {
          const usersData = await getSuggestedUsers(3);
          setSuggestedUsers(usersData.users || []);
        } catch (err) {
          console.error('Failed to fetch suggested users:', err);
        } finally {
          setLoadingUsers(false);
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

  const handleFollow = async (targetUser) => {
    try {
      await followUser(targetUser.uuid);
      // Remove from suggestions after following
      setSuggestedUsers((prev) => prev.filter((u) => u.uuid !== targetUser.uuid));
    } catch (err) {
      console.error('Failed to follow:', err);
    }
  };

  // Determine section title
  const getSectionTitle = () => {
    if (category?.isSubcategory && parentCategory) {
      return `More in ${parentCategory.name}`;
    }
    if (category && !category.isSubcategory) {
      return 'Explore Topics';
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

      <MotionCard
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4, delay: 0.15 }}
        variant="outlined"
      >
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
            Trending Now
          </Typography>
          <Stack spacing={2}>
            {popularPosts.length > 0 ? (
              popularPosts.slice(0, 4).map((post) => (
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

      {/* Recommended Authors */}
      <MotionCard
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
        variant="outlined"
      >
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
            Recommended Authors
          </Typography>
          {loadingUsers ? (
            <Stack spacing={2}>
              {[1, 2, 3].map((i) => (
                <Stack key={i} direction="row" spacing={1.5} alignItems="center">
                  <Skeleton variant="circular" width={40} height={40} />
                  <Box sx={{ flex: 1 }}>
                    <Skeleton width="60%" />
                    <Skeleton width="80%" />
                  </Box>
                </Stack>
              ))}
            </Stack>
          ) : suggestedUsers.length > 0 ? (
            <Stack spacing={2}>
              {suggestedUsers.map((user) => (
                <Stack key={user.uuid || user.id} direction="row" spacing={1.5} alignItems="flex-start">
                  <Avatar
                    src={user.avatar}
                    alt={user.full_name || user.username}
                    sx={{ width: 40, height: 40 }}
                  />
                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    <Typography variant="body2" fontWeight={600} noWrap>
                      {user.full_name || user.username}
                    </Typography>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      sx={{
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden'
                      }}
                    >
                      {user.bio || 'Writer'}
                    </Typography>
                  </Box>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => handleFollow(user)}
                    sx={{
                      borderRadius: 3,
                      textTransform: 'none',
                      fontWeight: 500,
                      minWidth: 70,
                      fontSize: '0.75rem'
                    }}
                  >
                    Follow
                  </Button>
                </Stack>
              ))}
              <Typography
                component={RouterLink}
                to="/dashboard/following"
                variant="caption"
                color="primary"
                sx={{ textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
              >
                See more suggestions
              </Typography>
            </Stack>
          ) : (
            <Typography variant="body2" color="text.secondary">
              No suggestions available
            </Typography>
          )}
        </CardContent>
      </MotionCard>
    </Box>
  );
}
