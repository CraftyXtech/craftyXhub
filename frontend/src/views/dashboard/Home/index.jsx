import React, { useState, useEffect } from 'react';
import {
  Box, Tabs, Tab, Typography, Stack, CircularProgress, Alert, Divider,
  Chip, Avatar, Button, Paper, Skeleton
} from '@mui/material';
import { IconBookmark } from '@tabler/icons-react';
import { getPosts, getFeaturedPosts, getForYouPosts, getImageUrl } from '@/api/services/postService';
import { getCategories } from '@/api/services/categoryService';
import { followUser, getSuggestedUsers } from '@/api/services/userService';
import { getReadingLists } from '@/api/services/collectionService';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useAuth } from '@/api/AuthProvider';

// ===== FEED POST ITEM =====
function FeedPostItem({ post }) {
  const navigate = useNavigate();
  const postUrl = `/post/${post.slug || post.uuid}`;
  const imageUrl = post.featured_image
    ? getImageUrl(post.featured_image)
    : 'https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=400&h=300&fit=crop';
  const authorName = post.author?.full_name || post.author?.username || 'Anonymous';
  const categoryName = post.category?.name || 'General';
  const formattedDate = post.created_at
    ? new Date(post.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    : '';

  return (
    <Box
      onClick={() => navigate(postUrl)}
      sx={{
        display: 'flex',
        gap: 2,
        py: 2.5,
        cursor: 'pointer',
        '&:hover': { bgcolor: 'action.hover' },
        borderRadius: 1,
        px: 1
      }}
    >
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.5 }}>
          <Typography variant="caption" fontWeight={500}>{authorName}</Typography>
          <Typography variant="caption" color="text.secondary">in {categoryName}</Typography>
        </Stack>
        <Typography
          variant="subtitle1"
          fontWeight={700}
          sx={{ mb: 0.5, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', lineHeight: 1.3 }}
        >
          {post.title}
        </Typography>
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mb: 1, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}
        >
          {post.excerpt}
        </Typography>
        <Stack direction="row" spacing={1} alignItems="center">
          <Typography variant="caption" color="text.secondary">{formattedDate}</Typography>
          {post.read_time && <Typography variant="caption" color="text.secondary">· {post.read_time}</Typography>}
        </Stack>
      </Box>
      <Box
        component="img"
        src={imageUrl}
        alt={post.title}
        sx={{ width: 120, height: 80, objectFit: 'cover', borderRadius: 1, flexShrink: 0 }}
      />
    </Box>
  );
}

// ===== RECOMMENDED TOPICS =====
function RecommendedTopics({ categories, loading }) {
  if (loading) {
    return (
      <Box sx={{ mb: 4 }}>
        <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 2 }}>Recommended topics</Typography>
        <Stack direction="row" flexWrap="wrap" gap={1}>
          {[1, 2, 3, 4, 5].map((i) => <Skeleton key={i} variant="rounded" width={80} height={32} />)}
        </Stack>
      </Box>
    );
  }

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 2 }}>Recommended topics</Typography>
      <Stack direction="row" flexWrap="wrap" gap={1}>
        {categories.slice(0, 7).map((cat) => (
          <Chip
            key={cat.id}
            label={cat.name}
            component={RouterLink}
            to={`/category/${cat.slug}`}
            clickable
            variant="outlined"
            size="small"
            sx={{ borderRadius: 3, fontWeight: 500, '&:hover': { bgcolor: 'action.hover' } }}
          />
        ))}
      </Stack>
      {categories.length > 7 && (
        <Typography
          component={RouterLink}
          to="/categories"
          variant="caption"
          color="primary"
          sx={{ display: 'block', mt: 1.5, textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
        >
          See more topics
        </Typography>
      )}
    </Box>
  );
}

// ===== WHO TO FOLLOW =====
function WhoToFollow({ users, loading, onFollow }) {
  if (loading) {
    return (
      <Box sx={{ mb: 4 }}>
        <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 2 }}>Recommended Authors</Typography>
        {[1, 2, 3].map((i) => (
          <Stack key={i} direction="row" spacing={1.5} alignItems="center" sx={{ mb: 2 }}>
            <Skeleton variant="circular" width={40} height={40} />
            <Box sx={{ flex: 1 }}><Skeleton width="60%" /><Skeleton width="80%" /></Box>
          </Stack>
        ))}
      </Box>
    );
  }

  if (!users || users.length === 0) return null;

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 2 }}>Recommended Authors</Typography>
      {users.map((user) => (
        <Stack key={user.uuid || user.id} direction="row" spacing={1.5} alignItems="flex-start" sx={{ mb: 2 }}>
          <Avatar
            src={user.avatar}
            alt={user.full_name || user.username}
            sx={{ width: 40, height: 40 }}
          />
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant="body2" fontWeight={600} noWrap>
              {user.full_name || user.username}
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
              {user.bio || 'Writer'}
            </Typography>
          </Box>
          <Button
            variant="outlined"
            size="small"
            onClick={() => onFollow(user)}
            sx={{ borderRadius: 3, textTransform: 'none', fontWeight: 500, minWidth: 70 }}
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
    </Box>
  );
}

// ===== READING LISTS =====
function ReadingListsSection({ lists, loading }) {
  if (loading) {
    return (
      <Box sx={{ mb: 4 }}>
        <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 2 }}>Reading list</Typography>
        <Skeleton width="100%" height={20} />
      </Box>
    );
  }

  return (
    <Box sx={{ mb: 4 }}>
      {lists && lists.length > 0 ? (
        <>
          <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 2 }}>Reading list</Typography>
          {lists.slice(0, 3).map((list) => (
            <Typography
              key={list.uuid}
              component={RouterLink}
              to={`/dashboard/collection/list/${list.uuid}`}
              variant="body2"
              sx={{ display: 'block', mb: 1, color: 'text.primary', textDecoration: 'none', '&:hover': { color: 'primary.main' } }}
            >
              {list.name} ({list.item_count || 0})
            </Typography>
          ))}
          <Typography
            component={RouterLink}
            to="/dashboard/collection"
            variant="caption"
            color="primary"
            sx={{ textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
          >
            View all lists
          </Typography>
        </>
      ) : (
        <Box
          sx={{
            bgcolor: 'primary.main',
            color: 'primary.contrastText',
            borderRadius: 2,
            p: 2.5,
            boxShadow: 2
          }}
        >
          <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1.5 }}>
            Reading list
          </Typography>
          <Stack direction="row" spacing={2} alignItems="flex-start">
            <IconBookmark size={32} />
            <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
              Click the bookmark icon on any story to save it to your reading list.
            </Typography>
          </Stack>
        </Box>
      )}
    </Box>
  );
}

