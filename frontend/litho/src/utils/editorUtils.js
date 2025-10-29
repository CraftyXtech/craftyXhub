import edjsHTML from 'editorjs-html';

/**
 * EditorJS Utility Functions
 * Handles conversion between EditorJS JSON and HTML formats
 */

// Initialize the EditorJS HTML parser
const edjsParser = edjsHTML();

/**
 * Convert EditorJS JSON data to HTML string
 * @param {Object} editorData - EditorJS data object with blocks array
 * @returns {string} HTML string
 */
export function editorJsToHtml(editorData) {
  if (!editorData || !editorData.blocks || editorData.blocks.length === 0) {
    return '';
  }

  try {
    const html = edjsParser.parse(editorData);
    return html.join('');
  } catch (error) {
    console.error('Error converting EditorJS to HTML:', error);
    return '';
  }
}

/**
 * Convert HTML string to EditorJS JSON format
 * This is a basic implementation for backward compatibility with old HTML posts
 * @param {string} htmlString - HTML content string
 * @returns {Object} EditorJS data object
 */
export function htmlToEditorJs(htmlString) {
  if (!htmlString || htmlString.trim() === '') {
    return {
      time: Date.now(),
      blocks: [],
      version: '2.28.0'
    };
  }

  try {
    // Create a temporary DOM element to parse HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = htmlString.trim();

    const blocks = [];
    const children = Array.from(tempDiv.children);

    children.forEach((element) => {
      const block = parseHtmlElement(element);
      if (block) {
        blocks.push(block);
      }
    });

    return {
      time: Date.now(),
      blocks: blocks,
      version: '2.28.0'
    };
  } catch (error) {
    console.error('Error converting HTML to EditorJS:', error);
    // Return a single paragraph block with the raw HTML as fallback
    return {
      time: Date.now(),
      blocks: [
        {
          type: 'paragraph',
          data: {
            text: htmlString
          }
        }
      ],
      version: '2.28.0'
    };
  }
}

/**
 * Parse a single HTML element into an EditorJS block
 * @param {HTMLElement} element - HTML element to parse
 * @returns {Object|null} EditorJS block object or null
 */
function parseHtmlElement(element) {
  const tagName = element.tagName.toLowerCase();
  const id = generateBlockId();

  switch (tagName) {
    case 'h1':
      return {
        id,
        type: 'header',
        data: {
          text: element.innerHTML,
          level: 1
        }
      };

    case 'h2':
      return {
        id,
        type: 'header',
        data: {
          text: element.innerHTML,
          level: 2
        }
      };

    case 'h3':
      return {
        id,
        type: 'header',
        data: {
          text: element.innerHTML,
          level: 3
        }
      };

    case 'p':
      return {
        id,
        type: 'paragraph',
        data: {
          text: element.innerHTML
        }
      };

    case 'ul':
      return {
        id,
        type: 'list',
        data: {
          style: 'unordered',
          items: Array.from(element.querySelectorAll('li')).map(li => li.innerHTML)
        }
      };

    case 'ol':
      return {
        id,
        type: 'list',
        data: {
          style: 'ordered',
          items: Array.from(element.querySelectorAll('li')).map(li => li.innerHTML)
        }
      };

    case 'blockquote':
      return {
        id,
        type: 'quote',
        data: {
          text: element.innerHTML,
          caption: '',
          alignment: 'left'
        }
      };

    case 'pre':
      const codeElement = element.querySelector('code');
      return {
        id,
        type: 'code',
        data: {
          code: codeElement ? codeElement.textContent : element.textContent
        }
      };

    case 'img':
      return {
        id,
        type: 'image',
        data: {
          file: {
            url: element.src
          },
          caption: element.alt || '',
          withBorder: false,
          stretched: false,
          withBackground: false
        }
      };

    case 'figure':
      const img = element.querySelector('img');
      const figcaption = element.querySelector('figcaption');
      if (img) {
        return {
          id,
          type: 'image',
          data: {
            file: {
              url: img.src
            },
            caption: figcaption ? figcaption.textContent : (img.alt || ''),
            withBorder: false,
            stretched: false,
            withBackground: false
          }
        };
      }
      break;

    case 'hr':
      return {
        id,
        type: 'delimiter',
        data: {}
      };

    default:
      // For unknown elements, convert to paragraph
      if (element.textContent.trim()) {
        return {
          id,
          type: 'paragraph',
          data: {
            text: element.innerHTML
          }
        };
      }
      return null;
  }
}

/**
 * Generate a unique block ID
 * @returns {string} Unique ID string
 */
