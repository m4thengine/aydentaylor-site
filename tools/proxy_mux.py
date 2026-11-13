#!/usr/bin/env python3
"""Serve Mux thumbnails from aydentaylor.com/img/w/<descriptive-name>.jpg via Vercel rewrites."""
import re, html, json, os, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
block = s[s.index('var MUX_THUMBS'):s.index('var LIGHT_BG_THUMBS')]
thumbs = re.findall(r"'(https?://[^']+)':\s*'(https://image\.mux\.com/[^']+)'", block)
rows = {html.unescape(h): (html.unescape(c), html.unescape(t)) for c, h, t in re.findall(r'data-client="([^"]*)"[^>]*>.*?<a href="([^"]+)"[^>]*>([^<]+)</a>', s)}
def slug(x):
    x = x.replace('Ø','O').replace('ø','o'); x = unicodedata.normalize('NFKD', x).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', x)).strip('-')
cfg_path = os.path.join(ROOT, 'vercel.json')
cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else {}
rewrites = [r for r in cfg.get('rewrites', []) if not r['source'].startswith('/img/w/')]
used = set()
for href, mux in thumbs:
    client, title = rows.get(href, ('', ''))
    name = slug(f'{client} {title}')[:70].strip('-') or slug(mux.split('/')[3])[:20]
    base, i = name, 2
    while name in used: name = f'{base}-{i}'; i += 1
    used.add(name)
    local = f'/img/w/{name}-ayden-taylor.jpg'
    rewrites.append({'source': local, 'destination': mux})
    s = s.replace(mux, local)
cfg['rewrites'] = rewrites
json.dump(cfg, open(cfg_path, 'w'), indent=2); open(p, 'w', encoding='utf-8').write(s)
print(len(thumbs), 'thumbnails now served from aydentaylor.com')
for r in rewrites: print(' ', r['source'])
