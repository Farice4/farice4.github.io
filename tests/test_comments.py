import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_file(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


class CommentConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.config = read_file("_config.yml")

    def test_giscus_is_the_configured_comment_provider(self):
        self.assertRegex(
            self.config,
            r"(?m)^comments:\n  provider: giscus$",
        )

    def test_giscus_configuration_has_all_supported_options(self):
        expected_lines = (
            "  repo: Farice4/farice4.github.io",
            '  repo_id: "MDEwOlJlcG9zaXRvcnkxNDMxMTc1NzY="',
            "  category: General",
            '  category_id: "MDE4OkRpc2N1c3Npb25DYXRlZ29yeTMyMzY3MDY4"',
            "  mapping: pathname",
            '  strict: "1"',
            '  reactions_enabled: "1"',
            '  emit_metadata: "0"',
            "  input_position: top",
            "  theme: preferred_color_scheme",
            "  lang: zh-CN",
            "  loading: lazy",
        )
        for expected_line in expected_lines:
            with self.subTest(expected_line=expected_line):
                self.assertIn(expected_line, self.config)

    def test_legacy_comment_configuration_is_removed(self):
        self.assertNotRegex(self.config, r"(?m)^disqus:")
        self.assertNotIn("duoshuo_shortname", self.config)
        self.assertNotIn("disqus_shortname", self.config)


class CommentEmbedTests(unittest.TestCase):
    def setUp(self):
        self.include = read_file("_includes/comments.html")

    def test_embed_uses_only_the_fixed_giscus_client(self):
        self.assertIn('src="https://giscus.app/client.js"', self.include)
        self.assertNotIn("disqus", self.include.lower())
        self.assertNotIn("duoshuo", self.include.lower())

    def test_embed_reads_and_escapes_every_configured_attribute(self):
        expected_attributes = {
            "data-repo": "repo",
            "data-repo-id": "repo_id",
            "data-category": "category",
            "data-category-id": "category_id",
            "data-mapping": "mapping",
            "data-strict": "strict",
            "data-reactions-enabled": "reactions_enabled",
            "data-emit-metadata": "emit_metadata",
            "data-input-position": "input_position",
            "data-theme": "theme",
            "data-lang": "lang",
            "data-loading": "loading",
        }
        for attribute, key in expected_attributes.items():
            expected = f'{attribute}="{{{{ site.giscus.{key} | escape }}}}"'
            with self.subTest(attribute=attribute):
                self.assertIn(expected, self.include)

    def test_embed_is_non_blocking_and_has_a_noscript_message(self):
        self.assertRegex(self.include, r"(?m)^    async$")
        self.assertIn('crossorigin="anonymous"', self.include)
        self.assertIn("评论功能需要启用 JavaScript。", self.include)


class CommentLayoutTests(unittest.TestCase):
    def setUp(self):
        self.layout = read_file("_layouts/post.html")

    def test_layout_defaults_to_disabled_then_checks_every_requirement(self):
        self.assertIn("{% assign comments_enabled = false %}", self.layout)
        requirements = (
            "site.comments.provider == 'giscus'",
            "page.comments != false",
            "site.giscus.repo != empty",
            "site.giscus.repo_id != empty",
            "site.giscus.category != empty",
            "site.giscus.category_id != empty",
        )
        for requirement in requirements:
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, self.layout)
        self.assertIn("{% assign comments_enabled = true %}", self.layout)

    def test_comment_section_is_guarded_by_the_shared_flag(self):
        guarded_section = re.compile(
            r"{% if comments_enabled %}\s*"
            r'<section class="comments" aria-labelledby="comments">\s*'
            r'<h2 id="comments">评论</h2>\s*'
            r"{% include comments.html %}\s*"
            r"</section>\s*{% endif %}",
            re.DOTALL,
        )
        self.assertRegex(self.layout, guarded_section)

    def test_comment_include_is_never_rendered_without_the_shared_flag(self):
        comment_guard = self.layout.index("{% if comments_enabled %}")
        comment_include = self.layout.index("{% include comments.html %}")
        comment_end = self.layout.index("{% endif %}", comment_include)
        self.assertLess(comment_guard, comment_include)
        self.assertLess(comment_include, comment_end)


class CommentPresentationTests(unittest.TestCase):
    def setUp(self):
        self.styles = read_file("_sass/_post.scss")
        self.readme = read_file("README.md")

    def test_comment_section_has_spacing_and_safe_width(self):
        self.assertIn(".comments {", self.styles)
        self.assertIn("margin-top: 36px;", self.styles)
        self.assertIn(".giscus,", self.styles)
        self.assertIn(".giscus-frame {", self.styles)
        self.assertIn("max-width: 100%;", self.styles)

    def test_readme_documents_repository_setup_and_configuration(self):
        required_text = (
            "GitHub Discussions",
            "Giscus App",
            "repo_id",
            "category_id",
            "comments: false",
            "python3 tests/test_comments.py -v",
        )
        for text in required_text:
            with self.subTest(text=text):
                self.assertIn(text, self.readme)


if __name__ == "__main__":
    unittest.main()
