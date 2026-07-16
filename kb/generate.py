#!/usr/bin/env python3
"""Generate brand-specific SEO knowledge base pages from 659 cleaned Q&A files."""

import json, os, html, re
from collections import defaultdict
from datetime import datetime

DATA_DIR = "C:/Users/23206/Desktop/一人公司/3dprint-kb/cleaned"
OUT_DIR = "C:/Users/23206/WorkBuddy/2026-07-16-21-11-12/site/kb"
BASE_URL = "https://qm121.github.io"

def load_all():
    entries = []
    for root, dirs, files in os.walk(DATA_DIR):
        for f in files:
            if not f.endswith('.json'): continue
            try:
                with open(os.path.join(root, f), encoding='utf-8') as fh:
                    d = json.load(fh)
                brands = d.get("tags",{}).get("brand",[]) or ["General"]
                materials = d.get("tags",{}).get("material",[])
                symptoms = d.get("tags",{}).get("symptom",[])
                entries.append({
                    "title": d.get("title","Unknown").replace(" | Bambu Lab Wiki","").strip(),
                    "text": d.get("clean_text",""),
                    "url": d.get("url",""),
                    "source": d.get("source",""),
                    "brand": max(brands, key=lambda b: len(b)) if brands else "General",
                    "all_brands": brands,
                    "materials": materials,
                    "symptoms": symptoms,
                    "doc_id": d.get("doc_id",""),
                })
            except: pass

    # Group by primary brand
    groups = defaultdict(list)
    for e in entries:
        groups[e["brand"]].append(e)
    return dict(groups)

BRAND_INFO = {
    "Bambu Lab": {"slug":"bambu-lab", "desc":"Bambu Lab printers (X1C, P1S, P1P, A1, A1 Mini) troubleshooting guides — extruder clogs, first layer, AMS issues, bed leveling, and more."},
    "Prusa": {"slug":"prusa", "desc":"Prusa printers (MK3, MK4, Mini, XL) troubleshooting guides — stringing, warping, layer adhesion, Z-banding, and more."},
    "Creality": {"slug":"creality", "desc":"Creality printers (Ender 3, Ender 5, CR-10, K1, K1 Max) troubleshooting guides — bed leveling, clogging, under-extrusion, and more."},
    "Elegoo": {"slug":"elegoo", "desc":"Elegoo printers (Mars, Saturn, Neptune series) troubleshooting guides — leveling, adhesion, print failures, and more."},
    "General": {"slug":"general", "desc":"General 3D printing troubleshooting guides covering all brands — extrusion problems, stringing, warping, bed adhesion, and more."},
}

def truncate_text(text, max_words=80):
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + '...'

