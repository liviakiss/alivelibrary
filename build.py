#!/usr/bin/env python3
"""
ALIVE Library static site generator.

Reads per-theme markdown files from content/ (01-mind.md ... 05-tools.md),
parses each entry, and emits a multi-file static site into site/:
  - index.html               (home grid, all entries)
  - about.html               (about the library)
  - themes/<slug>.html        (one page per theme)
  - entries/<slug>.html       (one page per entry)
  - assets/style.css, assets/main.js
  - robots.txt, sitemap.xml

Adding a new entry = edit the relevant content/NN-theme.md file and rerun:
    python3 build.py
"""

import os
import re
import html
import shutil
import datetime
import markdown as md

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

BASE_URL = "https://alivedesignlibrary.com"          # production domain
STUDIO_URL = "https://alivedesignstudio.net"

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(HERE, "content")
SITE_DIR = os.path.join(HERE, "site")
ASSETS_SRC = os.path.join(HERE, "assets")

# theme key -> metadata. Key matches the NN-<key>.md filename stem suffix.
THEMES = {
    "mind": {
        "file": "01-mind.md",
        "name": "Mind & Behavior",
        "nav": "Mind",
        "slug": "mind",
        "desc": "Cognitive psychology, neuroscience, and behavioral science applied to "
                "design — grounded in the actual mechanisms, not just the named effects.",
        "cover": "https://res.cloudinary.com/dnnfhyeuv/image/upload/v1781278707/"
                 "grok-image-c291e0a1-e684-4e62-8b74-1da5c2fcf85a_nx1tcm.jpg",
    },
    "calm": {
        "file": "02-calm.md",
        "name": "Calm Technology",
        "nav": "Calm Tech",
        "slug": "calm",
        "desc": "Mindful, attention-respecting design — the philosophy and ethics of "
                "intentional technology, grounded in research rather than vibes.",
        "cover": "https://res.cloudinary.com/dnnfhyeuv/image/upload/v1781278707/"
                 "grok-image-282f823e-4afa-45b2-9eb4-3239ec514818_krsuax.jpg",
    },
    "ai": {
        "file": "03-ai.md",
        "name": "AI & Human Interfaces",
        "nav": "AI",
        "slug": "ai",
        "desc": "Designing products that integrate AI thoughtfully — grounded in how the "
                "models actually work, so the guidance is technically real.",
        "cover": "https://res.cloudinary.com/dnnfhyeuv/image/upload/v1781278707/"
                 "grok-image-d3dfdec1-6189-432b-8368-d5d50886923c_cfdpwb.jpg",
    },
    "patterns": {
        "file": "04-patterns.md",
        "name": "Patterns & Practice",
        "nav": "Patterns",
        "slug": "patterns",
        "desc": "Specific UX patterns and decisions, with the reasoning and research behind "
                "each one — not a screenshot gallery.",
        "cover": "https://res.cloudinary.com/dnnfhyeuv/image/upload/v1781278707/"
                 "grok-image-3b2786bb-fd87-4d36-a1b3-659ae57b6abd_thmrjf.jpg",
    },
    "tools": {
        "file": "05-tools.md",
        "name": "Tools & Workflow",
        "nav": "Tools",
        "slug": "tools",
        "desc": "The actual tools, processes, and decisions of design-engineering work. "
                "Honest and experience-based, not sponsored roundups.",
        "cover": "https://res.cloudinary.com/dnnfhyeuv/image/upload/v1781278707/"
                 "grok-image-e5762b2d-2eba-409d-8fcb-9f0fbabc0837_bt4wgq.jpg",
    },
}

# nav order
THEME_ORDER = ["mind", "calm", "ai", "patterns", "tools"]

MAIN_SECTIONS = ["The Principle", "Why It Matters for Design & Building", "Real-World Examples"]
TODAY = datetime.date.today().strftime("%B %Y")

# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

