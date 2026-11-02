
import os
import asyncio
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==================================
# BOT CONFIGURATION
# ==================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ==================================
# MAIN MENU
# ==================================

def get_menu():

    keyboard = [
        [
            InlineKeyboardButton(
                "📰 Football News",
                callback_data="news"
            )
        ],
        [
            InlineKeyboardButton(
                "🏆 Football Leagues",
                callback_data="leagues"
            ),
            InlineKeyboardButton(
                "⚽ Match Results",
                callback_data="results"
            )
        ],
        [
            InlineKeyboardButton(
                "💡 Football Facts",
                callback_data="facts"
            ),
            InlineKeyboardButton(
                "ℹ️ Help",
                callback_data="help"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


# ==================================
# WELCOME MESSAGE
# ==================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    name = update.effective_user.first_name or "Football Fan"

    message = (
        f"⚽ Welcome {name}!\n\n"
        "Welcome to Football News Bot!\n\n"
        "Get football information, news updates, "
        "club information and football facts.\n\n"
        "Choose an option below to get started."
    )

    await update.effective_message.reply_text(
        message,
        reply_markup=get_menu()
    )


# ==================================
# FOOTBALL NEWS
# ==================================

async def send_news(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = (
        "📰 FOOTBALL NEWS\n\n"
        "Welcome to our football news section!\n\n"
        "Here you can explore updates about:\n\n"
        "⚽ Premier League\n"
        "⚽ Champions League\n"
        "⚽ La Liga\n"
        "⚽ Serie A\n"
        "⚽ International Football\n\n"
        "For current headlines, visit trusted "
        "football news publishers.\n\n"
        "More football updates coming soon!"
    )

    await update.effective_message.reply_text(
        message,
        reply_markup=get_menu()
    )


# ==================================
# FOOTBALL LEAGUES
# ==================================

async def send_leagues(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = (
        "🏆 POPULAR FOOTBALL LEAGUES\n\n"
        "🏴 English Premier League\n"
        "🇪🇸 Spanish La Liga\n"
        "🇮🇹 Italian Serie A\n"
        "🇩🇪 German Bundesliga\n"
        "🇫🇷 French Ligue 1\n"
        "🌍 UEFA Champions League\n\n"
        "Which competition do you follow?"
    )

    await update.effective_message.reply_text(
        message,
        reply_markup=get_menu()
    )


# ==================================
# MATCH RESULTS
# ==================================

async def send_results(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = (
        "⚽ MATCH RESULTS\n\n"
        "You can follow results from:\n\n"
        "🏆 Premier League\n"
        "🏆 Champions League\n"
        "🏆 La Liga\n"
        "🏆 Serie A\n"
        "🏆 Bundesliga\n\n"
        "Live scores and verified match results "
        "will be added in a future update."
    )

    await update.effective_message.reply_text(
        message,
        reply_markup=get_menu()
    )


# ==================================
# FOOTBALL FACTS
# ==================================

async def send_facts(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = (
        "💡 FOOTBALL FACTS\n\n"
        "1. A standard football match lasts 90 minutes "
        "before added time.\n\n"
        "2. Each team normally has 11 players on the pitch.\n\n"
        "3. A hat-trick means scoring three goals "
        "in one match.\n\n"
        "4. The FIFA World Cup takes place every "
        "four years.\n\n"
        "5. The goalkeeper is the only player "
        "normally allowed to handle the ball "
        "inside their own penalty area."
    )

    await update.effective_message.reply_text(
        message,
        reply_markup=get_menu()
    )


# ==================================
# HELP
# ==================================

async def send_help(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = (
        "ℹ️ HOW TO USE THIS BOT\n\n"
        "/start - Open the bot\n"
        "/news - Football news information\n"
        "/help - Get help\n\n"
        "You can also type football-related "
        "questions directly into the bot."
    )

    await update.effective_message.reply_text(
        message,
        reply_markup=get_menu()
    )


# ==================================
# BUTTON RESPONSES
# ==================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if query.data == "news":
        message = (
            "📰 FOOTBALL NEWS\n\n"
            "Follow updates about football clubs, "
            "players, transfers and competitions.\n\n"
            "Live headlines are not connected yet."
        )

    elif query.data == "leagues":
        message = (
            "🏆 FOOTBALL LEAGUES\n\n"
            "Premier League\n"
            "La Liga\n"
            "Serie A\n"
            "Bundesliga\n"
            "Ligue 1\n"
            "Champions League"
        )

    elif query.data == "results":
        message = (
            "⚽ MATCH RESULTS\n\n"
            "Football results and live scores "
            "will be added in a future update."
        )

    elif query.data == "facts":
        message = (
            "💡 FOOTBALL FACT\n\n"
            "A hat-trick is when a footballer "
            "scores three goals in one match!"
        )

    elif query.data == "help":
        message = (
            "ℹ️ HELP\n\n"
            "Use the menu to explore football "
            "information.\n\n"
            "Send /start to return to the main menu."
        )

    else:
        message = "Please select an option from the menu."

    await query.edit_message_text(
        message,
        reply_markup=get_menu()
    )


# ==================================
# NORMAL USER MESSAGES
# ==================================

async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.effective_message.text.lower().strip()

    if any(word in text for word in ["hello", "hi", "hey"]):

        reply = (
            "Hello football fan! 👋\n\n"
            "Welcome to Football News Bot. "
            "What would you like to know about football?"
        )

    elif any(word in text for word in ["news", "headline", "transfer"]):

        reply = (
            "📰 Football News\n\n"
            "You can explore football news about "
            "clubs, players, transfers and competitions.\n\n"
            "Live news headlines are not connected yet."
        )

    elif any(word in text for word in ["premier league", "epl"]):

        reply = (
            "🏴 The English Premier League is one "
            "of the most popular football competitions "
            "in the world.\n\n"
            "You can follow clubs such as Arsenal, "
            "Liverpool, Chelsea and Manchester City."
        )

    elif "champions league" in text:

        reply = (
            "🏆 The UEFA Champions League is a major "
            "European club football competition."
        )

    elif any(word in text for word in ["la liga", "laliga"]):

        reply = (
            "🇪🇸 La Liga is Spain's top professional "
            "football league. Famous clubs include "
            "Real Madrid and Barcelona."
        )

    elif any(word in text for word in ["score", "result", "results"]):

        reply = (
            "⚽ You can use our Match Results menu "
            "to explore football results information. "
            "Live scores are not connected yet."
        )

    elif any(word in text for word in ["player", "footballer"]):

        reply = (
            "⚽ Which football player are you interested in? "
            "You can ask about a player's club, position "
            "or football career."
        )

    elif "fact" in text:

        reply = (
            "💡 Football Fact:\n\n"
            "A standard football team has 11 players "
            "on the pitch, including the goalkeeper."
        )

    else:

        reply = (
            "⚽ Thanks for your message!\n\n"
            "I am your Football News Bot. "
            "I can help with football news topics, "
            "leagues, players and football facts.\n\n"
            "Try typing 'football news', "
            "'Premier League' or 'football facts'."
        )

    await update.effective_message.reply_text(
        reply,
        reply_markup=get_menu()
    )


# ==================================
# MAIN BOT STARTUP
# ==================================

def main():

    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN is missing. Add it in Render Environment Variables."
        )

    logger.info("Starting Football News Bot...")

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("news", send_news)
    )

    application.add_handler(
        CommandHandler("help", send_help)
    )

    application.add_handler(
        CommandHandler("fact", send_facts)
    )

    application.add_handler(
        CallbackQueryHandler(button_handler)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    # Start Telegram polling
    asyncio.set_event_loop(asyncio.new_event_loop())

    application.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
