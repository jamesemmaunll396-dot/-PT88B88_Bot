
import os
import html
import logging
import random
import sqlite3
import asyncio
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

import feedparser

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==========================================
# BOT CONFIGURATION
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")

ADMIN_IDS = {
    int(value.strip())
    for value in os.getenv("ADMIN_IDS", "").split(",")
    if value.strip().isdigit()
}

DB_PATH = os.getenv(
    "DATABASE_PATH",
    "football_news_users.sqlite3"
)

NEWS_LIMIT = 5

# Public football RSS news feeds
RSS_FEEDS = [
    (
        "BBC Sport",
        "https://feeds.bbci.co.uk/sport/football/rss.xml"
    ),
    (
        "ESPN Soccer",
        "https://www.espn.com/espn/rss/soccer/news"
    ),
    (
        "Sky Sports",
        "https://www.skysports.com/rss/12040"
    ),
]

# Football league categories
LEAGUES = {
    "premier": (
        "Premier League",
        [
            "premier league", "arsenal", "chelsea",
            "liverpool", "manchester city",
            "manchester united", "tottenham",
            "newcastle", "aston villa", "brighton",
            "west ham", "everton"
        ]
    ),

    "laliga": (
        "La Liga",
        [
            "la liga", "barcelona", "real madrid",
            "atletico madrid", "girona", "sevilla",
            "real sociedad", "athletic club"
        ]
    ),

    "ucl": (
        "Champions League",
        [
            "champions league", "uefa", "ucl"
        ]
    ),

    "seriea": (
        "Serie A",
        [
            "serie a", "inter milan", "ac milan",
            "juventus", "napoli", "roma",
            "lazio", "atalanta"
        ]
    ),
}

FACTS = [
    "A standard football match lasts 90 minutes, split into two 45-minute halves, plus added time.",
    "A football team normally has 11 players on the pitch.",
    "The FIFA World Cup is held every four years.",
    "A hat-trick is when a player scores three goals in one match.",
    "The penalty spot is 11 metres from the goal line.",
    "The Champions League is UEFA's top annual club competition.",
]

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger("football-news-bot")


# ==========================================
# DATABASE
# ==========================================

