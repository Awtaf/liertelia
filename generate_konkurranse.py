#!/usr/bin/env python3
"""
Generate konkurranse.html - Gulskogen Mai anime-style competition page
Auto-updated whenever new ToppSelger reports arrive.
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
            'anime': 'NARUTO UZUMAKI',
            'jp': 'うずまきナルト',
            'ability': '🌀 Shadow Clone Jutsu',
            'emoji': '🌀',
            'gradient': 'linear-gradient(160deg, #7a2e00 0%, #FF6600 60%, #FFB300 100%)',
            'bg': '#7a2e00',
        },
        'right': {
            'name': 'Yasin Ali Ismail',
            'hours': 90,
            'color': '#5599FF',
            'anime': 'SASUKE UCHIHA',
            'jp': 'うちはサスケ',
            'ability': '⚡ Chidori',
            'emoji': '⚡',
            'gradient': 'linear-gradient(160deg, #0a0a40 0%, #1a1aaa 60%, #5599FF 100%)',
            'bg': '#0a0a40',
        },
    },
    {
        'id': 'm2',
        'left': {
            'name': 'Saidt Oliver Alavi',
            'hours': 60,
            'color': '#FFD700',
            'anime': 'SON GOKU',
            'jp': '孫悟空',
            'ability': '🔆 Kamehameha',
            'emoji': '🔆',
            'gradient': 'linear-gradient(160deg, #4a3000 0%, #FF8C00 60%, #FFD700 100%)',
            'bg': '#4a3000',
        },
        'right': {
            'name': 'Mert Ambarduzgun',
            'hours': 50,
            'color': '#CC55FF',
            'anime': 'VEGETA',
            'jp': 'ベジータ',
            'ability': '👑 Final Flash',
            'emoji': '👑',
            'gradient': 'linear-gradient(160deg, #2a0040 0%, #6600aa 60%, #CC55FF 100%)',
            'bg': '#2a0040',
        },
    },
    {
        'id': 'm3',
        'left': {
            'name': 'Josef Ishan Latif Mossaiar',
            'hours': 65,
            'color': '#00DD66',
            'anime': 'IZUKU MIDORIYA',
            'jp': '緑谷出久',
            'ability': '💪 One For All',
            'emoji': '💪',
            'gradient': 'linear-gradient(160deg, #003300 0%, #006622 60%, #00DD66 100%)',
            'bg': '#003300',
        },
        'right': {
            'name': 'Aya Mohammad',
            'hours': 68,
            'color': '#FF69B4',
            'anime': 'ZERO TWO',
            'jp': 'ゼロツー',
            'ability': '🌸 Strelizia',
            'emoji': '🌸',
            'gradient': 'linear-gradient(160deg, #4a0020 0%, #cc0066 60%, #FF69B4 100%)',
            'bg': '#4a0020',
            'is_girl': True,
        },
    },
    {
        'id': 'm4',
        'left': {
            'name': 'Ali Esmati',
            'hours': 90,
            'color': '#FF4422',
            'anime': 'ICHIGO KUROSAKI',
            'jp': '黒崎一護',
            'ability': '⚔️ Getsuga Tenshou',
            'emoji': '⚔️',
            'gradient': 'linear-gradient(160deg, #3a0000 0%, #991100 60%, #FF4422 100%)',
            'bg': '#3a0000',
        },
        'right': {
            'name': 'Kasim & Tommy',
            'hours': 90,
            'color': '#00E5FF',
            'anime': 'MIGHT GUY & ROCK LEE',
            'jp': 'マイト・ガイ & ロック・リー',
            'ability': '🔥 Gates of Youth',
            'emoji': '🔥',
            'gradient': 'linear-gradient(160deg, #003333 0%, #006644 60%, #00E5FF 100%)',
            'bg': '#003333',
            'team': ['Kasim Al Ali', 'Tommy Olafsen'],
        },
    },
]


def load_data():
    path = '/agent/home/complete_extracted_data.json'
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def get_seller_stats(data, store, month, name):
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
    total = a + b
    if total == 0:
        return 50, 50
    return round(a / total * 100), round(b / total * 100)


def winner_class(lp, rp):
    if lp > rp:   return 'left-wins'
    if rp > lp:   return 'right-wins'
    return 'draw'


def generate_html(data):
    matchup_data = []
    for m in MATCHUPS:
        ls = fighter_stats(data, m['left'])
        rs = fighter_stats(data, m['right'])
        matchup_data.append({'matchup': m, 'ls': ls, 'rs': rs})

    css = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        background: #04040f;
        color: #fff;
        font-family: 'Segoe UI', sans-serif;
        min-height: 100vh;
        overflow-x: hidden;
        min-width: 900px;
    }

    /* ── STARFIELD ── */
    .bg-stars {
        position: fixed; top:0; left:0; width:100%; height:100%;
        background: radial-gradient(ellipse at 20% 20%, #0a0a2e 0%, #04040f 60%);
        z-index: -1;
    }
    .bg-stars::before {
        content: '';
        position: absolute; top:0; left:0; width:100%; height:100%;
        background-image:
            radial-gradient(1px 1px at 5%  10%, #fff 0%, transparent 100%),
            radial-gradient(1px 1px at 15% 30%, #aaf 0%, transparent 100%),
            radial-gradient(1px 1px at 25% 5%,  #fff 0%, transparent 100%),
            radial-gradient(1px 1px at 35% 50%, #ffa 0%, transparent 100%),
            radial-gradient(1px 1px at 45% 75%, #fff 0%, transparent 100%),
            radial-gradient(1px 1px at 55% 20%, #aff 0%, transparent 100%),
            radial-gradient(1px 1px at 65% 65%, #fff 0%, transparent 100%),
            radial-gradient(1px 1px at 75% 40%, #faf 0%, transparent 100%),
            radial-gradient(1px 1px at 85% 15%, #fff 0%, transparent 100%),
            radial-gradient(1px 1px at 92% 85%, #aaf 0%, transparent 100%),
            radial-gradient(1px 1px at 10% 60%, #fff 0%, transparent 100%),
            radial-gradient(1px 1px at 70% 90%, #ffa 0%, transparent 100%);
        opacity: 0.7;
    }

    header {
        text-align: center;
        padding: 50px 20px 24px;
    }
    .header-title {
        font-size: 3.2rem;
        font-weight: 900;
        letter-spacing: 4px;
        text-transform: uppercase;
        background: linear-gradient(135deg, #FFD700, #FF4500, #FF69B4, #00BFFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: titlePulse 3s ease-in-out infinite;
        margin-bottom: 8px;
    }
    @keyframes titlePulse {
        0%, 100% { filter: brightness(1); }
        50%       { filter: brightness(1.5); }
    }
    .header-sub {
        color: #aaa;
        font-size: 1.1rem;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    .month-badge {
        display: inline-block;
        background: linear-gradient(135deg, #990AE3, #00BFFF);
        color: #fff;
        font-weight: 800;
        font-size: 1rem;
        padding: 6px 24px;
        border-radius: 30px;
        margin-top: 14px;
        letter-spacing: 3px;
    }
    .back-link {
        display: inline-block;
        margin-top: 16px;
        color: #555;
        font-size: 0.9rem;
        text-decoration: none;
        letter-spacing: 2px;
        transition: color 0.2s;
    }
    .back-link:hover { color: #aaa; }

    .arena {
        max-width: 1000px;
        margin: 0 auto;
        padding: 24px 20px 80px;
    }

    /* ── MATCHUP CARD ── */
    .matchup-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        margin-bottom: 36px;
        overflow: hidden;
        position: relative;
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .matchup-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.5);
    }
    .matchup-number {
        text-align: center;
        font-size: 0.85rem;
        letter-spacing: 4px;
        color: #555;
        padding: 18px 0 0;
        text-transform: uppercase;
    }

    .fighters-row {
        display: flex;
        align-items: stretch;
        padding: 20px;
        gap: 0;
    }

    /* ── FIGHTER PANEL ── */
    .fighter {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px 16px 24px;
        border-radius: 18px;
        position: relative;
        transition: background 0.3s;
    }
    .fighter.winner {
        background: rgba(255,255,255,0.07);
    }

    /* ── AVATAR (emoji-based, always works) ── */
    .fighter-avatar {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3.8rem;
        margin-bottom: 14px;
        position: relative;
        border: 4px solid transparent;
        animation: avatarGlow 2s ease-in-out infinite;
        flex-shrink: 0;
    }
    @keyframes avatarGlow {
        0%, 100% { box-shadow: 0 0 14px var(--c), 0 0 28px var(--c); }
        50%       { box-shadow: 0 0 30px var(--c), 0 0 60px var(--c), 0 0 90px var(--c); }
    }
    .girl-glow { animation: girlGlow 2s ease-in-out infinite !important; }
    @keyframes girlGlow {
        0%, 100% { box-shadow: 0 0 16px #FF69B4, 0 0 32px #FF69B4, 0 0 6px #fff; }
        50%       { box-shadow: 0 0 32px #FF69B4, 0 0 64px #FF69B4, 0 0 100px #FF69B4, 0 0 12px #fff; }
    }

    .winner-crown {
        position: absolute;
        top: -20px;
        font-size: 1.6rem;
        display: none;
        filter: drop-shadow(0 0 8px gold);
    }
    .fighter.winner .winner-crown { display: block; }

    .fighter-anime {
        font-size: 0.85rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        opacity: 0.9;
        margin-bottom: 4px;
        font-weight: 800;
        text-align: center;
    }
    .fighter-jp {
        font-size: 1rem;
        color: #888;
        margin-bottom: 6px;
        text-align: center;
        letter-spacing: 1px;
    }
    .fighter-name {
        font-size: 1.1rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 4px;
        line-height: 1.3;
    }
    .fighter-ability {
        font-size: 0.82rem;
        letter-spacing: 1px;
        color: #666;
        margin-bottom: 6px;
        text-align: center;
        font-style: italic;
    }
    .fighter-hours {
        font-size: 0.82rem;
        color: #555;
        margin-bottom: 18px;
        letter-spacing: 1px;
    }

    .stat-row {
        display: flex;
        justify-content: center;
        gap: 28px;
        width: 100%;
    }
    .stat-box { text-align: center; }
    .stat-val {
        font-size: 2rem;
        font-weight: 900;
        line-height: 1;
    }
    .stat-lbl {
        font-size: 0.72rem;
        letter-spacing: 2px;
        color: #777;
        text-transform: uppercase;
        margin-top: 4px;
    }
    .power-badge {
        margin-top: 14px;
        font-size: 0.85rem;
        font-weight: 800;
        letter-spacing: 2px;
        padding: 5px 16px;
        border-radius: 14px;
        border: 1px solid currentColor;
    }

    /* ── VS COLUMN ── */
    .vs-col {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 14px;
        min-width: 70px;
    }
    .vs-circle {
        width: 62px; height: 62px;
        border-radius: 50%;
        background: linear-gradient(135deg, #FF4500, #FFD700);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 1.3rem;
        letter-spacing: 1px;
        box-shadow: 0 0 24px rgba(255,100,0,0.6);
        animation: vsPulse 1.5s ease-in-out infinite;
    }
    @keyframes vsPulse {
        0%, 100% { transform: scale(1);    box-shadow: 0 0 24px rgba(255,100,0,0.6); }
        50%       { transform: scale(1.15); box-shadow: 0 0 48px rgba(255,100,0,1); }
    }

    /* ── POWER BAR ── */
    .power-bar-section { padding: 0 28px 24px; }
    .power-bar-label {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        color: #666;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .power-bar-track {
        display: flex;
        height: 14px;
        border-radius: 7px;
        overflow: hidden;
        background: rgba(255,255,255,0.05);
    }
    .power-bar-left  { transition: width 1s ease; border-radius: 7px 0 0 7px; }
    .power-bar-right { transition: width 1s ease; border-radius: 0 7px 7px 0; }

    /* ── PER HOUR ── */
    .per-hour-row {
        display: flex;
        justify-content: space-between;
        padding: 12px 28px 8px;
        gap: 10px;
    }
    .ph-block {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.88rem;
        color: #aaa;
    }
    .ph-val { font-weight: 800; font-size: 1rem; }

    /* ── DRAW ── */
    .draw-banner {
        text-align: center;
        font-size: 1rem;
        letter-spacing: 3px;
        color: #FFD700;
        padding: 8px 0 16px;
        text-transform: uppercase;
    }

    /* ── SCOREBOARD ── */
    .scoreboard {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 36px;
    }
    .scoreboard h3 {
        text-align: center;
        font-size: 1rem;
        letter-spacing: 4px;
        color: #aaa;
        text-transform: uppercase;
        margin-bottom: 20px;
    }
    .score-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        font-size: 1rem;
    }
    .score-row:last-child { border-bottom: none; }
    .score-name { flex: 1; font-size: 1rem; }
    .score-val  { min-width: 80px; text-align: right; font-weight: 800; font-size: 1.1rem; }
    .rank-1 { color: #FFD700; }
    .rank-2 { color: #C0C0C0; }
    .rank-3 { color: #CD7F32; }

    footer {
        text-align: center;
        color: #333;
        font-size: 0.85rem;
        letter-spacing: 2px;
        padding-bottom: 40px;
    }
    """

    # ── BUILD MATCHUP HTML ────────────────────────────────────────────────────
    matchup_html = ''
    for i, md in enumerate(matchup_data):
        m  = md['matchup']
        ls = md['ls']
        rs = md['rs']

        wc  = winner_class(ls['power'], rs['power'])
        lw  = 'winner' if wc == 'left-wins'  else ''
        rw  = 'winner' if wc == 'right-wins' else ''

        lpct, rpct = bar_pct(ls['power'], rs['power'])
        lc  = m['left']['color']
        rc  = m['right']['color']
        lg  = m['left']['gradient']
        rg  = m['right']['gradient']

        draw_banner = '<div class="draw-banner">⚔️ DRAW ⚔️</div>' if wc == 'draw' else ''

        l_girl = 'girl-glow' if m['left'].get('is_girl')  else ''
        r_girl = 'girl-glow' if m['right'].get('is_girl') else ''

        matchup_html += f"""
        <div class="matchup-card {wc}">
            <div class="matchup-number">⚔️ KAMP {i+1}</div>
            <div class="fighters-row">

                <!-- LEFT FIGHTER -->
                <div class="fighter {lw}" style="--c:{lc}">
                    <div class="winner-crown">👑</div>
                    <div class="fighter-avatar {l_girl}" style="--c:{lc}; border-color:{lc}; background:{lg};">
                        {m['left']['emoji']}
                    </div>
                    <div class="fighter-anime" style="color:{lc}">{m['left']['anime']}</div>
                    <div class="fighter-jp">{m['left']['jp']}</div>
                    <div class="fighter-name">{m['left']['name']}</div>
                    <div class="fighter-ability">{m['left']['ability']}</div>
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

                <!-- RIGHT FIGHTER -->
                <div class="fighter {rw}" style="--c:{rc}">
                    <div class="winner-crown">👑</div>
                    <div class="fighter-avatar {r_girl}" style="--c:{rc}; border-color:{rc}; background:{rg};">
                        {m['right']['emoji']}
                    </div>
                    <div class="fighter-anime" style="color:{rc}">{m['right']['anime']}</div>
                    <div class="fighter-jp">{m['right']['jp']}</div>
                    <div class="fighter-name">{m['right']['name']}</div>
                    <div class="fighter-ability">{m['right']['ability']}</div>
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
                    <span style="color:#555">⚡ POWER LEVEL ⚡</span>
                    <span style="color:{rc}">{m['right']['name'].split()[0]}</span>
                </div>
                <div class="power-bar-track">
                    <div class="power-bar-left"  style="width:{lpct}%; background:{lc}"></div>
                    <div class="power-bar-right" style="width:{rpct}%; background:{rc}"></div>
                </div>
            </div>
            {draw_banner}
        </div>
        """

    # ── POWER RANKING ─────────────────────────────────────────────────────────
    all_fighters = []
    for md in matchup_data:
        m  = md['matchup']
        ls = md['ls']
        rs = md['rs']
        all_fighters.append((m['left']['name'],  ls['power'], ls['gross'], ls['trygg'],
                              m['left']['color'],  m['left']['emoji'],  m['left']['anime']))
        all_fighters.append((m['right']['name'], rs['power'], rs['gross'], rs['trygg'],
                              m['right']['color'], m['right']['emoji'], m['right']['anime']))

    all_fighters.sort(key=lambda x: x[1], reverse=True)
    rank_classes = ['rank-1', 'rank-2', 'rank-3']
    rank_emojis  = ['🥇', '🥈', '🥉']

    ranking_rows = ''
    for idx, (name, power, gross, trygg, color, emoji, anime) in enumerate(all_fighters):
        rc_cls = rank_classes[idx] if idx < 3 else ''
        re_lbl = rank_emojis[idx]  if idx < 3 else f'#{idx+1}'
        ranking_rows += f"""
        <div class="score-row">
            <span style="min-width:36px; text-align:center; font-size:1.2rem">{re_lbl}</span>
            <span class="score-name {rc_cls}" style="margin-left:12px">
                {emoji} <strong>{name}</strong>
                <span style="color:#444; font-size:0.8rem; margin-left:8px">{anime}</span>
            </span>
            <span class="score-val" style="color:{color}">{power}</span>
        </div>"""

    # ── FULL HTML ──────────────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1000">
