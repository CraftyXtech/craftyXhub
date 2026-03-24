export const resolveUseWebSearch = (use_web_search = true) =>
  typeof use_web_search === 'boolean' ? use_web_search : true;

export const buildBlogGenerationPayload = ({
  topic,
  blog_type = 'how-to',
  keywords = [],
  audience = null,
  word_count = 'medium',
  tone = 'professional',
  language = 'en-US',
  model = 'glm-5',
  creativity = 0.7,
  use_web_search = true,
  save_draft = true,
  publish_post = false,
  category_id = null,
  is_published = false,
} = {}) => ({
  topic,
  blog_type,
  keywords: Array.isArray(keywords)
    ? keywords
    : String(keywords || '')
      .split(',')
      .map((keyword) => keyword.trim())
      .filter(Boolean),
  audience,
  word_count,
  tone,
  language,
  model,
  creativity,
  use_web_search: resolveUseWebSearch(use_web_search),
  save_draft,
  publish_post,
  category_id,
  is_published,
});
