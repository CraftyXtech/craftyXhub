import { test, expect } from '@playwright/test';


const productionBaseUrl = process.env.PRODUCTION_BASE_URL;
const productionCategoryPath = process.env.PRODUCTION_CATEGORY_PATH;
const productionPostPath = process.env.PRODUCTION_POST_PATH;
const productionLegacyCategoryPath = process.env.PRODUCTION_LEGACY_CATEGORY_PATH;
const productionCanonicalCategoryPath = process.env.PRODUCTION_CANONICAL_CATEGORY_PATH;


test.describe('production smoke', () => {
  test.skip(
    !productionBaseUrl,
    'Set PRODUCTION_BASE_URL (and optional category/post paths) to run read-only production smoke checks.',
  );

  test('homepage loads read-only', async ({ page }) => {
    await page.goto(productionBaseUrl, { waitUntil: 'networkidle' });
    await expect(page).toHaveURL(new RegExp(productionBaseUrl.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  });

  test('category and post pages load read-only when configured', async ({ page }) => {
    test.skip(!productionCategoryPath || !productionPostPath, 'Set PRODUCTION_CATEGORY_PATH and PRODUCTION_POST_PATH.');

    await page.goto(new URL(productionCategoryPath, productionBaseUrl).toString(), { waitUntil: 'networkidle' });
    await expect(page).toHaveURL(/category\//);

    await page.goto(new URL(productionPostPath, productionBaseUrl).toString(), { waitUntil: 'networkidle' });
    await expect(page).toHaveURL(/post\//);
  });

  test('legacy category slug redirects when configured', async ({ page }) => {
    test.skip(
      !productionLegacyCategoryPath || !productionCanonicalCategoryPath,
      'Set PRODUCTION_LEGACY_CATEGORY_PATH and PRODUCTION_CANONICAL_CATEGORY_PATH.',
    );

    await page.goto(new URL(productionLegacyCategoryPath, productionBaseUrl).toString(), {
      waitUntil: 'networkidle',
    });
    await expect(page).toHaveURL(new RegExp(`${productionCanonicalCategoryPath.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`));
  });
});
