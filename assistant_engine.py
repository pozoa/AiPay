"""
Motor dinámico del asistente: detecta intención, construye contexto y responde.
"""

from __future__ import annotations

import re

from main import (
    CRITERIA_LABELS,
    JUSTIFICATION,
    build_evaluation_report,
    get_payment_method,
    get_winners,
    rank_payment_methods,
)

PRODUCT_ALIASES: dict[str, str] = {
    "bitcoin": "bitcoin",
    "btc": "bitcoin",
    "cbdc": "cbdc",
    "moneda digital": "cbdc",
    "banco central": "cbdc",
    "stablecoin": "stablecoins",
    "stablecoins": "stablecoins",
    "stable coin": "stablecoins",
    "token de depósito": "deposit_tokens",
    "tokens de depósito": "deposit_tokens",
    "token de deposito": "deposit_tokens",
    "tokens de deposito": "deposit_tokens",
    "deposit token": "deposit_tokens",
    "deposit tokens": "deposit_tokens",
}

INTENT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("ranking", re.compile(r"\b(ranking|clasificación|orden|puntuación|puntos|quién gana)\b", re.I)),
    ("compare", re.compile(r"\b(compar|diferenc|vs|versus|frente a|mejor que)\b", re.I)),
    ("winner", re.compile(r"\b(ganador|ganan|futuro|recomend|invertir|benefici)\b", re.I)),
    ("bitcoin", re.compile(r"\b(bitcoin|btc)\b", re.I)),
    ("cbdc", re.compile(r"\b(cbdc|banco central|moneda digital)\b", re.I)),
    ("stablecoins", re.compile(r"\b(stablecoin)\b", re.I)),
    ("deposit_tokens", re.compile(r"\b(token.*dep[oó]sito|deposit token)\b", re.I)),
    ("criteria", re.compile(r"\b(criterio|control político|estabilidad|compatibilidad|ia)\b", re.I)),
]


def detect_product_ids(text: str) -> list[str]:
    """Detecta productos mencionados en la pregunta."""
    lowered = text.lower()
    found: list[str] = []

    for alias, product_id in PRODUCT_ALIASES.items():
        if alias in lowered and product_id not in found:
            found.append(product_id)

    for intent_id, pattern in INTENT_PATTERNS[3:6]:
        if pattern.search(text) and intent_id not in found:
            found.append(intent_id)

    return found


def detect_intents(text: str) -> list[str]:
    intents: list[str] = []
    for intent_id, pattern in INTENT_PATTERNS:
        if pattern.search(text):
            intents.append(intent_id)
    return intents or ["general"]


def format_method_detail(method_id: str) -> str:
    method = get_payment_method(method_id)
    if method is None:
        return ""
    lines = [
        f"## {method.name}",
        f"Rol: {method.role}",
        f"Descripción: {method.description}",
        f"Puntuación total: {method.total_score()}/30",
    ]
    for criterion, score in method.scores.items():
        lines.append(f"- {CRITERIA_LABELS[criterion]}: {score}/10")
    lines.append(f"Análisis: {JUSTIFICATION[method_id]}")
    return "\n".join(lines)


def format_comparison(method_ids: list[str]) -> str:
    if len(method_ids) < 2:
        return ""
    lines = ["## Comparativa directa"]
    for method_id in method_ids[:4]:
        method = get_payment_method(method_id)
        if method:
            lines.append(
                f"- {method.name}: total {method.total_score()} | "
                + ", ".join(f"{CRITERIA_LABELS[k]} {v}" for k, v in method.scores.items())
            )
    return "\n".join(lines)


def build_dynamic_context(user_message: str, history: list[dict[str, str]]) -> str:
    """Construye contexto relevante según la pregunta, no el informe completo."""
    intents = detect_intents(user_message)
    products = detect_product_ids(user_message)

    # Si es seguimiento ("¿y el bitcoin?"), mirar historial reciente
    if not products and history:
        for msg in reversed(history[-4:]):
            if msg["role"] == "user":
                products = detect_product_ids(msg["content"])
                if products:
                    break

    sections: list[str] = [
        "Marco analítico AiPay (referencia: elEconomista — Víctor Alvargonzález). "
        "El proyecto evalúa de forma independiente con datos en vivo."
    ]

    if "ranking" in intents or "winner" in intents or not products:
        ranking = rank_payment_methods()
        sections.append("## Ranking actual")
        for i, method in enumerate(ranking, 1):
            sections.append(f"{i}. {method.name} — {method.total_score()} pts")

        winners = get_winners()
        sections.append(
            "## Ganadores estratégicos: "
            + ", ".join(w.name for w in winners)
        )

    if products:
        for product_id in products:
            detail = format_method_detail(product_id)
            if detail:
                sections.append(detail)

    if "compare" in intents and len(products) >= 2:
        sections.append(format_comparison(products))

    if "criteria" in intents:
        sections.append("## Criterios de evaluación (0-10 cada uno)")
        for key, label in CRITERIA_LABELS.items():
            sections.append(f"- {label} ({key})")

    if "winner" in intents:
        report = build_evaluation_report()
        sections.append(f"## Conclusión del modelo\n{report['conclusion']}")

    return "\n\n".join(sections)


def local_fallback_answer(user_message: str) -> str | None:
    """Respuesta local si GROQ no está disponible."""
    products = detect_product_ids(user_message)
    intents = detect_intents(user_message)

    if "ranking" in intents:
        lines = ["**Ranking de medios de pago:**\n"]
        for i, method in enumerate(rank_payment_methods(), 1):
            lines.append(f"{i}. **{method.name}** — {method.total_score()} pts")
        return "\n".join(lines)

    if products and len(products) == 1:
        return format_method_detail(products[0])

    if "compare" in intents and len(products) >= 2:
        return format_comparison(products) + "\n\n" + "\n\n".join(
            format_method_detail(pid) for pid in products[:2]
        )

    if "winner" in intents:
        winners = get_winners()
        return (
            "Los **ganadores estratégicos** del análisis son: "
            + " y ".join(f"**{w.name}** ({w.total_score()} pts)" for w in winners)
            + ".\n\n"
            + JUSTIFICATION["stablecoins"]
            + "\n\n"
            + JUSTIFICATION["deposit_tokens"]
        )

    return None


def products_for_display(user_message: str, history: list[dict[str, str]]) -> list[str]:
    """Productos a mostrar visualmente tras una respuesta."""
    products = detect_product_ids(user_message)
    if not products and history:
        for msg in reversed(history[-4:]):
            products = detect_product_ids(msg.get("content", ""))
            if products:
                break
    return products[:2]
