#!/usr/bin/env python3
"""Builds the Velinsurance and Financial Services website into docs/ (served by GitHub Pages).

Edit page content in src/pages/<page>.html and styles in src/style.css, then run:  python3 build.py
Every page shares the header, footer and <head> below, so a menu or footer change is made once here.
"""
import json
import pathlib
import re
import shutil
from urllib.parse import quote

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs"
SITE_URL = "https://www.velinsurance.com"

# The document upload assistant (Google Apps Script web app). Paste its /exec link here; while it is empty the
# Contact page shows WhatsApp and email instead of the upload chat.
UPLOAD_URL = "https://script.google.com/macros/s/AKfycbwNLHYYMK2hor5f8lopfKgBsCSR2THp9yQFdY89043Yjic8aBSzZw6LqEDC0bjFA_F2/exec"

# The chat's one-tap quote buttons. Each name must also be in START_LINES in the chat's Code.gs, or the chat asks again.
QUOTE_LINES = ["Home + Auto", "Auto", "Home", "Home + Auto + Landlord", "Landlord", "Pet", "Renters", "Umbrella", "Condo"]

# Home page "Start my quote" list: QUOTE_LINES start the chat; these open their own page. Placeholders until each page
# exists: an empty address texts the agency about that insurance instead.
LINK_LINES = {"Term Life Insurance": "", "Life Insurance": "", "Health Insurance": "", "Visitors Insurance": ""}

# Companies we quote with, shown as plain names (no logos). Keep to companies the agency is appointed with.
# Empty = the "Companies we quote include" row is left off every page. Hidden 2026-11-13 until each company approves
# being named; the list that was shown: Progressive, GEICO, National General, Foremost, Bristol West, American Modern,
# Orion180, Root.
CARRIERS = []

# The home page redesign (Design canvas "Velinsurance Website Redesign") uses Inter and Space Grotesk.
HOME_FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700'
              '&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">\n')

PHONE = "(770) 547-6030"
PHONE_E164 = "+17705476030"
EMAIL = "rameshv@velinsurance.com"
WHATSAPP = "https://wa.me/17705476030?text=I%20need%20an%20insurance%20quote"
CALENDAR = "https://calendar.app.google/kjZDW5A8bHQvBCos5"

PAGES = {  # file: (title, description, menu key)
    "index": ("Velinsurance and Financial Services | Independent insurance agency in Cumming, GA",
              "Independent insurance agency in Cumming, Georgia. Send your declarations page and we compare home, auto, "
              "landlord and umbrella insurance from several companies.", "home"),
    "auto": ("Auto insurance in Georgia | Velinsurance and Financial Services",
             "Car insurance for every driver and vehicle in your household, quoted with the same coverage across "
             "several insurance companies.", "insurance"),
    "homeowners": ("Homeowners insurance in Georgia | Velinsurance and Financial Services",
                   "Homeowners, condo and renters insurance for Forsyth, Gwinnett and the rest of Georgia, priced on "
                   "what it costs to rebuild.", "insurance"),
    "landlord": ("Landlord insurance in Georgia | Velinsurance and Financial Services",
                 "Dwelling (landlord) insurance for homes you rent out: loss of rent, landlord liability and the "
                 "building itself.", "insurance"),
    "umbrella": ("Umbrella insurance in Georgia | Velinsurance and Financial Services",
                 "An extra $1 million or more of liability above your home and auto limits.", "insurance"),
    "commercial": ("Commercial insurance in Georgia | Velinsurance and Financial Services",
                   "General liability, business owner's policies, commercial auto and workers' compensation for "
                   "Georgia small businesses.", "insurance"),
    "about": ("About us | Velinsurance and Financial Services",
              "A local, independent property and casualty agency in Cumming, Georgia. Georgia agency license #245535.",
              "about"),
    "contact": ("Free policy review | Velinsurance and Financial Services",
                "Upload your declarations page for a free policy review, or reach us on WhatsApp, phone or email.",
                "contact"),
}

# Old Google Sites addresses, so links people saved or Google indexed still work.
REDIRECTS = {"home": "index", "services": "index", "services/auto": "auto", "services/home": "homeowners",
             "services/umbrella": "umbrella"}

INSURANCE_MENU = [("auto", "Auto"), ("homeowners", "Home"), ("landlord", "Landlord"), ("umbrella", "Umbrella"),
                  ("commercial", "Commercial")]

JSON_LD = {
    "@context": "https://schema.org", "@type": "InsuranceAgency",
    "name": "Velinsurance and Financial Services LLC", "url": SITE_URL + "/",
    "logo": SITE_URL + "/images/logo.png", "telephone": PHONE_E164, "email": EMAIL,
    "address": {"@type": "PostalAddress", "addressLocality": "Cumming", "addressRegion": "GA",
                "postalCode": "30041", "addressCountry": "US"},
    "areaServed": "Georgia",
}


