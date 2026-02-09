import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configurações
TOKEN = os.getenv("TELEGRAM_TOKEN", "8305041771:AAHNthwbsa7ePECMIoXVdfjN0uqQHM1H5FI")
USER_AGENT = "meu_pai_premium_bot"

# Preços (Perfil Econômico)
TAXA_FIXA = 5.00
VALOR_POR_KM = 2.50
VALOR_POR_MINUTO = 0.60
VELOCIDADE_MEDIA = 30  # km/h para cidade
LOCALIZACAO_PADRAO = (-21.7626, -43.3335)  # Praça Jaraguá, Juiz de Fora
NOME_LOCAL_PADRAO = "Praça Jaraguá, Juiz de Fora"

# Inicialização do geocodificador
geolocator = Nominatim(user_agent=USER_AGENT, timeout=10)


def _build_geocode_queries(query):
    query = query.strip()
    queries = [query]
    if "Juiz de Fora" in query and "MG" not in query and "Minas" not in query:
        queries.append(f"{query}, MG, Brasil")
    if "Brasil" not in query and "Brazil" not in query:
        queries.append(f"{query}, Brasil")
    seen = set()
    unique_queries = []
    for item in queries:
        if item not in seen:
            unique_queries.append(item)
            seen.add(item)
    return unique_queries


async def _geocode_with_fallback(query):
    for candidate in _build_geocode_queries(query):
        loc = await asyncio.to_thread(
            geolocator.geocode,
            candidate,
            language="pt-BR",
            exactly_one=True
        )
        if loc:
            return loc
    return None


async def calcular_distancia(endereco1, endereco2):
    """
    Calcula a distância (em km) entre dois endereços usando geopy.
    
    Args:
        endereco1 (str ou tuple): Primeiro endereço ou coordenadas (lat, lon)
        endereco2 (str ou tuple): Segundo endereço ou coordenadas (lat, lon)
    
    Returns:
        tuple: (distancia_km, endereco1_completo, endereco2_completo) ou None se falhar
    """
    try:
        # Se for string, geocodificar
        if isinstance(endereco1, str):
            loc1 = await _geocode_with_fallback(endereco1)
            if not loc1:
                return None, f"Origem não encontrada: {endereco1}", None
            coords1 = (loc1.latitude, loc1.longitude)
            endereco1_nome = loc1.address
        else:
            coords1 = endereco1
            endereco1_nome = NOME_LOCAL_PADRAO

        if isinstance(endereco2, str):
            loc2 = await _geocode_with_fallback(endereco2)
            if not loc2:
                return None, endereco1_nome, f"Destino não encontrado: {endereco2}"
            coords2 = (loc2.latitude, loc2.longitude)
            endereco2_nome = loc2.address
        else:
            coords2 = endereco2
            endereco2_nome = NOME_LOCAL_PADRAO

        # Usar fórmula de Haversine para calcular distância
        from math import radians, sin, cos, sqrt, atan2
        
        lat1, lon1 = coords1
        lat2, lon2 = coords2
        
        R = 6371  # Raio da Terra em km
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distancia = R * c
        
        return distancia, endereco1_nome, endereco2_nome
        
    except (GeocoderTimedOut, GeocoderServiceError):
        return None, "Erro ao conectar ao serviço de localização", None
    except Exception as e:
        logger.error(f"Erro ao calcular distância: {e}")
        return None, f"Erro ao processar endereço: {str(e)}", None


async def calcular_preco(distancia_km):
    """
    Calcula o preço da viagem baseado na distância.
    
    Args:
        distancia_km (float): Distância em quilômetros
    
    Returns:
        tuple: (preco, tempo_minutos)
    """
    tempo_horas = distancia_km / VELOCIDADE_MEDIA
    tempo_minutos = tempo_horas * 60
    
    valor_km = distancia_km * VALOR_POR_KM
    valor_tempo = tempo_minutos * VALOR_POR_MINUTO
    preco_total = TAXA_FIXA + valor_km + valor_tempo
    
    return preco_total, tempo_minutos


async def formatar_orcamento(origem, destino, distancia, preco, tempo):
    """
    Formata a resposta como um cartão de visita elegante.
    
    Args:
        origem (str): Endereço de origem
        destino (str): Endereço de destino
        distancia (float): Distância em km
        preco (float): Preço em R$
        tempo (float): Tempo estimado em minutos
    
    Returns:
        str: Mensagem formatada
    """
    modelo_carro = "Toyota Corolla XEi 2.0"  # Modelo padrão
    
    mensagem = f"""
✨ ORÇAMENTO PREMIUM ✨

📍 De: {origem}

🏁 Para: {destino}

📏 Distância: {distancia:.2f} km
⏱️ Tempo estimado: {int(tempo)} minutos

🚗 Veículo: {modelo_carro}

💰 Detalhamento:
   • Taxa fixa: R$ {TAXA_FIXA:.2f}
   • Distância ({distancia:.2f} km × R$ {VALOR_POR_KM:.2f}): R$ {distancia * VALOR_POR_KM:.2f}
   • Tempo ({int(tempo)} min × R$ {VALOR_POR_MINUTO:.2f}): R$ {tempo * VALOR_POR_MINUTO:.2f}

💳 Valor Sugerido: R$ {preco:.2f}

💳 Aceitamos Pix e Cartão

Obrigado por usar nosso serviço! 🙏
"""
    return mensagem


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /start"""
    usuario = update.effective_user.first_name or "Passageiro"
    
    mensagem_boas_vindas = f"""
