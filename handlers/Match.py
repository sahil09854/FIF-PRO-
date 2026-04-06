import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import (get_or_create_user, get_user, get_squad, add_coins,
                       record_result, create_match, create_quick_draft,
                       get_quick_draft, update_quick_draft)
from simulation import simulate_match, format_match_report, format_squad_card
from players_data import PLAYERS, PLAYER_MAP, RARITY_EMOJI, POSITION_EMOJI

# In-memory pending challenges: {chat_id: {challenger_id: {type, opponent_id, ...}}}
pending_challenges = {}

# In-memory quick draft sessions: {match_id: {team1_user, team2_user, ...}}
draft_sessions = {}

QUICK_DRAFT_POOL_SIZE = 12
QUICK_DRAFT_PICKS = 5

WIN_COINS = 150
DRAW_COINS = 50
LOSS_COINS = 20

# ─── 1v1 Full Squad Challenge ────────────────────────────────────────────────

async def challenge_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    challenger = update.effective_user
    get_or_create_user(challenger.id, challenger.first_name)

    if not context.args:
        await update.message.reply_text(
            "Usage: `/challenge @username` — challenge someone to a 1v1\n"
            "Or use `/quickmatch @username` for a quick draft 5v5!",
            parse_mode="Markdown"
        )
        return

    challenger_squad = get_squad(challenger.id)
    if not challenger_squad["player_ids"]:
        await update.message.reply_text(
            "❌ You haven't set a squad! Use /setsquad first."
        )
        return

    mention = context.args[0].lstrip("@")
    chat_id = update.effective_chat.id

    # Store pending challenge
    if chat_id not in pending_challenges:
        pending_challenges[chat_id] = {}
    pending_challenges[chat_id][challenger.id] = {
        "type": "1v1",
        "challenger_name": challenger.first_name,
        "mention": mention,
    }

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Accept", callback_data=f"accept:{challenger.id}"),
        InlineKeyboardButton("❌ Decline", callback_data=f"decline:{challenger.id}"),
    ]])
    await update.message.reply_text(
        f"⚔️ *{challenger.first_name}* challenges *@{mention}* to a 1v1!\n\n"
        f"@{mention} — do you accept?",
        parse_mode="Markdown",
        reply_markup=kb
    )

async def accept_challenge_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, challenger_id_str = query.data.split(":")
    challenger_id = int(challenger_id_str)
    opponent = query.from_user
    chat_id = update.effective_chat.id

    challenge = pending_challenges.get(chat_id, {}).get(challenger_id)
    if not challenge:
        await query.edit_message_text("❌ This challenge has expired.")
        return

    if action == "decline":
        await query.edit_message_text(f"❌ *{opponent.first_name}* declined the challenge.", parse_mode="Markdown")
        pending_challenges[chat_id].pop(challenger_id, None)
        return

    # Check opponent has a squad
    get_or_create_user(opponent.id, opponent.first_name)
    opp_squad = get_squad(opponent.id)
    if not opp_squad["player_ids"]:
        await query.edit_message_text(
            f"❌ *{opponent.first_name}* doesn't have a squad set yet!\nUse /setsquad first.",
            parse_mode="Markdown"
        )
        return

    challenger_squad = get_squad(challenger_id)
    challenger_user = get_user(challenger_id)

    await query.edit_message_text(
        f"⚽ Match starting!\n*{challenger_user['name']}* vs *{opponent.first_name}*\n\n🎮 Simulating...",
        parse_mode="Markdown"
    )

    result = simulate_match(
        challenger_squad["player_ids"],
        opp_squad["player_ids"],
        team1_name=challenger_user["name"],
        team2_name=opponent.first_name,
    )

    report = format_match_report(result)

    # Record results and award coins
    if result["score1"] > result["score2"]:
        record_result(challenger_id, "win"); add_coins(challenger_id, WIN_COINS)
        record_result(opponent.id, "loss"); add_coins(opponent.id, LOSS_COINS)
        coins_note = f"\n💰 *{challenger_user['name']}* +{WIN_COINS} coins | *{opponent.first_name}* +{LOSS_COINS} coins"
    elif result["score2"] > result["score1"]:
        record_result(challenger_id, "loss"); add_coins(challenger_id, LOSS_COINS)
        record_result(opponent.id, "win"); add_coins(opponent.id, WIN_COINS)
        coins_note = f"\n💰 *{opponent.first_name}* +{WIN_COINS} coins | *{challenger_user['name']}* +{LOSS_COINS} coins"
    else:
        record_result(challenger_id, "draw"); add_coins(challenger_id, DRAW_COINS)
        record_result(opponent.id, "draw"); add_coins(opponent.id, DRAW_COINS)
        coins_note = f"\n💰 Both players +{DRAW_COINS} coins"

    pending_challenges[chat_id].pop(challenger_id, None)
    await context.bot.send_message(chat_id, report + coins_note, parse_mode="Markdown")

