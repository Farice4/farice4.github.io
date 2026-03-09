# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Jekyll static site blog hosted on GitHub Pages at https://farice4.github.io. The site is written primarily in Chinese and documents the author's journey in IT, covering topics like OpenStack, Kubernetes, Python, and Linux.

## Commands

### Build and Serve

```bash
# Install dependencies
bundle install

# Serve locally with live reload
bundle exec jekyll serve

# Build for production
bundle exec jekyll build
```

## Architecture

### Jekyll Structure

```
├── _config.yml        # Site configuration (title, URL, theme, pagination, comments)
├── _layouts/          # HTML templates (default, post, page, demo)
├── _includes/         # Reusable HTML snippets (header, footer, head, comments)
├── _posts/            # Blog posts organized by category (OpenStack, Kubernetes, Python, Linux, etc.)
├── _drafts/           # Unpublished posts
├── _sass/             # SCSS partials imported by main.scss
├── css/               # Compiled stylesheets
├── js/                # JavaScript files (main.js, scroll.js, pageContent.js, etc.)
├── page/              # Static pages (about, collections)
├── index.html         # Homepage with pagination and sidebar
└── 404.md             # Custom 404 page
```

### Key Configuration (_config.yml)

- **Theme**: Custom theme using kramdown markdown and Rouge syntax highlighting
- **Pagination**: 6 posts per page using jekyll-paginate
- **Comments**: Uses Disqus (shortname: fabian4)
- **URL**: http://farice4.github.io

### Post Front Matter

Posts use YAML front matter with these fields:
```yaml
---
layout: post
title: "Post Title"
date: YYYY-MM-DD
categories: Category
tags: [tag1, tag2]
author: Author Name
---
```

### Styling

- Main stylesheet: `css/main.scss` imports partials from `_sass/`
- Custom font: Fontello icon font in `assets/font/`
- Responsive design with mobile-friendly layouts

### Key Includes

- `header.html` - Site navigation header
- `footer.html` - Site footer
- `head.html` - HTML head with meta tags and stylesheets
- `category.html` / `tag.html` - Display post categories and tags
- `comments.html` - Disqus comments integration
- `backToTop.html` - Back to top button
