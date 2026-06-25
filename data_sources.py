"""
Fuentes de datos en vivo del ecosistema de pagos digitales e IA.

APIs públicas (sin clave): CoinGecko para mercado cripto/stablecoins.
Datos CBDC: referencia curada basada en seguimiento BIS / Atlantic Council.
"""

from __future__ import annotations

import json
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
        "stablecoins, tokens de depósito). El volumen de stablecoins supera los "
        "300.000 M$ y crece como capa de liquidación para software autónomo."
    ),
}


def _http_get_json(url: str, timeout: int = 15) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "AIPAY/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_crypto_market() -> dict[str, Any]:
    """Obtiene precios y capitalización desde CoinGecko."""
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

    return {
        "ok": True,
        "source": "CoinGecko",
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


def fetch_ecosystem_snapshot() -> dict[str, Any]:
    """Snapshot completo del ecosistema: mercado + CBDC + señales IA."""
    market = fetch_crypto_market()
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
            f"- Bitcoin: ${btc.get('price_usd', 'N/A'):,.0f} | "
            f"24h: {btc.get('change_24h_pct', 0):.1f}% | "
            f"7d: {btc.get('change_7d_pct', 0):.1f}%",
            f"- Stablecoins total: ~{stables.get('total_cap_b', 0)}B$ "
            f"(USDT {stables.get('usdt_cap_b')}B, USDC {stables.get('usdc_cap_b')}B)",
            f"- Mercado cripto global: ~{market.get('global_crypto_cap_b', 0)}B$",
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
    lines.extend([
        "### Pagos en ecosistema IA",
        f"- {ai['tendencia']}",
        "- Señales: " + "; ".join(ai["agentes_comerciales"][:4]),
    ])

    return "\n".join(lines)
