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
        self.assertIn("{% include theme-init.html %}", head)
        self.assertLess(
            head.index("{% include theme-init.html %}"),
            head.index('rel="stylesheet"'),
        )
        self.assertIn('id="theme-color"', head)

    def test_default_layout_has_skip_link_and_semantic_main(self):
        layout = read_file("_layouts/default.html")
        self.assertIn('class="skip-link"', layout)
        self.assertIn('<main id="main-content"', layout)
        self.assertIn("{{ content }}", layout)


class GlobalInteractionTests(unittest.TestCase):
    def test_header_has_accessible_explicit_navigation(self):
        header = read_file("_includes/header.html")
        for marker in (
            'class="site-header',
            'id="site-nav"',
            'id="nav-toggle"',
            'id="theme-toggle"',
            'aria-controls="site-nav"',
            'aria-expanded="false"',
            'href="{{ site.baseurl }}/archive/"',
            'href="{{ site.baseurl }}/category/"',
            'href="{{ site.baseurl }}/tag/"',
            'href="{{ site.baseurl }}/about/"',
        ):
            self.assertIn(marker, header)

    def test_theme_script_manages_preferences_and_giscus(self):
        script = read_file("js/theme.js")
        for marker in (
            "farice-theme",
            "matchMedia",
            "localStorage.setItem",
            "dataset.theme",
            "theme-color",
            "giscus-frame",
            "postMessage",
        ):
            self.assertIn(marker, script)

    def test_navigation_script_handles_state_escape_and_outside_click(self):
        script = read_file("js/navigation.js")
        self.assertIn("aria-expanded", script)
        self.assertIn("Escape", script)
        self.assertIn("addEventListener", script)
        self.assertIn("contains", script)

    def test_global_controls_are_safe_and_accessible(self):
        main_script = read_file("js/main.js")
        footer = read_file("_includes/footer.html")
        back_to_top = read_file("_includes/backToTop.html")
        self.assertIn("if (!backToTop)", main_script)
        self.assertIn("addEventListener", main_script)
        self.assertNotIn("window.onscroll", main_script)
        self.assertIn('class="site-footer glass-panel"', footer)
        self.assertIn('aria-label="返回顶部"', back_to_top)


class HomepageTests(unittest.TestCase):
    def test_homepage_uses_approved_sections_and_card_modifiers(self):
        homepage = read_file("index.html")
        for marker in (
            'class="home-hero',
            'class="post-grid"',
            "post-card--featured",
            'class="topic-navigation',
            'aria-label="文章分页"',
            "forloop.first",
        ):
            self.assertIn(marker, homepage)
        self.assertNotIn("Recent Posts", homepage)
        self.assertNotIn("<h3><a", homepage)

    def test_homepage_sanitizes_excerpts_and_calculates_reading_time(self):
        homepage = read_file("index.html")
        for marker in (
            "number_of_words",
            "divided_by",
            "plus",
            "strip_html",
            "strip_newlines",
            "truncate",
        ):
            self.assertIn(marker, homepage)

    def test_homepage_grid_is_dense_and_responsive(self):
        styles = read_file("_sass/_home.scss")
        self.assertIn("grid-auto-flow: dense", styles)
        self.assertIn(".post-card--featured", styles)
        self.assertIn(".post-card--wide", styles)
        self.assertIn("grid-template-columns: repeat(3", styles)
        self.assertIn("grid-template-columns: repeat(2", styles)
        self.assertIn("grid-template-columns: 1fr", styles)


class ArticleExperienceTests(unittest.TestCase):
    def test_post_layout_has_approved_structure_and_comments(self):
        layout = read_file("_layouts/post.html")
        navigation = read_file("_includes/previousAndNext.html")
        for marker in (
            'class="reading-progress"',
            'class="post-shell',
            'class="post-toc-desktop',
            'class="post-toc-mobile',
            'class="post-content"',
            "number_of_words",
            "divided_by",
            "plus",
            "{% if comments_enabled %}",
            "{% include comments.html %}",
        ):
            self.assertIn(marker, layout)
        self.assertIn("<aside", layout)
        self.assertIn("<details", layout)
        self.assertIn('class="post-navigation"', navigation)
        self.assertNotIn("pageContent.js", layout)

    def test_article_script_builds_toc_progress_and_active_heading(self):
        script = read_file("js/article.js")
        for marker in (
            "IntersectionObserver",
            "reading-progress",
            "#markdown-toc",
            "cloneNode",
            "requestAnimationFrame",
            "is-active",
        ):
            self.assertIn(marker, script)
        self.assertIn("tocContainers", script)
        self.assertIn("container.hidden = true", script)
        self.assertIn("has-no-toc", script)

    def test_post_styles_use_sticky_responsive_reading_layout(self):
        styles = read_file("_sass/_post.scss")
        for marker in (
            "position: sticky",
            "var(--reading-width)",
            "scroll-margin-top",
            ".giscus,",
            ".giscus-frame",
            "overflow-x: auto",
            "grid-template-columns: 1fr",
            ".post-shell.has-no-toc",
        ):
            self.assertIn(marker, styles)

    def test_syntax_highlighting_uses_theme_tokens(self):
        styles = read_file("_sass/_syntax-highlighting.scss")
        self.assertIn("var(--color-code-bg)", styles)
        self.assertIn("var(--color-code-text)", styles)


