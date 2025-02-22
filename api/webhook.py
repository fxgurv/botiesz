from telegram import Update, ForceReply
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
import json
import os
from http.server import BaseHTTPRequestHandler

# Your bot token from BotFather
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Initialize bot application
application = Application.builder().token(TOKEN).build()

# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! 👋\nI'm your bot. Use /help to see available commands.",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
/ping - Check if bot is alive
    """
    await update.message.reply_text(help_text)

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Response to /ping command"""
    await update.message.reply_text("Pong! 🏓")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message."""
    await update.message.reply_text(f"You said: {update.message.text}")

# Register handlers
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("ping", ping_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Vercel serverless function handler
async def handle_webhook(update_data):
    try:
        update = Update.de_json(update_data, application.bot)
        await application.process_update(update)
        return {"statusCode": 200, "body": "OK"}
    except Exception as e:
        print(f"Error processing update: {e}")
        return {"statusCode": 500, "body": "Error processing update"}

class handler(BaseHTTPRequestHandler):
    async def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            update_data = json.loads(post_data.decode())
            
            result = await handle_webhook(update_data)
            
            self.send_response(result["statusCode"])
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(result["body"].encode())
        except Exception as e:
            print(f"Error in webhook handler: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("Internal server error".encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write("Bot webhook is running!".encode())
