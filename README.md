# AIPAY — Análisis de medios de pago para la era de la IA

Proyecto en Python que evalúa cuatro medios de pago digitales según el artículo de **Víctor Alvargonzález** (*elEconomista*): *«El medio de pago del futuro lo elegirá la inteligencia artificial»*.

El objetivo es identificar qué instrumentos están mejor posicionados para transacciones entre agentes de IA, con implicaciones para inversores y el futuro del Bitcoin y otras criptomonedas.

## Contenido del proyecto

| Archivo | Descripción |
|---------|-------------|
| `main.py` | Lógica de evaluación: puntuación, ranking y determinación de ganadores |
| `test_main.py` | Pruebas unitarias (`unittest`) |
| `app.py` | Interfaz web Streamlit con asistente GROQ |
| `requirements.txt` | Dependencias Python |
| `.env.example` | Plantilla para la API key de GROQ |
| `ejecutar_local.sh` / `.bat` | Scripts de arranque rápido |

## Medios de pago evaluados

1. **Bitcoin** — Reserva digital de valor; descartado como moneda global por volatilidad e independencia de bancos centrales.
2. **CBDC** — Moneda digital de banco central; máximo control político, adopción ciudadana incierta.
3. **Stablecoins** — Criptos ancladas a activos estables (dólar, euro, letras del tesoro). **Candidata ganadora.**
4. **Tokens de depósito** — Respaldados por depósitos bancarios y de BC; unidad natural para agentes IA. **Candidato ganador.**

## Criterios de evaluación (0–10)

| Criterio | Qué mide |
|----------|----------|
| Control político | Aceptación por gobiernos y bancos centrales |
| Estabilidad financiera | Baja volatilidad, aptitud para comercio |
| Compatibilidad con IA | Velocidad, digitalización, uso entre agentes |

## Resultado del análisis

| Posición (puntos) | Medio de pago | Puntuación |
|-------------------|---------------|------------|
| 1 | Tokens de depósito | 28 |
| 2 | CBDC | 27 |
| 3 | Stablecoins | 23 |
| 4 | Bitcoin | 12 |

**Ganadores estratégicos:** Stablecoins y Tokens de depósito. Aunque la CBDC puntúa más que las stablecoins, el artículo prioriza los **modelos híbridos** por equilibrar IA, estabilidad y viabilidad política/social sin el rechazo ciudadano de una moneda 100 % estatal.

## Requisitos

- Python 3.10 o superior
- Navegador web moderno
- Clave API de [GROQ](https://console.groq.com) (solo para el asistente)

## Instalación y uso

### 1. Clonar o abrir el proyecto en Cursor

```bash
cd /home/delpo/Escritorio/AIPAY
```

En Cursor, usa **Ctrl + I** (Agent/Composer) para iterar sobre el código con el doble agente.

### 2. Entorno virtual e dependencias

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

### 3. Configurar GROQ (asistente)

```bash
cp .env.example .env
# Edita .env y añade tu GROQ_API_KEY
```

### 4. Ejecutar la evaluación por consola

```bash
python main.py
```

### 5. Ejecutar tests

```bash
python -m unittest test_main.py -v
```

### 6. Lanzar la interfaz web

```bash
streamlit run app.py
# o bien:
./ejecutar_local.sh
```

La interfaz incluye tres pestañas:

- **Evaluación** — Ranking visual con barras de puntuación
- **Productos** — Fichas de Bitcoin, CBDC, stablecoins y tokens de depósito
- **Asistente GROQ** — Chat sobre los productos financieros (no sobre el código del proyecto)

## Subir a GitHub

```bash
git init
git add .
git commit -m "Commit inicial: Proyecto de evaluación de pagos para la IA"
```

Crea un repositorio vacío en GitHub y vincúlalo:

```bash
git remote add origin https://github.com/TU_USUARIO/AIPAY.git
git branch -M main
git push -u origin main
```

## Estructura

```text
AIPAY/
├── main.py
├── test_main.py
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── ejecutar_local.sh
├── ejecutar_local.bat
└── README.md
```

## Referencia

Artículo base: análisis de Víctor Alvargonzález sobre pagos digitales, stablecoins, CBDC y el papel de la IA en el comercio del futuro (*elEconomista*, 25/06/2026).

## Licencia

Uso educativo y de análisis financiero. No constituye asesoramiento de inversión.
