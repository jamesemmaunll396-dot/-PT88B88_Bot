
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

    # FIX: Create an event loop explicitly
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Start receiving Telegram updates
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
