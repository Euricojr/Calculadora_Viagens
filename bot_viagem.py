import logging
import os
import sys
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
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

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
AVG_SPEED_KMH = 30

# Conversation States
ORIGIN, DESTINATION = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the conversation and shows the main menu button."""
    logger.info("User %s started the conversation.", update.effective_user.first_name)
    
    keyboard = [[KeyboardButton("🚀 Novo Orçamento")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    await update.message.reply_text(
        "Olá! Eu sou o Bot de Viagens do seu pai.\n"
        "Toque no botão abaixo para calcular uma viagem correta e segura!",
        reply_markup=reply_markup
    )

async def novo_orcamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiates the budget calculation flow."""
    logger.info("User requested new budget.")
    
    # Keyboard to request location
    keyboard = [[KeyboardButton("📍 Enviar minha localização atual", request_location=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        "Certo! Primeiro, **onde é o ponto de partida?**\n"
        "Você pode escrever o endereço ou enviar sua localização clicando no botão abaixo.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return ORIGIN

async def get_origin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the origin input (Text or Location)."""
    user = update.effective_user
    message = update.message

    if message.location:
        # User sent GPS location
        lat = message.location.latitude
        lon = message.location.longitude
        origin_coords = (lat, lon)
        origin_address = "Localização GPS (Atual)"
        logger.info("Origin received via GPS: %s", origin_coords)
    else:
        # User sent text
        address_text = message.text
        logger.info("Origin received via text: %s", address_text)
        
        geolocator = Nominatim(user_agent="bot_viagem_pai")
        try:
            location = geolocator.geocode(address_text, timeout=10)
            if not location:
                await message.reply_text("Não consegui encontrar esse endereço. Tente ser mais específico (ex: Rua X, Cidade Y).")
                return ORIGIN
            
            origin_coords = (location.latitude, location.longitude)
            origin_address = location.address
            logger.info("Geocoded origin: %s -> %s", address_text, origin_coords)
        except Exception as e:
            logger.error("Error geocoding origin: %s", e)
            await message.reply_text("Ocorreu um erro ao buscar o endereço. Tente novamente.")
            return ORIGIN

    # Save to context
    context.user_data['origin_coords'] = origin_coords
    context.user_data['origin_address'] = origin_address

    await message.reply_text(
        f"✅ Partida definida: *{origin_address}*\n\n"
        "Agora, **onde é o destino?** (Digite o nome da rua, bairro ou cidade)",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True) # Remove keyboard
    )
    return DESTINATION

async def get_destination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the destination input and performs calculation."""
    message = update.message
    destination_text = message.text
    logger.info("Destination received: %s", destination_text)

    geolocator = Nominatim(user_agent="bot_viagem_pai")
    try:
        location = geolocator.geocode(destination_text, timeout=10)
        if not location:
            await message.reply_text("Não consegui encontrar o destino. Tente ser mais específico.")
            return DESTINATION
        
        dest_coords = (location.latitude, location.longitude)
        dest_address = location.address
        logger.info("Geocoded destination: %s -> %s", destination_text, dest_coords)
    except Exception as e:
        logger.error("Error geocoding destination: %s", e)
        await message.reply_text("Erro ao buscar destino. Tente novamente.")
        return DESTINATION

    # Calculation
    origin_coords = context.user_data.get('origin_coords')
    if not origin_coords:
        await message.reply_text("Ocorreu um erro com o ponto de partida. Vamos recomeçar?")
        return ConversationHandler.END

    # Distance in km
    distance_km = geodesic(origin_coords, dest_coords).km
    
    # Estimated time (min) = (Distance / 30km/h) * 60 min
    estimated_time_min = (distance_km / AVG_SPEED_KMH) * 60
    
    # Price
    # Base R$ 5 + (2.5 * km) + (0.6 * min)
    price_total = BASE_PRICE + (PRICE_PER_KM * distance_km) + (PRICE_PER_MIN * estimated_time_min)

    # Rounding
    distance_km = round(distance_km, 2)
    estimated_time_min = int(round(estimated_time_min))
    price_total = round(price_total, 2)

    logger.info("Calculation: Dist=%.2f km, Time=%d min, Price=R$ %.2f", distance_km, estimated_time_min, price_total)

    response = (
        f"🏁 *Orçamento Calculado!* 🏁\n\n"
        f"📍 *De:* {context.user_data.get('origin_address', 'Desconhecido')}\n"
        f"🏁 *Para:* {dest_address}\n\n"
        f"📏 *Distância:* {distance_km} km\n"
        f"⏱️ *Tempo Estimado:* {estimated_time_min} min\n\n"
        f"💰 *VALOR FINAL: R$ {price_total:.2f}*\n\n"
        f"_Base R$ {BASE_PRICE:.2f} + Km R$ {PRICE_PER_KM:.2f} + Min R$ {PRICE_PER_MIN:.2f}_"
    )

    # Show "Novo Orçamento" button again
    keyboard = [[KeyboardButton("🚀 Novo Orçamento")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await message.reply_text(response, parse_mode="Markdown", reply_markup=reply_markup)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels and ends the conversation."""
    logger.info("Conversation canceled by user.")
    await update.message.reply_text(
        "Operação cancelada. Toque em 🚀 Novo Orçamento quando quiser.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🚀 Novo Orçamento")]], resize_keyboard=True)
    )
    return ConversationHandler.END

def main():
    """Start the bot."""
    token = os.getenv("TELEGRAM_TOKEN")
    if not token or "TOKEN" in token and "AQUI" in token: # Simple check for placeholder
        logger.error("Error: TELEGRAM_TOKEN not found in .env or is a placeholder.")
        print("ERRO: Configure o TELEGRAM_TOKEN no arquivo .env antes de rodar!")
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
                ORIGIN: [
                    MessageHandler(filters.LOCATION, get_origin),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_origin)
                ],
                DESTINATION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_destination)
                ]
            },
            fallbacks=[CommandHandler("cancel", cancel)]
        )

        application.add_handler(CommandHandler("start", start))
        application.add_handler(conv_handler)

        logger.info("Bot is polling...")
        application.run_polling()
        
    except Exception as e:
        logger.critical("Failed to start bot: %s", e, exc_info=True)

if __name__ == "__main__":
    main()
