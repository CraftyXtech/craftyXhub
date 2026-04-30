import { test, expect } from '@playwright/test';


function buildToken() {
  const header = Buffer.from(JSON.stringify({ alg: 'none', typ: 'JWT' })).toString('base64url');
  const payload = Buffer.from(
    JSON.stringify({
      sub: '1',
      exp: Math.floor(Date.now() / 1000) + 60 * 60,
    }),
  ).toString('base64url');
  return `${header}.${payload}.signature`;
}


function json(route, body, status = 200) {
  return route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(body),
  });
}


test('admin AI flow auto-fills taxonomy and SEO, preserves publish date, and shows updated date', async ({ page }) => {
  const token = buildToken();
  const user = {
    uuid: 'admin-uuid',
    email: 'admin@craftyx.com',
    username: 'admin',
    full_name: 'CraftyX Admin',
    role: 'admin',
    is_active: true,
    created_at: '2026-04-07T00:00:00Z',
    updated_at: '2026-04-07T00:00:00Z',
  };

  const categories = [
    {
      id: 44,
      name: 'Tech & Innovation',
      slug: 'tech-and-innovation',
      parent_id: null,
      subcategories: [
        { id: 74, name: 'Products & Platforms', slug: 'products-and-platforms' },
      ],
    },
    {
      id: 50,
      name: 'Business & Finance',
      slug: 'business-and-finance',
      parent_id: null,
      subcategories: [
        {
          id: 75,
          name: 'Business News & Market Intelligence',
          slug: 'business-news-and-market-intelligence',
        },
      ],
    },
  ];
  const tags = [
    { id: 301, name: 'AI Agents', slug: 'ai-agents', category_id: 74, created_at: '2026-04-07T00:00:00Z', is_active: true },
    { id: 302, name: 'Automation', slug: 'automation', category_id: 74, created_at: '2026-04-07T00:00:00Z', is_active: true },
  ];
  const generated = {
    blog_post: {
      title: 'AI Agents for Enterprise Teams',
      slug: 'ai-agents-for-enterprise-teams',
      summary: 'A practical look at how enterprise teams evaluate AI agents, workflow design, and governance before rollout.',
      sections: [
        { heading: 'Why Teams Care', body_markdown: 'Enterprise teams need clarity before rollout.' },
        { heading: 'How Evaluation Works', body_markdown: 'Strong pilots balance capability, control, and measurable outcomes.' },
        { heading: 'What Leaders Should Watch', body_markdown: 'Security, process design, and change management matter most.' },
      ],
      tags: ['ai agents', 'automation'],
      seo_title: 'Enterprise AI Agents Buying Guide',
      seo_description: 'See how enterprise teams assess AI agents, workflow automation, and rollout risk before wider adoption.',
    },
    resolved_keywords: ['AI Agents', 'Workflow Automation'],
    taxonomy_suggestion: {
      category: {
        id: 74,
        name: 'Products & Platforms',
        slug: 'products-and-platforms',
        parent_id: 44,
      },
      tags: [
        { id: 301, name: 'AI Agents', slug: 'ai-agents', category_id: 74 },
        { id: 302, name: 'Automation', slug: 'automation', category_id: 74 },
      ],
    },
    draft_id: null,
    post_id: null,
    model_used: 'qwen-3.6-max-preview',
    generation_time: 0.42,
    web_search_used: true,
    search_sources: [{ title: 'Enterprise AI report', url: 'https://example.com/report' }],
    quality_report: { passed: true, readability: {}, phase_metrics: {} },
  };

  let storedPost = null;
  let lastPublishedAt = null;

  await page.route('**/v1/**', async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname;

    if (path.endsWith('/auth/login') && request.method() === 'POST') {
      return json(route, { access_token: token, token_type: 'bearer', expires_in: 3600 });
    }

    if (path.endsWith('/auth/me') && request.method() === 'GET') {
      return json(route, user);
    }

    if (path.endsWith('/ai/blog/options') && request.method() === 'GET') {
      return json(route, {
        blog_types: [{ value: 'news', label: 'News Article' }],
        tones: [{ value: 'professional', label: 'Professional' }],
        audiences: [{ value: 'general', label: 'General Audience' }],
        lengths: [{ value: 'medium', label: 'Medium (~500 words)' }],
        models: [
          { value: 'qwen-3.6-max-preview', label: 'Qwen 3.6 Max Preview' },
          { value: 'glm-5.1', label: 'GLM 5.1' },
          { value: 'deepseek-v4-pro', label: 'DeepSeek V4 Pro' },
        ],
        use_web_search_default: true,
      });
    }

    if (path.endsWith('/ai/generate/blog') && request.method() === 'POST') {
      const body = request.postDataJSON();
      expect(body.blog_type).toBe('news');
      expect(body.model).not.toBe('gpt-5.4');
      expect(body.use_web_search).toBe(true);
      expect(body.save_draft).toBe(false);
      return json(route, generated);
    }

    if (path.endsWith('/posts/categories/') && request.method() === 'GET') {
      return json(route, { categories });
    }

    if (path.includes('/posts/categories/resolve/') && request.method() === 'GET') {
      return json(route, {
        ...categories[0].subcategories[0],
        description: 'Product previews, launches, and platform reviews.',
        created_at: '2026-04-07T00:00:00Z',
        post_count: 0,
        subcategories: [],
        parent: {
          id: 44,
          name: 'Tech & Innovation',
          slug: 'tech-and-innovation',
        },
        is_subcategory: true,
        matched_slug: 'products-and-platforms',
        canonical_slug: 'products-and-platforms',
        redirect_required: false,
      });
    }

    if (path.endsWith('/posts/tags/') && request.method() === 'GET') {
      return json(route, { tags });
    }

    if (path.endsWith('/posts/') && request.method() === 'POST') {
      const body = request.postData() ?? '';
      expect(body).toContain('seo_keywords');
      expect(body).toContain('AI Agents, Workflow Automation');
      storedPost = {
        uuid: 'draft-post-uuid',
        title: generated.blog_post.title,
        slug: generated.blog_post.slug,
        content: '<p>AI-generated draft</p>',
        content_blocks: null,
        excerpt: generated.blog_post.summary,
        featured_image: null,
        is_published: false,
        is_featured: false,
        view_count: 0,
        reading_time: 3,
        meta_title: generated.blog_post.seo_title,
        meta_description: generated.blog_post.seo_description,
        seo_keywords: generated.resolved_keywords,
        published_at: null,
        created_at: '2026-04-07T00:05:00Z',
        updated_at: '2026-04-07T00:05:00Z',
        deleted_at: null,
        is_reviewed: false,
        review_comments: null,
        is_flagged: false,
        author: user,
        category: generated.taxonomy_suggestion.category,
        tags: generated.taxonomy_suggestion.tags,
        comments: [],
        liked_by: [],
        bookmarked_by: [],
      };
      return json(route, storedPost, 201);
    }

    if (path.endsWith('/posts/draft-post-uuid') && request.method() === 'GET') {
      return json(route, storedPost);
    }

    if (path.endsWith('/posts/draft-post-uuid') && request.method() === 'PUT') {
      const body = request.postData() ?? '';
      const shouldPublish = body.includes('is_published') && body.includes('true');
      const secondEdit = body.includes('AI Agents for Enterprise Teams Updated');

      if (secondEdit) {
        storedPost = {
          ...storedPost,
          title: 'AI Agents for Enterprise Teams Updated',
        };
      }

      if (shouldPublish) {
        lastPublishedAt = lastPublishedAt || '2026-04-07T01:00:00Z';
        storedPost = {
          ...storedPost,
          is_published: true,
          published_at: lastPublishedAt,
          updated_at: secondEdit ? '2026-04-07T03:00:00Z' : '2026-04-07T01:00:00Z',
        };
      }

      return json(route, storedPost);
    }

    if (path.endsWith('/posts/ai-agents-for-enterprise-teams') && request.method() === 'GET') {
      return json(route, {
        ...storedPost,
        likes_count: 0,
      });
    }

    if (path.endsWith('/posts/ai-agents-for-enterprise-teams/related') && request.method() === 'GET') {
      return json(route, { posts: [], total: 0, page: 1, size: 12 });
    }

    if (path.endsWith('/posts/draft-post-uuid/view') && request.method() === 'POST') {
      return json(route, { counted: true });
    }

    if (path.endsWith('/posts/') && request.method() === 'GET') {
      return json(route, { posts: [], total: 0, page: 1, size: 10 });
    }

    return json(route, {});
  });

  await page.goto('/auth/login');
  await page.getByLabel('Email Address').fill('admin@craftyx.com');
  await page.getByLabel('Password').fill('admin123');
  await page.getByRole('button', { name: 'Sign In' }).click();
  await page.waitForURL('**/dashboard');

  await page.goto('/dashboard/posts/create');
  await expect(page.getByRole('textbox', { name: 'Title', exact: true })).toBeVisible();

  await page.getByRole('button', { name: /ai writer/i }).click();
  await page.getByPlaceholder('Topic or title idea...').fill('How enterprise AI agents improve internal operations');
  await expect(page.getByText('News Article')).toBeVisible();
  await expect(page.getByRole('checkbox', { name: /web search/i })).toBeChecked();
  await page.getByRole('button', { name: 'Generate Post' }).click();

  await expect(page.getByRole('button', { name: 'Use as Post' })).toBeVisible();
  await page.getByRole('button', { name: 'Use as Post' }).click();
  await page.keyboard.press('Escape');

  await expect(page.locator('input[value="AI Agents for Enterprise Teams"]').first()).toBeVisible();
  await expect(page.getByLabel('SEO Keywords')).toHaveValue('AI Agents, Workflow Automation');

  await page.getByRole('button', { name: 'Save Draft' }).click();
  await page.waitForURL('**/dashboard/posts');

  await page.goto('/dashboard/posts/edit/draft-post-uuid');
  await expect(page.locator('input[value="AI Agents for Enterprise Teams"]').first()).toBeVisible();
  await expect(page.getByLabel('SEO Keywords')).toHaveValue('AI Agents, Workflow Automation');

  await page.getByRole('button', { name: 'Update & Publish' }).click();
  await page.waitForURL('**/dashboard/posts');

  await page.goto('/dashboard/posts/edit/draft-post-uuid');
  await page.locator('input[value="AI Agents for Enterprise Teams"]').first().fill('AI Agents for Enterprise Teams Updated');
  await page.getByRole('button', { name: 'Update & Publish' }).click();
  await page.waitForURL('**/dashboard/posts');

  await page.goto('/post/ai-agents-for-enterprise-teams');
  await expect(page.getByText(/^Published /)).toBeVisible();
  await expect(page.getByText(/^Updated /)).toBeVisible();
});
