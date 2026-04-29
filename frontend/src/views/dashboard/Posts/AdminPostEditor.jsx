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
import Tooltip from '@mui/material/Tooltip';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';

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
import 'tinymce/plugins/directionality';
import 'tinymce/plugins/quickbars';
import 'tinymce/plugins/table';

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
  IconCheck,
} from '@tabler/icons-react';

// Components
import AiWriterPanel from '@/components/ai-writer/AiWriterPanel';

// API
import { createPost, updatePost, getPost, getImageUrl, uploadPostImage } from '@/api/services/postService';
import {
  approvePostQualityOverride,
  createContentSource,
  generateDistributionAssets,
  generateTopicBriefs,
  getDistributionAssets,
  getLatestPostQualityReview,
  getTopicBriefs,
  importSearchConsoleRows,
  importTrendingRows,
  runPostQualityReview,
  updateTopicBriefStatus,
  updateDistributionAssetStatus,
} from '@/api/services/contentIntelligenceService';
import { getCategories } from '@/api/services/categoryService';
import { getTags } from '@/api/services/tagService';
import { generateExcerpt as generateAiExcerpt } from '@/api/services/aiService';

// Utils
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import { getPublishExcerptError, normalizeExcerpt } from '@/utils/editorUtils';
import {
  FEATURED_IMAGE_GUIDANCE,
  getImageFileFromClipboardEvent,
  normalizeFeaturedImageFile,
  readImageFileFromClipboard,
  validateFeaturedImageFile,
} from '@/utils/featuredImageValidation';
import { getApiErrorMessage } from '@/utils/apiError';

const SETTINGS_PANEL_WIDTH = 200;
const INTELLIGENCE_PANEL_WIDTH = 380;
const CONTENT_INTELLIGENCE_ENABLED = import.meta.env.VITE_CONTENT_INTELLIGENCE_ENABLED !== 'false';

