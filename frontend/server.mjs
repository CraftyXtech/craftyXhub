/**
 * Production server for CraftyXHub frontend.
 *
 * Replaces `vite preview` to add transparent reverse-proxying of
 * share-bridge routes (/s/*, /post/*) to the API backend.
 * This lets social-media crawlers (WhatsApp, Facebook, Twitter …)
 * see proper OG meta tags (featured image, title, description)
 * while keeping clean, branded URLs (craftyxhub.com/s/slug).
 *
 * Usage:  node server.mjs          (port 4173 by default)
 *         PORT=3000 node server.mjs
 */

import { createServer, request as httpRequest } from 'node:http';
import { createReadStream, existsSync, statSync } from 'node:fs';
import { extname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = fileURLToPath(new URL('.', import.meta.url));
const DIST = resolve(__dirname, 'dist');
const PORT = parseInt(process.env.PORT || '4173', 10);

// API backend to proxy share routes to
const API_ORIGIN = process.env.API_ORIGIN || 'http://localhost:8000';
const apiUrl = new URL(API_ORIGIN);

// Routes to proxy to the API (share bridge + crawler render)
const PROXY_PREFIXES = ['/s/', '/post/', '/share/'];

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js':   'application/javascript; charset=utf-8',
  '.mjs':  'application/javascript; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif':  'image/gif',
  '.svg':  'image/svg+xml',
  '.ico':  'image/x-icon',
  '.webp': 'image/webp',
  '.woff': 'font/woff',
  '.woff2':'font/woff2',
  '.ttf':  'font/ttf',
  '.webm': 'video/webm',
  '.mp4':  'video/mp4',
};

/** Proxy a request to the API backend and pipe the response back. */
function proxyToApi(req, res) {
  const opts = {
    hostname: apiUrl.hostname,
    port: apiUrl.port || (apiUrl.protocol === 'https:' ? 443 : 80),
    path: req.url,
    method: req.method,
    headers: {
      ...req.headers,
      host: apiUrl.host,
    },
  };

  const proxyReq = httpRequest(opts, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res, { end: true });
  });

  proxyReq.on('error', (err) => {
    console.error(`[proxy] Error proxying ${req.url}:`, err.message);
    if (!res.headersSent) {
      res.writeHead(502, { 'Content-Type': 'text/plain' });
      res.end('Bad Gateway');
    }
  });

  req.pipe(proxyReq, { end: true });
}

/** Serve a static file from dist/ or fall back to index.html (SPA). */
function serveStatic(req, res) {
  // Strip query string
  const pathname = req.url.split('?')[0];
  let filePath = join(DIST, pathname === '/' ? 'index.html' : pathname);

  // If the path maps to an existing file, serve it
  if (existsSync(filePath) && statSync(filePath).isFile()) {
    const ext = extname(filePath);
    const mime = MIME_TYPES[ext] || 'application/octet-stream';

    const cacheControl = ext === '.html'
      ? 'no-cache'
      : 'public, max-age=31536000, immutable';

    res.writeHead(200, {
      'Content-Type': mime,
      'Cache-Control': cacheControl,
    });
    createReadStream(filePath).pipe(res);
    return;
  }

  // SPA fallback — serve index.html for all non-file routes
  const indexPath = join(DIST, 'index.html');
  if (existsSync(indexPath)) {
    res.writeHead(200, {
      'Content-Type': 'text/html; charset=utf-8',
      'Cache-Control': 'no-cache',
    });
    createReadStream(indexPath).pipe(res);
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not Found');
  }
}

// --- Server ---

const server = createServer((req, res) => {
  const path = req.url.split('?')[0];

  // Proxy share/crawler routes to the API
  if (PROXY_PREFIXES.some((prefix) => path.startsWith(prefix))) {
    return proxyToApi(req, res);
  }

  // Serve static SPA
  serveStatic(req, res);
});

server.listen(PORT, () => {
  console.log(`  ➜  CraftyXHub server running at http://localhost:${PORT}/`);
  console.log(`  ➜  Share routes (/s/*, /post/*) proxied to ${API_ORIGIN}`);
});
