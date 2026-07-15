# Style Demo 实现契约（每个风格标本子代理必读）

你在为「Learn UI Name」（namethatui.com 的双语复刻站）实现**视觉风格标本**。
14 个风格共用同一台「迷你音乐播放器」，只有外观（皮肤）随风格变化 ——
这样对比页面里「同一应用、不同风格」的效果才成立。

## 输入

- 风格数据：`data/styles.json`，按 slug 找你的风格（signals/brief/tagline 是最准确的风格定义，照着它做）
- 通用契约：`reference/DEMO_CONTRACT.md`（作用域/自包含/字体/尺寸等硬性规则全部适用）
- 参考实现：`demos/switch-checkbox-radio.html`（看文件格式：根 `.demo demo-<slug>` + scoped `<style>` + 可选 IIFE `<script>`）

## 统一 DOM（结构、文案、类名不得更改；图标可换成 CSS/SVG 形状）

```html
<div class="demo demo-style-SLUG">
  <div class="player">
    <div class="art"></div>              <!-- 封面：用 CSS 画出符合风格的图案 -->
    <div class="meta">
      <div class="title">Midnight Drive</div>
      <div class="artist">Neon Coast</div>
    </div>
    <div class="progress">
      <div class="track"><div class="bar"></div></div>
      <div class="times"><span>1:12</span><span>3:48</span></div>
    </div>
    <div class="controls">
      <button class="cbtn prev" type="button" aria-label="Previous">…</button>
      <button class="cbtn play" type="button" aria-label="Play">…</button>
      <button class="cbtn next" type="button" aria-label="Next">…</button>
    </div>
    <div class="volume">
      <span class="vicon"></span>
      <div class="vtrack"><div class="vfill"></div></div>
    </div>
  </div>
</div>
```

可以：给容器加额外 class、在 `.art`/按钮内部塞 SVG、调整内部嵌套（如把按钮图标换成 SVG）。
不可以：改类名、改文案（Midnight Drive / Neon Coast / 1:12 / 3:48）、加外部资源。

## 交互（用 JS 做完整，细节风格化）

1. **play/pause**：点击切换播放态 —— 图标切换 + `.bar` 进度条从 31% 平滑走向 100%（约 30s），暂停保持
2. **prev/next**：进度归零重播
3. **volume**：点击 `.vtrack` 设置 `.vfill` 宽度（0–100%），初始 70%
4. JS 用 `document.currentScript.parentElement.querySelector(':scope > .demo')` 拿根节点，addEventListener
5. `@media (prefers-reduced-motion: reduce)` 下进度条瞬移不做动画

## 尺寸

- 播放器宽度 260–300px、整体高度 ≤ 340px（首页舞台 220px 高会缩放展示，详情舞台 400px）
- 根元素自适应，不溢出 100% 宽

## 风格准确度（最重要 —— 评审标准）

先读 `data/styles.json` 里你这个 slug 的 signals（defining 信号必须体现，avoid 信号绝不能出现）。
一般常识锚点（以 signals 为准）：

- **skeuomorphism**：iOS 6 质感 —— 拉丝金属、缝线皮革、真实高光阴影、拟物旋钮
- **neumorphism**：同底色软挤出（`#e0e5ec` 底 + 双侧浅/深阴影），低对比
- **glassmorphism**：彩色壁纸 + 半透明磨砂卡片（backdrop-filter blur + 半透白边）
- **liquid-glass**：Apple 2025 —— 玻璃只用于控制层（按钮/滑块浮在不透明内容上）、透镜感高光、胶囊形、同心圆角
- **web-brutalism**：裸 HTML 美学 —— Times 字体、纯蓝链接、默认边框、无圆角无阴影
- **neobrutalism**：粗黑描边 2-3px、硬偏移阴影（无模糊）、高饱和撞色、粗黑字
- **y2k**：千禧金属 —— 铬色渐变、镭射/全息、星芒、气泡、亮蓝紫
- **frutiger-aero**：2006–2013 光泽乐观主义 —— 水珠、散景光斑、极光渐变、玻璃光泽按钮、绿草/蓝天
- **flat-design**：Metro —— 纯色块、零渐变零阴影零圆角（或极小）、大胆纯色排版
- **minimalism**：大量留白、发丝线、黑白灰、细字重、无装饰
- **claymorphism**：黏土 —— 马卡龙色、超圆（20px+）、内阴影+外投影做出蓬松 3D
- **vernacular-web**：90 年代 GeoCities —— 平铺背景、GIF 感装饰、计数器、marquee、亮黄/品红
- **aqua**：Mac OS X —— 糖果条纹凝胶按钮（蓝/ graphite）、pinstripe 背景、水滴高光
- **windows-aero**：Vista/Win7 —— 半透明玻璃标题栏、极光、柔和辉光、细白边框

## 自验证（必做）

```bash
python3 scripts/preview-demo.py style-SLUG
# 截图输出到 /tmp/preview-style-SLUG.png，自己 Read 查看，迭代到「一眼认出是这个风格」为止
```

完成后报告：文件行数、实现了哪些 defining 信号、截图路径。
