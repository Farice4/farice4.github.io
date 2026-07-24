# Farice Blog Visual Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the approved gradient-glass visual system to every public blog page while preserving Jekyll content, URLs, pagination, and Giscus comments.

**Architecture:** A small design-token layer drives light and dark themes through CSS custom properties. Jekyll layouts remain server-rendered and semantic; CSS Grid replaces float-based layout, while three dependency-free deferred scripts enhance theme switching, mobile navigation, article progress, and table-of-contents behavior. Python standard-library tests validate the Liquid, SCSS, JavaScript, accessibility, and cleanup contracts before optional Jekyll build verification.

**Tech Stack:** Jekyll, Liquid, SCSS, vanilla JavaScript, Python 3 `unittest`, Giscus

---

## File Map

- Create `_includes/theme-init.html`: pre-paint theme selection from local storage or system preference.
- Modify `_includes/head.html`: theme color metadata, theme bootstrap, stylesheet URLs.
- Modify `_layouts/default.html`: skip link, semantic main container, deferred scripts.
- Create `_sass/_tokens.scss`: light/dark semantic design tokens.
- Create `_sass/_base.scss`: global background, typography, element defaults, reduced-motion behavior.
- Create `_sass/_utilities.scss`: containers, screen-reader helpers, focus treatment.
- Create `_sass/_home.scss`: approved Hero, dense card grid, topic navigation, pagination.
- Create `_sass/_content-index.scss`: archive, category, and tag index styling.
- Rewrite `_sass/_header.scss`, `_sass/_post.scss`, `_sass/_page.scss`, `_sass/_footer.scss`, `_sass/_backToTop.scss`, `_sass/_syntax-highlighting.scss` for the new system.
- Modify `css/main.scss`: import only the active visual system partials.
- Rewrite `_includes/header.html`: explicit navigation, mobile button, theme button.
- Rewrite `_includes/footer.html`: compact glass footer.
- Rewrite `_includes/backToTop.html`: accessible fixed control.
- Create `js/theme.js`: theme state, system preference, local storage, Giscus synchronization.
- Create `js/navigation.js`: accessible mobile navigation.
- Create `js/article.js`: progress bar, current heading, desktop/mobile table of contents.
- Rewrite `js/main.js`: safe back-to-top behavior.
- Rewrite `index.html`: approved gradient Hero and dense post card grid.
- Rewrite `_layouts/post.html`: sticky TOC, article header/body, related content, comments.
- Rewrite `_includes/previousAndNext.html`: navigation cards.
- Rewrite `_layouts/page.html`: unified page card and optional TOC.
- Rewrite `page/0archives.html`, `page/1category.html`, `page/2tags.html`: unified content-index markup.
- Update `page/3collections.md`, `page/4about.md`: optional descriptions and unchanged content meaning.
- Rewrite `404.md`: default layout, recovery actions.
- Delete `js/pageContent.js`, `js/scroll.js`, `js/scroll.min.js`: obsolete layout and scrolling behavior.
- Create `.gitignore`: ignore `_site/` and `.superpowers/` preview artifacts.
- Create `tests/test_visual_redesign.py`: dependency-free regression suite.
- Update `README.md`: theme architecture, commands, page behavior.

## Task 1: Establish Theme Tokens and Semantic Shell

**Files:**
- Create: `tests/test_visual_redesign.py`
- Create: `_includes/theme-init.html`
- Create: `_sass/_tokens.scss`
- Create: `_sass/_base.scss`
- Create: `_sass/_utilities.scss`
- Modify: `_includes/head.html`
- Modify: `_layouts/default.html`
- Modify: `css/main.scss`

- [ ] **Step 1: Write failing shell and token tests**

Create `tests/test_visual_redesign.py` with a shared `read_file()` helper and `ThemeFoundationTests` that assert:

