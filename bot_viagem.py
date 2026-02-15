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
BTN_CONSUMO = "⛽ Calcular Consumo"
BTN_RESUMO = "📅 Resumo Diário"

# Constants for Calculation
BASE_PRICE = 3.00
PRICE_PER_KM = 1.25
PRICE_PER_MIN = 0.20
MINIMUM_FARE = 10.00
CAR_MODEL = "Toyota Yaris"

# Conversation States
DISTANCIA, TEMPO, CONDICAO, CON_LITROS, CON_KM, DIARIA_RIDAS, DIARIA_GANHO, DIARIA_COMB = range(8)

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

    keyboard = [[KeyboardButton(BTN_NOVO_ORCAMENTO), KeyboardButton(BTN_CONSUMO), KeyboardButton(BTN_RESUMO)]]
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
        condition_name = "Chuva/Noite"
    elif "trânsito" in text_lower or "transito" in text_lower or "1.4" in text:
        multiplier = 1.4
        condition_name = "Trânsito Pesado"
    elif "normal" in text_lower or "1.0" in text:
        multiplier = 1.0
        condition_name = "Normal"
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
    
    # Message 1: Driver Panel (Technical)
    driver_msg = (
        f"<b>🚖 PAINEL DO MOTORISTA</b>\n"
        f"──────────────\n"
        f"<b>� FINAL: R$ {price_fmt}</b>\n"
        f"<b>�📏 Dist:</b> {distance} km\n"
        f"<b>⏱️ Tempo:</b> {minutes:.0f} min\n"
        f"<b>🌧️ Fator:</b> {multiplier_fmt} ({condition_name})\n"
        f"──────────────\n"
        f"<i>(Mínimo: R$ {MINIMUM_FARE:.2f})</i>"
    )

    # Message 2: Passenger Message (Clean & Polite)
    passenger_msg = (
        f"Olá! Segue o orçamento da sua viagem:\n\n"
        f"<b>R$ {price_fmt}</b>\n\n"
        f"🚗 <b>Carro:</b> {CAR_MODEL}\n"
        f"📏 <b>Distância:</b> {distance} km\n"
        f"⏱️ <b>Tempo Estimado:</b> {minutes:.0f} min\n\n"
        f"<i>Qualquer dúvida, estou à disposição!</i>"
    )
    
    # Reset Keyboard (show both options)
    keyboard = [[KeyboardButton(BTN_NOVO_ORCAMENTO), KeyboardButton(BTN_CONSUMO)]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        is_persistent=True
    )

    # Send Driver Message
    await update.message.reply_text(driver_msg, parse_mode="HTML")

    # Send Passenger Message
    await update.message.reply_text(passenger_msg, parse_mode="HTML", reply_markup=reply_markup)
    
    return ConversationHandler.END


