
import os
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

# ==========================================
# LOGGING
# ==========================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# ==========================================
# BOT CONFIGURATION
# ==========================================

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Telegram contact link
CONTACT_LINK = "https://t.me/Slotvipswc88vra"

# Button text
BUTTON_TEXT = "DM ME NOW GET FREE BONUS"


# ==========================================
# WELCOME MESSAGE
# ==========================================

WELCOME_MESSAGE = (
    "សូមស្វាគមន៍មកវេបសាយធំបំផុត ងាយស្រួលលេង📲 "
    "និងគួរឱ្យទុកចិត្តបំផុតនៅកម្ពុជា🔥\n\n"
    "សេវាកម្ម២៤ម៉ោង\n\n"
    "https://t.me/Slotvipswc88vra"
)


# ==========================================
# START COMMAND
# ==========================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = [
        [
            InlineKeyboardButton(
                text=BUTTON_TEXT,
                url=CONTACT_LINK
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_message.reply_text(
        text=WELCOME_MESSAGE,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

    logger.info(
        "Welcome message sent to user %s",
        update.effective_user.id
    )


# ==========================================
# HELP COMMAND
# ==========================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.effective_message.reply_text(
        "សូមប្រើ /start ដើម្បីចាប់ផ្តើម។\n\n"
        "Send /start to receive the welcome message."
    )


# ==========================================
# UNKNOWN COMMAND
# ==========================================

async def unknown_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.effective_message.reply_text(
        "Please send /start to begin."
    )


# ==========================================
# ERROR HANDLER
# ==========================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    logger.error(
        "Telegram bot error:",
        exc_info=context.error
    )


# ==========================================
# MAIN FUNCTION
# ==========================================

def main():

    if not BOT_TOKEN:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN is missing. "
            "Please add it to Render environment variables."
        )

    logger.info("Starting Telegram bot...")

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # Register commands
    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("help", help_command)
    )

    application.add_handler(
        MessageHandler(
            filters.COMMAND,
            unknown_command
        )
    )

    # Register error handler
    application.add_error_handler(error_handler)

    logger.info("Bot is ready to receive Telegram messages.")

    # Start bot
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


# ==========================================
# RUN BOT
# ==========================================

from telegram.ext import MessageHandler, filters

if __name__ == "__main__":
    main()