const parseJsonRows = (value) => {
  const trimmed = value.trim();
  if (!trimmed) return [];
  const parsed = JSON.parse(trimmed);
  return Array.isArray(parsed) ? parsed : [parsed];
};

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
  const intelligenceRequest = new URLSearchParams(location.search).get('intelligence');
  const imageInputRef = useRef(null);

  // State
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [editorReady, setEditorReady] = useState(false);

  // Drawer state
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [aiDrawerOpen, setAiDrawerOpen] = useState(false);
  const [intelligenceOpen, setIntelligenceOpen] = useState(
    CONTENT_INTELLIGENCE_ENABLED && Boolean(aiState?.openIntelligence || intelligenceRequest)
  );
  const [intelligenceTab, setIntelligenceTab] = useState(aiState?.openIntelligence || intelligenceRequest || 'brief');

  // Form state
  const [title, setTitle] = useState(aiState?.title || '');
  const [slug, setSlug] = useState('');
  const [content, setContent] = useState(aiState?.aiContent || '');
  const [excerpt, setExcerpt] = useState(aiState?.excerpt || '');
  const [excerptError, setExcerptError] = useState('');
  const [isGeneratingExcerpt, setIsGeneratingExcerpt] = useState(false);
  const [categoryId, setCategoryId] = useState('');
  const [selectedTags, setSelectedTags] = useState([]);
  const [metaTitle, setMetaTitle] = useState(aiState?.metaTitle || '');
  const [metaDescription, setMetaDescription] = useState(aiState?.metaDescription || '');
  const [seoKeywords, setSeoKeywords] = useState(
    Array.isArray(aiState?.seoKeywords) ? aiState.seoKeywords.join(', ') : (aiState?.seoKeywords || '')
  );
  const [featuredImage, setFeaturedImage] = useState(null);
  const [featuredImagePath, setFeaturedImagePath] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [imageUploading, setImageUploading] = useState(false);
  const [imageUploadProgress, setImageUploadProgress] = useState(0);
  const [qualityReview, setQualityReview] = useState(null);
  const [distributionAssets, setDistributionAssets] = useState([]);
  const [intelligenceLoading, setIntelligenceLoading] = useState(false);
  const [topicBriefs, setTopicBriefs] = useState([]);
  const [briefStatusFilter, setBriefStatusFilter] = useState('pending');
  const [briefsLoading, setBriefsLoading] = useState(false);
  const [sourceName, setSourceName] = useState('');
  const [sourceType, setSourceType] = useState('rss');
  const [sourceUrl, setSourceUrl] = useState('');
  const [importJson, setImportJson] = useState('');

  // Data
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);

  const [wordCount, setWordCount] = useState(0);

  useEffect(() => {
    if (aiState?.categoryId && !categoryId) {
      setCategoryId(String(aiState.categoryId));
    }
  }, [aiState?.categoryId, categoryId]);

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

  // Helper: update word count from editor content
  const updateStatsFromEditor = useCallback(() => {
    if (!editorRef.current) return;
    const html = editorRef.current.getContent();
    const text = html.replace(/<[^>]*>/g, '');
    setWordCount(text.split(/\s+/).filter(w => w.length > 0).length);
  }, []);

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
    if (isEditing && id) {
      const loadPost = async () => {
        try {
          setLoading(true);
          const post = await getPost(id);
          
          setTitle(post.title || '');
          setSlug(post.slug || '');
          setContent(post.content || ''); // Store in state so TinyMCE picks it up on re-mount
          setExcerpt(post.excerpt || '');
          setCategoryId(post.category?.id || post.category_id || '');
          setSelectedTags(post.tags?.map(t => t.id) || []);
          setMetaTitle(post.meta_title || '');
          setMetaDescription(post.meta_description || '');
          setSeoKeywords(Array.isArray(post.seo_keywords) ? post.seo_keywords.join(', ') : '');
          
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
  }, [id, isEditing]);

  const loadIntelligence = useCallback(async () => {
    if (!isEditing || !id) return;
    try {
      const [review, assets] = await Promise.all([
        getLatestPostQualityReview(id),
        getDistributionAssets(id),
      ]);
      setQualityReview(review || null);
      setDistributionAssets(assets || []);
    } catch (err) {
      console.error('Failed to load content intelligence:', err);
    }
  }, [id, isEditing]);

  useEffect(() => {
    loadIntelligence();
  }, [loadIntelligence]);

  const loadTopicBriefs = useCallback(async () => {
    try {
      setBriefsLoading(true);
      const data = await getTopicBriefs({ status: briefStatusFilter || undefined, limit: 20 });
      setTopicBriefs(data || []);
    } catch (err) {
      console.error('Failed to load topic briefs:', err);
      setError(getApiErrorMessage(err, 'Failed to load topic briefs'));
    } finally {
      setBriefsLoading(false);
    }
  }, [briefStatusFilter]);

  useEffect(() => {
    if (intelligenceOpen && intelligenceTab === 'brief') {
      loadTopicBriefs();
    }
  }, [intelligenceOpen, intelligenceTab, loadTopicBriefs]);

  // Handle image upload — eagerly uploads when user selects a file
  const processFeaturedImageFile = useCallback(async (file) => {
    if (!file) return;

    const validation = await validateFeaturedImageFile(file);
    if (!validation.ok) {
      setError(validation.message);
      return;
    }

    setError(null);

    let normalizedFile;
    try {
      normalizedFile = await normalizeFeaturedImageFile(file);
    } catch (normalizationError) {
      setError(normalizationError.message || 'Failed to prepare the image. Please try a different file.');
      return;
    }

    // Show preview immediately
    setImagePreview(URL.createObjectURL(normalizedFile));
    setFeaturedImage(normalizedFile);
    setImageUploading(true);
    setImageUploadProgress(0);

    try {
      const result = await uploadPostImage(normalizedFile, (progress) => {
        setImageUploadProgress(progress);
      });
      // Store the file_path returned by the upload
      setFeaturedImagePath(result.file_path || result.filename);
      setImageUploading(false);
    } catch (err) {
      console.error('Image upload failed:', err);
      setError('Failed to upload image. Please try again.');
      setFeaturedImage(null);
      setImagePreview(null);
      setFeaturedImagePath(null);
      setImageUploading(false);
    }
  }, []);

  const handleImageChange = async (e) => {
    const file = e.target.files?.[0];
    await processFeaturedImageFile(file);
    e.target.value = '';
  };

  const handleImagePaste = useCallback(async (event) => {
    const file = getImageFileFromClipboardEvent(event);
    if (!file) return;
    event.preventDefault();
    await processFeaturedImageFile(file);
  }, [processFeaturedImageFile]);

  const openImagePicker = useCallback(() => {
    imageInputRef.current?.click();
  }, []);

  const handlePasteImageButton = useCallback(async () => {
    try {
      const file = await readImageFileFromClipboard();
      await processFeaturedImageFile(file);
    } catch (clipboardError) {
      setError(clipboardError.message || 'Clipboard image unavailable.');
    }
  }, [processFeaturedImageFile]);

  const handleImageRemove = () => {
    setFeaturedImage(null);
    setFeaturedImagePath(null);
    setImagePreview(null);
    setImageUploadProgress(0);
  };

  // Drawer toggles — only one open at a time
  const toggleSettings = () => {
    setSettingsOpen(!settingsOpen);
    if (!settingsOpen) {
      setAiDrawerOpen(false);
      setIntelligenceOpen(false);
    }
  };

  const toggleAiDrawer = () => {
    setAiDrawerOpen(!aiDrawerOpen);
    if (!aiDrawerOpen) {
      setSettingsOpen(false);
      setIntelligenceOpen(false);
    }
  };

  const toggleIntelligence = () => {
    if (!CONTENT_INTELLIGENCE_ENABLED) return;
    setIntelligenceOpen(!intelligenceOpen);
    if (!intelligenceOpen) {
      setSettingsOpen(false);
      setAiDrawerOpen(false);
    }
  };

  // Handle AI content insert (append)
  const handleAiInsert = useCallback((html) => {
    if (editorRef.current) {
      const currentContent = editorRef.current.getContent();
      const newContent = currentContent + (currentContent ? '<div></div>' : '') + html;
      editorRef.current.setContent(newContent);
      updateStatsFromEditor();
    }
  }, [updateStatsFromEditor]);

  // Handle AI content replace (overwrite entire editor)
  const handleAiReplace = useCallback((html) => {
    if (editorRef.current) {
      editorRef.current.setContent(html);
      updateStatsFromEditor();
    }
  }, [updateStatsFromEditor]);

  // Handle AI metadata auto-fill (title, slug, excerpt, SEO, tags)
  const handleAiMetadataFill = useCallback((metadata) => {
    if (!metadata) return;

    if (metadata.title && !title.trim()) setTitle(metadata.title);
    if (metadata.slug && !slug.trim()) setSlug(metadata.slug);
    if (metadata.excerpt && !excerpt.trim()) {
      setExcerpt(metadata.excerpt);
      setExcerptError('');
    }
    if (metadata.metaTitle && !metaTitle.trim()) setMetaTitle(metadata.metaTitle);
    if (metadata.metaDescription && !metaDescription.trim()) setMetaDescription(metadata.metaDescription);
    if (metadata.seoKeywords?.length > 0 && !seoKeywords.trim()) {
      setSeoKeywords(metadata.seoKeywords.join(', '));
    }
    if (metadata.categoryId && !categoryId) setCategoryId(String(metadata.categoryId));

    if (metadata.tagIds?.length > 0 && selectedTags.length === 0) {
      setSelectedTags(metadata.tagIds);
      return;
    }

    // Auto-match AI-generated tag names against loaded tags
    if (metadata.tags?.length > 0 && tags.length > 0) {
      const matchedTagIds = tags
        .filter(t => metadata.tags.some(
          aiTag => t.name.toLowerCase() === aiTag.toLowerCase()
        ))
        .map(t => t.id);
      if (matchedTagIds.length > 0 && selectedTags.length === 0) {
        setSelectedTags(matchedTagIds);
      }
    }
  }, [categoryId, excerpt, metaDescription, metaTitle, selectedTags.length, seoKeywords, slug, tags, title]);

  const handleGenerateExcerpt = useCallback(async () => {
    const currentContent = editorRef.current ? editorRef.current.getContent() : content;
    const plainText = currentContent.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();

    if (plainText.length < 120) {
      setError('Add more article content before generating the excerpt.');
      return;
    }

    try {
      setIsGeneratingExcerpt(true);
      setError(null);
      setExcerptError('');
      const result = await generateAiExcerpt({
        title: title || 'Untitled',
        content: currentContent,
      });
      setExcerpt(result.excerpt || '');
    } catch (err) {
      console.error('Failed to generate excerpt:', err);
      setError(getApiErrorMessage(err, 'Failed to generate excerpt'));
    } finally {
      setIsGeneratingExcerpt(false);
    }
  }, [content, title]);

  const handleRunQualityReview = useCallback(async () => {
    if (!isEditing || !id) {
      setError('Save the post before running quality checks.');
      return;
    }
    try {
      setIntelligenceLoading(true);
      setError(null);
      const review = await runPostQualityReview(id);
      setQualityReview(review);
    } catch (err) {
      console.error('Failed to run quality review:', err);
      setError(getApiErrorMessage(err, 'Failed to run quality review'));
    } finally {
      setIntelligenceLoading(false);
    }
  }, [id, isEditing]);

  const handleApproveQualityOverride = useCallback(async () => {
    if (!isEditing || !id) return;
    const reason = window.prompt('Why are you approving this post despite quality warnings?');
    if (!reason?.trim()) return;
    try {
      setIntelligenceLoading(true);
      const review = await approvePostQualityOverride(id, reason.trim());
      setQualityReview(review);
    } catch (err) {
      console.error('Failed to approve quality override:', err);
      setError(getApiErrorMessage(err, 'Failed to approve quality override'));
    } finally {
      setIntelligenceLoading(false);
    }
  }, [id, isEditing]);

  const handleGenerateDistributionAssets = useCallback(async () => {
    if (!isEditing || !id) {
      setError('Save the post before generating distribution assets.');
      return;
    }
    try {
      setIntelligenceLoading(true);
      const assets = await generateDistributionAssets(id);
      setDistributionAssets(assets || []);
    } catch (err) {
      console.error('Failed to generate distribution assets:', err);
      setError(getApiErrorMessage(err, 'Failed to generate distribution assets'));
    } finally {
      setIntelligenceLoading(false);
    }
  }, [id, isEditing]);

  const handleApproveAsset = useCallback(async (asset) => {
    try {
      setIntelligenceLoading(true);
      await updateDistributionAssetStatus(asset.uuid, 'approved');
      await loadIntelligence();
    } catch (err) {
      console.error('Failed to approve asset:', err);
      setError(getApiErrorMessage(err, 'Failed to approve distribution asset'));
    } finally {
      setIntelligenceLoading(false);
    }
  }, [loadIntelligence]);

  const handleCopyAsset = useCallback((asset) => {
    const text = asset.tracked_url ? `${asset.content}\n${asset.tracked_url}` : asset.content;
    navigator.clipboard.writeText(text);
  }, []);

  const handleGenerateBriefs = useCallback(async () => {
    try {
      setIntelligenceLoading(true);
      setError(null);
      await generateTopicBriefs({ limit: 10 });
      await loadTopicBriefs();
    } catch (err) {
      console.error('Failed to generate topic briefs:', err);
      setError(getApiErrorMessage(err, 'Failed to generate topic briefs'));
    } finally {
      setIntelligenceLoading(false);
    }
  }, [loadTopicBriefs]);

  const handleBriefStatus = useCallback(async (brief, nextStatus) => {
    try {
      setIntelligenceLoading(true);
      await updateTopicBriefStatus(brief.uuid, nextStatus);
      await loadTopicBriefs();
    } catch (err) {
      console.error('Failed to update topic brief:', err);
      setError(getApiErrorMessage(err, 'Failed to update topic brief'));
    } finally {
      setIntelligenceLoading(false);
    }
  }, [loadTopicBriefs]);

  const handleApplyBrief = useCallback(async (brief) => {
    setTitle(brief.title || '');
    setExcerpt(brief.angle || '');
    setExcerptError('');
    setSeoKeywords((brief.keywords || []).join(', '));
    if (brief.category_id) setCategoryId(String(brief.category_id));
    await handleBriefStatus(brief, 'approved');
    setIntelligenceTab('quality');
  }, [handleBriefStatus]);

  const handleCreateSource = useCallback(async () => {
    if (!sourceName.trim()) {
      setError('Source name is required');
      return;
    }
    try {
      setIntelligenceLoading(true);
      setError(null);
      await createContentSource({
        name: sourceName.trim(),
        source_type: sourceType,
        url: sourceUrl.trim() || null,
      });
      setSourceName('');
      setSourceUrl('');
    } catch (err) {
      console.error('Failed to add content source:', err);
      setError(getApiErrorMessage(err, 'Failed to add source'));
    } finally {
      setIntelligenceLoading(false);
    }
  }, [sourceName, sourceType, sourceUrl]);

  const handleImportSignals = useCallback(async (kind) => {
    try {
      setIntelligenceLoading(true);
      setError(null);
      const rows = parseJsonRows(importJson);
      if (kind === 'search_console') {
        await importSearchConsoleRows(rows);
      } else {
        await importTrendingRows(rows);
      }
      setImportJson('');
      await loadTopicBriefs();
    } catch (err) {
      console.error('Failed to import signal rows:', err);
      setError(getApiErrorMessage(err, 'Failed to import rows'));
    } finally {
      setIntelligenceLoading(false);
    }
  }, [importJson, loadTopicBriefs]);

  // Submit form
  const handleSubmit = async (shouldPublish = false) => {
    try {
      setSaving(true);
      setError(null);

      if (!title.trim()) {
        setError('Title is required');
        return;
      }

      const currentContent = editorRef.current ? editorRef.current.getContent() : '';
      if (!currentContent.trim()) {
        setError('Content is required');
        return;
      }

      if (shouldPublish && !categoryId) {
        setError('Please choose a category before publishing');
        setSettingsOpen(true);
        return;
      }

      if (shouldPublish) {
        const publishExcerptError = getPublishExcerptError(excerpt);
        if (publishExcerptError) {
          setExcerptError(publishExcerptError);
          return;
        }
      }

      const formData = new FormData();
      formData.append('title', title);
      formData.append('slug', slug);
      formData.append('content', currentContent);
      formData.append('excerpt', normalizeExcerpt(excerpt));
      formData.append('meta_title', metaTitle || '');
      formData.append('meta_description', metaDescription || '');
      formData.append('seo_keywords', seoKeywords || '');
      formData.append('is_published', shouldPublish ? 'true' : 'false');
      
      if (categoryId) {
        formData.append('category_id', categoryId);
      }
      if (selectedTags.length) {
        formData.append('tag_ids', selectedTags.join(','));
      }
      if (featuredImagePath) {
        // Image was already uploaded eagerly — just send the path
        formData.append('featured_image_path', featuredImagePath);
      } else if (featuredImage) {
        // Fallback: upload with the request (shouldn't happen normally)
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
      setError(getApiErrorMessage(err, 'Failed to save post'));
    } finally {
      setSaving(false);
    }
  };

  const qualityIssues = qualityReview
    ? [
        ...(qualityReview.checks?.critical_failures || []),
        ...(qualityReview.checks?.warnings || [])
      ]
    : [];

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

          {CONTENT_INTELLIGENCE_ENABLED && (
            <Tooltip title="Content Intelligence">
              <IconButton
                onClick={toggleIntelligence}
                sx={{
                  bgcolor: intelligenceOpen ? 'action.selected' : 'transparent',
                  '&:hover': { bgcolor: 'action.hover' }
                }}
              >
                <IconCheck size={20} />
              </IconButton>
            </Tooltip>
          )}

          <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />

          {/* Save/Publish */}
          <Button
            variant="outlined"
            size="small"
            startIcon={saving ? <CircularProgress size={16} /> : <IconDeviceFloppy size={18} />}
            onClick={() => handleSubmit(false)}
            disabled={saving || imageUploading}
          >
            Save Draft
          </Button>
          <Button
            variant="contained"
            size="small"
            startIcon={saving ? <CircularProgress size={16} color="inherit" /> : <IconSend size={18} />}
            onClick={() => handleSubmit(true)}
            disabled={saving || imageUploading}
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
                  init={{
                    height: 500,
                    menubar: false,
                    plugins: 'link lists image directionality quickbars table',
                    toolbar:
                      'undo redo | blocks | bold italic forecolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | link insertimage',
                    // Quickbars — floating toolbar on text selection (Word-style)
                    quickbars_selection_toolbar: 'bold italic underline | blocks | forecolor backcolor | link blockquote | alignleft aligncenter alignright',
                    quickbars_insert_toolbar: 'insertimage hr table',
                    // Context menu — right-click actions
                    contextmenu: 'cut copy paste selectall | link image table',
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
                    image_advtab: true,
                    setup: (editor) => {
                      // Update word count + auto-excerpt on every keystroke
                      editor.on('keyup change SetContent', () => {
                        updateStatsFromEditor();
                      });

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
                                editor.insertContent(`<img src="${reader.result}" alt="${file.name}" style="max-width:100%; height:auto;" />`);
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

            {/* Excerpt */}
            <Box>
              <Stack direction="row" alignItems="center" justifyContent="space-between" spacing={2} sx={{ mb: 1 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Excerpt
                </Typography>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={handleGenerateExcerpt}
                  disabled={isGeneratingExcerpt}
                  startIcon={isGeneratingExcerpt ? <CircularProgress size={14} /> : <IconSparkles size={14} />}
                >
                  {excerpt ? 'Regenerate' : 'Generate'}
                </Button>
              </Stack>
              <TextField
                multiline
                rows={2}
                fullWidth
                size="small"
                value={excerpt}
                onChange={(e) => {
                  setExcerpt(e.target.value);
                  setExcerptError('');
                }}
                placeholder="Brief summary shown in post listings and used as a publish-ready summary"
                error={Boolean(excerptError)}
                helperText={excerptError || (excerpt ? `${excerpt.length}/500 characters` : ' ')}
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
                      placeholder="Short, sharp social title"
                      helperText={`${metaTitle.length}/65 characters. Aim for 45-65 and skip the site name.`}
                      inputProps={{ maxLength: 65 }}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      label="Meta Description"
                      fullWidth
                      size="small"
                      multiline
                      rows={2}
                      value={metaDescription}
                      onChange={(e) => setMetaDescription(e.target.value)}
                      placeholder="Why the article matters, in one tight teaser"
                      helperText={`${metaDescription.length}/155 characters. Keep it specific and social-ready.`}
                      inputProps={{ maxLength: 155 }}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      label="SEO Keywords"
                      fullWidth
                      size="small"
                      value={seoKeywords}
                      onChange={(e) => setSeoKeywords(e.target.value)}
                      placeholder="AI-generated if blank, comma-separated"
                      helperText="Use short search phrases separated by commas."
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {CONTENT_INTELLIGENCE_ENABLED && (
              <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
                <CardContent>
                  <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ xs: 'stretch', sm: 'center' }} spacing={1.5}>
                    <Box>
                      <Typography variant="subtitle2" fontWeight={600}>
                        Content Intelligence
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Topic briefs, publish checks, and distribution assets live in the editor side panel.
                      </Typography>
                    </Box>
                    <Button size="small" variant="outlined" startIcon={<IconSparkles size={16} />} onClick={toggleIntelligence}>
                      Open Panel
                    </Button>
                  </Stack>
                </CardContent>
              </Card>
            )}
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
                    <Box component="img" src={imagePreview} sx={{ width: '100%', borderRadius: 1, opacity: imageUploading ? 0.5 : 1 }} />
                    {imageUploading && (
                      <Box sx={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
                        <CircularProgress size={28} variant="determinate" value={imageUploadProgress} />
                        <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>{imageUploadProgress}%</Typography>
                      </Box>
                    )}
                    <IconButton
                      size="small"
                      onClick={handleImageRemove}
                      disabled={imageUploading}
                      sx={{ position: 'absolute', top: 4, right: 4, bgcolor: 'background.paper', boxShadow: 1 }}
                    >
                      <IconX size={14} />
                    </IconButton>
                  </Box>
                ) : (
                  <Box
                    onPaste={handleImagePaste}
                    sx={{
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1,
                      py: 2,
                      px: 1.5,
                      textAlign: 'center',
                    }}
                  >
                    <input
                      ref={imageInputRef}
                      type="file"
                      hidden
                      accept="image/*"
                      onChange={handleImageChange}
                    />
                    <Stack spacing={1} alignItems="stretch">
                      <Button variant="outlined" fullWidth startIcon={<IconPhoto size={16} />} onClick={openImagePicker}>
                        Upload
                      </Button>
                      <Button variant="text" fullWidth onClick={handlePasteImageButton}>
                        Paste image
                      </Button>
                    </Stack>
                  </Box>
                )}
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                  {FEATURED_IMAGE_GUIDANCE}
                </Typography>
              </Box>

              <Divider />

              {/* Category */}
              <Box>
                <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                  Category
                </Typography>
                <FormControl fullWidth size="small" required>
                  <InputLabel>Category *</InputLabel>
                  <Select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} label="Category *">
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
            zIndex: (theme) => theme.zIndex.drawer + 2,
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
                  <Box component="img" src={imagePreview} sx={{ width: '100%', borderRadius: 1, opacity: imageUploading ? 0.5 : 1 }} />
                  {imageUploading && (
                    <Box sx={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
                      <CircularProgress size={28} variant="determinate" value={imageUploadProgress} />
                      <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>{imageUploadProgress}%</Typography>
                    </Box>
                  )}
                  <IconButton size="small" onClick={handleImageRemove} disabled={imageUploading}
                    sx={{ position: 'absolute', top: 4, right: 4, bgcolor: 'background.paper', boxShadow: 1 }}>
                    <IconX size={14} />
                  </IconButton>
                </Box>
              ) : (
                <Box
                  onPaste={handleImagePaste}
                  sx={{
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    py: 2,
                    px: 1.5,
                    textAlign: 'center',
                  }}
                >
                  <input
                    ref={imageInputRef}
                    type="file"
                    hidden
                    accept="image/*"
                    onChange={handleImageChange}
                  />
                  <Stack spacing={1} alignItems="stretch">
                    <Button variant="outlined" fullWidth startIcon={<IconPhoto size={16} />} onClick={openImagePicker}>
                      Upload
                    </Button>
                    <Button variant="text" fullWidth onClick={handlePasteImageButton}>
                      Paste image
                    </Button>
                  </Stack>
                </Box>
              )}
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                {FEATURED_IMAGE_GUIDANCE}
              </Typography>
            </Box>
            <Divider />
            <Box>
              <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>Category</Typography>
              <FormControl fullWidth size="small" required>
                <InputLabel>Category *</InputLabel>
                <Select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} label="Category *">
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

      {/* Content Intelligence Drawer */}
      <Drawer
        anchor="right"
        open={intelligenceOpen}
        onClose={() => setIntelligenceOpen(false)}
        variant="temporary"
        ModalProps={{ keepMounted: true }}
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 2,
          '& .MuiDrawer-paper': {
            width: { xs: '100%', sm: INTELLIGENCE_PANEL_WIDTH },
            p: 0,
          }
        }}
      >
        <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
          <Stack direction="row" alignItems="center" justifyContent="space-between" spacing={1}>
            <Box>
              <Typography variant="h6" fontWeight={600}>Content Intelligence</Typography>
              <Typography variant="caption" color="text.secondary">Briefs, gates, and distribution</Typography>
            </Box>
            <IconButton size="small" onClick={() => setIntelligenceOpen(false)}>
              <IconX size={18} />
            </IconButton>
          </Stack>
        </Box>

        <Tabs
          value={intelligenceTab}
          onChange={(_, value) => setIntelligenceTab(value)}
          variant="fullWidth"
          sx={{ borderBottom: '1px solid', borderColor: 'divider', minHeight: 42 }}
        >
          <Tab value="brief" label="Brief" sx={{ minHeight: 42 }} />
          <Tab value="quality" label="Quality" sx={{ minHeight: 42 }} />
          <Tab value="distribution" label="Distribution" sx={{ minHeight: 42 }} />
        </Tabs>

        <Box sx={{ p: 2, overflowY: 'auto' }}>
          {intelligenceTab === 'brief' && (
            <Stack spacing={2}>
              <Stack direction="row" spacing={1.25} alignItems="center">
                <Button
                  size="small"
                  variant="contained"
                  startIcon={intelligenceLoading ? <CircularProgress size={14} color="inherit" /> : <IconSparkles size={14} />}
                  onClick={handleGenerateBriefs}
                  disabled={intelligenceLoading}
                  sx={{ textTransform: 'none', px: 2 }}
                >
                  Generate
                </Button>
                <Button size="small" variant="outlined" onClick={loadTopicBriefs} disabled={briefsLoading} sx={{ textTransform: 'none', px: 2 }}>
                  Refresh
                </Button>
                <TextField
                  select
                  size="small"
                  value={briefStatusFilter}
                  onChange={(event) => setBriefStatusFilter(event.target.value)}
                  sx={{ minWidth: 140 }}
                >
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="approved">Approved</MenuItem>
                  <MenuItem value="dismissed">Dismissed</MenuItem>
                  <MenuItem value="">All</MenuItem>
                </TextField>
              </Stack>

              {briefsLoading ? (
                <Stack direction="row" spacing={1} alignItems="center">
                  <CircularProgress size={18} />
                  <Typography variant="body2" color="text.secondary">Loading briefs...</Typography>
                </Stack>
              ) : topicBriefs.length === 0 ? (
                <Alert severity="info" variant="outlined">
                  No briefs found. Generate briefs from search, import, RSS, and gap signals.
                </Alert>
              ) : (
                <Stack spacing={1.25}>
                  {topicBriefs.map((brief) => (
                    <Box key={brief.uuid} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1, p: 1.25 }}>
                      <Stack spacing={1}>
                        <Stack direction="row" justifyContent="space-between" spacing={1}>
                          <Typography variant="subtitle2" fontWeight={600}>{brief.title}</Typography>
                          <Chip size="small" label={brief.status} variant="outlined" />
                        </Stack>
                        {brief.angle && (
                          <Typography variant="body2" color="text.secondary">{brief.angle}</Typography>
                        )}
                        <Stack direction="row" spacing={0.5} flexWrap="wrap">
                          {(brief.keywords || []).slice(0, 5).map((keyword) => (
                            <Chip key={keyword} size="small" label={keyword} variant="outlined" />
                          ))}
                        </Stack>
                        <Stack direction="row" spacing={1} justifyContent="flex-end">
                          <Button size="small" onClick={() => handleApplyBrief(brief)}>Apply</Button>
                          {brief.status !== 'approved' && (
                            <Button size="small" startIcon={<IconCheck size={14} />} onClick={() => handleBriefStatus(brief, 'approved')} disabled={intelligenceLoading}>
                              Approve
                            </Button>
                          )}
                          {brief.status !== 'dismissed' && (
                            <Button size="small" color="inherit" onClick={() => handleBriefStatus(brief, 'dismissed')} disabled={intelligenceLoading}>
                              Dismiss
                            </Button>
                          )}
                        </Stack>
                      </Stack>
                    </Box>
                  ))}
                </Stack>
              )}

              <Divider />
              <Box>
                <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>Signals</Typography>
                <Stack spacing={1.25}>
                  <TextField size="small" label="Source name" value={sourceName} onChange={(event) => setSourceName(event.target.value)} />
                  <Stack direction="row" spacing={1}>
                    <TextField
                      select
                      size="small"
                      label="Type"
                      value={sourceType}
                      onChange={(event) => setSourceType(event.target.value)}
                      sx={{ width: 130 }}
                    >
                      <MenuItem value="rss">RSS</MenuItem>
                      <MenuItem value="competitor">Competitor</MenuItem>
                      <MenuItem value="category">Category</MenuItem>
                    </TextField>
                    <TextField size="small" label="URL" value={sourceUrl} onChange={(event) => setSourceUrl(event.target.value)} fullWidth />
                  </Stack>
                  <Button size="small" variant="outlined" onClick={handleCreateSource} disabled={intelligenceLoading}>
                    Add Source
                  </Button>
                  <TextField
                    label="Import rows as JSON"
                    size="small"
                    multiline
                    minRows={4}
                    value={importJson}
                    onChange={(event) => setImportJson(event.target.value)}
                    placeholder='[{"query":"ai automation","impressions":1200,"clicks":24}]'
                  />
                  <Stack direction="row" spacing={1}>
                    <Button size="small" variant="outlined" onClick={() => handleImportSignals('search_console')} disabled={intelligenceLoading}>
                      Search Console
                    </Button>
                    <Button size="small" variant="outlined" onClick={() => handleImportSignals('trending')} disabled={intelligenceLoading}>
                      Trending
                    </Button>
                  </Stack>
                </Stack>
              </Box>
            </Stack>
          )}

          {intelligenceTab === 'quality' && (
            <Stack spacing={2}>
              <Stack direction="row" spacing={1} alignItems="center">
                <Button size="small" variant="contained" onClick={handleRunQualityReview} disabled={intelligenceLoading}>
                  Run Check
                </Button>
                {qualityReview?.status === 'needs_review' && (
                  <Button size="small" startIcon={<IconCheck size={14} />} onClick={handleApproveQualityOverride} disabled={intelligenceLoading}>
                    Approve Override
                  </Button>
                )}
              </Stack>

              {qualityReview ? (
                <Stack spacing={2}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Chip
                      size="small"
                      label={qualityReview.status === 'passed' ? 'Passed' : qualityReview.status === 'blocked' ? 'Blocked' : 'Needs Review'}
                      color={qualityReview.status === 'passed' ? 'success' : qualityReview.status === 'blocked' ? 'error' : 'warning'}
                    />
                    <Typography variant="caption" color="text.secondary">Score {qualityReview.score}/100</Typography>
                  </Stack>

                  <Box>
                    <Typography variant="caption" fontWeight={600} color="text.secondary">Gate Results</Typography>
                    {qualityIssues.length ? (
                      qualityIssues.map((item) => (
                        <Typography key={item} variant="body2" color="text.secondary">• {item}</Typography>
                      ))
                    ) : (
                      <Typography variant="body2" color="text.secondary">No warnings recorded.</Typography>
                    )}
                  </Box>

                  <Box>
                    <Typography variant="caption" fontWeight={600} color="text.secondary">Internal Links</Typography>
                    {(qualityReview.checks?.internal_link_suggestions || []).length ? (
                      (qualityReview.checks?.internal_link_suggestions || []).map((item) => (
                        <Typography key={item.post_uuid} variant="body2" color="text.secondary">• Link to {item.title}</Typography>
                      ))
                    ) : (
                      <Typography variant="body2" color="text.secondary">No link suggestions yet.</Typography>
                    )}
                  </Box>

                  <Box>
                    <Typography variant="caption" fontWeight={600} color="text.secondary">FAQ / Schema</Typography>
                    {(qualityReview.checks?.faq_suggestions || []).length ? (
                      (qualityReview.checks?.faq_suggestions || []).map((item) => (
                        <Typography key={item.question} variant="body2" color="text.secondary">• {item.question}</Typography>
                      ))
                    ) : (
                      <Typography variant="body2" color="text.secondary">No schema suggestions yet.</Typography>
                    )}
                  </Box>
                </Stack>
              ) : (
                <Alert severity="info" variant="outlined">
                  Save the post, then run a quality check to see publish gates and suggestions.
                </Alert>
              )}
            </Stack>
          )}

          {intelligenceTab === 'distribution' && (
            <Stack spacing={2}>
              <Button size="small" variant="contained" onClick={handleGenerateDistributionAssets} disabled={intelligenceLoading}>
                Generate Assets
              </Button>
              {distributionAssets.length === 0 ? (
                <Alert severity="info" variant="outlined">
                  Save the post, then generate platform snippets, previews, alt text, summaries, and tracked links.
                </Alert>
              ) : (
                <Stack spacing={1.25}>
                  {distributionAssets.map((asset) => (
                    <Box key={asset.uuid} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1, p: 1.25 }}>
                      <Stack spacing={1}>
                        <Stack direction="row" justifyContent="space-between" spacing={1}>
                          <Stack direction="row" spacing={0.75} alignItems="center">
                            <Chip size="small" label={asset.platform} variant="outlined" />
                            <Chip size="small" label={asset.status} color={asset.status === 'approved' ? 'success' : 'default'} />
                          </Stack>
                          <Stack direction="row" spacing={0.5}>
                            <Button size="small" onClick={() => handleCopyAsset(asset)}>Copy</Button>
                            {asset.status === 'pending' && (
                              <Button size="small" onClick={() => handleApproveAsset(asset)}>Approve</Button>
                            )}
                          </Stack>
                        </Stack>
                        <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
                          {asset.content}
                        </Typography>
                        {asset.tracked_url && (
                          <Typography variant="caption" color="primary" sx={{ wordBreak: 'break-all' }}>
                            {asset.tracked_url}
                          </Typography>
                        )}
                      </Stack>
                    </Box>
                  ))}
                </Stack>
              )}
            </Stack>
          )}
        </Box>
      </Drawer>

      {/* ===== AI Writer Drawer (Right) ===== */}
      <Drawer
        anchor="right"
        open={aiDrawerOpen}
        onClose={() => setAiDrawerOpen(false)}
        variant="temporary"
        ModalProps={{ keepMounted: true }}
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 2,
          '& .MuiDrawer-paper': {
            width: { xs: '100%', sm: 380 },
            p: 0,
          }
        }}
      >
        <AiWriterPanel
          initialTopic={aiState?.title || ''}
          initialKeywords={aiState?.seoKeywords || []}
          onInsert={handleAiInsert}
          onReplace={handleAiReplace}
          onMetadataFill={handleAiMetadataFill}
        />
      </Drawer>
    </Box>
  );
}
