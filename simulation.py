"""
Match simulation engine.
Works for both full squad (11v11) and quick match (5v5).
"""
import random
from players_data import PLAYERS, POSITION_EMOJI

PLAYER_MAP = {p["id"]: p for p in PLAYERS}

COMMENTARY_GOAL = [
    "⚽ GOAL! {scorer} fires it into the bottom corner!",
    "⚽ GOAL! What a finish from {scorer}!",
    "⚽ GOAL! {scorer} with a thunderbolt — the keeper had no chance!",
    "⚽ GOAL! {scorer} slots it in calmly — pure class!",
    "⚽ GOAL! {scorer} heads it home from the corner!",
    "⚽ GOAL! {scorer} nutmegs the keeper — cheeky!",
    "⚽ GOAL! A worldie from {scorer}! Top bins!",
    "⚽ GOAL! {scorer} with the tap-in after a brilliant run!",
]

COMMENTARY_MISS = [
    "😬 {shooter} fires wide — so close!",
    "🧤 Great save! The keeper denies {shooter}!",
    "😤 {shooter} hits the post — unlucky!",
    "❌ {shooter} blazes it over the bar!",
    "🛡 Brilliant defending — the chance is cleared!",
]

COMMENTARY_YELLOW = [
    "🟨 Yellow card! Reckless challenge in midfield.",
    "🟨 Booking! The referee isn't happy.",
    "🟨 Yellow card for a cynical foul.",
]

COMMENTARY_RED = [
    "🟥 RED CARD! A man is sent off!",
    "🟥 Straight red! That's a terrible challenge!",
]

COMMENTARY_PENALTY = [
    "🎯 PENALTY to {team}! The referee points to the spot!",
]

def get_team_strength(player_ids: list) -> float:
    players = [PLAYER_MAP.get(pid) for pid in player_ids if PLAYER_MAP.get(pid)]
    if not players:
        return 50.0
    return sum(p["overall"] for p in players) / len(players)

def pick_scorer(player_ids: list) -> str:
    attackers = [PLAYER_MAP[pid] for pid in player_ids
                 if PLAYER_MAP.get(pid) and PLAYER_MAP[pid]["position"] in ("ST","LW","RW","CAM")]
    pool = attackers if attackers else [PLAYER_MAP[pid] for pid in player_ids if PLAYER_MAP.get(pid)]
    if not pool:
        return "Unknown"
    weights = [p["shooting"] for p in pool]
    return random.choices(pool, weights=weights)[0]["name"]

def simulate_match(team1_ids: list, team2_ids: list, team1_name: str = "Team 1", team2_name: str = "Team 2") -> dict:
    str1 = get_team_strength(team1_ids)
    str2 = get_team_strength(team2_ids)
    total = str1 + str2
    t1_win_prob = str1 / total

    events = []
    score1, score2 = 0, 0

    minutes = sorted(random.sample(range(1, 91), random.randint(6, 14)))

    for minute in minutes:
        rnd = random.random()
        # yellow card ~12%
        if rnd < 0.12:
            events.append((minute, random.choice(COMMENTARY_YELLOW)))
            continue
        # red card ~2%
        if rnd < 0.14:
            events.append((minute, random.choice(COMMENTARY_RED)))
            continue

        # shot event — who attacks?
        team1_attacks = random.random() < t1_win_prob
        attacking_ids = team1_ids if team1_attacks else team2_ids
        defending_ids = team2_ids if team1_attacks else team1_ids
        att_strength = str1 if team1_attacks else str2
        def_strength = str2 if team1_attacks else str1

        # penalty?
        is_penalty = random.random() < 0.08
        if is_penalty:
            team_name = team1_name if team1_attacks else team2_name
            events.append((minute, random.choice(COMMENTARY_PENALTY).format(team=team_name)))

        # goal probability: attacker strength vs defender strength + randomness
            goal_chance = (att_strength / (att_strength + def_strength)) + random.uniform(-0.25, 0.25)
            if goal_chance > 0.55:
            scorer = pick_scorer(attacking_ids)
            events.append((minute, random.choice(COMMENTARY_GOAL).format(scorer=scorer)))
            if team1_attacks:
                score1 += 1
            else:
                score2 += 1
        else:
            shooter = pick_scorer(attacking_ids)
            events.append((minute, random.choice(COMMENTARY_MISS).format(shooter=shooter)))

    return {
        "score1": score1,
        "score2": score2,
        "events": events,
        "team1_name": team1_name,
        "team2_name": team2_name,
    }

def format_match_report(result: dict) -> str:
    lines = []
    lines.append(f"🏟 *{result['team1_name']}  {result['score1']} — {result['score2']}  {result['team2_name']}*")
    lines.append("─" * 30)
    for minute, text in result["events"]:
        lines.append(f"`{minute:2d}'` {text}")
    lines.append("─" * 30)
    if result["score1"] > result["score2"]:
        lines.append(f"🏆 *{result['team1_name']} wins!*")
    elif result["score2"] > result["score1"]:
        lines.append(f"🏆 *{result['team2_name']} wins!*")
    else:
        lines.append("🤝 *It's a draw!*")
    return "\n".join(lines)

def format_squad_card(player_ids: list, title: str = "Squad") -> str:
    lines = [f"*{title}*"]
    for pid in player_ids:
        p = PLAYER_MAP.get(pid)
        if p:
            pos_emoji = POSITION_EMOJI.get(p["position"], "⚽")
            lines.append(f"{pos_emoji} *{p['name']}* ({p['position']}) — OVR {p['overall']}")
    avg = get_team_strength(player_ids)
    lines.append(f"\n📊 Team OVR: *{avg:.0f}*")
    return "\n".join(lines)
