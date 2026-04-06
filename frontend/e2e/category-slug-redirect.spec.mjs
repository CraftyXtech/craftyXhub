import { test, expect } from '@playwright/test';


function json(route, body, status = 200) {
  return route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(body),
  });
}


test('legacy category slugs redirect to the canonical slug', async ({ page }) => {
  await page.route('**/v1/**', async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname;

    if (path.endsWith('/posts/categories/resolve/tech-products') && request.method() === 'GET') {
      return json(route, {
        id: 74,
        name: 'Products & Platforms',
        slug: 'products-and-platforms',
        description: 'Product previews, launches, and platform reviews.',
        parent_id: 44,
        created_at: '2026-04-07T00:00:00Z',
        post_count: 0,
        subcategories: [],
        parent: { id: 44, name: 'Tech & Innovation', slug: 'tech-and-innovation' },
        is_subcategory: true,
        matched_slug: 'tech-products',
        canonical_slug: 'products-and-platforms',
        redirect_required: true,
      });
    }

    if (path.endsWith('/posts/categories/resolve/products-and-platforms') && request.method() === 'GET') {
      return json(route, {
        id: 74,
        name: 'Products & Platforms',
        slug: 'products-and-platforms',
        description: 'Product previews, launches, and platform reviews.',
        parent_id: 44,
        created_at: '2026-04-07T00:00:00Z',
        post_count: 0,
        subcategories: [],
        parent: { id: 44, name: 'Tech & Innovation', slug: 'tech-and-innovation' },
        is_subcategory: true,
        matched_slug: 'products-and-platforms',
        canonical_slug: 'products-and-platforms',
        redirect_required: false,
      });
    }

    if (path.endsWith('/posts/') && request.method() === 'GET') {
      return json(route, { posts: [], total: 0, page: 1, size: 6 });
    }

    return json(route, {});
  });

  await page.goto('/category/tech-products');
  await page.waitForURL('**/category/products-and-platforms');
  await expect(page.getByRole('heading', { name: 'Products & Platforms' })).toBeVisible();
});
