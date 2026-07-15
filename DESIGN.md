# DESIGN.md — Learn UI Name · 界面叫啥（中英双语 UI 视觉词典）

> 唯一事实源。所有页面、所有 demo、所有轮次的修改都以本文件为准。改风格 = 先改本文件。

## 1. 视觉主题与氛围

「Vercel 式黑白工程美学」。默认纯白底，黑 / 灰阶 / 白三色构成全部界面，
链接蓝 `#0070f3` 是唯一功能色且克制使用。demo（UI 标本）是绝对主角，
站点 chrome 安静、精确、不抢戏。气质 = vercel.com / Geist 设计系统的克制与留白。

- 读取为：开发者向视觉词典参考站，面向用 AI 编程代理的设计师与开发者
- 拨盘：视觉冒险度 3 / 动效强度 4 / 信息密度 7
- 主题：浅色-only（默认白）。不做暗色模式

## 2. 色板与角色

| 角色 | 值 | 用途 |
|---|---|---|
| `--bg` | `#FFFFFF` | 页面底色（纯白） |
| `--bg-2` | `#FAFAFA` | demo 舞台、复制块底 |
| `--fill` | `#F5F5F5` | hover 填充、编号块底 |
| `--line` | `#EAEAEA` | 发丝边框 |
| `--line-strong` | `#D4D4D4` | hover / 强调边框 |
| `--gray-400` | `#A3A3A3` | 标本签、说明文字、占位符 |
| `--gray-500` | `#737373` | 中文对照行、三级文字 |
| `--gray-600` | `#525252` | 次级文字、正文段落 |
| `--gray-700` | `#404040` | 强调段落 |
| `--fg` | `#0A0A0A` | 主文字、标题、激活态 |
| `--blue` | `#0070F3` | 唯一功能色：内容链接、new 标记、focus 环 |
| `--blue-soft` | `rgba(0,112,243,.14)` | 搜索高亮 `<mark>` 底 |

功能色仅在 demo 标本内部按被模仿系统如实使用（macOS 灰、iOS 蓝等），不参与站点主题。
阴影：仅弹层用 `0 8px 30px rgba(0,0,0,.12)`；卡片不用阴影，用发丝边框。

## 3. 排版规则

- 拉丁/数字展示：**Geist**（自托管可变字重 woff2，`assets/fonts/geist-vf.woff2`）
- 代码/术语/标本签：**Geist Mono**（自托管，`assets/fonts/geist-mono-vf.woff2`）
- 中文：系统栈 `-apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", sans-serif`
- 字重只用 400 / 500 / 600；禁用斜体；强调用字重/颜色/下划线
- H1 `letter-spacing: -0.045em`（clamp 40–64px）；详情页 H1 `-0.03em`（clamp 28–40px）
- 正文 15px/1.7；中文对照行 −1 档 + `--gray-500`，形成「原文 + 注」层次
- 数字与 API 符号一律 Geist Mono
- 中西文之间留盘古之白；中文用全角标点
- 标本签（section title）：Geist Mono 11px、大写、tracking 0.12em、`--gray-400`

## 4. 双语对照规则（本站核心）

- 三种阅读模式：`对照`（默认）/ `EN` / `中文`，`<html data-lang-mode="bilingual|en|zh">` 控制，
  localStorage 持久化；页眉切换器（激活态 = 黑底白字）
- 对照模式下：英文在前，中文紧随其后，中文用 `--gray-500`、字号 −1 档
- 术语名（entry/style name）永远保留英文原名，中文译名作为对照行
- API 符号、prompt、brief 原文不翻译只对照：EN 原文 + 中文译文两段并列
- 双语段落始终上下堆叠，窄屏友好；zh-only 模式下中文行继承正文色

## 5. 组件样式

- **标本卡（首页/风格网格）**：上方 demo 舞台（`--bg-2` 底 + `--line` 边框 + 圆角 8px，
  高 200px，内容居中，pointer-events:none 整卡可点），下方名称（EN 500 字重 + 中文对照）、
  Geist Mono 11px 灰符号行、tagline 双语（EN `--gray-600` / ZH `--gray-500`，限 2 行）。
  hover：舞台边框 → `--gray-400`，无位移无阴影
