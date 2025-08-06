# bot.py

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
# from index import main_logic  # Import your function
from app import run_main  # Assuming main.py contains the logic you want to run
from dotenv import load_dotenv
import os


load_dotenv()  # Load .env file

# Replace with your actual bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = run_main()
    await update.message.reply_text(response)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handle both /start and /check
    app.add_handler(CommandHandler(["start", "check"], handle_command))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()