import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

// MUI
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Chip from '@mui/material/Chip';
import IconButton from '@mui/material/IconButton';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';

// TinyMCE
import { Editor } from '@tinymce/tinymce-react';

// Import TinyMCE core and plugins
import 'tinymce/tinymce';
import 'tinymce/models/dom/model';
import 'tinymce/themes/silver';
import 'tinymce/icons/default';
import 'tinymce/skins/content/default/content';

// Icons
import {
  IconArrowLeft,
  IconDeviceFloppy,
  IconSend,
  IconPhoto,
  IconX,
} from '@tabler/icons-react';

// Components
import AiWriterPanel from '@/components/ai-writer/AiWriterPanel';

// API
import { createPost, updatePost, getPost, getImageUrl } from '@/api/services/postService';
import { getCategories } from '@/api/services/categoryService';
import { getTags } from '@/api/services/tagService';

// Utils
import { useTheme } from '@mui/material/styles';

/**
 * AdminPostEditor - TinyMCE editor with AI writing panel for admins/moderators
 */
export default function AdminPostEditor() {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditing = Boolean(id);
  const editorRef = useRef(null);
  const theme = useTheme();

  // State
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [editorReady, setEditorReady] = useState(false);

  // Form state
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [content, setContent] = useState('');
  const [excerpt, setExcerpt] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [selectedTags, setSelectedTags] = useState([]);
  const [metaTitle, setMetaTitle] = useState('');
  const [metaDescription, setMetaDescription] = useState('');
  const [featuredImage, setFeaturedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  // Data
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);

  // Stats
  const [wordCount, setWordCount] = useState(0);
  const [charCount, setCharCount] = useState(0);

  // Auto-generate slug
  useEffect(() => {
    if (!isEditing && title) {
      const newSlug = title
        .toLowerCase()
        .replace(/[^\w\s-]/g, '')
        .replace(/\s+/g, '-')
        .slice(0, 100);
      setSlug(newSlug);
    }
  }, [title, isEditing]);

  // Update stats when content changes
  useEffect(() => {
    const text = content.replace(/<[^>]*>/g, '');
    setCharCount(text.length);
    setWordCount(text.split(/\s+/).filter(w => w.length > 0).length);
  }, [content]);

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
        console.error('Failed to load data:', err);
      }
    };
    loadData();
  }, []);

  // Load post for editing
  useEffect(() => {
    if (isEditing && id && editorReady) {
      const loadPost = async () => {
        try {
          setLoading(true);
          const post = await getPost(id);
          
          setTitle(post.title || '');
          setSlug(post.slug || '');
          setContent(post.content || '');
          setExcerpt(post.excerpt || '');
          setCategoryId(post.category?.id || post.category_id || '');
          setSelectedTags(post.tags?.map(t => t.id) || []);
          setMetaTitle(post.meta_title || '');
          setMetaDescription(post.meta_description || '');
          
          if (editorRef.current) {
            editorRef.current.setContent(post.content || '');
          }
          
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
  }, [id, isEditing, editorReady]);

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

  // Handle AI content insert
  const handleAiInsert = useCallback((html) => {
    if (editorRef.current) {
      const currentContent = editorRef.current.getContent();
      const newContent = currentContent + (currentContent ? '<div></div>' : '') + html;
      editorRef.current.setContent(newContent);
      setContent(newContent);
    }
  }, []);

  // Submit form
  const handleSubmit = async (shouldPublish = false) => {
    try {
      setSaving(true);
      setError(null);

      if (!title.trim()) {
        setError('Title is required');
        return;
      }

      const currentContent = editorRef.current ? editorRef.current.getContent() : content;
      if (!currentContent.trim()) {
        setError('Content is required');
        return;
      }

      const formData = new FormData();
      formData.append('title', title);
      formData.append('slug', slug);
      formData.append('content', currentContent);
      formData.append('excerpt', excerpt || '');
      formData.append('meta_title', metaTitle || '');
      formData.append('meta_description', metaDescription || '');
      formData.append('is_published', shouldPublish ? 'true' : 'false');
      
      if (categoryId) {
        formData.append('category_id', categoryId);
      }
      if (selectedTags.length) {
        formData.append('tag_ids', selectedTags.join(','));
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
      console.error('Failed to save:', err);
      setError(err.response?.data?.detail || 'Failed to save post');
    } finally {
      setSaving(false);
    }
  };

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
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
        <Stack direction="row" alignItems="center" spacing={2}>
          <IconButton onClick={() => navigate('/dashboard/posts')}>
            <IconArrowLeft size={20} />
          </IconButton>
          <Box>
            <Typography variant="h5" fontWeight={600}>
              {isEditing ? 'Edit Post' : 'Create New Post'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Words: {wordCount} | Characters: {charCount}
            </Typography>
          </Box>
        </Stack>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            startIcon={saving ? <CircularProgress size={16} /> : <IconDeviceFloppy size={18} />}
            onClick={() => handleSubmit(false)}
            disabled={saving}
          >
            Save Draft
          </Button>
          <Button
            variant="contained"
            startIcon={saving ? <CircularProgress size={16} color="inherit" /> : <IconSend size={18} />}
            onClick={() => handleSubmit(true)}
            disabled={saving}
          >
            {isEditing ? 'Update & Publish' : 'Publish'}
          </Button>
        </Stack>
      </Stack>

      {/* Error */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Main Content */}
      <Grid container spacing={3} sx={{ minHeight: 'calc(100vh - 150px)' }}>
        {/* Editor Column */}
        <Grid item xs={12} lg={8}>
          <Stack spacing={3}>
            {/* Title */}
            <TextField
              label="Title"
              fullWidth
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />

            {/* Slug */}
            <TextField
              label="URL Slug"
              fullWidth
              value={slug}
              onChange={(e) => setSlug(e.target.value)}
              helperText="e.g., my-awesome-post"
            />

            {/* TinyMCE Editor */}
            <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
              <CardContent sx={{ p: 0, '&:last-child': { pb: 0 } }}>
                <Editor
                  licenseKey="gpl"
                  onInit={(evt, editor) => {
                    editorRef.current = editor;
                    setEditorReady(true);
                  }}
                  initialValue={content}
                  onEditorChange={(newContent) => setContent(newContent)}
                  init={{
                    height: 500,
                    menubar: false,
                    toolbar:
                      'undo redo | blocks | bold italic forecolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | link image',
                    content_style:
                      theme.palette.mode === 'dark'
                        ? 'body { font-family: "Open Sans", sans-serif; font-size: 14px; color: #fff; background-color: #1a1a1a; }'
                        : 'body { font-family: "Open Sans", sans-serif; font-size: 14px; color: #000; background-color: #fff; }',
                    branding: false,
                    directionality: 'ltr',
                    skin: 'oxide',
                  }}
                />
              </CardContent>
            </Card>

            {/* Excerpt */}
            <TextField
              label="Excerpt"
              multiline
              rows={3}
              fullWidth
              value={excerpt}
              onChange={(e) => setExcerpt(e.target.value)}
              helperText="Brief summary shown in post listings"
            />

            {/* SEO */}
            <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                  SEO Settings
                </Typography>
                <Stack spacing={2}>
                  <TextField
                    label="Meta Title"
                    fullWidth
                    size="small"
                    value={metaTitle}
                    onChange={(e) => setMetaTitle(e.target.value)}
                  />
                  <TextField
                    label="Meta Description"
                    multiline
                    rows={2}
                    fullWidth
                    size="small"
                    value={metaDescription}
                    onChange={(e) => setMetaDescription(e.target.value)}
                  />
                </Stack>
              </CardContent>
            </Card>

            {/* Sidebar stuff on small screens */}
            <Box sx={{ display: { xs: 'block', lg: 'none' } }}>
              <Grid container spacing={2}>
                {/* Featured Image */}
                <Grid item xs={12} sm={6}>
                  <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
                    <CardContent>
                      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                        Featured Image
                      </Typography>
                      {imagePreview ? (
                        <Box sx={{ position: 'relative' }}>
                          <Box component="img" src={imagePreview} sx={{ width: '100%', borderRadius: 1 }} />
                          <IconButton
                            size="small"
                            onClick={handleImageRemove}
                            sx={{ position: 'absolute', top: 8, right: 8, bgcolor: 'background.paper', boxShadow: 1 }}
                          >
                            <IconX size={16} />
                          </IconButton>
                        </Box>
                      ) : (
                        <Button variant="outlined" component="label" fullWidth startIcon={<IconPhoto size={18} />} sx={{ py: 3 }}>
                          Upload Image
                          <input type="file" hidden accept="image/*" onChange={handleImageChange} />
                        </Button>
                      )}
                    </CardContent>
                  </Card>
                </Grid>

                {/* Category & Tags */}
                <Grid item xs={12} sm={6}>
                  <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
                    <CardContent>
                      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                        Categories & Tags
                      </Typography>
                      <Stack spacing={2}>
                        <FormControl fullWidth size="small">
                          <InputLabel>Category</InputLabel>
                          <Select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} label="Category">
                            <MenuItem value="">None</MenuItem>
                            {categories.map((cat) => (
                              <MenuItem key={cat.id} value={cat.id}>{cat.name}</MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                        <FormControl fullWidth size="small">
                          <InputLabel>Tags</InputLabel>
                          <Select
                            multiple
                            value={selectedTags}
                            onChange={(e) => setSelectedTags(e.target.value)}
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
                        </FormControl>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          </Stack>
        </Grid>

        {/* AI Panel Column (Large screens) */}
        <Grid 
          item 
          xs={12} 
          lg={4} 
          sx={{ 
            display: { xs: 'none', lg: 'block' },
            mr: -3,  // Negative margin to extend to edge
            pr: 3,   // Add padding back inside
          }}
        >
          <Box sx={{ position: 'sticky', top: 80, pr: 0 }}>
            <Stack spacing={3}>
              {/* Featured Image */}
              <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
                <CardContent>
                  <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                    Featured Image
                  </Typography>
                  {imagePreview ? (
                    <Box sx={{ position: 'relative' }}>
                      <Box component="img" src={imagePreview} sx={{ width: '100%', borderRadius: 1 }} />
                      <IconButton
                        size="small"
                        onClick={handleImageRemove}
                        sx={{ position: 'absolute', top: 8, right: 8, bgcolor: 'background.paper', boxShadow: 1 }}
                      >
                        <IconX size={16} />
                      </IconButton>
                    </Box>
                  ) : (
                    <Button variant="outlined" component="label" fullWidth startIcon={<IconPhoto size={18} />} sx={{ py: 3 }}>
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
                    <FormControl fullWidth size="small">
                      <InputLabel>Category</InputLabel>
                      <Select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} label="Category">
                        <MenuItem value="">None</MenuItem>
                        {categories.map((cat) => (
                          <MenuItem key={cat.id} value={cat.id}>{cat.name}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                    <FormControl fullWidth size="small">
                      <InputLabel>Tags</InputLabel>
                      <Select
                        multiple
                        value={selectedTags}
                        onChange={(e) => setSelectedTags(e.target.value)}
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
                    </FormControl>
                  </Stack>
                </CardContent>
              </Card>

              {/* AI Writer Panel */}
              <AiWriterPanel onInsert={handleAiInsert} />
            </Stack>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}
