from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from aiohttp import web
import os
import json

# Get token from environment variables
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Initialize bot
app = Application.builder().token(TOKEN).build()

# ----- Command Handlers -----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    await update.message.reply_html(
        f"👋 Hello {user.mention_html()}!\n"
        "I'm your Vercel-hosted bot!\n"
        "Try /help for commands"
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
🛠 Available Commands:
/start - Start conversation
/help - Show this help
/ping - Check bot latency
/echo - Reply with your message
    """
    await update.message.reply_text(help_text)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ping command"""
    await update.message.reply_text("🏓 Pong!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo user's text message"""
    await update.message.reply_text(f"📢 You said: {update.message.text}")

# ----- Setup Handlers -----
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("ping", ping))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# ----- Vercel Serverless Handler -----
async def vercel_handler(request):
    try:
        # Parse Telegram update
        data = await request.json()
        update = Update.de_json(data, app.bot)
        
        # Process update
        await app.process_update(update)
        return web.Response(text="OK", status=200)
    
    except Exception as e:
        print(f"⚠️ Error: {str(e)}")
        return web.Response(text="Error", status=500)

# Vercel requires this named export
async def main(request):
    return await vercel_handler(request)
