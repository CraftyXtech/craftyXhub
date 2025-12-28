import { useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

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
import Slider from '@mui/material/Slider';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';
import IconButton from '@mui/material/IconButton';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';

// TinyMCE
import { Editor } from '@tinymce/tinymce-react';
import 'tinymce/tinymce';
import 'tinymce/models/dom/model';
import 'tinymce/themes/silver';
import 'tinymce/icons/default';
import 'tinymce/skins/content/default/content';

// Icons
import {
  IconSparkles,
  IconFileText,
  IconCopy,
  IconDownload,
  IconSend,
  IconRefresh,
  IconArrowRight,
} from '@tabler/icons-react';

// API
import { generateBlog, saveDraft, getDrafts } from '@/api/services/aiService';
import { createPost } from '@/api/services/postService';
import { getCategories } from '@/api/services/categoryService';

// Utils
import { useTheme } from '@mui/material/styles';
import { useEffect } from 'react';

const BLOG_TYPES = [
  { value: 'how-to', label: 'How-To Guide' },
  { value: 'listicle', label: 'Listicle' },
  { value: 'tutorial', label: 'Tutorial' },
  { value: 'opinion', label: 'Opinion/Editorial' },
  { value: 'news', label: 'News Article' },
  { value: 'review', label: 'Product Review' },
  { value: 'comparison', label: 'Comparison' },
  { value: 'case-study', label: 'Case Study' },
];

const TONES = [
  { value: 'professional', label: 'Professional' },
  { value: 'casual', label: 'Casual' },
  { value: 'friendly', label: 'Friendly' },
  { value: 'authoritative', label: 'Authoritative' },
  { value: 'humorous', label: 'Humorous' },
  { value: 'educational', label: 'Educational' },
];

const LENGTHS = [
  { value: 'short', label: 'Short (~500 words)' },
  { value: 'medium', label: 'Medium (~1000 words)' },
  { value: 'long', label: 'Long (~1500 words)' },
  { value: 'very-long', label: 'Very Long (~2500+ words)' },
];

const MODELS = [
  { value: 'gpt-5-mini', label: 'GPT-5 Mini (Fast)' },
  { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
  { value: 'gpt-4o', label: 'GPT-4o (Best quality)' },
];

/**
 * AI Writer Dashboard - Standalone AI content generation page
 */
export default function AiWriter() {
  const navigate = useNavigate();
  const theme = useTheme();
  const editorRef = useRef(null);

  // Tab state
  const [activeTab, setActiveTab] = useState(0);

  // Generation form state
  const [topic, setTopic] = useState('');
  const [blogType, setBlogType] = useState('how-to');
  const [keywords, setKeywords] = useState('');
  const [audience, setAudience] = useState('');
  const [tone, setTone] = useState('professional');
  const [length, setLength] = useState('medium');
  const [model, setModel] = useState('gpt-5-mini');
  const [creativity, setCreativity] = useState(0.7);

  // Generation state
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [generationTime, setGenerationTime] = useState(null);
  const [editorContent, setEditorContent] = useState('');

  // Drafts state
  const [drafts, setDrafts] = useState([]);
  const [draftsLoading, setDraftsLoading] = useState(false);

  // Publishing state
  const [publishing, setPublishing] = useState(false);
  const [categoryId, setCategoryId] = useState('');
  const [categories, setCategories] = useState([]);

  // Load drafts and categories
  useEffect(() => {
    const loadData = async () => {
      try {
        setDraftsLoading(true);
        const [draftsRes, catRes] = await Promise.all([
          getDrafts(0, 10),
          getCategories()
        ]);
        setDrafts(draftsRes.drafts || []);
        setCategories(catRes.categories || catRes || []);
      } catch (err) {
        console.error('Failed to load data:', err);
      } finally {
        setDraftsLoading(false);
      }
    };
    loadData();
  }, []);

  // Handle generation
  const handleGenerate = useCallback(async () => {
    if (!topic.trim()) {
      setError('Please enter a topic');
      return;
    }

    try {
      setGenerating(true);
      setError(null);
      setGeneratedContent(null);

      const result = await generateBlog({
        topic,
        blog_type: blogType,
        keywords: keywords.split(',').map(k => k.trim()).filter(k => k),
        audience: audience || null,
        word_count: length,
        tone,
        model,
        creativity,
        use_web_search: true,
        save_draft: true,
        publish_post: false,
      });

      setGeneratedContent(result.blog_post);
      setGenerationTime(result.generation_time);

      // Convert to HTML and set in editor
      const html = blogPostToHtml(result.blog_post);
      setEditorContent(html);
      if (editorRef.current) {
        editorRef.current.setContent(html);
      }

      // Refresh drafts
      const draftsRes = await getDrafts(0, 10);
      setDrafts(draftsRes.drafts || []);
    } catch (err) {
      console.error('Generation failed:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to generate content');
    } finally {
      setGenerating(false);
    }
  }, [topic, blogType, keywords, audience, tone, length, model, creativity]);

  // Convert blog post to HTML
  const blogPostToHtml = (post) => {
    if (!post) return '';
    
    let html = `<h1>${post.title}</h1>\n`;
    
    if (post.summary) {
      html += `<p><em>${post.summary}</em></p>\n`;
    }
    
    post.sections?.forEach(section => {
      html += `<h2>${section.heading}</h2>\n`;
      const bodyHtml = section.body_markdown
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/^/, '<p>')
        .replace(/$/, '</p>');
      html += bodyHtml + '\n';
    });

    return html;
  };

  // Handle copy
  const handleCopy = useCallback(() => {
    const content = editorRef.current ? editorRef.current.getContent() : editorContent;
    navigator.clipboard.writeText(content);
  }, [editorContent]);

  // Handle export
  const handleExport = useCallback(() => {
    const content = editorRef.current ? editorRef.current.getContent() : editorContent;
    const blob = new Blob([content], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${topic.replace(/\s+/g, '-').toLowerCase() || 'ai-content'}.html`;
    link.click();
    URL.revokeObjectURL(url);
  }, [editorContent, topic]);

  // Handle publish as post
  const handlePublishAsPost = useCallback(async () => {
    const content = editorRef.current ? editorRef.current.getContent() : editorContent;
    
    if (!content.trim()) {
      setError('No content to publish');
      return;
    }

    try {
      setPublishing(true);
      setError(null);

      const formData = new FormData();
      formData.append('title', generatedContent?.title || topic || 'Untitled');
      formData.append('content', content);
      formData.append('excerpt', generatedContent?.summary || '');
      formData.append('meta_title', generatedContent?.seo_title || '');
      formData.append('meta_description', generatedContent?.seo_description || '');
      formData.append('is_published', 'false'); // Save as draft first
      
      if (categoryId) {
        formData.append('category_id', categoryId);
      }

      await createPost(formData);
      navigate('/dashboard/posts');
    } catch (err) {
      console.error('Failed to publish:', err);
      setError(err.response?.data?.detail || 'Failed to create post');
    } finally {
      setPublishing(false);
    }
  }, [editorContent, generatedContent, topic, categoryId, navigate]);

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 3 }}>
        <IconSparkles size={28} />
        <Box>
          <Typography variant="h4" fontWeight={600}>
            AI Writer
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Generate blog posts with AI assistance
          </Typography>
        </Box>
      </Stack>

      {/* Tabs */}
      <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ mb: 3 }}>
        <Tab label="Generate" icon={<IconSparkles size={18} />} iconPosition="start" />
        <Tab label="My Drafts" icon={<IconFileText size={18} />} iconPosition="start" />
      </Tabs>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Generate Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {/* Left: Generation Form */}
          <Grid item xs={12} md={4}>
            <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
              <CardContent>
                <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                  Generate Content
                </Typography>

                <Stack spacing={2}>
                  <TextField
                    label="Topic / Title Idea"
                    placeholder="e.g., How to Start a Successful Blog in 2024"
                    fullWidth
                    size="small"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    required
                  />

                  <FormControl fullWidth size="small">
                    <InputLabel>Blog Type</InputLabel>
                    <Select value={blogType} onChange={(e) => setBlogType(e.target.value)} label="Blog Type">
                      {BLOG_TYPES.map(t => (
                        <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  <TextField
                    label="SEO Keywords"
                    placeholder="keyword1, keyword2"
                    fullWidth
                    size="small"
                    value={keywords}
                    onChange={(e) => setKeywords(e.target.value)}
                    helperText="Comma-separated"
                  />

                  <TextField
                    label="Target Audience"
                    placeholder="e.g., beginners, developers"
                    fullWidth
                    size="small"
                    value={audience}
                    onChange={(e) => setAudience(e.target.value)}
                  />

                  <FormControl fullWidth size="small">
                    <InputLabel>Tone</InputLabel>
                    <Select value={tone} onChange={(e) => setTone(e.target.value)} label="Tone">
                      {TONES.map(t => (
                        <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  <FormControl fullWidth size="small">
                    <InputLabel>Length</InputLabel>
                    <Select value={length} onChange={(e) => setLength(e.target.value)} label="Length">
                      {LENGTHS.map(l => (
                        <MenuItem key={l.value} value={l.value}>{l.label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  <FormControl fullWidth size="small">
                    <InputLabel>AI Model</InputLabel>
                    <Select value={model} onChange={(e) => setModel(e.target.value)} label="AI Model">
                      {MODELS.map(m => (
                        <MenuItem key={m.value} value={m.value}>{m.label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Creativity: {creativity}
                    </Typography>
                    <Slider
                      size="small"
                      value={creativity}
                      onChange={(e, val) => setCreativity(val)}
                      min={0}
                      max={1}
                      step={0.1}
                      marks={[
                        { value: 0, label: 'Precise' },
                        { value: 1, label: 'Creative' },
                      ]}
                    />
                  </Box>

                  <Button
                    variant="contained"
                    fullWidth
                    size="large"
                    onClick={handleGenerate}
                    disabled={generating || !topic.trim()}
                    startIcon={generating ? <CircularProgress size={18} color="inherit" /> : <IconSparkles size={18} />}
                  >
                    {generating ? 'Generating...' : 'Generate Blog Post'}
                  </Button>

                  {generationTime && (
                    <Typography variant="caption" color="text.secondary" textAlign="center">
                      Generated in {generationTime}s
                    </Typography>
                  )}
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          {/* Right: Editor & Preview */}
          <Grid item xs={12} md={8}>
            <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
              <CardContent>
                {/* Toolbar */}
                <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                  <Typography variant="h6" fontWeight={600}>
                    {generatedContent?.title || 'Generated Content'}
                  </Typography>
                  <Stack direction="row" spacing={1}>
                    <IconButton size="small" onClick={handleCopy} title="Copy HTML">
                      <IconCopy size={18} />
                    </IconButton>
                    <IconButton size="small" onClick={handleExport} title="Export HTML">
                      <IconDownload size={18} />
                    </IconButton>
                    <IconButton size="small" onClick={handleGenerate} disabled={generating} title="Regenerate">
                      <IconRefresh size={18} />
                    </IconButton>
                  </Stack>
                </Stack>

                {/* Generated tags */}
                {generatedContent?.tags && (
                  <Box sx={{ mb: 2 }}>
                    {generatedContent.tags.map((tag, i) => (
                      <Chip key={i} label={tag} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                    ))}
                  </Box>
                )}

                {/* TinyMCE Editor */}
                <Box sx={{ mb: 2 }}>
                  <Editor
                    licenseKey="gpl"
                    onInit={(evt, editor) => {
                      editorRef.current = editor;
                    }}
                    initialValue={editorContent}
                    onEditorChange={(content) => setEditorContent(content)}
                    init={{
                      height: 450,
                      menubar: false,
                      toolbar: 'undo redo | blocks | bold italic | alignleft aligncenter alignright | bullist numlist | removeformat',
                      content_style: theme.palette.mode === 'dark'
                        ? 'body { font-family: "Open Sans", sans-serif; font-size: 14px; color: #fff; background-color: #1a1a1a; }'
                        : 'body { font-family: "Open Sans", sans-serif; font-size: 14px; color: #000; background-color: #fff; }',
                      branding: false,
                    }}
                  />
                </Box>

                <Divider sx={{ my: 2 }} />

                {/* Publish Actions */}
                <Stack direction="row" spacing={2} alignItems="center">
                  <FormControl size="small" sx={{ minWidth: 200 }}>
                    <InputLabel>Category</InputLabel>
                    <Select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} label="Category">
                      <MenuItem value="">No category</MenuItem>
                      {categories.map((cat) => (
                        <MenuItem key={cat.id} value={cat.id}>{cat.name}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <Button
                    variant="contained"
                    onClick={handlePublishAsPost}
                    disabled={publishing || !editorContent}
                    startIcon={publishing ? <CircularProgress size={16} color="inherit" /> : <IconSend size={18} />}
                  >
                    Save as Post Draft
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={() => navigate('/dashboard/posts/create')}
                    endIcon={<IconArrowRight size={18} />}
                  >
                    Open in Full Editor
                  </Button>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Drafts Tab */}
      {activeTab === 1 && (
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
          <CardContent>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
              Recent AI Drafts
            </Typography>

            {draftsLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : drafts.length === 0 ? (
              <Typography color="text.secondary" textAlign="center" sx={{ py: 4 }}>
                No drafts yet. Generate some content to see them here.
              </Typography>
            ) : (
              <Stack spacing={2}>
                {drafts.map((draft) => (
                  <Paper key={draft.id} variant="outlined" sx={{ p: 2 }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                      <Box>
                        <Typography variant="subtitle1" fontWeight={600}>
                          {draft.name || 'Untitled Draft'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(draft.created_at).toLocaleDateString()} • {draft.model_used || 'AI'}
                        </Typography>
                      </Box>
                      <Button size="small" variant="outlined">
                        Open
                      </Button>
                    </Stack>
                  </Paper>
                ))}
              </Stack>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
}
