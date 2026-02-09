# 📚 Exemplos de Uso - Bot de Viagem

## 🎯 Primeiros Passos

### 1. Instalação de Dependências
```bash
pip install -r requirements.txt
```

### 2. Validar Instalação
```bash
python test_instalacao.py
```

### 3. Iniciar o Bot
```bash
python bot_viagem.py
```

---

## 💬 Exemplos de Conversas no Telegram

### Exemplo 1: Comando /start
```
Usuário: /start

Bot: 
👋 Bem-vindo ao CALCULADORA DE VIAGENS PREMIUM! 👋

Olá Marcos! 

Somos uma plataforma inovadora de transporte que oferece:

✅ Cálculo preciso de rotas
✅ Preços justos e transparentes
✅ Veículos de qualidade
✅ Atendimento profissional

🎯 Como usar:

1️⃣ Use o comando /rota seguido do formato:
   /rota Origem - Destino
   
   Exemplo: /rota Rua Halfeld, Juiz de Fora - UFJF, Juiz de Fora
...
```

### Exemplo 2: Comando /rota (Sucesso)
```
Usuário: /rota Rua Halfeld, Juiz de Fora - UFJF, Juiz de Fora

Bot:
⏳ Processando sua rota...
🔍 Buscando endereços e calculando distância...

[Após processamento]

✨ ORÇAMENTO PREMIUM ✨

📍 De: Rua Halfeld - Juiz de Fora, MG

🏁 Para: Universidade Federal de Juiz de Fora - Juiz de Fora, MG

📏 Distância: 5.42 km
⏱️ Tempo estimado: 11 minutos

🚗 Veículo: Toyota Corolla XEi 2.0

💰 Detalhamento:
   • Taxa fixa: R$ 5.00
   • Distância (5.42 km × R$ 2.50): R$ 13.55
   • Tempo (11 min × R$ 0.60): R$ 6.60

💳 Valor Sugerido: R$ 25.15

💳 Aceitamos Pix e Cartão

Obrigado por usar nosso serviço! 🙏
```

### Exemplo 3: Comando /rota (Erro)
```
Usuário: /rota Rua Inexistente, Cidade Fantasma - Local que não existe

Bot:
⏳ Processando sua rota...

❌ Erro ao processar a rota:

Origem não encontrada: Rua Inexistente, Cidade Fantasma
Destino não encontrado: Local que não existe

[Sugestão: Verifique a grafia dos endereços]
```

### Exemplo 4: Compartilhamento de Localização
```
Usuário: [Compartilha localização via Telegram - Coordenadas: -21.76, -43.33]

Bot:
⏳ Processando sua localização...
📍 Sua posição: -21.7600, -43.3300
🔍 Calculando distância até a Praça Jaraguá...

[Após processamento]

✨ ORÇAMENTO PREMIUM ✨

📍 De: Sua posição (-21.7600, -43.3300)

🏁 Para: Praça Jaraguá, Juiz de Fora

📏 Distância: 0.05 km
⏱️ Tempo estimado: 0 minutos

🚗 Veículo: Toyota Corolla XEi 2.0

💰 Detalhamento:
   • Taxa fixa: R$ 5.00
   • Distância (0.05 km × R$ 2.50): R$ 0.12
   • Tempo (0 min × R$ 0.60): R$ 0.00

💳 Valor Sugerido: R$ 5.12

💳 Aceitamos Pix e Cartão

Obrigado por usar nosso serviço! 🙏
```

### Exemplo 5: Comando /help
```
Usuário: /help

Bot:
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
```

### Exemplo 6: Comando /rota (Formato Inválido)
```
Usuário: /rota Rua Halfeld Juiz de Fora UFJF

Bot:
❌ Formato inválido!

Use: /rota Origem - Destino

Exemplo: /rota Rua Halfeld, Juiz de Fora - UFJF, Juiz de Fora
```

---

## 🔧 Exemplos de Customização

