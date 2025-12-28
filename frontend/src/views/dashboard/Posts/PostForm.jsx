import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';

// MUI
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import Grid from '@mui/material/Grid';
import FormControl from '@mui/material/FormControl';
import FormHelperText from '@mui/material/FormHelperText';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Chip from '@mui/material/Chip';
import IconButton from '@mui/material/IconButton';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';

// Icons
import {
  IconArrowLeft,
  IconDeviceFloppy,
  IconSend,
  IconPhoto,
  IconX
} from '@tabler/icons-react';

// API
import { createPost, updatePost, getPost, getImageUrl } from '@/api/services/postService';
import { getCategories } from '@/api/services/categoryService';
import { getTags } from '@/api/services/tagService';

/**
 * Post Create/Edit Form
 */
export default function PostForm() {
  const navigate = useNavigate();
  const { id } = useParams(); // Post UUID for editing
  const isEditing = Boolean(id);

  // State
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);
  const [featuredImage, setFeaturedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  // Form
  const { control, handleSubmit, reset, watch, setValue, formState: { errors } } = useForm({
    defaultValues: {
      title: '',
      slug: '',
      content: '',
      excerpt: '',
      category_id: '',
      tag_ids: [],
      meta_title: '',
      meta_description: '',
      is_published: false
    }
  });

  const title = watch('title');

  // Auto-generate slug from title
  useEffect(() => {
    if (!isEditing && title) {
      const slug = title
        .toLowerCase()
        .replace(/[^\w\s-]/g, '')
        .replace(/\s+/g, '-')
        .slice(0, 100);
      setValue('slug', slug);
    }
  }, [title, isEditing, setValue]);

  // Load categories and tags
  useEffect(() => {
    const loadData = async () => {
      try {
        const [catRes, tagRes] = await Promise.all([
          getCategories(),
          getTags()
        ]);
        setCategories(catRes.categories || catRes || []);
        setTags(tagRes.tags || tagRes || []);
      } catch (err) {
        console.error('Failed to load categories/tags:', err);
      }
    };
    loadData();
  }, []);

  // Load post for editing
  useEffect(() => {
    if (isEditing && id) {
      const loadPost = async () => {
        try {
          setLoading(true);
          const post = await getPost(id);
          reset({
            title: post.title || '',
            slug: post.slug || '',
            content: post.content || '',
            excerpt: post.excerpt || '',
            category_id: post.category?.id || post.category_id || '',
            tag_ids: post.tags?.map(t => t.id) || [],
            meta_title: post.meta_title || '',
            meta_description: post.meta_description || '',
            is_published: post.is_published || false
          });
          if (post.featured_image) {
            setImagePreview(getImageUrl(post.featured_image));
          }
        } catch (err) {
          console.error('Failed to load post:', err);
          setError('Failed to load post');
        } finally {
          setLoading(false);
        }
      };
      loadPost();
    }
  }, [id, isEditing, reset]);

  // Handle image upload
  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setFeaturedImage(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleImageRemove = () => {
    setFeaturedImage(null);
    setImagePreview(null);
  };

  // Submit form
  const onSubmit = async (data, shouldPublish = false) => {
    try {
      setSaving(true);
      setError(null);

      const formData = new FormData();
      formData.append('title', data.title);
      formData.append('slug', data.slug);
      formData.append('content', data.content);
      formData.append('excerpt', data.excerpt || '');
      formData.append('meta_title', data.meta_title || '');
      formData.append('meta_description', data.meta_description || '');
      formData.append('is_published', shouldPublish ? 'true' : data.is_published ? 'true' : 'false');
      
      if (data.category_id) {
        formData.append('category_id', data.category_id);
      }
      if (data.tag_ids?.length) {
        formData.append('tag_ids', data.tag_ids.join(','));
      }
      if (featuredImage) {
        formData.append('featured_image', featuredImage);
      }

      if (isEditing) {
        await updatePost(id, formData);
      } else {
        await createPost(formData);
      }

      navigate('/dashboard/posts');
    } catch (err) {
      console.error('Failed to save post:', err);
      setError(err.response?.data?.detail || 'Failed to save post');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveDraft = handleSubmit((data) => onSubmit(data, false));
  const handlePublish = handleSubmit((data) => onSubmit(data, true));

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 3 }}>
        <IconButton onClick={() => navigate('/dashboard/posts')}>
          <IconArrowLeft size={20} />
        </IconButton>
        <Typography variant="h5" fontWeight={600}>
          {isEditing ? 'Edit Post' : 'Create New Post'}
        </Typography>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Main Content */}
        <Grid item xs={12} md={8}>
          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
            <CardContent>
              <Stack spacing={3}>
                {/* Title */}
                <Controller
                  name="title"
                  control={control}
                  rules={{ required: 'Title is required' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Title"
                      fullWidth
                      error={Boolean(errors.title)}
                      helperText={errors.title?.message}
                    />
                  )}
                />

                {/* Slug */}
                <Controller
                  name="slug"
                  control={control}
                  rules={{ required: 'Slug is required' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="URL Slug"
                      fullWidth
                      error={Boolean(errors.slug)}
                      helperText={errors.slug?.message || 'e.g., my-awesome-post'}
                    />
                  )}
                />

                {/* Content */}
                <Controller
                  name="content"
                  control={control}
                  rules={{ required: 'Content is required' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Content"
                      multiline
                      rows={12}
                      fullWidth
                      error={Boolean(errors.content)}
                      helperText={errors.content?.message || 'Write your post content here. HTML supported.'}
                    />
                  )}
                />

                {/* Excerpt */}
                <Controller
                  name="excerpt"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Excerpt"
                      multiline
                      rows={3}
                      fullWidth
                      helperText="Brief summary shown in post listings"
                    />
                  )}
                />
              </Stack>
            </CardContent>
          </Card>

          {/* SEO Section */}
          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', mt: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                SEO Settings
              </Typography>
              <Stack spacing={2}>
                <Controller
                  name="meta_title"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Meta Title" fullWidth size="small" />
                  )}
                />
                <Controller
                  name="meta_description"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Meta Description" multiline rows={2} fullWidth size="small" />
                  )}
                />
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          {/* Publish */}
          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', mb: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                Publish
              </Typography>
              <Stack spacing={2}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<IconDeviceFloppy size={18} />}
                  onClick={handleSaveDraft}
                  disabled={saving}
                >
                  {saving ? 'Saving...' : 'Save Draft'}
                </Button>
                <Button
                  variant="contained"
                  fullWidth
                  startIcon={<IconSend size={18} />}
                  onClick={handlePublish}
                  disabled={saving}
                >
                  {saving ? 'Publishing...' : isEditing ? 'Update & Publish' : 'Publish'}
                </Button>
              </Stack>
            </CardContent>
          </Card>

          {/* Featured Image */}
          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', mb: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                Featured Image
              </Typography>
              
              {imagePreview ? (
                <Box sx={{ position: 'relative' }}>
                  <Box
                    component="img"
                    src={imagePreview}
                    sx={{ width: '100%', borderRadius: 1 }}
                  />
                  <IconButton
                    size="small"
                    onClick={handleImageRemove}
                    sx={{
                      position: 'absolute',
                      top: 8,
                      right: 8,
                      bgcolor: 'background.paper',
                      boxShadow: 1
                    }}
                  >
                    <IconX size={16} />
                  </IconButton>
                </Box>
              ) : (
                <Button
                  variant="outlined"
                  component="label"
                  fullWidth
                  startIcon={<IconPhoto size={18} />}
                  sx={{ py: 3 }}
                >
                  Upload Image
                  <input type="file" hidden accept="image/*" onChange={handleImageChange} />
                </Button>
              )}
            </CardContent>
          </Card>

          {/* Category & Tags */}
          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                Categories & Tags
              </Typography>
              <Stack spacing={2}>
                <Controller
                  name="category_id"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth size="small">
                      <InputLabel>Category</InputLabel>
                      <Select {...field} label="Category">
                        <MenuItem value="">None</MenuItem>
                        {categories.map((cat) => (
                          <MenuItem key={cat.id} value={cat.id}>{cat.name}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  )}
                />

                <Controller
                  name="tag_ids"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth size="small">
                      <InputLabel>Tags</InputLabel>
                      <Select
                        {...field}
                        multiple
                        label="Tags"
                        renderValue={(selected) => (
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {selected.map((id) => {
                              const tag = tags.find(t => t.id === id);
                              return <Chip key={id} label={tag?.name || id} size="small" />;
                            })}
                          </Box>
                        )}
                      >
                        {tags.map((tag) => (
                          <MenuItem key={tag.id} value={tag.id}>{tag.name}</MenuItem>
                        ))}
                      </Select>
                      <FormHelperText>Select multiple tags</FormHelperText>
                    </FormControl>
                  )}
                />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