```python
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_file(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


class ThemeFoundationTests(unittest.TestCase):
    def test_main_scss_imports_new_foundation(self):
        stylesheet = read_file("css/main.scss")
        for partial in ('"tokens"', '"base"', '"utilities"'):
            self.assertIn(partial, stylesheet)

    def test_tokens_define_light_and_dark_semantic_colors(self):
        tokens = read_file("_sass/_tokens.scss")
        for token in (
            "--color-bg:",
            "--color-surface:",
            "--color-text:",
            "--color-muted:",
            "--color-border:",
            "--gradient-brand:",
        ):
            self.assertIn(token, tokens)
        self.assertIn(':root[data-theme="dark"]', tokens)
        self.assertIn("@media (prefers-color-scheme: dark)", tokens)

    def test_theme_is_selected_before_the_stylesheet(self):
        head = read_file("_includes/head.html")
        self.assertIn('{% include theme-init.html %}', head)
        self.assertLess(
            head.index('{% include theme-init.html %}'),
            head.index('rel="stylesheet"'),
        )
        self.assertIn('id="theme-color"', head)

    def test_default_layout_has_skip_link_and_semantic_main(self):
        layout = read_file("_layouts/default.html")
        self.assertIn('class="skip-link"', layout)
        self.assertIn('<main id="main-content"', layout)
        self.assertIn("{{ content }}", layout)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run RED verification**

Run `python3 tests/test_visual_redesign.py ThemeFoundationTests -v`.

Expected: four failures because the new foundation files and semantic shell do not exist.

- [ ] **Step 3: Implement the theme bootstrap**

Create `_includes/theme-init.html` as an inline guarded script that:

```html
<script>
(function() {
    var storageKey = 'farice-theme';
    var savedTheme = null;
    try {
        savedTheme = localStorage.getItem(storageKey);
    } catch (error) {
        savedTheme = null;
    }
    var systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    document.documentElement.dataset.theme = savedTheme === 'light' || savedTheme === 'dark' ? savedTheme : systemTheme;
    document.documentElement.dataset.themeSource = savedTheme ? 'user' : 'system';
}());
</script>
```

- [ ] **Step 4: Implement semantic token partials**

Create `_sass/_tokens.scss` with `:root`, automatic dark media fallback, and explicit `[data-theme]` blocks. Define the exact semantic variables listed in the test plus spacing, radius, shadow, content-width, reading-width, and transition variables. Use the approved purple-to-cyan gradient and deep blue-black dark background.

Create `_sass/_base.scss` with global box sizing, body radial-gradient background, system UI font, serif article body font variable, responsive media defaults, accessible link behavior, image/table/code defaults, native smooth scrolling, and `prefers-reduced-motion` overrides.

Create `_sass/_utilities.scss` with `.site-container`, `.reading-container`, `.sr-only`, `.skip-link`, `.glass-panel`, and shared `:focus-visible` treatment.

- [ ] **Step 5: Rewrite head and default layout**

In `_includes/head.html`, preserve existing SEO/analytics Liquid, change the site URL stylesheet references to whitespace-free paths, add `<meta id="theme-color" name="theme-color" content="#edf1fa">`, and include `theme-init.html` before CSS.

Rewrite `_layouts/default.html` to use a language-aware root, skip link, header, `<main id="main-content">`, footer, back-to-top control, and four deferred scripts: `theme.js`, `navigation.js`, `article.js`, and `main.js`. Remove `scroll.min.js`.

- [ ] **Step 6: Replace active Sass imports**

Change `css/main.scss` to import exactly:

```scss
@import
        "tokens",
        "base",
        "utilities",
        "header",
        "home",
        "post",
        "content-index",
        "page",
        "syntax-highlighting",
        "footer",
        "backToTop";