- **标签（new / platform）**：Geist Mono 9–10px 大写 tracking 0.1em；new = `--blue`，platform = `--gray-400`
- **按钮**：圆角 6px、白底 `--line` 边框，hover 边框 → `--gray-400`；`:active scale(0.97)`
- **分段控件（tabs / 语言切换）**：圆角 6px `--line` 边框，激活段 = 黑底白字
- **输入框**：白底 `--line` 边框，focus 时边框 `--fg` + 3px `rgba(0,0,0,.06)` 环；
  右侧 `/` kbd 提示（移动端隐藏）
- **全局 focus-visible**：2px `--blue` outline，offset 2px
- **复制块**：`--bg-2` 底 + `--line` 边框 + 圆角 8px + 等宽字体 + 右上角复制按钮
- **代码块**：同复制块样式，`pre` 可横向滚动
- **风格 DNA 列表**：发丝线分隔；role 徽章 —— defining = 黑底白字实心，
  supporting = 灰边，variable = 虚线边，avoid = 灰边 + 删除线
- **对比标本（vs-pair）**：双栏舞台 + 标签；下方 because / wouldBecomeIf 双卡片
- **表格（翻译表/对比表）**：发丝横线分隔、无竖线、表头 Geist Mono 小号大写 `--gray-400`
- **页眉**：白底 85% 透明 + backdrop blur saturate(1.8)，下发丝边；
  左 wordmark「Learn UI Name / 界面叫啥」，右导航 + 语言切换；移动端导航横向滚动

## 6. 布局原则

- 容器 `max-width: 1080px` 居中，页边距 24px（移动端 16px）
- 首页标本网格：`repeat(auto-fill, minmax(300px, 1fr))`，gap 28px 24px
- 详情页：单列 760px 阅读列宽（DNA/对比区段通栏），demo 舞台通栏
- 间距节奏：hero 72px 顶距、区段 48px 顶距、卡片内 14px
- 分组用发丝线 + 留白，不滥用卡片嵌卡片
- 一个页面一个视觉焦点；留白服务层级

## 7. 深度层级

- z 轴极扁：页面 → sticky 页眉（blur + 发丝边）→ 弹层（词典定义 popover）
- 弹层：`--shadow-pop` + `--line` 边框，圆角 10px

## 8. Do's / Don'ts

**Do**
- demo 标本内部可如实还原被模仿系统的外观（macOS 红绿灯、iOS 蓝开关、Aqua 糖果……）
- 每个术语/风格给一个「记忆点」呈现：解剖编号、对照 prompt、DNA 徽章
- 所有交互元素：hover / active / focus-visible / disabled 状态齐全
- 链接下划线 offset 3px，hover 才出现（导航/卡片除外）

**Don't**
- 任何彩色重音（橙/紫/渐变）——只有黑、灰、白、一点蓝
- 纯黑 `#000` 以外的彩色标题；斜体；Inter/Roboto
- 居中 Hero 大标题 + 三等分卡片横排的 AI 模板感
- 站点 chrome 动效喧宾夺主（demo 才是动画主角）
- 卡片套卡片、阴影堆叠

## 9. 响应式行为

- ≥1024px：3 列网格；≥760px：2 列；<760px：1 列，demo 舞台高 180px
- 详情页 760px 列宽自适应；双语段落不并排
- 页眉移动端：wordmark 中文与导航中文隐藏，导航横向滚动
- 对比标本（vs-pair）移动端变单列
- 禁 `h-screen`，用 `min-height: 100dvh`；flex 文本子项 `min-width: 0`

## 10. Motion 哲学

- 站点 chrome：hover 120–160ms、`:active scale(0.97)`；只动 transform/opacity/border-color
- 缓动：`cubic-bezier(0.23, 1, 0.32, 1)`；禁 ease-in、禁 transition: all
- demo 标本动画是展品内容，不受 300ms 限制，但必须有 `prefers-reduced-motion` 兜底
- 列表入场不做 stagger 炫技；页面切换无转场

## 11. PWA 与工程

- `manifest.webmanifest`：白底主题（`#ffffff`），黑圆角方块 + 白「UI?」图标
  （192 / 512 / maskable-512 / apple-touch-icon-180 / favicon.svg）
- `sw.js`：静态资源 cache-first，页面 network-first 回退缓存，离线回退到首页；
  构建时由 build.py 注入版本号清旧缓存
- nginx：`/sw.js` 与 `/manifest.webmanifest` 强制 `no-cache`，其余静态资源 7d
- 分析：Umami（`data-domains="learnui.qiaomu.ai"`）
