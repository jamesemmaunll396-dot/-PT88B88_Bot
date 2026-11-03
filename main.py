import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Your exact welcome message (no link inside the text)
WELCOME_MESSAGE = (
    "សូមស្វាគមន៍មកវេបសាយធំបំផុត ងាយស្រួលលេង📲 និងគួរឱ្យទុកចិត្តបំផុតនៅកម្ពុជា🔥\n\n"
    "សេវាកម្ម២៤ម៉ោង"
    "https://t.me/galaxy99_kh"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends the welcome message with a clickable link button."""
    
    # Create the button layout
    keyboard = [
        [
            # This creates the clickable button
            InlineKeyboardButton(
                text="DM NOW OR CONTACT ME NOW TO GET FREE BONUS", 
                url="https://t.me/galaxy99_kh" 
            )
        ]
    ]
    
    # Wrap the keyboard in InlineKeyboardMarkup
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message along with the button
    await update.message.reply_text(
        text=WELCOME_MESSAGE, 
        reply_markup=reply_markup,
        disable_web_page_preview=True # Keeps the message clean without the big preview box
    )

def main() -> None:
    """Start the bot."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not token:
        raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables.")

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))

    # drop_pending_updates=True prevents the bot from spamming old /start messages
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
