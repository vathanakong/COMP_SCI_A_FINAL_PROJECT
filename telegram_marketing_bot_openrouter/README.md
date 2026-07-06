# Telegram Marketing Chatbot (OpenRouter)

This is a  Telegram bot powered by OpenRouter LLMs for marketing interactions. It features conversation memory, command handling, and rate limiting.

## Features

- **OpenRouter integration** — Use any model on OpenRouter (GPT-4, Claude, Llama, Gemini, etc.)
- **Conversation memory** — Remembers last 20 exchanges per chat
- **Command handling** — `/start`, `/help`, `/reset`, `/history`, `/model`, `/rate`
- **Rate limiting** — 20 requests/minute per user
- **Marketing-focused system prompt** — Engages users persuasively

## Setup

1. **Clone and install dependencies**
   
   cd telegram_marketing_bot_openrouter
   pip install -r requirements.txt
   

2. **Configure environment**
   
   cp .env.example .env
   # Edit .env with your credentials
   

3. **Required `.env` variables**
   
   TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
   OPENROUTER_API_KEY=your_openrouter_api_key
   OPENROUTER_MODEL=any OpenRouter model ID (can find on OpenRouter's website by searching the model name)
   

4. **Run the bot**
   
   Open a new terminal in VS CODE and run:

   python bot.py
   

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Show all commands |
| `/reset` | Clear conversation history |
| `/history` | Show recent messages |
| `/model` | Show current OpenRouter model |
| `/rate` | Show remaining rate limit |

## Project Structure

telegram_marketing_bot_openrouter/
├── bot.py                 # Main bot logic (commands, history, rate limiting)
├── openrouter_client.py   # OpenRouter API client
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── .gitignore             # This file
└── README.md              # This file

## Customization

- **System prompt** — Edit `SYSTEM_PROMPT` in `bot.py` for different personas
- **Rate limit** — Adjust `RATE_LIMIT` and `RATE_WINDOW` in `bot.py`
- **History length** — Change `MAX_HISTORY` in `bot.py`
- **Model** — Set `OPENROUTER_MODEL` in `.env` (see [OpenRouter models](https://openrouter.ai/models))

## Requirements

- Python 3.8+
- Telegram bot token (from [@BotFather](https://t.me/BotFather))
- OpenRouter API key (from [openrouter.ai](https://openrouter.ai))
