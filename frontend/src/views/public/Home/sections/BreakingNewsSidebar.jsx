import { useEffect, useMemo, useState } from 'react';
import { Box, Skeleton, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { IconFlame } from '@tabler/icons-react';
import { getBreakingPosts, getImageUrl } from '@/api/services/postService';

const FALLBACK_IMAGE = 'https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=200&h=140&fit=crop';

function formatBreakingDate(dateString) {
  if (!dateString) {
    return '';
  }

  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) {
    return '';
  }

  const diffMinutes = Math.max(0, Math.floor((Date.now() - date.getTime()) / (1000 * 60)));
  if (diffMinutes < 1) return 'Just now';
  if (diffMinutes < 60) return `${diffMinutes} min ago`;

  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`;

  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
}

function BreakingNewsItem({ item }) {
  const categoryName = typeof item.category === 'object' ? item.category?.name : item.category;
  const imageUrl = getImageUrl(item.featured_image) || FALLBACK_IMAGE;

  return (
    <Box
      component={RouterLink}
      to={`/post/${item.slug || item.uuid}`}
      sx={{
        display: 'flex',
        gap: 2,
        textDecoration: 'none',
        color: 'inherit',
        py: 1.5,
        borderBottom: '1px solid',
        borderColor: 'divider',
        transition: 'background-color 0.2s ease',
        px: 1,
        mx: -1,
        borderRadius: 1,
        '&:hover': {
          bgcolor: 'action.hover',
        },
        '&:last-child': {
          borderBottom: 'none',
        },
      }}
    >
      {/* Thumbnail */}
      <Box
        component="img"
        src={imageUrl}
        alt={item.title}
        sx={{
          width: 80,
          height: 64,
          borderRadius: 1,
          objectFit: 'cover',
          flexShrink: 0,
        }}
      />

      {/* Text Content */}
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Typography
          variant="subtitle2"
          sx={{
            fontWeight: 600,
            lineHeight: 1.3,
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            mb: 0.5,
            fontSize: '0.82rem',
          }}
        >
          {item.title}
        </Typography>
        <Stack direction="row" spacing={1} alignItems="center" useFlexGap flexWrap="wrap">
          {categoryName ? (
            <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 700, fontSize: '0.68rem' }}>
              {categoryName}
            </Typography>
          ) : null}
          <Typography
            variant="caption"
            sx={{ color: 'text.disabled', fontSize: '0.7rem' }}
          >
            {formatBreakingDate(item.published_at || item.created_at)}
          </Typography>
        </Stack>
      </Box>
    </Box>
  );
}

export default function BreakingNewsSidebar() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchBreakingPosts = async () => {
      try {
        setLoading(true);
        const data = await getBreakingPosts({ limit: 4 });
        setPosts(data?.posts || []);
        setError('');
      } catch (err) {
        console.error('Failed to fetch breaking posts:', err);
        setError('Could not load breaking stories right now.');
      } finally {
        setLoading(false);
      }
    };

    fetchBreakingPosts();
  }, []);

  const content = useMemo(() => {
    if (loading) {
      return (
        <Stack spacing={1.5}>
          {[...Array(4)].map((_, index) => (
            <Box key={index} sx={{ display: 'flex', gap: 2, py: 1.5 }}>
              <Skeleton variant="rounded" width={80} height={64} />
              <Box sx={{ flex: 1 }}>
                <Skeleton width="90%" height={18} sx={{ mb: 1 }} />
                <Skeleton width="75%" height={18} sx={{ mb: 1 }} />
                <Skeleton width="50%" height={14} />
              </Box>
            </Box>
          ))}
        </Stack>
      );
    }

    if (error) {
      return (
        <Typography color="text.secondary" sx={{ py: 1 }}>
          {error}
        </Typography>
      );
    }

    if (posts.length === 0) {
      return (
        <Typography color="text.secondary" sx={{ py: 1 }}>
          No breaking stories have been picked yet.
        </Typography>
      );
    }

    return (
      <Stack spacing={0}>
        {posts.map((item) => (
          <BreakingNewsItem key={item.uuid || item.id} item={item} />
        ))}
      </Stack>
    );
  }, [error, loading, posts]);

  return (
    <Box
      sx={{
        position: 'sticky',
        top: 100,
      }}
    >
      {/* Header Bar */}
      <Box
        sx={{
          bgcolor: '#1a1a2e',
          color: 'white',
          px: 2.5,
          py: 1.5,
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          borderRadius: '8px 8px 0 0',
        }}
      >
        <IconFlame size={20} color="#ff6b35" />
        <Typography variant="subtitle1" sx={{ fontWeight: 700, letterSpacing: 0.5 }}>
          Breaking News
        </Typography>
      </Box>

      {/* News Items */}
      <Box
        sx={{
          bgcolor: 'background.paper',
          border: '1px solid',
          borderColor: 'divider',
          borderTop: 'none',
          borderRadius: '0 0 8px 8px',
          p: 2,
        }}
      >
        {content}
      </Box>
    </Box>
  );
}
