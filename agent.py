"""
Agente AiPay: orquesta asistente conversacional y evaluación del ecosistema.

Fase 1 — Asistente: responde con contexto dinámico + datos en vivo.
Fase 2 — Agente: ejecuta evaluación completa (APIs + scoring) y sintetiza con GROQ.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any

from assistant_engine import (
    build_dynamic_context,
    detect_intents,
    detect_product_ids,
    local_fallback_answer,
    products_for_display,
)
from data_sources import fetch_ecosystem_snapshot, format_snapshot_text
from evaluator import run_ecosystem_evaluation

AGENT_TRIGGERS = re.compile(
    r"\b("
    r"eval[uú]a|evaluar|anali[sz]a|analizar|ecosistema|"
    r"datos en vivo|mercado actual|agente|informe completo|"
    r"actualiza.*ranking|qué pasa ahora|situación actual"
    r")\b",
    re.I,
)

SYSTEM_ASSISTANT = """Eres AiPay, asistente especializado en la economía de pagos
del ecosistema de agentes de IA (2025-2026).

MISIÓN: analizar cómo se están pagando hoy las transacciones entre agentes de IA,
APIs comerciales y software autónomo — no solo teoría del artículo de elEconomista.

PRODUCTOS: Bitcoin, CBDC, Stablecoins, Tokens de depósito.
CRITERIOS: control político, estabilidad financiera, compatibilidad con IA.

REGLAS:
1. Usa los DATOS EN VIVO del contexto (CoinGecko, CBDC, señales IA).
2. Responde a la pregunta concreta; no repitas siempre la misma conclusión.
3. Cita cifras reales cuando estén en el contexto (precio BTC, cap. stablecoins…).
4. El artículo de elEconomista es marco de referencia, no la única fuente.
5. Español, tono de analista. Máx. 250 palabras salvo que pidan informe."""

SYSTEM_AGENT = """Eres AiPay en modo AGENTE. Acabas de ejecutar una evaluación en vivo
del ecosistema de pagos para agentes de IA.

Tu tarea: presentar el informe de forma clara y accionable para un inversor o analista.
Incluye:
- Situación actual del mercado (datos CoinGecko si disponibles)
- Ranking actualizado con puntuaciones
- Ganadores estratégicos y por qué
- Implicaciones para el ecosistema de agentes IA
- 1-2 ideas de sectores o empresas que podrían beneficiarse

No hables del código. Español, estructurado con subtítulos breves."""


@dataclass
class AgentResponse:
    """Respuesta unificada del agente para la interfaz."""

    text: str
    mode: str  # "assistant" | "agent"
    evaluation: dict[str, Any] | None = None
    product_ids: list[str] = field(default_factory=list)
    snapshot: dict[str, Any] | None = None


def _should_run_full_evaluation(message: str) -> bool:
    return bool(AGENT_TRIGGERS.search(message))


def _call_groq(
    system: str,
    user_content: str,
    history: list[dict[str, str]],
    api_key: str,
    model: str,
) -> str:
    from groq import Groq

    messages: list[dict[str, str]] = [{"role": "system", "content": system}]
    for msg in history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_content})

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.35,
        max_tokens=1200,
    )
    return response.choices[0].message.content or "Sin respuesta."


def process_message(
    message: str,
    history: list[dict[str, str]],
    groq_api_key: str = "",
    groq_model: str = "llama-3.1-8b-instant",
) -> AgentResponse:
    """
    Procesa un mensaje del usuario.
    Modo agente si pide evaluación/ecosistema; si no, modo asistente.
    """
    snapshot = fetch_ecosystem_snapshot()
    product_ids = products_for_display(message, history)

    # ── Modo AGENTE: evaluación completa ──
    if _should_run_full_evaluation(message):
        evaluation = run_ecosystem_evaluation(snapshot)

        if groq_api_key:
            try:
                context = (
                    f"{evaluation['live_data_text']}\n\n"
                    f"## Ranking evaluado\n"
                    + "\n".join(
                        f"{i}. {r['name']} — {r['total']} pts"
                        for i, r in enumerate(evaluation["ranking"], 1)
                    )
                    + f"\n\nGanadores: {', '.join(w['name'] for w in evaluation['winners'])}"
                )
                text = _call_groq(
                    SYSTEM_AGENT,
                    f"{context}\n\nPetición del usuario: {message}",
                    history,
                    groq_api_key,
                    groq_model,
                )
            except Exception as exc:
                text = _format_evaluation_fallback(evaluation) + f"\n\n_(GROQ: {exc})_"
        else:
            text = _format_evaluation_fallback(evaluation)

        return AgentResponse(
            text=text,
            mode="agent",
            evaluation=evaluation,
            product_ids=[r["id"] for r in evaluation["ranking"][:2]],
            snapshot=snapshot,
        )

    # ── Modo ASISTENTE: chat con datos en vivo ──
    live_context = format_snapshot_text(snapshot)
    article_context = build_dynamic_context(message, history)
    full_context = f"{live_context}\n\n{article_context}"

    if groq_api_key:
        try:
            text = _call_groq(
                SYSTEM_ASSISTANT,
                f"[Contexto]\n{full_context}\n\n[Pregunta]\n{message}",
                history,
                groq_api_key,
                groq_model,
            )
        except Exception as exc:
            fallback = local_fallback_answer(message)
            text = (fallback or "No pude procesar la consulta.") + f"\n\n_(GROQ: {exc})_"
    else:
        fallback = local_fallback_answer(message)
        text = fallback or (
            "Configura GROQ_API_KEY en `.env` para respuestas con IA.\n\n"
            + live_context
        )

    return AgentResponse(
        text=text,
        mode="assistant",
        product_ids=product_ids,
        snapshot=snapshot,
    )


def _format_evaluation_fallback(evaluation: dict[str, Any]) -> str:
    """Informe textual si GROQ no está disponible."""
    lines = [
        "## Evaluación del ecosistema de pagos IA",
        "",
        evaluation["live_data_text"],
        "",
        "### Ranking",
    ]
    for i, item in enumerate(evaluation["ranking"], 1):
        lines.append(f"{i}. **{item['name']}** — {item['total']} pts")
    lines.extend(["", "### Ganadores estratégicos"])
    for w in evaluation["winners"]:
        lines.append(f"- **{w['name']}**: {w['justification']}")
    lines.extend(["", evaluation["conclusion"]])
    return "\n".join(lines)
