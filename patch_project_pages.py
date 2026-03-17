#!/usr/bin/env python3
"""
PATCH SCRIPT — Run locally in your amanuelagut.github.io repo root.

Usage:
  cd ~/amanuelagut.github.io
  python3 patch_project_pages.py

Reads each existing project page in /projects/, applies fixes
(SEO, toggle, bilingual labels, Coming Soon), preserving ALL content.
Skips 2025-capstone and 2025-rb1 (provided as new complete files).
"""
import os, re

PROJECTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projects")
SKIP = {"2025-capstone.html", "2025-rb1-biotech-food-security.html"}

SEO_DESCS = {
    "2025-rb2-portfolio-risk": "GARCH-based volatility modeling for agricultural commodity portfolio risk in Latin American emerging markets.",
    "2025-rb3-export-competitiveness": "Structural determinants of Colombian agricultural export competitiveness: logistics, exchange rate, and productivity.",
    "2024-capstone": "Python-based ARIMA forecasting models for agricultural commodity prices in Colombian and Latin American markets.",
    "2024-rb1-biotech-volatility": "Cross-country analysis of biotech seed adoption and agricultural price volatility in Latin America 2010-2024.",
    "2024-rb2-fred-automation": "Automating commodity price time-series analysis with Python and the FRED API.",
    "2024-rb3-macro-correlations": "Macroeconomic indicators and agricultural price correlations in Colombia 2015-2024.",
    "2023-capstone": "Interactive Power BI dashboard integrating currency risk, biotech trends, and trade geography for Colombian agriculture.",
    "2023-rb1-usdcop-powerbi": "Power BI visual analysis of USD/COP exchange rate risk and agricultural import cost dynamics.",
    "2023-rb2-biotech-latam": "Agricultural biotechnology adoption and crop yield patterns across Latin America 2015-2023.",
    "2023-rb3-trade-geography": "Geographic mapping of Colombia agricultural trade partnerships and flow patterns 2019-2023.",
    "2022-capstone": "Agricultural price risk in Colombia 2018-2022: volatility, correlation, and price transmission analysis.",
    "2022-rb1-oil-transport": "Statistical analysis of oil price shocks and agricultural transport costs in Colombia 2018-2022.",
    "2022-rb2-rice-prices": "Multiple regression analysis of price determinants in Colombian rice wholesale markets 2019-2022.",
    "2022-rb3-corn-transmission": "Corn price transmission from Chicago Board of Trade to Colombian wholesale markets 2018-2022.",
    "2021-capstone": "SQL-based analysis of structural patterns in Latin American agricultural trade networks 2015-2021.",
    "2021-rb1-export-evolution": "Evolution of Colombian agricultural exports to key trading partners 2015-2021.",
    "2021-rb2-latam-commodities": "Fastest-growing agricultural commodities in Latin American trade 2018-2021.",
    "2021-rb3-andean-grain": "Colombia share in regional Andean grain imports 2017-2021.",
    "2020-capstone": "Multi-market analysis of Colombian grain price dynamics during the COVID-19 pandemic 2018-2020.",
    "2020-rb1-frijol": "Frijol price volatility in Colombia main wholesale market during the first 6 months of COVID-19.",
    "2020-rb2-usdcop": "USD/COP exchange rate and grain import costs in Colombia during the COVID-19 shock 2018-2020.",
    "2020-rb3-ibague-bogota": "Regional grain wholesale price divergence between Ibague and Bogota during the COVID-19 pandemic.",
}

SECTION_BI = {
    "Research Question": "Pregunta de Investigación",
    "Data &amp; Sources": "Datos y Fuentes",
    "Methodology": "Metodología",
    "Key Finding": "Hallazgo Principal",
    "What I Learned": "Lo que Aprendí",
    "Limitation": "Limitación",
    "Deliverable": "Entregable",
}

LIM_TYPES = ["Scope Limitation","Data Limitation","Method Limitation",
             "Scope & Data Limitation","Scope & Method Limitation","Data & Method Limitation"]