class ContentPageTests(unittest.TestCase):
    def test_archive_uses_timeline_and_year_navigation(self):
        archive = read_file("page/0archives.html")
        self.assertIn('class="content-index', archive)
        self.assertIn('class="archive-timeline"', archive)
        self.assertIn('class="year-navigation', archive)
        self.assertIn('id="y{{ post.date', archive)

    def test_category_and_tag_pages_use_unified_taxonomy_components(self):
        categories = read_file("page/1category.html")
        tags = read_file("page/2tags.html")
        self.assertIn('class="taxonomy-overview', categories)
        self.assertIn("category | last | size", categories)
        self.assertIn('class="tag-cloud', tags)
        self.assertIn("site.tags[tag].size", tags)
        self.assertNotIn("pageContent.js", categories + tags)

    def test_generic_page_and_article_script_support_optional_toc(self):
        layout = read_file("_layouts/page.html")
        script = read_file("js/article.js")
        for marker in ('class="page-hero', 'class="page-content', 'class="page-toc'):
            self.assertIn(marker, layout)
        self.assertIn(".page-toc__content", script)
        self.assertNotIn("pageContent.js", layout)

    def test_about_collections_and_404_use_new_page_system(self):
        about = read_file("page/4about.md")
        collections = read_file("page/3collections.md")
        not_found = read_file("404.md")
        self.assertIn("contact-links", about)
        self.assertIn("description:", collections)
        self.assertTrue(not_found.startswith("---\n"))
        self.assertIn("layout: default", not_found)
        self.assertIn('class="not-found', not_found)
        self.assertIn("/archive/", not_found)

    def test_content_index_styles_are_sticky_and_responsive(self):
        styles = read_file("_sass/_content-index.scss")
        for marker in (
            "position: sticky",
            ".archive-timeline",
            ".tag-cloud",
            ".taxonomy-overview",
            "grid-template-columns: 1fr",
        ):
            self.assertIn(marker, styles)


class CleanupAndDocumentationTests(unittest.TestCase):
    def test_active_templates_do_not_reference_legacy_scripts(self):
        templates = "\n".join(
            read_file(path)
            for path in (
                "_layouts/default.html",
                "_layouts/post.html",
                "_layouts/page.html",
                "page/0archives.html",
                "page/1category.html",
                "page/2tags.html",
                "index.html",
            )
        )
        for legacy_script in ("pageContent.js", "scroll.js", "scroll.min.js"):
            self.assertNotIn(legacy_script, templates)

    def test_legacy_script_files_are_removed(self):
        for relative_path in ("js/content.js", "js/pageContent.js", "js/scroll.js", "js/scroll.min.js"):
            self.assertFalse((ROOT / relative_path).exists(), relative_path)

    def test_active_sass_and_preview_artifacts_are_clean(self):
        stylesheet = read_file("css/main.scss")
        for legacy_partial in ('"reset"', '"index"', '"layout"', '"scrollbar"'):
            self.assertNotIn(legacy_partial, stylesheet)
        gitignore = read_file(".gitignore")
        self.assertIn("_site/", gitignore)
        self.assertIn(".superpowers/", gitignore)

    def test_readme_documents_theme_pages_and_verification(self):
        readme = read_file("README.md")
        for marker in (
            "默认跟随系统",
            "手动切换",
            "首页、文章、归档、分类、标签、合集、关于和 404",
            "python3 tests/test_visual_redesign.py -v",
            "python3 tests/test_comments.py -v",
            "comments: false",
            "bundle exec jekyll build",
        ):
            self.assertIn(marker, readme)

    def test_active_html_does_not_use_javascript_urls(self):
        active_html = "\n".join(
            read_file(path)
            for path in (
                "_includes/header.html",
                "_includes/footer.html",
                "_includes/comments.html",
                "_layouts/default.html",
                "_layouts/post.html",
                "_layouts/page.html",
                "index.html",
            )
        )
        self.assertNotIn("javascript:", active_html.lower())


if __name__ == "__main__":
    unittest.main()
