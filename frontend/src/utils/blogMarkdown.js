import MarkdownIt from 'markdown-it';

const markdownRenderer = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
});

const escapeHtml = (value = '') =>
  String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');

export const renderBlogMarkdownToHtml = (markdown = '') =>
  markdownRenderer.render(markdown || '');

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

  return htmlParts.join('\n');
};
