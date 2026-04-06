import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import (get_or_create_user, get_user, get_squad, add_coins,
                       record_result, create_match)
from simulation import simulate_match, format_match_report, format_squad_card
from players_data import PLAYERS, PLAYER_MAP, RARITY_EMOJI, POSITION_EMOJI

pending_challenges = {}
draft_sessions = {}

WIN_COINS = 150
DRAW_COINS = 50
LOSS_COINS = 20

DRAFT_SLOTS = ["GK", "ANY", "ANY", "ANY", "ANY"]

def get_random_options(position=None, exclude_ids=None, count=5):
    exclude_ids = exclude_ids or []
    if position and position != "ANY":
        pool = [p for p in PLAYERS if p["position"] == position and p["id"] not in exclude_ids]
    else:
        pool = [p for p in PLAYERS if p["id"] not in exclude_ids]
    if len(pool) < count:
        pool = [p for p in PLAYERS if p["id"] not in exclude_ids]
    return random.sample(pool, min(count, len(pool)))

def format_options_text(options, slot_label):
    lines = [f"🎯 *Pick your {slot_label}*\n"]
    for p in options:
        r = RARITY_EMOJI[p["rarity"]]
        pos = POSITION_EMOJI.get(p["position"], "⚽")
        lines.append(f"{r}{pos} *{p['name']}* ({p['position']}) OVR {p['overall']}")
    return "\n".join(lines)

async def challenge_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    challenger = update.effective_user
    get_or_create_user(challenger.id, challenger.first_name)
    if not context.args:
        await update.message.reply_text("Usage: `/challenge @username`", parse_mode="Markdown")
        return
    challenger_squad = get_squad(challenger.id)
    if not challenger_squad["player_ids"]:
        await update.message.reply_text("❌ Set your squad first with /setsquad")
        return
    mention = context.args[0].lstrip("@")
    chat_id = update.effective_chat.id
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
        f"⚔️ *{challenger.first_name}* challenges *@{mention}* to a 1v1!\n@{mention} — accept?",
        parse_mode="Markdown", reply_markup=kb
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
        await query.edit_message_text("❌ Challenge expired.")
        return
    if action == "decline":
        await query.edit_message_text(f"❌ *{opponent.first_name}* declined.", parse_mode="Markdown")
        pending_challenges[chat_id].pop(challenger_id, None)
        return
    get_or_create_user(opponent.id, opponent.first_name)
    opp_squad = get_squad(opponent.id)
    if not opp_squad["player_ids"]:
        await query.edit_message_text(f"❌ *{opponent.first_name}* has no squad! Use /setsquad.", parse_mode="Markdown")
        return
    challenger_squad = get_squad(challenger_id)
    challenger_user = get_user(challenger_id)
    await query.edit_message_text(
        f"⚽ *{challenger_user['name']}* vs *{opponent.first_name}* — simulating...",
        parse_mode="Markdown"
    )
    result = simulate_match(
        challenger_squad["player_ids"], opp_squad["player_ids"],
        team1_name=challenger_user["name"], team2_name=opponent.first_name,
    )
    report = format_match_report(result)
    if result["score1"] > result["score2"]:
        record_result(challenger_id, "win"); add_coins(challenger_id, WIN_COINS)
        record_result(opponent.id, "loss"); add_coins(opponent.id, LOSS_COINS)
        coins_note = f"\n💰 *{challenger_user['name']}* +{WIN_COINS} | *{opponent.first_name}* +{LOSS_COINS}"
    elif result["score2"] > result["score1"]:
        record_result(challenger_id, "loss"); add_coins(challenger_id, LOSS_COINS)
        record_result(opponent.id, "win"); add_coins(opponent.id, WIN_COINS)
        coins_note = f"\n💰 *{opponent.first_name}* +{WIN_COINS} | *{challenger_user['name']}* +{LOSS_COINS}"
    else:
        record_result(challenger_id, "draw"); add_coins(challenger_id, DRAW_COINS)
        record_result(opponent.id, "draw"); add_coins(opponent.id, DRAW_COINS)
        coins_note = f"\n💰 Both +{DRAW_COINS} coins"
    pending_challenges[chat_id].pop(challenger_id, None)
    await context.bot.send_message(chat_id, report + coins_note, parse_mode="Markdown")

async def coop_challenge_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤝 2v2 co-op coming soon!")

