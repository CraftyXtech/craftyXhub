import { useState, useEffect, useCallback, useRef } from 'react';

// MUI
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import Grid from '@mui/material/Grid';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';
import Skeleton from '@mui/material/Skeleton';
import Chip from '@mui/material/Chip';

// Icons
import {
  IconUpload,
  IconSearch,
  IconTrash,
  IconCopy,
  IconPhoto,
  IconRefresh,
  IconCheck
} from '@tabler/icons-react';

// API
import { uploadMedia, getUserMedia, deleteMedia, getMediaUrl } from '@/api/services/mediaService';

/**
 * Media Library Page
 */
export default function Media() {
  // State
  const [media, setMedia] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedMedia, setSelectedMedia] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const fileInputRef = useRef(null);

  // Fetch media
  const fetchMedia = useCallback(async () => {
    try {
      setLoading(true);
      const response = await getUserMedia();
      setMedia(response.items || response || []);
    } catch (err) {
      console.error('Failed to fetch media:', err);
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    fetchMedia();
  }, [fetchMedia]);

  // Handle upload
  const handleUpload = async (e) => {
    const files = e.target.files;
    if (!files?.length) return;

    try {
      setUploading(true);
      for (const file of files) {
        await uploadMedia(file);
      }
      fetchMedia();
    } catch (err) {
      console.error('Failed to upload:', err);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  // Handle delete
  const handleDelete = async () => {
    if (!selectedMedia) return;
    
    try {
      await deleteMedia(selectedMedia.id);
      setDeleteDialogOpen(false);
      setSelectedMedia(null);
      fetchMedia();
    } catch (err) {
      console.error('Failed to delete:', err);
    }
  };

  // Copy URL
  const handleCopyUrl = (item) => {
    const url = getMediaUrl(item.path || item.url);
    navigator.clipboard.writeText(url);
    setCopiedId(item.id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Format file size
  const formatSize = (bytes) => {
    if (!bytes) return '-';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h5" fontWeight={600}>
            Media Library
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage your uploaded images and files
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <IconButton onClick={fetchMedia} disabled={loading}>
            <IconRefresh size={20} />
          </IconButton>
          <Button
            variant="contained"
            startIcon={<IconUpload size={18} />}
            component="label"
            disabled={uploading}
            sx={{ borderRadius: 2 }}
          >
            {uploading ? 'Uploading...' : 'Upload'}
            <input
              ref={fileInputRef}
              type="file"
              hidden
              multiple
              accept="image/*"
              onChange={handleUpload}
            />
          </Button>
        </Stack>
      </Stack>

      {/* Search */}
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', mb: 3 }}>
        <CardContent sx={{ py: 2 }}>
          <TextField
            size="small"
            placeholder="Search media..."
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
        </CardContent>
      </Card>

      {/* Media Grid */}
      {loading ? (
        <Grid container spacing={2}>
          {[...Array(8)].map((_, i) => (
            <Grid item xs={6} sm={4} md={3} key={i}>
              <Skeleton variant="rounded" height={150} />
            </Grid>
          ))}
        </Grid>
      ) : media.length === 0 ? (
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', textAlign: 'center', py: 8 }}>
          <IconPhoto size={48} color="#9E9E9E" style={{ marginBottom: 16 }} />
          <Typography variant="h6" gutterBottom>No media yet</Typography>
          <Typography color="text.secondary" sx={{ mb: 3 }}>
            Upload images to start building your media library
          </Typography>
          <Button
            variant="contained"
            startIcon={<IconUpload size={18} />}
            component="label"
          >
            Upload Files
            <input
              type="file"
              hidden
              multiple
              accept="image/*"
              onChange={handleUpload}
            />
          </Button>
        </Card>
      ) : (
        <Grid container spacing={2}>
          {media.map((item) => (
            <Grid item xs={6} sm={4} md={3} key={item.id}>
              <Card
                elevation={0}
                sx={{
                  border: '1px solid',
                  borderColor: 'divider',
                  cursor: 'pointer',
                  transition: 'box-shadow 0.2s',
                  '&:hover': { boxShadow: 2 }
                }}
              >
                {/* Thumbnail */}
                <Box
                  sx={{
                    height: 140,
                    backgroundImage: `url(${getMediaUrl(item.path || item.url)})`,
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                    bgcolor: 'grey.100'
                  }}
                />
                
                {/* Info */}
                <CardContent sx={{ py: 1.5 }}>
                  <Typography variant="caption" noWrap display="block">
                    {item.filename || item.name}
                  </Typography>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Chip label={formatSize(item.size)} size="small" variant="outlined" />
                    <Stack direction="row" spacing={0.5}>
                      <IconButton
                        size="small"
                        onClick={() => handleCopyUrl(item)}
                        color={copiedId === item.id ? 'success' : 'default'}
                      >
                        {copiedId === item.id ? <IconCheck size={16} /> : <IconCopy size={16} />}
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => {
                          setSelectedMedia(item);
                          setDeleteDialogOpen(true);
                        }}
                        color="error"
                      >
                        <IconTrash size={16} />
                      </IconButton>
                    </Stack>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Delete Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Media?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this file? This cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error" variant="contained">Delete</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
