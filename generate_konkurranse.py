#!/usr/bin/env python3
"""
Gulskogen Arena — Anime Competition Page Generator
Uses base64-embedded anime character images (always works, no hotlinking issues)
Mobile + Desktop responsive
"""
import json, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load character images (base64 encoded)
img_path = os.path.join(SCRIPT_DIR, 'char_images_b64.json')
with open(img_path) as f:
    CHAR_IMAGES = json.load(f)

# Load seller data
data_path = os.path.join(SCRIPT_DIR, 'complete_extracted_data.json')
with open(data_path) as f:
    all_data = json.load(f)

# Competition config
MATCHES = [
    {
        'p1': {'search': 'Ahmed Al Ali', 'char': 'NARUTO UZUMAKI', 'img': 'naruto', 'color': '#FF6600', 'glow': '#FF660066', 'attack': 'Shadow Clone Jutsu', 'hours': 100, 'kanji': 'うずまきナルト'},
        'p2': {'search': 'Yasin Ali Ismail', 'char': 'SASUKE UCHIHA', 'img': 'sasuke', 'color': '#5599FF', 'glow': '#5599FF66', 'attack': 'Chidori', 'hours': 90, 'kanji': 'うちはサスケ'}
    },
    {
        'p1': {'search': 'Saidt Oliver Alavi', 'char': 'SON GOKU', 'img': 'goku', 'color': '#FF8C00', 'glow': '#FFD70066', 'attack': 'Kamehameha', 'hours': 60, 'kanji': '孫悟空'},
        'p2': {'search': 'Mert Ambarduzgun', 'char': 'VEGETA', 'img': 'vegeta', 'color': '#9944FF', 'glow': '#9944FF66', 'attack': 'Final Flash', 'hours': 50, 'kanji': 'ベジータ'}
    },
    {
        'p1': {'search': 'Josef Ishan Latif Mossaiar', 'char': 'IZUKU MIDORIYA', 'img': 'deku', 'color': '#22CC66', 'glow': '#22CC6666', 'attack': 'One For All', 'hours': 65, 'kanji': '緑谷出久'},
        'p2': {'search': 'Aya Mohammad', 'char': 'ZERO TWO', 'img': 'zerotwo', 'color': '#FF69B4', 'glow': '#FF69B466', 'attack': 'Strelitzia', 'hours': 68, 'kanji': 'ゼロツー', 'girl': True}
    },
    {
        'p1': {'search': 'Ali Esmati', 'char': 'ICHIGO KUROSAKI', 'img': 'ichigo', 'color': '#FF4444', 'glow': '#FF444466', 'attack': 'Bankai: Tensa Zangetsu', 'hours': 90, 'kanji': '黒崎一護'},
        'p2': {'search': ['Kasim', 'Tommy'], 'char': 'MIGHT GUY & ROCK LEE', 'img': 'guy', 'color': '#00CC44', 'glow': '#00CC4466', 'attack': 'Gates of Youth', 'hours': 90, 'kanji': 'ガイ＆リー', 'duo': True, 'duo_img': 'lee'}
    }
]

def find_seller(sellers, search_name):
    """Find seller data by name (partial match)"""
    if isinstance(search_name, list):
        # Duo - combine stats
        total = {'gross': 0, 'trygg': 0}
        for sn in search_name:
            for s in sellers:
                name = s.get('navn', s.get('name', ''))
                if sn.lower() in name.lower():
                    total['gross'] += s.get('gross', 0)
                    total['trygg'] += s.get('trygg', s.get('telia_trygg', 0))
                    break
        return total
    for s in sellers:
        name = s.get('navn', s.get('name', ''))
        if search_name.lower() in name.lower():
            return {'gross': s.get('gross', 0), 'trygg': s.get('trygg', s.get('telia_trygg', 0))}
    return {'gross': 0, 'trygg': 0}

def calc_power(gross, trygg, hours):
    """Power per time = (gross/t * 10) + (trygg/t * 5)"""
    if hours <= 0:
        return 0.0
    return round((gross / hours) * 10 + (trygg / hours) * 5, 1)

# Get May data for Gulskogen
may_sellers = []
gul = all_data.get('gulskogen', {})
if 'mai' in gul and 'sellers' in gul['mai']:
    may_sellers = gul['mai']['sellers']
