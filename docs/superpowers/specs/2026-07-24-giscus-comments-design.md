# Giscus 评论系统设计

## 目标

为现有 Jekyll GitHub Pages 博客增加可靠、低维护成本的文章评论功能，并修复当前评论配置与模板字段不一致导致评论区无法加载的问题。

评论系统采用 Giscus 和 GitHub Discussions。所有文章默认开启评论；文章可通过 Front Matter 中的 `comments: false` 单独关闭。

## 当前状态

- 博客是无服务端的 Jekyll 静态站点，部署于 `farice4.github.io`。
- `_layouts/post.html` 始终显示评论标题和侧边目录入口。
- `_includes/comments.html` 保留多说与 Disqus 集成代码。
- `_config.yml` 使用嵌套字段 `disqus.shortname`，模板却读取 `site.disqus_shortname`，因此现有 Disqus 配置不会生效。
- 多说服务已经不适合作为新评论系统继续保留。

## 方案选择

### 采用：Giscus

Giscus 使用 GitHub Discussions 保存文章评论，适合公开的 GitHub Pages 仓库，无需维护数据库、认证服务或评论 API。读者使用 GitHub 账号参与讨论。

### 不采用：Utterances

Utterances 使用 GitHub Issues 保存评论。它同样适用于静态站点，但 Discussions 的讨论结构、回复和表情回应更符合博客评论场景。

### 不采用：自建评论后端

自建方案需要额外处理身份认证、数据存储、反垃圾、输入验证、限流、审核和服务可用性，明显超过当前静态博客的需求范围。

## 配置设计

在 `_config.yml` 中移除失效的旧评论配置，增加以下结构：

```yaml
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

`repo_id` 和 `category_id` 是公开标识符，不是密钥，可以提交到仓库。两个 ID 均已通过 GitHub 与 Giscus 的公开接口确认。

`mapping: pathname` 使用文章稳定路径匹配 Discussion；`strict: "1"` 防止相似路径误匹配。文章标题变化不会改变现有文章路径时，评论仍关联到原 Discussion。

## 渲染设计

### 评论启用规则

评论区只在以下条件全部满足时渲染：

1. `site.comments.provider == "giscus"`。
2. 当前文章没有设置 `comments: false`。
3. `site.giscus.repo`、`site.giscus.repo_id`、`site.giscus.category` 和 `site.giscus.category_id` 均非空。

所有文章默认满足第二项，无需逐篇修改已有文章。

### 文章布局

`_layouts/post.html` 负责计算一次 `comments_enabled`，并用同一结果控制：

- 评论区标题。
- `_includes/comments.html` 的渲染。
- 右侧文章目录中的评论锚点。

这样可避免评论组件关闭或配置不完整时仍出现空标题和无效目录链接。

评论标题改为“评论”，保持页面面向中文读者的一致性。

### 评论组件

`_includes/comments.html` 只负责输出 Giscus 容器和官方客户端脚本，不再包含多说或 Disqus 兼容分支。

脚本属性全部从 `site.giscus` 读取，并使用 Liquid 的 `escape` 过滤器处理配置值。脚本采用：

- `src="https://giscus.app/client.js"`。
- `async`，避免阻塞文章内容渲染。
- `crossorigin="anonymous"`。
- `loading="lazy"`，在读者接近评论区时加载。

## 用户体验

- 评论输入框位于现有评论上方，便于读者直接留言。
- Giscus 使用简体中文界面。
- 主题跟随操作系统浅色或深色偏好。
- 评论区与正文、上一篇/下一篇之间保持清晰间距。
- 小屏设备使用同样的内容宽度，不产生横向滚动。
- 当 JavaScript 被禁用时，显示简短提示，说明评论功能需要 JavaScript。

## 配置缺失行为

生产环境配置不完整时，不输出 Giscus 脚本，也不显示空评论标题或目录入口。

为避免向普通读者暴露部署细节，不在线上页面显示仓库 ID 缺失提示。配置完整性通过构建测试检查，并在 README 中提供配置步骤。

## 安全与隐私

- 不引入自建用户输入接口，评论内容由 GitHub/Giscus 处理。
- 配置中不保存 GitHub Token、OAuth Secret 或其他凭据。
- 所有 Liquid 配置值在写入 HTML 属性前执行转义。
- 第三方脚本仅从固定的 `https://giscus.app/client.js` 加载，脚本地址不可由页面 Front Matter 覆盖。
- 单篇文章只能控制是否显示评论，不能覆盖仓库、分类或脚本地址。

## 仓库前置条件

部署前需要由仓库管理员完成：

1. 确认 `Farice4/farice4.github.io` 是公开仓库。
2. 确认仓库设置中已启用 GitHub Discussions。
3. 确认该仓库已安装 Giscus GitHub App。
4. 使用允许 Giscus 创建新 Discussion 的 `General` 分类。
5. 确认 `_config.yml` 中的仓库 ID 与分类 ID 匹配当前仓库配置。

## 测试策略

当前仓库没有现成测试框架，因此不引入大型 JavaScript 测试栈。增加轻量级 Ruby 测试或仓库已有环境可执行的等价静态测试，验证生成逻辑和模板约束。

必须覆盖：

1. 默认文章启用评论。
2. `comments: false` 的文章不显示评论标题、脚本和目录入口。
3. Giscus 配置缺失时不输出第三方脚本。
4. 配置完整时脚本包含仓库、分类、映射、语言、主题和懒加载属性。
5. 旧多说与 Disqus 脚本不再存在。
6. 生成站点后不存在指向已关闭评论区的 `#comments` 链接。

如果本地 Jekyll 环境可用，再执行完整站点构建，确认 Liquid 模板和 Sass 编译成功。

## 文档更新

更新 `README.md`，包括：

- 评论系统说明。
- GitHub Discussions 和 Giscus App 的启用步骤。
- Giscus ID 的配置位置。
- 使用 `comments: false` 关闭单篇文章评论的示例。
- 本地构建与验证命令。

## 非目标

本次不实现：

- 匿名评论。
- 评论计数展示。
- 首页评论摘要或最近评论列表。
- 评论数据迁移。
- 自定义 GitHub OAuth 登录。
- 自建审核后台、垃圾评论检测或邮件通知。

## 验收标准

- 配置完整后，每篇未显式关闭评论的文章底部显示可用的 Giscus 评论区。
- `comments: false` 可完整移除单篇文章的评论 UI 和导航入口。
- 页面正文加载不被评论脚本阻塞。
- 桌面端和移动端均无明显布局溢出。
- 仓库中不保留可执行的多说或 Disqus 评论代码。
- README 足以让维护者独立完成 Giscus 的仓库配置。
- 所有新增测试和可用的 Jekyll 构建检查通过。
