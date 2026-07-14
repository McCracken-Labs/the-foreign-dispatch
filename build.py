#!/usr/bin/env python3
"""The Foreign Desk static site builder.

Builds from JSON data:
  data/edition.json      -> index.html + edition-<iso>.html   (World Press edition)
  data/independent.json  -> independent.html                  (Independent journalism page)
  data/archive.json      -> archive.html                      (list of past World Press editions)

Static files kept as-is: style.css, about.html, .nojekyll
Python 3 stdlib only. Usage: python3 build.py
"""
import json, os, html

ROOT = os.path.dirname(os.path.abspath(__file__))

TAGS = {
    "neutral": ("n-neutral", "Independent"),
    "funded":  ("n-funded",  "State-funded"),
    "progov":  ("n-progov",  "Pro-government"),
    "state":   ("n-state",   "State-controlled"),
    "invest":   ("n-invest",   "Investigative nonprofit"),
    "left":     ("n-left",     "Independent · left"),
    "libert":   ("n-libert",   "Libertarian"),
    "cright":   ("n-cright",   "Conservative"),
    "hetero":   ("n-hetero",   "Heterodox"),
    "indie":    ("n-indie",    "Independent"),
    "exile":    ("n-exile",    "Independent · in exile"),
    "analysis": ("n-analysis", "Academic analysis"),
}

def esc(s):
    return html.escape(s or "", quote=True)

def topbar(active):
    def cls(name): return ' class="active"' if name == active else ''
    return f'''<div class="topbar"><div class="inner">
  <span class="brand">The Foreign Desk</span>
  <nav>
    <a href="index.html"{cls("today")}>World Press</a>
    <a href="independent.html"{cls("independent")}>Independent</a>
    <a href="archive.html"{cls("archive")}>Archive</a>
    <a href="about.html"{cls("about")}>About</a>
  </nav>
</div></div>'''

def render_item(it):
    bits = []
    if it.get("outlet"):
        bits.append(esc(it["outlet"]))
    lean = it.get("lean")
    if lean in TAGS:
        lc, ll = TAGS[lean]
        bits.append(f'<span class="lean {lc}"><span class="dot"></span>{ll}</span>')
    if it.get("date"):
        bits.append("· " + esc(it["date"]))
    src = " ".join(bits)
    orig = f'\n      <div class="orig">{esc(it["orig"])}</div>' if it.get("orig") else ""
    note = f'\n      <div class="note">{esc(it["note"])}</div>' if it.get("note") else ""
    return f'''    <article class="item">
      <div class="src">{src}</div>
      <h3><a href="{esc(it["url"])}" target="_blank" rel="noopener">{esc(it["title"])}</a></h3>{orig}{note}
    </article>'''

def render_section(c):
    items = "\n".join(render_item(it) for it in c["items"])
    region = f'<span class="region">{esc(c["region"])}</span>' if c.get("region") else ""
    flag = f'<span class="flag">{c.get("flag","")}</span> ' if c.get("flag") else ""
    return f'''  <section class="country">
    <h2>{flag}{esc(c["name"])} {region}</h2>
{items}
  </section>'''

GOV_LEGEND = '''    <div class="legend">
      <span class="lchip"><span class="dot n-neutral"></span>Independent / neutral</span>
      <span class="lchip"><span class="dot n-funded"></span>State-funded, broad editorial</span>
      <span class="lchip"><span class="dot n-progov"></span>Pro-government</span>
      <span class="lchip"><span class="dot n-state"></span>State-controlled</span>
    </div>'''

IND_LEGEND = '''    <div class="legend">
      <span class="lchip"><span class="dot n-invest"></span>Investigative / nonprofit</span>
      <span class="lchip"><span class="dot n-left"></span>Independent left</span>
      <span class="lchip"><span class="dot n-libert"></span>Libertarian</span>
      <span class="lchip"><span class="dot n-cright"></span>Conservative</span>
      <span class="lchip"><span class="dot n-hetero"></span>Heterodox</span>
      <span class="lchip"><span class="dot n-exile"></span>In exile</span>
      <span class="lchip"><span class="dot n-analysis"></span>Academic</span>
    </div>'''

