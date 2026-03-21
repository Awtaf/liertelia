#!/usr/bin/env python3
"""Complete HTML generator for Telia Drammen dashboard.
Reads data from JSON files and generates a single HTML file.
FULLY DYNAMIC: auto-detects months with data, current month, work days, etc."""

import json, math, os
from datetime import date

# === LOAD DATA ===
with open('/tmp/complete_extracted_data.json', 'r') as f:
    extracted = json.load(f)

with open('/tmp/budgets.json', 'r') as f:
    budgets = json.load(f)

# === CONFIGURATION ===
STORES = {
    'gulskogen': {'name': 'Gulskogen', 'color': '#00BFFF', 'emoji': '🏬'},
    'liertoppen': {'name': 'Liertoppen', 'color': '#990AE3', 'emoji': '🏪'},
    'buskerud': {'name': 'Buskerud', 'color': '#FF6B35', 'emoji': '🏢'},
}

MONTHS_2026 = ['jan', 'feb', 'mar', 'apr', 'mai', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'des']
MONTH_NAMES = {'jan': 'Januar', 'feb': 'Februar', 'mar': 'Mars', 'apr': 'April', 'mai': 'Mai', 'jun': 'Juni',
               'jul': 'Juli', 'aug': 'August', 'sep': 'September', 'okt': 'Oktober', 'nov': 'November', 'des': 'Desember'}
MONTH_NUMBERS = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'mai': 5, 'jun': 6,
                 'jul': 7, 'aug': 8, 'sep': 9, 'okt': 10, 'nov': 11, 'des': 12}

# === AUTO-DETECT MONTHS WITH DATA ===
# Check which months have sellers in any store
MONTHS_WITH_DATA = []
for m in MONTHS_2026:
    has_data = False
    for store_id in STORES:
        sellers = extracted.get(store_id, {}).get(m, {}).get('sellers', [])
        if sellers:
            has_data = True
            break
    if has_data:
        MONTHS_WITH_DATA.append(m)

# Auto-detect current month: use /tmp/current_month.txt if it exists, otherwise latest month with data
if os.path.exists('/tmp/current_month.txt'):
    with open('/tmp/current_month.txt', 'r') as f:
        CURRENT_MONTH = f.read().strip()
elif MONTHS_WITH_DATA:
    CURRENT_MONTH = MONTHS_WITH_DATA[-1]  # latest month with data
else:
    CURRENT_MONTH = 'jan'

# Use today's real date
TODAY = date.today()

# Calculate work days dynamically for the current month
WORK_DAYS_TOTAL = 22
current_month_num = MONTH_NUMBERS.get(CURRENT_MONTH, TODAY.month)
current_year = 2026

work_days_passed = 0
for d in range(1, TODAY.day + 1):
    try:
        dt = date(current_year, current_month_num, d)
        if dt.weekday() < 5:  # Mon-Fri
            work_days_passed += 1
    except ValueError:
        break
WORK_DAYS_REMAINING = max(WORK_DAYS_TOTAL - work_days_passed, 1)

# DATA_KEY_MAP: identity map (all keys are 3-letter abbreviations now)
DATA_KEY_MAP = {m: m for m in MONTHS_2026}

print(f"  Months with data: {MONTHS_WITH_DATA}")
print(f"  Current month: {CURRENT_MONTH}")
print(f"  Work days passed: {work_days_passed}, remaining: {WORK_DAYS_REMAINING}")

# === HELPER FUNCTIONS ===
def iv(v):
    try: return int(float(v)) if v else 0
    except: return 0

def fv(v):
    try: return float(v) if v else 0.0
    except: return 0.0

def format_kr(v):
    """Format kr amounts: 122k kr, 1.2M kr, 800 kr"""
    v = fv(v)
    if v >= 1000000:
        return f"{v/1000000:.1f}M kr"
    elif v >= 1000:
        return f"{round(v/1000)}k kr"
    else:
        return f"{int(v)} kr"

def format_num(v):
    """Format non-kr values (gross, upgrades etc): plain integers"""
    return str(iv(v))