ENTRY_RE = re.compile(
    r"\*\*(?P<title>[^\n]+?)\*\*\s*\n\s*\n"
    r"\*\*(?P<oneliner>[^\n]+?)\*\*\s*\n"
    r"(?P<body>.*?)"
    r"\*Last updated:[^\n]*\*",
    re.DOTALL,
)

SECTION_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)


def short_title(title):
    """The display 'short' title = part before an em-dash, trimmed."""
    return title.split("—")[0].strip()


def norm(s):
    """Normalize a title for related-entry matching."""
    s = s.lower()
    s = s.split("—")[0]           # drop after em-dash
    s = s.split("(")[0]           # drop parentheticals
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def slugify(s):
    s = short_title(s).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def split_sections(body):
    """Return dict {section_name: raw_markdown} preserving order."""
    out = {}
    matches = list(SECTION_RE.finditer(body))
    for i, m in enumerate(matches):
        name = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        out[name] = body[start:end].strip()
    return out


def linkify_references(raw):
    """Render a numbered reference list to an <ol>, linkifying bare URLs."""
    items = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^\d+\.\s*", "", line)        # strip leading "N. "
        items.append(inline_format(line, link_urls=True))
    lis = "\n".join(f"    <li>{it}</li>" for it in items)
    return f"<ol class=\"refs\">\n{lis}\n  </ol>"


