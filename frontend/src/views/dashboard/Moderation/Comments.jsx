import { useState, useEffect, useCallback } from 'react';

// MUI
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import TablePagination from '@mui/material/TablePagination';
import Chip from '@mui/material/Chip';
import Avatar from '@mui/material/Avatar';
import Skeleton from '@mui/material/Skeleton';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';

// Icons
import {
  IconCheck,
  IconX,
  IconTrash,
  IconRefresh,
  IconMessageCircle
} from '@tabler/icons-react';

// API
import { approveComment, deleteComment } from '@/api/services/commentService';
import { axiosPrivate } from '@/api/axios';

// Inline API functions for moderation (not in service yet)
const getPendingComments = async (params) => {
  try {
    const response = await axiosPrivate.get('/comments/moderation', { params });
    return response.data;
  } catch {
    return { comments: [], total: 0 };
  }
};

const rejectComment = async (commentId) => {
  return axiosPrivate.put(`/comments/${commentId}/reject`);
};
export default function Comments() {
  // State
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [selectedComment, setSelectedComment] = useState(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [tabValue, setTabValue] = useState(0);

  // Fetch comments
  const fetchComments = useCallback(async () => {
    try {
      setLoading(true);
      const status = tabValue === 0 ? 'pending' : tabValue === 1 ? 'approved' : 'rejected';
      const response = await getPendingComments({
        page: page + 1,
        limit: rowsPerPage,
        status
      });
      setComments(response.comments || response.items || []);
      setTotal(response.total || 0);
    } catch (err) {
      console.error('Failed to fetch comments:', err);
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, tabValue]);

  useEffect(() => {
    fetchComments();
  }, [fetchComments]);

  // Actions
  const handleApprove = async (comment) => {
    try {
      setActionLoading(true);
      await approveComment(comment.id);
      fetchComments();
    } catch (err) {
      console.error('Failed to approve:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async (comment) => {
    try {
      setActionLoading(true);
      await rejectComment(comment.id);
      fetchComments();
    } catch (err) {
      console.error('Failed to reject:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedComment) return;
    try {
      setActionLoading(true);
      await deleteComment(selectedComment.id);
      setViewDialogOpen(false);
      setSelectedComment(null);
      fetchComments();
    } catch (err) {
      console.error('Failed to delete:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleViewComment = (comment) => {
    setSelectedComment(comment);
    setViewDialogOpen(true);
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h5" fontWeight={600}>
            Comment Moderation
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Review and moderate user comments
          </Typography>
        </Box>
        <IconButton onClick={fetchComments} disabled={loading}>
          <IconRefresh size={20} />
        </IconButton>
      </Stack>

      {/* Tabs */}
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={(e, v) => { setTabValue(v); setPage(0); }}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="Pending" />
          <Tab label="Approved" />
          <Tab label="Rejected" />
        </Tabs>
      </Card>

      {/* Comments Table */}
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Author</TableCell>
                <TableCell>Comment</TableCell>
                <TableCell>Post</TableCell>
                <TableCell>Date</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <TableRow key={i}>
                    <TableCell><Skeleton width={120} /></TableCell>
                    <TableCell><Skeleton width={200} /></TableCell>
                    <TableCell><Skeleton width={150} /></TableCell>
                    <TableCell><Skeleton width={100} /></TableCell>
                    <TableCell><Skeleton width={80} /></TableCell>
                  </TableRow>
                ))
              ) : comments.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 6 }}>
                    <IconMessageCircle size={48} color="#9E9E9E" style={{ marginBottom: 8 }} />
                    <Typography color="text.secondary">
                      No {tabValue === 0 ? 'pending' : tabValue === 1 ? 'approved' : 'rejected'} comments
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                comments.map((comment) => (
                  <TableRow key={comment.id} hover>
                    <TableCell>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <Avatar sx={{ width: 32, height: 32 }}>
                          {comment.author?.username?.[0] || 'U'}
                        </Avatar>
                        <Typography variant="body2">{comment.author?.username || 'Anonymous'}</Typography>
                      </Stack>
                    </TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        sx={{
                          maxWidth: 250,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                          cursor: 'pointer'
                        }}
                        onClick={() => handleViewComment(comment)}
                      >
                        {comment.content}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary" noWrap sx={{ maxWidth: 150 }}>
                        {comment.post?.title || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption" color="text.secondary">
                        {formatDate(comment.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                        {tabValue === 0 && (
                          <>
                            <IconButton
                              size="small"
                              color="success"
                              onClick={() => handleApprove(comment)}
                              disabled={actionLoading}
                            >
                              <IconCheck size={18} />
                            </IconButton>
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleReject(comment)}
                              disabled={actionLoading}
                            >
                              <IconX size={18} />
                            </IconButton>
                          </>
                        )}
                        <IconButton
                          size="small"
                          onClick={() => handleViewComment(comment)}
                        >
                          <IconTrash size={18} />
                        </IconButton>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        {!loading && comments.length > 0 && (
          <TablePagination
            component="div"
            count={total}
            page={page}
            onPageChange={(e, p) => setPage(p)}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value, 10)); setPage(0); }}
            rowsPerPageOptions={[5, 10, 25]}
          />
        )}
      </Card>

      {/* View/Delete Dialog */}
      <Dialog open={viewDialogOpen} onClose={() => setViewDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Comment Details</DialogTitle>
        <DialogContent>
          <Typography variant="subtitle2" gutterBottom>Author</Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            {selectedComment?.author?.username || 'Anonymous'}
          </Typography>
          
          <Typography variant="subtitle2" gutterBottom>Comment</Typography>
          <Typography variant="body2" sx={{ mb: 2, whiteSpace: 'pre-wrap' }}>
            {selectedComment?.content}
          </Typography>
          
          <Typography variant="subtitle2" gutterBottom>On Post</Typography>
          <Typography variant="body2" color="text.secondary">
            {selectedComment?.post?.title || '-'}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
          <Button onClick={handleDelete} color="error" variant="contained" disabled={actionLoading}>
            Delete Comment
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
