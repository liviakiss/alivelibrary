# ALIVE Library

A living reference of design knowledge — built slowly and intentionally.

ALIVE Library is a free, quietly-made reference site where design knowledge lives across
five themes: cognitive psychology, calm technology, AI interfaces, UX patterns, and the
tools of the craft. Most design writing stops at naming an effect. This goes one layer
deeper — to the mechanism, the research, the *why beneath the why* — then draws the design
implication.

Not a blog. Not a course. A growing body of work to return to.

> **Live:** [alivedesignlibrary.com](https://alivedesignlibrary.com)
> **By:** [Lívia Kiss · ALIVE Design Studio](https://alivedesignstudio.net)

---

## How it works

Entries are written as plain Markdown in `content/`, one file per theme. A small Python
script, `build.py`, parses them and generates a complete static site: a real HTML page per
entry (for clean, indexable URLs), one page per theme, a home page, plus `sitemap.xml` and
`robots.txt`.

There's no framework and no client-side rendering — just generated HTML, one stylesheet,
and a few lines of JavaScript. It loads fast and stays calm, which is part of the point.

```
content/01-mind.md      →  parsed by  →  build.py  →  site/entries/*.html
content/02-calm.md                                    site/themes/*.html
content/03-ai.md                                      site/index.html
content/04-patterns.md                                site/about.html
content/05-tools.md                                   site/sitemap.xml, robots.txt
```

## The themes

| Theme | What it covers |
|-------|----------------|
| **Mind & Behavior** | Cognitive psychology and neuroscience applied to design, down to the mechanism. |
| **Calm Technology** | The philosophy and ethics of attention-respecting design, grounded in research. |
| **AI & Human Interfaces** | Designing for AI honestly — based on how the models actually work. |
| **Patterns & Practice** | Specific UX patterns, with the reasoning and evidence behind each. |
| **Tools & Workflow** | The real tools and decisions of design-engineering work. |

Fifty entries at launch (ten per theme), growing by roughly one every 2–3 weeks.

## Project structure

```
.
├── content/            # Markdown source — one file per theme (the "database")
├── assets/             # style.css, main.js
├── entries/            # generated — one HTML page per entry
├── themes/             # generated — one HTML page per theme
├── about.html          # generated
├── index.html          # generated — the home / start screen
├── sitemap.xml         # generated
├── robots.txt          # generated
├── build.py            # the static-site generator
├── CNAME               # GitHub Pages custom-domain config
└── README.md
```

> Source (`content/`, `build.py`) and generated output live together at the repo root so
> GitHub Pages can serve the site directly.

## Build it locally

Requires Python 3 and the `markdown` package.

```bash
pip install markdown
python3 build.py
```

Preview with any static server:

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Adding a new entry

1. Open the relevant `content/NN-theme.md`.
2. Append a new entry using the same shape as the others:

   ```markdown
   **Full title — optional subtitle after an em-dash**

   **One-line definition, as a single bold sentence.**

   ### The Principle
   ...

   ### Why It Matters for Design & Building
   ...

   ### Real-World Examples
   ...

   ### Visual Suggestion
   (author note — not published; preserved as an HTML comment in the source)

   ### Related Entries
   - Another entry's title
   - And another

   ### References
   1. Author, A. (Year). *Work*. Publisher.
   2. Some source. https://example.com

   *Last updated: Month Year*
   ```

3. Run `python3 build.py`.

The page URL (slug) is derived from the part of the title before the em-dash.
Related-entry links resolve automatically by title; any that don't yet match an existing
entry stay as plain text until that entry is written.

## Design notes

- **Identity:** warm paper (`#ECEAE2`), deep warm ink (`#0C0B09`), a single muted accent
  (`#88867A`). Type is Newsreader (serif body), Inter (UI), and Caveat (margin notes).
- **Reading-first:** ~680px column, generous line-height, no first-line indents.
- **Entry structure:** the three core sections (Principle / Why It Matters / Examples) are
  numbered down a thin vertical line — structure without heavy headers.
- **Theme covers** appear once, at the top of each theme page. Entry pages are text-only.
- **Margin notes:** the CSS system is in place (`<aside class="note">` inside a section's
  `.step-body`); it floats into the right margin on wide screens and falls inline on mobile.
  Intentionally unpopulated — a layer to add by hand over time.
- **No tracking, no popups, no cookie banners, no affiliate links.** Each page ends with a
  quiet line linking to X / LinkedIn for new-entry notifications.

## Deploy (GitHub Pages)

1. Set `BASE_URL` at the top of `build.py` to the production address, then rebuild.
2. Push to the Pages branch. `build.py` emits a `CNAME` file (`alivedesignlibrary.com`) on
   every build, so the custom domain survives rebuilds — just enable HTTPS in the repo's
   Pages settings.

## Not included yet

- Search (theme navigation covers it for now)
- Dark mode (a deliberate post-launch addition)
- Per-entry hand-drawn illustrations

---

© Lívia Kiss · ALIVE Design Studio. Content is the author's own work.
