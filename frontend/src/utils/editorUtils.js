/**
 * Editor Utilities
 * Conversion and helper functions for EditorJS content
 */

/**
 * Convert EditorJS blocks to HTML
 * @param {object} editorData - EditorJS output data
 * @returns {string} HTML string
 */
export const editorJsToHtml = (editorData) => {
  if (!editorData?.blocks) return '';

  return editorData.blocks.map(block => {
    switch (block.type) {
      case 'header':
        const level = block.data.level || 2;
        return `<h${level}>${block.data.text}</h${level}>`;

      case 'paragraph':
        return `<p>${block.data.text}</p>`;

      case 'list':
        const listTag = block.data.style === 'ordered' ? 'ol' : 'ul';
        const items = block.data.items.map(item => `<li>${item}</li>`).join('');
        return `<${listTag}>${items}</${listTag}>`;

      case 'quote':
        const caption = block.data.caption ? `<cite>${block.data.caption}</cite>` : '';
        return `<blockquote>${block.data.text}${caption}</blockquote>`;

      case 'code':
        return `<pre><code>${escapeHtml(block.data.code)}</code></pre>`;

      case 'image':
        const captionHtml = block.data.caption ? `<figcaption>${block.data.caption}</figcaption>` : '';
        return `<figure><img src="${block.data.file?.url || block.data.url}" alt="${block.data.caption || ''}" />${captionHtml}</figure>`;

      case 'delimiter':
        return '<hr />';

      case 'embed':
        return `<div class="embed" data-service="${block.data.service}"><iframe src="${block.data.embed}" frameborder="0" allowfullscreen></iframe></div>`;

      default:
        return '';
    }
  }).join('\n');
};

/**
 * Convert HTML to EditorJS blocks (basic conversion)
 * @param {string} html - HTML string
 * @returns {object} EditorJS data format
 */
export const htmlToEditorJs = (html) => {
  if (!html || typeof html !== 'string') {
    return { time: Date.now(), blocks: [], version: '2.28.0' };
  }

  const blocks = [];
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');
  const elements = doc.body.childNodes;

  elements.forEach(element => {
    if (element.nodeType !== Node.ELEMENT_NODE) {
      if (element.textContent?.trim()) {
        blocks.push({
          type: 'paragraph',
          data: { text: element.textContent.trim() }
        });
      }
      return;
    }

    const tagName = element.tagName.toLowerCase();

    switch (tagName) {
      case 'h1':
      case 'h2':
      case 'h3':
      case 'h4':
      case 'h5':
      case 'h6':
        blocks.push({
          type: 'header',
          data: {
            text: element.innerHTML,
            level: parseInt(tagName[1])
          }
        });
        break;

      case 'p':
        if (element.textContent?.trim()) {
          blocks.push({
            type: 'paragraph',
            data: { text: element.innerHTML }
          });
        }
        break;

      case 'ul':
      case 'ol':
        const listItems = Array.from(element.querySelectorAll('li')).map(li => li.innerHTML);
        if (listItems.length) {
          blocks.push({
            type: 'list',
            data: {
              style: tagName === 'ol' ? 'ordered' : 'unordered',
              items: listItems
            }
          });
        }
        break;

      case 'blockquote':
        blocks.push({
          type: 'quote',
          data: {
            text: element.innerHTML,
            caption: ''
          }
        });
        break;

      case 'pre':
        blocks.push({
          type: 'code',
          data: {
            code: element.textContent || ''
          }
        });
        break;

      case 'figure':
        const img = element.querySelector('img');
        const figcaption = element.querySelector('figcaption');
        if (img) {
          blocks.push({
            type: 'image',
            data: {
              file: { url: img.src },
              caption: figcaption?.textContent || img.alt || ''
            }
          });
        }
        break;

      case 'img':
        blocks.push({
          type: 'image',
          data: {
            file: { url: element.src },
            caption: element.alt || ''
          }
        });
        break;

      case 'hr':
        blocks.push({ type: 'delimiter', data: {} });
        break;

      default:
        if (element.textContent?.trim()) {
          blocks.push({
            type: 'paragraph',
            data: { text: element.innerHTML }
          });
        }
    }
  });

  return {
    time: Date.now(),
    blocks,
    version: '2.28.0'
  };
};

