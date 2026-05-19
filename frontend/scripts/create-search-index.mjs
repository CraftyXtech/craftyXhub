import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';

const distIndexPath = join(process.cwd(), 'dist', 'index.html');
const searchIndexPath = join(process.cwd(), 'dist', 'search', 'index.html');

const html = await readFile(distIndexPath, 'utf8');
const marker = '<meta name="description" content="CraftyXHub - Your Creative Content Hub" />';
const injection = `${marker}\n    <meta name="robots" content="noindex,follow" />`;

if (!html.includes(marker)) {
  throw new Error('Could not find description meta tag in dist/index.html');
}

const updated = html.replace(marker, injection);
await mkdir(dirname(searchIndexPath), { recursive: true });
await writeFile(searchIndexPath, updated, 'utf8');
console.log(`Created ${searchIndexPath}`);
