import test from 'node:test';
import assert from 'node:assert/strict';

import { renderBlogPostToHtml } from '../src/utils/blogMarkdown.js';

test('renderBlogPostToHtml turns markdown links into anchor tags', () => {
  const html = renderBlogPostToHtml({
    title: 'Quit smoking',
    sections: [
      {
        heading: 'Conclusion',
        body_markdown:
          'These changes are confirmed by the [CDC](https://www.cdc.gov/tobacco/about/how-to-quit.html), not marketing copy.',
      },
    ],
  });

  assert.match(html, /<a href="https:\/\/www\.cdc\.gov\/tobacco\/about\/how-to-quit\.html"/);
  assert.doesNotMatch(html, /\[CDC\]\(https:\/\/www\.cdc\.gov\/tobacco\/about\/how-to-quit\.html\)/);
});