def format_full(v):
    """Format with thousand separators: 244 000 kr"""
    v = iv(v)
    s = f"{abs(v):,}".replace(",", " ")
    return f"{'-' if v < 0 else ''}{s}"

def esc(s):
    """HTML escape"""
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", "&#39;")

# === COMPUTE STORE DATA ===
def compute_store_totals(sellers):
    """Compute aggregate KPIs from seller list"""
    totals = {'gross': 0, 'upgrades': 0, 'forsikring': 0, 'trygg': 0, 'tjenester': 0.0, 'tilbehor': 0.0, 'omsetning': 0.0}
    for s in sellers:
        totals['gross'] += iv(s.get('gross', 0))
        totals['upgrades'] += iv(s.get('upgr', s.get('upgrades', 0)))
        totals['forsikring'] += iv(s.get('forsikring', 0))
        totals['trygg'] += iv(s.get('trygg', 0))
        totals['tjenester'] += fv(s.get('tjenester', 0))
        totals['tilbehor'] += fv(s.get('tilbehor', 0))
    totals['omsetning'] = totals['tjenester'] + totals['tilbehor']
    return totals

def find_diploma_winners(sellers):
    """Find winners for each diploma category"""
    if not sellers:
        return {}
    
    categories = {
        'gross': ('📊 Gross Mester', 'gross', False),
        'upgrades': ('🔄 Upgrade Mester', lambda s: iv(s.get('upgr', s.get('upgrades', 0))), False),
        'trygg': ('🛡️ T.Trygg Mester', 'trygg', False),
        'forsikring': ('🔒 Forsikring Mester', 'forsikring', False),
        'tilbehor': ('🎧 Tilbehør Mester', 'tilbehor', True),
        'tjenester': ('🛠️ Tjenester Mester', 'tjenester', True),
    }
    
    winners = {}
    for key, (title, field, is_kr) in categories.items():
        if callable(field):
            best = max(sellers, key=field)
            val = field(best)
        else:
            best = max(sellers, key=lambda s: fv(s.get(field, 0)))
            val = fv(best.get(field, 0))
        
        winners[key] = {
            'title': title,
            'name': best.get('navn', '?'),
            'stilling': best.get('stilling', ''),
            'value': format_kr(val) if is_kr else format_num(val),
            'raw_value': val,
        }
    return winners

# Pre-compute all data
store_data = {}
for store_id, store_info in STORES.items():
    store_data[store_id] = {}
    
    # 2025 YTD
    ytd_sellers = extracted[store_id]['ytd_2025']['sellers']
    store_data[store_id]['ytd_2025'] = {
        'sellers': sorted(ytd_sellers, key=lambda s: fv(s.get('gross', 0)), reverse=True),
        'totals': compute_store_totals(ytd_sellers),
        'diplomas': find_diploma_winners(ytd_sellers),
    }
    
    # Monthly data
    for month in MONTHS_WITH_DATA:
        data_key = DATA_KEY_MAP[month]
        month_sellers = extracted[store_id][data_key]['sellers']
        store_data[store_id][month] = {
            'sellers': sorted(month_sellers, key=lambda s: fv(s.get('gross', 0)), reverse=True),
            'totals': compute_store_totals(month_sellers),
            'diplomas': find_diploma_winners(month_sellers),
        }

# === CSS ===
CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#080818; color:#fff; font-family:'Segoe UI',system-ui,-apple-system,sans-serif; }
.page { display:none; }
.page.active { display:block; }

/* Navbar */
.nav { position:sticky; top:0; z-index:100; background:rgba(8,8,24,0.95); backdrop-filter:blur(12px);
  padding:12px 20px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.1); }
