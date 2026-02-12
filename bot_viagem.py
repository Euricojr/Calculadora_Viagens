import logging
import os
import math
from dotenv import load_dotenv
import re
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
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
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Button Constants
BTN_NOVO_ORCAMENTO = "🚀 Novo Orçamento"
BTN_CANCELAR = "❌ Cancelar"

# Constants for Calculation
BASE_PRICE = 3.00
PRICE_PER_KM = 1.25
PRICE_PER_MIN = 0.20
MINIMUM_FARE = 10.00
CAR_MODEL = "Toyota Yaris"

# Conversation States
DISTANCIA, TEMPO, CONDICAO = range(3)

def round_to_nearest_50_cents(amount):
    """Rounds the amount to the nearest 0.50"""
    return math.ceil(amount * 2) / 2

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the conversation and shows the main menu button."""
    logger.info("User %s started the conversation.", update.effective_user.first_name)
    
    # Force reset keyboard (just in case)
    temp_msg = await update.message.reply_text("🔄...", reply_markup=ReplyKeyboardRemove())
    try:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=temp_msg.message_id)
    except:
        pass

    keyboard = [[KeyboardButton(BTN_NOVO_ORCAMENTO)]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        is_persistent=True
    )
    
    await update.message.reply_text(
        "👋 **Bot de Viagens Premium**\n\n"
        f"🚗 Carro: **{CAR_MODEL}**\n"
        f"Toque no botão **'{BTN_NOVO_ORCAMENTO}'** abaixo para começar.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def novo_orcamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiates the budget calculation flow."""
    logger.info("User requested new budget.")
    
    keyboard = [[KeyboardButton(BTN_CANCELAR)]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        one_time_keyboard=True
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
    if text == BTN_CANCELAR:
        return await cancel(update, context)
        
    try:
        clean_text = text.replace(',', '.')
        distance = float(clean_text)
        
        if distance < 0:
             await update.message.reply_text("⛔ Valor inválido. Tente novamente.")
             return DISTANCIA

        context.user_data['distance'] = distance
        logger.info("Distance: %.2f km", distance)

        keyboard = [[KeyboardButton(BTN_CANCELAR)]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, 
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await update.message.reply_text(
            f"✅ **Distância:** {distance} km\n\n"
            "⏱️ **Qual o Tempo?**\n"
            "Digite quantos **minutos** vai levar.",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return TEMPO

    except ValueError:
        await update.message.reply_text("⚠️ Digite apenas números (ex: 5.2).")
        return DISTANCIA

async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the time input."""
    text = update.message.text
    if text == BTN_CANCELAR:
        return await cancel(update, context)

    try:
        clean_text = text.replace(',', '.')
        minutes = float(clean_text)
        
        if minutes < 0:
             await update.message.reply_text("⛔ Valor inválido.")
             return TEMPO

        context.user_data['minutes'] = minutes
        logger.info("Time: %.2f min", minutes)
        
        # Ask for Condition
        keyboard = [
            [KeyboardButton("☀️ Normal (1.0x)")],
            [KeyboardButton("🌧️ Chuva/Noite (1.2x)")],
            [KeyboardButton("🚦 Trânsito Pesado (1.4x)")],
            [KeyboardButton(BTN_CANCELAR)]
        ]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, 
            resize_keyboard=True, 
            one_time_keyboard=True
        )

        await update.message.reply_text(
            "🌤️ **Como está o trânsito/clima?**\n\n"
            "Selecione uma opção abaixo para ajustar o preço:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return CONDICAO

    except ValueError:
        await update.message.reply_text("⚠️ Digite apenas números.")
        return TEMPO

async def calculate_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calculates the final price based on condition."""
    text = update.message.text
    if text == BTN_CANCELAR:
        return await cancel(update, context)

    # Determine Multiplier
    multiplier = 1.0
    text_lower = text.lower()
    condition_name = "Normal"
    
    if "chuva" in text_lower or "noite" in text_lower or "1.2" in text:
        multiplier = 1.2
        condition_name = "Chuva/Noite 🌧️"
    elif "trânsito" in text_lower or "transito" in text_lower or "1.4" in text:
        multiplier = 1.4
        condition_name = "Trânsito Pesado 🚦"
    elif "normal" in text_lower or "1.0" in text:
        multiplier = 1.0
        condition_name = "Normal ☀️"
    else:
        await update.message.reply_text("⚠️ Por favor, selecione uma das opções do menu.")
        return CONDICAO

    distance = context.user_data['distance']
    minutes = context.user_data['minutes']

    # Logic: Base R$ 3,00 + (KM * 1,25) + (Min * 0,20)
    base_calc = BASE_PRICE + (PRICE_PER_KM * distance) + (PRICE_PER_MIN * minutes)
    
    # Apply Multiplier
    total_with_multiplier = base_calc * multiplier
    
    # Apply Minimum Fare
    final_raw = max(total_with_multiplier, MINIMUM_FARE)
    
    # Round to nearest 0.50
    final_price = round_to_nearest_50_cents(final_raw)
    
    # Formatting
    price_fmt = f"{final_price:.2f}".replace('.', ',')
    multiplier_fmt = f"{multiplier}x"
    
    response = (
        f"🚘 **ORÇAMENTO PREMIUM** 🚘\n"
        f"🏎️ _Veículo: {CAR_MODEL}_\n"
        f"───────────────────\n"
        f"📏 **Distância:** {distance} km\n"
        f"⏱️ **Tempo:** {minutes:.0f} min\n"
        f"📊 **Condição:** {condition_name}\n"
        f"───────────────────\n"
        f"💰 **TOTAL: R$ {price_fmt}**\n"
        f"───────────────────\n"
        f"_(Tarifa Mínima: R$ {MINIMUM_FARE:.2f} | Fator: {multiplier_fmt})_"
    )
    
    # Reset Keyboard
    keyboard = [[KeyboardButton(BTN_NOVO_ORCAMENTO)]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        is_persistent=True
    )

    await update.message.reply_text(response, parse_mode="Markdown", reply_markup=reply_markup)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels and ends the conversation."""
    logger.info("User canceled conversation.")
    keyboard = [[KeyboardButton(BTN_NOVO_ORCAMENTO)]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        is_persistent=True
    )
    await update.message.reply_text("🚫 **Operação Cancelada.**", parse_mode="Markdown", reply_markup=reply_markup)
    return ConversationHandler.END

if __name__ == '__main__':
    # Start the bot
    token = os.getenv("TELEGRAM_TOKEN")
    if not token or "NOVO_TOKEN_AQUI" in token:
        logger.error("TELEGRAM_TOKEN env var is missing or invalid.")
        print("❌ ERRO CRÍTICO: Token não configurado no arquivo .env!")
    else:
        print("🚀 Bot rodando localmente...")
        application = ApplicationBuilder().token(token).build()

        conv_handler = ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex(f"^{re.escape(BTN_NOVO_ORCAMENTO)}$"), novo_orcamento),
                CommandHandler("novo", novo_orcamento)
            ],
            states={
                DISTANCIA: [
                    MessageHandler(filters.Regex(f"^{re.escape(BTN_CANCELAR)}$"), cancel),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_distance)
                ],
                TEMPO: [
                    MessageHandler(filters.Regex(f"^{re.escape(BTN_CANCELAR)}$"), cancel),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)
                ],
                CONDICAO: [
                    MessageHandler(filters.Regex(f"^{re.escape(BTN_CANCELAR)}$"), cancel),
                    MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex(f"^({re.escape(BTN_NOVO_ORCAMENTO)})$"), calculate_final)
                ]
            },
            fallbacks=[CommandHandler("cancel", cancel)]
        )
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(conv_handler)
        
        application.run_polling()
