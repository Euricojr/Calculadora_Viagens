#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GUIA RÁPIDO - Calculadora de Viagens Telegram Bot
"""

print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     🚗 CALCULADORA DE VIAGENS - BOT TELEGRAM PREMIUM 🚗        ║
║                                                                ║
║              Bot criado com sucesso! ✨                        ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

📁 ESTRUTURA DO PROJETO:
═══════════════════════════════════════════════════════════════

Calculadora_Viagens/
├── bot_viagem.py              ⭐ Arquivo principal do bot
├── requirements.txt           📦 Dependências do projeto
├── README.md                  📖 Documentação completa
├── EXEMPLOS_USO.md            📚 Exemplos práticos
├── test_instalacao.py         🧪 Script de teste
├── GUIA_RAPIDO.py             ⚡ Este arquivo (apenas info)
├── .env.example               ⚙️  Configurações exemplo
└── LICENSE                    📜 Licença do projeto


⚙️ INSTALAÇÃO RÁPIDA:
═══════════════════════════════════════════════════════════════

1️⃣ Instalar dependências:
   
   pip install -r requirements.txt

2️⃣ Validar instalação (RECOMENDADO):
   
   python test_instalacao.py

3️⃣ Iniciar o bot:
   
   python bot_viagem.py

⏳ O bot começará a rodar e ficará aguardando mensagens no Telegram!


🎯 COMO USAR NO TELEGRAM:
═══════════════════════════════════════════════════════════════

Após iniciar o bot, no seu Telegram:

1. Procure por: @Calculadora_Viagens_Bot
   (ou qualquer nome que tiver dado no BotFather)

2. Inicie conversando:

   /start
   └─ Mensagem de boas-vindas

   /rota Origem - Destino
   └─ /rota Rua Halfeld, Juiz de Fora - UFJF, Juiz de Fora
   
   /help
   └─ Lista de todos os comandos
   
   [Enviar Localização]
   └─ Calcular até Praça Jaraguá


📊 CONFIGURAÇÕES ATUAIS:
═══════════════════════════════════════════════════════════════

Token Telegram: ✅ Já configurado
Geocodificador: ✅ Nominatim (OpenStreetMap)
User Agent:     ✅ meu_pai_premium_bot

Preços:
  • Taxa Fixa:        R$ 5.00
  • Valor por KM:     R$ 2.50
  • Valor por Minuto: R$ 0.60
  • Velocidade Base:  30 km/h

Localização Padrão: Praça Jaraguá, Juiz de Fora


🔧 PERSONALIZAÇÃO:
═══════════════════════════════════════════════════════════════

Para modificar preços, edite em bot_viagem.py (linhas 20-26):

    TAXA_FIXA = 5.00
    VALOR_POR_KM = 2.50
    VALOR_POR_MINUTO = 0.60
    VELOCIDADE_MEDIA = 30

Para mudar localização padrão (linhas 27-28):

    LOCALIZACAO_PADRAO = (-21.7626, -43.3335)
    NOME_LOCAL_PADRAO = "Praça Jaraguá, Juiz de Fora"


📱 BOTS TESTE RECOMENDADOS:
═══════════════════════════════════════════════════════════════

Para testar antes de colocar em produção:

1. Crie um novo bot no BotFather:
   @BotFather no Telegram → /newbot

2. Copie o novo token

3. Substitua em bot_viagem.py (linha 25):
   TOKEN = "NOVO_TOKEN_AQUI"

4. Execute novamente


🛠️ SOLUCIONADORES DE PROBLEMAS:
═══════════════════════════════════════════════════════════════

❌ "ModuleNotFoundError: No module named 'telegram'"
   → pip install python-telegram-bot[all]

❌ "ModuleNotFoundError: No module named 'geopy'"
   → pip install geopy

❌ "O bot não responde"
   → Verifique se está rodando (veja console)
   → Reinicie: Ctrl+C e novamente python bot_viagem.py
   → Verifique o token

❌ "Endereço não encontrado"
   → Digite de forma mais completa (com cidade)
   → Teste: /rota Rua das Flores, Juiz de Fora - Praça Jaraguá, Juiz de Fora

❌ "Erro de timeout do geocodificador"
   → Aguarde alguns segundos
   → Verifique internet
   → Tente novamente


📚 DOCUMENTAÇÃO VERSIONADA:
═══════════════════════════════════════════════════════════════

README.md                      → Documentação completa
EXEMPLOS_USO.md               → Exemplos de conversas
GUIA_RAPIDO.py (este arquivo) → Quick start
bot_viagem.py                 → Código comentado


🚀 PRÓXIMOS PASSOS:
═══════════════════════════════════════════════════════════════

□ Instalar dependências: pip install -r requirements.txt
□ Testar instalação: python test_instalacao.py
□ Iniciar bot: python bot_viagem.py
□ Testar no Telegram: /start, /rota, /help
□ Ler documentação: README.md
□ Personalizar preços: bot_viagem.py (linhas 20-26)


💡 DICAS PROFISSIONAIS:
═══════════════════════════════════════════════════════════════

✓ Use ambiente virtual: python -m venv venv && .\\venv\\Scripts\\activate
✓ Registre logs: python bot_viagem.py > logs.txt 2>&1
✓ Use .env para tokens em produção (veja .env.example)
✓ Teste com test_instalacao.py antes de usar
✓ Monitore os logs para debug
✓ Use /help no Telegram para listar comandos


📞 SUPORTE:
═══════════════════════════════════════════════════════════════

Verifique o arquivo README.md para:
  • Troubleshooting detalhado
  • Exemplos de customização
  • Referências de APIs
  • Como adicionar novos comandos


🎉 VOCÊ ESTÁ PRONTO PARA COMEÇAR! 🎉


═══════════════════════════════════════════════════════════════
Para iniciar agora, execute:

    python bot_viagem.py

═══════════════════════════════════════════════════════════════
""")

# Verificação Rápida
print("\n✅ Verificação rápida de dependências...\n")

try:
    from telegram import __version__ as tg_version
    print(f"   ✅ python-telegram-bot v{tg_version}")
except ImportError:
    print(f"   ❌ python-telegram-bot não instalado")

try:
    from geopy import __version__ as geo_version
    print(f"   ✅ geopy v{geo_version}")
except ImportError:
    print(f"   ❌ geopy não instalado")

print("\n" + "=" * 66)
print("Se faltaram dependências, execute: pip install -r requirements.txt")
print("=" * 66 + "\n")
