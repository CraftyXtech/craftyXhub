import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

// MUI
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Card from '@mui/material/Card';
import CardMedia from '@mui/material/CardMedia';
import CardContent from '@mui/material/CardContent';
import CardActionArea from '@mui/material/CardActionArea';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import Skeleton from '@mui/material/Skeleton';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';

// Icons
import {
  IconArrowLeft,
  IconEdit,
  IconTrash,
  IconLock,
  IconWorld
} from '@tabler/icons-react';

// Hooks
import { useReadingList, useListOperations } from '@/api/hooks/useCollection';
import { getImageUrl } from '@/api/services/postService';

/**
 * List Detail Page
 * Display a single reading list with all its posts
 */
export default function ListDetail() {
  const { uuid } = useParams();
  const navigate = useNavigate();
  const { list, items, loading, refetch } = useReadingList(uuid);
  const { update, removePost, loading: opLoading } = useListOperations();
  
  const [editOpen, setEditOpen] = useState(false);
  const [editData, setEditData] = useState({ name: '', description: '', is_public: false });

  const handleEdit = () => {
    if (list) {
      setEditData({
        name: list.name,
        description: list.description || '',
        is_public: list.is_public
      });
      setEditOpen(true);
    }
  };

  const handleSaveEdit = async () => {
    try {
      await update(uuid, editData);
      setEditOpen(false);
      refetch();
    } catch (err) {
      console.error('Failed to update list:', err);
    }
  };

  const handleRemovePost = async (postUuid) => {
    if (window.confirm('Remove this post from the list?')) {
      try {
        await removePost(uuid, postUuid);
        refetch();
      } catch (err) {
        console.error('Failed to remove post:', err);
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
        <Skeleton variant="text" width={200} height={40} />
        <Skeleton variant="text" width={300} height={24} sx={{ mb: 3 }} />
        <Grid container spacing={3}>
          {[1, 2, 3].map((i) => (
            <Grid item xs={12} sm={6} md={4} key={i}>
              <Skeleton variant="rounded" height={280} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  if (!list) {
    return (
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', textAlign: 'center', py: 8 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>List Not Found</Typography>
        <Button variant="contained" onClick={() => navigate('/dashboard/collection')}>
          Back to Collection
        </Button>
      </Card>
    );
  }

  return (
    <Box>
      {/* Back button + Header */}
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
        <IconButton onClick={() => navigate('/dashboard/collection')}>
          <IconArrowLeft />
        </IconButton>
        <Typography variant="h4" fontWeight={600}>
          {list.name}
        </Typography>
        {list.is_public ? (
          <IconWorld size={20} color="#4CAF50" />
        ) : (
          <IconLock size={20} color="#9E9E9E" />
        )}
        <IconButton onClick={handleEdit}>
          <IconEdit size={20} />
        </IconButton>
      </Stack>

      {list.description && (
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3, ml: 6 }}>
          {list.description}
        </Typography>
      )}

      <Typography variant="body2" color="text.secondary" sx={{ mb: 3, ml: 6 }}>
        {items.length} post{items.length !== 1 ? 's' : ''} • Created {formatDate(list.created_at)}
      </Typography>

      {/* Posts Grid */}
      {items.length === 0 ? (
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', textAlign: 'center', py: 8 }}>
          <Typography variant="h6" sx={{ mb: 1 }}>This List is Empty</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Add posts to this list while browsing.
          </Typography>
          <Button variant="contained" onClick={() => navigate('/')}>
            Explore Posts
          </Button>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {items.map((item) => (
            <Grid item xs={12} sm={6} md={4} key={item.uuid}>
              <Card
                elevation={0}
                sx={{
                  border: '1px solid',
                  borderColor: 'divider',
                  height: '100%',
                  '&:hover': { borderColor: 'primary.main' }
                }}
              >
                <CardActionArea onClick={() => navigate(`/blog/${item.post.slug}`)}>
                  {item.post.featured_image && (
                    <CardMedia
                      component="img"
                      height="140"
                      image={getImageUrl(item.post.featured_image)}
                      alt={item.post.title}
                    />
                  )}
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                      <Typography
                        variant="h6"
                        sx={{
                          fontSize: '1rem',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical'
                        }}
                      >
                        {item.post.title}
                      </Typography>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRemovePost(item.post.uuid);
                        }}
                        sx={{ color: 'error.main' }}
                      >
                        <IconTrash size={18} />
                      </IconButton>
                    </Stack>
                    {item.note && (
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mt: 1, fontStyle: 'italic' }}
                      >
                        "{item.note}"
                      </Typography>
                    )}
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                      Added {formatDate(item.created_at)}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Edit Dialog */}
      <Dialog open={editOpen} onClose={() => setEditOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit List</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label="List Name"
            value={editData.name}
            onChange={(e) => setEditData({ ...editData, name: e.target.value })}
            sx={{ mt: 2, mb: 2 }}
          />
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Description"
            value={editData.description}
            onChange={(e) => setEditData({ ...editData, description: e.target.value })}
            sx={{ mb: 2 }}
          />
          <FormControlLabel
            control={
              <Switch
                checked={editData.is_public}
                onChange={(e) => setEditData({ ...editData, is_public: e.target.checked })}
              />
            }
            label="Make this list public"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSaveEdit}
            disabled={!editData.name.trim() || opLoading}
          >
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
