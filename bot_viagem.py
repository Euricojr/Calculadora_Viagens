import logging
import os
import sys
import math
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants for Calculation
BASE_PRICE = 5.00
PRICE_PER_KM = 2.50
PRICE_PER_MIN = 0.60
CAR_MODEL = "Toyota Yaris"

# Conversation States
DISTANCIA, TEMPO = range(2)

def round_to_nearest_50_cents(amount):
    """Rounds the amount to the nearest 0.50"""
    return math.ceil(amount * 2) / 2

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the conversation and shows the main menu button."""
    logger.info("User %s started the conversation.", update.effective_user.first_name)
    
    keyboard = [[KeyboardButton("🚀 Novo Orçamento")]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        is_persistent=True,
        input_field_placeholder="Clique no botão abaixo 👇"
    )
    
    await update.message.reply_text(
        "👋 **Bot de Viagens Premium**\n\n"
        "Toque no botão **'🚀 Novo Orçamento'** abaixo para começar.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def novo_orcamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiates the budget calculation flow."""
    logger.info("User requested new budget.")
    
    keyboard = [[KeyboardButton("❌ Cancelar")]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        input_field_placeholder="Digite a distância..."
    )

    await update.message.reply_text(
        "📏 **Qual a Distância?**\n\n"
        "Digite quantos **KM** tem a corrida (ex: 4.5 ou 12).",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return DISTANCIA

async def get_distance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the distance input."""
    text = update.message.text
    if text == "❌ Cancelar":
        return await cancel(update, context)
        
    try:
        # Replace comma with dot for conversion
        clean_text = text.replace(',', '.')
        distance = float(clean_text)
        
        if distance < 0:
             await update.message.reply_text("⛔ A distância não pode ser negativa. Tente novamente.")
             return DISTANCIA

        context.user_data['distance'] = distance
        logger.info("Distance received: %.2f km", distance)

        keyboard = [[KeyboardButton("❌ Cancelar")]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, 
            resize_keyboard=True, 
            input_field_placeholder="Digite os minutos..."
        )

        await update.message.reply_text(
            f"✅ **Distância:** {distance} km\n\n"
            "⏱️ **Qual o Tempo?**\n"
            "Digite quantos **minutos** vai levar (ex: 15 ou 20).",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return TEMPO

    except ValueError:
        await update.message.reply_text("⚠️ Por favor, digite apenas números (ex: 5.2).")
        return DISTANCIA

async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the time input and calculates price."""
    text = update.message.text
    if text == "❌ Cancelar":
        return await cancel(update, context)

    try:
        clean_text = text.replace(',', '.')
        minutes = float(clean_text)
        
        if minutes < 0:
             await update.message.reply_text("⛔ O tempo não pode ser negativo. Tente novamente.")
             return TEMPO

        logger.info("Time received: %.2f min", minutes)
        
        distance = context.user_data['distance']
        
        # Calculate Logic
        # R$ 5,00 base + R$ 2,50/km + R$ 0,60/min
        raw_price = BASE_PRICE + (PRICE_PER_KM * distance) + (PRICE_PER_MIN * minutes)
        
        # Rounding logic (Ceil to nearest 0.50 usually better for simple payments, 
        # or simple round logic. User asked for "nearest", let's standard round half up to nearest 0.50 or just use general rounding logic provided) 
        # Requirement: "arredondar o valor final para os 50 centavos mais próximos"
        # Logic: round(X / 0.5) * 0.5
        final_price = round(raw_price * 2) / 2
        
        # Formatting
        price_fmt = f"{final_price:.2f}".replace('.', ',')
        raw_price_fmt = f"{raw_price:.2f}".replace('.', ',')
        
        response = (
            f"🚘 **ORÇAMENTO PREMIUM** 🚘\n"
            f"🏎️ _Veículo: {CAR_MODEL}_\n\n"
            f"📏 **Distância:** {distance} km\n"
            f"⏱️ **Tempo:** {minutes:.0f} min\n"
            f"───────────────────\n"
            f"💰 **TOTAL: R$ {price_fmt}**\n"
            f"───────────────────\n"
            f"_(Cálculo exato seria R$ {raw_price_fmt})_"
        )
        
        # Reset Keyboard
        keyboard = [[KeyboardButton("🚀 Novo Orçamento")]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, 
            resize_keyboard=True, 
            is_persistent=True
        )

        await update.message.reply_text(response, parse_mode="Markdown", reply_markup=reply_markup)
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("⚠️ Por favor, digite apenas números para os minutos.")
        return TEMPO

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels and ends the conversation."""
    logger.info("User canceled conversation.")
    keyboard = [[KeyboardButton("🚀 Novo Orçamento")]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        is_persistent=True
    )
    await update.message.reply_text("🚫 **Operação Cancelada.**\nToque no botão abaixo para reiniciar.", parse_mode="Markdown", reply_markup=reply_markup)
    return ConversationHandler.END

def main():
    """Start the bot."""
    token = os.getenv("TELEGRAM_TOKEN")
    if not token or "NOVO_TOKEN_AQUI" in token:
        logger.error("TELEGRAM_TOKEN env var is missing or invalid.")
        print("❌ ERRO CRÍTICO: Token não configurado no arquivo .env!")
        return

    logger.info("Starting bot...")
    
    try:
        application = ApplicationBuilder().token(token).build()

        conv_handler = ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex("^🚀 Novo Orçamento$"), novo_orcamento),
                CommandHandler("novo", novo_orcamento)
            ],
            states={
                DISTANCIA: [
                    MessageHandler(filters.Regex("^❌ Cancelar$"), cancel),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_distance)
                ],
                TEMPO: [
                    MessageHandler(filters.Regex("^❌ Cancelar$"), cancel),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel)]
        )
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(conv_handler)

        logger.info("Bot is polling...")
        print("LOG: Bot is polling... Press Ctrl+C to stop.")
        application.run_polling()
        
    except Exception as e:
        logger.critical("Failed to start bot: %s", e)
        print(f"LOG: Failed to start: {e}")

if __name__ == "__main__":
    main()
