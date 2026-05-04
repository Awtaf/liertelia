#!/usr/bin/env python3
"""
Generate konkurranse.html - Gulskogen Mai anime-style competition page
Auto-updated whenever new ToppSelger reports arrive.
Uses pure CSS character art - NO emojis, NO external images.
"""
import json
import os

# ── MATCHUPS ─────────────────────────────────────────────────────────────────
MATCHUPS = [
    {
        'id': 'm1',
        'left': {
            'name': 'Ahmed Al Ali',
            'hours': 100,
            'color': '#FF6600',
            'anime': 'NARUTO',
            'jp': 'うずまきナルト',
            'ability': 'Shadow Clone Jutsu',
            'symbol': 'N',
            'gradient': 'linear-gradient(160deg, #7a2e00 0%, #FF6600 60%, #FFB300 100%)',
            'glow': '#FF6600',
        },
        'right': {
            'name': 'Yasin Ali Ismail',
            'hours': 90,
            'color': '#5599FF',
            'anime': 'SASUKE',
            'jp': 'うちはサスケ',
            'ability': 'Chidori',
            'symbol': 'S',
            'gradient': 'linear-gradient(160deg, #0a0a40 0%, #1a1aaa 60%, #5599FF 100%)',
            'glow': '#5599FF',
        },
    },
    {
        'id': 'm2',
        'left': {
            'name': 'Saidt Oliver Alavi',
            'hours': 60,
            'color': '#FFD700',
            'anime': 'GOKU',
            'jp': '孫悟空',
            'ability': 'Kamehameha',
            'symbol': 'G',
            'gradient': 'linear-gradient(160deg, #4a3000 0%, #FF8C00 60%, #FFD700 100%)',
            'glow': '#FFD700',
        },
        'right': {
            'name': 'Mert Ambarduzgun',
            'hours': 50,
            'color': '#BB66FF',
            'anime': 'VEGETA',
            'jp': 'ベジータ',
            'ability': 'Final Flash',
            'symbol': 'V',
            'gradient': 'linear-gradient(160deg, #2a0050 0%, #6600aa 60%, #BB66FF 100%)',
            'glow': '#BB66FF',
        },
    },
    {
        'id': 'm3',
        'left': {
            'name': 'Josef Ishan Latif Mossaiar',
            'hours': 65,
            'color': '#44DD88',
            'anime': 'DEKU',
            'jp': 'デク',
            'ability': 'One For All',
            'symbol': 'D',
            'gradient': 'linear-gradient(160deg, #003322 0%, #22aa55 60%, #44DD88 100%)',
            'glow': '#44DD88',
        },
        'right': {
            'name': 'Aya Mohammad',
            'hours': 68,
            'color': '#FF69B4',
            'anime': 'ZERO TWO',
            'jp': 'ゼロツー',
            'ability': 'Strelizia',
            'symbol': '02',
            'gradient': 'linear-gradient(160deg, #4a0028 0%, #cc2277 60%, #FF69B4 100%)',
            'glow': '#FF69B4',
            'is_girl': True,
        },
    },
    {
        'id': 'm4',
        'left': {
            'name': 'Ali Esmati',
            'hours': 90,
            'color': '#FF4444',
            'anime': 'ICHIGO',
            'jp': '黒崎一護',
            'ability': 'Bankai: Tensa Zangetsu',
            'symbol': 'I',
            'gradient': 'linear-gradient(160deg, #3a0000 0%, #cc2222 60%, #FF4444 100%)',
            'glow': '#FF4444',
        },
        'right': {
            'name': 'Kasim & Tommy',
            'hours': 90,
            'color': '#00CC66',
            'anime': 'GUY & LEE',
            'jp': 'ガイ＆リー',
            'ability': 'Gates of Youth',
            'symbol': 'GL',
            'gradient': 'linear-gradient(160deg, #003322 0%, #009944 60%, #00CC66 100%)',
            'glow': '#00CC66',
        },
    },
]

ALL_FIGHTERS = []
for m in MATCHUPS:
    ALL_FIGHTERS.append(m['left'])
    ALL_FIGHTERS.append(m['right'])


def load_may_data():
    """Load Mai data from complete_extracted_data.json"""
    data_path = os.path.join(os.path.dirname(__file__), 'complete_extracted_data.json')
    if not os.path.exists(data_path):
        return {}
    with open(data_path, 'r') as f:
        data = json.load(f)
    gulskogen = data.get('gulskogen', {})
    mai = gulskogen.get('mai', gulskogen.get('may', {}))
    sellers = mai.get('sellers', [])
    result = {}
    for s in sellers:
        name = s.get('navn', s.get('name', ''))
        result[name] = {
            'gross': s.get('gross', 0),
            'trygg': s.get('trygg', s.get('telia_trygg', 0)),
        }
    return result


