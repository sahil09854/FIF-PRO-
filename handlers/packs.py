import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import (get_or_create_user, can_open_free_pack, mark_pack_opened,
                       add_to_collection, deduct_coins, get_user)
from players_data import PLAYERS, RARITY_WEIGHTS, PACK_COSTS, PACK_SIZES, RARITY_EMOJI

def draw_pack(pack_type: str = "standard") -> list:
    weights = RARITY_WEIGHTS[pack_type]
    rarities = list(weights.keys())
    rarity_weights = list(weights.values())
    size = PACK_SIZES[pack_type]

    drawn = []
    for _ in range(size):
        rarity = random.choices(rarities, weights=rarity_weights)[0]
        pool = [p for p in PLAYERS if p["rarity"] == rarity]
        if pool:
            drawn.append(random.choice(pool))
    return drawn

def format_pack_result(players: list, pack_type: str) -> str:
    lines = [f"📦 *{pack_type.title()} Pack Opened!*\n"]
    for p in players:
        emoji = RARITY_EMOJI[p["rarity"]]
        lines.append(
            f"{emoji} *{p['name']}* — {p['position']} | OVR {p['overall']}\n"
            f"   ⚡{p['pace']} 🎯{p['shooting']} 🎲{p['passing']} 🛡{p['defending']} 💪{p['physical']}"
        )
    return "\n".join(lines)

async def open_pack_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.first_name)

    if not can_open_free_pack(user.id):
        await update.message.reply_text(
            "⏳ You already opened your free pack today!\n"
            "Come back in 24 hours, or use /shop to buy more packs with coins."
        )
        return

    players = draw_pack("standard")
    player_ids = [p["id"] for p in players]
    add_to_collection(user.id, player_ids)
    mark_pack_opened(user.id)

    text = format_pack_result(players, "standard")
    text += "\n\n✅ Players added to your collection! Use /collection to view them."
    await update.message.reply_text(text, parse_mode="Markdown")

async def buy_pack_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.first_name)
    args = context.args

    pack_type = args[0].lower() if args else "standard"
    if pack_type not in PACK_COSTS:
        await update.message.reply_text(
            "❌ Unknown pack type. Choose: `standard` (200), `premium` (500), `elite` (1200)",
            parse_mode="Markdown"
        )
        return

    cost = PACK_COSTS[pack_type]
    db_user = get_user(user.id)
    if not deduct_coins(user.id, cost):
        await update.message.reply_text(
            f"❌ Not enough coins! You have *{db_user['coins']}* coins but need *{cost}*.\n"
            "Win matches to earn more!",
            parse_mode="Markdown"
        )
        return

    players = draw_pack(pack_type)
    player_ids = [p["id"] for p in players]
    add_to_collection(user.id, player_ids)

    text = format_pack_result(players, pack_type)
    text += f"\n\n💰 -{cost} coins spent. Use /profile to check your balance."
    await update.message.reply_text(text, parse_mode="Markdown")
