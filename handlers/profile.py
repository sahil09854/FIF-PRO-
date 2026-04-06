from telegram import Update
from telegram.ext import ContextTypes
from database import get_or_create_user, get_user, get_leaderboard
from players_data import PACK_COSTS

async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.first_name)
    data = get_user(user.id)
    played = data["wins"] + data["losses"] + data["draws"]
    winrate = f"{(data['wins']/played*100):.0f}%" if played else "N/A"

    text = (
        f"👤 *{data['name']}*\n"
        f"─────────────────\n"
        f"💰 Coins:   *{data['coins']}*\n"
        f"🏆 Wins:    *{data['wins']}*\n"
        f"💀 Losses:  *{data['losses']}*\n"
        f"🤝 Draws:   *{data['draws']}*\n"
        f"📊 Win rate: *{winrate}*\n"
        f"─────────────────\n"
        f"Use /collection to see your players.\n"
        f"Use /shop to buy packs."
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def leaderboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    board = get_leaderboard()
    if not board:
        await update.message.reply_text("No matches played yet! Be the first with /challenge.")
        return

    medals = ["🥇", "🥈", "🥉"]
    lines = ["🏆 *Street FIFA Leaderboard*\n"]
    for i, row in enumerate(board):
        medal = medals[i] if i < 3 else f"{i+1}."
        lines.append(
            f"{medal} *{row['name']}* — {row['points']} pts "
            f"({row['wins']}W {row['draws']}D {row['losses']}L)"
        )
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def shop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🛒 *Pack Shop*\n\n"
        "📦 *Standard Pack* — 200 coins\n"
        "   5 players · Bronze-Silver focus\n"
        "   `/buypack standard`\n\n"
        "📦 *Premium Pack* — 500 coins\n"
        "   5 players · Silver-Gold focus\n"
        "   `/buypack premium`\n\n"
        "📦 *Elite Pack* — 1,200 coins\n"
        "   5 players · Gold-Icon focus\n"
        "   `/buypack elite`\n\n"
        "💡 Win matches to earn coins!\n"
        "   Win = +150 · Draw = +50 · Loss = +20"
    )
    await update.message.reply_text(text, parse_mode="Markdown")
