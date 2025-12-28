import { axiosPrivate } from '../axios';

/**
 * AI Service
 * Handles AI content generation and drafts
 */

// ===== CONTENT GENERATION =====

/**
 * Generate AI content
 * @param {object} options - Generation options
 * @param {string} options.tool_id - AI tool ID
 * @param {string} options.model - AI model to use
 * @param {object} options.params - Tool-specific parameters
 * @param {string} options.tone - Content tone (default: 'professional')
 * @param {string} options.length - Content length (default: 'medium')
 * @param {string} options.language - Output language (default: 'en-US')
 * @param {number} options.creativity - Creativity level 0-1 (default: 0.7)
 * @param {number} options.variant_count - Number of variants (default: 1)
 * @param {boolean} options.stream - Enable streaming (default: false)
 * @returns {Promise<object>} Generated content
 */
export const generate = async ({
  tool_id,
  model = 'gpt-5-mini',
  params = {},
  prompt,
  keywords,
  tone = 'professional',
  length = 'medium',
  language = 'en-US',
  creativity = 0.7,
  variant_count = 1,
  stream = false,
}) => {
  const payload = {
    tool_id,
    model,
    params,
    prompt,
    keywords,
    tone,
    length,
    language,
    creativity,
    variant_count,
    stream,
  };
  
  const response = await axiosPrivate.post('ai/generate', payload);
  return response.data?.variants ?? response.data;
};

/**
 * Generate a complete blog post using the Blog Agent
 * @param {object} options - Blog generation options
 * @param {string} options.topic - Blog topic or title idea
 * @param {string} options.blog_type - Type of blog (how-to, listicle, tutorial, etc.)
 * @param {string[]} options.keywords - Target SEO keywords
 * @param {string} options.audience - Target audience description
 * @param {string} options.word_count - Target length (short, medium, long, very-long)
 * @param {string} options.tone - Writing tone
 * @param {string} options.language - Output language
 * @param {string} options.model - AI model to use
 * @param {number} options.creativity - Temperature/creativity level (0.0-1.0)
 * @param {boolean} options.use_web_search - Enable web search for research
 * @param {boolean} options.save_draft - Save as AI draft
 * @param {boolean} options.publish_post - Publish directly to Posts
 * @param {number} options.category_id - Category ID for publishing
 * @param {boolean} options.is_published - Set published status when creating post
 * @returns {Promise<object>} { blog_post, draft_id, post_id }
 */
export const generateBlog = async ({
  topic,
  blog_type = 'how-to',
  keywords = [],
  audience = null,
  word_count = 'medium',
  tone = 'professional',
  language = 'en-US',
  model = 'gpt-5-mini',
  creativity = 0.7,
  use_web_search = true,
  save_draft = true,
  publish_post = false,
  category_id = null,
  is_published = false,
}) => {
  const payload = {
    topic,
    blog_type,
    keywords: Array.isArray(keywords) 
      ? keywords 
      : keywords.split(',').map(k => k.trim()).filter(k => k),
    audience,
    word_count,
    tone,
    language,
    model,
    creativity,
    use_web_search,
    save_draft,
    publish_post,
    category_id,
    is_published,
  };
  
  const response = await axiosPrivate.post('ai/generate/blog', payload);
  return response.data;
};

// ===== DRAFTS =====

/**
 * Save an AI draft
 * @param {object} draft - Draft data
 * @returns {Promise<object>} Saved draft
 */
export const saveDraft = async (draft) => {
  const response = await axiosPrivate.post('ai/drafts', draft);
  return response.data;
};

/**
 * Get AI drafts
 * @param {number} skip - Offset for pagination
 * @param {number} limit - Number of items
 * @returns {Promise<object>} Drafts list
 */
export const getDrafts = async (skip = 0, limit = 50) => {
  const response = await axiosPrivate.get(`ai/drafts?skip=${skip}&limit=${limit}`);
  return response.data;
};

/**
 * Get a draft by ID
 * @param {string|number} id - Draft ID
 * @returns {Promise<object>} Draft data
 */
export const getDraftById = async (id) => {
  const response = await axiosPrivate.get(`ai/drafts/${id}`);
  return response.data;
};

/**
 * Update a draft
 * @param {string|number} id - Draft ID
 * @param {object} updates - Data to update
 * @returns {Promise<object>} Updated draft
 */
export const updateDraft = async (id, updates) => {
  const response = await axiosPrivate.put(`ai/drafts/${id}`, updates);
  return response.data;
};

/**
 * Delete a draft
 * @param {string|number} id - Draft ID
 * @returns {Promise<void>}
 */
export const deleteDraft = async (id) => {
  await axiosPrivate.delete(`ai/drafts/${id}`);
};

/**
 * Get favorite drafts
 * @param {number} skip - Offset for pagination
 * @param {number} limit - Number of items
 * @returns {Promise<object>} Favorite drafts list
 */
export const getFavoriteDrafts = async (skip = 0, limit = 50) => {
  const response = await axiosPrivate.get(`ai/drafts/favorites?skip=${skip}&limit=${limit}`);
  return response.data;
};
