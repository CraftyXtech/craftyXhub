export const AI_TEMPLATES = [
  // Writing
  {
    id: 'blog-ideas',
    category: 'Writing',
    icon: 'bulb',
    title: 'Blog Ideas Generator',
    description: 'Generate topics and angles by category',
    fields: ['category', 'keywords', 'tone', 'audience'],
    color: 'primary'
  },
  {
    id: 'outline-generator',
    category: 'Writing',
    icon: 'list',
    title: 'Outline Generator',
    description: 'H2/H3 with talking points and CTAs',
    fields: ['title', 'keywords', 'sections', 'tone'],
    color: 'info'
  },
  {
    id: 'section-draft',
    category: 'Writing',
    icon: 'file-plus',
    title: 'Section-by-Section Draft',
    description: 'Write sections from outline; choose length and tone',
    fields: ['outline', 'tone', 'length'],
    color: 'success'
  },
  {
    id: 'title-variants',
    category: 'Writing',
    icon: 'text',
    title: 'Title/Headline Variants',
    description: 'Generate headline options with simple scoring',
    fields: ['topic', 'keywords', 'style'],
    color: 'warning'
  },
  {
    id: 'intro-conclusion-cta',
    category: 'Writing',
    icon: 'check-circle',
    title: 'Intro/Conclusion/CTA Pack',
    description: 'Targeted hooks, closers and CTAs',
    fields: ['title', 'summary', 'cta_goal', 'tone'],
    color: 'primary'
  },
  // SEO
  {
    id: 'seo-pack',
    category: 'SEO',
    icon: 'search',
    title: 'SEO Pack',
    description: 'Meta title/description, slug, keywords, FAQ schema',
    fields: ['content', 'focus_keyword', 'audience'],
    color: 'success'
  },
  {
    id: 'image-alt-text',
    category: 'SEO',
    icon: 'img',
    title: 'Image Alt-Text Generator',
    description: 'Alt tags and captions from paragraph',
    fields: ['image_context', 'caption_style'],
    color: 'info'
  },
  {
    id: 'internal-link-suggester',
    category: 'SEO',
    icon: 'link',
    title: 'Internal Link Suggester',
    description: 'Anchor suggestions from given URL slugs',
    fields: ['content', 'available_slugs'],
    color: 'primary'
  },
  // Quality
  {
    id: 'content-refiner',
    category: 'Quality',
    icon: 'repeat',
    title: 'Content Refiner',
    description: 'Rewrite, simplify, expand, de-jargon',
    fields: ['content', 'tone', 'style'],
    color: 'info'
  },
  {
    id: 'summarizer-brief',
    category: 'Quality',
    icon: 'file-minus',
    title: 'Summarizer/Brief Builder',
    description: 'Concise brief from pasted sources or notes',
    fields: ['content', 'length'],
    color: 'primary'
  },
  {
    id: 'fact-checklist',
    category: 'Quality',
    icon: 'alert-circle',
    title: 'Fact Checklist',
    description: 'Highlight claims needing sources; add disclaimers',
    fields: ['content'],
    color: 'warning'
  },
  {
    id: 'style-adapter',
    category: 'Quality',
    icon: 'edit',
    title: 'Style/Tone Adapter',
    description: 'Adapt to brand voice and reading level',
    fields: ['content', 'tone', 'reading_level'],
    color: 'success'
  }
];

export const TEMPLATE_CATEGORIES = [
  { id: 'all', name: 'All Templates', icon: 'grid' },
  { id: 'Writing', name: 'Writing', icon: 'file-text' },
  { id: 'SEO', name: 'SEO & Optimization', icon: 'search' },
  { id: 'Quality', name: 'Quality & Editing', icon: 'check-circle' }
];

export const TONE_OPTIONS = [
  { value: 'professional', label: 'Professional' },
  { value: 'friendly', label: 'Friendly' },
  { value: 'casual', label: 'Casual' },
  { value: 'creative', label: 'Creative' },
  { value: 'enthusiastic', label: 'Enthusiastic' },
  { value: 'formal', label: 'Formal' },
  { value: 'conversational', label: 'Conversational' },
  { value: 'persuasive', label: 'Persuasive' }
];

export const LANGUAGE_OPTIONS = [
  { value: 'en-US', label: 'English (US)' },
  { value: 'en-GB', label: 'English (UK)' },
  { value: 'es', label: 'Spanish' },
  { value: 'fr', label: 'French' },
  { value: 'de', label: 'German' },
  { value: 'it', label: 'Italian' },
  { value: 'pt', label: 'Portuguese' },
  { value: 'nl', label: 'Dutch' }
];

export const LENGTH_OPTIONS = [
  { value: 'short', label: 'Short (50-100 words)' },
  { value: 'medium', label: 'Medium (100-300 words)' },
  { value: 'long', label: 'Long (300-500 words)' },
  { value: 'very-long', label: 'Very Long (500+ words)' }
];

export const getTemplateById = (id) => {
  return AI_TEMPLATES.find(template => template.id === id);
};

export const getTemplatesByCategory = (category) => {
  if (category === 'all') return AI_TEMPLATES;
  return AI_TEMPLATES.filter(template => template.category === category);
};

