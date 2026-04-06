import random
from players_data import PLAYERS, POSITION_EMOJI

PLAYER_MAP = {p["id"]: p for p in PLAYERS}

COMMENTARY_GOAL = [
    "⚽ GOAL! {scorer} fires it into the bottom corner!",
    "⚽ GOAL! What a finish from {scorer}!",
    "⚽ GOAL! {scorer} with a thunderbolt!",
    "⚽ GOAL! {scorer} slots it in calmly!",
    "⚽ GOAL! {scorer} heads it home!",
    "⚽ GOAL! {scorer} nutmegs the keeper!",
    "⚽ GOAL! A worldie from {scorer}! Top bins!",
    "⚽ GOAL! {scorer} with the tap-in!",
]

COMMENTARY_MISS = [
    "😬 {shooter} fires wide!",
    "🧤 Great save! Keeper denies {shooter}!",
    "😤 {shooter} hits the post!",
    "❌ {shooter} blazes it over!",
    "🛡 Brilliant defending — chance cleared!",
]

COMMENTARY_YELLOW = [
    "🟨 Yellow card! Reckless challenge.",
    "🟨 Booking! The referee isn't happy.",
    "🟨 Yellow card for a cynical foul.",
]

COMMENTARY_RED = [
    "🟥 RED CARD! A man is sent off!",
    "🟥 Straight red! Terrible challenge!",
]

COMMENTARY_PENALTY = [
    "🎯 PENALTY to {team}!",
]

def get_team_strength(player_ids):
    players = [PLAYER_MAP.get(pid) for pid in player_ids if PLAYER_MAP.get(pid)]
    if not players:
        return 50.0
    return sum(p["overall"] for p in players) / len(players)

def pick_scorer(player_ids):
    attackers = [PLAYER_MAP[pid] for pid in player_ids if PLAYER_MAP.get(pid) and PLAYER_MAP[pid]["position"] in ("ST","LW","RW","CAM")]
    pool = attackers if attackers else [PLAYER_MAP[pid] for pid in player_ids if PLAYER_MAP.get(pid)]
    if not pool:
        return "Unknown"
    weights = [p["shooting"] for p in pool]
    return random.choices(pool, weights=weights)[0]["name"]

def simulate_match(team1_ids, team2_ids, team1_name="Team 1", team2_name="Team 2"):
    str1 = get_team_strength(team1_ids)
    str2 = get_team_strength(team2_ids)
    total = str1 + str2
    t1_win_prob = str1 / total

    events = []
    score1, score2 = 0, 0
    minutes = sorted(random.sample(range(1, 91), random.randint(6, 14)))

    for minute in minutes:
        rnd = random.random()
        if rnd < 0.12:
            events.append((minute, random.choice(COMMENTARY_YELLOW)))
            continue
        if rnd < 0.14:
            events.append((minute, random.choice(COMMENTARY_RED)))
            continue

        team1_attacks = random.random() < t1_win_prob
        attacking_ids = team1_ids if team1_attacks else team2_ids
        att_strength = str1 if team1_attacks else str2
        def_strength = str2 if team1_attacks else str1
        team_name = team1_name if team1_attacks else team2_name

        is_penalty = random.random() < 0.08
        if is_penalty:
            events.append((minute, random.choice(COMMENTARY_PENALTY).format(team=team_name)))

        att_ratio = att_strength / (att_strength + def_strength)
        goal_chance = att_ratio + random.uniform(-0.25, 0.25)

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

def format_match_report(result):
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

def format_squad_card(player_ids, title="Squad"):
    lines = [f"*{title}*"]
    for pid in player_ids:
        p = PLAYER_MAP.get(pid)
        if p:
            pos_emoji = POSITION_EMOJI.get(p["position"], "⚽")
            lines.append(f"{pos_emoji} *{p['name']}* ({p['position']}) — OVR {p['overall']}")
    avg = get_team_strength(player_ids)
    lines.append(f"\n📊 Team OVR: *{avg:.0f}*")
    return "\n".join(lines)
