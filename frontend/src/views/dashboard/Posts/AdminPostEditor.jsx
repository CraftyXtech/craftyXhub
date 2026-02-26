import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';

// MUI
import Box from '@mui/material/Box';
import ListSubheader from '@mui/material/ListSubheader';
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
import Drawer from '@mui/material/Drawer';
import Divider from '@mui/material/Divider';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import Tooltip from '@mui/material/Tooltip';

// TinyMCE
import { Editor } from '@tinymce/tinymce-react';

// Import TinyMCE core and plugins
import 'tinymce/tinymce';
import 'tinymce/models/dom/model';
import 'tinymce/themes/silver';
import 'tinymce/icons/default';

// TinyMCE plugins
import 'tinymce/plugins/link';
import 'tinymce/plugins/image';
import 'tinymce/plugins/lists';

// TinyMCE skins (UI and content)
import 'tinymce/skins/ui/oxide/skin.min.css';
import 'tinymce/skins/ui/oxide/content.min.css';
import 'tinymce/skins/content/default/content.min.css';

// Icons
import {
  IconArrowLeft,
  IconDeviceFloppy,
  IconSend,
  IconPhoto,
  IconX,
  IconSettings,
  IconSparkles,
} from '@tabler/icons-react';

// Components
import AiWriterPanel from '@/components/ai-writer/AiWriterPanel';

// API
import { createPost, updatePost, getPost, getImageUrl } from '@/api/services/postService';
import { getCategories } from '@/api/services/categoryService';
import { getTags } from '@/api/services/tagService';

// Utils
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';

const SETTINGS_PANEL_WIDTH = 200;

/**
 * AdminPostEditor - TinyMCE editor with AI writing panel for admins/moderators
 * Notion-inspired layout with toggleable right drawers
 */
