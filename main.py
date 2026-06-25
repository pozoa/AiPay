"""
Evaluación de medios de pago para el futuro de la IA.

Basado en el análisis de Víctor Alvargonzález (elEconomista): Bitcoin, CBDC,
Stablecoins y Tokens de depósito se puntúan según control político, estabilidad
financiera y compatibilidad con agentes de IA.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


CRITERIA = (
    "control_politico",
    "estabilidad_financiera",
    "compatibilidad_ia",
)

CRITERIA_LABELS = {
    "control_politico": "Control político",
    "estabilidad_financiera": "Estabilidad financiera",
    "compatibilidad_ia": "Compatibilidad con IA",
}


@dataclass(frozen=True)
class PaymentMethod:
    """Medio de pago evaluado."""

    id: str
    name: str
    description: str
    scores: dict[str, int]
    role: str

    def total_score(self) -> int:
        return sum(self.scores[criterion] for criterion in CRITERIA)


PAYMENT_METHODS: tuple[PaymentMethod, ...] = (
    PaymentMethod(
        id="bitcoin",
        name="Bitcoin",
        description=(
            "Criptomoneda descentralizada, independiente de bancos centrales. "
            "Alta volatilidad; mejor como reserva digital de valor que como "
            "moneda de intercambio global."
        ),
        scores={
            "control_politico": 2,
            "estabilidad_financiera": 2,
            "compatibilidad_ia": 8,
        },
        role="Reserva digital de valor",
    ),
    PaymentMethod(
        id="cbdc",
        name="CBDC",
        description=(
            "Moneda digital emitida por bancos centrales. Máximo control "
            "estatal, pero difícil de vender a la ciudadanía por el riesgo "
            "percibido de vigilancia financiera."
        ),
        scores={
            "control_politico": 10,
            "estabilidad_financiera": 9,
            "compatibilidad_ia": 8,
        },
        role="Instrumento de política monetaria",
    ),
    PaymentMethod(
        id="stablecoins",
        name="Stablecoins",
        description=(
            "Criptomonedas ancladas a activos estables (dólar, euro, letras "
            "del tesoro). Modelo híbrido: atractivo digital para la población "
            "y demanda de deuda pública para los gobiernos."
        ),
        scores={
            "control_politico": 6,
            "estabilidad_financiera": 8,
            "compatibilidad_ia": 9,
        },
        role="Medio de pago híbrido (candidato ganador)",
    ),
    PaymentMethod(
        id="deposit_tokens",
        name="Tokens de depósito",
        description=(
            "Tokens digitales respaldados por depósitos bancarios y de bancos "
            "centrales. Unidad de cuenta natural para agentes de IA y aceptable "
            "para el poder político."
        ),
        scores={
            "control_politico": 9,
            "estabilidad_financiera": 9,
            "compatibilidad_ia": 10,
        },
        role="Medio de pago híbrido (candidato ganador)",
    ),
)

EXPECTED_WINNERS = ("stablecoins", "deposit_tokens")

JUSTIFICATION = {
    "stablecoins": (
        "Los modelos híbridos están mejor situados: las stablecoins combinan "
        "digitalización y velocidad para la IA, estabilidad vía activo subyacente "
        "y un relato moderno para la población, además de reducir el coste de la "
        "deuda pública al generar demanda de letras del tesoro."
    ),
    "deposit_tokens": (
        "Los tokens respaldados por depósitos bancarios y de bancos centrales "
        "son la unidad de cuenta con la que ya operan los agentes de IA, ofrecen "
        "estabilidad y son aceptables para el poder político sin el rechazo social "
        "que provoca una CBDC pura."
    ),
    "bitcoin": (
        "Descartado como moneda de intercambio global por volatilidad extrema "
        "y por no depender de bancos centrales, algo que los políticos no aceptarán."
    ),
    "cbdc": (
        "Cumple el requisito de aceptación por bancos centrales, pero su adopción "
        "masiva es incierta por el control ciudadano que implica."
    ),
}


def get_payment_methods() -> list[PaymentMethod]:
    """Devuelve una copia de la lista de medios de pago."""
    return list(PAYMENT_METHODS)


def get_payment_method(method_id: str) -> PaymentMethod | None:
    """Busca un medio de pago por identificador."""
    for method in PAYMENT_METHODS:
        if method.id == method_id:
            return method
    return None


def rank_payment_methods(methods: Iterable[PaymentMethod] | None = None) -> list[PaymentMethod]:
    """Ordena medios de pago por puntuación total descendente."""
    items = list(methods) if methods is not None else list(PAYMENT_METHODS)
    return sorted(items, key=lambda method: method.total_score(), reverse=True)


def get_winners(methods: Iterable[PaymentMethod] | None = None) -> list[PaymentMethod]:
    """
    Determina los ganadores según el artículo: stablecoins y tokens de depósito.

    Se valida que ambos estén entre los dos primeros del ranking y que su
    puntuación sea al menos la del tercer clasificado.
    """
    ranking = rank_payment_methods(methods)
    winner_ids = {method.id for method in ranking if method.id in EXPECTED_WINNERS}
    if winner_ids != set(EXPECTED_WINNERS):
        return [method for method in ranking if method.id in EXPECTED_WINNERS]

    third_place_score = ranking[2].total_score() if len(ranking) > 2 else 0
    winners = [
        method
        for method in ranking
        if method.id in EXPECTED_WINNERS and method.total_score() >= third_place_score
    ]
    return winners


def build_evaluation_report() -> dict:
    """Genera un informe estructurado con ranking, ganadores y justificaciones."""
    ranking = rank_payment_methods()
    winners = get_winners()

    return {
        "criteria": CRITERIA_LABELS,
        "ranking": [
            {
                "id": method.id,
                "name": method.name,
                "role": method.role,
                "scores": method.scores,
                "total": method.total_score(),
                "justification": JUSTIFICATION[method.id],
            }
            for method in ranking
        ],
        "winners": [
            {
                "id": method.id,
                "name": method.name,
                "total": method.total_score(),
                "justification": JUSTIFICATION[method.id],
            }
            for method in winners
        ],
        "conclusion": (
            "El medio de pago del futuro en circuitos de agentes de IA será "
            "digital. Los modelos híbridos —stablecoins y tokens de depósito— "
            "equilibran compatibilidad tecnológica, estabilidad y aceptación "
            "política. Bitcoin permanece como reserva de valor; la CBDC como "
            "herramienta estatal con adopción social limitada."
        ),
    }


def format_report_text() -> str:
    """Formatea el informe como texto legible para consola o asistente."""
    report = build_evaluation_report()
    lines = [
        "=== Evaluación de medios de pago para la era de la IA ===",
        "",
        "Criterios:",
    ]

    for key, label in report["criteria"].items():
        lines.append(f"  - {label} ({key})")

    lines.extend(["", "Ranking:"])
    for index, item in enumerate(report["ranking"], start=1):
        lines.append(
            f"  {index}. {item['name']} — {item['total']} pts — {item['role']}"
        )
        for criterion, score in item["scores"].items():
            lines.append(f"     · {report['criteria'][criterion]}: {score}/10")
        lines.append(f"     · {item['justification']}")

    lines.extend(["", "Ganadores (modelos híbridos):"])
    for winner in report["winners"]:
        lines.append(f"  • {winner['name']} ({winner['total']} pts)")
        lines.append(f"    {winner['justification']}")

    lines.extend(["", report["conclusion"]])
    return "\n".join(lines)


def main() -> None:
    """Punto de entrada por línea de comandos."""
    print(format_report_text())


if __name__ == "__main__":
    main()
