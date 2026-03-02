import { useState, useCallback, useEffect } from 'react';
import PropTypes from 'prop-types';

// MUI
import Box from '@mui/material/Box';
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
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import Collapse from '@mui/material/Collapse';
import Link from '@mui/material/Link';
import Tooltip from '@mui/material/Tooltip';

// Icons
import {
  IconSparkles,
  IconPlus,
  IconReplace,
  IconCopy,
  IconRefresh,
  IconWorldSearch,
  IconExternalLink,
} from '@tabler/icons-react';

// API
import { generateBlog, getBlogOptions } from '@/api/services/aiService';

// Utils
import { markdownToHtml } from '@/utils/markdownToHtml';

const FALLBACK_OPTIONS = {
  blog_types: [
    { value: 'how-to', label: 'How-To Guide' },
    { value: 'listicle', label: 'Listicle' },
    { value: 'tutorial', label: 'Tutorial' },
    { value: 'opinion', label: 'Opinion' },
    { value: 'news', label: 'News' },
    { value: 'review', label: 'Review' },
    { value: 'comparison', label: 'Comparison' },
    { value: 'case-study', label: 'Case Study' },
  ],
  tones: [
    { value: 'professional', label: 'Professional' },
    { value: 'casual', label: 'Casual' },
    { value: 'friendly', label: 'Friendly' },
    { value: 'authoritative', label: 'Authoritative' },
    { value: 'humorous', label: 'Humorous' },
    { value: 'educational', label: 'Educational' },
  ],
  audiences: [
    { value: 'general', label: 'General' },
    { value: 'beginners', label: 'Beginners' },
    { value: 'developers', label: 'Developers' },
    { value: 'marketers', label: 'Marketers' },
    { value: 'professionals', label: 'Professionals' },
  ],
  lengths: [
    { value: 'short', label: 'Short (~300 words)' },
    { value: 'medium', label: 'Medium (~500 words)' },
    { value: 'long', label: 'Long (~1000 words)' },
    { value: 'very-long', label: 'Very Long (~1500+ words)' },
  ],
  models: [
    { value: 'claude-sonnet-4.6', label: 'Sonnet 4.6' },
  ],
};

/**
 * AiWriterPanel — Linear.app-inspired compact AI content generation panel
 * Design: 8px spacing grid, 4px sub-grid for dense areas, minimal visual noise
 */
