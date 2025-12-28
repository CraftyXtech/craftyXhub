import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

// MUI
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import TablePagination from '@mui/material/TablePagination';
import Chip from '@mui/material/Chip';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import Stack from '@mui/material/Stack';
import Avatar from '@mui/material/Avatar';
import Skeleton from '@mui/material/Skeleton';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';

// Icons
import {
  IconPlus,
  IconSearch,
  IconDotsVertical,
  IconEdit,
  IconTrash,
  IconEye,
  IconSend,
  IconArrowBack,
  IconRefresh
} from '@tabler/icons-react';

// API
import { getPosts, deletePost, publishPost, unpublishPost, getImageUrl } from '@/api/services/postService';
import { useAuth } from '@/api/AuthProvider';

/**
 * Posts List Page
 * Display user's posts with CRUD actions
 */
export default function Posts() {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  // State
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedPost, setSelectedPost] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  // Fetch posts
  const fetchPosts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        page: page + 1,
        limit: rowsPerPage,
        author_id: user?.id,
        published: undefined // Get both published and drafts
      };
      
      if (search) {
        params.search = search;
      }
      
      const response = await getPosts(params);
      setPosts(response.posts || response.items || []);
      setTotal(response.total || 0);
    } catch (err) {
      console.error('Failed to fetch posts:', err);
      setError('Failed to load posts');
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, search, user?.id]);

  useEffect(() => {
    fetchPosts();
  }, [fetchPosts]);

  // Handle menu open
  const handleMenuOpen = (event, post) => {
    setAnchorEl(event.currentTarget);
    setSelectedPost(post);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedPost(null);
  };

  // Handle actions
  const handleEdit = () => {
    if (selectedPost) {
      navigate(`/dashboard/posts/edit/${selectedPost.uuid}`);
    }
    handleMenuClose();
  };

  const handleView = () => {
    if (selectedPost) {
      window.open(`/blog/${selectedPost.slug}`, '_blank');
    }
    handleMenuClose();
  };

  const handleDeleteClick = () => {
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!selectedPost) return;
    
    try {
      setActionLoading(true);
      await deletePost(selectedPost.uuid);
      setDeleteDialogOpen(false);
      handleMenuClose();
      fetchPosts();
    } catch (err) {
      console.error('Failed to delete post:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handlePublishToggle = async () => {
    if (!selectedPost) return;
    
    try {
      setActionLoading(true);
      if (selectedPost.is_published) {
        await unpublishPost(selectedPost.uuid);
      } else {
        await publishPost(selectedPost.uuid);
      }
      handleMenuClose();
      fetchPosts();
    } catch (err) {
      console.error('Failed to toggle publish:', err);
    } finally {
      setActionLoading(false);
    }
  };

  // Pagination handlers
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
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
            My Posts
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage your published and draft posts
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<IconPlus size={18} />}
          onClick={() => navigate('/dashboard/posts/create')}
          sx={{ borderRadius: 2 }}
        >
          New Post
        </Button>
      </Stack>

      {/* Filters */}
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', mb: 3 }}>
        <CardContent sx={{ py: 2 }}>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
            <TextField
              size="small"
              placeholder="Search posts..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <IconSearch size={18} />
                  </InputAdornment>
                )
              }}
              sx={{ width: { xs: '100%', sm: 300 } }}
            />
            <Box sx={{ flex: 1 }} />
            <IconButton onClick={fetchPosts} disabled={loading}>
              <IconRefresh size={20} />
            </IconButton>
          </Stack>
        </CardContent>
      </Card>

      {/* Posts Table */}
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Post</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Views</TableCell>
                <TableCell>Date</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                // Skeleton loading
                [...Array(5)].map((_, i) => (
                  <TableRow key={i}>
                    <TableCell>
                      <Stack direction="row" spacing={2} alignItems="center">
                        <Skeleton variant="rounded" width={60} height={45} />
                        <Box>
                          <Skeleton width={200} />
                          <Skeleton width={120} height={16} />
                        </Box>
                      </Stack>
                    </TableCell>
                    <TableCell><Skeleton width={80} /></TableCell>
                    <TableCell><Skeleton width={50} /></TableCell>
                    <TableCell><Skeleton width={100} /></TableCell>
                    <TableCell><Skeleton width={40} /></TableCell>
                  </TableRow>
                ))
              ) : error ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                    <Typography color="error">{error}</Typography>
                    <Button onClick={fetchPosts} sx={{ mt: 1 }}>Try Again</Button>
                  </TableCell>
                </TableRow>
              ) : posts.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 6 }}>
                    <Typography color="text.secondary" sx={{ mb: 2 }}>
                      No posts yet. Start writing!
                    </Typography>
                    <Button
                      variant="contained"
                      startIcon={<IconPlus size={18} />}
                      onClick={() => navigate('/dashboard/posts/create')}
                    >
                      Create Your First Post
                    </Button>
                  </TableCell>
                </TableRow>
              ) : (
                posts.map((post) => (
                  <TableRow key={post.uuid} hover>
                    <TableCell>
                      <Stack direction="row" spacing={2} alignItems="center">
                        <Avatar
                          variant="rounded"
                          src={getImageUrl(post.featured_image)}
                          sx={{ width: 60, height: 45 }}
                        >
                          {post.title?.[0]?.toUpperCase()}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight={500} noWrap sx={{ maxWidth: 280 }}>
                            {post.title}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {post.category?.name || 'Uncategorized'}
                          </Typography>
                        </Box>
                      </Stack>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={post.is_published ? 'Published' : 'Draft'}
                        size="small"
                        color={post.is_published ? 'success' : 'default'}
                        variant={post.is_published ? 'filled' : 'outlined'}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{post.views_count || 0}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {formatDate(post.published_at || post.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <IconButton onClick={(e) => handleMenuOpen(e, post)} size="small">
                        <IconDotsVertical size={18} />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        {!loading && posts.length > 0 && (
          <TablePagination
            component="div"
            count={total}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={[5, 10, 25]}
          />
        )}
      </Card>

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
        {selectedPost?.is_published && (
          <MenuItem onClick={handleView}>
            <ListItemIcon><IconEye size={18} /></ListItemIcon>
            View
          </MenuItem>
        )}
        <MenuItem onClick={handlePublishToggle} disabled={actionLoading}>
          <ListItemIcon>
            {selectedPost?.is_published ? <IconArrowBack size={18} /> : <IconSend size={18} />}
          </ListItemIcon>
          {selectedPost?.is_published ? 'Unpublish' : 'Publish'}
        </MenuItem>
        <MenuItem onClick={handleDeleteClick} sx={{ color: 'error.main' }}>
          <ListItemIcon><IconTrash size={18} color="currentColor" /></ListItemIcon>
          Delete
        </MenuItem>
      </Menu>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Post?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{selectedPost?.title}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)} disabled={actionLoading}>
            Cancel
          </Button>
          <Button 
            onClick={handleDeleteConfirm} 
            color="error" 
            variant="contained"
            disabled={actionLoading}
          >
            {actionLoading ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
