# Farice Blog

Jekyll 技术博客，部署于 GitHub Pages，记录 AI 编程、云原生、OpenStack、Kubernetes、Python 与工程实践。

## 视觉主题

全站采用渐变玻璃视觉系统，覆盖首页、文章、归档、分类、标签、合集、关于和 404 页面。

- 首页使用响应式瀑布卡片墙。
- 文章页使用粘性目录与双栏阅读布局。
- 移动端自动切换为单列卡片和折叠目录。
- 深浅主题默认跟随系统，也可通过导航栏按钮手动切换。
- 手动切换结果保存在浏览器本地，下次访问继续使用。
- 主题切换会同步更新 Giscus 评论区。
- 页面尊重系统的减少动画偏好。

主题使用系统字体、CSS 渐变和原生 JavaScript，不依赖前端框架或第三方 Web Font。

## 评论系统

文章评论由 Giscus 提供，评论数据保存在 GitHub Discussions 中。所有文章默认开启评论。

### 仓库配置

1. 确保 `Farice4/farice4.github.io` 是公开仓库。
2. 在仓库 Settings → General → Features 中启用 GitHub Discussions。
3. 为该仓库安装 Giscus App。
4. 当前评论使用 Discussions 的 `General` 分类。
5. Giscus 使用 `pathname` 将文章路径映射到 Discussion。
6. 仓库的 `repo_id` 与 `category_id` 已配置完成；更换分类时需要同步更新分类名称和 ID。

`repo_id` 和 `category_id` 是公开标识符，不是访问密钥。仓库中不要保存 GitHub Token 或 OAuth Secret。

### 关闭单篇文章评论

在文章 Front Matter 中设置：

```yaml
comments: false
```

未设置该字段的文章默认显示评论。

## 验证

运行视觉与交互回归测试：

```bash
python3 tests/test_visual_redesign.py -v
```

运行评论配置与模板测试：

```bash
python3 tests/test_comments.py -v
```

检查 JavaScript 语法：

```bash
node --check js/theme.js
node --check js/navigation.js
node --check js/article.js
node --check js/main.js
```

安装项目的 Ruby/Jekyll 依赖后，可执行完整构建：

```bash
bundle exec jekyll build
```
