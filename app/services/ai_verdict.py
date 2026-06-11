"""Plain-language verdict + synthesis for daily briefing picks."""

import json
from typing import Any

import httpx

from app.config import settings


def _template_verdict(pick: dict[str, Any]) -> dict[str, str]:
    name = pick["name"]
    tagline = pick.get("tagline") or pick.get("summary", "")

    if pick.get("pick_kind") == "investor":
        stage = pick.get("stage") or "—"
        sector = pick.get("sector") or "General"
        check = pick.get("estimated_raise") or "flexible check"
        verdict = "Worth meeting"
        synthesis = (
            f"{name} ({pick.get('tagline', 'Investor')}) focuses on {stage} in {sector}. "
            f"Typical check: {check}. {tagline}. "
            "Scan their portfolio overlap with your thesis before reaching out."
        )
    else:
        sector = pick.get("sector") or "Startup"
        stage = pick.get("stage") or "—"
        verdict = "Worth watching"
        synthesis = (
            f"{name} is a {stage} {sector} on startups.gallery. {tagline}. "
            "Useful signal for who is raising at scale — cross-check against your pipeline."
        )
    return {"verdict": verdict, "synthesis": synthesis.strip()}


def _openai_verdict(pick: dict[str, Any]) -> dict[str, str]:
    kind = pick.get("pick_kind") or "company"
    if kind == "investor":
        prompt = f"""You are an angel investor analyst writing a daily briefing line about a VC/investor profile.

Investor: {pick['name']}
Type: {pick.get('tagline')}
Sector focus: {pick.get('sector')}
Stages: {pick.get('stage')}
Check size: {pick.get('estimated_raise') or 'n/a'}
Locations: {pick.get('locations') or 'n/a'}
Notes: {pick.get('summary') or 'n/a'}
Source: {pick.get('source')}

Respond with JSON only: {{"verdict": "Worth meeting"|"Monitor"|"Pass", "synthesis": "2-3 sentences, plain language. No bullet lists."}}"""
    else:
        prompt = f"""You are an angel investor analyst writing a daily briefing line about a startup listing.

Company: {pick['name']}
Description: {pick.get('tagline') or pick.get('summary')}
Stage: {pick.get('stage')}
Source: {pick.get('source')}

Respond with JSON only: {{"verdict": "Worth watching"|"Early signal"|"Monitor"|"Pass", "synthesis": "2-3 sentences, plain language. No bullet lists."}}"""

    with httpx.Client(timeout=45) as client:
        response = client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key.strip()}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.openai_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You write concise investor briefings. Output valid JSON only.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.4,
                "max_tokens": 220,
            },
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        data = json.loads(content)
        return {
            "verdict": str(data.get("verdict", "Monitor")),
            "synthesis": str(data.get("synthesis", "")).strip(),
        }


def generate_signal_verdict(pick: dict[str, Any]) -> dict[str, str]:
    if settings.openai_api_key.strip():
        try:
            return _openai_verdict(pick)
        except Exception:
            pass
    return _template_verdict(pick)