```

- [ ] **Step 7: Run GREEN verification**

Run `python3 tests/test_visual_redesign.py ThemeFoundationTests -v`.

Expected: four tests pass.

## Task 2: Build Header, Theme Switching, and Global Controls

**Files:**
- Modify: `tests/test_visual_redesign.py`
- Rewrite: `_includes/header.html`
- Rewrite: `_includes/footer.html`
- Rewrite: `_includes/backToTop.html`
- Rewrite: `_sass/_header.scss`
- Rewrite: `_sass/_footer.scss`
- Rewrite: `_sass/_backToTop.scss`
- Create: `js/theme.js`
- Create: `js/navigation.js`
- Rewrite: `js/main.js`

- [ ] **Step 1: Add failing interaction tests**

Add `GlobalInteractionTests` asserting:

- Header contains `site-header`, `site-nav`, `nav-toggle`, `theme-toggle`, `aria-controls`, and `aria-expanded`.
- Navigation uses explicit links for `/`, `/archive/`, `/category/`, `/tag/`, and `/about/`.
- `theme.js` contains `farice-theme`, `matchMedia`, `localStorage.setItem`, `dataset.theme`, `theme-color`, `giscus-frame`, and `postMessage`.
- `navigation.js` toggles `aria-expanded`, closes on Escape, and uses `addEventListener`.
- `main.js` guards missing `.back-to-top` and uses `addEventListener` rather than `window.onscroll`.
- Footer uses `site-footer glass-panel` and back-to-top control has an `aria-label`.

- [ ] **Step 2: Run RED verification**

Run `python3 tests/test_visual_redesign.py GlobalInteractionTests -v`.

Expected: failures for missing accessible controls and scripts.

- [ ] **Step 3: Rewrite the global components**

Create a sticky glass header with explicit navigation links, active-page Liquid checks, an accessible theme button, and an accessible mobile menu button. Rewrite the footer as a compact glass panel preserving GitHub, email, visitor statistics, and attribution. Rewrite back-to-top as a `<button>`-like anchor with `aria-label="返回顶部"`.

- [ ] **Step 4: Implement global JavaScript**

`js/theme.js` must expose no globals and must:

- Resolve saved theme before system theme.
- Update `document.documentElement.dataset.theme`.
- Update `#theme-color`.
- Set theme button labels and pressed state.
- Persist manual choices.
- Follow system changes only when no manual preference exists.
- Send `{ giscus: { setConfig: { theme: theme } } }` to `https://giscus.app` when the Giscus frame exists or announces readiness.

`js/navigation.js` must toggle the mobile menu, synchronize `aria-expanded`, close on Escape, close on outside click, and safely exit when controls are absent.

`js/main.js` must show the back-to-top control after 320px, hide it near the top, and use native scrolling behavior.

- [ ] **Step 5: Implement global component styles**

Rewrite header, footer, and back-to-top Sass using token variables. Desktop navigation stays inline; below 760px the menu becomes a glass dropdown. Include focus, hover, active, dark-theme, and reduced-motion-compatible states.

- [ ] **Step 6: Run GREEN verification**

Run the interaction tests and then `python3 tests/test_visual_redesign.py -v`.

Expected: all current tests pass.

## Task 3: Implement the Approved Homepage

**Files:**
- Modify: `tests/test_visual_redesign.py`
- Rewrite: `index.html`
- Create: `_sass/_home.scss`

- [ ] **Step 1: Add failing homepage tests**

Add `HomepageTests` asserting:

- `index.html` contains `home-hero`, `post-grid`, `post-card--featured`, `topic-navigation`, and accessible pagination.
- The first paginator post uses a featured modifier through `forloop.first`.
- Reading time uses `number_of_words`, `divided_by`, and `plus` Liquid filters.
- Card excerpts use `strip_html`, `strip_newlines`, and `truncate`.
- `_sass/_home.scss` contains `grid-auto-flow: dense`, featured/wide card spans, three responsive column states, and a one-column mobile state.
- The old `Recent Posts` sidebar markup is absent.

- [ ] **Step 2: Run RED verification**

Run `python3 tests/test_visual_redesign.py HomepageTests -v`.

Expected: failures because the homepage still uses the old list/sidebar layout.

- [ ] **Step 3: Rewrite the homepage template**

Use semantic sections:

1. Gradient `home-hero` with the approved engineering-journal copy and links to archive/about.
2. `post-grid` loop over `paginator.posts`.
3. Featured modifier for the first card, wide modifier for every fourth non-featured card, normal modifier otherwise.
4. Each card shows category, title, sanitized excerpt, date, calculated reading time, and up to three tags.
5. `topic-navigation` below the grid lists categories, tags, and archive actions.
6. Pagination uses actual `paginator.previous_page_path` and `paginator.next_page_path`; no manually concatenated final-page URL.

- [ ] **Step 4: Implement approved homepage styling**

Create responsive dense CSS Grid, gradient featured card, glass standard cards, whole-card link treatment, compact metadata, topic chips, and accessible pagination. Use `nth-child` only for subtle decorative variation; structural modifiers come from Liquid classes.

- [ ] **Step 5: Run GREEN verification**

Run homepage tests and then the full visual suite.

Expected: all current tests pass.

## Task 4: Implement the Approved Article Reading Experience