// ===== MAIN COMPONENT =====
export default function DashboardHome() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState(0);

  // Feed state
  const [posts, setPosts] = useState([]);
  const [loadingPosts, setLoadingPosts] = useState(true);
  const [error, setError] = useState(null);

  // Sidebar state
  const [categories, setCategories] = useState([]);
  const [loadingCategories, setLoadingCategories] = useState(true);
  const [suggestedUsers, setSuggestedUsers] = useState([]);
  const [loadingUsers, setLoadingUsers] = useState(true);
  const [readingLists, setReadingLists] = useState([]);
  const [loadingLists, setLoadingLists] = useState(true);

  // Fetch posts
  useEffect(() => {
    const fetchPosts = async () => {
      setLoadingPosts(true);
      setError(null);
      try {
        const data = activeTab === 0
          ? await getForYouPosts({ limit: 20 })
          : await getFeaturedPosts({ limit: 20 });
        setPosts(data.posts || data || []);
      } catch (err) {
        console.error('Failed to fetch posts:', err);
        setError('Failed to load posts.');
      } finally {
        setLoadingPosts(false);
      }
    };
    fetchPosts();
  }, [activeTab]);

  // Fetch suggested users from API
  useEffect(() => {
    const fetchSuggestedUsers = async () => {
      try {
        const data = await getSuggestedUsers(5);
        setSuggestedUsers(data.users || []);
      } catch (err) {
        console.error('Suggested users error:', err);
      } finally {
        setLoadingUsers(false);
      }
    };
    fetchSuggestedUsers();
  }, []);

  // Fetch sidebar data
  useEffect(() => {
    const fetchSidebarData = async () => {
      // Categories
      try {
        const catData = await getCategories();
        setCategories(catData.categories || catData || []);
      } catch (err) {
        console.error('Categories error:', err);
      } finally {
        setLoadingCategories(false);
      }

      // Suggested users - extract unique authors from loaded posts
      // (We'll update this after posts load)
      setLoadingUsers(false);

      // Reading lists
      try {
        const listData = await getReadingLists();
        setReadingLists(listData.lists || listData || []);
      } catch (err) {
        console.error('Lists error:', err);
      } finally {
        setLoadingLists(false);
      }
    };

    fetchSidebarData();
  }, [user?.uuid]);

  const handleFollow = async (targetUser) => {
    try {
      await followUser(targetUser.uuid);
      // Remove from suggestions
      setSuggestedUsers((prev) => prev.filter((u) => u.uuid !== targetUser.uuid));
    } catch (err) {
      console.error('Failed to follow:', err);
    }
  };

  return (
    <Box sx={{ display: 'flex', gap: 6, maxWidth: 1100, mx: 'auto', py: 2 }}>
      {/* Main Feed */}
      <Box sx={{ flex: 1, minWidth: 0, maxWidth: 680 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs
            value={activeTab}
            onChange={(e, v) => setActiveTab(v)}
            sx={{ '& .MuiTab-root': { textTransform: 'none', fontWeight: 500, fontSize: '0.95rem' } }}
          >
            <Tab label="For you" />
            <Tab label="Featured" />
          </Tabs>
        </Box>

        {loadingPosts ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}><CircularProgress /></Box>
        ) : error ? (
          <Alert severity="error" sx={{ my: 2 }}>{error}</Alert>
        ) : posts.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 6 }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>No posts yet</Typography>
            <Typography variant="body2" color="text.secondary">Check back later for new content.</Typography>
          </Box>
        ) : (
          <Stack divider={<Divider />}>
            {posts.map((post) => <FeedPostItem key={post.uuid || post.id} post={post} />)}
          </Stack>
        )}
      </Box>

      {/* Right Sidebar */}
      <Box
        sx={{
          width: 320,
          flexShrink: 0,
          display: { xs: 'none', lg: 'block' },
          position: 'sticky',
          top: 80,
          alignSelf: 'flex-start',
          maxHeight: 'calc(100vh - 100px)',
          overflowY: 'auto',
          // Hide scrollbar like Twitter/X
          scrollbarWidth: 'none', // Firefox
          msOverflowStyle: 'none', // IE/Edge
          '&::-webkit-scrollbar': {
            display: 'none' // Chrome, Safari, Opera
          }
        }}
      >
        <RecommendedTopics categories={categories} loading={loadingCategories} />
        <Divider sx={{ my: 3 }} />
        <WhoToFollow users={suggestedUsers} loading={loadingUsers} onFollow={handleFollow} />
        <Divider sx={{ my: 3 }} />
        <ReadingListsSection lists={readingLists} loading={loadingLists} />
      </Box>
    </Box>
  );
}
