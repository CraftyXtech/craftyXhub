import test from 'node:test';
import assert from 'node:assert/strict';

import {
  BLOG_WEB_SEARCH_MODES,
  buildBlogGenerationPayload,
  resolveBlogWebSearchMode,
} from '../src/api/services/blogGenerationPayload.js';

test('resolveBlogWebSearchMode honors an explicit off selection', () => {
  assert.equal(
    resolveBlogWebSearchMode({ web_search_mode: BLOG_WEB_SEARCH_MODES.OFF }),
    BLOG_WEB_SEARCH_MODES.OFF,
  );
});

test('resolveBlogWebSearchMode honors an explicit basic selection', () => {
  assert.equal(
    resolveBlogWebSearchMode({ web_search_mode: BLOG_WEB_SEARCH_MODES.BASIC }),
    BLOG_WEB_SEARCH_MODES.BASIC,
  );
});

test('buildBlogGenerationPayload keeps the selected DDG mode instead of silently overriding it', () => {
  const offPayload = buildBlogGenerationPayload({
    topic: 'DuckDuckGo mode test',
    web_search_mode: BLOG_WEB_SEARCH_MODES.OFF,
  });
  const basicPayload = buildBlogGenerationPayload({
    topic: 'DuckDuckGo mode test',
    web_search_mode: BLOG_WEB_SEARCH_MODES.BASIC,
  });

  assert.equal(offPayload.web_search_mode, BLOG_WEB_SEARCH_MODES.OFF);
  assert.equal(basicPayload.web_search_mode, BLOG_WEB_SEARCH_MODES.BASIC);
});

test('legacy boolean fallback still maps to off/basic consistently', () => {
  assert.equal(
    buildBlogGenerationPayload({ topic: 'Legacy false', web_search: false }).web_search_mode,
    BLOG_WEB_SEARCH_MODES.OFF,
  );
  assert.equal(
    buildBlogGenerationPayload({ topic: 'Legacy true', web_search: true }).web_search_mode,
    BLOG_WEB_SEARCH_MODES.BASIC,
  );
});