def header(page, menu):
    def a(target, label):
        on = ' class="on" aria-current="page"' if page == target else ""
        return f'<a href="{target}.html"{on}>{label}</a>'
    return f"""<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap">
  <span class="where">Independent agency in Cumming, Georgia &middot; GA license #245535</span>
  <span class="links"><a href="tel:{PHONE_E164}">{PHONE}</a><a href="mailto:{EMAIL}">{EMAIL}</a></span>
</div></div>
<header class="site-head">
  <div class="wrap">
    <a href="index.html" aria-label="Home"><img alt="Velinsurance and Financial Services" src="images/logo.png" width="300" height="182"></a>
    <nav class="nav" aria-label="Main">
      {"".join(a(p, label) for p, label in INSURANCE_MENU)}
      {a("about", "About")}{a("contact", "Contact")}
      <a class="btn primary" href="contact.html" style="padding:10px 16px">Free policy review</a>
    </nav>
  </div>
</header>"""


FOOTER = f"""<footer class="site-foot">
  <div class="wrap">
    <div class="foot-grid">
      <div class="stack">
        <h4>Velinsurance and Financial Services LLC</h4>
        <p>Independent home, auto, landlord and umbrella insurance for Georgia families.</p>
        <p>Cumming, GA 30041</p>
      </div>
      <div class="stack"><h4>Insurance</h4>{"".join(f'<a href="{p}.html">{label}</a>' for p, label in INSURANCE_MENU)}</div>
      <div class="stack"><h4>Contact</h4><a href="{WHATSAPP}">WhatsApp {PHONE}</a><a href="mailto:{EMAIL}">{EMAIL}</a><a href="{CALENDAR}">Book a call</a></div>
    </div>
    <p class="fine">Georgia property and casualty agency license #245535. Coverage is subject to each insurance company's terms and approval. &copy; 2026 Velinsurance and Financial Services LLC.</p>
  </div>
</footer>"""

SCRIPT = """<script>
  // Contact page on phones: the chat is a full-screen panel kept the size of the visible screen -- the part above
  // the keyboard when it is open (visualViewport) -- so the question and the text box always fit on one screen.
  // Only the panel's top and height change; the page itself is locked and never scrolled by this script.
  const chat = document.querySelector('.upload-frame');
  if (chat) {
    const box = document.querySelector('.upload-page');
    const phone = matchMedia('(max-width: 820px)');
    const vv = window.visualViewport;
    const fit = () => {
      document.documentElement.classList.toggle('chat-full', phone.matches);
      if (!phone.matches || !vv) { box.style.top = box.style.height = ''; return; }
      box.style.top = Math.max(0, vv.offsetTop) + 'px';
      box.style.height = Math.round(vv.height) + 'px';
    };
    fit();
    phone.addEventListener('change', fit);
    if (vv) { vv.addEventListener('resize', fit); vv.addEventListener('scroll', fit); }
    chat.loading = 'eager';
  }
</script>"""

WAVE = """<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
  <linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#032c69"/><stop offset=".5" stop-color="#0069aa"/><stop offset="1" stop-color="#4da618"/></linearGradient>
  <symbol id="wave" viewBox="0 0 1440 120" preserveAspectRatio="none"><path d="M0 106 C 480 106 1000 78 1440 18 L1440 120 L0 120 Z" fill="currentColor"/><path d="M0 88 C 480 88 1000 50 1440 0 L1440 18 C 1000 78 480 106 0 106 Z" fill="url(#g)"/></symbol>
  <symbol id="i-car" viewBox="0 0 48 48"><path d="M8 30v-6l4-10h24l4 10v6" fill="none" stroke="#0069aa" stroke-width="3" stroke-linejoin="round"/><rect x="6" y="24" width="36" height="10" rx="3" fill="#4da618"/><circle cx="14" cy="36" r="4" fill="#032c69"/><circle cx="34" cy="36" r="4" fill="#032c69"/></symbol>
  <symbol id="i-home" viewBox="0 0 48 48"><path d="M6 24 24 8l18 16" fill="none" stroke="#4da618" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M11 22v18h26V22" fill="none" stroke="#0069aa" stroke-width="3"/><rect x="20" y="27" width="8" height="8" fill="#0069aa"/></symbol>
  <symbol id="i-key" viewBox="0 0 48 48"><circle cx="16" cy="24" r="8" fill="none" stroke="#0069aa" stroke-width="3.5"/><path d="M24 24h18M36 24v7M41 24v5" stroke="#4da618" stroke-width="3.5" stroke-linecap="round"/></symbol>
  <symbol id="i-biz" viewBox="0 0 48 48"><rect x="8" y="12" width="20" height="28" fill="none" stroke="#0069aa" stroke-width="3"/><rect x="28" y="20" width="12" height="20" fill="#4da618"/><path d="M14 18h8M14 24h8M14 30h8" stroke="#0069aa" stroke-width="3"/><path d="M4 40h40" stroke="#032c69" stroke-width="3" stroke-linecap="round"/></symbol>
  <symbol id="i-umb" viewBox="0 0 48 48"><path d="M4 24a20 18 0 0 1 40 0Z" fill="#4da618"/><path d="M4 24a20 18 0 0 1 20-18v18Z" fill="#0069aa"/><path d="M24 24v14a4 4 0 0 1-8 0" fill="none" stroke="#e3b306" stroke-width="3" stroke-linecap="round"/></symbol>
</defs></svg>"""