# ─── 2v2 Co-op Challenge ─────────────────────────────────────────────────────

async def coop_challenge_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.first_name)

    if len(context.args) < 3:
        await update.message.reply_text(
            "Usage: `/coop @teammate @opponent1 @opponent2`\n"
            "You and your teammate share one squad vs the other pair.",
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        f"🤝 *2v2 Co-op Challenge!*\n\n"
        f"*Team 1:* {user.first_name} & @{context.args[0].lstrip('@')}\n"
        f"*Team 2:* @{context.args[1].lstrip('@')} & @{context.args[2].lstrip('@')}\n\n"
        "⚠️ Both teams use the squad of the first player on each team.\n"
        "Each pair — accept with /acceptcoop",
        parse_mode="Markdown"
    )

# ─── Quick Match (Draft 5v5) ──────────────────────────────────────────────────

async def quickmatch_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.first_name)
    chat_id = update.effective_chat.id

    if not context.args:
        await update.message.reply_text(
            "⚡ *Quick Match — Draft Mode*\n\n"
            "Both players pick 5 players from a shared random pool.\n"
            "Usage: `/quickmatch @username`",
            parse_mode="Markdown"
        )
        return

    mention = context.args[0].lstrip("@")

    # Build a random pool of 12 players
    pool = random.sample(PLAYERS, QUICK_DRAFT_POOL_SIZE)
    pool_ids = [p["id"] for p in pool]

    # Store in pending
    if chat_id not in pending_challenges:
        pending_challenges[chat_id] = {}
    pending_challenges[chat_id][f"qm_{user.id}"] = {
        "type": "quickmatch",
        "challenger_id": user.id,
        "challenger_name": user.first_name,
        "mention": mention,
        "pool_ids": pool_ids,
    }

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Accept Draft", callback_data=f"qmaccept:{user.id}"),
        InlineKeyboardButton("❌ Decline", callback_data=f"qmdecline:{user.id}"),
    ]])
    await update.message.reply_text(
        f"⚡ *{user.first_name}* wants a Quick Match against *@{mention}*!\n\n"
        "5v5 draft — you each pick 5 players from a shared pool.\n\n"
        f"@{mention} — do you accept?",
        parse_mode="Markdown",
        reply_markup=kb
    )

async def quickmatch_accept_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, challenger_id_str = query.data.split(":")
    challenger_id = int(challenger_id_str)
    opponent = query.from_user
    chat_id = update.effective_chat.id

    key = f"qm_{challenger_id}"
    challenge = pending_challenges.get(chat_id, {}).get(key)
    if not challenge:
        await query.edit_message_text("❌ This challenge has expired.")
        return

    if action == "qmdecline":
        await query.edit_message_text(f"❌ *{opponent.first_name}* declined.", parse_mode="Markdown")
        pending_challenges[chat_id].pop(key, None)
        return

    if opponent.id == challenger_id:
        await query.answer("You can't accept your own challenge!", show_alert=True)
        return

    get_or_create_user(opponent.id, opponent.first_name)
    pool_ids = challenge["pool_ids"]

    # Create draft session in memory
    match_key = f"draft_{challenger_id}_{opponent.id}"
    draft_sessions[match_key] = {
        "team1_id": challenger_id,
        "team1_name": challenge["challenger_name"],
        "team2_id": opponent.id,
        "team2_name": opponent.first_name,
        "pool": pool_ids,
        "team1_picks": [],
        "team2_picks": [],
        "turn": 1,  # 1 = team1's pick, 2 = team2's pick
        "chat_id": chat_id,
        "match_key": match_key,
    }

    pending_challenges[chat_id].pop(key, None)
    await query.edit_message_text("✅ Challenge accepted! Draft starting...", parse_mode="Markdown")
    await send_draft_pick(context, match_key, chat_id)

