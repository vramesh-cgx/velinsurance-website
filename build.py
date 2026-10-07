#!/usr/bin/env python3
"""Builds the Velinsurance and Financial Services website into docs/ (served by GitHub Pages).

Edit page content in src/pages/<page>.html and styles in src/style.css, then run:  python3 build.py
Every page shares the header, footer and <head> below, so a menu or footer change is made once here.
"""
import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs"
SITE_URL = "https://www.velinsurance.com"

# The document upload assistant (Google Apps Script web app). Paste its /exec link here; while it is empty the
# Contact page shows WhatsApp and email instead of the upload chat.
UPLOAD_URL = "https://script.google.com/macros/s/AKfycbwNLHYYMK2hor5f8lopfKgBsCSR2THp9yQFdY89043Yjic8aBSzZw6LqEDC0bjFA_F2/exec"

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

INSURANCE_MENU = [("auto", "Auto"), ("homeowners", "Homeowners"), ("landlord", "Landlord"), ("umbrella", "Umbrella")]

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
    sub = "".join(f'<a href="{p}.html"{" class=on" if page == p else ""}>{label}</a>' for p, label in INSURANCE_MENU)
    ins_on = " on" if menu == "insurance" else ""
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap">
    <a href="index.html"><img alt="Velinsurance and Financial Services" src="images/logo.png" width="300" height="182"></a>
    <nav class="nav" aria-label="Main">
      {a("index", "Home")}
      <div class="dd" id="dd">
        <button class="dd-btn{ins_on}" id="dd-btn" type="button" aria-expanded="false" aria-controls="dd-menu">Insurance <span aria-hidden="true">&#9662;</span></button>
        <div class="dd-menu" id="dd-menu">{sub}</div>
      </div>
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
  const dd = document.getElementById('dd'), ddBtn = document.getElementById('dd-btn');
  ddBtn.addEventListener('click', () => {
    const open = !dd.classList.contains('open');
    dd.classList.toggle('open', open); ddBtn.setAttribute('aria-expanded', String(open));
  });
  document.addEventListener('click', e => {
    if (!dd.contains(e.target)) { dd.classList.remove('open'); ddBtn.setAttribute('aria-expanded', 'false'); }
  });

  // Contact page on phones: once the visitor is in the chat, size it to the visible screen (above the keyboard)
  // and keep its top at the top of the screen, so the keyboard can't push the chat away.
  const chat = document.querySelector('.upload-frame');
  if (chat) {
    const phone = () => innerWidth <= 820;
    const vv = window.visualViewport;
    let active = false;
    const fit = () => {
      if (!active || !phone()) { chat.style.height = ''; return; }
      chat.style.height = Math.max(340, Math.round((vv ? vv.height : innerHeight) - 8)) + 'px';
    };
    const align = () => {
      const top = chat.getBoundingClientRect().top - (vv ? vv.offsetTop : 0);
      if (Math.abs(top - 4) > 2) scrollBy(0, top - 4);
    };
    addEventListener('blur', () => {          // focus moved into the chat (a tap or click inside it)
      setTimeout(() => {
        if (document.activeElement !== chat || !phone()) return;
        active = true; fit(); align();
      }, 0);
    });
    if (vv) vv.addEventListener('resize', () => {   // keyboard opened or closed
      if (!active || !phone()) return;
      fit(); if (document.activeElement === chat) align();
    });
    addEventListener('resize', fit);
    // The browser also scrolls the page by itself when the chat moves to its next question; put the chat back,
    // unless the visitor scrolled the page themselves (their touches on the page outside the chat).
    let userScroll = 0, timer;
    ['touchmove', 'wheel', 'keydown'].forEach(t => addEventListener(t, () => { userScroll = Date.now(); }, { passive: true }));
    addEventListener('scroll', () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        if (active && phone() && document.activeElement === chat && Date.now() - userScroll > 800) align();
      }, 120);
    }, { passive: true });
  }
</script>"""

WAVE = """<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
  <linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#1747a6"/><stop offset=".6" stop-color="#3c9a3a"/><stop offset="1" stop-color="#8cc63f"/></linearGradient>
  <symbol id="wave" viewBox="0 0 1440 110" preserveAspectRatio="none"><path d="M0 70 C 360 0, 900 120, 1440 30 L1440 110 L0 110 Z" fill="#ffffff"/><path d="M0 70 C 360 0, 900 120, 1440 30" fill="none" stroke="url(#g)" stroke-width="6"/></symbol>
  <symbol id="i-car" viewBox="0 0 48 48"><path d="M8 30v-6l4-10h24l4 10v6" fill="none" stroke="#1747a6" stroke-width="3" stroke-linejoin="round"/><rect x="6" y="24" width="36" height="10" rx="3" fill="#3c9a3a"/><circle cx="14" cy="36" r="4" fill="#0b2545"/><circle cx="34" cy="36" r="4" fill="#0b2545"/></symbol>
  <symbol id="i-home" viewBox="0 0 48 48"><path d="M6 24 24 8l18 16" fill="none" stroke="#3c9a3a" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M11 22v18h26V22" fill="none" stroke="#1747a6" stroke-width="3"/><rect x="20" y="27" width="8" height="8" fill="#1747a6"/></symbol>
  <symbol id="i-key" viewBox="0 0 48 48"><circle cx="16" cy="24" r="8" fill="none" stroke="#1747a6" stroke-width="3.5"/><path d="M24 24h18M36 24v7M41 24v5" stroke="#3c9a3a" stroke-width="3.5" stroke-linecap="round"/></symbol>
  <symbol id="i-umb" viewBox="0 0 48 48"><path d="M4 24a20 18 0 0 1 40 0Z" fill="#3c9a3a"/><path d="M4 24a20 18 0 0 1 20-18v18Z" fill="#1747a6"/><path d="M24 24v14a4 4 0 0 1-8 0" fill="none" stroke="#f2b705" stroke-width="3" stroke-linecap="round"/></symbol>
</defs></svg>"""


def upload_block():
    if UPLOAD_URL:
        return (f'<iframe class="upload-frame" src="{UPLOAD_URL}" title="Upload your policy documents" '
                'loading="lazy" allow="clipboard-write"></iframe>')
    return (f'<div class="upload-fallback"><h3>Send us your declarations page</h3>'
            f'<p>Send a photo or PDF of your current declarations page on WhatsApp or by email, and we will call you '
            f'within one business day.</p><div class="btns"><a class="btn primary" href="{WHATSAPP}">Send on WhatsApp</a>'
            f'<a class="btn outline" href="mailto:{EMAIL}?subject=Policy%20review">Email it</a></div></div>')


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
<link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@700;900&family=Montserrat:wght@500;600;700&family=Lato:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<script type="application/ld+json">{json.dumps(JSON_LD)}</script>
</head>
<body>
{WAVE}
{header(name, menu)}
<main id="main">
{body}</main>
{FOOTER}
{SCRIPT}
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
        body = body.replace("{{UPLOAD}}", upload_block())
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
