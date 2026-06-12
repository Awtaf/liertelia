#!/usr/bin/env python3
"""
GULSKOGEN WORLD CUP — Juni 2026
Stunning football competition page with CSS-designed jerseys and stadium atmosphere
"""

import json, os

SCRIPT_DIR = '/tasklet/agent/home'

# Load data
with open(os.path.join(SCRIPT_DIR, 'complete_extracted_data.json'), 'r') as f:
    all_data = json.load(f)

jun_data = all_data.get('gulskogen', {}).get('jun', {})
sellers = jun_data.get('sellers', [])

# Player configuration
PLAYERS = [
    {'seller': 'Ahmed Al Ali', 'char': 'Cristiano Ronaldo', 'short': 'CR7', 'team': 'Portugal', 'number': 7, 'flag': '🇵🇹',
     'c1': '#C4161C', 'c2': '#8B0000', 'accent': '#FFD700', 'collar': '#065A34', 'text_col': '#fff'},
    {'seller': 'Saidt Oliver Alavi', 'char': 'Zlatan Ibrahimović', 'short': 'Zlatan', 'team': 'Sverige', 'number': 10, 'flag': '🇸🇪',
     'c1': '#FECC02', 'c2': '#D4A800', 'accent': '#006AA7', 'collar': '#006AA7', 'text_col': '#006AA7'},
    {'seller': 'Aya Mohammad', 'char': 'Nouhaila Benzina', 'short': 'Benzina', 'team': 'Marokko', 'number': 5, 'flag': '🇲🇦',
     'c1': '#C1272D', 'c2': '#8B0000', 'accent': '#006233', 'collar': '#006233', 'text_col': '#fff'},
    {'seller': 'Ali Esmati', 'char': 'Lionel Messi', 'short': 'Messi', 'team': 'Argentina', 'number': 10, 'flag': '🇦🇷',
     'c1': '#75AADB', 'c2': '#5A8FBF', 'accent': '#FFFFFF', 'collar': '#F7F7F7', 'text_col': '#1a1a2e',
     'stripes': True},
    {'seller': 'Tommy Olafsen', 'char': 'Adebayo Akinfenwa', 'short': 'Beast', 'team': 'England', 'number': 45, 'flag': '🏴\u200d☠️',
     'c1': '#FFFFFF', 'c2': '#E8E8E8', 'accent': '#CF081F', 'collar': '#1D3461', 'text_col': '#1D3461'},
    {'seller': 'Kasim Al Ali', 'char': 'Erling Haaland', 'short': 'Haaland', 'team': 'Norge', 'number': 9, 'flag': '🇳🇴',
     'c1': '#BA0C2F', 'c2': '#8B0000', 'accent': '#002868', 'collar': '#fff', 'text_col': '#fff'},
    {'seller': 'Yasin Ali Ismail', 'char': 'Kylian Mbappé', 'short': 'Mbappé', 'team': 'Frankrike', 'number': 10, 'flag': '🇫🇷',
     'c1': '#002654', 'c2': '#001A3A', 'accent': '#ED2939', 'collar': '#ED2939', 'text_col': '#fff'},
    {'seller': 'Mert Ambarduzgun', 'char': 'Neymar Jr', 'short': 'Neymar', 'team': 'Brasil', 'number': 10, 'flag': '🇧🇷',
     'c1': '#FFDF00', 'c2': '#D4B800', 'accent': '#009739', 'collar': '#009739', 'text_col': '#009739'},
    {'seller': 'Josef Ishan Latif Mossaiar', 'char': 'Mohamed Salah', 'short': 'Salah', 'team': 'Egypt', 'number': 11, 'flag': '🇪🇬',
     'c1': '#CE1126', 'c2': '#8B0000', 'accent': '#C09B1C', 'collar': '#fff', 'text_col': '#fff'},
]