async def send_draft_pick(context, match_key: str, chat_id: int):
    session = draft_sessions.get(match_key)
    if not session:
        return

    pool = session["pool"]
    t1_picks = session["team1_picks"]
    t2_picks = session["team2_picks"]
    turn = session["turn"]
    picked_all = set(t1_picks + t2_picks)
    available = [pid for pid in pool if pid not in picked_all]

    # Check if draft is complete
    if len(t1_picks) >= QUICK_DRAFT_PICKS and len(t2_picks) >= QUICK_DRAFT_PICKS:
        await run_quick_match(context, match_key, chat_id)
        return

    current_player_id = session["team1_id"] if turn == 1 else session["team2_id"]
    current_name = session["team1_name"] if turn == 1 else session["team2_name"]
    picks_done = len(t1_picks) if turn == 1 else len(t2_picks)

    lines = [f"⚡ *Draft Pick — {current_name}* ({picks_done}/{QUICK_DRAFT_PICKS} picked)\n"]
    lines.append("*Available players:*")

    buttons = []
    row = []
    for i, pid in enumerate(available):
        p = PLAYER_MAP.get(pid)
        if p:
            r = RARITY_EMOJI[p["rarity"]]
            lines.append(f"`{i+1}.` {r} *{p['name']}* ({p['position']}) OVR {p['overall']}")
            row.append(InlineKeyboardButton(
                f"{i+1}. {p['name']}",
                callback_data=f"draft:{match_key}:{pid}"
            ))
            if len(row) == 2:
                buttons.append(row)
                row = []
    if row:
        buttons.append(row)

    # Show what's already picked
    if t1_picks or t2_picks:
        lines.append(f"\n*{session['team1_name']}:* {len(t1_picks)}/5 picked")
        lines.append(f"*{session['team2_name']}:* {len(t2_picks)}/5 picked")

    await context.bot.send_message(
        chat_id,
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def draft_pick_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    _, match_key, pid_str = query.data.split(":", 2)
    pid = int(pid_str)
    user = query.from_user
    chat_id = update.effective_chat.id

    session = draft_sessions.get(match_key)
    if not session:
        await query.answer("Session expired!", show_alert=True)
        return

    turn = session["turn"]
    current_id = session["team1_id"] if turn == 1 else session["team2_id"]

    if user.id != current_id:
        await query.answer("It's not your turn to pick!", show_alert=True)
        return

    picked_all = set(session["team1_picks"] + session["team2_picks"])
    if pid in picked_all:
        await query.answer("That player is already picked!", show_alert=True)
        return

    p = PLAYER_MAP.get(pid)
    if turn == 1:
        session["team1_picks"].append(pid)
    else:
        session["team2_picks"].append(pid)

    # Alternate turns
    t1_done = len(session["team1_picks"]) >= QUICK_DRAFT_PICKS
    t2_done = len(session["team2_picks"]) >= QUICK_DRAFT_PICKS

    if not t1_done and not t2_done:
        session["turn"] = 2 if turn == 1 else 1
    elif t1_done and not t2_done:
        session["turn"] = 2
    elif t2_done and not t1_done:
        session["turn"] = 1

    await query.edit_message_text(
        f"✅ *{user.first_name}* picked *{p['name']}* ({p['position']}) OVR {p['overall']}",
        parse_mode="Markdown"
    )
    await send_draft_pick(context, match_key, chat_id)

async def run_quick_match(context, match_key: str, chat_id: int):
    session = draft_sessions.get(match_key)
    if not session:
        return

    t1_ids = session["team1_picks"]
    t2_ids = session["team2_picks"]

    squad1_text = format_squad_card(t1_ids, f"{session['team1_name']}'s Draft Squad")
    squad2_text = format_squad_card(t2_ids, f"{session['team2_name']}'s Draft Squad")

    await context.bot.send_message(chat_id, squad1_text, parse_mode="Markdown")
    await context.bot.send_message(chat_id, squad2_text, parse_mode="Markdown")
    await context.bot.send_message(chat_id, "🎮 *Simulating Quick Match...*", parse_mode="Markdown")

    result = simulate_match(t1_ids, t2_ids, session["team1_name"], session["team2_name"])
    report = format_match_report(result)

    t1_id = session["team1_id"]
    t2_id = session["team2_id"]

    if result["score1"] > result["score2"]:
        record_result(t1_id, "win"); add_coins(t1_id, WIN_COINS)
        record_result(t2_id, "loss"); add_coins(t2_id, LOSS_COINS)
        coins_note = f"\n💰 *{session['team1_name']}* +{WIN_COINS} | *{session['team2_name']}* +{LOSS_COINS}"
    elif result["score2"] > result["score1"]:
        record_result(t1_id, "loss"); add_coins(t1_id, LOSS_COINS)
        record_result(t2_id, "win"); add_coins(t2_id, WIN_COINS)
        coins_note = f"\n💰 *{session['team2_name']}* +{WIN_COINS} | *{session['team1_name']}* +{LOSS_COINS}"
    else:
        record_result(t1_id, "draw"); add_coins(t1_id, DRAW_COINS)
        record_result(t2_id, "draw"); add_coins(t2_id, DRAW_COINS)
        coins_note = f"\n💰 Both +{DRAW_COINS} coins"

    await context.bot.send_message(chat_id, report + coins_note, parse_mode="Markdown")
    draft_sessions.pop(match_key, None)
