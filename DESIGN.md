# DESIGN.md — LearnUI / Name That UI 中英双语视觉词典

> 唯一事实源。所有页面、所有 demo、所有轮次的修改都以本文件为准。改风格 = 先改本文件。

## 1. 视觉主题与氛围

「暖纸标本馆」。一本摆在工作室桌上的 UI 图鉴：暖石纸底、发丝边框、等宽字体标本签、
一枚信号橙作为全站唯一重音色。demo（UI 标本）是绝对主角，站点 chrome 安静、精确、
不抢戏。整体气质 = Linear 的工程克制 × 词典/图鉴的编辑感。

- 读取为：开发者向视觉词典参考站，面向用 AI 编程代理的设计师与开发者
- 拨盘：视觉冒险度 5 / 动效强度 5 / 信息密度 7
- 主题：浅色-only（词典 = 纸）。不做暗色模式

## 2. 色板与角色

| 角色 | 值 | 用途 |
|---|---|---|
| `--paper` | `#FAFAF8` | 页面底色（暖白，非纯白） |
| `--paper-raised` | `#FFFFFF` | 卡片、demo 舞台 |
| `--ink` | `#1C1917` | 主文字（stone-900，非纯黑） |
| `--ink-2` | `#57534E` | 次级文字（stone-600） |
| `--ink-3` | `#A8A29E` | 弱化文字、标本签（stone-400） |
| `--line` | `#E7E5E0` | 发丝边框（暖调） |
| `--line-strong` | `#D6D3CC` | hover 边框 |
| `--accent` | `#E0551F` | 唯一重音色：信号橙（链接、术语牌、选中态） |
| `--accent-soft` | `#FBEDE6` | 重音浅底（标签底、选中底） |
| `--stage` | `#F4F4F1` | demo 舞台底（与卡片微差，界定标本区） |

功能色仅在 demo 标本内部按被模仿系统如实使用（macOS 灰、iOS 蓝等），不参与站点主题。
阴影：染暖色调，`0 1px 2px rgba(28,25,23,.05)`，克制使用。

## 3. 排版规则

- 拉丁/数字展示：**Geist**（自托管可变字重 woff2，`assets/fonts/geist-vf.woff2`）
- 代码/术语/标本签：**Geist Mono**（自托管，`assets/fonts/geist-mono-vf.woff2`）
- 中文：系统栈 `-apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", sans-serif`
- 禁用斜体；强调用字重/颜色/下划线
- 层级靠字重 + 颜色 + 字号三件套，不靠无脑放大
- H1 `letter-spacing: -0.02em`；正文中文 ≥14px、行高 1.6–1.75；英文正文 15px/1.65
- 数字与 API 符号一律 Geist Mono / `tabular-nums`
- 中西文之间留盘古之白；中文用全角标点
- 标本签（specimen label）：Geist Mono 10–11px、大写、tracking 0.1em、`--ink-3` 或 `--accent`

## 4. 双语对照规则（本站核心）

- 三种阅读模式：`对照`（默认）/ `EN` / `中文`，`<html data-lang-mode="bilingual|en|zh">` 控制，
  localStorage 持久化；页眉切换器
- 对照模式下：英文在前，中文紧随其后，中文用 `--ink-2`、字号 −1 档，形成「原文 + 注」层次
- 术语名（entry name）永远保留英文原名，中文译名作为对照行
- API 符号、prompt 原文不翻译只对照：EN 原文 + 中文译文两段并列
- 长文本（prompt/debugPrompt）：EN 段落后接中文段落，左边框 2px `--accent` 标记可复制区

## 5. 组件样式

- **标本卡（首页网格）**：白底圆角 12px、`--line` 边框；上方 demo 舞台（`--stage` 底，高 200px，
  内容居中，pointer-events:none 整卡可点），下方名称（EN + 中文对照）、Geist Mono 术语牌
  （第一 API 符号、`--accent`）、tagline 双语。hover：边框 → `--line-strong`，无位移无阴影膨胀
- **术语牌（API chip）**：Geist Mono 11px、`--accent` 文字、无边框或 `--accent-soft` 底
- **平台标签**：Geist Mono 9–10px 大写 tracking 0.1em、`--ink-3`（web / macOS / new 用 `--accent`）
- **按钮**：圆角 8px；主按钮 `--accent` 底白字；次按钮白底 `--line` 边框。`:active scale(0.97)`
- **输入框**：白底 `--line` 边框，focus 时 2px `--accent` 外环（outline 不位移）
- **复制块**：`--stage` 底 + 圆角 10px + 等宽字体 + 右上角复制按钮，复制成功变「Copied / 已复制」
- **页眉**：纸底 90% 透明 + backdrop blur，下发丝边；左 wordmark「name that ui? / 界面叫啥」，
  右搜索入口、语言切换、指南链接
- **Anatomy 列表**：编号 + 部件名（EN 600 字重 + 中文对照）+ Geist Mono API + 描述双语
- **表格（翻译表/对比表）**：发丝横线分隔、无竖线、表头 Geist Mono 小号大写

## 6. 布局原则

- 容器 `max-width: 1120px` 居中，页边距 24px（移动端 16px）
- 首页标本网格：`repeat(auto-fill, minmax(300px, 1fr))`，gap 20px
- 详情页：单列 720px 阅读列宽，demo 舞台通栏（跟随容器）
- 分组用发丝线 + 留白，不滥用卡片嵌卡片
- 一个页面一个视觉焦点；留白服务层级

## 7. 深度层级

- z 轴极扁：页面 → sticky 页眉（blur + 发丝边）→ 弹层（词典定义 popover / 搜索面板）
- 弹层阴影：`0 4px 16px rgba(28,25,23,.08)` + `--line` 边框，圆角 12px

## 8. Do's / Don'ts

**Do**
- demo 标本内部可如实还原被模仿系统的外观（macOS 红绿灯、iOS 蓝开关……）
- 每个术语给一个「记忆点」呈现：解剖编号、对照 prompt、可点术语牌
- 所有交互元素：hover / active / focus-visible / disabled 状态齐全

**Don't**
- 紫蓝渐变、外发光、玻璃拟态滥用、纯黑 #000、Inter/Roboto、斜体
- 居中 Hero 大标题 + 三等分卡片横排的 AI 模板感
- 站点 chrome 动效喧宾夺主（demo 才是动画主角）
- 卡片套卡片、无意义阴影堆叠

## 9. 响应式行为

- ≥1024px：3 列网格；≥640px：2 列；<640px：1 列，demo 舞台高 180px
- 详情页 720px 列宽自适应；双语段落不并排（始终上下堆叠，窄屏友好）
- 页眉移动端折叠为 wordmark + 搜索 + 语言切换
- 禁 `h-screen`，用 `min-height: 100dvh`；flex 文本子项 `min-width: 0`

## 10. Motion 哲学

- 站点 chrome：hover 150ms、弹层 200ms、`:active scale(0.97)`；只动 transform/opacity
- 缓动：`cubic-bezier(0.23, 1, 0.32, 1)`（强化 ease-out）；禁 ease-in、禁 transition: all
- demo 标本动画是展品内容，不受 300ms 限制，但必须有 `prefers-reduced-motion` 兜底
- 列表入场不做 stagger 炫技；页面切换无转场