def upload_block():
    if UPLOAD_URL:
        return (f'<iframe class="upload-frame" src="{UPLOAD_URL}" title="Upload your policy documents" '
                'loading="lazy" allow="clipboard-write"></iframe>')
    return (f'<div class="upload-fallback"><h3>Send us your declarations page</h3>'
            f'<p>Send a photo or PDF of your current declarations page on WhatsApp or by email, and we will call you '
            f'within one business day.</p><div class="btns"><a class="btn primary" href="{WHATSAPP}">Send on WhatsApp</a>'
            f'<a class="btn outline" href="mailto:{EMAIL}?subject=Policy%20review">Email it</a></div></div>')


def quote_block(line=""):
    """The quote chat inside a page (home, auto, landlord pages). line skips the chat's first question."""
    if not UPLOAD_URL:
        return upload_block()
    src = UPLOAD_URL + (f"?line={quote(line)}" if line else "")
    return (f'<div class="quote-box"><iframe class="quote-frame" id="quote-frame" src="{src}" '
            f'title="Get a quote" loading="lazy" allow="clipboard-write"></iframe>'
            f'<p class="no-sell"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 5 6v5c0 4.5 3 8.4 7 10 4-1.6 7-5.5 7-10V6Z" '
            f'fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="m9 12 2 2 4-4" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
            f'Only Velinsurance will contact you. We never sell your information.</p></div>')


def quote_options():
    chat = "".join(f'<a class="rd-opt" data-line="{l}" href="contact.html?line={quote(l)}">{l}</a>' for l in QUOTE_LINES)
    def link(label, url):
        if url:
            return f'<a class="rd-opt" href="{url}">{label}</a>'
        body = quote(f"Hi, I'd like a quote for {label.lower()}")
        return f'<a class="rd-opt" href="sms:{PHONE_E164}?&amp;body={body}">{label}</a>'
    return f'<div class="rd-opt-grid">{chat}{"".join(link(k, v) for k, v in LINK_LINES.items())}</div>'


def carriers_block():
    if not CARRIERS:
        return ""
    return ('<div class="carrier-row"><span class="eyebrow">Companies we quote include</span><div class="carriers">'
            + "".join(f"<span>{c}</span>" for c in CARRIERS) + '<span class="more">and others</span></div></div>')


def track_script(page):
    """Counts visits, where visitors came from and button taps, in the agency's Google Drive (the upload assistant's
    doPost). No cookies and nothing personal: a page name, a source word such as "google", and which button.
    The source is worked out once per visit and kept in sessionStorage so the chat can be told it too."""
    return f"""<script>
  (() => {{
    const URL_ = {json.dumps(UPLOAD_URL)};
    const host = h => {{ try {{ return new URL(h).hostname; }} catch (e) {{ return ''; }} }};
    const classify = () => {{
      const utm = (new URLSearchParams(location.search).get('utm_source') || '').toLowerCase();
      if (utm) return utm;
      const h = host(document.referrer);
      if (!h || h === location.hostname) return 'direct';
      const known = [[/(^|\\.)google\\./, 'google'], [/bing\\./, 'bing'], [/yahoo\\./, 'yahoo'], [/duckduckgo/, 'duckduckgo'],
        [/facebook|fb\\.|messenger/, 'facebook'], [/instagram/, 'instagram'], [/nextdoor/, 'nextdoor'], [/yelp/, 'yelp'],
        [/linkedin|lnkd/, 'linkedin'], [/chatgpt|openai|perplexity|claude\\.ai|gemini|copilot/, 'ai-chat']];
      for (const [re, name] of known) if (re.test(h)) return name;
      return 'referral';
    }};
    let src = null, first = false;
    try {{ src = sessionStorage.getItem('vel-src'); }} catch (e) {{}}
    if (!src) {{ first = true; src = classify(); try {{ sessionStorage.setItem('vel-src', src); }} catch (e) {{}} }}
    window.VEL_SRC = src;
    if (!URL_ || navigator.webdriver || !navigator.sendBeacon) return;   // no counting for test robots
    const send = q => {{ try {{ navigator.sendBeacon(URL_ + '?' + new URLSearchParams(q), ''); }} catch (e) {{}} }};
    send({{ ev: 'visit', p: {json.dumps(page)}, new: first ? '1' : '0', src }});
    document.addEventListener('click', e => {{
      const a = e.target.closest('a, button');
      if (!a) return;
      const href = a.getAttribute('href') || '';
      const k = a.dataset.track || (href.startsWith('tel:') ? 'call' : href.startsWith('sms:') ? 'text' :
        href.includes('calendar.app.google') ? 'book' : '');
      if (k) send({{ ev: 'click', k }});
    }}, true);
  }})();
</script>"""


