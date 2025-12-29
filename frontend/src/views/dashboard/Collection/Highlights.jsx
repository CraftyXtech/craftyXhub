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
import IconButton from '@mui/material/IconButton';
import Divider from '@mui/material/Divider';
import Skeleton from '@mui/material/Skeleton';

// Icons
import { IconHighlight, IconTrash, IconExternalLink } from '@tabler/icons-react';

// Hooks
import { useHighlights, useHighlightOperations } from '@/api/hooks/useCollection';

/**
 * Highlights Tab
 * Display user's saved text highlights from posts
 */
export default function Highlights() {
  const navigate = useNavigate();
  const { highlights, total, loading, refetch } = useHighlights(0, 50);
  const { remove, loading: deleteLoading } = useHighlightOperations();

  const handleDelete = async (uuid) => {
    if (window.confirm('Delete this highlight?')) {
      try {
        await remove(uuid);
        refetch();
      } catch (err) {
        console.error('Failed to delete highlight:', err);
      }
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <Box>
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} variant="rectangular" height={120} sx={{ mb: 1, borderRadius: 1 }} />
        ))}
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h6">
          {total} Highlight{total !== 1 ? 's' : ''}
        </Typography>
      </Stack>

      {/* Empty State */}
      {highlights.length === 0 ? (
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', textAlign: 'center', py: 8 }}>
          <IconHighlight size={48} color="#9E9E9E" />
          <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
            No Highlights Yet
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Highlight text while reading posts to save important passages.
          </Typography>
          <Button variant="contained" onClick={() => navigate('/')}>
            Start Reading
          </Button>
        </Card>
      ) : (
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
          <List disablePadding>
            {highlights.map((highlight, idx) => (
              <Box key={highlight.uuid}>
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
                      onClick={() => navigate(`/blog/${highlight.post?.slug || ''}`)}
                    >
                      <Typography variant="subtitle2" color="primary">
                        {highlight.post?.title || 'Unknown Post'}
                      </Typography>
                      <IconExternalLink size={14} />
                    </Stack>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Typography variant="caption" color="text.secondary">
                        {formatDate(highlight.created_at)}
                      </Typography>
                      <IconButton 
                        size="small" 
                        onClick={() => handleDelete(highlight.uuid)}
                        disabled={deleteLoading}
                      >
                        <IconTrash size={16} />
                      </IconButton>
                    </Stack>
                  </Stack>
                  
                  <Box
                    sx={{
                      p: 2,
                      bgcolor: 'rgba(243, 159, 90, 0.1)',
                      borderLeft: '3px solid #f39F5A',
                      borderRadius: 1,
                      width: '100%'
                    }}
                  >
                    <Typography variant="body2" fontStyle="italic">
                      "{highlight.text}"
                    </Typography>
                  </Box>
                  
                  {highlight.note && (
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Note: {highlight.note}
                    </Typography>
                  )}
                </ListItem>
                {idx < highlights.length - 1 && <Divider />}
              </Box>
            ))}
          </List>
        </Card>
      )}
    </Box>
  );
}