def inline_format(text, link_urls=False):
    """Escape, then apply **bold**, *italic*, and (optionally) bare-URL links."""
    text = html.escape(text)
    if link_urls:
        def repl(m):
            url = m.group(0)
            dom = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
            return (f'<a href="{url}" class="ref-link" target="_blank" '
                    f'rel="noopener">{dom}</a>')
        text = re.sub(r"https?://[^\s)]+", repl, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    return text


def parse_theme(theme_key):
    """Parse one theme's markdown file into a list of entry dicts."""
    meta = THEMES[theme_key]
    path = os.path.join(CONTENT_DIR, meta["file"])
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        text = f.read()

    entries = []
    for m in ENTRY_RE.finditer(text):
        title = m.group("title").strip()
        oneliner = m.group("oneliner").strip()
        body = m.group("body")
        sections = split_sections(body)
        entries.append({
            "theme": theme_key,
            "title": title,
            "short": short_title(title),
            "oneliner": oneliner,
            "sections": sections,
            "slug": slugify(title),
        })
    return entries


# --------------------------------------------------------------------------
# Rendering helpers
# --------------------------------------------------------------------------

def head(title, description, prefix, og_image, canonical):
    desc = html.escape(description, quote=True)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{og_image}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=Inter:wght@400;500;600&family=Caveat:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<div class="progress" id="progress" aria-hidden="true"></div>
"""


def nav(prefix, active=None):
    links = [f'<a href="{prefix}index.html"'
             + (' class="active"' if active == "all" else "") + ">All</a>"]
    for k in THEME_ORDER:
        t = THEMES[k]
        cls = ' class="active"' if active == k else ""
        links.append(f'<a href="{prefix}themes/{t["slug"]}.html"{cls}>{t["nav"]}</a>')
    sep = '<span class="dot" aria-hidden="true">·</span>'
    return (f'<header class="site-head">\n'
            f'  <a class="wordmark" href="{prefix}index.html">ALIVE <span>LIBRARY</span></a>\n'
            f'  <nav class="theme-nav">{sep.join(links)}</nav>\n'
            f'</header>\n')


def footer(prefix):
    return (f'<footer class="site-foot">\n'
            f'  <p>By <a href="{STUDIO_URL}" target="_blank" rel="noopener">Lívia Kiss · ALIVE Design Studio</a></p>\n'
            f'  <p class="muted">A living reference, revised over time.</p>\n'
            f'</footer>\n'
            f'<script src="{prefix}assets/main.js"></script>\n'
            f'</body>\n</html>')


def email_form():
    return """<section class="follow" aria-label="Follow for new entries">
  <p class="follow-lead">New entries are published every 2–3 weeks.<br><span class="muted">Follow along on <a href="https://x.com/LiviaKissDesign" target="_blank" rel="noopener">X</a> or <a href="https://www.linkedin.com/in/l%C3%ADvia-kiss-991401391/" target="_blank" rel="noopener">LinkedIn</a> to get notified.</span></p>
</section>
"""


def card(entry, prefix, show_tag=True):
    """Text-only entry card (no image). Used in theme-page entry lists."""
    t = THEMES[entry["theme"]]
    tag = (f'  <span class="tag">{html.escape(t["name"]).upper()}</span>\n'
           if show_tag else "")
    return (f'<a class="card" href="{prefix}entries/{entry["slug"]}.html">\n'
            f'{tag}'
            f'  <h3 class="card-title">{html.escape(entry["short"])}</h3>\n'
            f'  <p class="card-desc">{html.escape(entry["oneliner"])}</p>\n'
            f'</a>\n')


def theme_card(theme_key, count, prefix):
    """Text-only theme card for the home page (no cover image)."""
    t = THEMES[theme_key]
    plural = "entry" if count == 1 else "entries"
    return (f'<a class="theme-card" href="{prefix}themes/{t["slug"]}.html">\n'
            f'  <span class="tag">THEME · {count} {plural}</span>\n'
            f'  <h3 class="theme-card-title">{html.escape(t["name"])}</h3>\n'
            f'  <p class="theme-card-desc">{html.escape(t["desc"])}</p>\n'
            f'  <span class="explore">Explore →</span>\n'
            f'</a>\n')


# --------------------------------------------------------------------------
# Page builders
# --------------------------------------------------------------------------

def build_entry_page(entry, slug_map, prefix="../"):
    t = THEMES[entry["theme"]]
    canonical = f"{BASE_URL}/entries/{entry['slug']}.html"
    title = f"{entry['short']} — ALIVE Library"
    parts = [head(title, entry["oneliner"], prefix, t["cover"], canonical),
             nav(prefix, active=entry["theme"])]

    parts.append('<main id="main" class="entry">\n')

    # header
    parts.append('<article>\n<header class="entry-head">\n')
    parts.append(f'  <span class="tag">{html.escape(t["name"]).upper()}</span>\n')
    parts.append(f'  <h1 class="entry-title">{html.escape(entry["short"])}</h1>\n')
    parts.append(f'  <p class="updated muted">Last updated: {TODAY}</p>\n')
    parts.append('</header>\n')

    # one-line definition (lead)
    parts.append(f'<p class="definition">{inline_format(entry["oneliner"])}</p>\n')

    # visual suggestion preserved as comment (authoring note, not shown)
    if "Visual Suggestion" in entry["sections"]:
        vs = entry["sections"]["Visual Suggestion"].replace("--", "—")
        parts.append(f"<!-- Visual suggestion (author note):\n{vs}\n-->\n")

    # numbered main sections
    parts.append('<div class="numbered">\n')
    n = 0
    for sec in MAIN_SECTIONS:
        if sec not in entry["sections"]:
            continue
        n += 1
        body_html = md.markdown(entry["sections"][sec], extensions=["extra"])
        parts.append('  <section class="step">\n')
        parts.append(f'    <div class="step-num">{n:02d}</div>\n')
        parts.append('    <div class="step-body">\n')
        parts.append(f'      <h2>{html.escape(sec)}</h2>\n')
        parts.append(f'      {body_html}\n')
        parts.append('    </div>\n  </section>\n')
    parts.append('</div>\n')

    # related entries
    if "Related Entries" in entry["sections"]:
        parts.append('<section class="related">\n  <h2>Related entries</h2>\n  <ul>\n')
        for line in entry["sections"]["Related Entries"].splitlines():
            line = line.strip()
            if not line.startswith("-"):
                continue
            label = line.lstrip("-").strip()
            target = resolve_related(label, slug_map, entry["slug"])
            if target:
                parts.append(f'    <li><a href="{prefix}entries/{target}.html">'
                             f'{html.escape(short_title(label))}</a></li>\n')
            else:
                parts.append(f'    <li>{html.escape(short_title(label))}</li>\n')
        parts.append('  </ul>\n</section>\n')

    # references
    if "References" in entry["sections"]:
        parts.append('<section class="references">\n  <h2>References</h2>\n  ')
        parts.append(linkify_references(entry["sections"]["References"]))
        parts.append('\n</section>\n')

    parts.append('</article>\n')
    parts.append(email_form())
    parts.append('</main>\n')
    parts.append(footer(prefix))
    return "".join(parts)


def resolve_related(label, slug_map, self_slug):
    key = norm(label)
    # exact
    if key in slug_map and slug_map[key] != self_slug:
        return slug_map[key]
    # containment either direction
    for k, v in slug_map.items():
        if v == self_slug:
            continue
        if key and (key in k or k in key):
            return v
    return None


def build_home(theme_entries, prefix=""):
    canonical = f"{BASE_URL}/index.html"
    title = "ALIVE Library — a living reference of design knowledge"
    desc = ("A free, carefully made reference of design knowledge — cognitive science, "
            "calm technology, AI interfaces, patterns, and tools.")
    total = sum(len(v) for v in theme_entries.values())
    parts = [head(title, desc, prefix, THEMES["mind"]["cover"], canonical),
             nav(prefix, active="all")]
    parts.append('<main id="main">\n')

    # big start screen
    parts.append('<section class="start">\n'
                 '  <p class="start-kicker">A LIVING REFERENCE OF DESIGN KNOWLEDGE</p>\n'
                 '  <h1 class="start-title">ALIVE<br>Library</h1>\n'
                 '  <p class="start-sub">Design knowledge, built slowly and intentionally — '
                 'each idea traced down to the science beneath it, and connected to the rest.</p>\n'
                 '  <a class="start-cue" href="#about" aria-label="Begin reading">↓</a>\n'
                 '</section>\n')

    # about
    parts.append('<section class="home-about" id="about">\n'
                 '  <span class="tag">ABOUT</span>\n'
                 '  <p>Most design writing stops at naming an effect. ALIVE Library goes one '
                 'layer deeper — to the mechanism, the research, the why beneath the why — then '
                 'draws the design implication. Not a blog, not a course. A growing body of work '
                 'to return to, learn from, and pass along.</p>\n'
                 f'  <p class="muted">{total} entries across five themes, revised over time. '
                 'Roughly one new entry every few weeks.</p>\n'
                 '</section>\n')

    # themes
    parts.append('<section class="home-themes">\n'
                 '  <h2 class="section-label">The themes</h2>\n'
                 '  <div class="theme-grid">\n')
    for k in THEME_ORDER:
        if k in theme_entries:
            parts.append(theme_card(k, len(theme_entries[k]), prefix))
    parts.append('  </div>\n</section>\n')

    parts.append(email_form())
    parts.append('</main>\n')
    parts.append(footer(prefix))
    return "".join(parts)


def build_theme_page(theme_key, entries, prefix="../"):
    t = THEMES[theme_key]
    canonical = f"{BASE_URL}/themes/{t['slug']}.html"
    title = f"{t['name']} — ALIVE Library"
    parts = [head(title, t["desc"], prefix, t["cover"], canonical),
             nav(prefix, active=theme_key)]
    parts.append('<main id="main">\n')
    parts.append('<section class="theme-hero">\n')
    parts.append(f'  <img class="theme-hero-img" src="{t["cover"]}" '
                 f'alt="{html.escape(t["name"])}" loading="lazy">\n')
    parts.append(f'  <div><span class="tag">THEME</span>'
                 f'<h1>{html.escape(t["name"])}</h1>'
                 f'<p>{html.escape(t["desc"])}</p></div>\n')
    parts.append('</section>\n')
    parts.append('<section class="entry-list">\n')
    for e in entries:
        parts.append(card(e, prefix, show_tag=False))
    parts.append('</section>\n')
    parts.append(footer(prefix))
    return "".join(parts)


def build_about(prefix=""):
    canonical = f"{BASE_URL}/about.html"
    title = "About — ALIVE Library"
    desc = "About the ALIVE Library and how it is made."
    parts = [head(title, desc, prefix, THEMES["mind"]["cover"], canonical),
             nav(prefix, active=None)]
    parts.append('<main id="main" class="entry">\n<article>\n')
    parts.append('<h1 class="entry-title">About the library</h1>\n')
    parts.append('<p class="definition">A free, beautifully made reference where design '
                 'knowledge lives across several themes — read through a rigorous, '
                 'psychologically-grounded lens.</p>\n')
    parts.append('<div class="prose">\n'
                 '<p>Most design writing stays at the surface — naming an effect and moving on. '
                 'ALIVE Library goes one layer deeper, to the mechanism and the research beneath '
                 'it, then draws the design implication. That depth is the point.</p>\n'
                 '<p>The library grows by roughly one entry every few weeks. Entries are revised '
                 'over time; the only date shown is when each was last updated.</p>\n'
                 f'<p>Made by <a href="{STUDIO_URL}" target="_blank" rel="noopener">Lívia Kiss '
                 'at ALIVE Design Studio</a>.</p>\n</div>\n')
    parts.append('</article>\n')
    parts.append(email_form())
    parts.append('</main>\n')
    parts.append(footer(prefix))
    return "".join(parts)


def build_sitemap(all_entries):
    urls = [f"{BASE_URL}/index.html", f"{BASE_URL}/about.html"]
    urls += [f"{BASE_URL}/themes/{THEMES[k]['slug']}.html"
             for k in THEME_ORDER if parse_theme(k)]
    urls += [f"{BASE_URL}/entries/{e['slug']}.html" for e in all_entries]
    body = "\n".join(
        f'  <url><loc>{u}</loc></url>' for u in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f'{body}\n</urlset>\n')


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    if os.path.exists(SITE_DIR):
        shutil.rmtree(SITE_DIR)
    os.makedirs(os.path.join(SITE_DIR, "entries"))
    os.makedirs(os.path.join(SITE_DIR, "themes"))
    os.makedirs(os.path.join(SITE_DIR, "assets"))

    # parse all themes that have content files
    theme_entries = {}
    all_entries = []
    for k in THEME_ORDER:
        es = parse_theme(k)
        if es:
            theme_entries[k] = es
            all_entries.extend(es)

    # build slug map for related resolution (normalized short title -> slug)
    slug_map = {}
    for e in all_entries:
        slug_map[norm(e["title"])] = e["slug"]

    # entries
    for e in all_entries:
        with open(os.path.join(SITE_DIR, "entries", e["slug"] + ".html"),
                  "w", encoding="utf-8") as f:
            f.write(build_entry_page(e, slug_map))

    # themes
    for k, es in theme_entries.items():
        with open(os.path.join(SITE_DIR, "themes", THEMES[k]["slug"] + ".html"),
                  "w", encoding="utf-8") as f:
            f.write(build_theme_page(k, es))

    # home + about
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_home(theme_entries))
    with open(os.path.join(SITE_DIR, "about.html"), "w", encoding="utf-8") as f:
        f.write(build_about())

    # assets
    for fn in os.listdir(ASSETS_SRC):
        shutil.copy(os.path.join(ASSETS_SRC, fn), os.path.join(SITE_DIR, "assets", fn))

    # robots + sitemap
    with open(os.path.join(SITE_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
    with open(os.path.join(SITE_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(build_sitemap(all_entries))

    # CNAME — GitHub Pages custom domain (re-emitted each build so it isn't lost)
    domain = BASE_URL.split("://", 1)[-1].rstrip("/")
    with open(os.path.join(SITE_DIR, "CNAME"), "w", encoding="utf-8") as f:
        f.write(domain + "\n")

    print(f"Built {len(all_entries)} entries across {len(theme_entries)} themes.")
    for k in THEME_ORDER:
        n = len(theme_entries.get(k, []))
        print(f"  {THEMES[k]['name']}: {n}")


if __name__ == "__main__":
    main()
