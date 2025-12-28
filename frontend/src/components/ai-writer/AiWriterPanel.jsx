import { useState, useCallback } from 'react';
import PropTypes from 'prop-types';

// MUI
import Box from '@mui/material/Box';
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
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import IconButton from '@mui/material/IconButton';

// Icons
import {
  IconSparkles,
  IconChevronDown,
  IconPlus,
  IconCopy,
  IconRefresh,
} from '@tabler/icons-react';

// API
import { generateBlog } from '@/api/services/aiService';

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
 * AiWriterPanel - AI content generation sidebar
 * 
 * @param {function} onInsert - Callback to insert generated content into editor
 */
export default function AiWriterPanel({ onInsert }) {
  // Form state
  const [topic, setTopic] = useState('');
  const [blogType, setBlogType] = useState('how-to');
  const [keywords, setKeywords] = useState('');
  const [audience, setAudience] = useState('');
  const [tone, setTone] = useState('professional');
  const [length, setLength] = useState('medium');
  const [model, setModel] = useState('gpt-5-mini');
  const [creativity, setCreativity] = useState(0.7);
  const [useWebSearch, setUseWebSearch] = useState(true);

  // Generation state
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [generationTime, setGenerationTime] = useState(null);

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
        use_web_search: useWebSearch,
        save_draft: true,
        publish_post: false,
      });

      setGeneratedContent(result.blog_post);
      setGenerationTime(result.generation_time);
    } catch (err) {
      console.error('Generation failed:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to generate content');
    } finally {
      setGenerating(false);
    }
  }, [topic, blogType, keywords, audience, tone, length, model, creativity, useWebSearch]);

  // Convert blog post to HTML for insertion
  const getContentHtml = useCallback(() => {
    if (!generatedContent) return '';

    let html = `<h1>${generatedContent.title}</h1>\n`;
    
    generatedContent.sections?.forEach(section => {
      html += `<h2>${section.heading}</h2>\n`;
      // Convert markdown to basic HTML
      const bodyHtml = section.body_markdown
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/^/, '<p>')
        .replace(/$/, '</p>');
      html += bodyHtml + '\n';
    });

    return html;
  }, [generatedContent]);

  // Handle insert
  const handleInsert = useCallback(() => {
    if (onInsert && generatedContent) {
      onInsert(getContentHtml());
    }
  }, [onInsert, generatedContent, getContentHtml]);

  // Handle copy
  const handleCopy = useCallback(() => {
    const html = getContentHtml();
    navigator.clipboard.writeText(html);
  }, [getContentHtml]);

  return (
    <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', height: '100%' }}>
      <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
          <IconSparkles size={20} />
          <Typography variant="h6" fontWeight={600}>
            AI Writer
          </Typography>
        </Stack>

        {/* Error */}
        {error && (
          <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Form */}
        <Box sx={{ flex: 1, overflowY: 'auto', pb: 2 }}>
          <Stack spacing={2}>
            {/* Topic */}
            <TextField
              label="Topic / Title Idea"
              placeholder="e.g., How to Start a Successful Blog in 2024"
              fullWidth
              size="small"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              required
            />

            {/* Blog Type */}
            <FormControl fullWidth size="small">
              <InputLabel>Blog Type</InputLabel>
              <Select
                value={blogType}
                onChange={(e) => setBlogType(e.target.value)}
                label="Blog Type"
              >
                {BLOG_TYPES.map(t => (
                  <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Keywords */}
            <TextField
              label="SEO Keywords"
              placeholder="keyword1, keyword2, keyword3"
              fullWidth
              size="small"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              helperText="Comma-separated"
            />

            {/* Advanced Options */}
            <Accordion elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
              <AccordionSummary expandIcon={<IconChevronDown size={16} />}>
                <Typography variant="body2">Advanced Options</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Stack spacing={2}>
                  {/* Audience */}
                  <TextField
                    label="Target Audience"
                    placeholder="e.g., beginners, developers, marketers"
                    fullWidth
                    size="small"
                    value={audience}
                    onChange={(e) => setAudience(e.target.value)}
                  />

                  {/* Tone */}
                  <FormControl fullWidth size="small">
                    <InputLabel>Tone</InputLabel>
                    <Select
                      value={tone}
                      onChange={(e) => setTone(e.target.value)}
                      label="Tone"
                    >
                      {TONES.map(t => (
                        <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  {/* Length */}
                  <FormControl fullWidth size="small">
                    <InputLabel>Length</InputLabel>
                    <Select
                      value={length}
                      onChange={(e) => setLength(e.target.value)}
                      label="Length"
                    >
                      {LENGTHS.map(l => (
                        <MenuItem key={l.value} value={l.value}>{l.label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  {/* Model */}
                  <FormControl fullWidth size="small">
                    <InputLabel>AI Model</InputLabel>
                    <Select
                      value={model}
                      onChange={(e) => setModel(e.target.value)}
                      label="AI Model"
                    >
                      {MODELS.map(m => (
                        <MenuItem key={m.value} value={m.value}>{m.label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  {/* Creativity */}
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
                </Stack>
              </AccordionDetails>
            </Accordion>

            {/* Generate Button */}
            <Button
              variant="contained"
              fullWidth
              onClick={handleGenerate}
              disabled={generating || !topic.trim()}
              startIcon={
                generating
                  ? <CircularProgress size={16} color="inherit" />
                  : <IconSparkles size={16} />
              }
            >
              {generating ? 'Generating...' : 'Generate Blog Post'}
            </Button>

            {/* Generated Content */}
            {generatedContent && (
              <>
                <Divider />
                
                <Box>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                    <Typography variant="subtitle2" fontWeight={600}>
                      Generated Content
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {generationTime}s
                    </Typography>
                  </Stack>

                  {/* Title */}
                  <Typography variant="h6" sx={{ mb: 1 }}>
                    {generatedContent.title}
                  </Typography>

                  {/* Summary */}
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {generatedContent.summary}
                  </Typography>

                  {/* Tags */}
                  <Box sx={{ mb: 2 }}>
                    {generatedContent.tags?.map((tag, i) => (
                      <Chip key={i} label={tag} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                    ))}
                  </Box>

                  {/* Actions */}
                  <Stack direction="row" spacing={1}>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<IconPlus size={16} />}
                      onClick={handleInsert}
                    >
                      Insert to Editor
                    </Button>
                    <IconButton size="small" onClick={handleCopy} title="Copy HTML">
                      <IconCopy size={16} />
                    </IconButton>
                    <IconButton size="small" onClick={handleGenerate} title="Regenerate">
                      <IconRefresh size={16} />
                    </IconButton>
                  </Stack>
                </Box>
              </>
            )}
          </Stack>
        </Box>
      </CardContent>
    </Card>
  );
}

AiWriterPanel.propTypes = {
  onInsert: PropTypes.func.isRequired,
};