MATCHES = [
    {'a': 'Ahmed Al Ali', 'b': 'Saidt Oliver Alavi', 'hours_a': 113, 'hours_b': 116},
    {'a': 'Tommy Olafsen', 'b': 'Ali Esmati', 'hours_a': 120, 'hours_b': 123},
    {'a': 'Kasim Al Ali', 'b': 'Yasin Ali Ismail', 'hours_a': 30, 'hours_b': 30},
    {'a': 'Mert Ambarduzgun', 'b': 'Josef Ishan Latif Mossaiar', 'hours_a': 52, 'hours_b': 55},
    {'a': 'Aya Mohammad', 'b': 'Kasim+Yasin', 'hours_a': 85, 'hours_b': 60, 'combo': True},
]

def find_seller(name, sellers):
    nl = name.lower()
    for s in sellers:
        if nl in s['navn'].lower() or s['navn'].lower() in nl:
            return s
    parts = nl.split()
    for s in sellers:
        sp = s['navn'].lower().split()
        if any(p in sp for p in parts if len(p) > 2):
            return s
    return None

def get_pc(name):
    for p in PLAYERS:
        if p['seller'].lower() in name.lower() or name.lower() in p['seller'].lower():
            return p
    for p in PLAYERS:
        parts = p['seller'].lower().split()
        nparts = name.lower().split()
        if any(pa in nparts for pa in parts if len(pa) > 2):
            return p
    return None

# Build stats
for p in PLAYERS:
    s = find_seller(p['seller'], sellers)
    p['gross'] = s['gross'] if s else 0
    p['trygg'] = s['trygg'] if s else 0
    p['forsikring'] = s.get('forsikring', 0) if s else 0

# Calculate match results
for m in MATCHES:
    if m.get('combo'):
        sa = find_seller(m['a'], sellers)
        sk = find_seller('Kasim', sellers)
        sy = find_seller('Yasin', sellers)
        m['gross_a'] = sa['gross'] if sa else 0
        m['trygg_a'] = sa['trygg'] if sa else 0
        m['gross_b'] = (sk['gross'] if sk else 0) + (sy['gross'] if sy else 0)
        m['trygg_b'] = (sk['trygg'] if sk else 0) + (sy['trygg'] if sy else 0)
    else:
        sa = find_seller(m['a'], sellers)
        sb = find_seller(m['b'], sellers)
        m['gross_a'] = sa['gross'] if sa else 0
        m['trygg_a'] = sa['trygg'] if sa else 0
        m['gross_b'] = sb['gross'] if sb else 0
        m['trygg_b'] = sb['trygg'] if sb else 0
    
    ha, hb = m['hours_a'], m['hours_b']
    m['score_a'] = round((m['gross_a']/ha)*10 + (m['trygg_a']/ha)*5, 2) if ha > 0 else 0
    m['score_b'] = round((m['gross_b']/hb)*10 + (m['trygg_b']/hb)*5, 2) if hb > 0 else 0
    m['winner'] = 'a' if m['score_a'] > m['score_b'] else ('b' if m['score_b'] > m['score_a'] else 'draw')

    # Get player configs
    m['pc_a'] = get_pc(m['a'])
    if m.get('combo'):
        m['pc_b'] = {'short': 'Duo', 'char': 'Haaland + Mbappé', 'flag': '🇳🇴🇫🇷', 'c1': '#BA0C2F', 'c2': '#002654', 'accent': '#FFD700', 'collar': '#fff', 'number': '9+10', 'text_col': '#fff', 'team': 'Norge+Frankrike'}
    else:
        m['pc_b'] = get_pc(m['b'])

# Rankings
all_scores = []
for p in PLAYERS:
    # Find which match this player is in
    total_score = 0
    for m_idx, m in enumerate(MATCHES):
        if m['a'] == p['seller']:
            total_score = m['score_a']
        elif m['b'] == p['seller']:
            total_score = m['score_b']
    p['score'] = total_score

rankings = sorted(PLAYERS, key=lambda x: x['score'], reverse=True)