async def diario_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia o fluxo de resumo diário (corridas, ganho, combustível)."""
    logger.info("User started diario flow.")

    keyboard = [[KeyboardButton(BTN_CANCELAR)]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "📅 **Resumo Diário**\n\n"
        "Quantas corridas você fez hoje? (ex: 12)",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return DIARIA_RIDAS


async def diario_get_rides(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == BTN_CANCELAR:
        return await cancel(update, context)

    try:
        rides = int(text)
        if rides < 0:
            await update.message.reply_text("⛔ Valor inválido. Informe um número inteiro não-negativo.")
            return DIARIA_RIDAS

        context.user_data['diaria_rides'] = rides

        keyboard = [[KeyboardButton(BTN_CANCELAR)]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await update.message.reply_text(
            f"✅ Corridas: {rides}\n\nQuanto você ganhou no total hoje? (R$, ex: 150.50)",
            reply_markup=reply_markup
        )
        return DIARIA_GANHO

    except ValueError:
        await update.message.reply_text("⚠️ Digite apenas um número inteiro (ex: 12).")
        return DIARIA_RIDAS


async def diario_get_earned(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == BTN_CANCELAR:
        return await cancel(update, context)

    try:
        clean = text.replace(',', '.')
        earned = float(clean)
        if earned < 0:
            await update.message.reply_text("⛔ Valor inválido. Informe um número não-negativo.")
            return DIARIA_GANHO

        context.user_data['diaria_earned'] = earned

        keyboard = [[KeyboardButton(BTN_CANCELAR)]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await update.message.reply_text(
            f"✅ Ganho total: R$ {earned:.2f}\n\nQuanto você gastou com combustível hoje? (R$, ex: 60.5)",
            reply_markup=reply_markup
        )
        return DIARIA_COMB

    except ValueError:
        await update.message.reply_text("⚠️ Digite apenas números (ex: 150.50).")
        return DIARIA_GANHO


async def diario_get_fuel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == BTN_CANCELAR:
        return await cancel(update, context)

    try:
        clean = text.replace(',', '.')
        fuel_spent = float(clean)
        if fuel_spent < 0:
            await update.message.reply_text("⛔ Valor inválido. Informe um número não-negativo.")
            return DIARIA_COMB

        rides = context.user_data.get('diaria_rides', 0)
        earned = context.user_data.get('diaria_earned', 0.0)

        profit = earned - fuel_spent
        profit_per_ride = profit / rides if rides > 0 else profit
        margin_pct = (profit / earned * 100) if earned > 0 else 0.0

        # Format numbers for pt-BR style
        earned_fmt = f"{earned:.2f}".replace('.', ',')
        fuel_fmt = f"{fuel_spent:.2f}".replace('.', ',')
        profit_fmt = f"{profit:.2f}".replace('.', ',')
        profit_per_fmt = f"{profit_per_ride:.2f}".replace('.', ',')
        margin_fmt = f"{margin_pct:.2f}".replace('.', ',')

        msg = (
            f"📊 <b>Resumo Diário</b>\n\n"
            f"🚖 Corridas: <b>{rides}</b>\n"
            f"💰 Ganho total: <b>R$ {earned_fmt}</b>\n"
            f"⛽ Combustível: <b>R$ {fuel_fmt}</b>\n\n"
            f"🧾 Lucro líquido: <b>R$ {profit_fmt}</b>\n"
            f"📈 Lucro por corrida: <b>R$ {profit_per_fmt}</b>\n"
            f"📊 Margem: <b>{margin_fmt}%</b>\n"
        )

        # Reset keyboard (show main options)
        keyboard = [[KeyboardButton(BTN_NOVO_ORCAMENTO), KeyboardButton(BTN_CONSUMO), KeyboardButton(BTN_RESUMO)]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            is_persistent=True
        )

        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=reply_markup)
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("⚠️ Digite apenas números (ex: 60.50).")
        return DIARIA_COMB


async def consumo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the fuel consumption flow (liters -> km)."""
    logger.info("User started consumo flow.")

    keyboard = [[KeyboardButton(BTN_CANCELAR)]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "⛽ **Consumo de Combustível**\n\n"
        "Quantos litros foram abastecidos? (ex: 40 ou 40.5)",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return CON_LITROS


async def consumo_get_liters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == BTN_CANCELAR:
        return await cancel(update, context)

    try:
        clean_text = text.replace(',', '.')
        liters = float(clean_text)
        if liters <= 0:
            await update.message.reply_text("⛔ Valor inválido. Informe um número maior que zero.")
            return CON_LITROS

        context.user_data['liters'] = liters

        keyboard = [[KeyboardButton(BTN_CANCELAR)]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await update.message.reply_text(
            f"✅ Litros: {liters}\n\nQuanto KM foram rodados desde esse abastecimento?",
            reply_markup=reply_markup
        )
        return CON_KM

    except ValueError:
        await update.message.reply_text("⚠️ Digite apenas números (ex: 40.5).")
        return CON_LITROS


async def consumo_get_km(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == BTN_CANCELAR:
        return await cancel(update, context)

    try:
        clean_text = text.replace(',', '.')
        km = float(clean_text)
        if km <= 0:
            await update.message.reply_text("⛔ Valor inválido. Informe um número maior que zero.")
            return CON_KM

        liters = context.user_data.get('liters')
        if not liters:
            await update.message.reply_text("⚠️ Não encontrei os litros. Reinicie com /consumo.")
            return ConversationHandler.END

        km_per_l = km / liters
        liters_per_100 = (liters * 100) / km

        kmpl_fmt = f"{km_per_l:.2f}".replace('.', ',')
        l100_fmt = f"{liters_per_100:.2f}".replace('.', ',')

        msg = (
            f"📊 Resultado do Consumo:\n\n"
            f"🚗 Kilômetros rodados: {km} km\n"
            f"⛽ Litros: {liters}\n\n"
            f"📈 Consumo: <b>{kmpl_fmt} km/l</b>\n"
            f"📉 Consumo médio: <b>{l100_fmt} L/100km</b>\n"
        )

        # Reset keyboard (show both options)
        keyboard = [[KeyboardButton(BTN_NOVO_ORCAMENTO), KeyboardButton(BTN_CONSUMO)]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            is_persistent=True
        )

        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=reply_markup)
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("⚠️ Digite apenas números (ex: 150).")
        return CON_KM

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels and ends the conversation."""
    logger.info("User canceled conversation.")
    keyboard = [[KeyboardButton(BTN_NOVO_ORCAMENTO), KeyboardButton(BTN_CONSUMO)]]
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
        
        # Conversation handler for consumo (km/l)
        # Conversation handler for diario (resumo diário)
        conv_diario = ConversationHandler(
            entry_points=[
                CommandHandler("diario", diario_start),
                MessageHandler(filters.Regex(f"^{re.escape(BTN_RESUMO)}$"), diario_start)
            ],
            states={
                DIARIA_RIDAS: [
                    MessageHandler(filters.Regex(f"^{re.escape(BTN_CANCELAR)}$"), cancel),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, diario_get_rides)
                ],
                DIARIA_GANHO: [
                    MessageHandler(filters.Regex(f"^{re.escape(BTN_CANCELAR)}$"), cancel),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, diario_get_earned)
                ],
                DIARIA_COMB: [
                    MessageHandler(filters.Regex(f"^{re.escape(BTN_CANCELAR)}$"), cancel),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, diario_get_fuel)
                ]
            },
            fallbacks=[CommandHandler("cancel", cancel)]
        )

        conv_consumo = ConversationHandler(
            entry_points=[
                CommandHandler("consumo", consumo_start),
                MessageHandler(filters.Regex(f"^{re.escape(BTN_CONSUMO)}$"), consumo_start)
            ],
            states={
                CON_LITROS: [
                    MessageHandler(filters.Regex(f"^{re.escape(BTN_CANCELAR)}$"), cancel),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, consumo_get_liters)
                ],
                CON_KM: [
                    MessageHandler(filters.Regex(f"^{re.escape(BTN_CANCELAR)}$"), cancel),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, consumo_get_km)
                ]
            },
            fallbacks=[CommandHandler("cancel", cancel)]
        )

        application.add_handler(CommandHandler("start", start))
        application.add_handler(conv_handler)
        application.add_handler(conv_diario)
        application.add_handler(conv_consumo)
        
        application.run_polling()
