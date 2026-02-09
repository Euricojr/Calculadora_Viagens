# 🚗 Calculadora de Viagens - Bot Telegram Premium

Um bot de Telegram profissional para cálculo de preços de viagem com localização em tempo real.

## 🎯 Funcionalidades

✨ **Cálculo de Rotas**: Calcula distância real entre endereços usando geopy
💰 **Preços Transparentes**: Mostra detalhamento completo (taxa fixa + km + minutos)
📍 **Suporte a Localização**: Integra compartilhamento de localização do Telegram
🚗 **Formatação Premium**: Respostas elegantes em cartão de visita
🛡️ **Tratamento de Erros**: Valida endereços e comunica problemas claramente

## 📋 Requisitos

- Python 3.8+
- Conexão com internet
- Token de Bot do Telegram

## 🚀 Instalação

### 1. Clonar/Visitar o Repositório

```bash
cd c:/Users/ddom1/Calculadora_Viagens
```

### 2. Criar Ambiente Virtual (Opcional, mas recomendado)

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

## ⚙️ Configuração

O token do bot já está configurado no arquivo:

```python
TOKEN = "8305041771:AAHNthwbsa7ePECMIoXVdfjN0uqQHM1H5FI"
```

Os preços estão configurados como:

- **Taxa Fixa**: R$ 5,00
- **Valor por KM**: R$ 2,50
- **Valor por Minuto**: R$ 0,60
- **Velocidade Média**: 30 km/h (para cidades)

## 📱 Comandos do Bot

### /start

Exibe mensagem de boas-vindas profissional com instruções de uso.

### /rota

Calcula preço de uma rota entre dois endereços.

**Formato**: `/rota Origem - Destino`

**Exemplo**:

```
/rota Rua Halfeld, Juiz de Fora - UFJF, Juiz de Fora
```

### Compartilhamento de Localização

Envie sua localização (botão anexo do Telegram) para calcular a distância até a Praça Jaraguá.

### /help

Mostra lista completa de comandos e dicas de uso.

## 🔧 Estrutura do Código

### Funções Principais

#### `calcular_distancia(endereco1, endereco2)`

- Converte endereços em coordenadas usando geopy
- Usa fórmula de Haversine para calcular distância real
- Suporta strings (endereços) ou tuplas (coordenadas)
- Retorna: (distância_km, endereco_completo_1, endereco_completo_2)

#### `calcular_preco(distancia_km)`

- Calcula tempo estimado: distância / 30 km/h
- Aplica fórmula: Taxa Fixa + (km × valor/km) + (minutos × valor/min)
- Retorna: (preço_total, tempo_estimado)

#### `formatar_orcamento(...)`

- Cria resposta elegante em formato de cartão
- Inclui detalhamento de custos
- Mostra modelo do carro e meios de pagamento

#### Handlers de Comandos

- `start()`: Boas-vindas
- `rota()`: Processa comando /rota
- `handle_location()`: Processa localização do usuário
- `help_command()`: Exibe ajuda

## 🌍 Geocodificação

Usa **Nominatim (OpenStreetMap)** da biblioteca geopy:

- User Agent: `meu_pai_premium_bot`
- Nenhuma chave de API necessária
- Respeita limite de requisições
- Trata timeouts e erros graciosamente

## 💳 Formatos de Saída

### Exemplo de Resposta

```
✨ ORÇAMENTO PREMIUM ✨

📍 De: Rua Halfeld, 123 - Juiz de Fora, MG

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

## 🏃 Executar o Bot

```bash
python bot_viagem.py
```

Você verá a mensagem:

```
🚀 Bot iniciado com sucesso!
```

Agora o bot está pronto para receber mensagens no Telegram!

## 🐛 Tratamento de Erros

- ✅ Endereço não encontrado: Mensagem clara informando qual endereço falhou
- ✅ Timeout de geocodificação: Comunica erro de conexão
- ✅ Formato de comando inválido: Sugere formato correto
- ✅ Erros gerais: Log detalhado para debugging

## 📊 Variáveis Configuráveis

Modifique estas constantes no inicio do arquivo para ajustar:

```python
TAXA_FIXA = 5.00              # Taxa base em R$
VALOR_POR_KM = 2.50           # Custo por km em R$
VALOR_POR_MINUTO = 0.60       # Custo por minuto em R$
VELOCIDADE_MEDIA = 30         # Velocidade média em km/h
LOCALIZACAO_PADRAO = (...)    # Coordenadas padrão
NOME_LOCAL_PADRAO = "..."     # Nome do local padrão
```

## 🔐 Segurança

- Token armazenado no código (em produção, use variáveis de ambiente)
- User Agent customizado para evitar bloqueios
- Logging de todos os erros
- Validação de entrada para todos os comandos

## 📝 Logs

Todos os eventos são registrados com timestamp:

```
2026-02-09 10:30:45 - __main__ - INFO - 🚀 Bot iniciado com sucesso!
2026-02-09 10:31:12 - __main__ - INFO - Usuário solicitou rota...
```

## 🚨 Troubleshooting

### "Origem não encontrada"

- Verifique a grafia do endereço
- Inclua a cidade no endereço
- Tente um endereço mais específico (com número)

### "Erro ao conectar ao serviço de localização"

- Verifique sua conexão com internet
- Aguarde alguns segundos e tente novamente
- O serviço Nominatim pode ter limite de requisições

### Bot não responde

- Verifique se o token está correto
- Confira se o bot está rodando (veja mensagem "🚀 Bot iniciado")
- Reinicie o bot
- Verifique os logs

## 📄 Licença

Projeto criado para uso profissional em transporte.

## 👨‍💻 Desenvolvido com ❤️

Bot completo para Telegram v20+ em Python

taskkill /F /IM python.exe # para matar o processo do python
