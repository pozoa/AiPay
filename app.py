"""
Interfaz web AIPAY: evaluación visual de medios de pago y asistente GROQ.

El asistente responde sobre los productos financieros analizados (Bitcoin, CBDC,
stablecoins y tokens de depósito), no sobre la configuración del proyecto.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from main import (
    CRITERIA_LABELS,
    PAYMENT_METHODS,
    build_evaluation_report,
    format_report_text,
    get_payment_method,
    get_winners,
    rank_payment_methods,
)

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

SYSTEM_PROMPT = """Eres un asesor financiero especializado en medios de pago digitales
para la era de los agentes de IA. Tu conocimiento se basa en el análisis de
Víctor Alvargonzález (elEconomista) sobre el futuro de los pagos.

PRODUCTOS QUE DEBES EXPLICAR (no hables de cómo está programado este proyecto):

1. Bitcoin — Cripto descentralizada, volátil, reserva digital de valor, no moneda global.
2. CBDC — Moneda digital de banco central, máximo control estatal, adopción social difícil.
3. Stablecoins — Criptos ancladas al dólar/euro/letras del tesoro; modelo híbrido ganador.
4. Tokens de depósito — Tokens respaldados por depósitos bancarios/BC; ideales para agentes IA.

CRITERIOS DE EVALUACIÓN: control político, estabilidad financiera, compatibilidad con IA.
GANADORES DEL ANÁLISIS: Stablecoins y Tokens de depósito.

Responde en español, de forma clara y concisa. Si no sabes algo, dilo.
Usa los datos del informe adjunto como fuente de verdad numérica."""


def query_groq(user_message: str, context: str) -> str:
    """Envía una consulta al API de GROQ."""
    if not GROQ_API_KEY:
        return (
            "⚠️ Configura tu clave GROQ_API_KEY en el archivo `.env` para activar "
            "el asistente. Puedes obtener una en https://console.groq.com"
        )

    try:
        from groq import Groq
    except ImportError:
        return "⚠️ Instala dependencias: `pip install -r requirements.txt`"

    client = Groq(api_key=GROQ_API_KEY)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Informe de evaluación actual:\n\n{context}\n\n"
                f"Pregunta del usuario: {user_message}"
            ),
        },
    ]

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.2,
            max_tokens=1024,
        )
        return response.choices[0].message.content or "Sin respuesta del modelo."
    except Exception as exc:
        return f"❌ Error al consultar GROQ: {exc}"


def render_score_bar(label: str, score: int) -> None:
    st.progress(score / 10, text=f"{label}: {score}/10")


def render_evaluation_tab() -> None:
    st.subheader("Ranking de medios de pago")
    report = build_evaluation_report()
    winners = {winner["id"] for winner in report["winners"]}

    for index, item in enumerate(report["ranking"], start=1):
        badge = " 🏆" if item["id"] in winners else ""
        with st.expander(f"{index}. {item['name']} — {item['total']} pts{badge}", expanded=index <= 2):
            st.caption(item["role"])
            st.write(item["justification"])
            for criterion, score in item["scores"].items():
                render_score_bar(CRITERIA_LABELS[criterion], score)

    st.divider()
    st.subheader("Conclusión")
    st.info(report["conclusion"])

    st.subheader("Datos en JSON")
    st.json(report)


def render_products_tab() -> None:
    st.subheader("Fichas de productos")
    cols = st.columns(2)
    for index, method in enumerate(PAYMENT_METHODS):
        with cols[index % 2]:
            st.markdown(f"### {method.name}")
            st.caption(method.role)
            st.write(method.description)
            st.metric("Puntuación total", method.total_score())
            for criterion, score in method.scores.items():
                st.write(f"**{CRITERIA_LABELS[criterion]}:** {score}/10")


def render_assistant_tab() -> None:
    st.subheader("Asistente GROQ sobre medios de pago")

    if not GROQ_API_KEY:
        st.warning(
            "Introduce tu `GROQ_API_KEY` en `.env` (copia `.env.example` como plantilla). "
            "El asistente explica Bitcoin, CBDC, stablecoins y tokens de depósito."
        )
    else:
        st.success(f"Conectado a GROQ — modelo `{GROQ_MODEL}`")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    context = format_report_text()

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    suggestions = [
        "¿Por qué Bitcoin no será la moneda global del futuro?",
        "¿Qué son las stablecoins y por qué son candidatas ganadoras?",
        "Compara CBDC y tokens de depósito para agentes de IA",
        "¿Qué empresas o sectores podrían beneficiarse de las stablecoins?",
    ]

    st.caption("Preguntas sugeridas:")
    suggestion_cols = st.columns(2)
    for index, suggestion in enumerate(suggestions):
        if suggestion_cols[index % 2].button(suggestion, key=f"suggest_{index}"):
            st.session_state.pending_question = suggestion

    prompt = st.chat_input("Pregunta sobre los medios de pago analizados...")
    if "pending_question" in st.session_state:
        prompt = st.session_state.pop("pending_question")

    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consultando GROQ..."):
                answer = query_groq(prompt, context)
            st.markdown(answer)

        st.session_state.chat_history.append({"role": "assistant", "content": answer})

    if st.session_state.chat_history and st.button("Limpiar conversación"):
        st.session_state.chat_history = []
        st.rerun()


def main() -> None:
    st.set_page_config(
        page_title="AIPAY — Pagos para la era de la IA",
        page_icon="💳",
        layout="wide",
    )

    st.title("💳 AIPAY")
    st.markdown(
        "Análisis de **medios de pago digitales** para circuitos de agentes de IA, "
        "basado en el artículo de Víctor Alvargonzález (*elEconomista*)."
    )

    winners = get_winners()
    winner_names = ", ".join(winner.name for winner in winners)
    st.success(f"Ganadores del análisis: **{winner_names}**")

    tab_eval, tab_products, tab_assistant = st.tabs(
        ["📊 Evaluación", "📦 Productos", "🤖 Asistente GROQ"]
    )

    with tab_eval:
        render_evaluation_tab()
    with tab_products:
        render_products_tab()
    with tab_assistant:
        render_assistant_tab()

    with st.sidebar:
        st.header("Resumen rápido")
        ranking = rank_payment_methods()
        for index, method in enumerate(ranking, start=1):
            st.write(f"{index}. {method.name} — {method.total_score()} pts")

        st.divider()
        st.caption("Ejecutar por consola: `python main.py`")
        st.caption("Tests: `python -m unittest test_main.py`")


if __name__ == "__main__":
    main()