PAGES = {
    "today": {
        "title": "The Foreign Desk — What the world's press is saying about America",
        "meta": "A daily digest of how newspapers outside the United States are covering it — headlines translated to English, with links to the originals.",
        "tagline": "What the world's press is saying about America — in their own words",
        "dateline_right": lambda n: f"Foreign-press digest · {n} countries today",
        "intro": ("A daily look at how newspapers <b>outside</b> the United States are covering it — "
                  "headlines translated to English, the original shown where relevant, and a link to every "
                  "full article. Sources rotate day to day; each is tagged by editorial character so you can "
                  "weigh the framing yourself."),
        "legend": GOV_LEGEND,
    },
    "independent": {
        "title": "The Foreign Desk — Independent journalism on America",
        "meta": "Independent, nonprofit, reader-funded and investigative journalism on the United States — grouped by editorial orientation so you can read across viewpoints.",
        "tagline": "Independent &amp; investigative journalism on America — read across the spectrum",
        "dateline_right": lambda n: f"Independent journalism · {n} viewpoints",
        "intro": ("Beyond the big outlets: <b>independent, nonprofit, reader-funded and investigative</b> "
                  "journalism — the kind with more room for critical thinking and adversarial reporting. "
                  "Sources are grouped by editorial orientation so you can read <b>across</b> viewpoints, not "
                  "just within one. Independent media leans left globally, so libertarian, conservative and "
                  "heterodox voices are included on purpose for balance. The <b>in exile</b> group carries "
                  "diaspora outlets that report on authoritarian home countries — and their US dealings — "
                  "from abroad, for safety."),
        "legend": IND_LEGEND,
    },
}

def render_page(data, kind):
    cfg = PAGES[kind]
    sections = "\n\n".join(render_section(c) for c in data["countries"])
    n = len(data["countries"])
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{cfg["title"]}</title>
<meta name="description" content="{esc(cfg["meta"])}">
<link rel="stylesheet" href="style.css">
</head>
<body>
{topbar(kind)}

<div class="wrap">
  <header class="masthead">
    <h1>The Foreign Desk</h1>
    <div class="motto">Outside the box. Outside the border.</div>
    <div class="tag">{cfg["tagline"]}</div>
  </header>
  <div class="dateline">
    <span>{esc(data["date_human"])}</span>
    <span>{cfg["dateline_right"](n)}</span>
  </div>

  <div class="intro">
    {cfg["intro"]}
{cfg["legend"]}
  </div>

{sections}

  <footer>
    <b>The Foreign Desk</b> · {esc(data["date_human"])} · <a href="index.html">World Press</a> · <a href="independent.html">Independent</a> · <a href="archive.html">Archive</a><br>
    Headlines translated from the original where noted. Follow each link for the full article in its original outlet. See <a href="about.html">About</a> for method and sources.
  </footer>
</div>
</body>
</html>
'''

def render_archive(archive):
    lis = "\n".join(f'''    <li>
      <a href="{esc(e["file"])}">{esc(e["human"])}</a>
      <div class="meta">{esc(e["summary"])}</div>
    </li>''' for e in archive)
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
    <div class="tag">Every past World Press edition, preserved</div>
  </header>

  <ul class="arch-list">
{lis}
  </ul>

  <footer>
    <b>The Foreign Desk</b> · <a href="index.html">World Press</a> · <a href="independent.html">Independent</a> · <a href="about.html">About</a><br>
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
    edition_html = render_page(ed, "today")
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(edition_html)
    dated_file = f"edition-{iso}.html"
    with open(os.path.join(ROOT, dated_file), "w", encoding="utf-8") as f:
        f.write(edition_html)

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
    built = ["index.html", dated_file, "archive.html"]

    ipath = os.path.join(ROOT, "data", "independent.json")
    if os.path.exists(ipath):
        with open(ipath, encoding="utf-8") as f:
            ind = json.load(f)
        with open(os.path.join(ROOT, "independent.html"), "w", encoding="utf-8") as f:
            f.write(render_page(ind, "independent"))
        built.append("independent.html")

    print(f"Built edition {iso}: {', '.join(built)} ({len(archive)} archived editions)")

if __name__ == "__main__":
    main()