def db_connect():
    connection = sqlite3.connect(DB_PATH)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            username TEXT,
            joined_at TEXT
        )
    """)

    connection.commit()
    return connection


def save_user(user):
    if not user:
        return

    with db_connect() as connection:
        connection.execute(
            """
            INSERT INTO users
            (user_id, first_name, username, joined_at)
            VALUES (?, ?, ?, ?)

            ON CONFLICT(user_id) DO UPDATE SET
            first_name=excluded.first_name,
            username=excluded.username
            """,
            (
                user.id,
                user.first_name or "",
                user.username or "",
                datetime.now(timezone.utc).isoformat(),
            ),
        )


def get_user_ids():
    with db_connect() as connection:
        rows = connection.execute(
            "SELECT user_id FROM users"
        ).fetchall()

    return [row[0] for row in rows]


def get_user_count():
    with db_connect() as connection:
        return connection.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]


# ==========================================
# TELEGRAM MENU
# ==========================================

def main_menu():

    keyboard = [
        [
            InlineKeyboardButton(
                "📰 Latest Football News",
                callback_data="news:all"
            )
        ],

        [
            InlineKeyboardButton(
                "🏴 Premier League",
                callback_data="news:premier"
            ),
            InlineKeyboardButton(
                "🇪🇸 La Liga",
                callback_data="news:laliga"
            )
        ],

        [
            InlineKeyboardButton(
                "🏆 Champions League",
                callback_data="news:ucl"
            ),
            InlineKeyboardButton(
                "🇮🇹 Serie A",
                callback_data="news:seriea"
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
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


WELCOME_TEXT = (
    "⚽ <b>Welcome to Football News!</b>\n\n"

    "Your place for football headlines, "
    "club updates and stories from around the world.\n\n"

    "Choose an option below to get started."
)


# ==========================================
# FOOTBALL NEWS SYSTEM
# ==========================================

def read_feed(source_name, feed_url):

    parsed = feedparser.parse(feed_url)

    articles = []

    for entry in parsed.entries[:20]:

        title = entry.get("title", "").strip()

        link = entry.get("link", "").strip()

        summary = (
            entry.get("summary", "")
            or entry.get("description", "")
        )

        summary = html.unescape(summary)

        summary = re.sub(
            r"<[^>]+>",
            " ",
            summary
        )

        summary = " ".join(summary.split())

        published = entry.get("published", "")

        if (
            title
            and link
            and urlparse(link).scheme in ("http", "https")
        ):

            articles.append({
                "source": source_name,
                "title": title,
                "summary": summary[:280],
                "link": link,
                "published": published,
            })

    return articles


async def fetch_news(category="all"):

    tasks = [
        asyncio.to_thread(
            read_feed,
            source_name,
            feed_url
        )

        for source_name, feed_url in RSS_FEEDS
    ]

    results = await asyncio.gather(
        *tasks,
        return_exceptions=True
    )

    articles = []

    for result in results:

        if isinstance(result, Exception):

            logger.warning(
                "News feed error: %s",
                result
            )

            continue

        articles.extend(result)

    # Filter by selected football league
    if category in LEAGUES:

        keywords = LEAGUES[category][1]

        articles = [
            article
            for article in articles

            if any(
                word in (
                    article["title"]
                    + " "
                    + article["summary"]
                ).lower()

                for word in keywords
            )
        ]

    # Remove duplicate headlines
    unique = []

    seen = set()

    for article in articles:

        key = article["title"].lower()

        if key not in seen:

            seen.add(key)

            unique.append(article)

    return unique[:NEWS_LIMIT]


def format_articles(articles, category):

    if category in LEAGUES:

        heading = LEAGUES[category][0]

    else:

        heading = "Latest Football News"

    if not articles:

        return (
            f"📰 <b>{heading}</b>\n\n"
            "No headlines are available right now. "
            "Please try again later."
        )

    lines = [
        f"📰 <b>{heading}</b>\n"
    ]

    for index, article in enumerate(
        articles,
        start=1
    ):

        title = html.escape(article["title"])

        source = html.escape(article["source"])

        link = html.escape(
            article["link"],
            quote=True
        )

        summary = html.escape(
            article["summary"]
        )

        item = (
            f'{index}. <a href="{link}">'
            f"<b>{title}</b></a>\n"
        )

        if summary:

            item += f"<i>{summary}</i>\n"

        item += (
            f"<code>Source: {source}</code>\n"
        )

        lines.append(item)

    lines.append(
        "\n<i>News headlines are collected from "
        "public RSS feeds. Open a headline to read "
        "the full report.</i>"
    )

    return "\n".join(lines)


# ==========================================
# START COMMAND
# ==========================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    save_user(update.effective_user)

    await update.effective_message.reply_text(
        WELCOME_TEXT,
        reply_markup=main_menu(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


# ==========================================
# HELP COMMAND
# ==========================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    save_user(update.effective_user)

    help_text = (
        "ℹ️ <b>How to use this bot</b>\n\n"

        "📰 Latest Football News - Get football headlines.\n"

        "🏴 Premier League - Browse related headlines.\n"

        "🇪🇸 La Liga - Browse related headlines.\n"

        "🏆 Champions League - Browse related headlines.\n"

        "💡 Football Facts - Learn something about football.\n\n"

        "Send /start at any time to open the main menu."
    )

    await update.effective_message.reply_text(
        help_text,
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu()
    )


# ==========================================
# NEWS COMMAND
# ==========================================

async def news_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    save_user(update.effective_user)

    await update.effective_message.reply_text(
        "🔎 Fetching the latest football headlines..."
    )

    articles = await fetch_news("all")

    await update.effective_message.reply_text(
        format_articles(articles, "all"),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=main_menu(),
    )


# ==========================================
# FOOTBALL FACTS
# ==========================================

async def facts_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    save_user(update.effective_user)

    fact = random.choice(FACTS)

    await update.effective_message.reply_text(
        "💡 <b>Football Fact</b>\n\n"
        + html.escape(fact),
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(),
    )


# ==========================================
# ADMIN STATISTICS
# ==========================================

async def stats_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id not in ADMIN_IDS:

        await update.effective_message.reply_text(
            "⛔ This command is for the bot administrator."
        )

        return

    count = get_user_count()

    await update.effective_message.reply_text(
        f"👥 Registered users: {count}"
    )


# ==========================================
# ADMIN BROADCAST
# ==========================================

async def broadcast_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id not in ADMIN_IDS:

        await update.effective_message.reply_text(
            "⛔ This command is for the bot administrator."
        )

        return

    message = " ".join(context.args).strip()

    if not message:

        await update.effective_message.reply_text(
            "Usage:\n"
            "/broadcast Your announcement goes here"
        )

        return

    user_ids = get_user_ids()

    sent = 0

    failed = 0

    for user_id in user_ids:

        try:

            await context.bot.send_message(
                chat_id=user_id,
                text=message,
                disable_web_page_preview=True,
            )

            sent += 1

            await asyncio.sleep(0.04)

        except Exception as error:

            failed += 1

            logger.info(
                "Broadcast failed for %s: %s",
                user_id,
                error
            )

    await update.effective_message.reply_text(
        f"Broadcast finished.\n"
        f"Delivered: {sent}\n"
        f"Failed: {failed}"
    )


# ==========================================
# BUTTON RESPONSE SYSTEM
# ==========================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    save_user(query.from_user)

    if query.data.startswith("news:"):

        category = query.data.split(":", 1)[1]

        await query.edit_message_text(
            "🔎 Fetching football headlines..."
        )

        articles = await fetch_news(category)

        await query.edit_message_text(
            format_articles(articles, category),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=main_menu(),
        )

    elif query.data == "facts":

        fact = random.choice(FACTS)

        await query.edit_message_text(
            "💡 <b>Football Fact</b>\n\n"
            + html.escape(fact),
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu(),
        )

    elif query.data == "help":

        await query.edit_message_text(
            "ℹ️ <b>Help</b>\n\n"
            "Use the menu to browse football headlines "
            "by section.\n\n"
            "Send /start to return to the main menu.",
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu(),
        )


# ==========================================
# AUTOMATIC TEXT RESPONSES
# ==========================================

async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    save_user(update.effective_user)

    message = (
        update.effective_message.text or ""
    ).lower()

    if any(
        word in message
        for word in ("news", "headline", "latest")
    ):

        await update.effective_message.reply_text(
            "📰 Getting the latest football news..."
        )

        articles = await fetch_news("all")

        await update.effective_message.reply_text(
            format_articles(articles, "all"),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=main_menu(),
        )

    elif "premier" in message or "epl" in message:

        articles = await fetch_news("premier")

        await update.effective_message.reply_text(
            format_articles(articles, "premier"),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=main_menu(),
        )

    elif "la liga" in message or "laliga" in message:

        articles = await fetch_news("laliga")

        await update.effective_message.reply_text(
            format_articles(articles, "laliga"),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=main_menu(),
        )

    elif (
        "champions league" in message
        or "ucl" in message
    ):

        articles = await fetch_news("ucl")

        await update.effective_message.reply_text(
            format_articles(articles, "ucl"),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=main_menu(),
        )

    elif "fact" in message:

        await facts_command(update, context)

    elif any(
        word in message
        for word in (
            "hello",
            "hi",
            "hey",
            "good morning"
        )
    ):

        await update.effective_message.reply_text(
            "Hello! 👋 Welcome to Football News. "
            "Choose an option below.",
            reply_markup=main_menu(),
        )

    else:

        await update.effective_message.reply_text(
            "⚽ I can help you find football headlines "
            "and facts.\n\n"
            "Choose an option below or send /help.",
            reply_markup=main_menu(),
        )


# ==========================================
# ERROR HANDLER
# ==========================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    logger.error(
        "An error occurred:",
        exc_info=context.error
    )


# ==========================================
# START BOT
# ==========================================

def main():

    if not BOT_TOKEN:

        raise RuntimeError(
            "Missing bot token. Add BOT_TOKEN "
            "in Render environment variables."
        )

    # Create database
    db_connect().close()

    # Build Telegram application
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # Register bot commands
    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("help", help_command)
    )

    application.add_handler(
        CommandHandler("news", news_command)
    )

    application.add_handler(
        CommandHandler("fact", facts_command)
    )

    application.add_handler(
        CommandHandler("stats", stats_command)
    )

    application.add_handler(
        CommandHandler("broadcast", broadcast_command)
    )

    # Register button responses
    application.add_handler(
        CallbackQueryHandler(button_handler)
    )

    # Register normal text responses
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler
        )
    )

    application.add_error_handler(error_handler)

    logger.info("Football News Bot is starting...")

    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