elif 'may' in gul and 'sellers' in gul['may']:
    may_sellers = gul['may']['sellers']

# Build match data
match_data = []
all_players = []
for m in MATCHES:
    p1_stats = find_seller(may_sellers, m['p1']['search'])
    p2_stats = find_seller(may_sellers, m['p2']['search'])
    p1_power = calc_power(p1_stats['gross'], p1_stats['trygg'], m['p1']['hours'])
    p2_power = calc_power(p2_stats['gross'], p2_stats['trygg'], m['p2']['hours'])
    
    p1d = {**m['p1'], **p1_stats, 'power': p1_power, 'gross_t': round(p1_stats['gross']/m['p1']['hours'], 2) if m['p1']['hours'] > 0 else 0, 'trygg_t': round(p1_stats['trygg']/m['p1']['hours'], 2) if m['p1']['hours'] > 0 else 0}
    p2d = {**m['p2'], **p2_stats, 'power': p2_power, 'gross_t': round(p2_stats['gross']/m['p2']['hours'], 2) if m['p2']['hours'] > 0 else 0, 'trygg_t': round(p2_stats['trygg']/m['p2']['hours'], 2) if m['p2']['hours'] > 0 else 0}
    
    match_data.append((p1d, p2d))
    
    p1_name = m['p1']['search'] if isinstance(m['p1']['search'], str) else ' & '.join(m['p1']['search'])
    p2_name = m['p2']['search'] if isinstance(m['p2']['search'], str) else ' & '.join(m['p2']['search'])
    all_players.append({'name': p1_name, 'char': m['p1']['char'], 'img': m['p1']['img'], 'color': m['p1']['color'], 'power': p1_power, 'kanji': m['p1']['kanji']})
    all_players.append({'name': p2_name, 'char': m['p2']['char'], 'img': m['p2'].get('duo_img', m['p2']['img']) if m['p2'].get('duo') else m['p2']['img'], 'color': m['p2']['color'], 'power': p2_power, 'kanji': m['p2']['kanji']})

all_players.sort(key=lambda x: x['power'], reverse=True)