export default function AiWriterPanel({ onInsert, onReplace, onMetadataFill }) {
  const [options, setOptions] = useState(FALLBACK_OPTIONS);
  const [topic, setTopic] = useState('');
  const [blogType, setBlogType] = useState('how-to');
  const [keywords, setKeywords] = useState('');
  const [audience, setAudience] = useState('general');
  const [tone, setTone] = useState('professional');
  const [length, setLength] = useState('medium');
  const [model, setModel] = useState('claude-sonnet-4.6');
  const [creativity, setCreativity] = useState(0.7);
  const [webSearchEnabled, setWebSearchEnabled] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [generationTime, setGenerationTime] = useState(null);
  const [searchSources, setSearchSources] = useState(null);
  const [showSources, setShowSources] = useState(false);

  useEffect(() => {
    const loadOptions = async () => {
      try {
        const res = await getBlogOptions();
        if (res) {
          setOptions(res);
          if (res.models?.length > 0 && !res.models.find(m => m.value === model)) {
            setModel(res.models[0].value);
          }
        }
      } catch { /* fall back silently */ }
    };
    loadOptions();
  }, []);

  const handleGenerate = useCallback(async () => {
    if (!topic.trim()) { setError('Enter a topic'); return; }
    try {
      setGenerating(true); setError(null); setGeneratedContent(null); setSearchSources(null);
      const result = await generateBlog({
        topic, blog_type: blogType,
        keywords: keywords.split(',').map(k => k.trim()).filter(k => k),
        audience: audience || null, word_count: length, tone, model, creativity,
        web_search: webSearchEnabled,
        save_draft: true, publish_post: false,
      });
      setGeneratedContent(result.blog_post);
      setGenerationTime(result.generation_time);
      if (result.search_sources) {
        setSearchSources(result.search_sources);
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Generation failed');
    } finally { setGenerating(false); }
  }, [topic, blogType, keywords, audience, tone, length, model, creativity, webSearchEnabled]);

  const getContentHtml = useCallback(() => {
    if (!generatedContent) return '';
    let html = `<h1>${generatedContent.title}</h1>\n`;
    generatedContent.sections?.forEach(section => {
      html += `<h2>${section.heading}</h2>\n`;
      html += markdownToHtml(section.body_markdown) + '\n';
    });
    return html;
  }, [generatedContent]);

  const getMetadata = useCallback(() => {
    if (!generatedContent) return null;
    return {
      title: generatedContent.title, slug: generatedContent.slug,
      excerpt: generatedContent.summary, metaTitle: generatedContent.seo_title,
      metaDescription: generatedContent.seo_description, tags: generatedContent.tags || [],
    };
  }, [generatedContent]);

  const handleInsert = useCallback(() => {
    if (onInsert && generatedContent) {
      onInsert(getContentHtml());
      if (onMetadataFill) onMetadataFill(getMetadata());
    }
  }, [onInsert, onMetadataFill, generatedContent, getContentHtml, getMetadata]);

  const handleReplace = useCallback(() => {
    const fn = onReplace || onInsert;
    if (fn && generatedContent) {
      fn(getContentHtml());
      if (onMetadataFill) onMetadataFill(getMetadata());
    }
  }, [onInsert, onReplace, onMetadataFill, generatedContent, getContentHtml, getMetadata]);

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(getContentHtml());
  }, [getContentHtml]);

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Header — 16px horizontal padding (2 * 8px grid) */}
      <Box sx={{ px: 2, py: 1.5, borderBottom: '1px solid', borderColor: 'divider', flexShrink: 0 }}>
        <Stack direction="row" alignItems="center" spacing={1}>
          <IconSparkles size={16} />
          <Typography variant="subtitle2" fontWeight={600} sx={{ fontSize: 13 }}>
            AI Writer
          </Typography>
        </Stack>
      </Box>

      {/* Scrollable Form */}
      <Box sx={{ flex: 1, overflowY: 'auto', overflowX: 'hidden' }}>
        {/* Error */}
        {error && (
          <Alert
            severity="error"
            onClose={() => setError(null)}
            sx={{ m: 1, py: 0, '& .MuiAlert-message': { fontSize: 12, py: 0.5 } }}
            variant="outlined"
          >
            {error}
          </Alert>
        )}

        {/* 16px padding, 8px gaps — Linear's grid */}
        <Box sx={{ px: 2, py: 1.5 }}>
          <Stack spacing={2.5}>
            {/* Topic */}
            <TextField
              placeholder="Topic or title idea..."
              fullWidth size="small"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />

            {/* Type */}
            <FormControl fullWidth size="small">
              <InputLabel>Type</InputLabel>
              <Select value={blogType} onChange={(e) => setBlogType(e.target.value)} label="Type">
                {options.blog_types.map(t => <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>)}
              </Select>
            </FormControl>

            {/* Tone */}
            <FormControl fullWidth size="small">
              <InputLabel>Tone</InputLabel>
              <Select value={tone} onChange={(e) => setTone(e.target.value)} label="Tone">
                {options.tones.map(t => <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>)}
              </Select>
            </FormControl>

            {/* Audience */}
            <FormControl fullWidth size="small">
              <InputLabel>Audience</InputLabel>
              <Select value={audience} onChange={(e) => setAudience(e.target.value)} label="Audience">
                {options.audiences.map(a => <MenuItem key={a.value} value={a.value}>{a.label}</MenuItem>)}
              </Select>
            </FormControl>

            {/* Length */}
            <FormControl fullWidth size="small">
              <InputLabel>Length</InputLabel>
              <Select value={length} onChange={(e) => setLength(e.target.value)} label="Length">
                {options.lengths.map(l => <MenuItem key={l.value} value={l.value}>{l.label}</MenuItem>)}
              </Select>
            </FormControl>

            {/* Keywords */}
            <TextField
              placeholder="SEO keywords (comma-separated)"
              fullWidth size="small"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
            />

            {/* Model */}
            <FormControl fullWidth size="small">
              <InputLabel>Model</InputLabel>
              <Select value={model} onChange={(e) => setModel(e.target.value)} label="Model">
                {options.models.map(m => <MenuItem key={m.value} value={m.value}>{m.label}</MenuItem>)}
              </Select>
            </FormControl>

            {/* Web Search Toggle */}
            <Box sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1, px: 1.5, py: 0.75 }}>
              <FormControlLabel
                sx={{ m: 0, width: '100%', justifyContent: 'space-between' }}
                control={
                  <Switch
                    checked={webSearchEnabled}
                    onChange={(e) => setWebSearchEnabled(e.target.checked)}
                    size="small"
                  />
                }
                labelPlacement="start"
                label={
                  <Typography variant="body2" sx={{ fontSize: 13 }}>
                    Web Search
                  </Typography>
                }
              />
            </Box>

            {/* Creativity */}
            <Box>
              <Typography variant="caption" color="text.secondary">
                Creativity {creativity}
              </Typography>
              <Slider
                size="small"
                value={creativity}
                onChange={(e, val) => setCreativity(val)}
                min={0} max={1} step={0.1}
                sx={{ mt: 0.5 }}
              />
            </Box>

            {/* Generate */}
            <Button
              variant="contained" fullWidth
              onClick={handleGenerate}
              disabled={generating || !topic.trim()}
              startIcon={generating ? <CircularProgress size={14} color="inherit" /> : <IconSparkles size={14} />}
              sx={{ py: 0.75, fontSize: 13, fontWeight: 600, mt: 0.5 }}
            >
              {generating ? 'Generating...' : 'Generate Post'}
            </Button>
          </Stack>
        </Box>

        {/* Generated Result */}
        {generatedContent && (
          <Box sx={{ px: 2, pb: 2 }}>
            <Divider sx={{ mb: 1.5 }} />

            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 0.5 }}>
              <Typography variant="caption" fontWeight={600} sx={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>
                Result
              </Typography>
              <Typography variant="caption" color="text.disabled" sx={{ fontSize: 11 }}>
                {generationTime}s
              </Typography>
            </Stack>

            <Typography variant="body2" fontWeight={600} sx={{ fontSize: 13, mb: 0.5, lineHeight: 1.3 }}>
              {generatedContent.title}
            </Typography>

            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1, lineHeight: 1.4, fontSize: 12 }}>
              {generatedContent.summary?.slice(0, 100)}{generatedContent.summary?.length > 100 ? '...' : ''}
            </Typography>

            {generatedContent.tags?.length > 0 && (
              <Box sx={{ mb: 1.5 }}>
                {generatedContent.tags.slice(0, 4).map((tag, i) => (
                  <Chip key={i} label={tag} size="small"
                    sx={{ mr: 0.5, mb: 0.5, height: 20, fontSize: 11, '& .MuiChip-label': { px: 1 } }}
                  />
                ))}
              </Box>
            )}

            <Stack spacing={0.75}>
              <Button variant="contained" size="small" fullWidth
                startIcon={<IconReplace size={14} />} onClick={handleReplace}
                sx={{ py: 0.5, fontSize: 12, fontWeight: 600 }}
              >
                Use as Post
              </Button>
              <Stack direction="row" spacing={0.5}>
                <Button variant="outlined" size="small" fullWidth
                  startIcon={<IconPlus size={14} />} onClick={handleInsert}
                  sx={{ py: 0.375, fontSize: 12 }}
                >
                  Append
                </Button>
                <IconButton size="small" onClick={handleCopy} title="Copy"
                  sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1, width: 32, height: 32 }}>
                  <IconCopy size={14} />
                </IconButton>
                <IconButton size="small" onClick={handleGenerate} title="Regenerate"
                  sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1, width: 32, height: 32 }}>
                  <IconRefresh size={14} />
                </IconButton>
              </Stack>
            </Stack>

            {/* Sources */}
            {searchSources && searchSources.length > 0 && (
              <Box sx={{ mt: 1 }}>
                <Stack
                  direction="row"
                  alignItems="center"
                  spacing={0.5}
                  sx={{ cursor: 'pointer', mb: 0.5 }}
                  onClick={() => setShowSources(!showSources)}
                >
                  <IconWorldSearch size={12} />
                  <Typography
                    variant="caption"
                    color="primary"
                    sx={{ fontSize: 11, fontWeight: 600 }}
                  >
                    {searchSources.length} sources used
                  </Typography>
                </Stack>
                <Collapse in={showSources}>
                  <Stack spacing={0.5}>
                    {searchSources.slice(0, 5).map((src, i) => (
                      <Link
                        key={i}
                        href={src.url}
                        target="_blank"
                        rel="noopener"
                        underline="hover"
                        sx={{
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: 0.5,
                          fontSize: 11,
                          color: 'text.secondary',
                          lineHeight: 1.3,
                        }}
                      >
                        <IconExternalLink size={10} style={{ marginTop: 2, flexShrink: 0 }} />
                        <span>
                          {src.title?.length > 60
                            ? src.title.slice(0, 60) + '...'
                            : src.title}
                        </span>
                      </Link>
                    ))}
                  </Stack>
                </Collapse>
              </Box>
            )}
          </Box>
        )}
      </Box>
    </Box>
  );
}

AiWriterPanel.propTypes = {
  onInsert: PropTypes.func.isRequired,
  onReplace: PropTypes.func,
  onMetadataFill: PropTypes.func,
};