### Modificar Preços
Abra `bot_viagem.py` e localize:
```python
# Preços (Perfil Econômico)
TAXA_FIXA = 5.00              # Mude para a taxa desejada
VALOR_POR_KM = 2.50           # Mude para o valor desejado
VALOR_POR_MINUTO = 0.60       # Mude para o valor desejado
```

### Mudar Localização Padrão
```python
LOCALIZACAO_PADRAO = (-21.7626, -43.3335)  # Coordenadas (lat, lon)
NOME_LOCAL_PADRAO = "Praça Jaraguá, Juiz de Fora"
```

### Alterar Modelo do Carro
Localize a função `formatar_orcamento`:
```python
modelo_carro = "Toyota Corolla XEi 2.0"  # Mude para o modelo desejado
```

### Mudar Velocidade Média
```python
VELOCIDADE_MEDIA = 30  # Mude para a velocidade desejada em km/h
```

---

## ⚡ Dicas e Truques

### 1. Obter IDs de Usuários
Para fazer logging mais detalhado:
```python
print(f"Usuário: {update.effective_user.id} ({update.effective_user.first_name})")
```

### 2. Adicionar Novos Comandos
```python
async def novo_comando(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Resposta aqui")

# No main():
application.add_handler(CommandHandler("novo", novo_comando))
```

### 3. Adicionar Handlers de Texto
```python
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Você disse: {update.message.text}")
```

### 4. Usar Teclados Customizados
```python
keyboard = [
    [KeyboardButton("Opção 1"), KeyboardButton("Opção 2")],
    [KeyboardButton("Opção 3")]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
await update.message.reply_text("Escolha uma opção:", reply_markup=reply_markup)
```

### 5. Usar Teclados Inline (com callbacks)
```python
keyboard = [
    [InlineKeyboardButton("Sim", callback_data='sim'), 
     InlineKeyboardButton("Não", callback_data='nao')]
]
reply_markup = InlineKeyboardMarkup(keyboard)
await update.message.reply_text("Confirmar?", reply_markup=reply_markup)
```

---

## 🧪 Testando Localmente

### Teste 1: Validar Cálculo de Distância
```python
# No Python, teste manualmente:
import asyncio
from bot_viagem import calcular_distancia, calcular_preco

async def test():
    dist, orig, dest = await calcular_distancia(
        "Rua Halfeld, Juiz de Fora", 
        "UFJF, Juiz de Fora"
    )
    preco, tempo = await calcular_preco(dist)
    print(f"Distância: {dist:.2f} km")
    print(f"Preço: R$ {preco:.2f}")
    print(f"Tempo: {tempo:.0f} min")

asyncio.run(test())
```

### Teste 2: Validar Geocodificação
```python
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="meu_pai_premium_bot")
location = geolocator.geocode("Praça Jaraguá, Juiz de Fora")
print(f"Lat: {location.latitude}, Lon: {location.longitude}")
```

---

## 🚀 Próximos Passos

Ideias para expansão do bot:

1. **Banco de Dados**: Armazenar histórico de viagens
2. **Pagamento**: Integrar gateway de pagamento (Stripe, PagSeguro)
3. **Avaliações**: Sistema de reviews de usuários e motoristas
4. **Admin Panel**: Dashboard para gerenciar preços e viagens
5. **Notificações**: Alertas de chegada do motorista
6. **Multiple Viagens**: Agendar viagens para horários futuros
7. **Categorias**: Oferecer diferentes tipos de veículos
8. **Cupons**: Sistema de desconto e promoções

---

## 📞 Suporte e Debugging

### Ativar Modo Debug
Modifique o nível de logging:
```python
logging.basicConfig(level=logging.DEBUG)  # Mais informações
```

### Ver Logs Detalhados
```bash
python bot_viagem.py 2>&1 | Tee bot.log
```

### Parar o Bot
```
Ctrl + C  (no terminal)
```

---

## 📖 Referências

- [python-telegram-bot docs](https://python-telegram-bot.readthedocs.io/)
- [geopy docs](https://geopy.readthedocs.io/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

Divirta-se! 🎉
