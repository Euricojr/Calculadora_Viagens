# 🚗 Calculadora de Viagens - Bot Telegram Premium

Um bot de Telegram simples e **rápido** para cálculo manual de preços de viagens, ideal para orçamentos de corridas particulares.

---

## 🎯 **Novidades e Ajustes (Fev/2026)**

O bot foi atualizado para simplificar o uso:

- **Sem GPS**: Agora você digita a distância e o tempo diretamente. Mais rápido e sem falhas de localização.
- **Botões Grandes**: Interface pensada para facilidade de uso no celular.
- **Preços de Mercado**: Valores ajustados para competir com apps (UberX/99Pop) mantendo lucro justo.

---

## 💰 **Tabela de Preços**

Os valores foram configurados para garantir competitividade e segurança:

| Item              | Valor        | Descrição                            |
| :---------------- | :----------- | :----------------------------------- |
| **Taxa Base**     | **R$ 3,00**  | Valor fixo ao iniciar a corrida      |
| **Km Rodado**     | **R$ 1,25**  | Custo por quilômetro                 |
| **Minuto**        | **R$ 0,20**  | Custo pelo tempo de viagem           |
| **Tarifa Mínima** | **R$ 10,00** | Nenhuma corrida custa menos que isso |

### ⚡ **Multiplicadores Dinâmicos**

Você pode aplicar taxas extras dependendo da situação:

1. **☀️ Normal (1.0x)**: Preço padrão da tabela.
2. **🌧️ Chuva/Noite (1.2x)**: Acréscimo de 20% no valor final.
3. **🚦 Trânsito Pesado (1.4x)**: Acréscimo de 40% (lucro extra).

---

## 🚀 **Como Usar**

1. **Inicie o Bot**:
   Envie `/start` ou clique em **🚀 Novo Orçamento**.

2. **Informe a Distância**:
   O bot perguntará: _"Qual a Distância?"_
   Digite apenas os números, ex: `5.6` ou `12`.

3. **Informe o Tempo**:
   O bot perguntará: _"Qual o Tempo?"_
   Digite os minutos estimados, ex: `15` ou `20`.

4. **Escolha a Condição**:
   Um menu aparecerá com as opções:
   - ☀️ Normal
   - 🌧️ Chuva/Noite
   - 🚦 Trânsito

5. **Resultado**:
   O bot envia um **Cartão de Orçamento** formatado e pronto para encaminhar ao cliente.

   > **Exemplo Prático**:
   > Corrida de **5.6km** em **15min** no modo Normal:
   > `3.00 + (1.25 * 5.6) + (0.20 * 15) = R$ 13.00`

---

## ⚙️ **Instalação e Execução**

### 1. Requisitos

- Python 3.8+ instalado
- Arquivo `.env` configurado com seu `TELEGRAM_TOKEN`

### 2. Rodando o Bot

No terminal (dentro da pasta do projeto):

```bash
# Ativar ambiente virtual (se houver)
.\venv\Scripts\activate

# Executar
python bot_viagem.py
```

### 3. Manter Rodando

Para parar o bot, use `Ctrl + C` no terminal.

---

## 🛠️ **Configuração Técnica**

O arquivo principal é `bot_viagem.py`. As constantes de preço estão no topo do arquivo para fácil alteração:

```python
BASE_PRICE = 3.00
PRICE_PER_KM = 1.25
PRICE_PER_MIN = 0.20
MINIMUM_FARE = 10.00
CAR_MODEL = "Toyota Yaris"
```

## 🐛 **Suporte**

Se o bot parar de responder:

1. Verifique se a janela do terminal (preta) está aberta.
2. Se fechou, abra novamente e rode o comando de execução.
3. Verifique sua conexão com a internet.

---

taskkill /F /IM python.exe

_Desenvolvido para agilizar o dia a dia no trânsito._ 🚘