# Jersey SVG generator
def jersey_svg(pid, c1, c2, accent, collar, number, text_col, size=100, stripes=False):
    """Generate a beautiful SVG jersey"""
    stripe_extra = ''
    if stripes:
        stripe_extra = f'''
        <rect x="45" y="0" width="8" height="170" fill="white" opacity="0.4"/>
        <rect x="61" y="0" width="8" height="170" fill="white" opacity="0.4"/>
        <rect x="77" y="0" width="8" height="170" fill="white" opacity="0.4"/>
        <rect x="93" y="0" width="8" height="170" fill="white" opacity="0.4"/>'''
    
    num_str = str(number)
    font_size = 36 if len(num_str) <= 2 else 24
    
    return f'''<svg viewBox="0 0 140 170" width="{size}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="jg_{pid}" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="{c1}"/>
          <stop offset="100%" stop-color="{c2}"/>
        </linearGradient>
        <filter id="js_{pid}">
          <feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="rgba(0,0,0,0.4)"/>
        </filter>
        <clipPath id="jc_{pid}">
          <path d="M35,5 L0,30 L18,70 L38,58 L38,165 L102,165 L102,58 L122,70 L140,30 L105,5 L90,18 Q70,28 50,18 Z"/>
        </clipPath>
      </defs>
      <g filter="url(#js_{pid})">
        <path d="M35,5 L0,30 L18,70 L38,58 L38,165 L102,165 L102,58 L122,70 L140,30 L105,5 L90,18 Q70,28 50,18 Z" 
              fill="url(#jg_{pid})" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
        <g clip-path="url(#jc_{pid})">{stripe_extra}</g>
        <path d="M50,18 Q70,28 90,18 Q80,8 70,12 Q60,8 50,18 Z" fill="{collar}" opacity="0.9"/>
        <line x1="0" y1="30" x2="18" y2="70" stroke="{accent}" stroke-width="2" opacity="0.6"/>
        <line x1="140" y1="30" x2="122" y2="70" stroke="{accent}" stroke-width="2" opacity="0.6"/>
        <text x="70" y="120" text-anchor="middle" fill="{text_col}" font-size="{font_size}" font-weight="900" 
              style="text-shadow:1px 1px 3px rgba(0,0,0,0.5)" font-family="Arial,sans-serif">{num_str}</text>
      </g>
    </svg>'''

# Generate match cards HTML
def match_card(m, idx):
    pa, pb = m['pc_a'], m['pc_b']
    if not pa or not pb:
        return ''
    
    win_a = 'winner-glow' if m['winner'] == 'a' else ''
    win_b = 'winner-glow' if m['winner'] == 'b' else ''
    dim_a = 'dimmed' if m['winner'] == 'b' else ''
    dim_b = 'dimmed' if m['winner'] == 'a' else ''
    
    # Score bar percentages
    total = m['score_a'] + m['score_b'] if (m['score_a'] + m['score_b']) > 0 else 1
    pct_a = (m['score_a'] / total) * 100
    pct_b = (m['score_b'] / total) * 100
    
    jersey_a = jersey_svg(f'm{idx}a', pa['c1'], pa['c2'], pa.get('accent','#fff'), pa.get('collar','#fff'), pa['number'], pa.get('text_col','#fff'), 90, pa.get('stripes', False))
    
    num_b = pb.get('number', '9+10')
    jersey_b = jersey_svg(f'm{idx}b', pb['c1'], pb['c2'], pb.get('accent','#fff'), pb.get('collar','#fff'), num_b, pb.get('text_col','#fff'), 90, pb.get('stripes', False))
    
    winner_badge = ''
    if m['winner'] == 'a':
        winner_badge = f'<div class="match-winner-badge left">⚽ LEDER</div>'
    elif m['winner'] == 'b':
        winner_badge = f'<div class="match-winner-badge right">⚽ LEDER</div>'
    else:
        winner_badge = '<div class="match-winner-badge center">🤝 UAVGJORT</div>'
    
    combo_label = '<div class="combo-tag">DUO</div>' if m.get('combo') else ''
    
    name_b = m['b'] if not m.get('combo') else 'Kasim + Yasin'
    char_b = pb.get('char', 'Duo')
    
    return f'''
    <div class="match-card" style="animation-delay:{idx*0.15}s">
      <div class="match-header">
        <span class="match-num">KAMP {idx+1}</span>
        <span class="match-live">🔴 LIVE</span>
      </div>
      <div class="match-body">
        <div class="match-player {win_a} {dim_a}">
          <div class="jersey-wrap">{jersey_a}</div>
          <div class="player-name">{m['a'].split()[0]}</div>
          <div class="player-char">{pa['short']} {pa['flag']}</div>
          <div class="player-stats-mini">
            <span>⚽ {m['gross_a']}</span>
            <span>🛡️ {m['trygg_a']}</span>
          </div>
          <div class="player-hours">{m['hours_a']}t</div>
        </div>
        
        <div class="match-center">
          <div class="match-score">
            <span class="score-num {'score-win' if m['winner']=='a' else ''}">{m['score_a']}</span>
            <span class="vs-divider">VS</span>
            <span class="score-num {'score-win' if m['winner']=='b' else ''}">{m['score_b']}</span>
          </div>
          <div class="score-bar">
            <div class="score-bar-a" style="width:{pct_a}%;background:{pa['c1']}"></div>
            <div class="score-bar-b" style="width:{pct_b}%;background:{pb['c1']}"></div>
          </div>
          {winner_badge}
          {combo_label}
        </div>
        
        <div class="match-player {win_b} {dim_b}">
          <div class="jersey-wrap">{jersey_b}</div>
          <div class="player-name">{name_b.split()[0] if not m.get('combo') else 'Kasim+Yasin'}</div>
          <div class="player-char">{pb['short']} {pb['flag']}</div>
          <div class="player-stats-mini">
            <span>⚽ {m['gross_b']}</span>
            <span>🛡️ {m['trygg_b']}</span>
          </div>
          <div class="player-hours">{m['hours_b']}t</div>
        </div>
      </div>
    </div>'''

