import test from 'node:test';
import assert from 'node:assert/strict';

import {
  buildBlogGenerationPayload,
  resolveUseWebSearch,
} from '../src/api/services/blogGenerationPayload.js';

test('resolveUseWebSearch honors an explicit off selection', () => {
  assert.equal(resolveUseWebSearch(false), false);
});

test('resolveUseWebSearch defaults to on when missing', () => {
  assert.equal(resolveUseWebSearch(), true);
});

test('buildBlogGenerationPayload keeps the selected web search state', () => {
  const offPayload = buildBlogGenerationPayload({ topic: 'DuckDuckGo toggle test', use_web_search: false });
  const onPayload = buildBlogGenerationPayload({ topic: 'DuckDuckGo toggle test', use_web_search: true });

  assert.equal(offPayload.use_web_search, false);
  assert.equal(onPayload.use_web_search, true);
});

test('buildBlogGenerationPayload defaults web search to on', () => {
  assert.equal(
    buildBlogGenerationPayload({ topic: 'Default state' }).use_web_search,
    true,
  );
});
