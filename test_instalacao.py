#!/usr/bin/env python3
"""
Script de teste para validar a instalação do bot de viagem
"""

import sys
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def test_imports():
    """Testa se todas as dependências estão instaladas"""
    print("🔍 Testando importações de dependências...\n")
    
    testes = {
        "telegram": "python-telegram-bot",
        "geopy": "geopy",
        "dotenv": "python-dotenv",
        "logging": "logging (stdlib)",
        "asyncio": "asyncio (stdlib)",
        "math": "math (stdlib)",
    }
    
    falhas = []
    
    for modulo, nome in testes.items():
        try:
            __import__(modulo)
            print(f"✅ {nome:<40} - OK")
        except ImportError as e:
            print(f"❌ {nome:<40} - FALHA")
            falhas.append((nome, str(e)))
    
    return falhas


def test_geopy_geocoder():
    """Testa se o geocodificador geopy está funcionando"""
    print("\n\n🌍 Testando Geocodificador Geopy...\n")
    
    try:
        from geopy.geocoders import Nominatim
        
        geolocator = Nominatim(user_agent="meu_pai_premium_bot", timeout=10)
        
        # Testar geocodificação
        queries = [
            "Praça da Estação, Juiz de Fora, MG, Brasil",
            "Praça da Estação, Juiz de Fora, Brasil",
            "Praça da Estação, Juiz de Fora",
        ]
        print("Testando geocodificação de: 'Praça da Estação, Juiz de Fora'...")
        location = None
        for query in queries:
            location = geolocator.geocode(query, language="pt-BR", exactly_one=True)
            if location:
                print(f"✅ Encontrado com: {query}")
                break
        
        if location:
            print(f"✅ Geocodificação funcionando!")
            print(f"   📍 Latitude: {location.latitude:.4f}")
            print(f"   📍 Longitude: {location.longitude:.4f}")
            print(f"   📍 Endereço: {location.address}")
            return True
        else:
            print("❌ Geocodificador não encontrou o endereço")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar geocodificador: {e}")
        return False


def test_calculations():
    """Testa as funções de cálculo"""
    print("\n\n💰 Testando Cálculos de Preço...\n")
    
    TAXA_FIXA = 5.00
    VALOR_POR_KM = 2.50
    VALOR_POR_MINUTO = 0.60
    VELOCIDADE_MEDIA = 30
    
    distancias_teste = [5.42, 10.0, 15.5]
    
    for distancia in distancias_teste:
        tempo_horas = distancia / VELOCIDADE_MEDIA
        tempo_minutos = tempo_horas * 60
        
        valor_km = distancia * VALOR_POR_KM
        valor_tempo = tempo_minutos * VALOR_POR_MINUTO
        preco_total = TAXA_FIXA + valor_km + valor_tempo
        
        print(f"Distância: {distancia:.2f} km")
        print(f"  Tempo: {tempo_minutos:.0f} minutos")
        print(f"  Taxa: R$ {TAXA_FIXA:.2f}")
        print(f"  KM: R$ {valor_km:.2f}")
        print(f"  Tempo: R$ {valor_tempo:.2f}")
        print(f"  ✅ TOTAL: R$ {preco_total:.2f}\n")
    
    return True


def test_telegram_token():
    """Testa se o token do Telegram é válido"""
    print("\n\n🤖 Testando Token do Telegram...\n")
    
    TOKEN = os.getenv("TELEGRAM_TOKEN", "8305041771:AAHNthwbsa7ePECMIoXVDfjNOuqQHMlH5FI")
    
    try:
        from telegram import Bot
        import asyncio
        
        async def check_token():
            bot = Bot(token=TOKEN)
            try:
                me = await bot.get_me()
                print(f"✅ Token válido!")
                print(f"   🤖 Bot: @{me.username}")
                print(f"   👤 Nome: {me.first_name}")
                print(f"   🆔 ID: {me.id}")
                return True
            except Exception as e:
                print(f"❌ Erro ao validar token: {e}")
                return False
        
        result = asyncio.run(check_token())
        return result
        
    except Exception as e:
        print(f"❌ Erro ao testar token: {e}")
        return False


def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🚀 TESTE DE INSTALAÇÃO - BOT DE VIAGEM".center(60))
    print("=" * 60)
    
    # Teste 1: Importações
    falhas_imports = test_imports()
    
    if falhas_imports:
        print(f"\n\n❌ {len(falhas_imports)} dependência(s) não encontrada(s)!")
        print("\nInstale com:")
        print("pip install -r requirements.txt")
        return False
    
    # Teste 2: Geocodificador
    teste_geo = test_geopy_geocoder()
    
    # Teste 3: Cálculos
    teste_calc = test_calculations()
    
    # Teste 4: Token Telegram
    teste_token = test_telegram_token()
    
    # Resumo
    print("\n\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES".center(60))
    print("=" * 60)
    
    print(f"✅ Dependências: OK")
    print(f"{'✅' if teste_geo else '❌'} Geocodificador: {'OK' if teste_geo else 'ERRO'}")
    print(f"✅ Cálculos: OK")
    print(f"{'✅' if teste_token else '❌'} Token Telegram: {'OK' if teste_token else 'ERRO'}")
    
    if teste_geo and teste_token:
        print("\n" + "=" * 60)
        print("✨ TUDO PRONTO! Você pode iniciar o bot com:".center(60))
        print("=" * 60)
        print("\npython bot_viagem.py\n")
        return True
    else:
        print("\n⚠️ Corriga os erros acima antes de executar o bot\n")
        return False


if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
