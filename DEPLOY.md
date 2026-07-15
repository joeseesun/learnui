# LearnUI 部署进度（learnui.qiaomu.ai）

## 2026-07-15 第三轮：语言自动探测 + 10 个原创新风格

- [x] 首开语言按浏览器探测：`navigator.languages` 含 zh → 纯中文模式，其他 → 纯英文（`<head>` 内联脚本防闪烁 + `assets/site.js` 同款 fallback；用户手动切换才写 localStorage；JS 禁用时回退双语）
- [x] 风格图鉴 14 → 24：原创增补 swiss-style、bauhaus、memphis、vaporwave、art-deco、cyberpunk、pixel-art、corporate-memphis、material-design、terminal-hacker（order 15–24，各含完整 EN+ZH 数据、交互标本、NEW 徽章）
- [x] 内容生产契约沉淀：`reference/STYLE_AUTHOR_BRIEF.md`（schema + 质量红线），10 个并行子代理按契约产出，合并时脚本校验段落配对/引用完整性
- [x] `data/styles-meta.json` 的「研究中」列表更新（Art Nouveau、Internet Ugly、Synthwave、Solarpunk、Maximalism）
- [x] 全量验证：91 页零 JS 错误、标本尺寸全部达标、移动端 390px 零溢出、搜索/语言切换/复制按钮交互通过

## 2026-07-15 第二轮：改名 + 风格图鉴 + PWA + 域名修正

- [x] 域名修正：`learnui.qiaomu.ai`（原 `leanui.qiaomu.ai` 拼写错误，已删除）
  - Cloudflare A 记录新建 `learnui.qiaomu.ai` → 76.13.103.27（proxied=false，id `569525a82001a7769f4e7d32577b64dc`）
  - 新 vhost `/www/server/panel/vhost/nginx/learnui.qiaomu.ai.conf`（含 `/sw.js`、`/manifest.webmanifest` 强制 no-cache 规则）
  - 新证书 `/etc/letsencrypt/live/learnui.qiaomu.ai/`（certbot webroot）
  - 静态根 `/www/wwwroot/learnui.qiaomu.ai`
  - Umami website `481306cd-4dad-4677-8456-f31490684e78` 直接 UPDATE domain（保留历史数据）
- [x] 网站改名 **Learn UI Name**（wordmark/title/feed/manifest 同步）
- [x] Name That Vibe 风格图鉴复刻：`/styles/` + 14 个风格详情页（DNA 信号、易混淆对比、代码起点、风格 brief）
- [x] PWA：manifest + 图标组（192/512/maskable/apple-touch-icon/favicon.svg）+ service worker（静态 cache-first，页面 network-first，离线回退首页；构建时注入版本号）
- [x] 设计重做：Vercel 式黑白（默认纯白，详见 DESIGN.md）
- [x] 搜索最佳实践：`/` 与 `⌘K` 聚焦、Esc 清空、80ms debounce、匹配 `<mark>` 高亮、命中别名时显示匹配理由、结果计数、`?q=`/`?platform=` 深链、空态示例词
- [x] a11y/性能：全局 focus-visible 蓝环、Geist 字体 preload、aria-live 结果区

## 2026-07-15 部署记录（第一轮，域名已废弃）

- [x] 本地构建：`python3 build.py` → `site/`（66 页，2.0MB，纯静态）
- [x] 本地验证：66 页无 JS 错误；搜索/筛选/语言切换/复制/翻译表过滤/灯箱交互通过；移动端无横向溢出
- [x] VPS 静态托管目录 + rsync 同步 → `/www/wwwroot/leanui.qiaomu.ai`（73 文件）
- [x] Nginx vhost `leanui.qiaomu.ai` → `/www/server/panel/vhost/nginx/leanui.qiaomu.ai.conf`
- [x] Cloudflare DNS A 记录 → 76.13.103.27（proxied=false）
- [x] TLS 证书 → `/etc/letsencrypt/live/leanui.qiaomu.ai/`（certbot webroot）
- [x] Umami 统计 → website ID `481306cd-4dad-4677-8456-f31490684e78`（真实 UA 写入验证通过；headless UA 被 umami 反机器人过滤属预期）
- [x] 低干扰署名（footer GitHub/乔木推荐/向阳乔木链接；不打赏/关注弹窗 —— 按 qiaomu-design 边界规则，用户未明确要求，只放页脚文字链接）
- [x] ~~PWA：本轮跳过~~ → 第二轮已实现
- [x] HTTPS + 内容验证（https://leanui.qiaomu.ai/ 200，http 301 跳转，umami script 加载，/api/send 200）
- [x] 服务器指南已登记 leanui.qiaomu.ai