# Build HTML
html = f'''<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>⚔️ Gulskogen Arena — Mai 2026</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Russo+One&family=Orbitron:wght@700;900&family=Inter:wght@400;600;700&display=swap');

* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
    background: #080818;
    color: #fff;
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
}}

/* Animated background */
body::before {{
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: 
        radial-gradient(ellipse at 20% 50%, rgba(255,102,0,0.08) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 50%, rgba(85,153,255,0.08) 0%, transparent 60%),
        radial-gradient(ellipse at 50% 0%, rgba(153,68,255,0.06) 0%, transparent 50%);
    z-index: -1;
}}

.container {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 30px 20px;
}}

/* HEADER */
.header {{
    text-align: center;
    margin-bottom: 40px;
}}
.header h1 {{
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 900;
    background: linear-gradient(135deg, #FF6600, #FF3366, #9944FF, #5599FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 8px;
}}
.header .subtitle {{
    font-size: clamp(0.9rem, 2vw, 1.2rem);
    color: #8888aa;
    letter-spacing: 2px;
    text-transform: uppercase;
}}
.header .badge {{
    display: inline-block;
    margin-top: 12px;
    padding: 6px 24px;
    background: linear-gradient(135deg, #FF3366, #FF6600);
    border-radius: 20px;
    font-family: 'Orbitron', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 2px;
}}
.back-link {{
    display: inline-block;
    margin-top: 12px;
    color: #6666aa;
    text-decoration: none;
    font-size: 0.95rem;
    transition: color 0.2s;
}}
.back-link:hover {{ color: #9999cc; }}

/* RANKING TABLE */
.ranking {{
    background: linear-gradient(180deg, #12122a 0%, #0e0e22 100%);
    border: 1px solid #222244;
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 40px;
}}
.ranking h2 {{
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(1.1rem, 2.5vw, 1.5rem);
    text-align: center;
    margin-bottom: 20px;
    color: #FFD700;
    letter-spacing: 2px;
}}
.rank-row {{
    display: flex;
    align-items: center;
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 6px;
    transition: background 0.2s;
}}
.rank-row:hover {{ background: rgba(255,255,255,0.04); }}
.rank-row.top3 {{ background: rgba(255,215,0,0.06); }}
.rank-num {{
    font-family: 'Orbitron', sans-serif;
    font-size: 1.2rem;
    font-weight: 900;
    width: 40px;
    text-align: center;
    flex-shrink: 0;
}}
.rank-num.gold {{ color: #FFD700; }}
.rank-num.silver {{ color: #C0C0C0; }}
.rank-num.bronze {{ color: #CD7F32; }}
.rank-avatar {{
    width: 46px;
    height: 46px;
    border-radius: 50%;
    object-fit: cover;
    margin: 0 14px;
    border: 2px solid;
    flex-shrink: 0;
}}
.rank-info {{
    flex: 1;
    min-width: 0;
}}
.rank-name {{
    font-size: 1.05rem;
    font-weight: 700;
}}
.rank-char {{
    font-size: 0.75rem;
    color: #8888aa;
    text-transform: uppercase;
    letter-spacing: 1px;
}}
.rank-power {{
    font-family: 'Orbitron', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    flex-shrink: 0;
    margin-left: 10px;
}}

/* MATCH CARDS */
.match {{
    background: linear-gradient(180deg, #12122a 0%, #0e0e22 100%);
    border: 1px solid #222244;
    border-radius: 20px;
    padding: 30px 20px;
    margin-bottom: 35px;
    position: relative;
    overflow: hidden;
}}
.match::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--c1), #333, var(--c2));
}}
.match-label {{
    text-align: center;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.85rem;
    color: #555577;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-bottom: 24px;
}}

.fighters {{
    display: flex;
    justify-content: center;
    align-items: flex-start;
    gap: 20px;
    flex-wrap: wrap;
}}
.fighter {{
    text-align: center;
    flex: 1;
    min-width: 180px;
    max-width: 300px;
}}
.fighter-avatar {{
    width: clamp(100px, 18vw, 140px);
    height: clamp(100px, 18vw, 140px);
    border-radius: 50%;
    object-fit: cover;
    margin: 0 auto 12px;
    display: block;
    border: 3px solid;
    transition: transform 0.3s, box-shadow 0.3s;
}}
.fighter-avatar:hover {{
    transform: scale(1.08);
}}
.fighter-avatar.girl {{
    animation: pinkGlow 2s ease-in-out infinite alternate;
}}
@keyframes pinkGlow {{
    0% {{ box-shadow: 0 0 20px #FF69B455, 0 0 40px #FF69B422; }}
    100% {{ box-shadow: 0 0 30px #FF69B488, 0 0 60px #FF69B444; }}
}}
.fighter-char {{
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(0.85rem, 2vw, 1.1rem);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 2px;
}}
.fighter-kanji {{
    font-size: 0.75rem;
    color: #666688;
    margin-bottom: 6px;
}}
.fighter-name {{
    font-size: clamp(0.95rem, 2vw, 1.15rem);
    font-weight: 700;
    color: #ddd;
    margin-bottom: 4px;
}}
.fighter-attack {{
    font-size: 0.8rem;
    color: #777799;
    font-style: italic;
    margin-bottom: 2px;
}}
.fighter-hours {{
    font-size: 0.78rem;
    color: #555577;
    margin-bottom: 14px;
}}

.stats-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 14px;
}}
.stat-box {{
    background: rgba(255,255,255,0.04);
    border-radius: 10px;
    padding: 10px 6px;
    text-align: center;
}}
.stat-val {{
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(1.6rem, 4vw, 2.2rem);
    font-weight: 900;
}}
.stat-label {{
    font-size: 0.7rem;
    color: #8888aa;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 2px;
}}
.stat-per-hour {{
    font-size: 0.7rem;
    color: #666688;
    margin-top: 1px;
}}

.power-badge {{
    display: inline-block;
    padding: 5px 16px;
    border-radius: 20px;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    border: 1px solid;
}}

.vs-circle {{
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: linear-gradient(135deg, #FF3366, #FF6600);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Orbitron', sans-serif;
    font-size: 1rem;
    font-weight: 900;
    flex-shrink: 0;
    align-self: center;
    margin-top: 40px;
}}

/* Power bar */
.power-bar-container {{
    margin-top: 20px;
    padding: 0 10px;
}}
.power-bar-labels {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
    font-size: 0.78rem;
}}
.power-bar-labels .left {{ color: var(--c1); font-weight: 700; }}
.power-bar-labels .right {{ color: var(--c2); font-weight: 700; text-align: right; }}
.power-bar {{
    height: 10px;
    border-radius: 5px;
    background: #1a1a33;
    overflow: hidden;
    display: flex;
}}
.power-bar .bar-left {{
    height: 100%;
    background: linear-gradient(90deg, var(--c1), var(--c1-light));
    transition: width 0.5s;
}}
.power-bar .bar-right {{
    height: 100%;
    background: linear-gradient(90deg, var(--c2-light), var(--c2));
    transition: width 0.5s;
}}
.match-result {{
    text-align: center;
    margin-top: 12px;
    font-family: 'Orbitron', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 2px;
}}
.match-result.winner {{ color: #FFD700; }}
.match-result.draw {{ color: #555577; }}

/* FORMULA */
.formula {{
    text-align: center;
    color: #444466;
    font-size: 0.75rem;
    margin-top: 20px;
    letter-spacing: 1px;
}}

/* FOOTER */
.footer {{
    text-align: center;
    padding: 30px 0;
    color: #333355;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 2px;
}}

/* RESPONSIVE */
@media (max-width: 600px) {{
    .container {{ padding: 16px 12px; }}
    .fighters {{ gap: 12px; }}
    .fighter {{ min-width: 140px; }}
    .vs-circle {{ width: 40px; height: 40px; font-size: 0.85rem; margin-top: 30px; }}
    .rank-row {{ padding: 8px 10px; }}
    .rank-avatar {{ width: 38px; height: 38px; margin: 0 10px; }}
}}
</style>
</head>
<body>
<div class="container">

<div class="header">
<h1>⚔️ GULSKOGEN ARENA ⚔️</h1>
<p class="subtitle">Hvem dominerer Mai — per time?</p>
<div class="badge">MAI 2026</div>
<br>
<a href="index.html" class="back-link">← Tilbake til dashboard</a>
</div>

<!-- POWER RANKING -->
<div class="ranking">
<h2>⚡ POWER RANKING — MAI 2026</h2>
'''

