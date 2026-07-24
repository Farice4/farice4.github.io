# Giscus Comments Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the inactive legacy comment integrations with a configurable Giscus comment section that is enabled for every post by default and can be disabled per post.

**Architecture:** Jekyll site configuration owns all trusted Giscus settings. The post layout calculates one `comments_enabled` flag and uses it for the heading, include, and sidebar link, while the include only renders the fixed Giscus client script. Dependency-free Python tests inspect the configuration and Liquid templates because this repository currently has no test framework or installed Jekyll executable.

**Tech Stack:** Jekyll, Liquid, Giscus, SCSS, Python 3 `unittest`

---

## File Map

- Create `tests/test_comments.py`: dependency-free regression tests for configuration, rendering guards, script attributes, styling, and documentation.
- Modify `_config.yml`: remove inactive Disqus settings and define trusted Giscus configuration.
- Modify `_includes/comments.html`: replace legacy providers with the Giscus client embed.
- Modify `_layouts/post.html`: calculate comment availability once and conditionally render every comment-related UI element.
- Modify `_sass/_post.scss`: add responsive spacing and safe iframe sizing for the comment section.
- Modify `README.md`: document repository setup, configuration IDs, per-post opt-out, and verification commands.

## Task 1: Add Comment Configuration Contract

**Files:**
- Create: `tests/test_comments.py`
- Modify: `_config.yml:24`

- [ ] **Step 1: Write the failing configuration tests**

Create `tests/test_comments.py` with:

```python
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
        self.assertRegex(self.config, r'(?m)^  repo_id: "[^"]*"$')
        self.assertRegex(self.config, r'(?m)^  category_id: "[^"]*"$')

    def test_legacy_comment_configuration_is_removed(self):
        self.assertNotRegex(self.config, r"(?m)^disqus:")
        self.assertNotIn("duoshuo_shortname", self.config)
        self.assertNotIn("disqus_shortname", self.config)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
python3 tests/test_comments.py -v
```

Expected: three failures because `_config.yml` still contains Disqus and has no Giscus contract.

- [ ] **Step 3: Replace the legacy configuration**

Replace `_config.yml:24-32` with:

```yaml
# comments
comments:
  provider: giscus

giscus:
  repo: Farice4/farice4.github.io
  repo_id: "MDEwOlJlcG9zaXRvcnkxNDMxMTc1NzY="
  category: General
  category_id: "MDE4OkRpc2N1c3Npb25DYXRlZ29yeTMyMzY3MDY4"
  mapping: pathname
  strict: "1"
  reactions_enabled: "1"
  emit_metadata: "0"
  input_position: top
  theme: preferred_color_scheme
  lang: zh-CN
  loading: lazy
```

The public repository and category IDs are fixed to the values returned for this repository and its `General` discussion category.

- [ ] **Step 4: Run the configuration tests and verify GREEN**

Run:

```bash
python3 tests/test_comments.py -v
```

Expected: `Ran 3 tests` and `OK`.

## Task 2: Replace Legacy Embeds With Giscus

**Files:**
- Modify: `tests/test_comments.py`
- Modify: `_includes/comments.html:1`

- [ ] **Step 1: Write failing Giscus embed tests**

Add this class before the `if __name__ == "__main__":` block in `tests/test_comments.py`:

```python
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
```

- [ ] **Step 2: Run the embed tests and verify RED**

Run:

```bash
python3 tests/test_comments.py CommentEmbedTests -v
```

Expected: three failures because the include still contains the old providers.

- [ ] **Step 3: Replace `_includes/comments.html`**

Use exactly:

```html
<div class="giscus"></div>
<script
    src="https://giscus.app/client.js"
    data-repo="{{ site.giscus.repo | escape }}"
    data-repo-id="{{ site.giscus.repo_id | escape }}"
    data-category="{{ site.giscus.category | escape }}"
    data-category-id="{{ site.giscus.category_id | escape }}"
    data-mapping="{{ site.giscus.mapping | escape }}"
    data-strict="{{ site.giscus.strict | escape }}"
    data-reactions-enabled="{{ site.giscus.reactions_enabled | escape }}"
    data-emit-metadata="{{ site.giscus.emit_metadata | escape }}"
    data-input-position="{{ site.giscus.input_position | escape }}"
    data-theme="{{ site.giscus.theme | escape }}"
    data-lang="{{ site.giscus.lang | escape }}"
    data-loading="{{ site.giscus.loading | escape }}"
    crossorigin="anonymous"
    async
></script>
<noscript>评论功能需要启用 JavaScript。</noscript>
```

- [ ] **Step 4: Run the embed tests and verify GREEN**

Run:

```bash
python3 tests/test_comments.py CommentEmbedTests -v
```

Expected: `Ran 3 tests` and `OK`.

## Task 3: Make Comment Rendering Conditional

**Files:**
- Modify: `tests/test_comments.py`
- Modify: `_layouts/post.html:5`
- Modify: `_layouts/post.html:67`
- Modify: `_layouts/post.html:83`

- [ ] **Step 1: Write failing layout behavior tests**

Add this class before the `if __name__ == "__main__":` block in `tests/test_comments.py`:

```python
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

    def test_sidebar_comment_link_is_guarded_by_the_shared_flag(self):
        guarded_link = re.compile(
            r"{% if comments_enabled %}\s*"
            r'<li><a href="#comments">评论</a></li>\s*'
            r"{% endif %}",
            re.DOTALL,
        )
        self.assertRegex(self.layout, guarded_link)
```

- [ ] **Step 2: Run the layout tests and verify RED**

Run:

```bash
python3 tests/test_comments.py CommentLayoutTests -v
```