async def quickmatch_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.first_name)
    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text(
            "⚡ *Quick Match — Secret Draft*\n\n"
            "Both pick 5 players privately.\n"
            "Teams revealed at the end!\n\n"
            "Usage: `/quickmatch @username`",
            parse_mode="Markdown"
        )
        return
    mention = context.args[0].lstrip("@")
    if chat_id not in pending_challenges:
        pending_challenges[chat_id] = {}
    pending_challenges[chat_id][f"qm_{user.id}"] = {
        "type": "quickmatch",
        "challenger_id": user.id,
        "challenger_name": user.first_name,
        "mention": mention,
    }
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Accept", callback_data=f"qmaccept:{user.id}"),
        InlineKeyboardButton("❌ Decline", callback_data=f"qmdecline:{user.id}"),
    ]])
    await update.message.reply_text(
        f"⚡ *{user.first_name}* challenges *@{mention}* to a Quick Match!\n\n"
        f"🔒 Secret draft — pick 5 players privately!\n"
        f"1st pick is GK, rest is your choice.\n\n"
        f"⚠️ Both players must have started the bot privately first!\n\n"
        f"@{mention} — accept?",
        parse_mode="Markdown", reply_markup=kb
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
        await query.edit_message_text("❌ Challenge expired.")
        return
    if action == "qmdecline":
        await query.edit_message_text(f"❌ *{opponent.first_name}* declined.", parse_mode="Markdown")
        pending_challenges[chat_id].pop(key, None)
        return
    if opponent.id == challenger_id:
        await query.answer("You can't accept your own challenge!", show_alert=True)
        return
    get_or_create_user(opponent.id, opponent.first_name)
    match_key = f"draft.{challenger_id}.{opponent.id}"
    draft_sessions[match_key] = {
        "team1_id": challenger_id,
        "team1_name": challenge["challenger_name"],
        "team2_id": opponent.id,
        "team2_name": opponent.first_name,
        "team1_picks": [],
        "team2_picks": [],
        "team1_done": False,
        "team2_done": False,
        "chat_id": chat_id,
        "match_key": match_key,
    }
    pending_challenges[chat_id].pop(key, None)
    await query.edit_message_text(
        f"✅ *Draft started!*\n\n"
        f"*{challenge['challenger_name']}* vs *{opponent.first_name}*\n\n"
        f"🔒 Check your *private chat* with the bot to pick your team!\n"
        f"Both teams are secret until the end 🤫",
        parse_mode="Markdown"
    )
    failed = []
    try:
        await send_pick_to_player(context, match_key, challenger_id, chat_id)
    except Exception as e:
        print(f"Error sending to challenger: {e}")
        failed.append(challenge["challenger_name"])
    try:
        await send_pick_to_player(context, match_key, opponent.id, chat_id)
    except Exception as e:
        print(f"Error sending to opponent: {e}")
        failed.append(opponent.first_name)
    if failed:
        await context.bot.send_message(
            chat_id,
            f"❌ Couldn't DM: *{', '.join(failed)}*\n\n"
            f"Open the bot privately → press /start → try again!",
            parse_mode="Markdown"
        )
        draft_sessions.pop(match_key, None)

async def send_pick_to_player(context, match_key: str, user_id: int, chat_id: int):
    session = draft_sessions.get(match_key)
    if not session:
        return
    is_team1 = user_id == session["team1_id"]
    my_picks = session["team1_picks"] if is_team1 else session["team2_picks"]
    slot_index = len(my_picks)
    if slot_index >= len(DRAFT_SLOTS):
        return
    slot = DRAFT_SLOTS[slot_index]
    slot_label = "Goalkeeper 🧤" if slot == "GK" else f"Player {slot_index + 1} — any position"
    options = get_random_options(position=slot, exclude_ids=my_picks, count=5)
    text = format_options_text(options, slot_label)
    text += f"\n\n📋 *Picks: {slot_index}/5*"
    buttons = []
    for p in options:
        r = RARITY_EMOJI[p["rarity"]]
        cb = f"qd|{match_key}|{user_id}|{p['id']}"
        buttons.append([InlineKeyboardButton(
            f"{r} {p['name']} ({p['position']}) OVR {p['overall']}",
            callback_data=cb
        )])
    name = session["team1_name"] if is_team1 else session["team2_name"]
    await context.bot.send_message(
        user_id,
        f"🔒 *Secret Draft — {name}*\n\n" + text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def quick_draft_pick_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("|")
    match_key = parts[1]
    target_user_id = int(parts[2])
    pid = int(parts[3])
    user = query.from_user
    if user.id != target_user_id:
        await query.answer("This pick is not for you!", show_alert=True)
        return
    session = draft_sessions.get(match_key)
    if not session:
        await query.answer("Session expired!", show_alert=True)
        return
    is_team1 = user.id == session["team1_id"]
    my_picks = session["team1_picks"] if is_team1 else session["team2_picks"]
    if pid in my_picks:
        await query.answer("Already picked!", show_alert=True)
        return
    my_picks.append(pid)
    p = PLAYER_MAP.get(pid)
    chat_id = session["chat_id"]
    await query.edit_message_text(
        f"✅ *{p['name']}* ({p['position']}) OVR {p['overall']} — picked!\n"
        f"📋 Picks: {len(my_picks)}/5",
        parse_mode="Markdown"
    )
    if len(my_picks) >= len(DRAFT_SLOTS):
        if is_team1:
            session["team1_done"] = True
        else:
            session["team2_done"] = True
        await context.bot.send_message(
            chat_id=user.id,
            text="✅ *Your team is locked in!*\nWaiting for opponent... ⏳",
            parse_mode="Markdown"
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ *{user.first_name}* has finished picking! Waiting for opponent... ⏳",
            parse_mode="Markdown"
        )
        if session["team1_done"] and session["team2_done"]:
            await reveal_and_simulate(context, match_key, chat_id)
    else:
        await send_pick_to_player(context, match_key, user.id, chat_id)

async def reveal_and_simulate(context, match_key: str, chat_id: int):
    session = draft_sessions.get(match_key)
    if not session:
        return
    t1_ids = session["team1_picks"]
    t2_ids = session["team2_picks"]
    squad1 = format_squad_card(t1_ids, f"⚡ {session['team1_name']}'s Squad")
    squad2 = format_squad_card(t2_ids, f"⚡ {session['team2_name']}'s Squad")
    await context.bot.send_message(chat_id, "🎭 *Both teams ready! Revealing now...*", parse_mode="Markdown")
    await asyncio.sleep(1)
    await context.bot.send_message(chat_id, squad1, parse_mode="Markdown")
    await context.bot.send_message(chat_id, squad2, parse_mode="Markdown")
    msg = await context.bot.send_message(chat_id, "⏱ Match starts in *3*...", parse_mode="Markdown")
    await asyncio.sleep(1)
    await msg.edit_text("⏱ Match starts in *2*...", parse_mode="Markdown")
    await asyncio.sleep(1)
    await msg.edit_text("⏱ Match starts in *1*...", parse_mode="Markdown")
    await asyncio.sleep(1)
    await msg.edit_text("🏁 *KICKOFF!*", parse_mode="Markdown")
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
