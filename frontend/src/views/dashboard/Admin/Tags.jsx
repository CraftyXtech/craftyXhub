import { useState, useEffect, useCallback } from 'react';
import { useForm, Controller } from 'react-hook-form';

// MUI
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Chip from '@mui/material/Chip';
import Grid from '@mui/material/Grid';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Skeleton from '@mui/material/Skeleton';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Divider from '@mui/material/Divider';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';

// Icons
import {
  IconPlus,
  IconEdit,
  IconTrash,
  IconRefresh,
  IconTag,
  IconChevronDown
} from '@tabler/icons-react';

// API
import { getTags, getTagsGrouped, createTag, updateTag, deleteTag } from '@/api/services/tagService';
import { getCategories } from '@/api/services/categoryService';

/**
 * Tag Management Page (Admin Only)
 */
export default function Tags() {
  // State
  const [tags, setTags] = useState([]);
  const [groupedTags, setGroupedTags] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedTag, setSelectedTag] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [viewMode, setViewMode] = useState('grouped'); // 'flat' or 'grouped'

  // Form
  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: { name: '', slug: '', category_id: '' }
  });

  // Fetch tags and categories
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const [tagsRes, groupedRes, catsRes] = await Promise.all([
        getTags(),
        getTagsGrouped(),
        getCategories()
      ]);
      setTags(tagsRes.tags || tagsRes || []);
      setGroupedTags(groupedRes.groups || []);
      // Only include parent categories for selection
      const parentCats = (catsRes.categories || catsRes || []).filter(c => !c.parent_id);
      setCategories(parentCats);
    } catch (err) {
      console.error('Failed to fetch data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Open dialog
  const handleOpenDialog = (tag = null) => {
    setSelectedTag(tag);
    reset(tag ? { name: tag.name, slug: tag.slug, category_id: tag.category_id || '' } : { name: '', slug: '', category_id: '' });
    setDialogOpen(true);
  };

  // Submit
  const onSubmit = async (data) => {
    try {
      setActionLoading(true);
      const payload = {
        ...data,
        category_id: data.category_id || null
      };
      if (selectedTag) {
        await updateTag(selectedTag.id, payload);
      } else {
        await createTag(payload);
      }
      setDialogOpen(false);
      fetchData();
    } catch (err) {
      console.error('Failed to save tag:', err);
    } finally {
      setActionLoading(false);
    }
  };

  // Delete
  const handleDeleteClick = (tag) => {
    setSelectedTag(tag);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!selectedTag) return;
    try {
      setActionLoading(true);
      await deleteTag(selectedTag.id);
      setDeleteDialogOpen(false);
      fetchData();
    } catch (err) {
      console.error('Failed to delete tag:', err);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Box>
          <Typography variant="h5" fontWeight={600}>
            Tags
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage post tags ({tags.length} total)
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button
            variant={viewMode === 'grouped' ? 'contained' : 'outlined'}
            size="small"
            onClick={() => setViewMode('grouped')}
          >
            Grouped
          </Button>
          <Button
            variant={viewMode === 'flat' ? 'contained' : 'outlined'}
            size="small"
            onClick={() => setViewMode('flat')}
          >
            All Tags
          </Button>
          <IconButton onClick={fetchData} disabled={loading}>
            <IconRefresh size={20} />
          </IconButton>
          <Button
            variant="contained"
            startIcon={<IconPlus size={18} />}
            onClick={() => handleOpenDialog()}
            sx={{ borderRadius: 2 }}
          >
            Add Tag
          </Button>
        </Stack>
      </Stack>

      {/* Tags Display */}
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
        <CardContent>
          {loading ? (
            <Stack spacing={2}>
              {[...Array(4)].map((_, i) => (
                <Skeleton key={i} height={60} sx={{ borderRadius: 1 }} />
              ))}
            </Stack>
          ) : tags.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 6 }}>
              <IconTag size={48} color="#9E9E9E" style={{ marginBottom: 8 }} />
              <Typography color="text.secondary">No tags yet</Typography>
              <Button onClick={() => handleOpenDialog()} sx={{ mt: 1 }}>
                Create First Tag
              </Button>
            </Box>
          ) : viewMode === 'grouped' ? (
            /* Grouped View */
            <Stack spacing={1}>
              {groupedTags.map((group) => (
                <Accordion key={group.category_id} defaultExpanded={false}>
                  <AccordionSummary expandIcon={<IconChevronDown size={20} />}>
                    <Typography fontWeight={600}>
                      {group.category_name} ({group.tags.length} tags)
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={1}>
                      {group.tags.map((tag) => (
                        <Grid item key={tag.id}>
                          <Chip
                            label={tag.name}
                            onDelete={() => handleDeleteClick(tag)}
                            onClick={() => handleOpenDialog(tag)}
                            sx={{ cursor: 'pointer' }}
                          />
                        </Grid>
                      ))}
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Stack>
          ) : (
            /* Flat View */
            <Grid container spacing={1}>
              {tags.map((tag) => (
                <Grid item key={tag.id}>
                  <Chip
                    label={`${tag.name} (${tag.post_count || 0})`}
                    onDelete={() => handleDeleteClick(tag)}
                    onClick={() => handleOpenDialog(tag)}
                    sx={{ cursor: 'pointer' }}
                  />
                </Grid>
              ))}
            </Grid>
          )}
        </CardContent>
      </Card>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>{selectedTag ? 'Edit Tag' : 'Create Tag'}</DialogTitle>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogContent>
            <Stack spacing={2}>
              <Controller
                name="name"
                control={control}
                rules={{ required: 'Name is required' }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Name"
                    fullWidth
                    error={Boolean(errors.name)}
                    helperText={errors.name?.message}
                  />
                )}
              />
              <Controller
                name="slug"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Slug"
                    fullWidth
                    helperText="Leave empty to auto-generate"
                  />
                )}
              />
              <Controller
                name="category_id"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>Category (for grouping)</InputLabel>
                    <Select
                      {...field}
                      label="Category (for grouping)"
                    >
                      <MenuItem value="">
                        <em>None</em>
                      </MenuItem>
                      {categories.map((cat) => (
                        <MenuItem key={cat.id} value={cat.id}>
                          {cat.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}
              />
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained" disabled={actionLoading}>
              {selectedTag ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Tag?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{selectedTag?.name}"?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained" disabled={actionLoading}>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
