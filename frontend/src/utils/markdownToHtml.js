import MarkdownIt from 'markdown-it';
import DOMPurify from 'dompurify';

/**
 * Shared markdown-it instance.
 * - html: false  → block raw HTML in markdown source (security)
 * - linkify: true → auto-link bare URLs
 * - breaks: true  → single \n becomes <br>
 */
const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
  typographer: false,
});

/**
 * DOMPurify whitelist — broader than a chat widget because TinyMCE
 * can handle tables, images, divs, etc.
 */
const SANITIZE_CONFIG = {
  ALLOWED_TAGS: [
    'p', 'br', 'strong', 'b', 'em', 'i', 'a',
    'ul', 'ol', 'li',
    'code', 'pre',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'hr',
    'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'div', 'span', 'sup', 'sub',
  ],
  ALLOWED_ATTR: ['href', 'target', 'rel', 'src', 'alt', 'class', 'style'],
};

/**
 * Convert markdown text to sanitised HTML.
 *
 * @param {string} markdownText - Raw markdown string
 * @returns {string} Safe HTML ready for TinyMCE or any HTML context
 */
export function markdownToHtml(markdownText) {
  if (!markdownText) return '';
  const rawHtml = md.render(markdownText);
  return DOMPurify.sanitize(rawHtml, SANITIZE_CONFIG);
}
