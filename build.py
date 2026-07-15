#!/usr/bin/env python3
"""Learn UI Name static site builder — bilingual (EN/中文) replica of namethatui.com.
Stdlib only. Reads data/ + demos/, writes site/."""
import json, html, os, shutil, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://learnui.qiaomu.ai"
SITE_NAME = "Learn UI Name"
UMAMI_ID = "481306cd-4dad-4677-8456-f31490684e78"
NEW_SLUGS = {"text-scramble","spring","easing","masonry","bento-grid","hamburger-menu","lightbox","marquee"}

def load(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return json.load(f)

ENTRIES = load("data/entries.json")
UI = load("data/ui.json")
GUIDES = load("data/guides.json")
TABLE = load("data/translate-table.json")
ZH = {}
for i in range(1, 5):
    ZH.update(load(f"data/zh/entries-{i}.json"))
GUIDES_ZH = load("data/zh/guides.json")
TABLE_ZH = load("data/zh/translate-table-zh.json")

def load_or(p, default):
    full = os.path.join(ROOT, p)
    if not os.path.exists(full):
        return default
    return load(p)

def _nn(obj):
    """Recursively convert None to "" so partial/WIP data stays renderable."""
    if obj is None:
        return ""
    if isinstance(obj, dict):
        return {k: _nn(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_nn(v) for v in obj]
    return obj

STYLES = _nn(load_or("data/styles.json", []))
STYLES_META = _nn(load_or("data/styles-meta.json", {"hubTagline": "", "governedNote": "", "researching": []}))
STYLES_ZH = _nn(load_or("data/zh/styles.json", {}))
STYLES_META_ZH = _nn(load_or("data/zh/styles-meta-zh.json", {"hubTagline_zh": "", "governedNote_zh": ""}))
STYLE_BY_SLUG = {s["slug"]: s for s in STYLES}

OUT = os.path.join(ROOT, "site")

def esc(s):
    return html.escape(str(s), quote=True)

def t(key, **kw):
    """UI copy: returns (en, zh) with optional format params."""
    en, zh = UI[key], UI.get(key + "Zh", "")
    for k, v in kw.items():
        en = en.replace("{" + k + "}", str(v))
        zh = zh.replace("{" + k + "}", str(v))
    return en, zh

def bi(en, zh, tag="p", cls="", clsen="", clszh=""):
    """Bilingual block: EN line + ZH line."""
    if not zh:
        return f'<{tag} class="lang-en {cls} {clsen}">{esc(en)}</{tag}>'
    return (f'<{tag} class="lang-en {cls} {clsen}">{esc(en)}</{tag}>'
            f'<{tag} class="lang-zh {cls} {clszh}">{esc(zh)}</{tag}>')

def bi_raw(en_html, zh_html, tag="p", cls="", clsen="", clszh=""):
    """Bilingual block with pre-rendered HTML (already escaped)."""
    if not zh_html:
        return f'<{tag} class="lang-en {cls} {clsen}">{en_html}</{tag}>'
    return (f'<{tag} class="lang-en {cls} {clsen}">{en_html}</{tag}>'
            f'<{tag} class="lang-zh {cls} {clszh}">{zh_html}</{tag}>')

def paras(text_en, text_zh, cls):
    """Multi-paragraph bilingual text (split on blank lines)."""
    out = []
    ens = [p.strip() for p in (text_en or "").split("\n\n") if p.strip()]
    zhs = [p.strip() for p in (text_zh or "").split("\n\n") if p.strip()]
    for i, p in enumerate(ens):
        z = zhs[i] if i < len(zhs) else ""
        out.append(bi(p, z, "p", cls))
    return "".join(out)

def demo_fragment(slug):
    path = os.path.join(ROOT, "demos", slug + ".html")
    if not os.path.exists(path):
        return f'<div class="demo demo-missing" style="color:#a3a3a3;font:12px monospace">specimen pending: {esc(slug)}</div>'
    with open(path, encoding="utf-8") as f:
        return f.read()

def stage(slug, detail=False):
    cls = "stage stage-detail" if detail else "stage stage-card"
    pe = "" if detail else " pe-none"
    return (f'<div class="{cls}{pe}"><div class="stage-center">'
            f'<div class="fragment" data-slug="{esc(slug)}">{demo_fragment(slug)}</div>'
            f'</div></div>')

def header():
    en_all, zh_all = t("tabAll"); en_g, zh_g = t("guideCrumb"); en_st, zh_st = t("stylesCrumb")
    return f'''<header class="site-header">
 <div class="wrap header-in">
  <a class="wordmark" href="/">Learn UI Name<span class="wordmark-zh">界面叫啥</span></a>
  <nav class="site-nav">
   <a href="/#dictionary">Dictionary<span class="lang-zh nav-zh">词典</span></a>
   <a href="/styles/">{esc(en_st)}<span class="lang-zh nav-zh">{esc(zh_st)}</span></a>
   <a href="/#guides">{esc(en_g)}<span class="lang-zh nav-zh">{esc(zh_g)}</span></a>
   <a href="/guides/translate/">Translation<span class="lang-zh nav-zh">翻译表</span></a>
  </nav>
  <div class="lang-switch" role="group" aria-label="Language">
   <button type="button" data-mode="bilingual" class="ls-btn">对照</button>
   <button type="button" data-mode="en" class="ls-btn">EN</button>
   <button type="button" data-mode="zh" class="ls-btn">中文</button>
  </div>
 </div>
</header>'''

def footer():
    en, zh = t("footerNews"); en2, zh2 = t("footerRss"); en3, zh3 = t("builtNote")
    return f'''<footer class="site-footer">
 <div class="wrap footer-in">
  <p><span class="fw-500">Learn UI Name</span> · <span class="lang-en">{esc(UI["tagline"])}</span> <span class="lang-zh">{esc(UI["taglineZh"])}</span></p>
  <p class="foot-note">
   <span class="lang-en">{esc(en)} <a href="/feed.xml">{esc(en2)}</a></span>
   <span class="lang-zh">{esc(zh)} <a href="/feed.xml">{esc(zh2)}</a></span>
  </p>
  <p class="foot-links">
   <a href="https://github.com/joeseesun/learnui" rel="noopener">GitHub</a><span class="sep">·</span><a href="https://tuijian.qiaomu.ai/" rel="noopener">乔木推荐</a><span class="sep">·</span><span class="lang-en">Powered by <a href="https://qiaomu.ai/" rel="noopener">向阳乔木</a></span><span class="lang-zh">Powered by <a href="https://qiaomu.ai/" rel="noopener">向阳乔木</a></span>
  </p>
  <p class="foot-src">
   <span class="lang-en">{esc(en3)} <a href="https://namethatui.com/" rel="noopener">namethatui.com</a></span>
   <span class="lang-zh">{esc(zh3)} <a href="https://namethatui.com/" rel="noopener">namethatui.com</a></span>
  </p>
 </div>
</footer>
<div class="def-pop" id="def-pop" hidden>
 <div class="def-word" id="def-word"></div>
 <div class="def-body" id="def-body"></div>
 <div class="def-src" id="def-src"></div>
</div>'''

def page(title_en, title_zh, desc_en, desc_zh, body, path=""):
    url = SITE_URL + "/" + path
    return f'''<!DOCTYPE html>
<html lang="zh-CN" data-lang-mode="bilingual">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title_en)} · {esc(title_zh)} — {SITE_NAME}</title>
<meta name="description" content="{esc(desc_zh)} {esc(desc_en)}">
<link rel="canonical" href="{esc(url)}">
<meta property="og:title" content="{esc(title_en)} · {esc(title_zh)} — {SITE_NAME}">
<meta property="og:description" content="{esc(desc_zh)} {esc(desc_en)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{esc(url)}">
<meta name="theme-color" content="#ffffff">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="alternate" type="application/rss+xml" title="{SITE_NAME} RSS" href="/feed.xml">
<link rel="icon" href="/assets/icons/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/icons/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/geist-vf.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
<script defer src="https://umami.qiaomu.ai/script.js" data-website-id="{UMAMI_ID}" data-domains="learnui.qiaomu.ai"></script>
</head>
<body>
{body}
<script src="/assets/site.js"></script>
</body>
</html>'''

def entry_url(e):
    return f'/{e["platform"]}/{e["slug"]}/'

def card(e):
    z = ZH[e["slug"]]
    new = f'<span class="tag tag-new">{esc(UI["newBadge"])}</span>' if e["slug"] in NEW_SLUGS else ""
    sym = e["api"][0]["symbol"]
    return f'''<a class="card" data-platform="{e["platform"]}" data-slug="{e["slug"]}" href="{entry_url(e)}">
 {stage(e["slug"])}
 <div class="card-meta">
  <h3 class="card-name">
   <span class="lang-en">{esc(e["name"])}{new}</span>
   <span class="lang-zh card-name-zh">{esc(z["name_zh"])}</span>
   <span class="tag tag-platform">{esc(e["platform"])}</span>
  </h3>
  <p class="card-symbol">{esc(sym)}</p>
  {bi(e["tagline"], z["tagline_zh"], "p", "card-tag")}
 </div>
</a>'''

def homepage():
    search_index = []
    for e in ENTRIES:
        z = ZH[e["slug"]]
        search_index.append({
            "slug": e["slug"], "platform": e["platform"], "url": entry_url(e),
            "name": e["name"], "name_zh": z["name_zh"], "tagline": e["tagline"],
            "tagline_zh": z["tagline_zh"], "symbol": e["api"][0]["symbol"],
            "aka": e["aka"], "aka_zh": z["aka_zh"],
            "fuzzy": e["fuzzy"], "fuzzy_zh": z["fuzzy_zh"],
        })
    cards = "\n".join(card(e) for e in ENTRIES)
    g1, g2 = GUIDES["appkit-vs-swiftui"], GUIDES["swift-vs-electron"]
    en_cnt, zh_cnt = t("entriesCount", n=len(ENTRIES))
    en_ph, zh_ph = t("searchPlaceholder")
    en_s, zh_s = t("surprise")
    en_gt, zh_gt = t("guidesTitle")
    en_vp, zh_vp = t("vibePromo")
    body = f'''{header()}
<main class="wrap">
 <section class="hero">
  <h1 class="hero-title"><span class="lang-en">{esc(UI["heroTitle"])}</span><span class="lang-zh hero-title-zh">{esc(UI["heroTitleZh"])}</span></h1>
  {bi(UI["heroSub"], UI["heroSubZh"], "p", "hero-sub")}
  <p class="vibe-promo"><span class="tag tag-new">{esc(UI["newBadge"])}</span>
   <a class="lang-en" href="/styles/">{esc(en_vp)} →</a>
   <a class="lang-zh" href="/styles/">{esc(zh_vp)} →</a></p>
  <div class="controls">
   <div class="search-box">
    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
    <input id="search" type="search" autocomplete="off"
     data-ph-en="{esc(en_ph)}" data-ph-zh="{esc(zh_ph)}" placeholder="{esc(zh_ph)} / {esc(en_ph)}" aria-label="Search">
    <kbd class="search-kbd">/</kbd>
   </div>
   <button type="button" id="surprise" class="btn btn-ghost">⚂ <span class="lang-en">{esc(en_s)}</span><span class="lang-zh">{esc(zh_s)}</span></button>
   <div class="tabs" role="tablist">
    <button type="button" class="tab active" data-filter="all">All</button>
    <button type="button" class="tab" data-filter="web">Web</button>
    <button type="button" class="tab" data-filter="macos">macOS</button>
   </div>
   <p class="count-note" id="count-note"><span class="lang-en" data-tpl="{esc(UI["entriesCount"])}">{esc(en_cnt)}</span><span class="lang-zh" data-tpl="{esc(UI["entriesCountZh"])}">{esc(zh_cnt)}</span></p>
  </div>
 </section>
 <section id="dictionary" class="grid" aria-live="polite">
{cards}
 </section>
 <div id="no-result" class="no-result" hidden>
  <p><span class="lang-en">{esc(UI["searchNoResult"])}</span><span class="lang-zh">{esc(UI["searchNoResultZh"])}</span></p>
  <div class="no-result-examples">
   <button type="button" data-q="the dots menu">“the dots menu”</button>
   <button type="button" data-q="mac window buttons">“mac window buttons”</button>
   <button type="button" data-q="红绿灯">「红绿灯」</button>
   <button type="button" data-q="角落里弹出来的小消息">「角落里弹出来的小消息」</button>
  </div>
 </div>
 <section id="guides" class="guides">
  <h2 class="section-title"><span class="lang-en">{esc(en_gt)}</span><span class="lang-zh">{esc(zh_gt)}</span></h2>
  <div class="guide-grid">
   <a class="guide-card" href="/guides/appkit-vs-swiftui/">
    <span class="guide-kind">Guide</span>
    <span class="guide-title">{esc(g1["title"])}</span>
    {bi(UI["guide1Desc"], UI["guide1DescZh"], "span", "guide-desc")}
   </a>
   <a class="guide-card" href="/guides/swift-vs-electron/">
    <span class="guide-kind">Guide</span>
    <span class="guide-title">{esc(g2["title"])}</span>
    {bi(UI["guide2Desc"], UI["guide2DescZh"], "span", "guide-desc")}
   </a>
   <a class="guide-card" href="/guides/translate/">
    <span class="guide-kind">Guide</span>
    <span class="guide-title">{esc(UI["translateTitle"])}</span>
    {bi(UI["guide3Desc"], UI["guide3DescZh"], "span", "guide-desc")}
   </a>
  </div>
 </section>
</main>
{footer()}
<script id="search-index" type="application/json">{json.dumps(search_index, ensure_ascii=False).replace("</", "<\\/")}</script>'''
    return page(UI["heroTitle"], UI["heroTitleZh"], UI["heroSub"], UI["heroSubZh"], body)

def api_table(e, z):
    en_f, zh_f = t("framework"); en_s, zh_s = t("symbol"); en_n, zh_n = t("note")
    rows = []
    for i, a in enumerate(e["api"]):
        note_en = a.get("note", "")
        note_zh = z["api_notes_zh"][i] if i < len(z["api_notes_zh"]) else None
        note = ""
        if note_en:
            note = f'<span class="lang-en">{esc(note_en)}</span><span class="lang-zh zh-line">{esc(note_zh or "")}</span>'
        rows.append(f'''<tr>
 <td class="mono fw">{esc(a["framework"])}</td>
 <td class="mono sym">{esc(a["symbol"])}</td>
 <td class="note">{note}</td>
</tr>''')
    return f'''<div class="table-scroll"><table class="api-table">
<thead><tr><th>{esc(en_f)}<span class="lang-zh th-zh">{esc(zh_f)}</span></th><th>{esc(en_s)}<span class="lang-zh th-zh">{esc(zh_s)}</span></th><th>{esc(en_n)}<span class="lang-zh th-zh">{esc(zh_n)}</span></th></tr></thead>
<tbody>{"".join(rows)}</tbody>
</table></div>'''

def copy_block(text_en, text_zh, block_id):
    en_c, zh_c = t("copy"); en_cd, zh_cd = t("copied")
    return f'''<div class="copy-block" data-copy-target="{block_id}">
 <button type="button" class="btn btn-copy" data-copy="{block_id}" data-label-en="{esc(en_c)}" data-label-zh="{esc(zh_c)}" data-done-en="{esc(en_cd)}" data-done-zh="{esc(zh_cd)}"><span class="lang-en">{esc(en_c)}</span><span class="lang-zh">{esc(zh_c)}</span></button>
 <div class="copy-text">
  <p class="lang-en" id="{block_id}">{esc(text_en)}</p>
  <p class="lang-zh zh-copy">{esc(text_zh)}</p>
 </div>
</div>'''

def entry_page(e):
    z = ZH[e["slug"]]
    en_b, zh_b = t("indexCrumb")
    plat_label = "Web" if e["platform"] == "web" else "macOS"
    new = f'<span class="tag tag-new">{esc(UI["newBadge"])}</span>' if e["slug"] in NEW_SLUGS else ""
    aka_en = ", ".join(e["aka"]); aka_zh = "、".join(z["aka_zh"])
    fuzzy_rows = "".join(
        f'<li><span class="lang-en">“{esc(f)}”</span><span class="lang-zh zh-line">「{esc(z["fuzzy_zh"][i])}」</span></li>'
        for i, f in enumerate(e["fuzzy"]))
    parts = []
    en_pf, zh_pf = t("promptFragment")
    for i, p in enumerate(e.get("parts", [])):
        pz = z["parts_zh"].get(p["id"], {})
        parts.append(f'''<li class="part">
 <div class="part-head">
  <span class="part-num">{i+1}</span>
  <span class="part-name"><span class="lang-en">{esc(p["name"])}</span><span class="lang-zh part-name-zh">{esc(pz.get("name_zh",""))}</span></span>
  <code class="part-api">{esc(p["api"])}</code>
 </div>
 {bi(p["description"], pz.get("description_zh",""), "p", "part-desc")}
 <div class="part-prompt">
  <span class="part-prompt-label"><span class="lang-en">{esc(en_pf)}</span><span class="lang-zh">{esc(zh_pf)}</span></span>
  <p class="lang-en mono-sm">{esc(p["prompt"])}</p>
  <p class="lang-zh mono-sm">{esc(pz.get("prompt_zh",""))}</p>
 </div>
</li>''')
    anatomy = ""
    if parts:
        en_a, zh_a = t("anatomy")
        anatomy = f'''<section class="sect">
 <h2 class="section-title"><span class="lang-en">{esc(en_a)}</span><span class="lang-zh">{esc(zh_a)}</span></h2>
 <ol class="parts">{"".join(parts)}</ol>
</section>'''
    related = []
    by_slug = {x["slug"]: x for x in ENTRIES}
    for r in e.get("related", []):
        if r in by_slug:
            re_ = by_slug[r]
            rz = ZH[r]
            related.append(f'''<a class="rel-card" href="{entry_url(re_)}">
 <span class="rel-name"><span class="lang-en">{esc(re_["name"])}</span><span class="lang-zh rel-name-zh">{esc(rz["name_zh"])}</span></span>
 <span class="rel-sym">{esc(re_["api"][0]["symbol"])}</span>
</a>''')
    see_also = ""
    if related:
        en_sa, zh_sa = t("seeAlso")
        see_also = f'''<section class="sect">
 <h2 class="section-title"><span class="lang-en">{esc(en_sa)}</span><span class="lang-zh">{esc(zh_sa)}</span></h2>
 <div class="rel-grid">{"".join(related)}</div>
</section>'''
    en_p, zh_p = t("promptSection"); en_d, zh_d = t("debugSection")
    en_ic, zh_ic = t("inCode"); en_ac, zh_ac = t("alsoCalled"); en_fy, zh_fy = t("ifYouCalledIt")
    en_cp, zh_cp = t("copyPage"); en_cd, zh_cd = t("copied")
    md = entry_markdown(e, z)
    body = f'''{header()}
<main class="wrap entry">
 <nav class="crumbs">
  <a href="/">{esc(en_b)}<span class="lang-zh">{esc(zh_b)}</span></a>
  <span class="crumb-sep">/</span>
  <a href="/?platform={e["platform"]}#dictionary">{plat_label}</a>
  <span class="crumb-sep">/</span>
  <span class="crumb-cur">{esc(e["name"])}</span>
 </nav>
 <header class="entry-head">
  <h1 class="entry-title">
   <span class="lang-en">{esc(e["name"])} {new}</span>
   <span class="lang-zh entry-title-zh">{esc(z["name_zh"])}</span>
   <span class="tag tag-platform">{esc(e["platform"])}</span>
  </h1>
  {bi(e["tagline"], z["tagline_zh"], "p", "entry-tag")}
  <dl class="entry-meta">
   <div class="meta-row"><dt>{esc(en_ac)}<span class="lang-zh dt-zh">{esc(zh_ac)}</span></dt>
    <dd><span class="lang-en">{esc(aka_en)}</span><span class="lang-zh zh-line">{esc(aka_zh)}</span></dd></div>
   <div class="meta-row"><dt>{esc(en_fy)}<span class="lang-zh dt-zh">{esc(zh_fy)}</span></dt>
    <dd><ul class="fuzzy-list">{fuzzy_rows}</ul></dd></div>
  </dl>
 </header>
 {stage(e["slug"], detail=True)}
 <p class="stage-hint lang-zh">标本可交互 —— 点点看。Specimen is live — try it.</p>
 {anatomy}
 <section class="sect">
  <h2 class="section-title"><span class="lang-en">{esc(en_p)}</span><span class="lang-zh">{esc(zh_p)}</span></h2>
  {copy_block(e["prompt"], z["prompt_zh"], "prompt-main")}
 </section>
 <section class="sect">
  <h2 class="section-title"><span class="lang-en">{esc(en_d)}</span><span class="lang-zh">{esc(zh_d)}</span></h2>
  {copy_block(e["debugPrompt"], z["debugPrompt_zh"], "prompt-debug")}
 </section>
 <section class="sect">
  <h2 class="section-title"><span class="lang-en">{esc(en_ic)}</span><span class="lang-zh">{esc(zh_ic)}</span></h2>
  {api_table(e, z)}
 </section>
 {see_also}
 <section class="sect">
  <button type="button" class="btn btn-ghost" id="copy-md" data-done-en="{esc(en_cd)}" data-done-zh="{esc(zh_cd)}">⧉ <span class="lang-en">{esc(en_cp)}</span><span class="lang-zh">{esc(zh_cp)}</span></button>
  <template id="md-source">{esc(md)}</template>
 </section>
</main>
{footer()}'''
    return page(e["name"], z["name_zh"], e["tagline"], z["tagline_zh"], body, f'{e["platform"]}/{e["slug"]}/')

def entry_markdown(e, z):
    lines = [f"# {e['name']} · {z['name_zh']}", "",
        f"UI reference — {SITE_URL}/{e['platform']}/{e['slug']}/", "",
        f"**{e['tagline']}**", z["tagline_zh"], "",
        f"**Also called / 也叫:** {', '.join(e['aka'])} / {'、'.join(z['aka_zh'])}", ""]
    if e.get("parts"):
        lines += ["## Anatomy — every part, named / 解剖", ""]
        for i, p in enumerate(e["parts"]):
            pz = z["parts_zh"].get(p["id"], {})
            lines += [f"{i+1}. **{p['name']} · {pz.get('name_zh','')}** (`{p['api']}`)",
                      f"   {p['description']}", f"   {pz.get('description_zh','')}",
                      f"   Prompt fragment: {p['prompt']}", ""]
    lines += ["## Prompt / 提示词", "", e["prompt"], "", z["prompt_zh"], "",
              "## Debug prompt / 调试提示词", "", e["debugPrompt"], "", z["debugPrompt_zh"], "",
              "## In code / 代码里叫什么", ""]
    for i, a in enumerate(e["api"]):
        note = a.get("note", "")
        nz = z["api_notes_zh"][i] or "" if i < len(z["api_notes_zh"]) else ""
        line = f"- **{a['framework']}** `{a['symbol']}`"
        if note:
            line += f" — {note} / {nz}"
        lines.append(line)
    return "\n".join(lines)

def guide_page(slug):
    g = GUIDES[slug]
    gz = GUIDES_ZH[slug]
    en_b, zh_b = t("indexCrumb"); en_g, zh_g = t("guideCrumb")
    inner = []
    if slug == "appkit-vs-swiftui":
        eq = g["equation"]
        inner.append(f'''<div class="equation">
 <span class="eq-side"><code>{esc(eq["left"])}</code><span class="eq-tag">{esc(eq["leftTag"])}</span></span>
 <span class="eq-op">=</span>
 <span class="eq-side"><code>{esc(eq["right"])}</code><span class="eq-tag">{esc(eq["rightTag"])}</span></span>
</div>''')
    for i, para in enumerate(g["intro"]):
        inner.append(bi(para, gz["intro_zh"][i], "p", "guide-para"))
    if "rules" in g:
        rows = "".join(f'''<li class="rule"><span class="rule-num">{i+1}</span>
 <div>{bi(r["title"], gz["rules_zh"][i]["title_zh"], "p", "rule-title")}{bi(r["body"], gz["rules_zh"][i]["body_zh"], "p", "rule-body")}</div>
</li>''' for i, r in enumerate(g["rules"]))
        inner.append(f'''<section class="sect"><h2 class="section-title"><span class="lang-en">{esc(g["rulesTitle"])}</span><span class="lang-zh">{esc(gz["rulesTitle_zh"])}</span></h2>
<ol class="rules">{rows}</ol></section>''')
    if "table" in g:
        rows = "".join(f'''<tr><td class="fw"><span class="lang-en">{esc(r["aspect"])}</span><span class="lang-zh zh-line">{esc(gz["table_zh"][i]["aspect_zh"])}</span></td>
<td><span class="lang-en">{esc(r["swift"])}</span><span class="lang-zh zh-line">{esc(gz["table_zh"][i]["swift_zh"])}</span></td>
<td><span class="lang-en">{esc(r["electron"])}</span><span class="lang-zh zh-line">{esc(gz["table_zh"][i]["electron_zh"])}</span></td></tr>''' for i, r in enumerate(g["table"]))
        inner.append(f'''<section class="sect"><h2 class="section-title"><span class="lang-en">{esc(g["tableTitle"])}</span><span class="lang-zh">{esc(gz["tableTitle_zh"])}</span></h2>
<table class="api-table vs-table"><thead><tr><th></th><th>Swift (native)</th><th>Electron (web shell)</th></tr></thead><tbody>{rows}</tbody></table></section>''')
    if "rule" in g:
        inner.append(f'''<section class="sect"><h2 class="section-title"><span class="lang-en">{esc(g["ruleTitle"])}</span><span class="lang-zh">{esc(gz["ruleTitle_zh"])}</span></h2>
{bi(g["rule"], gz["rule_zh"], "p", "guide-para")}</section>''')
    if "promptsIntro" in g:
        inner.append(bi(g["promptsIntro"], gz["promptsIntro_zh"], "p", "guide-para"))
    prompts = []
    for i, p in enumerate(g["prompts"]):
        pz = gz["prompts_zh"][i]
        note = f'<span class="prompt-note">· {esc(p.get("note",""))}<span class="lang-zh"> · {esc(pz.get("note_zh",""))}</span></span>' if p.get("note") else ""
        prompts.append(f'''<div class="guide-prompt">
 <p class="prompt-label"><span class="lang-en">{esc(p["label"])}</span><span class="lang-zh">{esc(pz["label_zh"])}</span>{note}</p>
 {copy_block(p["text"], pz["text_zh"], f"g-{slug}-{i}")}
</div>''')
    inner.append(f'''<section class="sect"><h2 class="section-title"><span class="lang-en">{esc(g["promptsTitle"])}</span><span class="lang-zh">{esc(gz["promptsTitle_zh"])}</span></h2>
{"".join(prompts)}</section>''')
    conf = "".join(f'''<li class="confuse"><span class="confuse-term"><span class="lang-en">{esc(c["term"])}</span><span class="lang-zh zh-line">{esc(gz["confuse_zh"][i]["term_zh"])}</span></span>
{bi(c["body"], gz["confuse_zh"][i]["body_zh"], "p", "confuse-body")}</li>''' for i, c in enumerate(g["confuse"]))
    inner.append(f'''<section class="sect"><h2 class="section-title"><span class="lang-en">{esc(g["confuseTitle"])}</span><span class="lang-zh">{esc(gz["confuseTitle_zh"])}</span></h2>
<ul class="confuse-list">{conf}</ul></section>''')
    if "faq" in g:
        faq = "".join(f'''<details class="faq">
 <summary><span class="lang-en">{esc(q["q"])}</span><span class="lang-zh zh-line">{esc(gz["faq_zh"][i]["q_zh"])}</span></summary>
 {bi(q["a"], gz["faq_zh"][i]["a_zh"], "p", "faq-a")}
</details>''' for i, q in enumerate(g["faq"]))
        inner.append(f'''<section class="sect"><h2 class="section-title"><span class="lang-en">{esc(g["faqTitle"])}</span><span class="lang-zh">{esc(gz["faqTitle_zh"])}</span></h2>
{faq}</section>''')
    inner.append(bi(g["outro"], gz["outro_zh"], "p", "guide-outro"))
    body = f'''{header()}
<main class="wrap entry guide">
 <nav class="crumbs">
  <a href="/">{esc(en_b)}<span class="lang-zh">{esc(zh_b)}</span></a>
  <span class="crumb-sep">/</span>
  <span>{esc(en_g)}<span class="lang-zh">{esc(zh_g)}</span></span>
  <span class="crumb-sep">/</span>
  <span class="crumb-cur">{esc(g["title"])}</span>
 </nav>
 <header class="entry-head">
  <h1 class="entry-title"><span class="lang-en">{esc(g["title"])}</span><span class="lang-zh entry-title-zh">{esc(gz["title_zh"])}</span></h1>
  <p class="guide-sub mono-sm">/ {esc(g["subtitle"])} /</p>
  {bi(g["lede"], gz["lede_zh"], "p", "entry-tag")}
 </header>
 {"".join(inner)}
</main>
{footer()}'''
    return page(g["title"], gz["title_zh"], g["lede"], gz["lede_zh"], body, f"guides/{slug}/")

def translate_page():
    en_b, zh_b = t("indexCrumb"); en_g, zh_g = t("guideCrumb")
    en_tc, zh_tc = t("thingCol")
    linkable = {"Alert": "alert", "Color well / color picker": "color-well", "Context menu": "context-menu",
                "Level indicator": "level-indicator", "Gauge / level indicator": "level-indicator",
                "Menu bar extra / status item": "menu-bar-extra", "Popover": "popover",
                "Pull-down button": "popup-pulldown-combo", "Pop-up button": "popup-pulldown-combo",
                "Save/export panel": "save-panel", "Search field": "search-field",
                "Segmented control": "segmented-control", "Sheet": "sheet", "Sidebar": "sidebar",
                "Slider": "slider", "Stepper": "stepper", "Switch": "switch-checkbox-radio",
                "Toolbar": "toolbar", "Outline / source list": "outline-view", "List": "outline-view"}
    rows = []
    for i, r in enumerate(TABLE):
        zh = TABLE_ZH[i]["thing_zh"]
        note_en = r.get("note", "")
        thing_html = esc(r["thing"])
        slug = linkable.get(r["thing"])
        if slug:
            plat = "macos"
            thing_html = f'<a class="thing-link" href="/{plat}/{slug}/">{esc(r["thing"])}</a>'
        note = f'<span class="table-note">{esc(note_en)}</span>' if note_en else ""
        rows.append(f'''<tr data-search="{esc((r["thing"] + " " + zh + " " + r["appkit"] + " " + r["swiftui"]).lower())}">
 <td class="fw">{thing_html}<span class="lang-zh zh-line">{esc(zh)}</span>{note}</td>
 <td class="mono">{esc(r["appkit"])}</td>
 <td class="mono">{esc(r["swiftui"])}</td>
</tr>''')
    en_cnt, zh_cnt = t("translateCount", n=len(TABLE), total=len(TABLE))
    body = f'''{header()}
<main class="wrap entry">
 <nav class="crumbs">
  <a href="/">{esc(en_b)}<span class="lang-zh">{esc(zh_b)}</span></a>
  <span class="crumb-sep">/</span>
  <span>{esc(en_g)}<span class="lang-zh">{esc(zh_g)}</span></span>
  <span class="crumb-sep">/</span>
  <span class="crumb-cur">{esc(UI["translateTitle"])}</span>
 </nav>
 <header class="entry-head">
  <h1 class="entry-title"><span class="lang-en">{esc(UI["translateTitle"])}</span><span class="lang-zh entry-title-zh">翻译对照表</span></h1>
  <p class="guide-sub mono-sm">/ {esc(UI["translateSubtitle"])} /</p>
  {bi(UI["translateLede"], UI["translateLedeZh"], "p", "entry-tag")}
 </header>
 <div class="search-box table-search">
  <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
  <input id="table-search" type="search" autocomplete="off" placeholder="Filter… / 筛选…" aria-label="Filter">
 </div>
 <div class="table-scroll"><table class="api-table translate-table" id="translate-table">
  <thead><tr><th>{esc(en_tc)}<span class="lang-zh th-zh">{esc(zh_tc)}</span></th><th>AppKit</th><th>SwiftUI</th></tr></thead>
  <tbody>{"".join(rows)}</tbody>
 </table></div>
 <p class="count-note"><span class="lang-en" id="table-count" data-tpl="{esc(UI["translateCount"])}">{esc(en_cnt)}</span><span class="lang-zh" id="table-count-zh" data-tpl="{esc(UI["translateCountZh"])}">{esc(zh_cnt)}</span></p>
</main>
{footer()}'''
    return page(UI["translateTitle"], "翻译对照表", UI["translateLede"], UI["translateLedeZh"], body, "guides/translate/")

# ---------------- styles atlas (Name That Vibe) ----------------

def style_url(s):
    return f'/styles/{s["slug"]}/'

def style_zh(s):
    return STYLES_ZH.get(s["slug"], {})

def first_para(text):
    return (text or "").split("\n\n")[0].strip()

def style_card(s):
    z = style_zh(s)
    hay = " ".join([s.get("name") or "", z.get("name_zh") or "", s.get("tagline") or "", z.get("tagline_zh") or ""] +
                   (s.get("aliases") or []) + (z.get("aliases_zh") or [])).lower()
    return f'''<a class="style-card" data-search="{esc(hay)}" href="{style_url(s)}">
 {stage("style-" + s["slug"])}
 <div class="card-meta">
  <h3 class="card-name">
   <span class="lang-en">{esc(s["name"])}</span>
   <span class="lang-zh card-name-zh">{esc(z.get("name_zh", ""))}</span>
  </h3>
  {bi(first_para(s.get("tagline", "")), first_para(z.get("tagline_zh", "")), "p", "card-tag")}
 </div>
</a>'''

def styles_hub_page():
    en_b, zh_b = t("indexCrumb"); en_sc, zh_sc = t("stylesCrumb")
    en_cnt, zh_cnt = t("stylesCount", n=len(STYLES))
    en_ph, zh_ph = t("searchStylesPlaceholder")
    en_gv, zh_gv = t("governedTitle"); en_rs, zh_rs = t("researchingLabel")
    cards = "\n".join(style_card(s) for s in STYLES)
    chips = "".join(f"<span>{esc(n)}</span>" for n in STYLES_META.get("researching", []))
    body = f'''{header()}
<main class="wrap">
 <nav class="crumbs">
  <a href="/">{esc(en_b)}<span class="lang-zh">{esc(zh_b)}</span></a>
  <span class="crumb-sep">/</span>
  <span class="crumb-cur">{esc(en_sc)}<span class="lang-zh">{esc(zh_sc)}</span></span>
 </nav>
 <section class="hero" style="padding-top:32px">
  <h1 class="hero-title" style="font-size:clamp(32px,4.6vw,48px)"><span class="lang-en">{esc(UI["stylesTitle"])}</span><span class="lang-zh hero-title-zh">{esc(UI["stylesTitleZh"])}</span></h1>
  {paras(STYLES_META.get("hubTagline", ""), STYLES_META_ZH.get("hubTagline_zh", ""), "hero-sub")}
  <div class="atlas-note">
   <h2><span class="lang-en">{esc(en_gv)}</span> <span class="lang-zh" style="font-weight:400;font-size:12.5px">{esc(zh_gv)}</span></h2>
   {paras(STYLES_META.get("governedNote", ""), STYLES_META_ZH.get("governedNote_zh", ""), "")}
   <div class="research-chips">{chips}</div>
  </div>
  <div class="controls">
   <div class="search-box">
    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
    <input id="style-search" type="search" autocomplete="off"
     data-ph-en="{esc(en_ph)}" data-ph-zh="{esc(zh_ph)}" placeholder="{esc(zh_ph)} / {esc(en_ph)}" aria-label="Search styles">
    <kbd class="search-kbd">/</kbd>
   </div>
   <p class="count-note" id="style-count"><span class="lang-en" data-tpl="{esc(UI["stylesCount"])}">{esc(en_cnt)}</span><span class="lang-zh" data-tpl="{esc(UI["stylesCountZh"])}">{esc(zh_cnt)}</span></p>
  </div>
 </section>
 <section class="style-grid" id="styles" aria-live="polite">
{cards}
 </section>
 <p id="style-no-result" class="no-result" hidden><span class="lang-en">{esc(UI["searchNoResult"])}</span><span class="lang-zh">{esc(UI["searchNoResultZh"])}</span></p>
</main>
{footer()}'''
    return page(UI["stylesTitle"], UI["stylesTitleZh"], STYLES_META.get("hubTagline", "")[:150],
                STYLES_META_ZH.get("hubTagline_zh", "")[:80], body, "styles/")

def style_page(s):
    z = style_zh(s)
    en_b, zh_b = t("indexCrumb"); en_sc, zh_sc = t("stylesCrumb")
    en_fy, zh_fy = t("ifYouCalledIt")
    en_dna, zh_dna = t("dnaTitle"); en_cf, zh_cf = t("confusedTitle")
    en_ic, zh_ic = t("styleCodeTitle"); en_br, zh_br = t("briefTitle")
    en_a11y, zh_a11y = t("a11yTitle"); en_or, zh_or = t("originTitle")
    en_sa, zh_sa = t("seeAlso"); en_cp, zh_cp = t("copyPage"); en_cd, zh_cd = t("copied")

    aliases = ""
    if s.get("aliases"):
        chips = []
        for i, a in enumerate(s["aliases"]):
            az = z.get("aliases_zh", [])
            ztxt = az[i] if i < len(az) else ""
            chips.append(f'''<span class="alias-chip"><span class="lang-en">“{esc(a)}”</span><span class="lang-zh">「{esc(ztxt)}」</span></span>''')
        aliases = f'''<section class="sect">
 <h2 class="section-title"><span class="lang-en">{esc(en_fy)}</span><span class="lang-zh">{esc(zh_fy)}</span></h2>
 <div class="alias-chips">{"".join(chips)}</div>
</section>'''

    dna = ""
    if s.get("signals"):
        items = []
        role_keys = {"defining": ("roleDefining",), "supporting": ("roleSupporting",),
                     "variable": ("roleVariable",), "avoid": ("roleAvoid",)}
        for sig in s["signals"]:
            sz = z.get("signals_zh", {}).get(sig["id"], {})
            rk = role_keys.get(sig["role"], ("roleSupporting",))[0]
            en_r, zh_r = t(rk)
            items.append(f'''<li class="dna-item">
 <div class="dna-head">
  <span class="dna-name"><span class="lang-en">{esc(sig["name"])}</span><span class="lang-zh dna-name-zh">{esc(sz.get("name_zh", ""))}</span></span>
  <span class="dna-facet">{esc(sig["facet"])}</span>
  <span class="dna-role dna-role-{esc(sig["role"])}"><span class="lang-en">{esc(en_r)}</span><span class="lang-zh">{esc(zh_r)}</span></span>
 </div>
 {bi(sig["description"], sz.get("description_zh", ""), "p", "dna-desc")}
</li>''')
        dna = f'''<section class="sect" style="max-width:none">
 <h2 class="section-title"><span class="lang-en">{esc(en_dna)}</span><span class="lang-zh">{esc(zh_dna)}</span></h2>
 <ol class="dna">{"".join(items)}</ol>
</section>'''

    confused = ""
    cw = s.get("confusedWith")
    if cw and cw.get("slug") in STYLE_BY_SLUG:
        other = STYLE_BY_SLUG[cw["slug"]]
        oz = style_zh(other)
        other_demo = "style-" + other["slug"]
        pair = ""
        if os.path.exists(os.path.join(ROOT, "demos", other_demo + ".html")):
            pair = f'''<div class="vs-pair">
 <div class="vs-cell">{stage("style-" + s["slug"])}<p class="vs-cell-label"><span class="lang-en">{esc(s["name"])}</span><span class="lang-zh">{esc(z.get("name_zh", ""))}</span></p></div>
 <div class="vs-cell">{stage(other_demo)}<p class="vs-cell-label"><span class="lang-en">{esc(other["name"])}</span><span class="lang-zh">{esc(oz.get("name_zh", ""))}</span></p></div>
</div>'''
        czw = z.get("confused_zh", {})
        confused = f'''<section class="sect" style="max-width:none">
 <h2 class="section-title"><span class="lang-en">{esc(en_cf)}: {esc(cw["name"])}</span><span class="lang-zh">{esc(zh_cf)}：{esc(oz.get("name_zh", cw["name"]))}</span></h2>
 {pair}
 <div class="vs-why">
  <div class="vs-why-card">{bi(cw.get("because", ""), czw.get("because_zh", ""), "p")}</div>
  <div class="vs-why-card">{bi(cw.get("wouldBecomeIf", ""), czw.get("wouldBecomeIf_zh", ""), "p")}</div>
 </div>
</section>'''

    code_sect = ""
    if s.get("code"):
        blocks = []
        for i, c in enumerate(s["code"]):
            title = f'<p class="code-title">{esc(c["title"])}</p>' if c.get("title") else ""
            blocks.append(f'''<div class="code-block">
 <button type="button" class="btn btn-copy" data-copy="code-{s["slug"]}-{i}" data-done-en="{esc(en_cd)}" data-done-zh="{esc(zh_cd)}"><span class="lang-en">{esc(t("copy")[0])}</span><span class="lang-zh">{esc(t("copy")[1])}</span></button>
 {title}
 <pre><code id="code-{s["slug"]}-{i}">{esc(c["code"])}</code></pre>
</div>''')
        code_sect = f'''<section class="sect">
 <h2 class="section-title"><span class="lang-en">{esc(en_ic)}</span><span class="lang-zh">{esc(zh_ic)}</span></h2>
 {"".join(blocks)}
</section>'''

    brief = ""
    if s.get("brief"):
        brief = f'''<section class="sect">
 <h2 class="section-title"><span class="lang-en">{esc(en_br)}</span><span class="lang-zh">{esc(zh_br)}</span></h2>
 {copy_block(s["brief"], z.get("brief_zh", ""), "brief-" + s["slug"])}
</section>'''

    a11y = ""
    if s.get("accessibility"):
        a11y = f'''<section class="sect">
 <h2 class="section-title"><span class="lang-en">{esc(en_a11y)}</span><span class="lang-zh">{esc(zh_a11y)}</span></h2>
 {paras(s["accessibility"], z.get("accessibility_zh", ""), "guide-para")}
</section>'''

    origin = ""
    if s.get("origin"):
        origin = f'''<section class="sect">
 <h2 class="section-title"><span class="lang-en">{esc(en_or)}</span><span class="lang-zh">{esc(zh_or)}</span></h2>
 {paras(s["origin"], z.get("origin_zh", ""), "guide-para")}
</section>'''

    see_also = ""
    if s.get("seeAlso"):
        cards = []
        for sa in s["seeAlso"]:
            ref = (sa.get("slug") or "")
            if ref.startswith("styles/"):
                ref = ref[len("styles/"):]
            if ref in STYLE_BY_SLUG:
                so = STYLE_BY_SLUG[ref]
                soz = style_zh(so)
                cards.append(f'''<a class="rel-card" href="{style_url(so)}">
 <span class="rel-name"><span class="lang-en">{esc(so["name"])}</span><span class="lang-zh rel-name-zh">{esc(soz.get("name_zh", ""))}</span></span>
</a>''')
            else:
                ent = next((x for x in ENTRIES if x["slug"] == ref), None)
                if ent:
                    ez = ZH[ent["slug"]]
                    cards.append(f'''<a class="rel-card" href="{entry_url(ent)}">
 <span class="rel-name"><span class="lang-en">{esc(ent["name"])}</span><span class="lang-zh rel-name-zh">{esc(ez["name_zh"])}</span></span>
 <span class="rel-sym">{esc(ent["api"][0]["symbol"])}</span>
</a>''')
        if cards:
            see_also = f'''<section class="sect">
 <h2 class="section-title"><span class="lang-en">{esc(en_sa)}</span><span class="lang-zh">{esc(zh_sa)}</span></h2>
 <div class="rel-grid">{"".join(cards)}</div>
</section>'''

    scope = ""
    if s.get("scope"):
        scope = paras(s["scope"], z.get("scope_zh", ""), "guide-para")

    md = style_markdown(s, z)
    body = f'''{header()}
<main class="wrap entry">
 <nav class="crumbs">
  <a href="/">{esc(en_b)}<span class="lang-zh">{esc(zh_b)}</span></a>
  <span class="crumb-sep">/</span>
  <a href="/styles/">{esc(en_sc)}<span class="lang-zh">{esc(zh_sc)}</span></a>
  <span class="crumb-sep">/</span>
  <span class="crumb-cur">{esc(s["name"])}</span>
 </nav>
 <header class="entry-head">
  <h1 class="entry-title">
   <span class="lang-en">{esc(s["name"])}</span>
   <span class="lang-zh entry-title-zh">{esc(z.get("name_zh", ""))}</span>
  </h1>
  {paras(s.get("tagline", ""), z.get("tagline_zh", ""), "entry-tag")}
  {scope}
 </header>
 {stage("style-" + s["slug"], detail=True)}
 <p class="stage-hint lang-zh">标本可交互 —— 点点看。Specimen is live — try it.</p>
 {aliases}
 {dna}
 {confused}
 {code_sect}
 {brief}
 {a11y}
 {origin}
 {see_also}
 <section class="sect">
  <button type="button" class="btn btn-ghost" id="copy-md" data-done-en="{esc(en_cd)}" data-done-zh="{esc(zh_cd)}">⧉ <span class="lang-en">{esc(en_cp)}</span><span class="lang-zh">{esc(zh_cp)}</span></button>
  <template id="md-source">{esc(md)}</template>
 </section>
</main>
{footer()}'''
    return page(s["name"], z.get("name_zh", s["name"]), (s.get("tagline") or "")[:150],
                (z.get("tagline_zh") or "")[:80], body, f'styles/{s["slug"]}/')

def style_markdown(s, z):
    lines = [f"# {s['name']} · {z.get('name_zh','')}", "",
             f"Style reference — {SITE_URL}/styles/{s['slug']}/", ""]
    if s.get("tagline"):
        lines += [s["tagline"], z.get("tagline_zh", ""), ""]
    if s.get("aliases"):
        lines += ["## If you called it… / 如果你管它叫……", ""]
        for i, a in enumerate(s["aliases"]):
            az = z.get("aliases_zh", [])
            lines.append(f"- “{a}” / 「{az[i] if i < len(az) else ''}」")
        lines.append("")
    if s.get("signals"):
        lines += ["## Full style DNA / 完整风格 DNA", ""]
        for sig in s["signals"]:
            sz = z.get("signals_zh", {}).get(sig["id"], {})
            lines += [f"- **[{sig['role']}] {sig['name']} · {sz.get('name_zh','')}** ({sig['facet']})",
                      f"  {sig['description']}", f"  {sz.get('description_zh','')}"]
        lines.append("")
    if s.get("brief"):
        lines += ["## Style brief / 风格 Brief", "", s["brief"], "", z.get("brief_zh", ""), ""]
    if s.get("origin"):
        lines += ["## Origin / 起源", "", s["origin"], "", z.get("origin_zh", "")]
    return "\n".join(lines)

def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

def build():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    write("index.html", homepage())
    for e in ENTRIES:
        write(f'{e["platform"]}/{e["slug"]}/index.html', entry_page(e))
    for slug in GUIDES:
        write(f"guides/{slug}/index.html", guide_page(slug))
    write("guides/translate/index.html", translate_page())
    if STYLES:
        write("styles/index.html", styles_hub_page())
        for s in STYLES:
            write(f'styles/{s["slug"]}/index.html', style_page(s))
    # static assets
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"))
    shutil.copyfile(os.path.join(ROOT, "manifest.webmanifest"), os.path.join(OUT, "manifest.webmanifest"))
    with open(os.path.join(ROOT, "sw.js"), encoding="utf-8") as f:
        sw = f.read()
    version = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S")
    write("sw.js", sw.replace("__SW_VERSION__", version))
    # feed
    items = []
    date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    for e in ENTRIES:
        z = ZH[e["slug"]]
        items.append(f'''<item><title>{esc(e["name"])} · {esc(z["name_zh"])}</title>
<link>{SITE_URL}/{e["platform"]}/{e["slug"]}/</link>
<guid>{SITE_URL}/{e["platform"]}/{e["slug"]}/</guid>
<pubDate>{date}</pubDate>
<description>{esc(e["tagline"])} / {esc(z["tagline_zh"])}</description></item>''')
    for s in STYLES:
        z = style_zh(s)
        items.append(f'''<item><title>{esc(s["name"])} · {esc(z.get("name_zh",""))}</title>
<link>{SITE_URL}/styles/{s["slug"]}/</link>
<guid>{SITE_URL}/styles/{s["slug"]}/</guid>
<pubDate>{date}</pubDate>
<description>{esc((s.get("tagline") or "")[:200])}</description></item>''')
    write("feed.xml", f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>Learn UI Name · 界面叫啥</title>
<link>{SITE_URL}/</link>
<description>{esc(UI["tagline"])} — bilingual UI dictionary</description>
{"".join(items)}
</channel></rss>''')
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    urls = ["/"] + [f'/{e["platform"]}/{e["slug"]}/' for e in ENTRIES] + \
           [f"/guides/{s}/" for s in GUIDES] + ["/guides/translate/"]
    if STYLES:
        urls += ["/styles/"] + [f'/styles/{s["slug"]}/' for s in STYLES]
    write("sitemap.xml", f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"".join(f"<url><loc>{SITE_URL}{u}</loc></url>" for u in urls)}
</urlset>''')
    print(f"Built {len(urls)} pages into site/")

if __name__ == "__main__":
    build()