Expected: three failures because the layout always renders comment UI.

- [ ] **Step 3: Calculate one shared flag**

Insert this Liquid block immediately after the front matter in `_layouts/post.html`:

```liquid
{% assign comments_enabled = false %}
{% if site.comments.provider == 'giscus' and page.comments != false and site.giscus.repo != empty and site.giscus.repo_id != empty and site.giscus.category != empty and site.giscus.category_id != empty %}
    {% assign comments_enabled = true %}
{% endif %}
```

- [ ] **Step 4: Guard the main comment section**

Replace the current unconditional heading and include with:

```html
        {% if comments_enabled %}
        <section class="comments" aria-labelledby="comments">
            <h2 id="comments">评论</h2>
            {% include comments.html %}
        </section>
        {% endif %}
```

- [ ] **Step 5: Guard the sidebar link**

Replace the current comment list item with:

```liquid
                    {% if comments_enabled %}
                    <li><a href="#comments">评论</a></li>
                    {% endif %}
```

- [ ] **Step 6: Run the layout tests and verify GREEN**

Run:

```bash
python3 tests/test_comments.py CommentLayoutTests -v
```

Expected: `Ran 3 tests` and `OK`.

## Task 4: Style and Document the Comment System

**Files:**
- Modify: `tests/test_comments.py`
- Modify: `_sass/_post.scss:39`
- Modify: `README.md:1`

- [ ] **Step 1: Write failing style and documentation tests**

Add this class before the `if __name__ == "__main__":` block in `tests/test_comments.py`:

```python
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
```

- [ ] **Step 2: Run the presentation tests and verify RED**

Run:

```bash
python3 tests/test_comments.py CommentPresentationTests -v
```

Expected: two failures because no Giscus styles or setup documentation exist.

- [ ] **Step 3: Add focused comment styles**

Insert inside `.page[post] .left` in `_sass/_post.scss`, before the existing commented-out `.post-recent` block:

```scss
        .comments {
            margin-top: 36px;

            h2 {
                margin-bottom: 24px;
            }

            .giscus,
            .giscus-frame {
                width: 100%;
                max-width: 100%;
            }

            noscript {
                display: block;
                padding: 16px;
                color: #6b6a6a;
                background: #f7f7f7;
                border-radius: 4px;
            }
        }
```

- [ ] **Step 4: Replace the README with setup and usage documentation**

Use:

```markdown
# Farice Blog

Jekyll 技术博客，部署于 GitHub Pages。

## 评论系统

文章评论由 Giscus 提供，评论数据保存在 GitHub Discussions 中。所有文章默认开启评论。

### 仓库配置

1. 确保 `Farice4/farice4.github.io` 是公开仓库。
2. 在仓库 Settings → General → Features 中启用 GitHub Discussions。
3. 为该仓库安装 Giscus App。
4. 在 Discussions 中创建或选择允许 Giscus 创建讨论的分类。
5. 在 Giscus 配置页面选择仓库、`pathname` 映射和目标分类。
6. 将生成的 `repo_id` 与 `category_id` 写入 `_config.yml` 的 `giscus` 配置。

`repo_id` 和 `category_id` 是公开标识符，不是访问密钥。仓库中不要保存 GitHub Token 或 OAuth Secret。

### 关闭单篇文章评论

在文章 Front Matter 中设置：

```yaml
comments: false
```

未设置该字段的文章默认显示评论。

## 验证

运行无需额外依赖的评论模板测试：

```bash
python3 tests/test_comments.py -v
```

安装项目的 Ruby/Jekyll 依赖后，可执行完整构建：

```bash
bundle exec jekyll build
```
```

- [ ] **Step 5: Run the full regression suite and verify GREEN**

Run:

```bash
python3 tests/test_comments.py -v
```

Expected: `Ran 11 tests` and `OK`.

- [ ] **Step 6: Run repository integrity checks**

Run:

```bash
git diff --check
rg -n "duoshuo|disqus" _config.yml _includes _layouts README.md
```

Expected: `git diff --check` exits successfully and `rg` returns no matches.

- [ ] **Step 7: Build Jekyll when dependencies are available**

Run:

```bash
bundle exec jekyll build
```

Expected: the site builds successfully. In the current environment, `bundle` and `jekyll` are unavailable, so record this validation as blocked rather than installing unrelated dependencies without approval.

## Task 5: Administrator Activation Check

**Files:**
- Modify: `_config.yml:31`
- Modify: `_config.yml:33`

- [ ] **Step 1: Enable the GitHub-side prerequisites**

The repository administrator confirms Giscus App remains installed for `Farice4/farice4.github.io`, which already has GitHub Discussions enabled, and keeps the configured `General` category available.

- [ ] **Step 2: Copy the generated public identifiers**

Confirm `_config.yml` contains the exact `data-repo-id` and `data-category-id` returned by the Giscus configurator. Preserve the surrounding quotes and do not guess either identifier.

- [ ] **Step 3: Re-run tests and build**

Run:

```bash
python3 tests/test_comments.py -v
bundle exec jekyll build
```

Expected: all 11 tests pass and the Jekyll build succeeds.

- [ ] **Step 4: Verify one default and one disabled post**

Open a normal article and confirm Giscus loads below the article. Temporarily set `comments: false` on a local test article, rebuild, and confirm the comment section and sidebar link are both absent; revert that temporary article edit after verification.

## Completion Constraints

- Do not create a Git commit unless the user explicitly asks for one.
- Do not store GitHub tokens, OAuth secrets, or administrator credentials in the repository.
- Do not enable the client script with guessed repository or category IDs.
- Do not modify existing articles solely to opt them into comments; default behavior already covers them.