# Ranking rows
for i, p in enumerate(all_players):
    rank = i + 1
    cls = ' top3' if rank <= 3 else ''
    num_cls = ' gold' if rank == 1 else (' silver' if rank == 2 else (' bronze' if rank == 3 else ''))
    medal = '👑' if rank == 1 else ('🥈' if rank == 2 else ('🥉' if rank == 3 else f'#{rank}'))
    img_data = CHAR_IMAGES.get(p['img'], '')
    
    html += f'''<div class="rank-row{cls}">
<span class="rank-num{num_cls}">{medal}</span>
<img class="rank-avatar" src="{img_data}" alt="{p['char']}" style="border-color:{p['color']}">
<div class="rank-info">
<div class="rank-name">{p['name']}</div>
<div class="rank-char" style="color:{p['color']}">{p['char']}</div>
</div>
<div class="rank-power" style="color:{p['color']}">{p['power']}</div>
</div>
'''

html += '''<div class="formula">⚡ POWER = (Gross/time × 10) + (T.Trygg/time × 5)</div>
</div>
'''

# MATCH CARDS
for idx, (p1, p2) in enumerate(match_data):
    match_num = idx + 1
    p1_img = CHAR_IMAGES.get(p1['img'], '')
    p2_img = CHAR_IMAGES.get(p2.get('duo_img', p2['img']) if p2.get('duo') else p2['img'], '')
    
    # Determine winner
    if p1['power'] > p2['power']:
        result_html = f'<div class="match-result winner">👑 {p1["char"].split()[0]} WINS</div>'
    elif p2['power'] > p1['power']:
        result_html = f'<div class="match-result winner">👑 {p2["char"].split()[0]} WINS</div>'
    else:
        result_html = '<div class="match-result draw">⚔ DRAW ⚔</div>'
    
    # Power bar percentages
    total_power = p1['power'] + p2['power']
    if total_power > 0:
        p1_pct = (p1['power'] / total_power) * 100
        p2_pct = 100 - p1_pct
    else:
        p1_pct = 50
        p2_pct = 50
    
    p1_name = p1['search'] if isinstance(p1['search'], str) else ' & '.join(p1['search'])
    p2_name = p2['search'] if isinstance(p2['search'], str) else ' & '.join(p2['search'])
    p1_short = p1_name.split()[0].upper()
    p2_short = p2_name.split()[0].upper() if not p2.get('duo') else 'DUO'
    
    girl_cls = ' girl' if p2.get('girl') else ''
    
    # For duo, show both images
    if p2.get('duo'):
        p2_avatar_html = f'<img class="fighter-avatar" src="{p2_img}" alt="{p2["char"]}" style="border-color:{p2["color"]};box-shadow:0 0 25px {p2["glow"]}">'
    else:
        p2_avatar_html = f'<img class="fighter-avatar{girl_cls}" src="{p2_img}" alt="{p2["char"]}" style="border-color:{p2["color"]};box-shadow:0 0 25px {p2["glow"]}">'
    
    html += f'''
<div class="match" style="--c1:{p1['color']};--c1-light:{p1['color']}88;--c2:{p2['color']};--c2-light:{p2['color']}88">
<div class="match-label">⚔ KAMP {match_num}</div>
<div class="fighters">

<div class="fighter">
<img class="fighter-avatar" src="{p1_img}" alt="{p1['char']}" style="border-color:{p1['color']};box-shadow:0 0 25px {p1['glow']}">
<div class="fighter-char" style="color:{p1['color']}">{p1['char']}</div>
<div class="fighter-kanji">{p1['kanji']}</div>
<div class="fighter-name">{p1_name}</div>
<div class="fighter-attack">⚡ {p1['attack']}</div>
<div class="fighter-hours">🕐 {p1['hours']} timer</div>
<div class="stats-grid">
<div class="stat-box">
<div class="stat-val" style="color:{p1['color']}">{p1['gross']}</div>
<div class="stat-label">Gross</div>
<div class="stat-per-hour">{p1['gross_t']}/t</div>
</div>
<div class="stat-box">
<div class="stat-val" style="color:{p1['color']}">{p1['trygg']}</div>
<div class="stat-label">T.Trygg</div>
<div class="stat-per-hour">{p1['trygg_t']}/t</div>
</div>
</div>
<div class="power-badge" style="color:{p1['color']};border-color:{p1['color']}44">⚡ {p1['power']} POWER</div>
</div>

<div class="vs-circle">VS</div>

<div class="fighter">
{p2_avatar_html}
<div class="fighter-char" style="color:{p2['color']}">{p2['char']}</div>
<div class="fighter-kanji">{p2['kanji']}</div>
<div class="fighter-name">{p2_name}</div>
<div class="fighter-attack">⚡ {p2['attack']}</div>
<div class="fighter-hours">🕐 {p2['hours']} timer</div>
<div class="stats-grid">
<div class="stat-box">
<div class="stat-val" style="color:{p2['color']}">{p2['gross']}</div>
<div class="stat-label">Gross</div>
<div class="stat-per-hour">{p2['gross_t']}/t</div>
</div>
<div class="stat-box">
<div class="stat-val" style="color:{p2['color']}">{p2['trygg']}</div>
<div class="stat-label">T.Trygg</div>
<div class="stat-per-hour">{p2['trygg_t']}/t</div>
</div>
</div>
<div class="power-badge" style="color:{p2['color']};border-color:{p2['color']}44">⚡ {p2['power']} POWER</div>
</div>

</div>

<div class="power-bar-container">
<div class="power-bar-labels">
<span class="left">{p1_short} {p1['gross_t']} gross/t | {p1['trygg_t']} trygg/t</span>
<span class="right">{p2['gross_t']} gross/t | {p2['trygg_t']} trygg/t {p2_short}</span>
</div>
<div class="power-bar">
<div class="bar-left" style="width:{p1_pct}%"></div>
<div class="bar-right" style="width:{p2_pct}%"></div>
</div>
</div>

{result_html}
</div>
'''

html += '''
<div class="footer">
TELIA DRAMMEN · GULSKOGEN · MAI 2026<br>
Oppdateres automatisk ved ny rapport
</div>

</div>
</body>
</html>'''

out_path = os.path.join(SCRIPT_DIR, 'konkurranse.html')
with open(out_path, 'w') as f:
    f.write(html)

print(f"konkurranse.html generert ({len(html):,} bytes)")