<title>⚔️ Gulskogen Konkurranse — Mai 2026</title>
<style>{css}</style>
</head>
<body>
<div class="bg-stars"></div>

<header>
    <div class="header-title">⚔️ Gulskogen Arena ⚔️</div>
    <div class="header-sub">Hvem dominerer mai — per time?</div>
    <div class="month-badge">MAI 2026</div>
    <div style="margin-top:16px;">
        <a href="index.html" class="back-link">← Tilbake til dashboard</a>
    </div>
</header>

<div class="arena">

    <!-- POWER RANKING -->
    <div class="scoreboard">
        <h3>⚡ Power Ranking — Mai 2026</h3>
        {ranking_rows}
        <div style="text-align:center; font-size:0.78rem; color:#444; margin-top:14px; letter-spacing:1px">
            ⚡ POWER = (Gross/time × 10) + (T.Trygg/time × 5)
        </div>
    </div>

    <!-- MATCHUPS -->
    {matchup_html}

</div>

<footer>
    <p>TELIA DRAMMEN &nbsp;·&nbsp; GULSKOGEN &nbsp;·&nbsp; MAI 2026</p>
    <p style="margin-top:6px; font-size:0.72rem;">Oppdateres automatisk ved ny rapport</p>
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
    print(f"✅ konkurranse.html generert ({len(html):,} bytes)")
