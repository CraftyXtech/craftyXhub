import { useState, useEffect, useCallback, useMemo } from 'react';
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
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Skeleton from '@mui/material/Skeleton';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Chip from '@mui/material/Chip';

// Icons
import {
  IconPlus,
  IconEdit,
  IconTrash,
  IconRefresh,
  IconCategory,
  IconChevronRight
} from '@tabler/icons-react';

// API
import { getCategories, createCategory, updateCategory, deleteCategory } from '@/api/services/categoryService';

/**
 * Category Management Page (Admin Only)
 */
export default function Categories() {
  // State
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Form
  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: { name: '', slug: '', description: '', parent_id: '' }
  });

  // Get parent categories (those without parent_id)
  const parentCategories = useMemo(() => {
    return categories.filter(cat => !cat.parent_id);
  }, [categories]);

  // Build hierarchical category list for display
  const hierarchicalCategories = useMemo(() => {
    const result = [];
    parentCategories.forEach(parent => {
      result.push({ ...parent, isParent: true });
      const subcategories = categories.filter(cat => cat.parent_id === parent.id);
      subcategories.forEach(sub => {
        result.push({ ...sub, isParent: false });
      });
    });
    // Add any orphaned categories (parent_id references deleted category)
    const displayedIds = new Set(result.map(c => c.id));
    categories.filter(cat => !displayedIds.has(cat.id)).forEach(cat => {
      result.push({ ...cat, isParent: !cat.parent_id });
    });
    return result;
  }, [categories, parentCategories]);

  // Fetch categories
  const fetchCategories = useCallback(async () => {
    try {
      setLoading(true);
      const response = await getCategories();
      setCategories(response.categories || response || []);
    } catch (err) {
      console.error('Failed to fetch categories:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  // Open dialog for create/edit
  const handleOpenDialog = (category = null) => {
    setSelectedCategory(category);
    if (category) {
      reset({ 
        name: category.name, 
        slug: category.slug, 
        description: category.description || '',
        parent_id: category.parent_id || ''
      });
    } else {
      reset({ name: '', slug: '', description: '', parent_id: '' });
    }
    setDialogOpen(true);
  };

  // Submit form
  const onSubmit = async (data) => {
    try {
      setActionLoading(true);
      // Convert empty parent_id to null
      const payload = {
        ...data,
        parent_id: data.parent_id || null
      };
      if (selectedCategory) {
        await updateCategory(selectedCategory.id, payload);
      } else {
        await createCategory(payload);
      }
      setDialogOpen(false);
      fetchCategories();
    } catch (err) {
      console.error('Failed to save category:', err);
    } finally {
      setActionLoading(false);
    }
  };

  // Delete
  const handleDeleteClick = (category) => {
    setSelectedCategory(category);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!selectedCategory) return;
    try {
      setActionLoading(true);
      await deleteCategory(selectedCategory.id);
      setDeleteDialogOpen(false);
      fetchCategories();
    } catch (err) {
      console.error('Failed to delete category:', err);
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
            Categories
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage post categories
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <IconButton onClick={fetchCategories} disabled={loading}>
            <IconRefresh size={20} />
          </IconButton>
          <Button
            variant="contained"
            startIcon={<IconPlus size={18} />}
            onClick={() => handleOpenDialog()}
            sx={{ borderRadius: 2 }}
          >
            Add Category
          </Button>
        </Stack>
      </Stack>

      {/* Categories Table */}
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Slug</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Posts</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                [...Array(4)].map((_, i) => (
                  <TableRow key={i}>
                    <TableCell><Skeleton width={120} /></TableCell>
                    <TableCell><Skeleton width={100} /></TableCell>
                    <TableCell><Skeleton width={80} /></TableCell>
                    <TableCell><Skeleton width={40} /></TableCell>
                    <TableCell><Skeleton width={60} /></TableCell>
                  </TableRow>
                ))
              ) : hierarchicalCategories.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 6 }}>
                    <IconCategory size={48} color="#9E9E9E" style={{ marginBottom: 8 }} />
                    <Typography color="text.secondary">No categories yet</Typography>
                    <Button onClick={() => handleOpenDialog()} sx={{ mt: 1 }}>
                      Create First Category
                    </Button>
                  </TableCell>
                </TableRow>
              ) : (
                hierarchicalCategories.map((category) => (
                  <TableRow key={category.id} hover>
                    <TableCell>
                      <Stack direction="row" alignItems="center" spacing={1}>
                        {!category.isParent && (
                          <IconChevronRight size={16} color="#9E9E9E" style={{ marginLeft: 16 }} />
                        )}
                        <Typography 
                          variant="body2" 
                          fontWeight={category.isParent ? 600 : 400}
                          color={category.isParent ? 'text.primary' : 'text.secondary'}
                        >
                          {category.name}
                        </Typography>
                      </Stack>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">{category.slug}</Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={category.isParent ? 'Category' : 'Subcategory'} 
                        size="small" 
                        color={category.isParent ? 'primary' : 'default'}
                        variant={category.isParent ? 'filled' : 'outlined'}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{category.post_count || 0}</Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                        <IconButton size="small" onClick={() => handleOpenDialog(category)}>
                          <IconEdit size={18} />
                        </IconButton>
                        <IconButton size="small" color="error" onClick={() => handleDeleteClick(category)}>
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
      </Card>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{selectedCategory ? 'Edit Category' : 'Create Category'}</DialogTitle>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogContent>
            <Stack spacing={2.5}>
              <Controller
                name="parent_id"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>Parent Category (Optional)</InputLabel>
                    <Select
                      {...field}
                      label="Parent Category (Optional)"
                      value={field.value || ''}
                    >
                      <MenuItem value="">
                        <em>None (Top-level Category)</em>
                      </MenuItem>
                      {parentCategories
                        .filter(cat => !selectedCategory || cat.id !== selectedCategory.id)
                        .map(cat => (
                          <MenuItem key={cat.id} value={cat.id}>
                            {cat.name}
                          </MenuItem>
                        ))
                      }
                    </Select>
                  </FormControl>
                )}
              />
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
                rules={{ required: 'Slug is required' }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Slug"
                    fullWidth
                    error={Boolean(errors.slug)}
                    helperText={errors.slug?.message || 'URL-friendly identifier'}
                  />
                )}
              />
              <Controller
                name="description"
                control={control}
                render={({ field }) => (
                  <TextField {...field} label="Description" multiline rows={2} fullWidth />
                )}
              />
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained" disabled={actionLoading}>
              {actionLoading ? 'Saving...' : selectedCategory ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Category?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{selectedCategory?.name}"? Posts in this category will become uncategorized.
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
