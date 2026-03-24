export const BLOG_WEB_SEARCH_MODES = Object.freeze({
  OFF: 'off',
  BASIC: 'basic',
});

export const resolveBlogWebSearchMode = ({
  web_search_mode,
  web_search,
} = {}) => {
  if (typeof web_search_mode === 'string') {
    const normalizedMode = web_search_mode.toLowerCase();
    if (normalizedMode === BLOG_WEB_SEARCH_MODES.OFF || normalizedMode === BLOG_WEB_SEARCH_MODES.BASIC) {
      return normalizedMode;
    }
  }

  if (web_search === false) {
    return BLOG_WEB_SEARCH_MODES.OFF;
  }

  return BLOG_WEB_SEARCH_MODES.BASIC;
};

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
  web_search = true,
  web_search_mode,
  execution_mode = 'strict',
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
  web_search_mode: resolveBlogWebSearchMode({ web_search_mode, web_search }),
  execution_mode,
  save_draft,
  publish_post,
  category_id,
  is_published,
});
