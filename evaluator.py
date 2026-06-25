"""
Evaluador dinámico del ecosistema de pagos para agentes de IA.

Combina el marco analítico del artículo (elEconomista) con datos en vivo
de APIs para generar puntuaciones y ranking actualizados.
"""

from __future__ import annotations

import copy
from typing import Any

from data_sources import fetch_ecosystem_snapshot, format_snapshot_text
from main import (
    CRITERIA,
    CRITERIA_LABELS,
    EXPECTED_WINNERS,
    JUSTIFICATION,
    PAYMENT_METHODS,
    PaymentMethod,
    get_winners,
    rank_payment_methods,
)


def _clamp(value: float, low: int = 0, high: int = 10) -> int:
    return max(low, min(high, round(value)))


def _adjust_scores_from_market(
    base_scores: dict[str, int],
    method_id: str,
    snapshot: dict[str, Any],
) -> dict[str, int]:
    """Ajusta puntuaciones base con datos de mercado en vivo."""
    scores = copy.deepcopy(base_scores)
    market = snapshot.get("market", {})

    if not market.get("ok"):
        return scores

    if method_id == "bitcoin":
        change_7d = abs(market["bitcoin"].get("change_7d_pct") or 0)
        if change_7d > 10:
            scores["estabilidad_financiera"] = _clamp(scores["estabilidad_financiera"] - 2)
        elif change_7d > 5:
            scores["estabilidad_financiera"] = _clamp(scores["estabilidad_financiera"] - 1)

    if method_id == "stablecoins":
        total_cap = market["stablecoins"].get("total_cap_b", 0)
        if total_cap > 200:
            scores["compatibilidad_ia"] = _clamp(scores["compatibilidad_ia"] + 1)
            scores["estabilidad_financiera"] = _clamp(scores["estabilidad_financiera"] + 1)
        elif total_cap > 100:
            scores["compatibilidad_ia"] = _clamp(scores["compatibilidad_ia"] + 1)

    if method_id == "cbdc":
        pilots = snapshot["cbdc"].get("pilots_activos", 0)
        if pilots >= 15:
            scores["control_politico"] = _clamp(scores["control_politico"])
            scores["compatibilidad_ia"] = _clamp(scores["compatibilidad_ia"] + 1)

    if method_id == "deposit_tokens":
        scores["compatibilidad_ia"] = _clamp(scores["compatibilidad_ia"] + 0)
        # Señal IA: si stablecoins crecen, tokens de depósito compiten en misma capa
        if market["stablecoins"].get("total_cap_b", 0) > 150:
            scores["compatibilidad_ia"] = 10

    return scores


def build_live_methods(snapshot: dict[str, Any] | None = None) -> list[PaymentMethod]:
    """Genera medios de pago con puntuación ajustada a datos en vivo."""
    if snapshot is None:
        snapshot = fetch_ecosystem_snapshot()

    methods: list[PaymentMethod] = []
    for base in PAYMENT_METHODS:
        adjusted = _adjust_scores_from_market(base.scores, base.id, snapshot)
        methods.append(
            PaymentMethod(
                id=base.id,
                name=base.name,
                description=base.description,
                scores=adjusted,
                role=base.role,
            )
        )
    return methods


def run_ecosystem_evaluation(snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Ejecuta evaluación completa del ecosistema.
    Devuelve informe con datos en vivo, ranking y ganadores.
    """
    if snapshot is None:
        snapshot = fetch_ecosystem_snapshot()

    methods = build_live_methods(snapshot)
    ranking = rank_payment_methods(methods)
    winners = get_winners(methods)

    return {
        "mode": "agent_evaluation",
        "fetched_at": snapshot["fetched_at"],
        "live_data": snapshot,
        "live_data_text": format_snapshot_text(snapshot),
        "criteria": CRITERIA_LABELS,
        "ranking": [
            {
                "id": m.id,
                "name": m.name,
                "role": m.role,
                "scores": m.scores,
                "total": m.total_score(),
                "justification": JUSTIFICATION[m.id],
            }
            for m in ranking
        ],
        "winners": [
            {
                "id": m.id,
                "name": m.name,
                "total": m.total_score(),
                "justification": JUSTIFICATION[m.id],
            }
            for m in winners
        ],
        "conclusion": (
            "Evaluación en vivo del ecosistema de pagos para agentes de IA. "
            "Los datos de mercado (CoinGecko) y el avance CBDC se combinan con "
            "el marco analítico del artículo de elEconomista. Los modelos híbridos "
            "(stablecoins y tokens de depósito) lideran la adopción práctica entre "
            "agentes autónomos, mientras Bitcoin actúa como reserva de valor y "
            "las CBDC avanzan vía pilotos estatales."
        ),
        "sources": [
            snapshot["market"].get("source", "CoinGecko"),
            snapshot["cbdc"].get("fuente", "BIS/CBDC Tracker"),
            "Marco analítico: Víctor Alvargonzález (elEconomista)",
        ],
    }