def patch(filepath):
    fn = os.path.basename(filepath).replace(".html","")
    with open(filepath,"r",encoding="utf-8") as f: html = f.read()
    c = 0

    # 1. SEO
    if "og:title" not in html:
        tm = re.search(r"<title>(.*?)</title>",html)
        ct = tm.group(1).replace(" — Angie M. Gutierrez-Oviedo","") if tm else fn
        sd = SEO_DESCS.get(fn, ct[:160])
        seo = f'  <meta name="description" content="{sd}"/>\n  <meta property="og:title" content="{ct}"/>\n  <meta property="og:description" content="{sd}"/>\n  <meta property="og:type" content="article"/>\n  <meta property="og:url" content="https://amanuelagut.github.io/projects/{fn}.html"/>\n  <meta property="og:image" content="https://amanuelagut.github.io/assets/photo.png"/>\n  <meta name="twitter:card" content="summary_large_image"/>\n'
        html = html.replace('  <link rel="preconnect"', seo + '  <link rel="preconnect"', 1); c+=1

    # 2. Toggle button → show current language
    if 'onclick="toggleLang()">ES</button>' in html:
        html = html.replace('onclick="toggleLang()">ES</button>','id="langBtn" onclick="toggleLang()">EN</button>'); c+=1
    if 'id="langBtn"' not in html and 'class="lang-toggle"' in html:
        html = html.replace('class="lang-toggle"','class="lang-toggle" id="langBtn"',1); c+=1

    # 3. Toggle JS fix
    for old_js in [
        "document.querySelector('.lang-toggle').textContent = lang === 'en' ? 'ES' : 'EN';",
        "document.getElementById('langBtn').textContent = lang === 'en' ? 'ES' : 'EN';",
    ]:
        if old_js in html:
            html = html.replace(old_js, "document.getElementById('langBtn').textContent = lang === 'en' ? 'EN' : 'ES';"); c+=1

    # 4. Bilingual section titles
    for en,es in SECTION_BI.items():
        old = f'<div class="section-title">{en}</div>'
        if old in html:
            html = html.replace(old, f'<div class="section-title en">{en}</div>\n    <div class="section-title es" style="display:none">{es}</div>'); c+=1

    # 5. Bilingual abstract label
    old_a = '<div class="abstract-label">Abstract</div>'
    if old_a in html:
        html = html.replace(old_a, '<div class="abstract-label en">Abstract</div>\n    <div class="abstract-label es" style="display:none">Resumen</div>'); c+=1

    # 6. Bilingual finding label
    for v in ["Key Finding","Key Finding — Pending Real Data"]:
        old_f = f'<div class="finding-label">{v}</div>'
        if old_f in html:
            es_v = v.replace("Key Finding","Hallazgo Principal").replace("Pending Real Data","Datos Pendientes")
            html = html.replace(old_f, f'<div class="finding-label en">{v}</div>\n      <div class="finding-label es" style="display:none">{es_v}</div>'); c+=1

    # 7. Bilingual limitation label
    for lt in LIM_TYPES:
        old_l = f'<div class="limitation-label">{lt}</div>'
        if old_l in html:
            es_l = lt.replace("Scope","Alcance").replace("Data","Datos").replace("Method","Método").replace("Limitation","Limitación").replace(" & "," y ")
            html = html.replace(old_l, f'<div class="limitation-label en">{lt}</div>\n      <div class="limitation-label es" style="display:none">{es_l}</div>'); c+=1

    # 8. Coming Soon buttons
    html = re.sub(r'<a href="#" class="dl-btn primary">\s*(<svg[^>]*>.*?</svg>)\s*(.*?)\s*</a>',
        r'<span class="dl-btn" style="opacity:0.6;cursor:default;">\1 \2</span>', html, flags=re.DOTALL)
    html = re.sub(r'<a href="#" class="dl-btn">\s*(<svg[^>]*>.*?</svg>)\s*(.*?)\s*</a>',
        r'<span class="dl-btn" style="opacity:0.6;cursor:default;">\1 \2</span>', html, flags=re.DOTALL)

    # 9. Bilingual breadcrumb
    old_bc = '<a href="../projects.html">Research Projects</a>'
    if old_bc in html and 'Proyectos de Investigación' not in html:
        html = html.replace(old_bc, '<a href="../projects.html" class="en">Research Projects</a>\n    <a href="../projects.html" class="es" style="display:none">Proyectos de Investigación</a>'); c+=1

    with open(filepath,"w",encoding="utf-8") as f: f.write(html)
    return c

if __name__ == "__main__":
    if not os.path.isdir(PROJECTS_DIR):
        print(f"ERROR: {PROJECTS_DIR} not found. Run from repo root."); raise SystemExit(1)
    files = sorted(f for f in os.listdir(PROJECTS_DIR) if f.endswith(".html"))
    patched = skipped = 0
    for fn in files:
        if fn in SKIP: print(f"  SKIP  {fn}"); skipped+=1; continue
        n = patch(os.path.join(PROJECTS_DIR,fn))
        print(f"  ✓  {fn}  ({n} changes)"); patched+=1
    print(f"\nDone: {patched} patched, {skipped} skipped.\nCommit and push.")
