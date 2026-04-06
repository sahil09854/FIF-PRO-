from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_or_create_user, get_collection, get_squad, set_squad
from players_data import PLAYERS, RARITY_EMOJI, POSITION_EMOJI

PLAYER_MAP = {p["id"]: p for p in PLAYERS}

def paginate_collection(player_ids: list, page: int = 0, per_page: int = 8):
    start = page * per_page
    return player_ids[start:start + per_page], len(player_ids)

async def view_collection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.first_name)
    collection = get_collection(user.id)

    if not collection:
        await update.message.reply_text(
            "📭 Your collection is empty!\nOpen a pack with /openpack to get started."
        )
        return

    page = 0
    page_ids, total = paginate_collection(collection, page)
    text = format_collection_page(page_ids, page, total)
    kb = collection_keyboard(page, total, len(page_ids))
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def collection_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, page_str = query.data.split(":")
    page = int(page_str)

    user = query.from_user
    collection = get_collection(user.id)
    page_ids, total = paginate_collection(collection, page)
    text = format_collection_page(page_ids, page, total)
    kb = collection_keyboard(page, total, len(page_ids))
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

def format_collection_page(player_ids, page, total, per_page=8):
    lines = [f"🗂 *Your Collection* — {total} players\n"]
    for pid in player_ids:
        p = PLAYER_MAP.get(pid)
        if p:
            r = RARITY_EMOJI[p["rarity"]]
            pos = POSITION_EMOJI.get(p["position"], "⚽")
            lines.append(f"{r}{pos} *{p['name']}* ({p['position']}) OVR {p['overall']}")
    lines.append(f"\nPage {page+1} / {max(1, -(-total//per_page))}")
    return "\n".join(lines)

def collection_keyboard(page, total, page_size, per_page=8):
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"col:{page-1}"))
    if (page + 1) * per_page < total:
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"col:{page+1}"))
    return InlineKeyboardMarkup([buttons]) if buttons else None

async def view_squad_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.first_name)
    squad = get_squad(user.id)

    if not squad["player_ids"]:
        await update.message.reply_text(
            "🏟 You haven't set a squad yet!\nUse /setsquad to pick your players."
        )
        return

    lines = [f"🏟 *Your Squad* — Formation: {squad['formation']}\n"]
    total_ovr = 0
    count = 0
    for pid in squad["player_ids"]:
        p = PLAYER_MAP.get(pid)
        if p:
            r = RARITY_EMOJI[p["rarity"]]
            pos = POSITION_EMOJI.get(p["position"], "⚽")
            lines.append(f"{r}{pos} *{p['name']}* ({p['position']}) — OVR {p['overall']}")
            total_ovr += p["overall"]
            count += 1
    if count:
        lines.append(f"\n📊 *Team OVR: {total_ovr // count}*")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def set_squad_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.first_name)
    collection = get_collection(user.id)

    if len(collection) < 5:
        await update.message.reply_text(
            "❌ You need at least 5 players in your collection to set a squad.\n"
            "Open packs with /openpack!"
        )
        return

    args = context.args
    if not args:
        # Show instructions with available players
        lines = ["*Set your squad — usage:*",
                 "`/setsquad <player_id1> <player_id2> ... (5 to 11 players)`\n",
                 "*Your players (ID — Name — OVR):*"]
        for pid in collection[:20]:
            p = PLAYER_MAP.get(pid)
            if p:
                lines.append(f"`{pid}` — {p['name']} ({p['position']}) OVR {p['overall']}")
        if len(collection) > 20:
            lines.append(f"_...and {len(collection)-20} more. Use /collection to see all._")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
        return

    try:
        picked_ids = [int(x) for x in args]
    except ValueError:
        await update.message.reply_text("❌ Please provide valid player IDs (numbers).")
        return

    if not (5 <= len(picked_ids) <= 11):
        await update.message.reply_text("❌ Pick between 5 and 11 players for your squad.")
        return

    collection_set = set(collection)
    invalid = [pid for pid in picked_ids if pid not in collection_set]
    if invalid:
        await update.message.reply_text(
            f"❌ You don't own player(s) with ID: {', '.join(map(str, invalid))}\n"
            "Check /collection for your players."
        )
        return

    set_squad(user.id, picked_ids)
    lines = ["✅ *Squad set!*\n"]
    total_ovr = 0
    count = 0
    for pid in picked_ids:
        p = PLAYER_MAP.get(pid)
        if p:
            pos = POSITION_EMOJI.get(p["position"], "⚽")
            lines.append(f"{pos} *{p['name']}* ({p['position']}) — OVR {p['overall']}")
            total_ovr += p["overall"]
            count += 1
    if count:
        lines.append(f"\n📊 *Team OVR: {total_ovr // count}*")
    lines.append("\nReady to play! Use /challenge @username to start a match.")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