**Files:**
- Modify: `tests/test_visual_redesign.py`
- Rewrite: `_layouts/post.html`
- Rewrite: `_includes/previousAndNext.html`
- Rewrite: `_sass/_post.scss`
- Rewrite: `_sass/_syntax-highlighting.scss`
- Create: `js/article.js`

- [ ] **Step 1: Add failing article tests**

Add `ArticleExperienceTests` asserting:

- Post layout contains `reading-progress`, `post-shell`, `post-toc-desktop`, `post-toc-mobile`, `post-content`, `post-navigation`, and the existing guarded Giscus comment include.
- Reading time uses Jekyll word-count filters.
- Desktop TOC is an `<aside>` and mobile TOC uses `<details>`.
- `article.js` uses `IntersectionObserver`, updates progress, clones `#markdown-toc`, and guards absent elements.
- Post Sass uses `position: sticky`, reading width tokens, scroll margins, responsive single-column layout, responsive tables/images, and Giscus width rules.
- Syntax highlighting uses semantic token backgrounds rather than the old fixed palette.

- [ ] **Step 2: Run RED verification**

Run `python3 tests/test_visual_redesign.py ArticleExperienceTests -v`.

Expected: failures because the old sidebar and `pageContent.js` remain.

- [ ] **Step 3: Rewrite article markup**

Preserve the existing `comments_enabled` calculation. Build:

- Reading progress element.
- Article header with category, title, optional description, author, date, reading time, and tags.
- Desktop sticky TOC aside and mobile `<details>` TOC.
- Semantic article body.
- Related-post cards using the existing tag intersection logic.
- Previous/next navigation cards.
- Guarded Giscus section.

Remove the old `.page .left/.right`, anchor button, and `pageContent.js` script.

- [ ] **Step 4: Implement article behavior**

`js/article.js` must:

- Update progress with `requestAnimationFrame` throttling.
- Clone the generated `#markdown-toc` into desktop and mobile containers.
- Add smooth anchor classes without rewriting URLs.
- Observe article headings and apply `.is-active` to matching TOC links.
- Safely do nothing on non-article pages.

- [ ] **Step 5: Implement article and code styles**

Use the approved two-column grid with a sticky left TOC, constrained reading column, serif body text, themed code blocks, responsive images/tables, related cards, previous/next cards, and mobile collapse below 900px. Preserve the previously added comment spacing and safe Giscus sizing.

- [ ] **Step 6: Run GREEN verification**

Run article tests, `tests/test_comments.py`, and the full visual suite.

Expected: both comment and visual suites pass.

## Task 5: Unify Archive, Category, Tag, Page, About, and 404 Views

**Files:**
- Modify: `tests/test_visual_redesign.py`
- Rewrite: `_layouts/page.html`
- Rewrite: `page/0archives.html`
- Rewrite: `page/1category.html`
- Rewrite: `page/2tags.html`
- Modify: `page/3collections.md`
- Modify: `page/4about.md`
- Rewrite: `404.md`
- Create: `_sass/_content-index.scss`
- Rewrite: `_sass/_page.scss`

- [ ] **Step 1: Add failing unified-page tests**

Add `ContentPageTests` asserting:

- Archive uses `content-index`, `archive-timeline`, year IDs, and year navigation.
- Categories use `taxonomy-overview`, category counts, and grouped article lists.
- Tags use `tag-cloud`, tag counts, and grouped article lists.
- Generic page layout uses `page-hero`, `page-content`, and optional `page-toc` without `pageContent.js`.
- About includes contact-link markup and Collections remains Markdown-driven.
- `404.md` has Front Matter, `layout: default`, `not-found`, a home link, and an archive link.
- Content-index Sass contains sticky navigation, timeline styling, tag chips, and responsive single-column behavior.

- [ ] **Step 2: Run RED verification**

Run `python3 tests/test_visual_redesign.py ContentPageTests -v`.

Expected: failures for old page/right-sidebar markup and missing 404 layout.

- [ ] **Step 3: Rewrite content index templates**

Use a shared `content-index site-container` shell. Preserve existing Liquid loops and anchor IDs, but replace old `.left/.right` markup with semantic header, sticky index navigation, grouped sections, article rows, and count badges.

- [ ] **Step 4: Rewrite generic page and 404 templates**

