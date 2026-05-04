#!/usr/bin/env python3
"""
Generate konkurranse.html - Gulskogen Mai anime-style competition page
Auto-updated whenever new ToppSelger reports arrive.
"""
import json
import os

# ── HOURS PER FIGHTER (fixed, set by manager) ───────────────────────────────
HOURS = {
    'Ahmed Al Ali':             100,
    'Yasin Ali Ismail':          90,
    'Saidt Oliver Alavi':        60,
    'Mert Ambarduzgun':          50,
    'Aya Mohammad':              68,
    'Josef Ishan Latif Mossaiar':65,
    'Ali Esmati':                90,
    # Team: Kasim + Tommy combined = 90h
    'Kasim Al Ali':              90,   # team hours (shared bucket)
    'Tommy Olafsen':             90,   # team hours (shared bucket)
}

# ── MATCHUPS ─────────────────────────────────────────────────────────────────
MATCHUPS = [
    {
        'id': 'm1',
        'left':  {'name': 'Ahmed Al Ali',       'hours': 100, 'color': '#FF4500', 'anime': 'NARUTO', 'emoji': '🔥'},
        'right': {'name': 'Yasin Ali Ismail',   'hours': 90,  'color': '#00BFFF', 'anime': 'SASUKE', 'emoji': '⚡'},
    },
    {
        'id': 'm2',
        'left':  {'name': 'Saidt Oliver Alavi', 'hours': 60,  'color': '#FFD700', 'anime': 'GOKU',   'emoji': '💛'},
        'right': {'name': 'Mert Ambarduzgun',   'hours': 50,  'color': '#9B59B6', 'anime': 'VEGETA', 'emoji': '🟣'},
    },
    {
        'id': 'm3',
        'left':  {'name': 'Josef Ishan Latif Mossaiar', 'hours': 65, 'color': '#00FF7F', 'anime': 'DEKU', 'emoji': '💚'},
        'right': {'name': 'Aya Mohammad',               'hours': 68, 'color': '#FF69B4', 'anime': 'ZERO TWO', 'emoji': '🌸'},
    },
    {
        'id': 'm4',
        'left':  {'name': 'Ali Esmati',   'hours': 90, 'color': '#FF6B35', 'anime': 'ICHIGO', 'emoji': '🟠',
                  'solo': True},
        'right': {'name': 'Kasim Al Ali + Tommy Olafsen', 'hours': 90, 'color': '#00E5FF', 'anime': 'DUO',
                  'emoji': '🤝', 'team': ['Kasim Al Ali', 'Tommy Olafsen']},
    },
]

def load_data():
    path = '/agent/home/complete_extracted_data.json'
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)

def get_seller_stats(data, store, month, name):
    """Return gross and trygg for a seller in a given store/month."""
    try:
        sellers = data[store][month]['sellers']
    except (KeyError, TypeError):
        return 0, 0
    for s in sellers:
        sname = s.get('navn', s.get('name', ''))
        if sname.strip().lower() == name.strip().lower():
            return float(s.get('gross', 0)), float(s.get('trygg', 0))
    return 0, 0

def fighter_stats(data, fighter):
    """Get gross, trygg, per-hour stats for a fighter."""
    if 'team' in fighter:
        gross, trygg = 0, 0
        for member in fighter['team']:
            g, t = get_seller_stats(data, 'gulskogen', 'mai', member)
            gross += g
            trygg += t
        hours = fighter['hours']
    else:
        gross, trygg = get_seller_stats(data, 'gulskogen', 'mai', fighter['name'])
        hours = fighter['hours']

    gross_ph = round(gross / hours, 2) if hours > 0 else 0
    trygg_ph = round(trygg / hours, 2) if hours > 0 else 0
    power    = round(gross_ph * 10 + trygg_ph * 5, 1)
    return {
        'gross':    int(gross),
        'trygg':    int(trygg),
        'hours':    hours,
        'gross_ph': gross_ph,
        'trygg_ph': trygg_ph,
        'power':    power,
    }

