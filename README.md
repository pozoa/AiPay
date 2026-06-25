# AIPAY — Asistente y agente de pagos en el ecosistema IA

Proyecto independiente inspirado en el artículo de **Víctor Alvargonzález** (*elEconomista*), pero orientado a **cómo se está realizando hoy la economía de pagos entre agentes de IA**: evalúa con datos en vivo, responde con GROQ y ejecuta evaluaciones completas en una **única interfaz de chat**.

## Hoja de ruta

| Fase | Estado | Descripción |
|------|--------|-------------|
| 1. Asistente | Activo | Chat con GROQ + datos en vivo (CoinGecko, CBDC) |
| 2. Agente | Activo | Evaluación automática del ecosistema con APIs y ranking |
| 3. Agente autónomo | Futuro | Creación y orquestación completa desde la interfaz |

## Qué hace

- **Una sola pantalla** — conversación, evaluación y datos de mercado en el mismo chat (sin pestañas).
- **Datos en vivo** — precios BTC, capitalización de stablecoins (CoinGecko), estado CBDC.
- **Evaluación dinámica** — puntuación ajustada según volatilidad, adopción y ecosistema IA.
- **Modo agente** — al pedir *«evalúa el ecosistema»*, consulta APIs, calcula ranking y sintetiza con GROQ.

## Estructura

```text
AIPAY/
├── app.py              # Interfaz única (Streamlit)
├── agent.py            # Orquestador asistente → agente
├── evaluator.py        # Evaluación dinámica con datos en vivo
├── data_sources.py     # APIs: CoinGecko, CBDC, señales IA
├── assistant_engine.py # Detección de intención y contexto
├── main.py             # Marco analítico base (elEconomista)
├── test_main.py
├── test_evaluator.py
└── requirements.txt
```

## Instalación

```bash
cd /home/delpo/Escritorio/AIPAY
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Añade GROQ_API_KEY
streamlit run app.py
```

## Uso

**Asistente** — preguntas libres:
- *«¿Cómo pagan hoy los agentes de IA?»*
- *«¿Cuál es la situación de las stablecoins?»*

**Agente** — evaluación completa:
- *«Evalúa el ecosistema de pagos para agentes IA»*
- Botón **Evaluar ecosistema** en la interfaz

## APIs utilizadas

| Fuente | Datos | Clave |
|--------|-------|-------|
| CoinGecko | BTC, USDT, USDC, DAI, mercado global | No |
| CBDC Tracker (curado) | Pilotos, países, lanzamientos | No |
| GROQ | Síntesis y respuestas del asistente/agente | Sí (`GROQ_API_KEY`) |

## Tests

```bash
python -m unittest discover -v
```

## Referencia

Marco analítico: artículo de Víctor Alvargonzález sobre pagos digitales y agentes de IA (*elEconomista*). El proyecto evalúa de forma **independiente** con datos de mercado actuales.
