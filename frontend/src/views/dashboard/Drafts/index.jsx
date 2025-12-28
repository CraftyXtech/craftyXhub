import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

// MUI
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import Avatar from '@mui/material/Avatar';
import Chip from '@mui/material/Chip';
import Skeleton from '@mui/material/Skeleton';
import Grid from '@mui/material/Grid';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';

// Icons
import {
  IconPlus,
  IconDotsVertical,
  IconEdit,
  IconTrash,
  IconSend,
  IconFile,
  IconRefresh
} from '@tabler/icons-react';

// API
import { getUserDraftPosts, deletePost, publishPost, getImageUrl } from '@/api/services/postService';

/**
 * Drafts Page
 * Display user's draft posts
 */
export default function Drafts() {
  const navigate = useNavigate();
  
  // State
  const [drafts, setDrafts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedDraft, setSelectedDraft] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  // Fetch drafts
  const fetchDrafts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getUserDraftPosts();
      setDrafts(response.posts || response.items || response || []);
    } catch (err) {
      console.error('Failed to fetch drafts:', err);
      setError('Failed to load drafts');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDrafts();
  }, [fetchDrafts]);

  // Handle menu
  const handleMenuOpen = (event, draft) => {
    setAnchorEl(event.currentTarget);
    setSelectedDraft(draft);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedDraft(null);
  };

  // Actions
  const handleEdit = () => {
    if (selectedDraft) {
      navigate(`/dashboard/posts/edit/${selectedDraft.uuid}`);
    }
    handleMenuClose();
  };

  const handlePublish = async () => {
    if (!selectedDraft) return;
    
    try {
      setActionLoading(true);
      await publishPost(selectedDraft.uuid);
      handleMenuClose();
      fetchDrafts();
    } catch (err) {
      console.error('Failed to publish:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!selectedDraft) return;
    
    try {
      setActionLoading(true);
      await deletePost(selectedDraft.uuid);
      setDeleteDialogOpen(false);
      handleMenuClose();
      fetchDrafts();
    } catch (err) {
      console.error('Failed to delete:', err);
    } finally {
      setActionLoading(false);
    }
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h5" fontWeight={600}>
            Drafts
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Your unpublished work in progress
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <IconButton onClick={fetchDrafts} disabled={loading}>
            <IconRefresh size={20} />
          </IconButton>
          <Button
            variant="contained"
            startIcon={<IconPlus size={18} />}
            onClick={() => navigate('/dashboard/posts/create')}
            sx={{ borderRadius: 2 }}
          >
            New Draft
          </Button>
        </Stack>
      </Stack>

      {/* Drafts Grid */}
      {loading ? (
        <Grid container spacing={3}>
          {[...Array(4)].map((_, i) => (
            <Grid item xs={12} sm={6} md={4} key={i}>
              <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
                <Skeleton variant="rectangular" height={140} />
                <CardContent>
                  <Skeleton width="80%" />
                  <Skeleton width="40%" />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      ) : error ? (
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', textAlign: 'center', py: 6 }}>
          <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>
          <Button onClick={fetchDrafts}>Try Again</Button>
        </Card>
      ) : drafts.length === 0 ? (
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', textAlign: 'center', py: 8 }}>
          <IconFile size={48} color="#9E9E9E" style={{ marginBottom: 16 }} />
          <Typography variant="h6" gutterBottom>No drafts yet</Typography>
          <Typography color="text.secondary" sx={{ mb: 3 }}>
            Start writing and save as draft to continue later
          </Typography>
          <Button
            variant="contained"
            startIcon={<IconPlus size={18} />}
            onClick={() => navigate('/dashboard/posts/create')}
          >
            Create New Post
          </Button>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {drafts.map((draft) => (
            <Grid item xs={12} sm={6} md={4} key={draft.uuid}>
              <Card 
                elevation={0} 
                sx={{ 
                  border: '1px solid', 
                  borderColor: 'divider',
                  transition: 'box-shadow 0.2s',
                  '&:hover': {
                    boxShadow: 2
                  }
                }}
              >
                {/* Thumbnail */}
                <Box sx={{ position: 'relative', height: 140, bgcolor: 'grey.100' }}>
                  {draft.featured_image ? (
                    <Avatar
                      variant="square"
                      src={getImageUrl(draft.featured_image)}
                      sx={{ width: '100%', height: '100%' }}
                    />
                  ) : (
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center', 
                      height: '100%' 
                    }}>
                      <IconFile size={40} color="#BDBDBD" />
                    </Box>
                  )}
                  
                  {/* Actions button */}
                  <IconButton
                    size="small"
                    onClick={(e) => handleMenuOpen(e, draft)}
                    sx={{
                      position: 'absolute',
                      top: 8,
                      right: 8,
                      bgcolor: 'background.paper',
                      boxShadow: 1,
                      '&:hover': { bgcolor: 'background.paper' }
                    }}
                  >
                    <IconDotsVertical size={16} />
                  </IconButton>
                </Box>

                <CardContent>
                  <Typography variant="subtitle1" fontWeight={500} noWrap>
                    {draft.title || 'Untitled'}
                  </Typography>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mt: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      Last edited {formatDate(draft.updated_at || draft.created_at)}
                    </Typography>
                    <Chip label="Draft" size="small" variant="outlined" />
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Actions Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <MenuItem onClick={handleEdit}>
          <ListItemIcon><IconEdit size={18} /></ListItemIcon>
          Edit
        </MenuItem>
        <MenuItem onClick={handlePublish} disabled={actionLoading}>
          <ListItemIcon><IconSend size={18} /></ListItemIcon>
          Publish
        </MenuItem>
        <MenuItem onClick={() => setDeleteDialogOpen(true)} sx={{ color: 'error.main' }}>
          <ListItemIcon><IconTrash size={18} color="currentColor" /></ListItemIcon>
          Delete
        </MenuItem>
      </Menu>

      {/* Delete Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Draft?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{selectedDraft?.title || 'Untitled'}"? This cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)} disabled={actionLoading}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained" disabled={actionLoading}>
            {actionLoading ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
