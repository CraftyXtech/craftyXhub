import MarkdownIt from 'markdown-it';

/**
 * Enhanced Markdown Renderer for Blog Content
 * 
 * Configured for professional blog output with:
 * - Proper list indentation and spacing
 * - Definition list-style numbered items with bold headings
 * - Clean typography following industry standards
 */
const markdownRenderer = new MarkdownIt({
  html: true,       // Allow HTML tags in markdown
  linkify: true,    // Auto-convert URLs to links
  breaks: false,    // Don't convert \n to <br> (use proper paragraphs)
  typographer: true // Enable smart quotes and other typography
});

// Custom renderer for ordered list items to handle "bold title + description" pattern
const defaultListItemRender = markdownRenderer.renderer.rules.list_item_open || 
  function(tokens, idx, options, env, self) {
    return self.renderToken(tokens, idx, options);
  };

markdownRenderer.renderer.rules.list_item_open = function(tokens, idx, options, env, self) {
  // Add a class for styling numbered items with descriptions
  const token = tokens[idx];
  token.attrJoin('class', 'blog-list-item');
  return defaultListItemRender(tokens, idx, options, env, self);
};

// Custom renderer for ordered lists
const defaultOrderedListRender = markdownRenderer.renderer.rules.ordered_list_open || 
  function(tokens, idx, options, env, self) {
    return self.renderToken(tokens, idx, options);
  };

markdownRenderer.renderer.rules.ordered_list_open = function(tokens, idx, options, env, self) {
  const token = tokens[idx];
  token.attrJoin('class', 'blog-ordered-list');
  return defaultOrderedListRender(tokens, idx, options, env, self);
};

// Custom renderer for unordered lists
const defaultUnorderedListRender = markdownRenderer.renderer.rules.bullet_list_open || 
  function(tokens, idx, options, env, self) {
    return self.renderToken(tokens, idx, options);
  };

markdownRenderer.renderer.rules.bullet_list_open = function(tokens, idx, options, env, self) {
  const token = tokens[idx];
  token.attrJoin('class', 'blog-unordered-list');
  return defaultUnorderedListRender(tokens, idx, options, env, self);
};

const escapeHtml = (value = '') =>
  String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');

/**
 * Transform markdown to properly structure numbered lists with descriptions
 * Converts patterns like:
 *   1. **Title.** Description text...
 * Into properly structured HTML with the description as a nested element
 */
const preprocessBlogMarkdown = (markdown = '') => {
  if (!markdown) return '';
  
  // Pattern: numbered item with bold heading followed by description
  // Match: "1. **Bold title.** Description paragraph..."
  // This transforms markdown so the description stays properly grouped with its heading
  let processed = markdown;
  
  // Ensure proper paragraph breaks after list items with descriptions
  // This helps markdown-it parse multi-paragraph list items correctly
  processed = processed
    // Normalize line endings
    .replace(/\r\n/g, '\n')
    // Ensure list items that continue on next lines are properly indented
    // (4 spaces or 1 tab for continuation in markdown)
    .replace(/^(\d+\.\s+\*\*[^*]+\*\*[^\n]*)\n(?!\d+\.|[-*]|\s*$)/gm, '$1\n\n');
  
  return processed;
};

export const renderBlogMarkdownToHtml = (markdown = '') => {
  const processed = preprocessBlogMarkdown(markdown);
  const html = markdownRenderer.render(processed || '');
  return html;
};

export const renderBlogPostToHtml = ({ title = '', sections = [] } = {}) => {
  const htmlParts = [];

  if (title) {
    htmlParts.push(`<h1>${escapeHtml(title)}</h1>`);
  }

  sections.forEach((section) => {
    if (section?.heading) {
      htmlParts.push(`<h2>${escapeHtml(section.heading)}</h2>`);
    }
    if (section?.body_markdown) {
      htmlParts.push(renderBlogMarkdownToHtml(section.body_markdown));
    }
  });

  // Wrap in a container with blog content styles
  return `<div class="blog-content">${htmlParts.join('\n')}</div>`;
};

/**
 * CSS styles to be injected for proper blog content formatting
 * These should be added to your global styles or component styles
 */
export const BLOG_CONTENT_STYLES = `
.blog-content {
  line-height: 1.8;
  font-size: 1rem;
}

.blog-content h1,
.blog-content h2,
.blog-content h3 {
  margin-top: 2em;
  margin-bottom: 0.75em;
  line-height: 1.3;
}

.blog-content h1:first-child,
.blog-content h2:first-child {
  margin-top: 0;
}

.blog-content p {
  margin-bottom: 1.25em;
}

/* Ordered lists with definition-style items */
.blog-content .blog-ordered-list,
.blog-content ol {
  counter-reset: list-counter;
  list-style: none;
  padding-left: 0;
  margin-bottom: 1.5em;
}

.blog-content .blog-ordered-list > li,
.blog-content ol > li {
  counter-increment: list-counter;
  position: relative;
  padding-left: 2.5em;
  margin-bottom: 1.25em;
}

.blog-content .blog-ordered-list > li::before,
.blog-content ol > li::before {
  content: counter(list-counter) ".";
  position: absolute;
  left: 0;
  top: 0;
  font-weight: 700;
  color: inherit;
}

/* Description text under numbered items - when li contains multiple paragraphs */
.blog-content .blog-ordered-list > li > p,
.blog-content ol > li > p {
  margin-bottom: 0.75em;
}

.blog-content .blog-ordered-list > li > p:first-child,
.blog-content ol > li > p:first-child {
  display: inline;
}

/* Unordered lists */
.blog-content .blog-unordered-list,
.blog-content ul {
  list-style: none;
  padding-left: 0;
  margin-bottom: 1.5em;
}

.blog-content .blog-unordered-list > li,
.blog-content ul > li {
  position: relative;
  padding-left: 1.5em;
  margin-bottom: 0.75em;
}

.blog-content .blog-unordered-list > li::before,
.blog-content ul > li::before {
  content: "•";
  position: absolute;
  left: 0;
  top: 0;
  color: currentColor;
  font-weight: bold;
}

/* Nested lists */
.blog-content ol ol,
.blog-content ul ul,
.blog-content ol ul,
.blog-content ul ol {
  margin-top: 0.5em;
  margin-bottom: 0.5em;
}

/* Bold text styling for list headings */
.blog-content li strong:first-child {
  display: block;
  margin-bottom: 0.25em;
}

/* Blockquotes */
.blog-content blockquote {
  border-left: 4px solid #3b82f6;
  padding-left: 1.5em;
  margin: 1.5em 0;
  font-style: italic;
  color: #4b5563;
}

/* Code blocks */
.blog-content pre {
  background: #1f2937;
  color: #e5e7eb;
  padding: 1em 1.25em;
  border-radius: 0.5em;
  overflow-x: auto;
  margin: 1.5em 0;
  font-size: 0.875em;
  line-height: 1.6;
}

.blog-content code {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

.blog-content p code {
  background: #f3f4f6;
  padding: 0.2em 0.4em;
  border-radius: 0.25em;
  font-size: 0.875em;
}

/* Links */
.blog-content a {
  color: #3b82f6;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.blog-content a:hover {
  color: #2563eb;
}
`;