def get_fighter_stats(fighter, mai_data):
    name = fighter['name']
    if '&' in name:
        parts = name.split('&')
        total_g = 0
        total_t = 0
        for part in parts:
            pname = part.strip()
            for k, v in mai_data.items():
                if pname.lower() in k.lower():
                    total_g += v['gross']
                    total_t += v['trygg']
                    break
        return total_g, total_t
    else:
        for k, v in mai_data.items():
            if name.lower().split()[0] in k.lower() and name.lower().split()[-1] in k.lower():
                return v['gross'], v['trygg']
        first = name.split()[0].lower()
        for k, v in mai_data.items():
            if first in k.lower():
                return v['gross'], v['trygg']
    return 0, 0


def calc_power(gross, trygg, hours):
    if hours == 0:
        return 0
    return round((gross / hours) * 10 + (trygg / hours) * 5, 1)


def generate():
    mai_data = load_may_data()

    # Calculate all stats
    fighter_stats = []
    for f in ALL_FIGHTERS:
        gross, trygg = get_fighter_stats(f, mai_data)
        power = calc_power(gross, trygg, f['hours'])
        gross_per_h = round(gross / f['hours'], 2) if f['hours'] > 0 else 0
        trygg_per_h = round(trygg / f['hours'], 2) if f['hours'] > 0 else 0
        fighter_stats.append({
            **f,
            'gross': gross,
            'trygg': trygg,
            'power': power,
            'gross_per_h': gross_per_h,
            'trygg_per_h': trygg_per_h,
        })

    # Sort by power for ranking
    ranked = sorted(fighter_stats, key=lambda x: x['power'], reverse=True)

    # Build HTML
    html = f'''<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<title>Gulskogen Konkurranse — Mai 2026</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    background: #080818;
    color: #fff;
    font-family: 'Segoe UI', Tahoma, sans-serif;
    min-width: 1000px;
    padding: 40px 60px;
}}

.title {{
    text-align: center;
    font-size: 52px;
    font-weight: 900;
    letter-spacing: 3px;
    margin-bottom: 8px;
    background: linear-gradient(90deg, #FF6600, #FFD700, #FF6600);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-transform: uppercase;
}}
.subtitle {{
    text-align: center;
    font-size: 24px;
    color: #aaa;
    margin-bottom: 10px;
}}
.badge {{
    display: inline-block;
    background: linear-gradient(135deg, #FF6600, #FF3300);
    color: #fff;
    padding: 8px 28px;
    border-radius: 30px;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 2px;
    margin: 0 auto 40px;
}}
.badge-wrap {{ text-align: center; }}
.back-link {{
    text-align: center;
    margin-bottom: 40px;
}}
.back-link a {{
    color: #888;
    text-decoration: none;
    font-size: 18px;
}}
.back-link a:hover {{ color: #fff; }}

/* ── RANKING TABLE ─────────────────────────────────────────── */
.ranking {{
    max-width: 900px;
    margin: 0 auto 60px;
    background: #111125;
    border-radius: 16px;
    border: 1px solid #222;
    overflow: hidden;
}}
.ranking-title {{
    text-align: center;
    font-size: 28px;
    font-weight: 800;
    padding: 20px;
    border-bottom: 1px solid #222;
    letter-spacing: 2px;
}}
.rank-row {{
    display: flex;
    align-items: center;
    padding: 14px 30px;
    border-bottom: 1px solid #1a1a30;
    font-size: 20px;
}}
.rank-row:last-child {{ border-bottom: none; }}
.rank-num {{
    width: 50px;
    font-weight: 800;
    font-size: 22px;
}}
.rank-num.gold {{ color: #FFD700; }}
.rank-num.silver {{ color: #C0C0C0; }}
.rank-num.bronze {{ color: #CD7F32; }}
.rank-avatar {{
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 20px;
    margin-right: 18px;
    color: #fff;
    text-shadow: 0 0 10px rgba(0,0,0,0.5);
    flex-shrink: 0;
}}
.rank-info {{
    flex: 1;
}}
.rank-name {{
    font-weight: 700;
    font-size: 20px;
}}
.rank-anime {{
    font-size: 14px;
    opacity: 0.5;
    letter-spacing: 1px;
}}
.rank-power {{
    font-weight: 800;
    font-size: 24px;
    min-width: 80px;
    text-align: right;
}}

/* ── MATCH CARDS ─────────────────────────────────────────── */
.match {{
    max-width: 950px;
    margin: 0 auto 50px;
    background: #0d0d22;
    border-radius: 20px;
    border: 1px solid #222;
    padding: 40px;
}}
.match-label {{
    text-align: center;
    font-size: 16px;
    letter-spacing: 4px;
    color: #555;
    margin-bottom: 30px;
    text-transform: uppercase;
}}
.fighters {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}}
.fighter {{
    width: 38%;
    text-align: center;
}}
.avatar-circle {{
    width: 140px;
    height: 140px;
    border-radius: 50%;
    margin: 0 auto 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 52px;
    color: #fff;
    text-shadow: 0 0 20px rgba(0,0,0,0.5);
    position: relative;
}}
.avatar-circle.girl {{
    animation: girlPulse 2s ease-in-out infinite;
}}
@keyframes girlPulse {{
    0%, 100% {{ box-shadow: 0 0 30px rgba(255,105,180,0.4); }}
    50% {{ box-shadow: 0 0 60px rgba(255,105,180,0.8), 0 0 100px rgba(255,105,180,0.3); }}
}}
.anime-name {{
    font-size: 26px;
    font-weight: 900;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 4px;
}}
.jp-name {{
    font-size: 14px;
    opacity: 0.4;
    margin-bottom: 6px;
}}
.real-name {{
    font-size: 20px;
    font-weight: 600;
    color: #ccc;
    margin-bottom: 4px;
}}
.ability {{
    font-size: 15px;
    opacity: 0.6;
    font-style: italic;
    margin-bottom: 4px;
}}
.hours-badge {{
    font-size: 14px;
    color: #66ff66;
    margin-bottom: 18px;
}}
.stats {{
    display: flex;
    justify-content: center;
    gap: 40px;
    margin-bottom: 14px;
}}
.stat-val {{
    font-size: 42px;
    font-weight: 900;
}}
.stat-label {{
    font-size: 14px;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 2px;
}}
.power-badge {{
    display: inline-block;
    padding: 6px 22px;
    border-radius: 20px;
    font-size: 18px;
    font-weight: 800;
    border: 2px solid;
}}

/* VS circle */
.vs-section {{
    width: 20%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding-top: 50px;
}}
.vs {{
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff3300, #ff0066);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    font-weight: 900;
    box-shadow: 0 0 30px rgba(255,0,60,0.5);
}}

/* ── POWER BAR ─────────────────────────────────────────── */
.power-bar-section {{
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #222;
}}
.bar-labels {{
    display: flex;
    justify-content: space-between;
    font-size: 14px;
    margin-bottom: 8px;
}}
.bar-name {{ font-weight: 700; font-size: 16px; text-transform: uppercase; }}
.bar-stats {{ font-size: 13px; color: #aaa; }}
.power-bar {{
    height: 14px;
    background: #1a1a30;
    border-radius: 7px;
    overflow: hidden;
    display: flex;
    margin-bottom: 10px;
}}
.bar-left, .bar-right {{
    height: 100%;
    transition: width 0.5s;
}}
.match-result {{
    text-align: center;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: 3px;
    margin-top: 8px;
}}

footer {{
    text-align: center;
    color: #333;
    font-size: 14px;
    margin-top: 60px;
    letter-spacing: 2px;
    text-transform: uppercase;
}}
</style>
</head>
<body>

<div class="title">GULSKOGEN ARENA</div>
<div class="subtitle">HVEM DOMINERER MAI — PER TIME?</div>
<div class="badge-wrap"><span class="badge">MAI 2026</span></div>
<div class="back-link"><a href="index.html">&larr; Tilbake til dashboard</a></div>

<!-- ── POWER RANKING ─────────────────────────────────────── -->
<div class="ranking">
<div class="ranking-title">POWER RANKING — MAI 2026</div>
'''

    # Ranking rows
    for i, f in enumerate(ranked):
        rank = i + 1
        cls = ''
        if rank == 1: cls = ' gold'
        elif rank == 2: cls = ' silver'
        elif rank == 3: cls = ' bronze'
        medal = ''
        if rank == 1: medal = ' &#x1F451;'
        elif rank == 2: medal = ' &#x1F948;'
        elif rank == 3: medal = ' &#x1F949;'

        html += f'''<div class="rank-row">
    <div class="rank-num{cls}">#{rank}{medal}</div>
    <div class="rank-avatar" style="background:{f['gradient']}">{f['symbol']}</div>
    <div class="rank-info">
        <div class="rank-name">{f['name']}</div>
        <div class="rank-anime">{f['anime']} &middot; {f['jp']}</div>
    </div>
    <div class="rank-power" style="color:{f['color']}">{f['power']}</div>
</div>
'''

    html += '''<div class="rank-row" style="justify-content:center;color:#555;font-size:14px;letter-spacing:1px;">
    POWER = (Gross/time &times; 10) + (T.Trygg/time &times; 5)
</div>
</div>
'''

    # ── MATCH CARDS ──────────────────────────────────────────
    for idx, m in enumerate(MATCHUPS):
        left = None
        right = None
        for fs in fighter_stats:
            if fs['name'] == m['left']['name']:
                left = fs
            if fs['name'] == m['right']['name']:
                right = fs

        total_power = left['power'] + right['power']
        if total_power > 0:
            left_pct = round(left['power'] / total_power * 100)
            right_pct = 100 - left_pct
        else:
            left_pct = 50
            right_pct = 50

        if left['power'] > right['power']:
            result_text = f"&#x1F451; {left['name'].split()[0].upper()} LEDER"
            result_color = left['color']
        elif right['power'] > left['power']:
            result_text = f"{right['name'].split()[0].upper()} LEDER &#x1F451;"
            result_color = right['color']
        else:
            result_text = "DRAW"
            result_color = "#888"

        girl_class = ' girl' if left.get('is_girl') else ''
        girl_class_r = ' girl' if right.get('is_girl') else ''

        html += f'''
<!-- ── KAMP {idx+1} ─────────────────────────────────────── -->
<div class="match">
<div class="match-label">KAMP {idx+1}</div>
<div class="fighters">
    <div class="fighter">
        <div class="avatar-circle{girl_class}" style="background:{left['gradient']};box-shadow:0 0 40px {left['glow']}55">{left['symbol']}</div>
        <div class="anime-name" style="color:{left['color']}">{left['anime']}</div>
        <div class="jp-name">{left['jp']}</div>
        <div class="real-name">{left['name']}</div>
        <div class="ability">{left['ability']}</div>
        <div class="hours-badge">{left['hours']} timer</div>
        <div class="stats">
            <div><div class="stat-val" style="color:{left['color']}">{left['gross']}</div><div class="stat-label">GROSS</div></div>
            <div><div class="stat-val" style="color:{left['color']}">{left['trygg']}</div><div class="stat-label">T.TRYGG</div></div>
        </div>
        <div class="power-badge" style="color:{left['color']};border-color:{left['color']}">{left['power']} POWER</div>
    </div>
    <div class="vs-section">
        <div class="vs">VS</div>
    </div>
    <div class="fighter">
        <div class="avatar-circle{girl_class_r}" style="background:{right['gradient']};box-shadow:0 0 40px {right['glow']}55">{right['symbol']}</div>
        <div class="anime-name" style="color:{right['color']}">{right['anime']}</div>
        <div class="jp-name">{right['jp']}</div>
        <div class="real-name">{right['name']}</div>
        <div class="ability">{right['ability']}</div>
        <div class="hours-badge">{right['hours']} timer</div>
        <div class="stats">
            <div><div class="stat-val" style="color:{right['color']}">{right['gross']}</div><div class="stat-label">GROSS</div></div>
            <div><div class="stat-val" style="color:{right['color']}">{right['trygg']}</div><div class="stat-label">T.TRYGG</div></div>
        </div>
        <div class="power-badge" style="color:{right['color']};border-color:{right['color']}">{right['power']} POWER</div>
    </div>
</div>

<div class="power-bar-section">
    <div class="bar-labels">
        <div>
            <span class="bar-name" style="color:{left['color']}">{left['name'].split()[0].upper()}</span>
            <span class="bar-stats">{left['gross_per_h']} gross/t | {left['trygg_per_h']} trygg/t</span>
        </div>
        <div style="text-align:right">
            <span class="bar-stats">{right['gross_per_h']} gross/t | {right['trygg_per_h']} trygg/t</span>
            <span class="bar-name" style="color:{right['color']}">{right['name'].split()[0].upper()}</span>
        </div>
    </div>
    <div class="power-bar">
        <div class="bar-left" style="width:{left_pct}%;background:{left['gradient']}"></div>
        <div class="bar-right" style="width:{right_pct}%;background:{right['gradient']}"></div>
    </div>
    <div class="match-result" style="color:{result_color}">{result_text}</div>
</div>
</div>
'''

    html += '''
<footer>TELIA DRAMMEN &middot; GULSKOGEN &middot; MAI 2026<br>Oppdateres automatisk ved ny rapport</footer>
</body>
</html>'''

    out_path = os.path.join(os.path.dirname(__file__), 'konkurranse.html')
    with open(out_path, 'w') as f:
        f.write(html)
    print(f"konkurranse.html generert ({len(html):,} bytes)")


if __name__ == '__main__':
    generate()