def quote_script():
    """Quote buttons (a[data-line]): restart the chat on this page with that choice, or, on pages without the chat,
    open the Contact page with it. The Contact page passes ?line= on to its chat."""
    return f"""<script>
  (() => {{
    const URL_ = {json.dumps(UPLOAD_URL)}, LINES = {json.dumps(QUOTE_LINES)};
    const src = line => {{
      const q = new URLSearchParams();
      if (LINES.includes(line)) q.set('line', line);
      if (window.VEL_SRC) q.set('src', window.VEL_SRC);   // where the visitor came from, counted with the lead
      return URL_ + (q.toString() ? '?' + q : '');
    }};
    const frame = document.getElementById('quote-frame');
    // tell the chat where this visitor came from (the iframes load lazily, so this lands before they load)
    document.querySelectorAll('.quote-frame, .upload-frame').forEach(f => {{
      if (!URL_ || !window.VEL_SRC) return;
      const line = new URL(f.src).searchParams.get('line');
      f.src = src(line);
    }});
    document.querySelectorAll('a[data-line]').forEach(a => a.addEventListener('click', e => {{
      if (!frame || !URL_) return;   // no chat on this page: follow the link to the Contact page
      e.preventDefault();
      frame.src = src(a.dataset.line);
      frame.closest('section').scrollIntoView({{ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' }});
    }}));
    const contact = document.querySelector('.upload-frame');
    const line = new URLSearchParams(location.search).get('line');
    if (contact && URL_ && LINES.includes(line)) contact.src = src(line);
  }})();
</script>"""


def page_html(name, title, desc, menu, body):
    canonical = SITE_URL + "/" + ("" if name == "index" else name)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE_URL}/images/photo-homeowners.jpg">
<meta property="og:type" content="website">
<link rel="icon" href="images/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=Figtree:wght@400;500;600;700&display=swap" rel="stylesheet">
{HOME_FONTS if name == "index" else ""}<link rel="stylesheet" href="style.css">
<script type="application/ld+json">{json.dumps(JSON_LD)}</script>
</head>
<body>
{WAVE}
{header(name, menu)}
<main id="main">
{body}</main>
{FOOTER}
{SCRIPT}
{track_script(name)}
{quote_script()}
</body>
</html>
"""


def redirect_html(depth, target):
    up = "../" * depth
    return (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Moved</title>'
            f'<link rel="canonical" href="{SITE_URL}/{"" if target == "index" else target}">'
            f'<meta http-equiv="refresh" content="0; url={up}{target}.html"></head>'
            f'<body><a href="{up}{target}.html">This page has moved.</a></body></html>\n')


def main():
    OUT.mkdir(exist_ok=True)
    shutil.copy(ROOT / "src" / "style.css", OUT / "style.css")
    for name, (title, desc, menu) in PAGES.items():
        body = (ROOT / "src" / "pages" / f"{name}.html").read_text()
        body = body.replace("{{UPLOAD}}", upload_block()).replace("{{CARRIERS}}", carriers_block())\
            .replace("{{QUOTE_OPTIONS}}", quote_options())
        body = re.sub(r"\{\{QUOTE(?::([^}]*))?\}\}", lambda m: quote_block(m.group(1) or ""), body)
        (OUT / f"{name}.html").write_text(page_html(name, title, desc, menu, body))
    for old, new in REDIRECTS.items():
        path = OUT / f"{old}.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(redirect_html(old.count("/"), new))
    (OUT / ".nojekyll").write_text("")
    (OUT / "CNAME").write_text(SITE_URL.split("//")[1] + "\n")   # custom domain for GitHub Pages
    urls = "".join(f"<url><loc>{SITE_URL}/{'' if n == 'index' else n}</loc></url>" for n in PAGES)
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                     f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    print("built", len(PAGES), "pages into", OUT)


if __name__ == "__main__":
    main()
