import logging
import re

from telegram import ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from utils import *

from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

# logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# avoid GET & POST
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


SEARCH_COLLECTION = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def market_time_range(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("24h", callback_data="24h"),
            InlineKeyboardButton("7d", callback_data="7d")
        ], [
            InlineKeyboardButton("30d", callback_data="30d"),
            InlineKeyboardButton("All", callback_data="all"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Choose a time range:", reply_markup=reply_markup)

async def market(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    text = get_market(query.data)
    await query.edit_message_text(text=text)

async def collection_rankings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = get_collection_rankings()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def collection_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter project name")

    return SEARCH_COLLECTION

async def search_collection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.message.text
    
    text = get_search_collection(query)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    
    return ConversationHandler.END
    



def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(CommandHandler("market", market_time_range))
    application.add_handler(CallbackQueryHandler(market))

    application.add_handler(CommandHandler("collection", collection_rankings))

    search_collection_conv = ConversationHandler(
        entry_points=[CommandHandler('search', collection_name)], 
        states={SEARCH_COLLECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_collection)]},
        fallbacks=[]
        )

    application.add_handler(search_collection_conv)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()