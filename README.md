# ALIVE Library

A living reference of design knowledge — a static site generated from plain markdown.
Warm paper, deep ink, quiet structure. Light mode, fast, no tracking.

## How it's built

Entries live as markdown in `content/`, one file per theme:

```
content/01-mind.md      Mind & Behavior
content/02-calm.md      Calm Technology
content/03-ai.md        AI & Human Interfaces
content/04-patterns.md  Patterns & Practice   (add your entries here)
content/05-tools.md     Tools & Workflow      (add your entries here)
```

`build.py` parses them and writes a complete static site into `site/`:
real HTML per entry (good for SEO), theme pages, a home grid, `about.html`,
`robots.txt`, and `sitemap.xml`.

## Build it

Needs Python 3 and the `markdown` package:

```bash
pip install markdown
python3 build.py
```

Output lands in `site/`. Preview locally with any static server:

```bash
cd site && python3 -m http.server 8000
# open http://localhost:8000
```

## Adding a new entry

1. Open the relevant `content/NN-theme.md`.
2. Paste a new entry using the exact same shape as the others:

```
**Full title — optional subtitle after an em-dash**

**One-line definition, as a single bold sentence.**

### The Principle
...

### Why It Matters for Design & Building
...

### Real-World Examples
...

### Visual Suggestion
(author note — NOT published; kept as an HTML comment in the source)

### Related Entries
- Some other entry title
- Another entry title

### References
1. Author, A. (Year). *Work*. Publisher.
2. Some source. https://example.com

*Last updated: Month Year*
```

3. Rerun `python3 build.py`. Related-entry links resolve automatically by title;
   any that don't match an existing entry stay as plain text until that entry exists.

The slug (and the page URL) is derived from the part of the title before the em-dash.

## Deploy (GitHub Pages)

1. Set `BASE_URL` at the top of `build.py` to your real address
   (e.g. `https://library.alivedesignstudio.net`), then rebuild.
2. Push the **contents of `site/`** to your Pages branch/root.
3. Point the `library` subdomain at GitHub Pages and enable HTTPS.

## Email subscription (Buttondown)

The signup form is a standard Buttondown embed. Before it works:

1. Create an account at buttondown.email.
2. In `build.py`, set `BUTTONDOWN_USER` to your username and rebuild
   (replaces the `YOURUSERNAME` placeholder in every form).
3. Customize the confirmation + new-entry emails in Buttondown to match the
   library voice ("New in the library: <title>" + one line + link).

No data is collected by the site itself — the form posts directly to Buttondown.

## Notes on the design

- Colors, type (Newsreader / Inter / Caveat), and the numbered-line entry
  structure follow the locked visual spec.
- Margin notes: the CSS system is ready (`<aside class="note">…</aside>` inside a
  section's `.step-body`). It's intentionally unpopulated — add notes in your own
  voice when you're ready; they float into the right margin on wide screens and
  fall inline on mobile.
- Per-entry hand-drawn illustrations are not included; the five theme cover images
  are used on cards, theme headers, and as social/OG images.
- "Visual Suggestion" sections are treated as author notes — preserved as HTML
  comments in the generated pages, not shown to readers.
- No affiliate links anywhere.

## What's not here yet

- `content/04-patterns.md` and `content/05-tools.md` — paste the 20 entries and rebuild.
- Search (the theme nav covers navigation for now).
- Dark mode (explicitly a later, post-launch addition).
