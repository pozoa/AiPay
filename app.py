"""
AiPay — Interfaz única: asistente y agente de pagos en el ecosistema IA.

Una sola pantalla de chat. El agente ejecuta evaluaciones en vivo (APIs)
y muestra resultados dinámicamente dentro de la conversación.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from agent import AgentResponse, process_message
from data_sources import fmt_pct, fmt_price_usd, safe_float
from main import CRITERIA_LABELS

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def get_branch_name() -> str:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def get_app_name() -> str:
    branch = get_branch_name()
    if branch == "dev-cursor":
        return "AiPay Cursor"
    if branch == "main":
        return "AiPay Pozoa"
    if branch in {"dev-codex", "dev-code"}:
        return "AiPay Codex"
    if branch == "dev-kiro":
        return "AiPay Kiro"
    return "AiPay"


def init_session() -> None:
    defaults = {
        "messages": [],
        "last_evaluation": None,
        "last_snapshot": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_evaluation_panel(evaluation: dict) -> None:
    """Panel dinámico de evaluación embebido en el chat."""
    st.markdown("#### Evaluación en vivo")

    market = evaluation.get("live_data", {}).get("market", {})
    if market.get("ok"):
        c1, c2, c3 = st.columns(3)
        btc = market["bitcoin"]
        stables = market["stablecoins"]
        c1.metric(
            "Bitcoin",
            fmt_price_usd(btc.get("price_usd")),
            fmt_pct(btc.get("change_24h_pct")),
        )
        c2.metric(
            "Stablecoins",
            f"{safe_float(stables.get('total_cap_b')):.1f}B$",
            "cap. total",
        )
        c3.metric(
            "Mercado cripto",
            f"{safe_float(market.get('global_crypto_cap_b')):.1f}B$",
            "global",
        )

    st.markdown("**Ranking actualizado**")
    for i, item in enumerate(evaluation["ranking"], 1):
        badge = " 🏆" if any(w["id"] == item["id"] for w in evaluation["winners"]) else ""
        with st.expander(f"{i}. {item['name']} — {item['total']} pts{badge}"):
            for criterion, score in item["scores"].items():
                st.progress(score / 10, text=f"{CRITERIA_LABELS[criterion]}: {score}/10")
            st.caption(item["justification"])

    sources = evaluation.get("sources", [])
    if sources:
        st.caption("Fuentes: " + " · ".join(sources))


def render_market_snapshot(snapshot: dict) -> None:
    """Mini panel de mercado para respuestas de asistente."""
    market = snapshot.get("market", {})
    if not market.get("ok"):
        return
    btc = market["bitcoin"]
    stables = market["stablecoins"]
    c1, c2 = st.columns(2)
    c1.caption(f"BTC {fmt_price_usd(btc.get('price_usd'))} ({fmt_pct(btc.get('change_7d_pct'))} 7d)")
    c2.caption(f"Stablecoins ~{safe_float(stables.get('total_cap_b')):.1f}B$")


def handle_message(prompt: str) -> None:
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
        if m["role"] in ("user", "assistant")
    ]

    with st.spinner("Consultando ecosistema y APIs..."):
        response: AgentResponse = process_message(
            prompt, history, GROQ_API_KEY, GROQ_MODEL
        )

    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
    })
    st.session_state.messages.append({
        "role": "assistant",
        "content": response.text,
        "mode": response.mode,
        "evaluation": response.evaluation,
        "snapshot": response.snapshot,
        "product_ids": response.product_ids,
    })

    if response.evaluation:
        st.session_state.last_evaluation = response.evaluation
    if response.snapshot:
        st.session_state.last_snapshot = response.snapshot


def render_chat() -> None:
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            if msg["role"] == "assistant":
                mode = msg.get("mode", "assistant")
                if mode == "agent":
                    st.caption("Modo agente · evaluación en vivo")
                if msg.get("evaluation"):
                    render_evaluation_panel(msg["evaluation"])
                elif msg.get("snapshot"):
                    render_market_snapshot(msg["snapshot"])

    actions = st.columns([1, 1, 1, 2])
    if actions[0].button("Evaluar ecosistema", use_container_width=True):
        handle_message("Evalúa el ecosistema actual de pagos para agentes de IA con datos en vivo")
        st.rerun()

    if actions[1].button("Mercado stablecoins", use_container_width=True):
        handle_message("¿Cuál es la situación actual de las stablecoins en el mercado?")
        st.rerun()

    if actions[2].button("Estado CBDC", use_container_width=True):
        handle_message("¿Qué está pasando ahora con las CBDC en el mundo?")
        st.rerun()

    prompt = st.chat_input("Pregunta sobre pagos en el ecosistema de agentes IA...")
    if prompt:
        handle_message(prompt)
        st.rerun()


def render_sidebar() -> None:
    app_name = get_app_name()
    with st.sidebar:
        st.header(app_name)
        st.caption("Asistente → Agente")
        st.markdown(
            "**Fase actual:** Asistente con evaluación agente\n\n"
            "Pide *«evalúa el ecosistema»* para activar el modo agente."
        )

        if st.session_state.last_evaluation:
            st.divider()
            st.markdown("**Última evaluación**")
            for i, item in enumerate(st.session_state.last_evaluation["ranking"][:3], 1):
                st.write(f"{i}. {item['name']} — {item['total']} pts")

        st.divider()
        st.caption("APIs: CoinGecko · CBDC Tracker")
        st.caption("Marco: elEconomista (V. Alvargonzález)")


def main() -> None:
    app_name = get_app_name()
    st.set_page_config(
        page_title=f"{app_name} — Pagos en el ecosistema IA",
        page_icon="💳",
        layout="wide",
    )
    init_session()
    render_sidebar()

    st.title(app_name)
    branch = get_branch_name()
    if branch:
        st.caption(f"🌿 rama: `{branch}`")
    st.markdown(
        "Asistente y **agente** de la economía de pagos en el ecosistema de **agentes de IA**. "
        "Consulta datos en vivo, analiza y evalúa — todo en una sola conversación."
    )

    if not GROQ_API_KEY:
        st.warning("Añade `GROQ_API_KEY` en `.env` para respuestas con IA. Sin clave, hay informes locales.")
    else:
        st.caption(f"GROQ `{GROQ_MODEL}` · datos CoinGecko en tiempo real")

    if not st.session_state.messages:
        st.info(
            "Prueba: *«¿Cómo pagan hoy los agentes de IA?»*, "
            "*«Evalúa el ecosistema con datos en vivo»* o usa los botones de acción rápida."
        )

    render_chat()

    if st.session_state.messages:
        if st.button("Nueva conversación"):
            st.session_state.messages = []
            st.session_state.last_evaluation = None
            st.session_state.last_snapshot = None
            st.rerun()


if __name__ == "__main__":
    main()
