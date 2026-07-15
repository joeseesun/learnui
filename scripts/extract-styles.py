#!/usr/bin/env python3
"""Extract structured data for the Name That Vibe (/styles) atlas.

Reads the React Server Component (RSC) payloads saved under reference/raw/
(style-<slug>-payload.txt per style page, styles-payload.txt for the hub)
and writes:

  data/styles.json       - array of 14 style entries, in ItemList order
  data/styles-meta.json  - hub tagline, governed-atlas note, researching list

The payload files are concatenations of decoded `self.__next_f.push([1,"..."])`
chunk strings. Records inside look like `<hex-id>:<value>` separated by
newlines, where a value is either JSON or `T<hexlen>,<raw text>`. Chunk
boundaries are lost in the payload files, so a T-record's text may be
immediately followed by the next record with no separating newline; the
declared length can also drift by a few code points (observed +2), so the
scanner searches for the nearest valid record boundary around the declared
length instead of trusting it blindly.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "reference" / "raw"
OUT = ROOT / "data"

# ItemList order from https://namethatui.com/styles
ORDER = [
    "skeuomorphism", "neumorphism", "glassmorphism", "liquid-glass",
    "web-brutalism", "neobrutalism", "y2k", "frutiger-aero", "flat-design",
    "minimalism", "claymorphism", "vernacular-web", "aqua", "windows-aero",
]

ROLES = {"defining", "supporting", "variable", "avoid"}

WARNINGS = []


def warn(msg):
    WARNINGS.append(msg)
    print(f"  ! {msg}", file=sys.stderr)


# ---------------------------------------------------------------- payload scan

HDR = re.compile(r"^([0-9a-f]{1,3}):(.*)$", re.S)
THDR = re.compile(r"^T([0-9a-f]+),(.*)$", re.S)


def u16len(s):
    return sum(2 if ord(c) > 0xFFFF else 1 for c in s)


def split_blob(body, ln, seen):
    """Split a T-record body into (blob text, rest of line).

    `ln` is the declared text length; the real boundary can drift by a dozen
    code points either way (observed: +2, and up to -10 when the text
    contains supplementary-plane characters, which count as 2 UTF-16 units).
    A following record starts immediately, so a wrong split can eat leading
    digits of the next record's hex id. Prefer the split whose trailing
    record id has not been seen yet, then one that does not cut a hex id in
    half, then the smallest drift.
    """
    cands = []
    for d in range(0, 17):
        for p in ((ln,) if d == 0 else (ln - d, ln + d)):
            if not (0 <= p <= len(body)):
                continue
            rest = body[p:]
            if not rest:
                cands.append((0, 0, d, p))
                continue
            m = HDR.match(rest)
            if m:
                val = m.group(2)
                ok = bool(THDR.match(val))
                if not ok:
                    try:
                        json.loads(val)
                        ok = True
                    except Exception:
                        ok = False
                if ok:
                    eats_hex = 1 if body[p - 1] in "0123456789abcdef" else 0
                    cands.append((1 if m.group(1) in seen else 0, eats_hex, d, p))
    if not cands:
        return body, ""
    cands.sort()
    p = cands[0][3]
    if p != ln:
        warn(f"T-record length drift: declared {ln}, used {p}")
    return body[:p], body[p:]


def scan_payload(text):
    """Parse a payload file into {record_id: raw_value_string}."""
    recs = {}
    lines = text.split("\n")
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        idx += 1
        if not line.strip():
            continue
        m = HDR.match(line)
        if not m:
            continue  # e.g. ':HL[...]' hint records without an id
        rid, val = m.group(1), m.group(2)
        if rid in recs:
            warn(f"duplicate record id {rid!r} (payload scan mis-split?)")
        tm = THDR.match(val)
        if tm:
            ln = int(tm.group(1), 16)
            body = tm.group(2)
            # blob may itself contain newlines; pull following lines back in
            while u16len(body) < ln - 2 and idx < len(lines):
                body += "\n" + lines[idx]
                idx += 1
            blob, rest = split_blob(body, ln, recs)
            recs[rid] = blob
            if rest:
                lines.insert(idx, rest)
        else:
            recs[rid] = val
    return recs


def parse_records(recs):
    parsed = {}
    for rid, v in recs.items():
        try:
            parsed[rid] = json.loads(v)
        except Exception:
            parsed[rid] = v  # raw T-text or I[...] import record
    return parsed


REF = re.compile(r"^\$[@L]?([0-9a-f]+)$")
PATHREF = re.compile(r"^\$([0-9a-f]+)((?::[^:$]+)+)$")


def nav_segment(target, seg):
    """One step of an RSC path ref. Elements are serialized as open arrays
    ['$', tag, key, props], so 'props'/'children' map onto index 3."""
    if isinstance(target, dict):
        return target[seg]
    if isinstance(target, list):
        if len(target) >= 4 and target[0] == "$":
            if seg == "props":
                return target[3]
            if seg == "children" and isinstance(target[3], dict):
                return target[3]["children"]
        if seg.isdigit():
            return target[int(seg)]
    raise KeyError(seg)


def resolve(v, parsed, depth=0):
    """Inline references into a plain tree.

    Handles plain refs ("$22", "$L22", "$@22") and path refs that point into
    a specific slot of another record ("$22:props:children:4:...:signals:0").
    """
    if depth > 80:
        return v
    if isinstance(v, str):
        m = PATHREF.match(v)
        if m and m.group(1) in parsed:
            target = resolve(parsed[m.group(1)], parsed, depth + 1)
            try:
                for seg in m.group(2)[1:].split(":"):
                    target = nav_segment(target, seg)
            except (KeyError, IndexError, TypeError):
                return v
            return resolve(target, parsed, depth + 1)
        m = REF.match(v)
        if m and m.group(1) in parsed:
            return resolve(parsed[m.group(1)], parsed, depth + 1)
        return v
    if isinstance(v, list):
        return [resolve(x, parsed, depth + 1) for x in v]
    if isinstance(v, dict):
        return {k: resolve(x, parsed, depth + 1) for k, x in v.items()}
    return v


# ---------------------------------------------------------------- tree helpers

def is_el(v, tag=None):
    return (
        isinstance(v, list)
        and len(v) >= 4
        and v[0] == "$"
        and isinstance(v[1], str)
        and (tag is None or v[1] == tag)
    )


def props_of(el):
    return el[3] if isinstance(el[3], dict) else {}


def children_of(el):
    return props_of(el).get("children")


def text_of(node):
    """Concatenate all string descendants; skip false/null/React sentinels."""
    if node is None or node is False:
        return ""
    if isinstance(node, str):
        return "" if node in ("$undefined",) else node
    if isinstance(node, list):
        if is_el(node):
            return text_of(children_of(node))
        return "".join(text_of(x) for x in node)
    if isinstance(node, dict):
        # a path ref can resolve to a bare props object in children position
        return text_of(node.get("children"))
    return ""


def walk(node):
    """Yield every element in the tree, depth-first.

    `children` may be a string, a list of child nodes, or a single element
    in open form (['$','div',null,{...}]) — recursing through walk() again
    sorts out which is which.
    """
    if is_el(node):
        yield node
        yield from walk(children_of(node))
    elif isinstance(node, list):
        for c in node:
            yield from walk(c)
    elif isinstance(node, dict):
        # a path ref can resolve to a bare props object in children position
        yield from walk(node.get("children"))


def direct_strings(node):
    """Only the string children directly under node (no nested elements)."""
    ch = children_of(node) if is_el(node) else node
    if isinstance(ch, str):
        return ch
    if isinstance(ch, list):
        return "".join(c for c in ch if isinstance(c, str))
    return ""


def find_sections(article):
    """Return [(h2_text, section_element), ...] for top-level <section>s."""
    out = []
    for el in walk(article):
        if is_el(el, "section"):
            ch = children_of(el)
            kids = [ch] if is_el(ch) else (ch if isinstance(ch, list) else [ch])
            h2 = next((k for k in kids if is_el(k, "h2")), None)
            if h2 is not None:
                out.append((text_of(h2), el, h2))
    return out


def find_article(parsed):
    for rid, v in parsed.items():
        if is_el(v, "article"):
            return rid, v
    raise SystemExit("no <article> record found in payload")


# ---------------------------------------------------------------- extraction

def extract_style(slug, order):
    text = (RAW / f"style-{slug}-payload.txt").read_text(encoding="utf-8")
    parsed = parse_records(scan_payload(text))
    article_rid, article_raw = find_article(parsed)
    article = resolve(article_raw, parsed)
    sections = find_sections(article)
    # some sections stream as separate records outside <article>
    # (e.g. windows-aero's Style brief) — merge them, article first
    seen_h2 = {h for h, _, _ in sections}
    for rid, v in parsed.items():
        if rid == article_rid:
            continue
        for h2txt, sec, h2el in find_sections(resolve(v, parsed)):
            if h2txt not in seen_h2:
                sections.append((h2txt, sec, h2el))
                seen_h2.add(h2txt)
    by_h2 = {}
    for h2txt, sec, h2el in sections:
        by_h2.setdefault(h2txt.split(" —")[0].split(" — ")[0], (sec, h2el))

    entry = {
        "slug": slug,
        "name": None,
        "order": order,
        "tagline": None,
        "scope": None,
        "aliases": None,
        "confusedWith": None,
        "signals": None,
        "code": None,
        "brief": None,
        "accessibility": None,
        "origin": None,
        "seeAlso": None,
    }

    # -- hero: name, tagline, scope
    h1 = next((el for el in walk(article) if is_el(el, "h1")), None)
    if h1 is not None:
        entry["name"] = text_of(h1).strip()
    else:
        warn(f"{slug}: no h1")

    tag_ps = []
    for el in walk(article):
        if is_el(el, "section"):
            break  # tagline lives in the hero, before any section
        cn = props_of(el).get("className", "")
        if is_el(el, "p") and "text-foreground/90" in cn and "text-[14.5px]" in cn:
            tag_ps.append(el)
    if tag_ps:
        entry["tagline"] = "\n\n".join(text_of(p).strip() for p in tag_ps)
    else:
        warn(f"{slug}: no tagline <p>")

    for el in walk(article):
        if is_el(el, "p"):
            t = text_of(el).strip()
            if t.startswith("Scope:"):
                entry["scope"] = t
                break

    # -- aliases ("If you called it…")
    sec = by_h2.get("If you called it…")
    aliases = []
    if sec:
        for el in walk(sec[0]):
            cn = props_of(el).get("className", "")
            if is_el(el, "span") and "bg-secondary/70" in cn:
                t = text_of(el).strip()
                if t.startswith("“") and t.endswith("”"):
                    t = t[1:-1]
                if t:
                    aliases.append(t)
    if not aliases:
        warn(f"{slug}: no alias chips")
    entry["aliases"] = aliases

    # -- often confused with
    for h2txt, sec_el, h2el in sections:
        if h2txt.startswith("Often confused with"):
            link = next(
                (el for el in walk(h2el) if props_of(el).get("href", "").startswith("/styles/")),
                None,
            )
            cards = [
                el for el in walk(sec_el)
                if is_el(el, "div") and "bg-card p-3.5" in props_of(el).get("className", "")
            ]
            cw = {"slug": None, "name": None, "because": None, "wouldBecomeIf": None}
            if link is not None:
                cw["slug"] = props_of(link)["href"].rsplit("/", 1)[-1]
                cw["name"] = text_of(link).strip()
            else:
                warn(f"{slug}: confused-with link missing")
            if len(cards) >= 1:
                cw["because"] = text_of(cards[0]).strip() or None
            if len(cards) >= 2:
                cw["wouldBecomeIf"] = text_of(cards[1]).strip() or None
            if len(cards) != 2:
                warn(f"{slug}: confused-with cards = {len(cards)}")
            entry["confusedWith"] = cw
            break

    # -- full style DNA
    sec = by_h2.get("Full style DNA")
    signals = []
    if sec:
        for el in walk(sec[0]):
            sig = props_of(el).get("signals")
            if isinstance(sig, list) and sig and isinstance(sig[0], dict):
                for s in sig:
                    signals.append({
                        "id": s.get("id"),
                        "facet": s.get("facet"),
                        "role": s.get("role"),
                        "name": s.get("name"),
                        "description": s.get("description"),
                    })
                    if s.get("role") not in ROLES:
                        warn(f"{slug}: unexpected signal role {s.get('role')!r}")
                break
    if not signals:
        warn(f"{slug}: no DNA signals")
    entry["signals"] = signals

    # -- in code
    sec = by_h2.get("In code")
    code = []
    if sec:
        for el in walk(sec[0]):
            if is_el(el, "tr"):
                tds = [c for c in (children_of(el) or []) if is_el(c, "td")]
                if len(tds) < 2:
                    continue
                lang = text_of(tds[0]).strip() or None
                code_el = next((x for x in walk(tds[1]) if is_el(x, "code")), None)
                snippet = text_of(code_el if code_el is not None else tds[1]).strip()
                note = text_of(tds[2]).strip() if len(tds) > 2 else ""
                code.append({
                    "title": note or None,
                    "language": lang.lower() if lang else None,
                    "code": snippet or None,
                })
    entry["code"] = code

    # -- style brief
    sec = by_h2.get("Style brief")
    if sec:
        brief = None
        for el in walk(sec[0]):
            if is_el(el, "p") and "font-mono" in props_of(el).get("className", ""):
                brief = text_of(el).strip()
                break
        if not brief:  # fallback: copy-button prop carries the same text
            for el in walk(sec[0]):
                t = props_of(el).get("text")
                if isinstance(t, str) and len(t) > 40:
                    brief = t.strip()
                    break
        if not brief:
            warn(f"{slug}: no brief text")
        entry["brief"] = brief
    else:
        warn(f"{slug}: no Style brief section")

    # -- accessibility & misuse
    sec = by_h2.get("Accessibility & misuse")
    if sec:
        items = [text_of(li).strip() for li in walk(sec[0]) if is_el(li, "li")]
        items = [t for t in items if t]
        entry["accessibility"] = "\n\n".join(items) if items else None
        if not items:
            warn(f"{slug}: accessibility section has no list items")
    else:
        warn(f"{slug}: no Accessibility section")

    # -- origin
    sec = by_h2.get("Origin")
    if sec:
        p = next((el for el in walk(sec[0]) if is_el(el, "p")), None)
        entry["origin"] = text_of(p).strip() if p is not None else None
        if p is None:
            warn(f"{slug}: origin section has no <p>")
    else:
        warn(f"{slug}: no Origin section")

    # -- see also
    sec = by_h2.get("See also")
    see = []
    if sec:
        for el in walk(sec[0]):
            href = props_of(el).get("href")
            if isinstance(href, str) and href.startswith("/"):
                name = direct_strings(el).strip() or text_of(el).strip()
                see.append({"slug": href.lstrip("/"), "name": name})
    else:
        warn(f"{slug}: no See also section")
    entry["seeAlso"] = see

    return entry


def extract_meta():
    text = (RAW / "styles-payload.txt").read_text(encoding="utf-8")
    parsed = parse_records(scan_payload(text))
    # hero and governed note may live in different RSC records — search all
    trees = [resolve(v, parsed) for v in parsed.values()]

    def find_first(pred):
        for t in trees:
            for e in walk(t):
                if pred(e):
                    return e
        return None

    h1 = find_first(lambda e: is_el(e, "h1"))
    intro = find_first(
        lambda e: is_el(e, "p")
        and text_of(e).strip().startswith("The visual styles atlas"))
    hub_tagline = text_of(h1).strip() if h1 is not None else ""
    if intro is not None:
        hub_tagline += " " + text_of(intro).strip()
    else:
        warn("hub: intro paragraph not found")

    # governed-atlas note + researching list (the note <p> opens with
    # "There is no honest list of ..." and inlines the researching spans)
    note_p = find_first(lambda e: is_el(e, "p") and "no honest list" in text_of(e))
    governed = None
    researching = []
    if note_p is not None:
        # children: [prose ending "In research now:", " ", [name spans], "."]
        ch = children_of(note_p)
        first = ch[0] if isinstance(ch, list) and ch and isinstance(ch[0], str) else None
        governed = (first or direct_strings(note_p)).strip()
        for e in walk(note_p):
            if is_el(e, "span") and "text-foreground/75" in props_of(e).get("className", ""):
                researching.append(text_of(e).strip())
    else:
        warn("hub: governed-atlas note not found")

    return {
        "hubTagline": hub_tagline or None,
        "governedNote": governed,
        "researching": researching,
    }


def main():
    styles = []
    for i, slug in enumerate(ORDER, start=1):
        print(f"[{i:2d}/14] {slug}")
        styles.append(extract_style(slug, i))

    meta = extract_meta()

    OUT.mkdir(exist_ok=True)
    styles_path = OUT / "styles.json"
    meta_path = OUT / "styles-meta.json"
    styles_path.write_text(
        json.dumps(styles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # ---- validation summary
    print("\nper-style summary:")
    failures = []
    for s in styles:
        checks = {
            "tagline": bool(s["tagline"]),
            "signals>=3": len(s["signals"]) >= 3,
            "brief": bool(s["brief"]),
            "aliases>=2": len(s["aliases"]) >= 2,
        }
        bad = [k for k, ok in checks.items() if not ok]
        if bad:
            failures.append((s["slug"], bad))
        cw = s["confusedWith"]["slug"] if s["confusedWith"] else "-"
        print(
            f"  {s['slug']:<15} name={s['name']!r:<22} "
            f"tag={len(s['tagline'] or ''):>4}c alias={len(s['aliases'])} "
            f"sig={len(s['signals'])} code={len(s['code'])} "
            f"brief={len(s['brief'] or ''):>4}c a11y={len(s['accessibility'] or ''):>4}c "
            f"origin={len(s['origin'] or ''):>4}c seeAlso={len(s['seeAlso'])} "
            f"scope={'y' if s['scope'] else '-'} cw={cw}"
            + (f"  FAIL:{','.join(bad)}" if bad else "")
        )
    print(f"\nwrote {styles_path} ({styles_path.stat().st_size} bytes)")
    print(f"wrote {meta_path} ({meta_path.stat().st_size} bytes)")
    if failures:
        print(f"\nVALIDATION FAILURES: {failures}")
        sys.exit(1)
    print("all validation checks passed")


if __name__ == "__main__":
    main()