match_cards = '\n'.join(match_card(m, i) for i, m in enumerate(MATCHES))

# Standings table rows
standings_rows = ''
for i, p in enumerate(rankings):
    rank_class = 'rank-gold' if i == 0 else ('rank-silver' if i == 1 else ('rank-bronze' if i == 2 else ''))
    crown = '👑' if i == 0 else ('🥈' if i == 1 else ('🥉' if i == 2 else ''))
    jersey = jersey_svg(f'r{i}', p['c1'], p['c2'], p.get('accent','#fff'), p.get('collar','#fff'), p['number'], p.get('text_col','#fff'), 40, p.get('stripes', False))
    
    fire = '🔥' if p['score'] > 2 else ''
    
    standings_rows += f'''
    <tr class="{rank_class}">
      <td class="rank-col">{crown if crown else i+1}</td>
      <td class="jersey-col">{jersey}</td>
      <td class="name-col">
        <div class="standing-name">{p['seller']}</div>
        <div class="standing-char">{p['short']} {p['flag']}</div>
      </td>
      <td class="stat-col">{p['gross']}</td>
      <td class="stat-col">{p['trygg']}</td>
      <td class="score-col">{p['score']} {fire}</td>
    </tr>'''

# MVP section
mvp = rankings[0]
mvp_jersey = jersey_svg('mvp', mvp['c1'], mvp['c2'], mvp.get('accent','#fff'), mvp.get('collar','#fff'), mvp['number'], mvp.get('text_col','#fff'), 150, mvp.get('stripes', False))

# Totals
total_gross = sum(p['gross'] for p in PLAYERS)
total_trygg = sum(p['trygg'] for p in PLAYERS)

