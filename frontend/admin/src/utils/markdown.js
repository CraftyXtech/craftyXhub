import MarkdownIt from 'markdown-it';
import DOMPurify from 'dompurify';

// Configure the parser (enable HTML, auto-linking, etc.)
const md = new MarkdownIt({
  html: true,
  linkify: true,
  breaks: true // Convert \n to <br>
});

// The Conversion Function
export function processContent(rawAIOutput) {
  if (!rawAIOutput) return '';

  // Step A: Convert Markdown to HTML
  const rawHtml = md.render(rawAIOutput);

  // Step B: Sanitize (CRITICAL for security)
  // This removes malicious scripts if the AI hallucinates them
  const cleanHtml = DOMPurify.sanitize(rawHtml);

  return cleanHtml;
}