def page_template(title, meta_desc, brand, entries, slug):
    """Generate a full HTML page for one brand."""
    card_html = ""
    for i, e in enumerate(entries):
        question = html.escape(e["title"])
        answer = html.escape(e["text"])
        url = html.escape(e["url"])
        source = html.escape(e["source"])
        snippet = html.escape(truncate_text(e["text"], 60))
        mat_tags = "".join(f'<span class="badge bg-light text-dark me-1">{html.escape(m)}</span>' for m in e["materials"][:3])
        sym_tags = "".join(f'<span class="badge bg-warning bg-opacity-10 text-warning-emphasis me-1">{html.escape(s)}</span>' for s in e["symptoms"][:3])

        card_html += f"""
    <div class="card mb-3 border">
      <div class="card-header bg-white py-3" data-bs-toggle="collapse" data-bs-target="#q{i}" role="button" aria-expanded="false">
        <h5 class="mb-0 fw-semibold" style="font-size:1.05rem;">{question}</h5>
        <div class="mt-1 small text-muted">
          <span class="me-3"><i class="fa-regular fa-file-lines me-1"></i>{source}</span>
          {mat_tags}
          {sym_tags}
        </div>
      </div>
      <div id="q{i}" class="collapse">
        <div class="card-body" style="font-size:.95rem;line-height:1.6;white-space:pre-wrap;">{answer}</div>
        {f'<div class="card-footer bg-white small text-muted border-top-0 pt-0"><a href="{url}" target="_blank" rel="nofollow"><i class="fa-regular fa-link me-1"></i>Original source</a></div>' if url else ''}
      </div>
    </div>"""

    total = len(entries)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(meta_desc)}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{BASE_URL}/kb/{slug}.html" />
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" />
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet" />
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #0f172a; background: #f8fafc; }}
    .kb-header {{ background: linear-gradient(135deg, #16a34a, #0d9488); color: #fff; padding: 3rem 0 2rem; }}
    .kb-header h1 {{ font-weight: 800; letter-spacing: -.02em; }}
    .kb-header .count {{ opacity: .85; }}
    .card-header {{ cursor: pointer; }}
    .card-header:hover {{ background: #f0fdf4 !important; }}
    .card-header h5 {{ color: #0f172a; }}
    .badge {{ font-weight: 500; }}
    .navbar-brand {{ font-weight: 800; }}
    footer {{ background: #0f172a; color: #94a3b8; padding: 2rem 0; font-size: .9rem; }}
    footer a {{ color: #cbd5e1; text-decoration: none; }}
  </style>
</head>
<body>
  <nav class="navbar navbar-expand-lg navbar-light bg-white fixed-top shadow-sm">
    <div class="container">
      <a class="navbar-brand" href="{BASE_URL}"><i class="fa-solid fa-cube text-success me-1"></i>FixMyPrint<span class="text-success">AI</span></a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#nav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="nav">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item"><a class="nav-link" href="{BASE_URL}/kb/index.html">Knowledge Base</a></li>
          <li class="nav-item"><a class="nav-link" href="{BASE_URL}/#waitlist">Join Waitlist</a></li>
          <li class="nav-item ms-lg-2"><a class="btn btn-brand btn-sm px-3" href="{BASE_URL}/#waitlist" style="background:#16a34a;border-color:#16a34a;color:#fff;font-weight:600;">Get Help</a></li>
        </ul>
      </div>
    </div>
  </nav>

  <header class="kb-header" style="margin-top:56px;">
    <div class="container">
      <p class="mb-1" style="text-transform:uppercase;letter-spacing:.08em;font-size:.8rem;opacity:.8;">3D Printing Troubleshooting · {brand}</p>
      <h1 class="mb-1">{html.escape(brand)} Fix Library</h1>
      <p class="count mb-0">{total} hand-curated fixes</p>
    </div>
  </header>

  <div class="container py-4">{card_html}</div>

  <footer>
    <div class="container text-center">
      <div class="mb-2"><i class="fa-solid fa-cube text-success me-1"></i> FixMyPrint<span class="text-success">AI</span></div>
      <div>
        <a href="{BASE_URL}/kb/index.html">Knowledge Base</a> · <a href="{BASE_URL}">Home</a> · <a href="{BASE_URL}/#waitlist">Waitlist</a>
      </div>
      <div class="mt-2">© {datetime.now().year} FixMyPrint AI</div>
    </div>
  </footer>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  <!-- Simple search toggle: close all on new page load for performance -->
  <script>document.querySelectorAll('.collapse.show').forEach(c=>new bootstrap.Collapse(c,{{toggle:false}}).hide())</script>
</body>
</html>"""

def index_page(groups):
    """Generate the Knowledge Base index page."""
    cards = ""
    for brand in ["Bambu Lab", "Prusa", "Creality", "Elegoo", "General"]:
        info = BRAND_INFO.get(brand, {"slug":"general","desc":""})
        entries = groups.get(brand, [])
        count = len(entries)
        if count == 0: continue
        slug = info["slug"]
        cards += f"""
    <div class="col-md-6 col-lg-4 mb-4">
      <a href="{slug}.html" class="text-decoration-none">
        <div class="card h-100 border shadow-sm hover-shadow">
          <div class="card-body">
            <h4 class="card-title fw-bold" style="color:#0f172a;">{html.escape(brand)}</h4>
            <p class="card-text text-muted">{html.escape(info['desc'])}</p>
            <span class="badge bg-success">{count} fixes</span>
          </div>
        </div>
      </a>
    </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>3D Printing Troubleshooting Knowledge Base — FixMyPrint AI</title>
  <meta name="description" content="1,000+ hand-curated 3D printing fixes for Bambu Lab, Prusa, Creality, Elegoo and more. Every fix verified by a real maker. Search by brand, material, or symptom." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{BASE_URL}/kb/index.html" />
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" />
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet" />
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #0f172a; background: #f8fafc; }}
    .kb-header {{ background: linear-gradient(135deg, #16a34a, #0d9488); color: #fff; padding: 3rem 0 2rem; }}
    .kb-header h1 {{ font-weight: 800; letter-spacing: -.02em; }}
    .navbar-brand {{ font-weight: 800; }}
    .hover-shadow:hover {{ box-shadow: 0 8px 24px rgba(0,0,0,.1) !important; transform: translateY(-2px); transition: .2s; }}
    footer {{ background: #0f172a; color: #94a3b8; padding: 2rem 0; font-size: .9rem; }}
    footer a {{ color: #cbd5e1; text-decoration: none; }}
    .brand-card .badge {{ font-size: .85rem; }}
  </style>
</head>
<body>
  <nav class="navbar navbar-expand-lg navbar-light bg-white fixed-top shadow-sm">
    <div class="container">
      <a class="navbar-brand" href="{BASE_URL}"><i class="fa-solid fa-cube text-success me-1"></i>FixMyPrint<span class="text-success">AI</span></a>
    </div>
  </nav>

  <header class="kb-header" style="margin-top:56px;">
    <div class="container">
      <p class="mb-1" style="text-transform:uppercase;letter-spacing:.08em;font-size:.8rem;opacity:.8;">Knowledge Base</p>
      <h1 class="mb-1">3D Printing Fix Library</h1>
      <p class="mb-0" style="opacity:.9;">1,000+ real printing problems, hand-curated by a working maker. Pick your brand below.</p>
    </div>
  </header>

  <div class="container py-4">
    <div class="row">{cards}</div>
  </div>

  <footer>
    <div class="container text-center">
      <div><i class="fa-solid fa-cube text-success me-1"></i> FixMyPrint<span class="text-success">AI</span></div>
      <div class="mt-2"><a href="{BASE_URL}">Home</a> · <a href="{BASE_URL}/#waitlist">Join Waitlist</a></div>
    </div>
  </footer>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

def sitemap_xml(brands):
    now = datetime.utcnow().strftime("%Y-%m-%d")
    urls = [
        f"  <url><loc>{BASE_URL}/</loc><lastmod>{now}</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>",
        f"  <url><loc>{BASE_URL}/kb/index.html</loc><lastmod>{now}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>",
    ]
    for brand, slug, count in brands:
        urls.append(f"  <url><loc>{BASE_URL}/kb/{slug}.html</loc><lastmod>{now}</lastmod><changefreq>monthly</changefreq><priority>{'0.7' if count >= 50 else '0.5'}</priority></url>")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""

def main():
    groups = load_all()
    print(f"Loaded {sum(len(v) for v in groups.values())} entries across {len(groups)} brands")

    brands_for_sitemap = []
    for brand in ["Bambu Lab", "Prusa", "Creality", "Elegoo", "General"]:
        entries = groups.get(brand, [])
        if not entries:
            continue
        info = BRAND_INFO.get(brand, {"slug":"general","desc":""})
        slug = info["slug"]
        desc = info["desc"]
        title = f"{brand} 3D Printer Troubleshooting — {len(entries)} Hand-Curated Fixes | FixMyPrint AI"
        html = page_template(title, desc, brand, entries, slug)
        out_path = os.path.join(OUT_DIR, f"{slug}.html")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  ✓ {slug}.html ({len(entries)} entries)")
        brands_for_sitemap.append((brand, slug, len(entries)))

    # Index
    index_html = index_page(groups)
    with open(os.path.join(OUT_DIR, "index.html"), 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f"  ✓ index.html (KB overview)")

    # Sitemap
    sm = sitemap_xml(brands_for_sitemap)
    with open("C:/Users/23206/WorkBuddy/2026-07-16-21-11-12/site/sitemap.xml", 'w', encoding='utf-8') as f:
        f.write(sm)
    print(f"  ✓ sitemap.xml")

if __name__ == "__main__":
    main()