Generic page layout uses a glass hero and reading card, with desktop/mobile TOC containers populated by `article.js`. About retains the existing personal information and adds styled contact links. Collections keeps the existing headings. 404 gains Front Matter, helpful copy, and home/archive actions.

- [ ] **Step 5: Implement shared content-page styles**

Create timeline, taxonomy overview, tag cloud, grouped article, generic content card, contact card, and not-found styles with desktop sticky navigation and mobile single-column fallback.

- [ ] **Step 6: Run GREEN verification**

Run content-page tests and all regression tests.

Expected: all tests pass.

## Task 6: Remove Legacy Behavior, Document, and Verify

**Files:**
- Modify: `tests/test_visual_redesign.py`
- Delete: `js/pageContent.js`
- Delete: `js/scroll.js`
- Delete: `js/scroll.min.js`
- Create: `.gitignore`
- Modify: `README.md`

- [ ] **Step 1: Add failing cleanup tests**

Add `CleanupAndDocumentationTests` asserting:

- Default, post, page, archive, category, and tag templates do not reference `pageContent.js`, `scroll.js`, or `scroll.min.js`.
- Deleted legacy files do not exist.
- No active Sass import references `reset`, `index`, `layout`, or `scrollbar` legacy partials.
- `.gitignore` contains `_site/` and `.superpowers/`.
- README documents theme behavior, visual test command, comment test command, `comments: false`, and optional Jekyll build.
- No changed HTML contains `javascript:` URLs or configurable third-party script sources.

- [ ] **Step 2: Run RED verification**

Run `python3 tests/test_visual_redesign.py CleanupAndDocumentationTests -v`.

Expected: failures because legacy scripts still exist and documentation is incomplete.

- [ ] **Step 3: Remove obsolete files and references**

Delete the three legacy JavaScript files after all references are removed. Keep unrelated `assets/js` files untouched because they belong to a separate unused asset tree and are outside the active theme path.

- [ ] **Step 4: Add ignore rules and update README**

Create `.gitignore` with:

```gitignore
_site/
.sass-cache/
.jekyll-cache/
.superpowers/
```

Update README with the approved design overview, automatic/manual theme behavior, page coverage, Giscus configuration, per-post opt-out, Python test commands, and optional Jekyll build command.

- [ ] **Step 5: Run all automated verification**

Run:

```bash
python3 tests/test_comments.py -v
python3 tests/test_visual_redesign.py -v
ruby -e 'require "yaml"; YAML.load_file("_config.yml"); puts "YAML OK"'
node --check js/theme.js
node --check js/navigation.js
node --check js/article.js
node --check js/main.js
git diff --check
```

Expected: both Python suites pass, YAML prints `YAML OK`, every JavaScript syntax check exits zero, and Git diff check exits zero.

- [ ] **Step 6: Run static security and legacy scans**

Run:

```bash
rg -n -i "duoshuo|disqus|javascript:|window\.onscroll|pageContent\.js|scroll\.min\.js" _config.yml _includes _layouts page index.html css js README.md
rg -n -i "(github[_-]?token|oauth[_-]?secret|api[_-]?key|password)\s*[:=]\s*[^#[:space:]]+" _config.yml _includes _layouts page index.html js README.md tests
```

Expected: no active legacy provider/script patterns and no credential assignments. Test assertions mentioning removed names are intentionally outside the scanned paths.

- [ ] **Step 7: Attempt Jekyll build without installing dependencies**

Run `bundle exec jekyll build` only if `bundle` and the project dependencies are already available. If unavailable, record the build as blocked and do not add or download dependencies without approval.

- [ ] **Step 8: Review desktop/mobile/theme states**

If a local build is available, verify at widths 1440px, 1024px, 768px, and 360px in light and dark themes. Confirm no horizontal overflow, mobile menu keyboard behavior, TOC collapse, card-grid fallback, Giscus theme synchronization, and readable focus states.

## Completion Constraints

- Do not create a Git commit, branch, push, or pull request unless the user explicitly requests it.
- Do not alter article URLs, post bodies, category names, tag names, or Giscus mapping.
- Do not add a frontend framework, third-party font, image CDN, or new analytics service.
- Do not commit `.superpowers/` visual companion files.
- Do not install build dependencies without user approval.