function generateBlockId() {
  return `block_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Extract plain text from EditorJS data for validation
 * @param {Object} editorData - EditorJS data object
 * @returns {string} Plain text content
 */
export function extractPlainText(editorData) {
  if (!editorData || !editorData.blocks || editorData.blocks.length === 0) {
    return '';
  }

  try {
    const textParts = editorData.blocks.map(block => {
      switch (block.type) {
        case 'paragraph':
        case 'header':
          // Remove HTML tags from text
          return block.data.text ? stripHtmlTags(block.data.text) : '';

        case 'list':
          return block.data.items
            ? block.data.items.map(item => stripHtmlTags(item)).join(' ')
            : '';

        case 'quote':
          return block.data.text ? stripHtmlTags(block.data.text) : '';

        case 'code':
          return block.data.code || '';

        case 'image':
          return block.data.caption || '';

        default:
          return '';
      }
    });

    return textParts.join(' ').trim();
  } catch (error) {
    console.error('Error extracting plain text:', error);
    return '';
  }
}

/**
 * Strip HTML tags from a string
 * @param {string} html - HTML string
 * @returns {string} Plain text
 */
function stripHtmlTags(html) {
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = html;
  return tempDiv.textContent || tempDiv.innerText || '';
}

/**
 * Validate EditorJS content meets minimum length requirement
 * @param {Object} editorData - EditorJS data object
 * @param {number} minLength - Minimum character length (default: 50)
 * @returns {boolean} True if content is valid
 */
export function validateEditorContent(editorData, minLength = 50) {
  const plainText = extractPlainText(editorData);
  return plainText.length >= minLength;
}

/**
 * Sanitize EditorJS data before storage
 * Removes any potentially harmful content or malformed blocks
 * @param {Object} editorData - EditorJS data object
 * @returns {Object} Sanitized EditorJS data
 */
export function sanitizeEditorData(editorData) {
  if (!editorData || !editorData.blocks) {
    return {
      time: Date.now(),
      blocks: [],
      version: '2.28.0'
    };
  }

  try {
    // Filter out empty or invalid blocks
    const sanitizedBlocks = editorData.blocks
      .filter(block => {
        // Must have a type
        if (!block.type) return false;

        // Must have data object
        if (!block.data || typeof block.data !== 'object') return false;

        // Block-specific validation
        switch (block.type) {
          case 'paragraph':
          case 'header':
            return block.data.text && block.data.text.trim() !== '';

          case 'list':
            return block.data.items && Array.isArray(block.data.items) && block.data.items.length > 0;

          case 'quote':
            return block.data.text && block.data.text.trim() !== '';

          case 'code':
            return block.data.code !== undefined;

          case 'image':
            return block.data.file && block.data.file.url;

          case 'delimiter':
            return true;

          default:
            return true;
        }
      })
      .map(block => {
        // Ensure each block has an ID
        if (!block.id) {
          block.id = generateBlockId();
        }
        return block;
      });

    return {
      time: editorData.time || Date.now(),
      blocks: sanitizedBlocks,
      version: editorData.version || '2.28.0'
    };
  } catch (error) {
    console.error('Error sanitizing EditorJS data:', error);
    return {
      time: Date.now(),
      blocks: [],
      version: '2.28.0'
    };
  }
}

/**
 * Check if EditorJS data is empty
 * @param {Object} editorData - EditorJS data object
 * @returns {boolean} True if empty
 */
export function isEditorEmpty(editorData) {
  if (!editorData || !editorData.blocks || editorData.blocks.length === 0) {
    return true;
  }

  // Check if all blocks are empty
  return editorData.blocks.every(block => {
    switch (block.type) {
      case 'paragraph':
      case 'header':
        return !block.data.text || block.data.text.trim() === '';

      case 'list':
        return !block.data.items || block.data.items.length === 0;

      case 'quote':
        return !block.data.text || block.data.text.trim() === '';

      case 'code':
        return !block.data.code || block.data.code.trim() === '';

      case 'image':
        return !block.data.file || !block.data.file.url;

      default:
        return false;
    }
  });
}

/**
 * Extract title from EditorJS content
 * Uses first H1/H2 block, or first paragraph if no headers found
 * @param {Object} editorData - EditorJS data object
 * @returns {string} Extracted title or 'Untitled Post'
 */
export function extractTitle(editorData) {
  if (!editorData?.blocks || editorData.blocks.length === 0) {
    return 'Untitled Post';
  }

  try {
    // Find first H1 or H2 block
    const titleBlock = editorData.blocks.find(
      block => block.type === 'header' && [1, 2].includes(block.data.level)
    );

    if (titleBlock) {
      return stripHtmlTags(titleBlock.data.text).trim() || 'Untitled Post';
    }

    // Fallback to first paragraph
    const firstPara = editorData.blocks.find(
      block => block.type === 'paragraph' && block.data.text?.trim()
    );

    if (firstPara) {
      const text = stripHtmlTags(firstPara.data.text).trim();
      return text.substring(0, 60) + (text.length > 60 ? '...' : '');
    }

    return 'Untitled Post';
  } catch (error) {
    console.error('Error extracting title:', error);
    return 'Untitled Post';
  }
}

/**
 * Calculate word count from EditorJS data
 * @param {Object} editorData - EditorJS data object
 * @returns {number} Word count
 */
export function calculateWordCount(editorData) {
  if (!editorData?.blocks) return 0;

  try {
    const plainText = extractPlainText(editorData);
    const words = plainText.split(/\s+/).filter(word => word.length > 0);
    return words.length;
  } catch (error) {
    console.error('Error calculating word count:', error);
    return 0;
  }
}

/**
 * Calculate reading time based on word count
 * @param {number} wordCount - Total word count
 * @returns {number} Reading time in minutes
 */
export function calculateReadingTime(wordCount) {
  const wordsPerMinute = 200;
  return Math.max(1, Math.ceil(wordCount / wordsPerMinute));
}

/**
 * Auto-generate excerpt from EditorJS content
 * Extracts first 2-3 paragraphs or first 150 characters
 * @param {Object} editorData - EditorJS data object
 * @param {number} maxLength - Maximum excerpt length (default: 150)
 * @returns {string} Generated excerpt
 */
export function generateExcerpt(editorData, maxLength = 150) {
  if (!editorData?.blocks || editorData.blocks.length === 0) {
    return '';
  }

  try {
    // Get first 2-3 paragraph blocks
    const paragraphs = editorData.blocks
      .filter(block => block.type === 'paragraph' && block.data.text?.trim())
      .slice(0, 3);

    if (paragraphs.length === 0) {
      return '';
    }

    const text = paragraphs
      .map(p => stripHtmlTags(p.data.text))
      .join(' ')
      .trim();

    // Return truncated text
    if (text.length <= maxLength) {
      return text;
    }

    return text.substring(0, maxLength).trim() + '...';
  } catch (error) {
    console.error('Error generating excerpt:', error);
    return '';
  }
}
