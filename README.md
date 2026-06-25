# AiPay — Asistente y agente de pagos en el ecosistema IA

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
AiPay/
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
cd /home/delpo/Escritorio/AiPay
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
python3 -m unittest discover -v
```

## Referencia

Marco analítico: artículo de Víctor Alvargonzález sobre pagos digitales y agentes de IA (*elEconomista*). El proyecto evalúa de forma **independiente** con datos de mercado actuales.

## Lógica de la interfaz

Los tres botones y la barra de chat envían un texto a `handle_message()` → `agent.process_message()`. La diferencia está en **qué texto envían** y **qué modo activa** el agente.

### Flujo general

```text
Usuario (botón o chat)
    → handle_message()
    → fetch_ecosystem_snapshot() [CoinGecko + CBDC + señales IA]
    → ¿Petición explícita de evaluación/ranking?
        Sí  → MODO AGENTE (ranking + informe completo)
        No  → MODO ASISTENTE (respuesta focalizada)
    → GROQ redacta la respuesta
    → Pantalla: texto + panel (evaluación o mini mercado)
```

### 1. Botón «Evaluar ecosistema»

**Texto que envía:**

> «Evalúa el ecosistema actual de pagos para agentes de IA con datos en vivo»

**Por qué activa el modo AGENTE:**  
Contiene *«evalúa»*, que coincide con los disparadores de evaluación en `agent.py`.

**Qué hace paso a paso:**

1. **Consulta APIs** (`data_sources.py`):
   - CoinGecko → precio Bitcoin, capitalización USDT/USDC/DAI, mercado global
   - Datos CBDC → países en piloto, lanzamientos retail, etc.
   - Señales IA → OpenAI API, Stripe Agent, x402, etc.

2. **Evalúa** (`evaluator.py`):
   - Parte de 4 medios de pago: Bitcoin, CBDC, Stablecoins, Tokens de depósito
   - Puntúa 3 criterios (0–10): control político, estabilidad, compatibilidad IA
   - Ajusta puntuaciones con datos en vivo, por ejemplo:
     - BTC muy volátil → baja estabilidad
     - Stablecoins con mucha capitalización → sube compatibilidad IA

3. **Genera ranking** y marca ganadores (stablecoins + tokens de depósito)

4. **GROQ** redacta un informe legible para inversor/analista

5. **En pantalla** ves:
   - Texto del informe (GROQ)
   - Panel con métricas BTC/stablecoins/mercado
   - Ranking con barras de puntuación por criterio

### 2. Botón «Mercado stablecoins»

**Texto que envía:**

> «¿Cuál es la situación actual de las stablecoins en el mercado?»

**Modo:** ASISTENTE (no dispara evaluación completa)

**Qué hace:**

1. Consulta el snapshot (CoinGecko + CBDC + señales IA)
2. `assistant_engine.py` detecta que preguntas por **stablecoins**
3. Construye contexto solo relevante: datos USDT/USDC, cap. total, marco del artículo sobre stablecoins
4. GROQ responde solo a esa pregunta, sin repetir todo el informe
5. En pantalla: respuesta en texto + mini panel (precio BTC y cap. stablecoins si CoinGecko responde)

### 3. Botón «Estado CBDC»

**Texto que envía:**

> «¿Qué está pasando ahora con las CBDC en el mundo?»

**Modo:** ASISTENTE

**Qué hace:**

1. Snapshot en vivo (mercado cripto + datos CBDC)
2. El motor detecta **CBDC** en la pregunta
3. Contexto centrado en: países en desarrollo, pilotos activos, retail lanzado (e-CNY, Bahamas…), Europa en piloto
4. GROQ explica el estado actual de las monedas digitales de banco central
5. Sin ranking completo; respuesta conversacional

### 4. Barra de chat (pregunta libre)

**Texto:** lo que tú escribas.

**Lógica de decisión:**

| Si tu pregunta contiene… | Modo | Resultado |
|--------------------------|------|-----------|
| evalúa, evaluar, evaluación, ranking, puntúa, informe completo, análisis completo o analiza + ecosistema | Agente | Evaluación completa + panel |
| Cualquier otra cosa | Asistente | Respuesta focalizada |

**Ejemplos:**

- *«¿Cómo pagan hoy los agentes de IA?»* → Asistente: habla de créditos API, stablecoins, tokens
- *«Compara Bitcoin y stablecoins»* → Asistente: contexto comparativo, sin ranking formal
- *«Evalúa el ecosistema»* → Agente: informe completo

El asistente conserva contexto reciente, así puedes hacer seguimiento (*«¿y la CBDC?»*).

### Resumen

| Control | Rol |
|---------|-----|
| Evaluar ecosistema | Modo agente: APIs + scoring + ranking + informe completo |
| Mercado stablecoins | Atajo de chat sobre stablecoins con datos CoinGecko |
| Estado CBDC | Atajo de chat sobre CBDC mundial |
| Barra de chat | Pregunta libre; el sistema elige asistente o agente según las palabras |

Todo pasa por **GROQ** para la respuesta en lenguaje natural, pero los **datos numéricos** vienen de CoinGecko y del evaluador Python; el modelo no los inventa.
