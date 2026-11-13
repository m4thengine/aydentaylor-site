// Serves Mux thumbnails from aydentaylor.com so Google Images credits them to this site.
// /img/w/<name>-ayden-taylor.jpg  ->  this function  ->  image.mux.com (fetched once, then cached at the edge)
import MAP from './mux-thumbs.json' with { type: 'json' };
export const config = { runtime: 'edge' };
export default async function handler(req) {
  const name = new URL(req.url).searchParams.get('n') || '';
  const src = MAP[name];
  if (!src) return new Response('Not found', { status: 404 });
  const r = await fetch(src, { headers: { Referer: 'https://aydentaylor.com/', 'User-Agent': 'Mozilla/5.0 (aydentaylor.com image proxy)' } });
  if (!r.ok) return new Response('Upstream ' + r.status, { status: 502 });
  return new Response(r.body, { status: 200, headers: {
    'Content-Type': r.headers.get('content-type') || 'image/jpeg',
    'Cache-Control': 'public, max-age=31536000, immutable',
    'CDN-Cache-Control': 'public, max-age=31536000, immutable',
  } });
}