export default function AdminPostEditor() {
  const navigate = useNavigate();
  const { id } = useParams();
  const location = useLocation();
  const isEditing = Boolean(id);
  const editorRef = useRef(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const aiState = location.state;

  // State
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [editorReady, setEditorReady] = useState(false);

  // Drawer state
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [aiDrawerOpen, setAiDrawerOpen] = useState(false);

  // Form state
  const [title, setTitle] = useState(aiState?.title || '');
  const [slug, setSlug] = useState('');
  const [content, setContent] = useState(aiState?.aiContent || '');
  const [excerpt, setExcerpt] = useState(aiState?.excerpt || '');
  const [autoExcerpt, setAutoExcerpt] = useState(!aiState?.excerpt);
  const [categoryId, setCategoryId] = useState('');
  const [selectedTags, setSelectedTags] = useState([]);
  const [metaTitle, setMetaTitle] = useState(aiState?.metaTitle || '');
  const [metaDescription, setMetaDescription] = useState(aiState?.metaDescription || '');
  const [featuredImage, setFeaturedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  // Data
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);

  const [wordCount, setWordCount] = useState(0);

  // Auto-generate slug from title
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

  // Update stats + auto-excerpt when content changes
  useEffect(() => {
    const text = content.replace(/<[^>]*>/g, '');
    setWordCount(text.split(/\s+/).filter(w => w.length > 0).length);

    // Auto-fill excerpt from first ~160 chars of plain text
    if (autoExcerpt && text.length > 0) {
      const autoText = text.slice(0, 160).trim();
      setExcerpt(autoText + (text.length > 160 ? '...' : ''));
    }
  }, [content, autoExcerpt]);

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
          setAutoExcerpt(false); // Manual mode when editing
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

  // Drawer toggles — only one open at a time
  const toggleSettings = () => {
    setSettingsOpen(!settingsOpen);
    if (!settingsOpen) setAiDrawerOpen(false);
  };

  const toggleAiDrawer = () => {
    setAiDrawerOpen(!aiDrawerOpen);
    if (!aiDrawerOpen) setSettingsOpen(false);
  };

  // Handle AI content insert (append)
  const handleAiInsert = useCallback((html) => {
    if (editorRef.current) {
      const currentContent = editorRef.current.getContent();
      const newContent = currentContent + (currentContent ? '<div></div>' : '') + html;
      editorRef.current.setContent(newContent);
      setContent(newContent);
    }
  }, []);

  // Handle AI content replace (overwrite entire editor)
  const handleAiReplace = useCallback((html) => {
    if (editorRef.current) {
      editorRef.current.setContent(html);
      setContent(html);
    }
  }, []);

  // Handle AI metadata auto-fill (title, slug, excerpt, SEO, tags)
  const handleAiMetadataFill = useCallback((metadata) => {
    if (!metadata) return;

    if (metadata.title) setTitle(metadata.title);
    if (metadata.slug) setSlug(metadata.slug);
    if (metadata.excerpt) {
      setExcerpt(metadata.excerpt);
      setAutoExcerpt(false); // Switch to manual mode
    }
    if (metadata.metaTitle) setMetaTitle(metadata.metaTitle);
    if (metadata.metaDescription) setMetaDescription(metadata.metaDescription);

    // Auto-match AI-generated tag names against loaded tags
    if (metadata.tags?.length > 0 && tags.length > 0) {
      const matchedTagIds = tags
        .filter(t => metadata.tags.some(
          aiTag => t.name.toLowerCase() === aiTag.toLowerCase()
        ))
        .map(t => t.id);
      if (matchedTagIds.length > 0) {
        setSelectedTags(matchedTagIds);
      }
    }
  }, [tags]);

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
      {/* Header Bar */}
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
        <Stack direction="row" alignItems="center" spacing={2}>
          <IconButton onClick={() => navigate('/dashboard/posts')}>
            <IconArrowLeft size={20} />
          </IconButton>
          <Box>
            <Typography variant="h5" fontWeight={600}>
              {isEditing ? 'Edit Post' : 'Create New Post'}
            </Typography>
          </Box>
        </Stack>

        <Stack direction="row" spacing={1} alignItems="center">
          {/* Settings Toggle */}
          {/* Settings toggle — mobile only */}
          {isMobile && (
            <Tooltip title="Post Settings">
              <IconButton
                onClick={toggleSettings}
                sx={{
                  bgcolor: settingsOpen ? 'action.selected' : 'transparent',
                  '&:hover': { bgcolor: 'action.hover' }
                }}
              >
                <IconSettings size={20} />
              </IconButton>
            </Tooltip>
          )}

          {/* AI Toggle */}
          <Tooltip title="AI Writer">
            <IconButton
              onClick={toggleAiDrawer}
              sx={{
                bgcolor: aiDrawerOpen ? 'action.selected' : 'transparent',
                '&:hover': { bgcolor: 'action.hover' }
              }}
            >
              <IconSparkles size={20} />
            </IconButton>
          </Tooltip>

          <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />

          {/* Save/Publish */}
          <Button
            variant="outlined"
            size="small"
            startIcon={saving ? <CircularProgress size={16} /> : <IconDeviceFloppy size={18} />}
            onClick={() => handleSubmit(false)}
            disabled={saving}
          >
            Save Draft
          </Button>
          <Button
            variant="contained"
            size="small"
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

      {/* Main layout: editor + inline settings on desktop */}
      <Box sx={{ display: 'flex', gap: 2 }}>
        {/* Editor column */}
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Stack spacing={3}>
            {/* Title */}
            <TextField
              label="Title"
              fullWidth
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />

            {/* TinyMCE Editor — Full Width */}
            <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
              <CardContent sx={{ p: 0, '&:last-child': { pb: 0 } }}>
                <Editor
                  licenseKey="gpl"
                  onInit={(evt, editor) => {
                    editorRef.current = editor;
                    setEditorReady(true);
                    if (aiState?.aiContent && !isEditing) {
                      editor.setContent(aiState.aiContent);
                    }
                  }}
                  initialValue={content}
                  onEditorChange={(newContent) => setContent(newContent)}
                  init={{
                    height: 500,
                    menubar: false,
                    plugins: 'link lists image',
                    toolbar:
                      'undo redo | blocks | bold italic forecolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | link insertimage',
                    content_style: [
                      theme.palette.mode === 'dark'
                        ? 'body { font-family: "Open Sans", sans-serif; font-size: 14px; color: #fff; background-color: #1a1a1a; }'
                        : 'body { font-family: "Open Sans", sans-serif; font-size: 14px; color: #000; background-color: #fff; }',
                      'img { cursor: pointer; max-width: 100%; }',
                      'img:hover { outline: 2px solid #1976d2; }',
                      'img.mce-selected { outline: 2px solid #1976d2; }',
                    ].join('\n'),
                    branding: false,
                    directionality: 'ltr',
                    skin: false,
                    content_css: false,
                    object_resizing: 'img',
                    resize_img_proportional: true,
                    image_advtab: false,
                    setup: (editor) => {
                      editor.ui.registry.addButton('insertimage', {
                        icon: 'image',
                        tooltip: 'Insert image from device',
                        onAction: () => {
                          const input = document.createElement('input');
                          input.type = 'file';
                          input.accept = 'image/*';
                          input.addEventListener('change', (e) => {
                            const file = e.target.files[0];
                            if (file) {
                              const reader = new FileReader();
                              reader.addEventListener('load', () => {
                                editor.insertContent(`<img src="${reader.result}" alt="${file.name}" style="max-width:300px; height:auto;" />`);
                              });
                              reader.readAsDataURL(file);
                            }
                          });
                          input.click();
                        },
                      });
                    },
                  }}
                />
              </CardContent>
            </Card>
            <Typography variant="caption" color="text.secondary" sx={{ mt: -2 }}>
              {wordCount} words
            </Typography>

            {/* Excerpt — with auto-generate toggle */}
            <Box>
              <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 1 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Excerpt
                </Typography>
                <FormControlLabel
                  control={
                    <Switch
                      size="small"
                      checked={autoExcerpt}
                      onChange={(e) => setAutoExcerpt(e.target.checked)}
                    />
                  }
                  label={<Typography variant="caption">Auto-generate</Typography>}
                  labelPlacement="start"
                  sx={{ mr: 0 }}
                />
              </Stack>
              <TextField
                multiline
                rows={2}
                fullWidth
                size="small"
                value={excerpt}
                onChange={(e) => {
                  setExcerpt(e.target.value);
                  setAutoExcerpt(false);
                }}
                placeholder="Brief summary shown in post listings"
                disabled={autoExcerpt}
                sx={{
                  '& .MuiInputBase-root': {
                    bgcolor: autoExcerpt ? 'action.hover' : 'background.paper'
                  }
                }}
              />
            </Box>

            {/* SEO Settings — Side by side on desktop */}
            <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
              <CardContent>
                <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 2 }}>
                  SEO Settings
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      label="Meta Title"
                      fullWidth
                      size="small"
                      value={metaTitle}
                      onChange={(e) => setMetaTitle(e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      label="Meta Description"
                      fullWidth
                      size="small"
                      value={metaDescription}
                      onChange={(e) => setMetaDescription(e.target.value)}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Stack>
        </Box>

        {/* Settings panel — inline on desktop, hidden on mobile */}
        {!isMobile && (
          <Box
            sx={{
              width: SETTINGS_PANEL_WIDTH,
              flexShrink: 0,
              position: 'sticky',
              top: 56,
              alignSelf: 'flex-start',
              maxHeight: 'calc(100vh - 72px)',
              overflowY: 'auto',
            }}
          >
            <Stack spacing={2.5}>
              {/* Featured Image */}
              <Box>
                <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                  Image
                </Typography>
                {imagePreview ? (
                  <Box sx={{ position: 'relative' }}>
                    <Box component="img" src={imagePreview} sx={{ width: '100%', borderRadius: 1 }} />
                    <IconButton
                      size="small"
                      onClick={handleImageRemove}
                      sx={{ position: 'absolute', top: 4, right: 4, bgcolor: 'background.paper', boxShadow: 1 }}
                    >
                      <IconX size={14} />
                    </IconButton>
                  </Box>
                ) : (
                  <Button variant="outlined" component="label" fullWidth startIcon={<IconPhoto size={16} />} sx={{ py: 2, fontSize: 12 }}>
                    Upload
                    <input type="file" hidden accept="image/*" onChange={handleImageChange} />
                  </Button>
                )}
              </Box>

              <Divider />

              {/* Category */}
              <Box>
                <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                  Category
                </Typography>
                <FormControl fullWidth size="small">
                  <InputLabel>Category</InputLabel>
                  <Select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} label="Category">
                    <MenuItem value="">None</MenuItem>
                    {categories.filter(c => !c.parent_id).map((cat) => [
                      <ListSubheader key={`header-${cat.id}`} sx={{ lineHeight: '32px', fontSize: '0.75rem', fontWeight: 700, color: 'text.secondary', bgcolor: 'background.paper' }}>
                        {cat.name}
                      </ListSubheader>,
                      <MenuItem key={cat.id} value={cat.id} sx={{ pl: 3, fontSize: '0.85rem' }}>
                        All {cat.name}
                      </MenuItem>,
                      ...(cat.subcategories || []).map((sub) => (
                        <MenuItem key={sub.id} value={sub.id} sx={{ pl: 4, fontSize: '0.85rem' }}>
                          {sub.name}
                        </MenuItem>
                      ))
                    ])}
                  </Select>
                </FormControl>
              </Box>

              {/* Tags */}
              <Box>
                <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                  Tags
                </Typography>
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
              </Box>
            </Stack>
          </Box>
        )}
      </Box>

      {/* Settings Drawer — mobile only */}
      {isMobile && (
        <Drawer
          anchor="right"
          open={settingsOpen}
          onClose={() => setSettingsOpen(false)}
          variant="temporary"
          ModalProps={{ keepMounted: true }}
          sx={{
            '& .MuiDrawer-paper': {
              width: 280,
              px: 2,
              py: 1.5,
            }
          }}
        >
          <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
            <Typography variant="h6" fontWeight={600}>Post Settings</Typography>
            <IconButton size="small" onClick={() => setSettingsOpen(false)}>
              <IconX size={18} />
            </IconButton>
          </Stack>
          <Divider sx={{ mb: 2 }} />
          <Stack spacing={2.5}>
            <Box>
              <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>Image</Typography>
              {imagePreview ? (
                <Box sx={{ position: 'relative' }}>
                  <Box component="img" src={imagePreview} sx={{ width: '100%', borderRadius: 1 }} />
                  <IconButton size="small" onClick={handleImageRemove}
                    sx={{ position: 'absolute', top: 4, right: 4, bgcolor: 'background.paper', boxShadow: 1 }}>
                    <IconX size={14} />
                  </IconButton>
                </Box>
              ) : (
                <Button variant="outlined" component="label" fullWidth startIcon={<IconPhoto size={16} />} sx={{ py: 2, fontSize: 12 }}>
                  Upload
                  <input type="file" hidden accept="image/*" onChange={handleImageChange} />
                </Button>
              )}
            </Box>
            <Divider />
            <Box>
              <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>Category</Typography>
              <FormControl fullWidth size="small">
                <InputLabel>Category</InputLabel>
                <Select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} label="Category">
                  <MenuItem value="">None</MenuItem>
                  {categories.filter(c => !c.parent_id).map((cat) => [
                    <ListSubheader key={`header-${cat.id}`} sx={{ lineHeight: '32px', fontSize: '0.75rem', fontWeight: 700, color: 'text.secondary', bgcolor: 'background.paper' }}>
                      {cat.name}
                    </ListSubheader>,
                    <MenuItem key={cat.id} value={cat.id} sx={{ pl: 3, fontSize: '0.85rem' }}>
                      All {cat.name}
                    </MenuItem>,
                    ...(cat.subcategories || []).map((sub) => (
                      <MenuItem key={sub.id} value={sub.id} sx={{ pl: 4, fontSize: '0.85rem' }}>
                        {sub.name}
                      </MenuItem>
                    ))
                  ])}
                </Select>
              </FormControl>
            </Box>
            <Box>
              <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>Tags</Typography>
              <FormControl fullWidth size="small">
                <InputLabel>Tags</InputLabel>
                <Select multiple value={selectedTags} onChange={(e) => setSelectedTags(e.target.value)} label="Tags"
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((id) => { const tag = tags.find(t => t.id === id); return <Chip key={id} label={tag?.name || id} size="small" />; })}
                    </Box>
                  )}>
                  {tags.map((tag) => <MenuItem key={tag.id} value={tag.id}>{tag.name}</MenuItem>)}
                </Select>
              </FormControl>
            </Box>
          </Stack>
        </Drawer>
      )}

      {/* ===== AI Writer Drawer (Right) ===== */}
      <Drawer
        anchor="right"
        open={aiDrawerOpen}
        onClose={() => setAiDrawerOpen(false)}
        variant="temporary"
        ModalProps={{ keepMounted: true }}
        sx={{
          '& .MuiDrawer-paper': {
            width: { xs: '100%', sm: 380 },
            p: 0,
          }
        }}
      >
        <AiWriterPanel
          onInsert={handleAiInsert}
          onReplace={handleAiReplace}
          onMetadataFill={handleAiMetadataFill}
        />
      </Drawer>
    </Box>
  );
}
