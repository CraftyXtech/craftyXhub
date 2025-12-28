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
import Skeleton from '@mui/material/Skeleton';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';

// Icons
import {
  IconFlag,
  IconCheck,
  IconTrash,
  IconRefresh,
  IconEye
} from '@tabler/icons-react';

// API (assuming these exist or will be created)
import { axiosPrivate } from '@/api/axios';

// Mock API functions (replace with actual service when available)
const getReports = async (params) => {
  try {
    const response = await axiosPrivate.get('/posts/reports', { params });
    return response.data;
  } catch {
    return { reports: [], total: 0 };
  }
};

const dismissReport = async (reportId) => {
  return axiosPrivate.put(`/posts/reports/${reportId}/dismiss`);
};

const removePost = async (postId) => {
  return axiosPrivate.delete(`/posts/${postId}`);
};

/**
 * Post Reports Page
 * Review reported posts
 */
export default function Reports() {
  // State
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [selectedReport, setSelectedReport] = useState(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  // Fetch reports
  const fetchReports = useCallback(async () => {
    try {
      setLoading(true);
      const response = await getReports({
        page: page + 1,
        limit: rowsPerPage
      });
      setReports(response.reports || response.items || []);
      setTotal(response.total || 0);
    } catch (err) {
      console.error('Failed to fetch reports:', err);
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage]);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  // Actions
  const handleDismiss = async (report) => {
    try {
      setActionLoading(true);
      await dismissReport(report.id);
      fetchReports();
    } catch (err) {
      console.error('Failed to dismiss:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleRemovePost = async () => {
    if (!selectedReport?.post?.uuid) return;
    try {
      setActionLoading(true);
      await removePost(selectedReport.post.uuid);
      setViewDialogOpen(false);
      setSelectedReport(null);
      fetchReports();
    } catch (err) {
      console.error('Failed to remove post:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleViewReport = (report) => {
    setSelectedReport(report);
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

  // Report reason colors
  const getReasonColor = (reason) => {
    const colors = {
      spam: 'warning',
      offensive: 'error',
      copyright: 'info',
      other: 'default'
    };
    return colors[reason?.toLowerCase()] || 'default';
  };

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h5" fontWeight={600}>
            Post Reports
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Review reported content
          </Typography>
        </Box>
        <IconButton onClick={fetchReports} disabled={loading}>
          <IconRefresh size={20} />
        </IconButton>
      </Stack>

      {/* Reports Table */}
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Post</TableCell>
                <TableCell>Reason</TableCell>
                <TableCell>Reporter</TableCell>
                <TableCell>Date</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <TableRow key={i}>
                    <TableCell><Skeleton width={200} /></TableCell>
                    <TableCell><Skeleton width={80} /></TableCell>
                    <TableCell><Skeleton width={100} /></TableCell>
                    <TableCell><Skeleton width={100} /></TableCell>
                    <TableCell><Skeleton width={80} /></TableCell>
                  </TableRow>
                ))
              ) : reports.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 6 }}>
                    <IconFlag size={48} color="#9E9E9E" style={{ marginBottom: 8 }} />
                    <Typography color="text.secondary">
                      No reported posts
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                reports.map((report) => (
                  <TableRow key={report.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight={500} noWrap sx={{ maxWidth: 220 }}>
                        {report.post?.title || 'Unknown Post'}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        by {report.post?.author?.username || 'Unknown'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={report.reason || 'Other'}
                        size="small"
                        color={getReasonColor(report.reason)}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {report.reporter?.username || 'Anonymous'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption" color="text.secondary">
                        {formatDate(report.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                        <IconButton
                          size="small"
                          onClick={() => handleViewReport(report)}
                        >
                          <IconEye size={18} />
                        </IconButton>
                        <IconButton
                          size="small"
                          color="success"
                          onClick={() => handleDismiss(report)}
                          disabled={actionLoading}
                          title="Dismiss report"
                        >
                          <IconCheck size={18} />
                        </IconButton>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        {!loading && reports.length > 0 && (
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

      {/* View Report Dialog */}
      <Dialog open={viewDialogOpen} onClose={() => setViewDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Report Details</DialogTitle>
        <DialogContent>
          <Typography variant="subtitle2" gutterBottom>Post Title</Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            {selectedReport?.post?.title || 'Unknown'}
          </Typography>
          
          <Typography variant="subtitle2" gutterBottom>Reason</Typography>
          <Chip
            label={selectedReport?.reason || 'Other'}
            size="small"
            color={getReasonColor(selectedReport?.reason)}
            sx={{ mb: 2 }}
          />
          
          <Typography variant="subtitle2" gutterBottom>Details</Typography>
          <Typography variant="body2" sx={{ mb: 2, whiteSpace: 'pre-wrap' }}>
            {selectedReport?.details || 'No additional details provided'}
          </Typography>
          
          <Typography variant="subtitle2" gutterBottom>Reported By</Typography>
          <Typography variant="body2" color="text.secondary">
            {selectedReport?.reporter?.username || 'Anonymous'} on {formatDate(selectedReport?.created_at)}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
          <Button
            onClick={() => handleDismiss(selectedReport)}
            color="success"
            disabled={actionLoading}
          >
            Dismiss Report
          </Button>
          <Button
            onClick={handleRemovePost}
            color="error"
            variant="contained"
            disabled={actionLoading}
          >
            Remove Post
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
