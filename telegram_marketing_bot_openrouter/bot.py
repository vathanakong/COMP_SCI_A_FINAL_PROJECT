import logging
import os
import time
from collections import defaultdict
from typing import Dict, List

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from openrouter_client import generate_response

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SYSTEM_PROMPT = (
    "You are Dexter, an expert social media strategist and copywriter. Tone: confident, energetic, direct, no fluff. First response MUST be exactly: 'Greetings! I am Dexter, your dedicated Digital Marketing Strategist. To craft the most effective strategies and compelling content for you, I need three crucial pieces of information:\n\n1. Your Niche/Industry: What specific market or sector do you operate in?\n2. Your Target Audience: Who are you trying to reach, in detail?\n3. Your Primary Campaign Goal: What measurable objective are we aiming for with this marketing effort? Rules: Wait for user context (niche, audience, goal) before giving strategy. Keep responses concise, highly actionable, platform-specific, and the output must be formatted for Telegram chat (no need to use bold text)."
)

MAX_HISTORY = 20
conversation_history: Dict[int, List[dict]] = defaultdict(list)

# Rate limiting: user_id -> list of timestamps
RATE_LIMIT = 20  # requests
RATE_WINDOW = 60  # seconds
user_requests: Dict[int, List[float]] = defaultdict(list)


def check_rate_limit(user_id: int) -> bool:
    """Return True if request allowed, False if rate limited."""
    now = time.time()
    # Clean old timestamps
    user_requests[user_id] = [t for t in user_requests[user_id] if now - t < RATE_WINDOW]
    if len(user_requests[user_id]) >= RATE_LIMIT:
        return False
    user_requests[user_id].append(now)
    return True


def add_to_history(chat_id: int, role: str, content: str) -> None:
    """Add a message to conversation history, trimming to MAX_HISTORY."""
    conversation_history[chat_id].append({"role": role, "content": content})
    # Keep only last MAX_HISTORY messages (each turn = user + assistant = 2 messages)
    if len(conversation_history[chat_id]) > MAX_HISTORY * 2:
        conversation_history[chat_id] = conversation_history[chat_id][-MAX_HISTORY * 2:]


def get_history(chat_id: int) -> List[dict]:
    """Get conversation history for a chat."""
    return conversation_history[chat_id].copy()


def clear_history(chat_id: int) -> None:
    """Clear conversation history for a chat."""
    conversation_history[chat_id].clear()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    clear_history(chat_id)
    await update.message.reply_text(
        "Hello! I'm Dexter, an expert social media strategist and copywriter. "
        "How can I help you today?\n\n"
        "Commands:\n"
        "/start - Restart conversation\n"
        "/help - Show this help\n"
        "/reset - Clear conversation history\n"
        "/model - Show current model"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Restart conversation\n"
        "/help - Show this help\n"
        "/reset - Clear conversation history\n"
        "/model - Show current model"
    )


async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    clear_history(chat_id)
    await update.message.reply_text("Conversation history cleared. Fresh start!")


async def model_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from openrouter_client import OPENROUTER_MODEL
    await update.message.reply_text(f"Current model: {OPENROUTER_MODEL}")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat_id = update.effective_chat.id
    user_message = update.message.text

    
    if not check_rate_limit(user.id):
        await update.message.reply_text(
            "You're sending messages too fast. Please wait a moment."
        )
        return

    try:
        history = get_history(chat_id)
        history.append({"role": "user", "content": user_message})

        bot_response = await generate_response(history, system_prompt=SYSTEM_PROMPT)

        add_to_history(chat_id, "user", user_message)
        add_to_history(chat_id, "assistant", bot_response)

        await update.message.reply_text(bot_response)

    except Exception as e:
        logger.error(f"Error generating response: {e}")
        await update.message.reply_text("Sorry, I couldn't process that. Please try again later.")


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN not found in .env. Please set it.")

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("reset", reset_cmd))
    application.add_handler(CommandHandler("model", model_cmd))

    # Message handler (non-commands)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.info("Bot started and polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()