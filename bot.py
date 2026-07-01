import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Get the bot token from Railway's environment variables ---
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables. Please set it in Railway.")

# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the /start command is issued."""
    welcome_text = (
        "👋 Hello! I am WordConvertBot.\n\n"
        "I can analyze any text you send me. Just send a message and I'll count:\n"
        "📝 Words\n"
        "🔠 Characters (with and without spaces)\n"
        "📄 Sentences\n\n"
        "You can also use these commands:\n"
        "/word_count - Count words in a text\n"
        "/character_count - Count characters in a text\n"
        "/sentence_count - Count sentences in a text\n"
        "/full_analysis - Get a complete analysis\n"
        "/help - Show this message again"
    )
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message."""
    await start(update, context)

# --- Analysis Functions ---
def analyze_text(text: str):
    """Perform all text analyses and return a dictionary of results."""
    # Word count
    words = re.findall(r'\b\w+\b', text)
    word_count = len(words)

    # Character count
    char_count_with_spaces = len(text)
    char_count_without_spaces = len(text.replace(" ", ""))

    # Sentence count
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])  # Count non-empty sentences

    return {
        "word_count": word_count,
        "char_with_spaces": char_count_with_spaces,
        "char_without_spaces": char_count_without_spaces,
        "sentence_count": sentence_count
    }

# --- Command Handlers for Specific Analyses ---
async def word_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Count words in the provided text."""
    text = ' '.join(context.args) if context.args else None
    if not text:
        await update.message.reply_text("Please provide some text. Example: /word_count This is a test.")
        return
    result = analyze_text(text)
    await update.message.reply_text(f"📝 Word Count: {result['word_count']}")

async def character_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Count characters in the provided text."""
    text = ' '.join(context.args) if context.args else None
    if not text:
        await update.message.reply_text("Please provide some text. Example: /character_count This is a test.")
        return
    result = analyze_text(text)
    await update.message.reply_text(
        f"🔠 Character Count:\n"
        f"With spaces: {result['char_with_spaces']}\n"
        f"Without spaces: {result['char_without_spaces']}"
    )

async def sentence_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Count sentences in the provided text."""
    text = ' '.join(context.args) if context.args else None
    if not text:
        await update.message.reply_text("Please provide some text. Example: /sentence_count This is a test. It has two sentences.")
        return
    result = analyze_text(text)
    await update.message.reply_text(f"📄 Sentence Count: {result['sentence_count']}")

async def full_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provide a complete analysis of the provided text."""
    text = ' '.join(context.args) if context.args else None
    if not text:
        await update.message.reply_text("Please provide some text. Example: /full_analysis This is a test.")
        return
    result = analyze_text(text)
    reply = (
        f"📊 **Full Analysis**\n\n"
        f"📝 Words: {result['word_count']}\n"
        f"🔠 Characters (with spaces): {result['char_with_spaces']}\n"
        f"🔠 Characters (without spaces): {result['char_without_spaces']}\n"
        f"📄 Sentences: {result['sentence_count']}"
    )
    await update.message.reply_text(reply)

# --- Message Handler for Plain Text ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Analyze any plain text message sent to the bot."""
    text = update.message.text
    result = analyze_text(text)
    reply = (
        f"📊 **Analysis**\n\n"
        f"📝 Words: {result['word_count']}\n"
        f"🔠 Characters (with spaces): {result['char_with_spaces']}\n"
        f"🔠 Characters (without spaces): {result['char_without_spaces']}\n"
        f"📄 Sentences: {result['sentence_count']}\n\n"
        f"Use /full_analysis for more details or specific commands like /word_count."
    )
    await update.message.reply_text(reply)

# --- Error Handler ---
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors."""
    print(f"Update {update} caused error {context.error}")

# --- Main Function ---
def main():
    """Start the bot."""
    print("Starting WordConvertBot...")
    
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("word_count", word_count))
    application.add_handler(CommandHandler("character_count", character_count))
    application.add_handler(CommandHandler("sentence_count", sentence_count))
    application.add_handler(CommandHandler("full_analysis", full_analysis))

    # Register message handler for all text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Register error handler
    application.add_error_handler(error_handler)

    # Start the bot using long polling. No webhook needed for Railway[citation:7][citation:9].
    print("Bot is polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
