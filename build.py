#!/usr/bin/env python3
"""A View on America static site builder.

  data/edition.json      -> index.html + edition-<iso>.html   (World Press edition)
  data/independent.json  -> independent.html                  (Independent journalism page)
  data/archive.json      -> archive.html                      (list of past World Press editions)

Static files kept as-is: style.css, about.html, .nojekyll
Python 3 stdlib only. Usage: python3 build.py
"""
import json, os, html

ROOT = os.path.dirname(os.path.abspath(__file__))

SHARE_JS = """<script>
function shareSite(){
  var url = new URL('./', location.href).href;
  var data = {title:"A View on America", text:"What the world's press is saying about America", url:url};
  if(navigator.share){ navigator.share(data).catch(function(){}); }
  else if(navigator.clipboard){ navigator.clipboard.writeText(url).then(flash); }
  else { window.prompt("Copy this link:", url); }
}
function flash(){ var b=document.querySelector(".sharebtn"); if(!b) return; var t=b.textContent; b.textContent="Link copied!"; setTimeout(function(){ b.textContent=t; }, 1500); }
</script>"""

TAGS = {
    "neutral": ("n-neutral", "Independent"),
    "funded":  ("n-funded",  "State-funded"),
    "progov":  ("n-progov",  "Pro-government"),
    "state":   ("n-state",   "State-controlled"),
    "invest":   ("n-invest",   "Investigative nonprofit"),
    "left":     ("n-left",     "Independent left"),
    "libert":   ("n-libert",   "Libertarian"),
    "cright":   ("n-cright",   "Conservative"),
    "hetero":   ("n-hetero",   "Heterodox"),
    "indie":    ("n-indie",    "Independent"),
    "exile":    ("n-exile",    "Independent, in exile"),
    "analysis": ("n-analysis", "Academic analysis"),
}

def esc(s):
    return html.escape(s or "", quote=True)

def topbar(active):
    def cls(name): return ' class="active"' if name == active else ''
    return f'''<div class="topbar"><div class="inner">
  <a class="brand" href="./">A View on America</a>
  <nav>
    <a href="./"{cls("today")}>World Press</a>
    <a href="independent.html"{cls("independent")}>Independent</a>
    <a href="archive.html"{cls("archive")}>Archive</a>
    <a href="about.html"{cls("about")}>About</a>
    <a class="support" href="https://paypal.me/McCracken365" target="_blank" rel="noopener">♥ Support</a>
    <button class="sharebtn" type="button" onclick="shareSite()">Share</button>
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

SUPPORTBOX = """
  <div class="supportbox">
    <span>Enjoying <b>A View on America</b>? It's free and ad-free.</span>
    <a class="btn" href="https://paypal.me/McCracken365" target="_blank" rel="noopener">♥ Support via PayPal</a>
  </div>
"""

PAGES = {
    "today": {
        "title": "A View on America · What the world's press is saying about America",
        "meta": "A daily digest of how newspapers outside the United States are covering it. Headlines translated to English, with links to the originals.",
        "tagline": "What the world's press is saying about America, in their own words",
        "dateline_right": lambda n: f"Foreign-press digest · {n} countries today",
        "intro": ("A daily look at how newspapers <b>outside</b> the United States cover it. Headlines are "
                  "translated to English, the original is shown where it matters, and every item links to the "
                  "full article. Sources rotate from day to day, and each is tagged by editorial character so "
                  "you can weigh the framing yourself."),
        "legend": GOV_LEGEND,
    },
    "independent": {
        "title": "A View on America · Independent journalism on America",
        "meta": "Independent, nonprofit, reader-funded and investigative journalism on the United States, grouped by editorial orientation so you can read across viewpoints.",
        "tagline": "Independent and investigative journalism on America. Read across the spectrum.",
        "dateline_right": lambda n: f"Independent journalism · {n} viewpoints",
        "intro": ("Beyond the big outlets sit <b>independent, nonprofit, reader-funded and investigative</b> "
                  "newsrooms, the kind with more room for critical thinking and adversarial reporting. Sources "
                  "are grouped by editorial orientation so you can read <b>across</b> viewpoints rather than "
                  "inside one. Independent media leans left worldwide, so libertarian, conservative and "
                  "heterodox voices are included on purpose for balance. Heterodox here means outlets that break from the usual left-versus-right script and question the mainstream consensus. The <b>in exile</b> group carries "
                  "diaspora outlets that report on authoritarian home countries, and on their dealings with "
                  "Washington, from abroad for safety."),
        "legend": IND_LEGEND,
    },
}

def render_page(data, kind):
    cfg = PAGES[kind]
    sections = "\n\n".join(render_section(c) for c in data["countries"])
    n = len(data["countries"])
    support = SUPPORTBOX if kind == "today" else ""
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
    <h1><a href="./">A View on America</a></h1>
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
{support}

{sections}

  <footer>
    <b>A View on America</b> · {esc(data["date_human"])} · <a href="./">World Press</a> · <a href="independent.html">Independent</a> · <a href="archive.html">Archive</a><br>
    <span class="support-line">A View on America is free and ad-free. <a href="https://paypal.me/McCracken365" target="_blank" rel="noopener">Chip in via PayPal</a> to help keep it that way.</span><br>
    Headlines and trademarks belong to their respective publishers, and we link to the originals. Translations and notes are our own. © 2026 A View on America. See <a href="about.html">About</a> for method and sources.
  </footer>
</div>
{SHARE_JS}
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
<title>Archive · A View on America</title>
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
    <b>A View on America</b> · <a href="./">World Press</a> · <a href="independent.html">Independent</a> · <a href="about.html">About</a><br>
    <span class="support-line">Free and ad-free. <a href="https://paypal.me/McCracken365" target="_blank" rel="noopener">Support via PayPal</a>.</span><br>
    A new edition is archived here automatically every morning.
  </footer>
</div>
{SHARE_JS}
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