/**
 * Extract plain text from EditorJS blocks
 * @param {object} editorData - EditorJS data
 * @returns {string} Plain text
 */
export const extractPlainText = (editorData) => {
  if (!editorData?.blocks) return '';

  return editorData.blocks.map(block => {
    switch (block.type) {
      case 'header':
      case 'paragraph':
        return stripHtml(block.data.text || '');
      case 'list':
        return (block.data.items || []).map(item => stripHtml(item)).join(' ');
      case 'quote':
        return stripHtml(block.data.text || '');
      case 'code':
        return block.data.code || '';
      default:
        return '';
    }
  }).filter(Boolean).join(' ');
};

/**
 * Extract title from first header block
 * @param {object} editorData - EditorJS data
 * @returns {string} Title or empty string
 */
export const extractTitle = (editorData) => {
  if (!editorData?.blocks) return '';
  
  const headerBlock = editorData.blocks.find(b => b.type === 'header');
  if (headerBlock) {
    return stripHtml(headerBlock.data.text || '');
  }
  
  // Fallback: use first paragraph
  const firstParagraph = editorData.blocks.find(b => b.type === 'paragraph');
  if (firstParagraph) {
    const text = stripHtml(firstParagraph.data.text || '');
    return text.slice(0, 100);
  }
  
  return '';
};

/**
 * Calculate word count from EditorJS data
 * @param {object} editorData - EditorJS data
 * @returns {number} Word count
 */
export const calculateWordCount = (editorData) => {
  const text = extractPlainText(editorData);
  return text.split(/\s+/).filter(word => word.length > 0).length;
};

/**
 * Calculate reading time in minutes
 * @param {number} wordCount - Number of words
 * @param {number} wordsPerMinute - Reading speed (default: 200)
 * @returns {number} Reading time in minutes
 */
export const calculateReadingTime = (wordCount, wordsPerMinute = 200) => {
  return Math.max(1, Math.ceil(wordCount / wordsPerMinute));
};

/**
 * Generate excerpt from EditorJS content
 * @param {object} editorData - EditorJS data
 * @param {number} maxLength - Maximum excerpt length (default: 150)
 * @returns {string} Excerpt
 */
export const generateExcerpt = (editorData, maxLength = 150) => {
  if (!editorData?.blocks) return '';

  // Skip headers, get first paragraph content
  for (const block of editorData.blocks) {
    if (block.type === 'paragraph' && block.data.text) {
      const text = stripHtml(block.data.text);
      if (text.length > maxLength) {
        return text.slice(0, maxLength).trim() + '...';
      }
      return text;
    }
  }

  return '';
};

/**
 * Sanitize EditorJS data (remove empty blocks, clean up)
 * @param {object} editorData - EditorJS data
 * @returns {object} Sanitized data
 */
export const sanitizeEditorData = (editorData) => {
  if (!editorData?.blocks) return editorData;

  const sanitizedBlocks = editorData.blocks.filter(block => {
    switch (block.type) {
      case 'paragraph':
      case 'header':
        return block.data.text && block.data.text.trim().length > 0;
      case 'list':
        return block.data.items && block.data.items.length > 0;
      case 'quote':
        return block.data.text && block.data.text.trim().length > 0;
      case 'code':
        return block.data.code && block.data.code.trim().length > 0;
      case 'image':
        return block.data.file?.url || block.data.url;
      case 'delimiter':
        return true;
      default:
        return true;
    }
  });

  return {
    ...editorData,
    blocks: sanitizedBlocks
  };
};

/**
 * Check if EditorJS content is empty
 * @param {object} editorData - EditorJS data
 * @returns {boolean} True if empty
 */
export const isEditorEmpty = (editorData) => {
  if (!editorData?.blocks || editorData.blocks.length === 0) return true;
  
  const sanitized = sanitizeEditorData(editorData);
  return sanitized.blocks.length === 0;
};

// Helper functions
const stripHtml = (html) => {
  if (!html) return '';
  return html.replace(/<[^>]*>/g, '');
};

const escapeHtml = (text) => {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
};