.nav .logo { font-size:1.1rem; font-weight:700; cursor:pointer; background:linear-gradient(135deg,#00BFFF,#990AE3);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.nav .hbtn { background:rgba(255,255,255,0.1); border:none; color:#fff; padding:8px 16px;
  border-radius:8px; cursor:pointer; font-size:0.85rem; }
.nav .hbtn:hover { background:rgba(255,255,255,0.2); }

/* Hero */
.hero { text-align:center; padding:40px 20px 20px; }
.hero h1 { font-size:2.2rem; background:linear-gradient(135deg,#00BFFF,#990AE3,#FF6B35);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.hero p { color:rgba(255,255,255,0.5); margin-top:4px; }

/* Section */
.sec { padding:16px 20px 8px; font-size:1rem; font-weight:600; color:rgba(255,255,255,0.7); }
.container { padding:0 16px; }

/* Store cards on home */
.store-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; padding:12px 16px; }
@media(max-width:700px) { .store-grid { grid-template-columns:1fr; } }
.sc { background:rgba(255,255,255,0.05); border-radius:16px; padding:20px; cursor:pointer;
  border:1px solid rgba(255,255,255,0.08); transition:all .3s; }
.sc:hover { transform:translateY(-4px); border-color:rgba(255,255,255,0.2); background:rgba(255,255,255,0.08); }
.sc .sn { font-size:1.1rem; font-weight:700; margin-bottom:12px; }
.sc .si { display:flex; justify-content:space-between; margin-top:6px; font-size:0.85rem; color:rgba(255,255,255,0.6); }
.sc .sv { font-weight:600; color:#fff; }
.sc .pct { font-size:1.8rem; font-weight:800; margin:8px 0; }
.sc .daily { font-size:0.85rem; color:rgba(255,255,255,0.5); }

/* KPI grid */
.kpi-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:10px; padding:12px 16px; }
.kc { background:rgba(255,255,255,0.05); border-radius:12px; padding:16px; text-align:center;
  border:1px solid rgba(255,255,255,0.06); }
.kl { font-size:0.75rem; color:rgba(255,255,255,0.5); margin-bottom:4px; text-transform:uppercase; }
.kv { font-size:1.4rem; font-weight:700; }

/* Tabs */
.tabs { display:flex; gap:8px; padding:12px 16px; }
.tab { padding:10px 24px; border-radius:10px; border:1px solid rgba(255,255,255,0.1);
  background:rgba(255,255,255,0.05); color:rgba(255,255,255,0.6); cursor:pointer; font-weight:600; font-size:0.9rem; }
.tab.active { background:linear-gradient(135deg,rgba(0,191,255,0.2),rgba(153,10,227,0.2));
  border-color:rgba(0,191,255,0.4); color:#fff; }
.tcontent { display:none; }
.tcontent.active { display:block; }

/* Month grid */
.mnd-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; padding:12px 16px; }
@media(max-width:600px) { .mnd-grid { grid-template-columns:repeat(2,1fr); } }
.mc { border-radius:12px; padding:16px; text-align:center; border:1px solid rgba(255,255,255,0.08); }
.mc-open { background:rgba(255,255,255,0.06); cursor:pointer; transition:all .3s; }
.mc-open:hover { transform:translateY(-2px); background:rgba(255,255,255,0.1); }
.mc-locked { background:rgba(255,255,255,0.02); opacity:0.4; }
.mc .mn { font-weight:700; font-size:0.95rem; margin-bottom:6px; }
.mc .mi { font-size:0.8rem; color:rgba(255,255,255,0.5); margin-top:4px; }

/* Month detail */
.mnd-detail { display:none; }

/* Back button */
.back { display:inline-flex; align-items:center; gap:6px; color:rgba(255,255,255,0.6); cursor:pointer;
  padding:12px 16px; font-size:0.9rem; }
.back:hover { color:#fff; }

/* Diploma grid */
.dip-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; padding:12px 16px; }
@media(max-width:700px) { .dip-grid { grid-template-columns:repeat(2,1fr); } }
.dip { border-radius:14px; padding:16px; text-align:center; border:1px solid rgba(255,255,255,0.1);
  background:rgba(255,255,255,0.04); }
.dt { font-size:0.8rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; }
.dline { height:2px; margin:8px auto; width:40px; border-radius:2px; }
.dname { font-size:1rem; font-weight:700; margin:4px 0; }
.drole { font-size:0.75rem; color:rgba(255,255,255,0.4); margin-bottom:6px; }
.dval { font-size:1.3rem; font-weight:800; }

/* Bars */
.bars { padding:12px 16px; }
.bar-row { display:flex; align-items:center; margin-bottom:8px; gap:10px; }
.bar-name { width:140px; font-size:0.8rem; text-align:right; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.bar-wrap { flex:1; background:rgba(255,255,255,0.06); border-radius:6px; height:28px; overflow:hidden; }
.bar { height:100%; border-radius:6px; display:flex; align-items:center; padding-left:10px;
  font-size:0.75rem; font-weight:700; min-width:30px; transition:width .5s; }
.bar-val { width:50px; font-size:0.8rem; font-weight:600; text-align:right; }

/* Seller table */
.tbl-wrap { padding:12px 16px; overflow-x:auto; }
table { width:100%; border-collapse:collapse; font-size:0.82rem; }
thead { position:sticky; top:0; }
th { background:rgba(255,255,255,0.08); padding:10px 8px; text-align:left; font-weight:600;
  font-size:0.7rem; text-transform:uppercase; color:rgba(255,255,255,0.5); }
td { padding:10px 8px; border-bottom:1px solid rgba(255,255,255,0.04); }
tr:hover { background:rgba(255,255,255,0.03); }
.rk { display:inline-flex; align-items:center; justify-content:center; width:24px; height:24px;
  border-radius:50%; font-size:0.7rem; font-weight:700; }
.rk1 { background:linear-gradient(135deg,#FFD700,#FFA500); color:#000; }
.rk2 { background:linear-gradient(135deg,#C0C0C0,#A0A0A0); color:#000; }
.rk3 { background:linear-gradient(135deg,#CD7F32,#A0522D); color:#fff; }
.rkn { background:rgba(255,255,255,0.1); color:rgba(255,255,255,0.5); }
.stag { font-size:0.7rem; padding:2px 8px; border-radius:4px; background:rgba(255,255,255,0.08); }
.nlink { cursor:pointer; font-weight:600; }
.nlink:hover { text-decoration:underline; }
.big { font-weight:600; }

/* Store page header */
.store-header { padding:20px 20px 0; }
.store-header h2 { font-size:1.8rem; font-weight:800; }

/* Profile page */
#profile { padding:20px; }
.prof-name { font-size:1.5rem; font-weight:800; margin-bottom:4px; }
.prof-role { color:rgba(255,255,255,0.5); margin-bottom:16px; }

/* 2025 summary on home */
.summary-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(120px,1fr)); gap:10px; padding:12px 16px; }

/* Year selection on home */
.year-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:16px; padding:16px 16px; max-width:600px; margin:0 auto; }
.year-card { background:rgba(255,255,255,0.05); border-radius:20px; padding:40px 24px; text-align:center;
  cursor:pointer; border:2px solid rgba(255,255,255,0.1); transition:all .3s; }
.year-card:hover { transform:translateY(-6px); border-color:rgba(255,255,255,0.3); background:rgba(255,255,255,0.1); }
.year-card .ynum { font-size:2.5rem; font-weight:900; margin-bottom:8px; }
.year-card .ysub { font-size:0.85rem; color:rgba(255,255,255,0.5); }
.year-card.y2025 { border-color:rgba(0,191,255,0.3); }
.year-card.y2025:hover { border-color:rgba(0,191,255,0.6); background:rgba(0,191,255,0.08); }
.year-card.y2025 .ynum { background:linear-gradient(135deg,#00BFFF,#00FF88); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.year-card.y2026 { border-color:rgba(153,10,227,0.3); }
.year-card.y2026:hover { border-color:rgba(153,10,227,0.6); background:rgba(153,10,227,0.08); }
.year-card.y2026 .ynum { background:linear-gradient(135deg,#990AE3,#FF6B35); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
"""

# === HTML GENERATION FUNCTIONS ===

def gen_kpi_card(label, value, color='#fff'):
    return f'<div class="kc"><div class="kl">{label}</div><div class="kv" style="color:{color}">{value}</div></div>'

def gen_kpi_grid(totals, store_color, show_budget=False, budget=0, oppnaaelse=0, daglig_maal=0):
    cards = []
    cards.append(gen_kpi_card('Total Gross', format_num(totals['gross']), store_color))
    cards.append(gen_kpi_card('Upgrades', format_num(totals['upgrades']), '#FFD700'))
    cards.append(gen_kpi_card('Forsikring', format_num(totals['forsikring']), '#FF6B6B'))
    cards.append(gen_kpi_card('Telia Trygg', format_num(totals['trygg']), '#C44DFF'))
    cards.append(gen_kpi_card('Omsetning', format_kr(totals['omsetning']), '#00FF88'))
    cards.append(gen_kpi_card('Tilbehør', format_kr(totals['tilbehor']), '#00BFFF'))
    cards.append(gen_kpi_card('Tjenester', format_kr(totals['tjenester']), '#00FF88'))
    if show_budget:
        cards.append(gen_kpi_card('Oppnåelse', f'{oppnaaelse:.0f}%', '#FFD700'))
        cards.append(gen_kpi_card('Daglig mål', f'{daglig_maal:.1f}', '#FF6B6B'))
    return f'<div class="kpi-grid">{"".join(cards)}</div>'

def gen_diploma_grid(diplomas, store_color):
    if not diplomas:
        return ''
    
    colors = {
        'gross': store_color,
        'upgrades': '#FFD700',
        'trygg': '#C44DFF',
        'forsikring': '#FF6B6B',
        'tilbehor': '#00BFFF',
        'tjenester': '#00FF88',
    }
    
    cards = []
    for key in ['gross', 'upgrades', 'trygg', 'forsikring', 'tilbehor', 'tjenester']:
        d = diplomas.get(key)
        if not d:
            continue
        c = colors.get(key, store_color)
        cards.append(f'''<div class="dip" style="border-color:{c}40">
<div class="dt" style="color:{c}">{d['title']}</div>
<div class="dline" style="background:{c}"></div>
<div class="dname">{esc(d['name'])}</div>
<div class="drole">{esc(d['stilling'])}</div>
<div class="dval" style="color:{c}">{d['value']}</div>
</div>''')
    
    return f'<div class="sec">🏆 Diplomer</div>\n<div class="dip-grid">{"".join(cards)}</div>'

def gen_bars(sellers, store_color):
    if not sellers:
        return ''
    max_gross = max(fv(s.get('gross', 0)) for s in sellers) if sellers else 1
    if max_gross == 0:
        max_gross = 1
    
    rows = []
    for s in sellers:
        g = iv(s.get('gross', 0))
        pct = (g / max_gross) * 100
        rows.append(f'''<div class="bar-row">
<div class="bar-name">{esc(s.get('navn', '?'))}</div>
<div class="bar-wrap"><div class="bar" style="width:{max(pct,3):.0f}%;background:{store_color}">{g}</div></div>
<div class="bar-val">{g}</div>
</div>''')
    
    return f'<div class="sec">📊 Gross per selger</div>\n<div class="bars">{"".join(rows)}</div>'

def gen_seller_table(sellers, store_id, period_suffix):
    if not sellers:
        return ''
    
    rows = []
    for i, s in enumerate(sellers):
        rank_class = ['rk1', 'rk2', 'rk3'][i] if i < 3 else 'rkn'
        rank_icon = '👑' if i == 0 else str(i + 1)
        name = esc(s.get('navn', '?'))
        stilling = esc(s.get('stilling', ''))
        gross = iv(s.get('gross', 0))
        upgr = iv(s.get('upgr', s.get('upgrades', 0)))
        forsikr = iv(s.get('forsikring', 0))
        trygg = iv(s.get('trygg', 0))
        tilbehor = fv(s.get('tilbehor', 0))
        tjenester = fv(s.get('tjenester', 0))
        
        # Data attributes for profile
        data_attrs = (f'data-navn="{name}" data-stilling="{stilling}" '
                     f'data-gross="{gross}" data-upgr="{upgr}" data-trygg="{trygg}" '
                     f'data-forsikring="{forsikr}" data-tjenester="{tjenester}" '
                     f'data-tilbehor="{tilbehor}"')
        
        row_class = ['tg', 'ts', 'tb'][i] if i < 3 else ''
        
        rows.append(f'''<tr class="{row_class}">
<td><span class="rk {rank_class}">{rank_icon}</span></td>
<td><span class="nlink" onclick="showProf(this,'{store_id}_{period_suffix}')" {data_attrs}>{name}</span></td>
<td><span class="stag">{stilling}</span></td>
<td><span class="big">{gross}</span></td>
<td><span class="big">{upgr}</span></td>
<td><span class="big">{forsikr}</span></td>
<td><span class="big" style="color:#C44DFF">{trygg}</span></td>
<td><span class="big">{format_kr(tilbehor)}</span></td>
<td><span class="big">{format_kr(tjenester)}</span></td>
</tr>''')
    
    return f'''<div class="sec">📋 Selgertabell</div>
<div class="tbl-wrap"><table>
<thead><tr><th>#</th><th>Selger</th><th>Stilling</th><th>Gross</th><th>Upgr</th><th>Forsikr</th><th>Trygg</th><th>Tilbehør</th><th>Tjenester</th></tr></thead>
<tbody>{"".join(rows)}</tbody>
</table></div>'''

# === GENERATE STORE PAGE ===
def gen_store_page(store_id):
    info = STORES[store_id]
    color = info['color']
    name = info['name']
    data = store_data[store_id]
    
    # === 2025 TAB ===
    ytd = data['ytd_2025']
    tab_2025 = f'''<div id="{store_id}_2025_c" class="tcontent active">
{gen_kpi_grid(ytd['totals'], color)}
{gen_diploma_grid(ytd['diplomas'], color)}
{gen_bars(ytd['sellers'], color)}
{gen_seller_table(ytd['sellers'], store_id, 'ytd')}
</div>'''
    
    # === 2026 TAB ===
    # Month grid
    month_cards = []
    for m in MONTHS_2026:
        if m in MONTHS_WITH_DATA:
            md = data[m]
            t = md['totals']
            month_cards.append(f'''<div class="mc mc-open" onclick="stab2('{store_id}_{m}_c')">
<div class="mn">{MONTH_NAMES[m]}</div>
<div class="mi">Gross: {t['gross']}</div>
<div class="mi">Upgr: {t['upgrades']}</div>
<div class="mi">Trygg: {t['trygg']}</div>
</div>''')
        else:
            month_cards.append(f'''<div class="mc mc-locked">
<div class="mn">{MONTH_NAMES[m]}</div>
<div class="mi">🔒</div>
</div>''')
    
    month_grid = f'<div class="mnd-grid">{"".join(month_cards)}</div>'
    
    # Month details
    month_details = []
    for m in MONTHS_WITH_DATA:
        md = data[m]
        budget = budgets.get(f'Telia {name}', budgets.get(name, 0))
        is_current = (m == CURRENT_MONTH)
        
        if is_current and budget > 0:
            oppnaaelse = (md['totals']['gross'] / budget) * 100
            daglig_maal = (budget - md['totals']['gross']) / max(WORK_DAYS_REMAINING, 1)
        else:
            oppnaaelse = 0
            daglig_maal = 0
        
        kpis = gen_kpi_grid(md['totals'], color, show_budget=is_current, budget=budget,
                           oppnaaelse=oppnaaelse, daglig_maal=daglig_maal)
        
        month_details.append(f'''<div id="{store_id}_{m}_c" class="mnd-detail">
<div class="back" onclick="hideMnd('{store_id}_{m}_c')">← Tilbake til måneder</div>
<div class="sec">{MONTH_NAMES[m]} 2026</div>
{kpis}
{gen_diploma_grid(md['diplomas'], color)}
{gen_bars(md['sellers'], color)}
{gen_seller_table(md['sellers'], store_id, m)}
</div>''')
    
    tab_2026 = f'''<div id="{store_id}_2026_c" class="tcontent">
{month_grid}
{"".join(month_details)}
</div>'''
    
    return f'''<div id="{store_id}" class="page">
<div class="back" onclick="goHome()">← Tilbake</div>
<div class="store-header"><h2 style="color:{color}">{info['emoji']} {name}</h2></div>
<div class="tabs">
<div class="tab active" onclick="stab(this,'{store_id}_2025_c')">📊 2025</div>
<div class="tab" onclick="stab(this,'{store_id}_2026_c')">📅 2026</div>
</div>
{tab_2025}
{tab_2026}
</div>'''

# === GENERATE HOME PAGE ===
def gen_home():
    # --- 2026 store cards (current month status) ---
    cards_2026 = []
    for store_id, info in STORES.items():
        data = store_data[store_id]
        mars_t = data[CURRENT_MONTH]['totals']
        budget = budgets.get(info['name'], 0)
        oppnaaelse = (mars_t['gross'] / budget * 100) if budget > 0 else 0
        daglig = (budget - mars_t['gross']) / max(WORK_DAYS_REMAINING, 1) if budget > 0 else 0
        
        cards_2026.append(f'''<div class="sc" onclick="goStore('{store_id}',2026)" style="border-top:3px solid {info['color']};cursor:pointer">
<div class="sn" style="color:{info['color']};font-size:1.3em;padding:20px 0">{info['emoji']} {info['name']}</div>
</div>''')
    
    # --- 2025 store cards (YTD totals) ---
    cards_2025 = []
    for store_id, info in STORES.items():
        ytd_t = store_data[store_id]['ytd_2025']['totals']
        cards_2025.append(f'''<div class="sc" onclick="goStore('{store_id}',2025)" style="border-top:3px solid {info['color']};cursor:pointer">
<div class="sn" style="color:{info['color']};font-size:1.3em;padding:20px 0">{info['emoji']} {info['name']}</div>
</div>''')
    
    return f'''<div id="home" class="page active">
<div class="hero">
<h1>Telia Drammen</h1>
<p>Region 1 — Salgsoversikt</p>
</div>
<div id="year-select">
<div class="sec" style="text-align:center">📅 Velg år</div>
<div class="year-grid">
<div class="year-card y2025" onclick="showYear(2025)">
<div class="ynum">2025</div>
<div class="ysub">Årssammendrag</div>
</div>
<div class="year-card y2026" onclick="showYear(2026)">
<div class="ynum">2026</div>
<div class="ysub">Inneværende år</div>
</div>
</div>
</div>
<div id="year-2025" style="display:none">
<div class="back" onclick="hideYear()">← Tilbake</div>
<div class="sec">📊 2025 — Velg butikk</div>
<div class="store-grid">{"".join(cards_2025)}</div>
</div>
<div id="year-2026" style="display:none">
<div class="back" onclick="hideYear()">← Tilbake</div>
<div class="sec">📅 2026 — Velg butikk</div>
<div class="store-grid">{"".join(cards_2026)}</div>
</div>
</div>'''

# === JAVASCRIPT ===
JS = """
var selectedYear = null;

function go(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo(0, 0);
}

function showYear(year) {
  selectedYear = year;
  document.getElementById('year-select').style.display = 'none';
  document.getElementById('year-2025').style.display = year === 2025 ? 'block' : 'none';
  document.getElementById('year-2026').style.display = year === 2026 ? 'block' : 'none';
}

function hideYear() {
  selectedYear = null;
  document.getElementById('year-select').style.display = 'block';
  document.getElementById('year-2025').style.display = 'none';
  document.getElementById('year-2026').style.display = 'none';
}

function goStore(id, year) {
  selectedYear = year;
  go(id);
  var page = document.getElementById(id);
  var tabs = page.querySelectorAll('.tab');
  var tcontents = page.querySelectorAll('.tcontent');
  tabs.forEach(function(t) { t.classList.remove('active'); });
  tcontents.forEach(function(t) { t.classList.remove('active'); });
  var tabIdx = year === 2025 ? 0 : 1;
  tabs[tabIdx].classList.add('active');
  document.getElementById(id + '_' + year + '_c').classList.add('active');
}

function goHome() {
  go('home');
  if (selectedYear) {
    showYear(selectedYear);
  }
}

function stab(btn, contentId) {
  var page = btn.closest('.page');
  page.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  page.querySelectorAll('.tcontent').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById(contentId).classList.add('active');
}

function stab2(id) {
  var detail = document.getElementById(id);
  var tcontent = detail.closest('.tcontent');
  tcontent.querySelectorAll('.mnd-detail').forEach(d => d.style.display = 'none');
  var grid = tcontent.querySelector('.mnd-grid');
  if (grid) grid.style.display = 'none';
  detail.style.display = 'block';
}

function hideMnd(id) {
  var detail = document.getElementById(id);
  var tcontent = detail.closest('.tcontent');
  detail.style.display = 'none';
  var grid = tcontent.querySelector('.mnd-grid');
  if (grid) grid.style.display = 'grid';
}

function showProf(el, source) {
  var d = el.dataset;
  var prof = document.getElementById('profile');
  prof.querySelector('.prof-name').textContent = d.navn || '';
  prof.querySelector('.prof-role').textContent = d.stilling || '';
  var g = prof.querySelector('.prof-grid');
  g.innerHTML = '';
  var items = [
    ['Gross', d.gross],
    ['Upgrades', d.upgr],
    ['Forsikring', d.forsikring],
    ['Telia Trygg', d.trygg],
    ['Tilbehør', d.tilbehor ? Math.round(d.tilbehor) + ' kr' : '0 kr'],
    ['Tjenester', d.tjenester ? Math.round(d.tjenester) + ' kr' : '0 kr']
  ];
  items.forEach(function(item) {
    g.innerHTML += '<div class="kc"><div class="kl">' + item[0] + '</div><div class="kv">' + (item[1] || 0) + '</div></div>';
  });
  prof.dataset.source = source;
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  prof.classList.add('active');
  window.scrollTo(0, 0);
}

function profBack() {
  var prof = document.getElementById('profile');
  var src = prof.dataset.source || '';
  var storePart = src.split('_')[0];
  if (storePart) {
    go(storePart);
  } else {
    goHome();
  }
}
"""

# === ASSEMBLE HTML ===
html_output = f'''<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Telia Drammen — Salgsoversikt</title>
<style>{CSS}</style>
</head>
<body>
<div class="nav">
<div class="logo" onclick="go('home');hideYear()">TELIA DRAMMEN</div>
<button class="hbtn" onclick="go('home');hideYear()">🏠 Hjem</button>
</div>
{gen_home()}
{gen_store_page('gulskogen')}
{gen_store_page('liertoppen')}
{gen_store_page('buskerud')}
<div id="profile" class="page">
<div class="back" onclick="profBack()">← Tilbake</div>
<div class="prof-name"></div>
<div class="prof-role"></div>
<div class="prof-grid kpi-grid"></div>
</div>
<script>{JS}</script>
</body>
</html>'''

# Write output
with open('/tmp/index_new.html', 'w', encoding='utf-8') as f:
    f.write(html_output)

# Validate
import re
opens = len(re.findall(r'<div[\s>]', html_output))
closes = html_output.count('</div>')
print(f"✅ Generated: {len(html_output):,} bytes")
print(f"   DIV balance: {opens} open, {closes} close, diff={opens-closes}")
print(f"   Pages: {len(re.findall(r'class=\"page\"', html_output))}")
print(f"   Tables: {html_output.count('<table>')}")
print(f"   format_num/format_kr calls remaining: {html_output.count('format_num(')}, {html_output.count('format_kr(')}")

# Check all IDs exist
for store_id in ['gulskogen', 'liertoppen', 'buskerud']:
    assert f'id="{store_id}"' in html_output, f"Missing page: {store_id}"
    assert f'id="{store_id}_2025_c"' in html_output, f"Missing: {store_id}_2025_c"
    assert f'id="{store_id}_2026_c"' in html_output, f"Missing: {store_id}_2026_c"
    for m in ['jan', 'feb', 'mar']:
        assert f'id="{store_id}_{m}_c"' in html_output, f"Missing: {store_id}_{m}_c"
assert 'id="home"' in html_output
assert 'id="profile"' in html_output
print("   All required IDs present ✅")
print("   No Python code leaked ✅" if 'format_num(' not in html_output and 'format_kr(' not in html_output else "   ⚠️ Python code leaked!")
