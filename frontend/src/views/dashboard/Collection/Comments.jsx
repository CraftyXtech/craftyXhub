import { useNavigate } from 'react-router-dom';

// MUI
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import Divider from '@mui/material/Divider';
import Skeleton from '@mui/material/Skeleton';

// Icons
import { IconMessage, IconExternalLink } from '@tabler/icons-react';

// Hooks
import { useUserComments } from '@/api/hooks/useCollection';

/**
 * Comments Tab
 * Display the user's comments across all posts
 */
export default function Comments() {
  const navigate = useNavigate();
  const { comments, total, loading } = useUserComments(0, 50);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const truncate = (text, length = 150) => {
    if (!text) return '';
    return text.length > length ? text.substring(0, length) + '...' : text;
  };

  if (loading) {
    return (
      <Box>
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} variant="rectangular" height={100} sx={{ mb: 1, borderRadius: 1 }} />
        ))}
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h6">
          {total} Comment{total !== 1 ? 's' : ''}
        </Typography>
      </Stack>

      {/* Empty State */}
      {comments.length === 0 ? (
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', textAlign: 'center', py: 8 }}>
          <IconMessage size={48} color="#9E9E9E" />
          <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
            No Comments Yet
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Your comments on posts will appear here.
          </Typography>
          <Button variant="contained" onClick={() => navigate('/')}>
            Explore Posts
          </Button>
        </Card>
      ) : (
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
          <List disablePadding>
            {comments.map((comment, idx) => (
              <Box key={comment.uuid}>
                <ListItem
                  sx={{ 
                    py: 2, 
                    flexDirection: 'column',
                    alignItems: 'flex-start'
                  }}
                >
                  <Stack 
                    direction="row" 
                    justifyContent="space-between" 
                    alignItems="flex-start"
                    sx={{ width: '100%', mb: 1 }}
                  >
                    <Stack 
                      direction="row" 
                      spacing={1} 
                      alignItems="center"
                      sx={{ cursor: 'pointer' }}
                      onClick={() => navigate(`/blog/${comment.post?.slug || ''}`)}
                    >
                      <Typography variant="subtitle2" color="primary">
                        {comment.post?.title || 'Unknown Post'}
                      </Typography>
                      <IconExternalLink size={14} />
                    </Stack>
                    <Typography variant="caption" color="text.secondary">
                      {formatDate(comment.created_at)}
                    </Typography>
                  </Stack>
                  <Typography variant="body2" color="text.secondary">
                    {truncate(comment.content)}
                  </Typography>
                </ListItem>
                {idx < comments.length - 1 && <Divider />}
              </Box>
            ))}
          </List>
        </Card>
      )}
    </Box>
  );
}
