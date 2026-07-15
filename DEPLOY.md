# LearnUI 部署进度（leanui.qiaomu.ai）

## 2026-07-15 部署记录

- [x] 本地构建：`python3 build.py` → `site/`（66 页，2.0MB，纯静态）
- [x] 本地验证：66 页无 JS 错误；搜索/筛选/语言切换/复制/翻译表过滤/灯箱交互通过；移动端无横向溢出
- [x] VPS 静态托管目录 + rsync 同步 → `/www/wwwroot/leanui.qiaomu.ai`（73 文件）
- [x] Nginx vhost `leanui.qiaomu.ai` → `/www/server/panel/vhost/nginx/leanui.qiaomu.ai.conf`
- [x] Cloudflare DNS A 记录 → 76.13.103.27（proxied=false）
- [x] TLS 证书 → `/etc/letsencrypt/live/leanui.qiaomu.ai/`（certbot webroot）
- [x] Umami 统计 → website ID `481306cd-4dad-4677-8456-f31490684e78`（真实 UA 写入验证通过；headless UA 被 umami 反机器人过滤属预期）
- [x] 低干扰署名（footer GitHub/乔木推荐/向阳乔木链接；不打赏/关注弹窗 —— 按 qiaomu-design 边界规则，用户未明确要求，只放页脚文字链接）
- [x] PWA：本轮跳过（静态词典站，离线缓存收益低），已记录
- [x] HTTPS + 内容验证（https://leanui.qiaomu.ai/ 200，http 301 跳转，umami script 加载，/api/send 200）
- [x] 服务器指南已登记 leanui.qiaomu.ai