# Build HTML
html = f'''<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>⚽ Gulskogen World Cup — Juni 2026</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-10px)}}}}
@keyframes glow{{0%,100%{{opacity:0.6}}50%{{opacity:1}}}}
@keyframes pulse{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.05)}}}}
@keyframes shimmer{{0%{{background-position:-200% 0}}100%{{background-position:200% 0}}}}
@keyframes slideUp{{from{{opacity:0;transform:translateY(30px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes rotateBall{{0%{{transform:rotate(0deg)}}100%{{transform:rotate(360deg)}}}}
@keyframes fireFlicker{{0%,100%{{text-shadow:0 0 10px #ff6b00,0 0 20px #ff4500}}50%{{text-shadow:0 0 20px #ff8c00,0 0 40px #ff6347}}}}
@keyframes spotlight{{0%,100%{{opacity:0.3;transform:scaleX(1)}}50%{{opacity:0.6;transform:scaleX(1.2)}}}}
@keyframes confetti{{0%{{transform:translateY(-10px) rotate(0deg);opacity:1}}100%{{transform:translateY(100vh) rotate(720deg);opacity:0}}}}

body{{
  font-family:'Segoe UI',system-ui,-apple-system,sans-serif;
  background:#0a0a1a;
  color:#fff;
  min-height:100vh;
  overflow-x:hidden;
}}

/* HERO */
.hero{{
  position:relative;
  padding:60px 20px 40px;
  text-align:center;
  overflow:hidden;
  background:linear-gradient(180deg,#0d1f0d 0%,#0a0a1a 100%);
}}
.hero::before{{
  content:'';position:absolute;top:-50%;left:50%;transform:translateX(-50%);
  width:300%;height:200%;
  background:radial-gradient(ellipse at center,rgba(255,215,0,0.08) 0%,transparent 60%);
  animation:spotlight 6s ease-in-out infinite;
}}
.hero::after{{
  content:'';position:absolute;bottom:0;left:0;right:0;height:4px;
  background:linear-gradient(90deg,transparent,#FFD700,transparent);
}}
.stadium-lines{{
  position:absolute;top:0;left:0;right:0;bottom:0;
  background:repeating-linear-gradient(0deg,transparent 0px,transparent 38px,rgba(255,255,255,0.02) 38px,rgba(255,255,255,0.02) 40px);
  pointer-events:none;
}}
.floodlights{{
  position:absolute;top:0;left:0;right:0;display:flex;justify-content:space-between;padding:0 10%;
}}
.floodlight{{
  width:3px;height:80px;
  background:linear-gradient(180deg,rgba(255,255,200,0.8),transparent);
  animation:glow 3s ease-in-out infinite;
}}
.floodlight:nth-child(2){{animation-delay:0.5s}}
.floodlight:nth-child(3){{animation-delay:1s}}
.floodlight:nth-child(4){{animation-delay:1.5s}}

.hero-ball{{
  font-size:50px;
  animation:rotateBall 4s linear infinite;
  display:inline-block;
  margin-bottom:10px;
}}
.hero h1{{
  font-size:clamp(28px,6vw,56px);
  font-weight:900;
  letter-spacing:3px;
  text-transform:uppercase;
  background:linear-gradient(135deg,#FFD700,#FFA500,#FFD700);
  background-size:200% auto;
  animation:shimmer 3s linear infinite;
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  background-clip:text;
  margin-bottom:5px;
}}
.hero h2{{
  font-size:clamp(16px,3vw,24px);
  color:rgba(255,255,255,0.6);
  font-weight:400;
  letter-spacing:8px;
  text-transform:uppercase;
  margin-bottom:25px;
}}
.hero-stats{{
  display:flex;gap:20px;justify-content:center;flex-wrap:wrap;
}}
.hero-stat{{
  background:rgba(255,255,255,0.05);
  border:1px solid rgba(255,255,255,0.1);
  border-radius:12px;padding:15px 25px;
  backdrop-filter:blur(10px);
}}
.hero-stat .hs-val{{font-size:28px;font-weight:800;color:#FFD700}}
.hero-stat .hs-lbl{{font-size:12px;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:2px}}

/* SECTION */
.section{{padding:40px 20px;max-width:1100px;margin:0 auto;animation:slideUp 0.8s ease}}
.section-title{{
  font-size:clamp(20px,4vw,32px);font-weight:800;text-align:center;margin-bottom:30px;
  display:flex;align-items:center;justify-content:center;gap:12px;
}}
.section-title .st-line{{flex:1;max-width:100px;height:2px;background:linear-gradient(90deg,transparent,rgba(255,215,0,0.4))}}
.section-title .st-line.right{{background:linear-gradient(90deg,rgba(255,215,0,0.4),transparent)}}

/* STANDINGS */
.standings-table{{
  width:100%;border-collapse:separate;border-spacing:0 4px;
}}
.standings-table th{{
  padding:10px 15px;text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:2px;
  color:rgba(255,255,255,0.4);border-bottom:1px solid rgba(255,255,255,0.1);
}}
.standings-table td{{padding:10px 15px;vertical-align:middle}}
.standings-table tr{{
  background:rgba(255,255,255,0.03);
  transition:all 0.3s;
  border-radius:8px;
}}
.standings-table tr:hover{{background:rgba(255,255,255,0.08);transform:scale(1.01)}}
.rank-gold{{background:rgba(255,215,0,0.08)!important;border-left:3px solid #FFD700}}
.rank-gold td:first-child{{font-size:24px}}
.rank-silver{{background:rgba(192,192,192,0.05)!important}}
.rank-silver td:first-child{{font-size:20px}}
.rank-bronze{{background:rgba(205,127,50,0.05)!important}}
.rank-bronze td:first-child{{font-size:18px}}
.rank-col{{font-size:16px;font-weight:700;width:40px;text-align:center}}
.jersey-col{{width:50px}}
.jersey-col svg{{vertical-align:middle}}
.name-col{{min-width:140px}}
.standing-name{{font-weight:700;font-size:14px}}
.standing-char{{font-size:12px;color:rgba(255,255,255,0.5)}}
.stat-col{{text-align:center;font-weight:600;font-size:16px}}
.score-col{{text-align:center;font-weight:800;font-size:18px;color:#FFD700}}

/* MATCH CARDS */
.matches-grid{{display:flex;flex-direction:column;gap:20px}}
.match-card{{
  background:linear-gradient(135deg,rgba(255,255,255,0.04),rgba(255,255,255,0.01));
  border:1px solid rgba(255,255,255,0.08);
  border-radius:20px;
  overflow:hidden;
  animation:slideUp 0.6s ease both;
  transition:transform 0.3s,box-shadow 0.3s;
}}
.match-card:hover{{transform:translateY(-4px);box-shadow:0 10px 40px rgba(0,0,0,0.3)}}
.match-header{{
  display:flex;justify-content:space-between;align-items:center;
  padding:12px 20px;
  background:rgba(255,255,255,0.03);
  border-bottom:1px solid rgba(255,255,255,0.05);
}}
.match-num{{font-size:12px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:rgba(255,255,255,0.5)}}
.match-live{{font-size:11px;letter-spacing:2px;animation:pulse 2s infinite}}
.match-body{{
  display:grid;
  grid-template-columns:1fr auto 1fr;
  gap:10px;
  padding:25px 15px;
  align-items:center;
}}
.match-player{{text-align:center;transition:all 0.3s}}
.match-player.dimmed{{opacity:0.5;filter:grayscale(0.5)}}
.jersey-wrap{{margin-bottom:8px;transition:transform 0.3s}}
.match-player:not(.dimmed) .jersey-wrap:hover{{transform:scale(1.1) rotate(-3deg)}}
.winner-glow .jersey-wrap{{animation:pulse 2s infinite;filter:drop-shadow(0 0 15px rgba(255,215,0,0.4))}}
.player-name{{font-weight:700;font-size:14px;margin-bottom:2px}}
.player-char{{font-size:12px;color:rgba(255,255,255,0.5)}}
.player-stats-mini{{display:flex;gap:10px;justify-content:center;margin-top:8px;font-size:13px}}
.player-stats-mini span{{
  background:rgba(255,255,255,0.06);padding:3px 8px;border-radius:6px;
}}
.player-hours{{font-size:11px;color:rgba(255,255,255,0.3);margin-top:4px}}

.match-center{{
  display:flex;flex-direction:column;align-items:center;gap:10px;
  min-width:110px;
}}
.match-score{{display:flex;align-items:center;gap:8px}}
.score-num{{
  font-size:24px;font-weight:900;
  background:rgba(255,255,255,0.05);
  padding:8px 12px;border-radius:10px;
  min-width:55px;text-align:center;
}}
.score-win{{
  background:linear-gradient(135deg,rgba(255,215,0,0.2),rgba(255,165,0,0.1));
  color:#FFD700;
  box-shadow:0 0 20px rgba(255,215,0,0.15);
}}
.vs-divider{{
  font-size:12px;font-weight:800;color:rgba(255,255,255,0.3);
  letter-spacing:2px;
}}
.score-bar{{
  display:flex;width:100%;height:6px;border-radius:3px;overflow:hidden;
  background:rgba(255,255,255,0.05);
}}
.score-bar-a,.score-bar-b{{height:100%;transition:width 1s ease}}
.match-winner-badge{{
  font-size:11px;font-weight:700;letter-spacing:2px;
  padding:4px 12px;border-radius:20px;
  background:rgba(255,215,0,0.15);color:#FFD700;
  border:1px solid rgba(255,215,0,0.3);
}}
.combo-tag{{
  font-size:10px;padding:2px 8px;border-radius:4px;
  background:rgba(255,107,53,0.2);color:#FF6B35;
  margin-top:4px;
}}

/* MVP SECTION */
.mvp-section{{
  text-align:center;padding:50px 20px;
  background:linear-gradient(180deg,rgba(255,215,0,0.03),transparent);
  position:relative;
}}
.mvp-card{{
  display:inline-block;
  background:linear-gradient(135deg,rgba(255,215,0,0.1),rgba(255,165,0,0.03));
  border:2px solid rgba(255,215,0,0.3);
  border-radius:24px;
  padding:40px 50px;
  position:relative;
  animation:pulse 3s infinite;
}}
.mvp-crown{{font-size:60px;margin-bottom:10px;animation:float 3s ease-in-out infinite}}
.mvp-jersey{{margin:15px 0;filter:drop-shadow(0 0 30px rgba(255,215,0,0.3))}}
.mvp-name{{font-size:28px;font-weight:900;margin-bottom:5px}}
.mvp-char{{font-size:18px;color:rgba(255,255,255,0.5);margin-bottom:15px}}
.mvp-stats{{display:flex;gap:25px;justify-content:center}}
.mvp-stat{{text-align:center}}
.mvp-stat .mv{{font-size:32px;font-weight:900;color:#FFD700}}
.mvp-stat .ml{{font-size:11px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:2px}}

/* QUOTE */
.quote-section{{
  text-align:center;padding:40px 20px 60px;
}}
.quote{{
  font-size:clamp(16px,3vw,22px);
  font-style:italic;
  color:rgba(255,255,255,0.4);
  max-width:600px;margin:0 auto;
  line-height:1.6;
}}
.quote-author{{
  margin-top:10px;font-size:14px;color:rgba(255,215,0,0.5);font-style:normal;
}}

/* FORMULA */
.formula-box{{
  text-align:center;padding:15px;margin:30px auto;max-width:500px;
  background:rgba(255,255,255,0.03);border-radius:12px;
  border:1px solid rgba(255,255,255,0.06);
}}
.formula-box code{{
  font-size:14px;color:#00E5FF;font-family:'Courier New',monospace;
}}
.formula-label{{font-size:11px;color:rgba(255,255,255,0.3);margin-bottom:5px;text-transform:uppercase;letter-spacing:2px}}

/* RESPONSIVE */
@media(max-width:700px){{
  .match-body{{grid-template-columns:1fr;gap:15px}}
  .match-center{{order:-1}}
  .match-player{{display:flex;align-items:center;gap:12px;text-align:left}}
  .jersey-wrap{{flex-shrink:0}}
  .match-score{{flex-direction:row}}
  .hero h1{{letter-spacing:1px}}
  .standings-table{{font-size:13px}}
  .standings-table th,.standings-table td{{padding:8px 6px}}
  .jersey-col svg{{width:30px}}
  .mvp-card{{padding:30px 20px}}
}}
</style>
</head>
<body>

<!-- HERO -->
<div class="hero">
  <div class="stadium-lines"></div>
  <div class="floodlights">
    <div class="floodlight"></div>
    <div class="floodlight"></div>
    <div class="floodlight"></div>
    <div class="floodlight"></div>
  </div>
  <div class="hero-ball">⚽</div>
  <h1>Gulskogen World Cup</h1>
  <h2>Juni 2026</h2>
  <div class="hero-stats">
    <div class="hero-stat">
      <div class="hs-val">{total_gross}</div>
      <div class="hs-lbl">Total Gross</div>
    </div>
    <div class="hero-stat">
      <div class="hs-val">{total_trygg}</div>
      <div class="hs-lbl">Total Trygg</div>
    </div>
    <div class="hero-stat">
      <div class="hs-val">{len(PLAYERS)}</div>
      <div class="hs-lbl">Spillere</div>
    </div>
  </div>
</div>

<!-- MVP -->
<div class="mvp-section section">
  <div class="section-title">
    <span class="st-line"></span>
    <span>👑 MÅNEDENS SPILLER</span>
    <span class="st-line right"></span>
  </div>
  <div class="mvp-card">
    <div class="mvp-crown">👑</div>
    <div class="mvp-jersey">{mvp_jersey}</div>
    <div class="mvp-name">{mvp['seller']}</div>
    <div class="mvp-char">{mvp['char']} {mvp['flag']}</div>
    <div class="mvp-stats">
      <div class="mvp-stat"><div class="mv">{mvp['gross']}</div><div class="ml">Gross</div></div>
      <div class="mvp-stat"><div class="mv">{mvp['trygg']}</div><div class="ml">Trygg</div></div>
      <div class="mvp-stat"><div class="mv">{mvp['score']}</div><div class="ml">Rating</div></div>
    </div>
  </div>
</div>

<!-- STANDINGS -->
<div class="section">
  <div class="section-title">
    <span class="st-line"></span>
    <span>🏆 TABELLEN</span>
    <span class="st-line right"></span>
  </div>
  <div style="overflow-x:auto">
  <table class="standings-table">
    <thead>
      <tr>
        <th>#</th>
        <th></th>
        <th>Spiller</th>
        <th style="text-align:center">⚽ Gross</th>
        <th style="text-align:center">🛡️ Trygg</th>
        <th style="text-align:center">⭐ Rating</th>
      </tr>
    </thead>
    <tbody>
      {standings_rows}
    </tbody>
  </table>
  </div>
  <div class="formula-box">
    <div class="formula-label">Beregning (per arbeidstimer)</div>
    <code>Rating = (Gross ÷ Timer) × 10 + (Trygg ÷ Timer) × 5</code>
  </div>
</div>

<!-- MATCHES -->
<div class="section">
  <div class="section-title">
    <span class="st-line"></span>
    <span>⚔️ KAMPENE</span>
    <span class="st-line right"></span>
  </div>
  <div class="matches-grid">
    {match_cards}
  </div>
</div>

<!-- MOTIVATIONAL QUOTE -->
<div class="quote-section">
  <div class="quote">
    "Hard work beats talent when talent doesn't work hard."
  </div>
  <div class="quote-author">— Tim Notke</div>
</div>

</body>
</html>'''

# Write
with open(os.path.join(SCRIPT_DIR, 'konkurranse.html'), 'w') as f:
    f.write(html)

print("✅ Konkurranse generated!")
print(f"   Total gross: {total_gross}, Total trygg: {total_trygg}")
print(f"   MVP: {mvp['seller']} ({mvp['short']}) — Score: {mvp['score']}")
for i, m in enumerate(MATCHES):
    w = m['a'].split()[0] if m['winner']=='a' else (m['b'].split()[0] if m['winner']=='b' else 'DRAW')
    print(f"   Kamp {i+1}: {m['a'].split()[0]} ({m['score_a']}) vs {m['b'].split()[0] if not m.get('combo') else 'Duo'} ({m['score_b']}) → {w}")
