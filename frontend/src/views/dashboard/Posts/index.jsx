import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';

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
import Alert from '@mui/material/Alert';

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
  IconRefresh,
  IconStar,
  IconStarOff,
  IconFlame,
  IconBolt
} from '@tabler/icons-react';

// API
import {
  getPosts,
  deletePost,
  publishPost,
  unpublishPost,
  featurePost,
  setHomepageTrending,
  setBreakingNews,
  getImageUrl
} from '@/api/services/postService';
import {
  approvePostQualityOverride,
  generateDistributionAssets,
  getDistributionAssets,
  getPostIntelligenceStatuses,
  runPostQualityReview,
  updateDistributionAssetStatus,
} from '@/api/services/contentIntelligenceService';
import { useAuth } from '@/api/AuthProvider';
import { getApiErrorMessage } from '@/utils/apiError';

const isAdminOrMod = (user) => ['super_admin', 'admin', 'moderator'].includes(user?.role);
const CONTENT_INTELLIGENCE_ENABLED = import.meta.env.VITE_CONTENT_INTELLIGENCE_ENABLED !== 'false';

/**
 * Posts List Page
 * Display user's posts with CRUD actions
 */
export default function Posts() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
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
  const [breakingDialogOpen, setBreakingDialogOpen] = useState(false);
  const [breakingOrderInput, setBreakingOrderInput] = useState('');
  const [breakingOrderError, setBreakingOrderError] = useState('');
  const [overrideDialogOpen, setOverrideDialogOpen] = useState(false);
  const [overrideReason, setOverrideReason] = useState('');
  const [overrideReasonError, setOverrideReasonError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [intelligenceStatuses, setIntelligenceStatuses] = useState({});

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

  useEffect(() => {
    const loadStatuses = async () => {
      if (!CONTENT_INTELLIGENCE_ENABLED || !isAdminOrMod(user) || posts.length === 0) {
        setIntelligenceStatuses({});
        return;
      }
      try {
        const statuses = await getPostIntelligenceStatuses(posts.map((post) => post.uuid));
        setIntelligenceStatuses(statuses || {});
      } catch (err) {
        console.error('Failed to load content intelligence statuses:', err);
      }
    };
    loadStatuses();
  }, [posts, user]);

  // Handle menu open
  const handleMenuOpen = (event, post) => {
    setAnchorEl(event.currentTarget);
    setSelectedPost(post);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedPost(null);
  };

  const closeMenuOnly = () => {
    setAnchorEl(null);
  };

  const closeBreakingDialog = () => {
    if (actionLoading) return;
    setBreakingDialogOpen(false);
    setBreakingOrderInput('');
    setBreakingOrderError('');
    setSelectedPost(null);
  };

  const closeOverrideDialog = () => {
    if (actionLoading) return;
    setOverrideDialogOpen(false);
    setOverrideReason('');
    setOverrideReasonError('');
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
      window.open(`/post/${selectedPost.slug}`, '_blank');
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

    // Require category before publishing
    if (!selectedPost.is_published && !selectedPost.category && !selectedPost.category_id) {
      handleMenuClose();
      setError('Please add a category before publishing. Edit the post to choose a category.');
      return;
    }
    
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
      const detail = err.response?.data?.detail;
      if (detail?.message) {
        setError(`${detail.message} ${detail.warnings?.join(' ') || detail.critical_failures?.join(' ') || ''}`.trim());
      } else {
        setError(getApiErrorMessage(err, 'Failed to toggle publish'));
      }
    } finally {
      setActionLoading(false);
    }
  };

  const handleRunQuality = async () => {
    if (!selectedPost) return;
    try {
      setActionLoading(true);
      await runPostQualityReview(selectedPost.uuid);
      handleMenuClose();
      fetchPosts();
    } catch (err) {
      console.error('Failed to run quality check:', err);
      setError(getApiErrorMessage(err, 'Failed to run quality check'));
    } finally {
      setActionLoading(false);
    }
  };

  const handleGenerateDistribution = async () => {
    if (!selectedPost) return;
    try {
      setActionLoading(true);
      await generateDistributionAssets(selectedPost.uuid);
      handleMenuClose();
      fetchPosts();
    } catch (err) {
      console.error('Failed to generate distribution assets:', err);
      setError(getApiErrorMessage(err, 'Failed to generate distribution assets'));
    } finally {
      setActionLoading(false);
    }
  };

  const handleApproveAssets = async () => {
    if (!selectedPost) return;
    try {
      setActionLoading(true);
      const assets = await getDistributionAssets(selectedPost.uuid);
      await Promise.all(
        (assets || [])
          .filter((asset) => asset.status === 'pending')
          .map((asset) => updateDistributionAssetStatus(asset.uuid, 'approved'))
      );
      handleMenuClose();
      fetchPosts();
    } catch (err) {
      console.error('Failed to approve distribution assets:', err);
      setError(getApiErrorMessage(err, 'Failed to approve distribution assets'));
    } finally {
      setActionLoading(false);
    }
  };

  const handleApproveOverride = async () => {
    if (!selectedPost) return;
    setOverrideReason('');
    setOverrideReasonError('');
    setOverrideDialogOpen(true);
    closeMenuOnly();
  };

  const handleFeatureToggle = async () => {
    if (!selectedPost) return;
    
    try {
      setActionLoading(true);
      await featurePost(selectedPost.uuid, !selectedPost.is_featured);
      handleMenuClose();
      fetchPosts();
    } catch (err) {
      console.error('Failed to toggle feature:', err);
      setError('Failed to update featured status');
    } finally {
      setActionLoading(false);
    }
  };

  const handleHomepageTrendingToggle = async () => {
    if (!selectedPost) return;

    try {
      setActionLoading(true);
      await setHomepageTrending(selectedPost.uuid, !selectedPost.is_homepage_trending);
      handleMenuClose();
      fetchPosts();
    } catch (err) {
      console.error('Failed to update homepage trending:', err);
      setError(getApiErrorMessage(err, 'Failed to update homepage trending'));
    } finally {
      setActionLoading(false);
    }
  };

  const handleBreakingNewsToggle = async () => {
    if (!selectedPost) return;

    if (!selectedPost.is_breaking_news) {
      setBreakingOrderInput('');
      setBreakingOrderError('');
      setBreakingDialogOpen(true);
      closeMenuOnly();
      return;
    }

    try {
      setActionLoading(true);
      await setBreakingNews(selectedPost.uuid, false);
      handleMenuClose();
      fetchPosts();
    } catch (err) {
      console.error('Failed to update breaking news:', err);
      setError(getApiErrorMessage(err, 'Failed to update breaking news'));
    } finally {
      setActionLoading(false);
    }
  };

  const handleBreakingDialogSubmit = async () => {
    if (!selectedPost) return;

    const trimmedOrder = breakingOrderInput.trim();
    let order = null;

    if (trimmedOrder) {
      if (!/^\d+$/.test(trimmedOrder)) {
        setBreakingOrderError('Enter a whole number like 1, 2, or 3.');
        return;
      }
      order = Number.parseInt(trimmedOrder, 10);
      if (order < 1) {
        setBreakingOrderError('Order must be 1 or greater.');
        return;
      }
    }

    try {
      setActionLoading(true);
      setBreakingOrderError('');
      await setBreakingNews(selectedPost.uuid, true, order);
      setBreakingDialogOpen(false);
      setBreakingOrderInput('');
      setSelectedPost(null);
      fetchPosts();
    } catch (err) {
      console.error('Failed to update breaking news:', err);
      setError(getApiErrorMessage(err, 'Failed to update breaking news'));
    } finally {
      setActionLoading(false);
    }
  };

  const handleOverrideDialogSubmit = async () => {
    if (!selectedPost) return;

    const trimmedReason = overrideReason.trim();
    if (!trimmedReason) {
      setOverrideReasonError('Please explain why this post should be approved.');
      return;
    }

    try {
      setActionLoading(true);
      setOverrideReasonError('');
      await approvePostQualityOverride(selectedPost.uuid, trimmedReason);
      setOverrideDialogOpen(false);
      setOverrideReason('');
      setSelectedPost(null);
      fetchPosts();
    } catch (err) {
      console.error('Failed to approve override:', err);
      setError(getApiErrorMessage(err, 'Failed to approve quality override'));
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

  const getQualityChip = (post) => {
    const status = intelligenceStatuses[post.uuid];
    const quality = status?.quality_status || 'not_checked';
    const labels = {
      not_checked: 'Not Checked',
      passed: 'Passed',
      needs_review: 'Needs Review',
      blocked: 'Blocked',
    };
    const colors = {
      not_checked: 'default',
      passed: 'success',
      needs_review: 'warning',
      blocked: 'error',
    };
    return (
      <Stack spacing={0.5} alignItems="flex-start">
        <Chip
          label={labels[quality] || quality}
          size="small"
          color={colors[quality] || 'default'}
          variant={quality === 'not_checked' ? 'outlined' : 'filled'}
        />
        {status?.distribution_pending > 0 && (
          <Typography variant="caption" color="text.secondary">
            {status.distribution_pending} assets pending
          </Typography>
        )}
      </Stack>
    );
  };

  return (
    <Box>
      {/* Header */}
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} justifyContent="space-between" alignItems={{ xs: 'stretch', sm: 'center' }} sx={{ mb: 3 }}>
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

      {/* Error Alert */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Posts Table */}
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Post</TableCell>
                <TableCell>Status</TableCell>
                {isAdminOrMod(user) && <TableCell>Quality</TableCell>}
                {!isMobile && <TableCell>Views</TableCell>}
                {!isMobile && <TableCell>Date</TableCell>}
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
                    {isAdminOrMod(user) && <TableCell><Skeleton width={90} /></TableCell>}
                    {!isMobile && <TableCell><Skeleton width={50} /></TableCell>}
                    {!isMobile && <TableCell><Skeleton width={100} /></TableCell>}
                    <TableCell><Skeleton width={40} /></TableCell>
                  </TableRow>
                ))
              ) : error ? (
                <TableRow>
                  <TableCell colSpan={isAdminOrMod(user) ? 6 : 5} align="center" sx={{ py: 4 }}>
                    <Typography color="error">{error}</Typography>
                    <Button onClick={fetchPosts} sx={{ mt: 1 }}>Try Again</Button>
                  </TableCell>
                </TableRow>
              ) : posts.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={isAdminOrMod(user) ? 6 : 5} align="center" sx={{ py: 6 }}>
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
                          <Typography variant="body2" fontWeight={500} noWrap sx={{ maxWidth: { xs: 160, sm: 200, md: 280 } }}>
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
                      {post.is_featured && (
                        <Chip
                          label="Featured"
                          size="small"
                          color="warning"
                          variant="filled"
                          icon={<IconStar size={14} />}
                        />
                      )}
                      {post.is_homepage_trending && (
                        <Chip
                          label={`Trending #${post.homepage_trending_order || ''}`.trim()}
                          size="small"
                          color="error"
                          variant="filled"
                          icon={<IconFlame size={14} />}
                        />
                      )}
                      {post.is_breaking_news && (
                        <Chip
                          label={`Breaking #${post.breaking_news_order || ''}`.trim()}
                          size="small"
                          color="primary"
                          variant="filled"
                          icon={<IconBolt size={14} />}
                        />
                      )}
                    </TableCell>
                    {isAdminOrMod(user) && (
                      <TableCell>
                        {getQualityChip(post)}
                      </TableCell>
                    )}
                    {!isMobile && (
                      <TableCell>
                        <Typography variant="body2">{post.view_count || 0}</Typography>
                      </TableCell>
                    )}
                    {!isMobile && (
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {formatDate(post.published_at || post.created_at)}
                        </Typography>
                      </TableCell>
                    )}
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
        {CONTENT_INTELLIGENCE_ENABLED && isAdminOrMod(user) && (
          <MenuItem onClick={handleRunQuality} disabled={actionLoading}>
            Run Quality Check
          </MenuItem>
        )}
        {CONTENT_INTELLIGENCE_ENABLED && isAdminOrMod(user) && (
          <MenuItem onClick={handleGenerateDistribution} disabled={actionLoading}>
            Generate Distribution
          </MenuItem>
        )}
        {CONTENT_INTELLIGENCE_ENABLED && isAdminOrMod(user) && intelligenceStatuses[selectedPost?.uuid]?.distribution_pending > 0 && (
          <MenuItem onClick={handleApproveAssets} disabled={actionLoading}>
            Approve Assets
          </MenuItem>
        )}
        {CONTENT_INTELLIGENCE_ENABLED && isAdminOrMod(user) && intelligenceStatuses[selectedPost?.uuid]?.quality_status === 'needs_review' && (
          <MenuItem onClick={handleApproveOverride} disabled={actionLoading}>
            Approve Override
          </MenuItem>
        )}
        {isAdminOrMod(user) && selectedPost?.is_published && (
          <MenuItem onClick={handleFeatureToggle} disabled={actionLoading}>
            <ListItemIcon>
              {selectedPost?.is_featured ? <IconStarOff size={18} /> : <IconStar size={18} />}
            </ListItemIcon>
            {selectedPost?.is_featured ? 'Unfeature' : 'Feature'}
          </MenuItem>
        )}
        {isAdminOrMod(user) && selectedPost?.is_published && (
          <MenuItem onClick={handleHomepageTrendingToggle} disabled={actionLoading}>
            <ListItemIcon>
              <IconFlame size={18} />
            </ListItemIcon>
            {selectedPost?.is_homepage_trending ? 'Remove from Trending' : 'Add to Trending'}
          </MenuItem>
        )}
        {isAdminOrMod(user) && selectedPost?.is_published && (
          <MenuItem onClick={handleBreakingNewsToggle} disabled={actionLoading}>
            <ListItemIcon>
              <IconBolt size={18} />
            </ListItemIcon>
            {selectedPost?.is_breaking_news ? 'Remove from Breaking' : 'Mark as Breaking'}
          </MenuItem>
        )}
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

      <Dialog
        open={breakingDialogOpen}
        onClose={closeBreakingDialog}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>Mark As Breaking</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Choose where this story should appear in the breaking list. Leave it blank to add it at the end.
            </Typography>
            <TextField
              label="Breaking order"
              placeholder="Append to end"
              value={breakingOrderInput}
              onChange={(event) => {
                setBreakingOrderInput(event.target.value);
                if (breakingOrderError) {
                  setBreakingOrderError('');
                }
              }}
              type="number"
              inputProps={{ min: 1, step: 1 }}
              error={Boolean(breakingOrderError)}
              helperText={breakingOrderError || 'Use 1 to pin it at the top, 2 for second, and so on.'}
              autoFocus
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeBreakingDialog} disabled={actionLoading}>
            Cancel
          </Button>
          <Button
            onClick={handleBreakingDialogSubmit}
            variant="contained"
            disabled={actionLoading}
          >
            {actionLoading ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={overrideDialogOpen}
        onClose={closeOverrideDialog}
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle>Approve Override</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Add a short reason for approving this post even though the quality review flagged it.
            </Typography>
            <TextField
              label="Approval reason"
              value={overrideReason}
              onChange={(event) => {
                setOverrideReason(event.target.value);
                if (overrideReasonError) {
                  setOverrideReasonError('');
                }
              }}
              error={Boolean(overrideReasonError)}
              helperText={overrideReasonError}
              multiline
              minRows={3}
              autoFocus
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeOverrideDialog} disabled={actionLoading}>
            Cancel
          </Button>
          <Button
            onClick={handleOverrideDialogSubmit}
            variant="contained"
            disabled={actionLoading}
          >
            {actionLoading ? 'Saving...' : 'Approve'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
