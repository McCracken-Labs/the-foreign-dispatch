#!/usr/bin/env python3
"""The Foreign Desk static site builder.

Usage:
    python3 build.py            # builds from data/edition.json using its date
    python3 build.py 2026-07-14 # override date (must match data/edition.json date_iso)

Reads:
    data/edition.json  -> today's headlines (see schema in data/edition.example.json)
    data/archive.json  -> running list of past editions (list of {iso,human,summary,file})

Writes:
    index.html                 -> today's edition (homepage)
    edition-<iso>.html         -> permanent dated copy of today's edition
    archive.html               -> archive index (rebuilt from archive.json)

Static files kept as-is: style.css, about.html, .nojekyll
No third-party dependencies (Python 3 stdlib only).
"""
import json, sys, os, html

ROOT = os.path.dirname(os.path.abspath(__file__))

LEAN = {
    "neutral": ("n-neutral", "Independent"),
    "funded":  ("n-funded",  "State-funded"),
    "progov":  ("n-progov",  "Pro-government"),
    "state":   ("n-state",   "State-controlled"),
}

def esc(s):
    return html.escape(s or "", quote=True)

def topbar(active):
    def cls(name): return ' class="active"' if name == active else ''
    return f'''<div class="topbar"><div class="inner">
  <span class="brand">The Foreign Desk</span>
  <nav>
    <a href="index.html"{cls("today")}>Today</a>
    <a href="archive.html"{cls("archive")}>Archive</a>
    <a href="about.html"{cls("about")}>About</a>
  </nav>
</div></div>'''

def render_item(it):
    lean_key = it.get("lean", "neutral")
    lean_cls, lean_label = LEAN.get(lean_key, LEAN["neutral"])
    date = it.get("date", "")
    src_bits = [esc(it["outlet"])]
    src_bits.append(f'<span class="lean {lean_cls}"><span class="dot"></span>{lean_label}</span>')
    if date:
        src_bits.append("· " + esc(date))
    src = " ".join(src_bits)
    orig = f'\n      <div class="orig">{esc(it["orig"])}</div>' if it.get("orig") else ""
    note = f'\n      <div class="note">{esc(it["note"])}</div>' if it.get("note") else ""
    return f'''    <article class="item">
      <div class="src">{src}</div>
      <h3><a href="{esc(it["url"])}" target="_blank" rel="noopener">{esc(it["title"])}</a></h3>{orig}{note}
    </article>'''

def render_country(c):
    items = "\n".join(render_item(it) for it in c["items"])
    region = f'<span class="region">{esc(c["region"])}</span>' if c.get("region") else ""
    return f'''  <section class="country">
    <h2><span class="flag">{c.get("flag","")}</span> {esc(c["name"])} {region}</h2>
{items}
  </section>'''

def render_edition(ed):
    countries = "\n\n".join(render_country(c) for c in ed["countries"])
    n = len(ed["countries"])
    title = "The Foreign Desk — What the world's press is saying about America"
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="A daily digest of how newspapers outside the United States are covering it — headlines translated to English, with links to the originals.">
<link rel="stylesheet" href="style.css">
</head>
<body>
{topbar("today")}

<div class="wrap">
  <header class="masthead">
    <h1>The Foreign Desk</h1>
    <div class="tag">What the world's press is saying about America — in their own words</div>
  </header>
  <div class="dateline">
    <span>{esc(ed["date_human"])}</span>
    <span>Foreign-press digest · {n} countries today</span>
  </div>

  <div class="intro">
    A daily look at how newspapers <b>outside</b> the United States are covering it — headlines translated to English, the original shown where relevant, and a link to every full article. Sources rotate day to day; each is tagged by editorial character so you can weigh the framing yourself.
    <div class="legend">
      <span class="lchip"><span class="dot n-neutral"></span>Independent / neutral</span>
      <span class="lchip"><span class="dot n-funded"></span>State-funded, broad editorial</span>
      <span class="lchip"><span class="dot n-progov"></span>Pro-government</span>
      <span class="lchip"><span class="dot n-state"></span>State-controlled</span>
    </div>
  </div>

{countries}

  <footer>
    <b>The Foreign Desk</b> · Edition of {esc(ed["date_human"])} · <a href="archive.html">Browse the archive</a><br>
    Headlines translated from the original where noted. Follow each link for the full article in its original outlet. See <a href="about.html">About</a> for method and sources.
  </footer>
</div>
</body>
</html>
'''

def render_archive(archive):
    lis = []
    for e in archive:
        lis.append(f'''    <li>
      <a href="{esc(e["file"])}">{esc(e["human"])}</a>
      <div class="meta">{esc(e["summary"])}</div>
    </li>''')
    items = "\n".join(lis)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Archive — The Foreign Desk</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
{topbar("archive")}

<div class="wrap">
  <header class="masthead">
    <h1>Archive</h1>
    <div class="tag">Every past edition, preserved</div>
  </header>

  <ul class="arch-list">
{items}
  </ul>

  <footer>
    <b>The Foreign Desk</b> · <a href="index.html">Today's edition</a> · <a href="about.html">About</a><br>
    A new edition is archived here automatically every morning.
  </footer>
</div>
</body>
</html>
'''

def main():
    with open(os.path.join(ROOT, "data", "edition.json"), encoding="utf-8") as f:
        ed = json.load(f)
    iso = ed["date_iso"]
    if len(sys.argv) > 1 and sys.argv[1] != iso:
        print(f"WARNING: arg date {sys.argv[1]} != edition date_iso {iso}; using {iso}")

    edition_html = render_edition(ed)
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(edition_html)
    dated_file = f"edition-{iso}.html"
    with open(os.path.join(ROOT, dated_file), "w", encoding="utf-8") as f:
        f.write(edition_html)

    # update archive.json (prepend today if not present)
    apath = os.path.join(ROOT, "data", "archive.json")
    archive = []
    if os.path.exists(apath):
        with open(apath, encoding="utf-8") as f:
            archive = json.load(f)
    archive = [e for e in archive if e.get("iso") != iso]
    archive.insert(0, {"iso": iso, "human": ed["date_human"],
                       "summary": ed.get("summary", ""), "file": dated_file})
    with open(apath, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)

    with open(os.path.join(ROOT, "archive.html"), "w", encoding="utf-8") as f:
        f.write(render_archive(archive))

    print(f"Built edition {iso}: index.html, {dated_file}, archive.html ({len(archive)} editions)")

if __name__ == "__main__":
    main()
