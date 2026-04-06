import logging
import os
from telegram import Update
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler,
                           ContextTypes)
from database import init_db, get_or_create_user
from handlers.packs import open_pack_handler, buy_pack_handler
from handlers.squad import (view_collection_handler, view_squad_handler,
                              set_squad_handler, collection_page_callback)
from handlers.match import (challenge_handler, accept_challenge_callback,
                             quickmatch_handler, quickmatch_accept_callback,
                             quick_draft_pick_callback, coop_challenge_handler)
from handlers.profile import profile_handler, leaderboard_handler, shop_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.first_name)
    await update.message.reply_text(
        f"⚽ *Welcome to Street FIFA, {user.first_name}!*\n\n"
        "Pack players, build your squad, and battle friends.\n\n"
        "─────────────────\n"
        "⚡ *QUICK MATCH*\n"
        "`/quickmatch @user` — Draft 5 players each, play!\n\n"
        "📦 *PACKS*\n"
        "`/openpack` — Free daily pack\n"
        "`/shop` — Buy packs with coins\n\n"
        "🏟 *SQUAD*\n"
        "`/collection` — Your players\n"
        "`/setsquad` — Pick your starting XI\n"
        "`/mysquad` — View your squad\n\n"
        "⚔️ *MATCHES*\n"
        "`/challenge @user` — Full squad 1v1\n"
        "`/coop @mate @opp1 @opp2` — 2v2 co-op\n\n"
        "📊 *STATS*\n"
        "`/profile` — Your stats & coins\n"
        "`/leaderboard` — Top players\n"
        "─────────────────\n"
        "Start with `/openpack` to get your first players! 🎁",
        parse_mode="Markdown"
    )

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

def main():
    init_db()
    logger.info("Database initialised.")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",       start))
    app.add_handler(CommandHandler("help",        help_handler))
    app.add_handler(CommandHandler("openpack",    open_pack_handler))
    app.add_handler(CommandHandler("buypack",     buy_pack_handler))
    app.add_handler(CommandHandler("shop",        shop_handler))
    app.add_handler(CommandHandler("collection",  view_collection_handler))
    app.add_handler(CommandHandler("mysquad",     view_squad_handler))
    app.add_handler(CommandHandler("setsquad",    set_squad_handler))
    app.add_handler(CommandHandler("challenge",   challenge_handler))
    app.add_handler(CommandHandler("quickmatch",  quickmatch_handler))
    app.add_handler(CommandHandler("coop",        coop_challenge_handler))
    app.add_handler(CommandHandler("profile",     profile_handler))
    app.add_handler(CommandHandler("leaderboard", leaderboard_handler))
    app.add_handler(CallbackQueryHandler(accept_challenge_callback,  pattern=r"^(accept|decline):\d+$"))
    app.add_handler(CallbackQueryHandler(quickmatch_accept_callback, pattern=r"^(qmaccept|qmdecline):\d+$"))
    app.add_handler(CallbackQueryHandler(quick_draft_pick_callback, pattern=r"^\qd\|"))
    app.add_handler(CallbackQueryHandler(collection_page_callback,   pattern=r"^col:\d+$"))
    logger.info("Bot started. Polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
