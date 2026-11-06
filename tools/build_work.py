#!/usr/bin/env python3
"""Regenerate /work/index.html (crawlable image index) from the rows and thumbnails in index.html.
Run after adding or removing projects:  python3 tools/build_work.py"""
import re, html, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
thumbs = dict(re.findall(r"'(https?://[^']+)':\s*'([^']+)'", s[s.index('var MUX_THUMBS'):s.index('var LIGHT_BG_THUMBS')]))
rows = re.findall(r'<tr data-order="(\d+)" data-client="([^"]*)" data-disc="([^"]*)"><td class="n">\d+</td><td class="p"><a href="([^"]+)"[^>]*>([^<]+)</a>', s)
NOUN = {'Cover Art': 'cover art', 'Film & 3D': 'film and 3D', 'Billboards & OOH': 'billboard', 'Brands & Campaigns': 'campaign', 'Social': 'social content', 'Merch': 'merch design'}
items, ld = [], []
for order, client, disc, href, title in sorted(rows, key=lambda r: int(r[0])):
    client, disc, title, href = html.unescape(client), html.unescape(disc), html.unescape(title), html.unescape(href)
    src = thumbs.get(href)
    if not src: continue
    full = src if src.startswith('http') else 'https://aydentaylor.com' + src
    alt = f'{title} — {NOUN.get(disc, disc.lower())} for {client} by Ayden Taylor (Math)'
    n = int(order) + 1
    items.append(f'''    <figure id="p{n:02d}">
      <a href="{html.escape(href)}" target="_blank" rel="noopener"><img src="{html.escape(src)}" alt="{html.escape(alt)}" loading="lazy" decoding="async"></a>
      <figcaption><span class="n">{n:02d}</span> {html.escape(title)}<br><span class="c">{html.escape(client)} · {html.escape(disc)}</span></figcaption>
    </figure>''')
    ld.append({"@type": "ImageObject", "contentUrl": full, "name": f"{title} — {client}", "caption": alt,
               "creator": {"@id": "https://aydentaylor.com/#person"}, "creditText": "Ayden Taylor (Math)"})
page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Work — Ayden Taylor</title>
  <meta name="description" content="Image index of {len(items)} projects by Ayden Taylor (Math), creative director and founder of UOX Studio: cover art, film, 3D, billboards and campaigns for Drake, Juice WRLD, Polymarket, ESPN and more." />
  <link rel="canonical" href="https://aydentaylor.com/work/" />
  <link rel="icon" href="/favicon.ico" sizes="any" />
  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
  <script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "ImageGallery", "@id": "https://aydentaylor.com/work/#gallery", "url": "https://aydentaylor.com/work/", "name": "Work by Ayden Taylor", "author": {"@id": "https://aydentaylor.com/#person"}, "about": {"@type": "Person", "@id": "https://aydentaylor.com/#person", "name": "Ayden Taylor", "alternateName": "Math", "url": "https://aydentaylor.com/"}, "associatedMedia": ld}, ensure_ascii=False)}</script>
  <script defer src="/_vercel/insights/script.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #fff; color: #000; font-family: 'Times New Roman', Times, serif; font-size: 16px; padding: 20px 20px 60px; }}
    a {{ color: #1155cc; }}
    header {{ max-width: 600px; margin-bottom: 1.6em; }}
    h1 {{ font-size: 2.6em; line-height: 1.1; margin-bottom: 4px; }}
    header p {{ line-height: 1.5; }}
    .back {{ font: 12px 'Courier New', Courier, monospace; display: inline-block; margin-bottom: 14px; color: #8a8a8f; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 28px 16px; }}
    figure img {{ display: block; width: 100%; aspect-ratio: 1 / 1; object-fit: contain; background: #f3f3f5; }}
    figcaption {{ font: 12px/1.45 'Courier New', Courier, monospace; margin-top: 6px; }}
    figcaption .n, figcaption .c {{ color: #8a8a8f; }}
  </style>
</head>
<body>
  <header>
    <a class="back" href="/">← aydentaylor.com</a>
    <h1>Work</h1>
    <p>{len(items)} projects by <a href="/">Ayden Taylor</a>, known as Math. Creative director and founder of <a href="https://www.uox.studio" target="_blank" rel="noopener">UOX Studio</a>.</p>
  </header>
  <main class="grid">
{chr(10).join(items)}
  </main>
</body>
</html>
'''
os.makedirs(os.path.join(ROOT, 'work'), exist_ok=True)
open(os.path.join(ROOT, 'work', 'index.html'), 'w', encoding='utf-8').write(page)
print('work/index.html:', len(items), 'projects')

# sitemap: home, about, and the work index carrying every image
imgs = re.findall(r'<img src="([^"]+)"', page)
def u(loc, extra=''):
    return f'  <url>\n    <loc>{loc}</loc>\n    <lastmod>{__import__("datetime").date.today()}</lastmod>\n{extra}  </url>\n'
img_xml = ''.join(f'    <image:image><image:loc>{html.escape(i if i.startswith("http") else "https://aydentaylor.com" + i)}</image:loc></image:image>\n' for i in dict.fromkeys(html.unescape(x) for x in imgs))
sm = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
      + u('https://aydentaylor.com/') + u('https://aydentaylor.com/about/') + u('https://aydentaylor.com/work/', img_xml) + '</urlset>\n')
open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(sm)
print('sitemap.xml:', len(imgs), 'images')