def bar_pct(a, b):
    """Return percentage widths for two values (left, right)."""
    total = a + b
    if total == 0:
        return 50, 50
    return round(a / total * 100), round(b / total * 100)

def winner_class(left_power, right_power):
    if left_power > right_power:
        return 'left-wins'
    elif right_power > left_power:
        return 'right-wins'
    return 'draw'

def generate_html(data):
    # Pre-compute all stats
    matchup_data = []
    for m in MATCHUPS:
        ls = fighter_stats(data, m['left'])
        rs = fighter_stats(data, m['right'])
        matchup_data.append({'matchup': m, 'ls': ls, 'rs': rs})

    # ── CSS ─────────────────────────────────────────────────────────────────
    css = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        background: #04040f;
        color: #fff;
        font-family: 'Segoe UI', sans-serif;
        min-height: 100vh;
        overflow-x: hidden;
    }
    .bg-stars {
        position: fixed; top:0; left:0; width:100%; height:100%;
        background: radial-gradient(ellipse at 20% 20%, #0a0a2e 0%, #04040f 60%);
        z-index: -1;
    }
    .bg-stars::before {
        content: '';
        position: absolute; top:0; left:0; width:100%; height:100%;
        background-image:
            radial-gradient(1px 1px at 10% 15%, #fff 0%, transparent 100%),
            radial-gradient(1px 1px at 30% 40%, #aaf 0%, transparent 100%),
            radial-gradient(1px 1px at 60% 10%, #fff 0%, transparent 100%),
            radial-gradient(1px 1px at 80% 60%, #ffa 0%, transparent 100%),
            radial-gradient(1px 1px at 50% 80%, #fff 0%, transparent 100%),
            radial-gradient(1px 1px at 90% 25%, #aff 0%, transparent 100%),
            radial-gradient(1px 1px at 15% 70%, #fff 0%, transparent 100%),
            radial-gradient(1px 1px at 70% 45%, #faf 0%, transparent 100%);
        opacity: 0.6;
    }

    header {
        text-align: center;
        padding: 40px 20px 20px;
        position: relative;
    }
    .header-title {
        font-size: clamp(1.8rem, 5vw, 3rem);
        font-weight: 900;
        letter-spacing: 3px;
        text-transform: uppercase;
        background: linear-gradient(135deg, #FFD700, #FF4500, #FF69B4, #00BFFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: titlePulse 3s ease-in-out infinite;
        text-shadow: none;
    }
    @keyframes titlePulse {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.3); }
    }
    .header-sub {
        color: #aaa;
        font-size: 0.9rem;
        letter-spacing: 2px;
        margin-top: 8px;
        text-transform: uppercase;
    }
    .month-badge {
        display: inline-block;
        background: linear-gradient(135deg, #990AE3, #00BFFF);
        color: #fff;
        font-weight: 700;
        font-size: 0.85rem;
        padding: 4px 16px;
        border-radius: 20px;
        margin-top: 10px;
        letter-spacing: 2px;
    }

    .arena {
        max-width: 900px;
        margin: 0 auto;
        padding: 20px 16px 60px;
    }

    /* ── MATCHUP CARD ── */
    .matchup-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        margin-bottom: 30px;
        overflow: hidden;
        position: relative;
        transition: transform 0.3s;
    }
    .matchup-card:hover { transform: translateY(-3px); }
    .matchup-card.left-wins  { border-color: rgba(255,255,255,0.15); }
    .matchup-card.right-wins { border-color: rgba(255,255,255,0.15); }

    .matchup-number {
        text-align: center;
        font-size: 0.7rem;
        letter-spacing: 3px;
        color: #555;
        padding: 14px 0 0;
        text-transform: uppercase;
    }

    .fighters-row {
        display: flex;
        align-items: stretch;
        gap: 0;
        padding: 16px;
    }

    /* ── FIGHTER ── */
    .fighter {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 16px 12px;
        border-radius: 14px;
        position: relative;
        transition: background 0.3s;
    }
    .fighter.winner {
        background: rgba(255,255,255,0.06);
    }
    .fighter-avatar {
        width: 80px; height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.2rem;
        margin-bottom: 8px;
        position: relative;
        border: 3px solid transparent;
        animation: avatarGlow 2s ease-in-out infinite;
    }
    @keyframes avatarGlow {
        0%, 100% { box-shadow: 0 0 10px var(--c), 0 0 20px var(--c); }
        50%       { box-shadow: 0 0 20px var(--c), 0 0 40px var(--c), 0 0 60px var(--c); }
    }
    .winner-crown {
        position: absolute;
        top: -14px;
        font-size: 1.2rem;
        display: none;
    }
    .fighter.winner .winner-crown { display: block; }

    .fighter-anime {
        font-size: 0.6rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        opacity: 0.6;
        margin-bottom: 4px;
    }
    .fighter-name {
        font-size: 0.95rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 4px;
        line-height: 1.3;
    }
    .fighter-hours {
        font-size: 0.7rem;
        color: #666;
        margin-bottom: 12px;
    }
    .stat-row {
        display: flex;
        justify-content: center;
        gap: 16px;
        width: 100%;
        flex-wrap: wrap;
    }
    .stat-box {
        text-align: center;
    }
    .stat-val {
        font-size: 1.4rem;
        font-weight: 900;
    }
    .stat-lbl {
        font-size: 0.6rem;
        letter-spacing: 1px;
        color: #777;
        text-transform: uppercase;
    }
    .power-badge {
        margin-top: 10px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1px;
        padding: 3px 10px;
        border-radius: 10px;
        border: 1px solid currentColor;
        opacity: 0.8;
    }

    /* ── VS ── */
    .vs-col {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 8px;
        min-width: 60px;
    }
    .vs-circle {
        width: 48px; height: 48px;
        border-radius: 50%;
        background: linear-gradient(135deg, #FF4500, #FFD700);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 1rem;
        letter-spacing: 1px;
        box-shadow: 0 0 20px rgba(255,100,0,0.5);
        animation: vsPulse 1.5s ease-in-out infinite;
    }
    @keyframes vsPulse {
        0%, 100% { transform: scale(1); box-shadow: 0 0 20px rgba(255,100,0,0.5); }
        50%       { transform: scale(1.1); box-shadow: 0 0 35px rgba(255,100,0,0.8); }
    }

    /* ── POWER BAR ── */
    .power-bar-section {
        padding: 0 20px 20px;
    }
    .power-bar-label {
        display: flex;
        justify-content: space-between;
        font-size: 0.65rem;
        color: #666;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .power-bar-track {
        display: flex;
        height: 10px;
        border-radius: 5px;
        overflow: hidden;
        background: rgba(255,255,255,0.05);
    }
    .power-bar-left  { transition: width 1s ease; border-radius: 5px 0 0 5px; }
    .power-bar-right { transition: width 1s ease; border-radius: 0 5px 5px 0; }

    /* ── PER HOUR STATS ROW ── */
    .per-hour-row {
        display: flex;
        justify-content: space-between;
        padding: 10px 20px 6px;
        gap: 10px;
    }
    .ph-block {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.75rem;
        color: #aaa;
    }
    .ph-val { font-weight: 700; font-size: 0.85rem; }

    /* ── DRAW ── */
    .draw-banner {
        text-align: center;
        font-size: 0.8rem;
        letter-spacing: 3px;
        color: #FFD700;
        padding: 6px 0 12px;
        text-transform: uppercase;
    }

    /* ── SCOREBOARD ── */
    .scoreboard {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 30px;
    }
    .scoreboard h3 {
        text-align: center;
        font-size: 0.8rem;
        letter-spacing: 3px;
        color: #aaa;
        text-transform: uppercase;
        margin-bottom: 16px;
    }
    .score-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        font-size: 0.85rem;
    }
    .score-row:last-child { border-bottom: none; }
    .score-name { flex: 1; }
    .score-val { min-width: 60px; text-align: right; font-weight: 700; }
    .rank-1 { color: #FFD700; }
    .rank-2 { color: #C0C0C0; }
    .rank-3 { color: #CD7F32; }

    footer {
        text-align: center;
        color: #333;
        font-size: 0.7rem;
        letter-spacing: 2px;
        padding-bottom: 30px;
    }

    @media (max-width: 500px) {
        .fighters-row { flex-direction: column; gap: 8px; }
        .vs-col { transform: rotate(90deg); padding: 4px 0; }
        .fighter-avatar { width: 60px; height: 60px; font-size: 1.6rem; }
        .stat-val { font-size: 1.1rem; }
    }
    """

    # ── BUILD MATCHUP HTML ────────────────────────────────────────────────────
    matchup_html = ''
    for i, md in enumerate(matchup_data):
        m  = md['matchup']
        ls = md['ls']
        rs = md['rs']

        wc = winner_class(ls['power'], rs['power'])
        lw = 'winner' if wc == 'left-wins' else ''
        rw = 'winner' if wc == 'right-wins' else ''

        lpct, rpct = bar_pct(ls['power'], rs['power'])

        lc = m['left']['color']
        rc = m['right']['color']

        draw_banner = '<div class="draw-banner">⚔️ DRAW ⚔️</div>' if wc == 'draw' else ''

        matchup_html += f"""
        <div class="matchup-card {wc}">
            <div class="matchup-number">⚔️ Kamp {i+1}</div>
            <div class="fighters-row">
                <!-- LEFT -->
                <div class="fighter {lw}" style="--c:{lc}">
                    <div class="winner-crown">👑</div>
                    <div class="fighter-avatar" style="background: radial-gradient(circle, {lc}33, {lc}11); border-color:{lc}; --c:{lc}">
                        {m['left']['emoji']}
                    </div>
                    <div class="fighter-anime" style="color:{lc}">{m['left']['anime']}</div>
                    <div class="fighter-name">{m['left']['name']}</div>
                    <div class="fighter-hours">⏱ {m['left']['hours']} timer</div>
                    <div class="stat-row">
                        <div class="stat-box">
                            <div class="stat-val" style="color:{lc}">{ls['gross']}</div>
                            <div class="stat-lbl">Gross</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-val" style="color:{lc}">{ls['trygg']}</div>
                            <div class="stat-lbl">T.Trygg</div>
                        </div>
                    </div>
                    <div class="power-badge" style="color:{lc}">⚡ {ls['power']} POWER</div>
                </div>

                <!-- VS -->
                <div class="vs-col">
                    <div class="vs-circle">VS</div>
                </div>

                <!-- RIGHT -->
                <div class="fighter {rw}" style="--c:{rc}">
                    <div class="winner-crown">👑</div>
                    <div class="fighter-avatar" style="background: radial-gradient(circle, {rc}33, {rc}11); border-color:{rc}; --c:{rc}">
                        {m['right']['emoji']}
                    </div>
                    <div class="fighter-anime" style="color:{rc}">{m['right']['anime']}</div>
                    <div class="fighter-name">{m['right']['name']}</div>
                    <div class="fighter-hours">⏱ {m['right']['hours']} timer</div>
                    <div class="stat-row">
                        <div class="stat-box">
                            <div class="stat-val" style="color:{rc}">{rs['gross']}</div>
                            <div class="stat-lbl">Gross</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-val" style="color:{rc}">{rs['trygg']}</div>
                            <div class="stat-lbl">T.Trygg</div>
                        </div>
                    </div>
                    <div class="power-badge" style="color:{rc}">⚡ {rs['power']} POWER</div>
                </div>
            </div>

            <!-- Per-hour row -->
            <div class="per-hour-row">
                <div class="ph-block">
                    <span style="color:{lc}">▶</span>
                    <span class="ph-val" style="color:{lc}">{ls['gross_ph']}</span>
                    <span>gross/t &nbsp;|&nbsp;</span>
                    <span class="ph-val" style="color:{lc}">{ls['trygg_ph']}</span>
                    <span>trygg/t</span>
                </div>
                <div class="ph-block">
                    <span>gross/t &nbsp;|&nbsp;</span>
                    <span class="ph-val" style="color:{rc}">{rs['gross_ph']}</span>
                    <span>&nbsp;trygg/t</span>
                    <span class="ph-val" style="color:{rc}">{rs['trygg_ph']}</span>
                    <span style="color:{rc}">◀</span>
                </div>
            </div>

            <!-- Power bar -->
            <div class="power-bar-section">
                <div class="power-bar-label">
                    <span style="color:{lc}">{m['left']['name'].split()[0]}</span>
                    <span style="color:#555">POWER LEVEL</span>
                    <span style="color:{rc}">{m['right']['name'].split()[-1]}</span>
                </div>
                <div class="power-bar-track">
                    <div class="power-bar-left"  style="width:{lpct}%; background:{lc}"></div>
                    <div class="power-bar-right" style="width:{rpct}%; background:{rc}"></div>
                </div>
            </div>
            {draw_banner}
        </div>
        """

    # ── ALL SELLERS POWER RANKING ─────────────────────────────────────────────
    all_fighters = []
    for md in matchup_data:
        m  = md['matchup']
        ls = md['ls']
        rs = md['rs']
        lname = m['left']['name']
        rname = m['right']['name']
        lc    = m['left']['color']
        rc    = m['right']['color']
        le    = m['left']['emoji']
        re    = m['right']['emoji']
        all_fighters.append((lname, ls['power'], ls['gross'], ls['trygg'], lc, le))
        all_fighters.append((rname, rs['power'], rs['gross'], rs['trygg'], rc, re))

    all_fighters.sort(key=lambda x: x[1], reverse=True)
    rank_classes = ['rank-1', 'rank-2', 'rank-3']
    rank_emojis  = ['🥇', '🥈', '🥉']

    ranking_rows = ''
    for idx, (name, power, gross, trygg, color, emoji) in enumerate(all_fighters):
        rc_cls = rank_classes[idx] if idx < 3 else ''
        re_lbl = rank_emojis[idx] if idx < 3 else f'#{idx+1}'
        ranking_rows += f"""
        <div class="score-row">
            <span style="min-width:30px; text-align:center">{re_lbl}</span>
            <span class="score-name {rc_cls}" style="margin-left:10px">{emoji} {name}</span>
            <span class="score-val" style="color:{color}">{power}</span>
        </div>"""

    # ── FULL HTML ─────────────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>⚔️ Gulskogen Konkurranse — Mai 2026</title>
<style>{css}</style>
</head>
<body>
<div class="bg-stars"></div>

<header>
    <div class="header-title">⚔️ Gulskogen Arena ⚔️</div>
    <div class="header-sub">Hvem dominerer mai-måneden?</div>
    <div class="month-badge">MAI 2026</div>
    <div style="margin-top:10px;">
        <a href="index.html" style="color:#555; font-size:0.75rem; text-decoration:none; letter-spacing:2px">
            ← TILBAKE TIL DASHBOARD
        </a>
    </div>
</header>

<div class="arena">

    <!-- POWER RANKING -->
    <div class="scoreboard">
        <h3>⚡ Power Ranking — Mai 2026</h3>
        {ranking_rows}
        <div style="text-align:center; font-size:0.65rem; color:#444; margin-top:10px; letter-spacing:1px">
            POWER = (Gross/time × 10) + (T.Trygg/time × 5)
        </div>
    </div>

    <!-- MATCHUPS -->
    {matchup_html}

</div>

<footer>
    <p>⚡ OPPDATERES AUTOMATISK NÅR NY RAPPORT MOTTAS ⚡</p>
    <p style="margin-top:4px">awtaf.github.io/liertelia/konkurranse.html</p>
</footer>

</body>
</html>"""

    return html

if __name__ == '__main__':
    data = load_data()
    html = generate_html(data)
    out  = '/agent/home/konkurranse.html'
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    size = os.path.getsize(out)
    print(f"✅ konkurranse.html generated ({size:,} bytes)")