👋 Bem-vindo ao CALCULADORA DE VIAGENS PREMIUM! 👋

Olá {usuario}! 

Somos uma plataforma inovadora de transporte que oferece:

✅ Cálculo preciso de rotas
✅ Preços justos e transparentes
✅ Veículos de qualidade
✅ Atendimento profissional

🎯 Como usar:

1️⃣ Use o comando /rota seguido do formato:
   /rota Origem - Destino
   
   Exemplo: /rota Rua Halfeld, Juiz de Fora - UFJF, Juiz de Fora

2️⃣ Ou compartilhe sua localização e usaremos a Praça Jaraguá como referência

📍 Sua localização será usada como ponto de partida se você compartilhá-la

Estamos prontos para calcular sua próxima viagem! 🚗
"""
    
    await update.message.reply_text(mensagem_boas_vindas)


async def rota(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /rota"""
    
    # Verificar se foi fornecido um argumento
    if not context.args:
        await update.message.reply_text(
            "❌ Uso incorreto!\n\n"
            "Use: /rota Origem - Destino\n\n"
            "Exemplo: /rota Rua Halfeld, Juiz de Fora - UFJF, Juiz de Fora"
        )
        return
    
    # Juntar os argumentos
    rota_texto = " ".join(context.args)
    
    # Verificar se contém o separador " - "
    if " - " not in rota_texto:
        await update.message.reply_text(
            "❌ Formato inválido!\n\n"
            "Use: /rota Origem - Destino\n\n"
            "Exemplo: /rota Rua Halfeld, Juiz de Fora - UFJF, Juiz de Fora"
        )
        return
    
    # Extrair origem e destino
    partes = rota_texto.split(" - ", 1)
    origem = partes[0].strip()
    destino = partes[1].strip()
    
    # Enviar mensagem de processamento
    mensagem_carregamento = await update.message.reply_text(
        "⏳ Processando sua rota...\n"
        "🔍 Buscando endereços e calculando distância..."
    )
    
    try:
        # Calcular distância
        distancia, endereco_origem, endereco_destino = await calcular_distancia(origem, destino)
        
        if distancia is None:
            # Erro ao geocodificar
            await mensagem_carregamento.edit_text(
                f"❌ Erro ao processar a rota:\n\n"
                f"{endereco_origem}\n"
                f"{endereco_destino}"
            )
            return
        
        # Calcular preço
        preco, tempo = await calcular_preco(distancia)
        
        # Formatar orcamento
        orcamento = await formatar_orcamento(endereco_origem, endereco_destino, distancia, preco, tempo)
        
        # Editar mensagem com o resultado
        await mensagem_carregamento.edit_text(orcamento)
        
    except Exception as e:
        logger.error(f"Erro ao processar rota: {e}")
        await mensagem_carregamento.edit_text(
            f"❌ Erro ao processar sua solicitação:\n{str(e)}"
        )


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mensagens de localização"""
    
    # Obter as coordenadas do usuário
    localizacao_usuario = update.message.location
    coords_usuario = (localizacao_usuario.latitude, localizacao_usuario.longitude)
    
    mensagem_carregamento = await update.message.reply_text(
        "⏳ Processando sua localização...\n"
        f"📍 Sua posição: {localizacao_usuario.latitude:.4f}, {localizacao_usuario.longitude:.4f}\n"
        "🔍 Calculando distância até a Praça Jaraguá..."
    )
    
    try:
        # Calcular distância do usuário até o local padrão
        distancia, endereco_origem, endereco_destino = await calcular_distancia(
            coords_usuario,
            LOCALIZACAO_PADRAO
        )
        
        if distancia is None:
            await mensagem_carregamento.edit_text(
                "❌ Erro ao processar sua localização. Tente novamente!"
            )
            return
        
        # Calcular preço
        preco, tempo = await calcular_preco(distancia)
        
        # Formatar orcamento
        orcamento = await formatar_orcamento(
            f"Sua posição ({coords_usuario[0]:.4f}, {coords_usuario[1]:.4f})",
            endereco_destino,
            distancia,
            preco,
            tempo
        )
        
        await mensagem_carregamento.edit_text(orcamento)
        
    except Exception as e:
        logger.error(f"Erro ao processar localização: {e}")
        await mensagem_carregamento.edit_text(
            f"❌ Erro ao processar sua localização:\n{str(e)}"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /help"""
    mensagem = """
📚 AJUDA - Comandos Disponíveis

/start - Mensagem de boas-vindas
/help - Esta mensagem
/rota - Calcular preço de uma rota
    Formato: /rota Origem - Destino
    Exemplo: /rota Rua Halfeld, Juiz de Fora - UFJF, Juiz de Fora

📍 Compartilhamento de Localização:
   Você também pode enviar sua localização (botão de localização no Telegram)
   e calcularemos a distância até a Praça Jaraguá

💡 Dicas:
   • Seja específico com os endereços (rua, número, cidade)
   • Use "-" para separar origem e destino
   • A localização pode levar alguns segundos para processar
"""
    await update.message.reply_text(mensagem)


def main():
    """Função principal para iniciar o bot"""
    
    # Criar application
    application = Application.builder().token(TOKEN).build()
    
    # Adicionar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rota", rota))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    
    # Iniciar o bot
    logger.info("🚀 Bot iniciado com sucesso!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
