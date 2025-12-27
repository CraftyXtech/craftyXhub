import { processContent } from './markdown';

export const contentFormatter = {
  markdownToHTML(text) {
    if (!text) return '';
    
    // Use the central utility for conversion and sanitization
    let html = processContent(text);
    
    html = html.replace(/<h1>/g, '<h1 class="fw-bold mb-3" style="font-size: 1.5rem;">');
    html = html.replace(/<h2>/g, '<h2 class="fw-bold mb-3" style="font-size: 1.25rem;">');
    html = html.replace(/<h3>/g, '<h3 class="fw-bold mb-2" style="font-size: 1.125rem;">');
    html = html.replace(/<ul>/g, '<ul style="padding-left: 1.5rem; margin-bottom: 1rem;">');
    html = html.replace(/<ol>/g, '<ol style="padding-left: 1.5rem; margin-bottom: 1rem;">');
    html = html.replace(/<p>/g, '<p style="margin-bottom: 0.75rem; line-height: 1.6;">');
    html = html.replace(/<li>/g, '<li style="margin-bottom: 0.5rem;">');
    
    return html;
  },
  
  toHTML(text) {
    return this.markdownToHTML(text);
  },
  
  stripHTML(html) {
    if (!html) return '';
    return html.replace(/<[^>]*>/g, '').replace(/\n\n+/g, '\n\n').trim();
  }
};

