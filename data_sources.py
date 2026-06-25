"""
Fuentes de datos en vivo del ecosistema de pagos digitales e IA.

APIs públicas (sin clave): CoinGecko para mercado cripto/stablecoins.
Datos CBDC: referencia curada basada en seguimiento BIS / Atlantic Council.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin,tether,usd-coin,dai,ethena-usde"
    "&vs_currencies=usd"
    "&include_24hr_change=true"
    "&include_7d_change=true"
    "&include_market_cap=true"
)

COINGECKO_GLOBAL_URL = "https://api.coingecko.com/api/v3/global"
DEFAULT_MARKET_TTL_SECONDS = 300
_MARKET_CACHE: dict[str, Any] | None = None
_MARKET_CACHE_MONOTONIC: float = 0.0

# Referencia curada (actualizable) — pilotos CBDC en marcha / lanzados
CBDC_ECOSYSTEM = {
    "pilots_activos": 18,
    "paises_en_desarrollo": 134,
    "lanzados_retail": ["Bahamas", "Nigeria", "Jamaica", "China (e-CNY)"],
    "lanzados_wholesale": ["Brasil", "Singapur", "Corea del Sur"],
    "en_europa_piloto": ["España", "Francia", "Alemania", "Italia"],
    "fuente": "BIS / Atlantic Council CBDC Tracker (referencia 2025-2026)",
}

AI_PAYMENT_SIGNALS = {
    "agentes_comerciales": [
        "OpenAI API billing (tokens/créditos como unidad de pago)",
        "Anthropic Claude API (consumo por créditos)",
        "Stripe Agent / payment intents para agentes",
        "PayPal agentic commerce (2025)",
        "Coinbase x402 — pagos machine-to-machine en stablecoins",
    ],
    "tendencia": (
        "Los agentes de IA operan con unidades de cuenta digitales (créditos API, "
        "stablecoins, tokens de depósito). Las stablecoins crecen como capa de "
        "liquidación para software autónomo."
    ),
}


def safe_float(value: Any, default: float = 0.0) -> float:
    """Convierte a float; None o valores inválidos devuelven default."""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def fmt_price_usd(value: Any) -> str:
    if value is None:
        return "N/A"
    try:
        return f"${float(value):,.0f}"
    except (TypeError, ValueError):
        return "N/A"


def fmt_pct(value: Any) -> str:
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.1f}%"
    except (TypeError, ValueError):
        return "N/A"


def _http_get_json(url: str, timeout: int = 15) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "AiPay/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_crypto_market(
    use_cache: bool = True,
    ttl_seconds: int = DEFAULT_MARKET_TTL_SECONDS,
) -> dict[str, Any]:
    """Obtiene precios y capitalización desde CoinGecko."""
    global _MARKET_CACHE, _MARKET_CACHE_MONOTONIC

    now = time.monotonic()
    if (
        use_cache
        and _MARKET_CACHE is not None
        and now - _MARKET_CACHE_MONOTONIC < ttl_seconds
    ):
        cached = dict(_MARKET_CACHE)
        cached["cache"] = "hit"
        return cached

    try:
        prices = _http_get_json(COINGECKO_URL)
        global_data = _http_get_json(COINGECKO_GLOBAL_URL)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc), "source": "CoinGecko"}

    stable_ids = ("tether", "usd-coin", "dai", "ethena-usde")
    stable_caps = sum(
        prices[coin].get("usd_market_cap", 0) or 0
        for coin in stable_ids
        if coin in prices
    )

    market = {
        "ok": True,
        "source": "CoinGecko",
        "cache": "miss",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "bitcoin": {
            "price_usd": prices.get("bitcoin", {}).get("usd"),
            "change_24h_pct": prices.get("bitcoin", {}).get("usd_24h_change"),
            "change_7d_pct": prices.get("bitcoin", {}).get("usd_7d_change"),
            "market_cap_usd": prices.get("bitcoin", {}).get("usd_market_cap"),
        },
        "stablecoins": {
            "usdt_cap_b": round((prices.get("tether", {}).get("usd_market_cap") or 0) / 1e9, 1),
            "usdc_cap_b": round((prices.get("usd-coin", {}).get("usd_market_cap") or 0) / 1e9, 1),
            "dai_cap_b": round((prices.get("dai", {}).get("usd_market_cap") or 0) / 1e9, 1),
            "total_cap_b": round(stable_caps / 1e9, 1),
        },
        "global_crypto_cap_b": round(
            (global_data.get("data", {}).get("total_market_cap", {}).get("usd") or 0) / 1e9,
            1,
        ),
    }
    _MARKET_CACHE = dict(market)
    _MARKET_CACHE_MONOTONIC = now
    return market


def fetch_ecosystem_snapshot(use_cache: bool = True) -> dict[str, Any]:
    """Snapshot completo del ecosistema: mercado + CBDC + señales IA."""
    market = fetch_crypto_market(use_cache=use_cache)
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "market": market,
        "cbdc": CBDC_ECOSYSTEM,
        "ai_payments": AI_PAYMENT_SIGNALS,
    }


def format_snapshot_text(snapshot: dict[str, Any]) -> str:
    """Formatea el snapshot para el contexto del asistente GROQ."""
    lines = [f"## Datos en vivo del ecosistema ({snapshot['fetched_at'][:10]})"]

    market = snapshot.get("market", {})
    if market.get("ok"):
        btc = market["bitcoin"]
        stables = market["stablecoins"]
        lines.extend([
            "### Mercado cripto (CoinGecko)",
            f"- Bitcoin: {fmt_price_usd(btc.get('price_usd'))} | "
            f"24h: {fmt_pct(btc.get('change_24h_pct'))} | "
            f"7d: {fmt_pct(btc.get('change_7d_pct'))}",
            f"- Stablecoins total: ~{safe_float(stables.get('total_cap_b')):.1f}B$ "
            f"(USDT {safe_float(stables.get('usdt_cap_b')):.1f}B, "
            f"USDC {safe_float(stables.get('usdc_cap_b')):.1f}B)",
            f"- Mercado cripto global: ~{safe_float(market.get('global_crypto_cap_b')):.1f}B$",
        ])
    else:
        lines.append(f"### Mercado: no disponible ({market.get('error', 'error')})")

    cbdc = snapshot["cbdc"]
    lines.extend([
        "### CBDC (referencia)",
        f"- Países en desarrollo: {cbdc['paises_en_desarrollo']}",
        f"- Pilotos activos: {cbdc['pilots_activos']}",
        f"- Retail lanzado: {', '.join(cbdc['lanzados_retail'])}",
        f"- Europa en piloto: {', '.join(cbdc['en_europa_piloto'])}",
    ])

    ai = snapshot["ai_payments"]
    stablecoin_trend = ai["tendencia"]
    if market.get("ok"):
        stablecoin_trend = (
            "Los agentes de IA operan con unidades de cuenta digitales "
            "(créditos API, stablecoins, tokens de depósito). El volumen "
            f"medido de stablecoins ronda {safe_float(stables.get('total_cap_b')):.1f}B$ "
            "y funciona como capa de liquidación para software autónomo."
        )
    lines.extend([
        "### Pagos en ecosistema IA",
        f"- {stablecoin_trend}",
        "- Señales: " + "; ".join(ai["agentes_comerciales"][:4]),
    ])

    return "\n".join(lines)
