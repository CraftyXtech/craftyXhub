import { axiosPrivate } from "@/api/axios";

export const aiWriterService = {
  generate: async ({
    tool_id,
    params = {},
    prompt,
    keywords,
    tone = "professional",
    language = "en-US",
    length = "medium",
    variant_count = 1,
    creativity = 0.7,
    model = "gpt-5-mini",
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
    };
    const { data } = await axiosPrivate.post("ai/generate", payload);
    return data?.variants ?? [];
  },

  /**
   * Generate a complete blog post using the Blog Agent.
   * 
   * @param {Object} options - Blog generation options
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
   * @returns {Promise<Object>} Blog generation response with blog_post, draft_id, post_id
   */
  generateBlog: async ({
    topic,
    blog_type = "how-to",
    keywords = [],
    audience = null,
    word_count = "medium",
    tone = "professional",
    language = "en-US",
    model = "gpt-5-mini",
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
      keywords: Array.isArray(keywords) ? keywords : keywords.split(',').map(k => k.trim()).filter(k => k),
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
    const { data } = await axiosPrivate.post("ai/generate/blog", payload);
    return data;
  },
};

export default aiWriterService;
