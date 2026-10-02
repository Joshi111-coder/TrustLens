import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests

from app.config import settings
from app.services.risk_engine import analyze_rules
from app.services.knowledge_service import knowledge_base
from app.services.language_service import translate_analysis_findings, get_language_info

AI_SYSTEM_PROMPT = """You are TrustLens, an AI financial content risk-awareness assistant for first-time investors.
Your task is to analyze financial messages, investment offers, or social media posts and provide an objective, educational risk evaluation.

CRITICAL SAFETY & POSITIONING RULES:
1. You are an EDUCATIONAL RISK-AWARENESS TOOL, NOT a financial advisor and NOT a scam detective.
2. NEVER give personalized investment advice (NO "Buy", "Sell", "Hold", "Invest ₹X", "Good for you", "Stock will rise").
3. NEVER use definitive or binary labels like "100% scam", "fraud", or "100% safe".
4. Use ONLY these risk categories: "LOW RISK", "NEEDS VERIFICATION", "HIGH RISK".
5. Use neutral safety language:
   - Say "Verify the claim using the official SEBI website before taking any financial action."
   - DO NOT say "Do not invest in this company."
   - Say "The message contains a guaranteed-return claim that warrants additional verification."
   - DO NOT say "This investment is definitely a scam."
6. Explain why patterns deserve attention and what information can be independently verified.
7. Return strictly valid JSON without markdown wrapping.
"""

def call_gemini_api(text: str) -> Optional[Dict[str, Any]]:
    """Calls Google Gemini API for structured content analysis."""
    if not settings.has_gemini:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    prompt_payload = (
        f"{AI_SYSTEM_PROMPT}\n\n"
        f"Analyze this financial message:\n---\n{text}\n---\n"
        "Return a JSON object with: risk_level, risk_score (0-100), summary, red_flags, claims, why_flagged, action_dos, action_donts."
    )

    body = {
        "contents": [{"parts": [{"text": prompt_payload}]}],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }

    try:
        response = requests.post(url, json=body, timeout=12)
        if response.status_code == 200:
            data = response.json()
            raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(raw_json)
        else:
            print(f"[AIService] Gemini API error: status {response.status_code}, {response.text}")
    except Exception as e:
        print(f"[AIService] Gemini API call exception: {e}")

    return None

def call_openai_api(text: str) -> Optional[Dict[str, Any]]:
    """Calls OpenAI-compatible API for structured analysis."""
    if not settings.has_openai:
        return None

    url = f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": settings.OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": AI_SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyze this financial message:\n\n---\n{text}\n---"}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(url, headers=headers, json=body, timeout=12)
        if response.status_code == 200:
            data = response.json()
            raw_json = data["choices"][0]["message"]["content"]
            return json.loads(raw_json)
        else:
            print(f"[AIService] OpenAI API error: status {response.status_code}, {response.text}")
    except Exception as e:
        print(f"[AIService] OpenAI API call exception: {e}")

    return None

def analyze_financial_content(text: str, language: str = "en") -> Dict[str, Any]:
    """
    Core Architecture Pipeline:
    1. Language-independent risk analysis via deterministic 10-rule risk engine.
    2. Optional supplementary AI interpretation (score fused with deterministic weights).
    3. Official trusted sources knowledge base matching.
    4. Multilingual explanation service generates user-facing text in the selected Indian language.
    """
    analysis_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()

    # Step 1: Run deterministic rule-based engine (language-neutral)
    rule_results = analyze_rules(text)

    # Step 2: Try AI provider if configured
    ai_result = None
    if settings.AI_PROVIDER == "openai" and settings.has_openai:
        ai_result = call_openai_api(text)
    elif settings.has_gemini:
        ai_result = call_gemini_api(text)
    elif settings.has_openai:
        ai_result = call_openai_api(text)

    # Step 3: Query Knowledge Base for matched official references
    matched_sources = knowledge_base.search(
        query=text,
        limit=4,
        keywords=rule_results.get("detected_keywords", [])
    )

    trusted_sources_formatted = [
        {
            "name": s.get("name", "Regulatory Advisory"),
            "topic": s.get("topic", "Financial Protection"),
            "verification_status": s.get("verification_status", "OFFICIAL GUIDELINE"),
            "url": s.get("url"),
            "summary": s.get("summary"),
            "advice": s.get("advice")
        }
        for s in matched_sources
    ]

    # Step 4: Blend Rule Engine + AI results
    if ai_result:
        ai_score = int(ai_result.get("risk_score", rule_results["score"]))
        # Rule engine holds heavy weight (60%) to preserve deterministic bounds
        fused_score = int(0.60 * rule_results["score"] + 0.40 * ai_score)
        fused_score = min(100, max(0, fused_score))

        if fused_score >= 60:
            final_level = "HIGH RISK"
        elif fused_score >= 30:
            final_level = "NEEDS VERIFICATION"
        else:
            final_level = "LOW RISK"

        combined_flags = list(rule_results["red_flags"])
        existing_rule_ids = {f.get("rule_id") for f in combined_flags}
        
        # Add supplementary AI flags if not duplicate
        for flag in ai_result.get("red_flags", []):
            flag_title = flag.get("title", "")
            if not any(f["title"].lower() == flag_title.lower() for f in combined_flags):
                r_id = flag.get("rule_id", f"RF_AI_{len(combined_flags)+1}")
                combined_flags.append({
                    "rule_id": r_id,
                    "title": flag_title,
                    "severity": flag.get("severity", "MEDIUM"),
                    "matched_text": flag.get("matched_text", ""),
                    "explanation": flag.get("explanation", ""),
                    "verification_action": flag.get("verification_action", "Verify through official regulatory channels."),
                    "icon": flag.get("icon", "AlertTriangle")
                })

        combined_claims = list(rule_results["claims"])
        existing_claims = {c["claim"].lower() for c in combined_claims}
        for c in ai_result.get("claims", []):
            if c.get("claim", "").lower() not in existing_claims:
                combined_claims.append(c)

        combined_why = list(rule_results["why_flagged"])
        if not combined_why and ai_result.get("why_flagged"):
            combined_why = ai_result.get("why_flagged")

        summary = ai_result.get("summary") or rule_results["summary"]
        dos = ai_result.get("action_dos") or rule_results["action_dos"]
        donts = ai_result.get("action_donts") or rule_results["action_donts"]
        recommended_actions = dos[:3] + donts[:2]

    else:
        # High quality heuristic baseline
        fused_score = rule_results["score"]
        final_level = rule_results["risk_level"]
        summary = rule_results["summary"]
        combined_flags = rule_results["red_flags"]
        combined_claims = rule_results["claims"]
        combined_why = rule_results["why_flagged"]
        dos = rule_results["action_dos"]
        donts = rule_results["action_donts"]
        recommended_actions = dos[:3] + donts[:2]

    if not combined_why:
        combined_why = [
            {"step_number": "01", "title": "Content scanning completed", "description": "Processed text across regulatory security heuristics."},
            {"step_number": "02", "title": "Pattern recognition", "description": "Evaluated return promises, urgency, and regulatory claims."},
            {"step_number": "03", "title": "Regulatory cross-reference", "description": "Checked against official SEBI and RBI investor advisories."}
        ]

    if not combined_claims:
        combined_claims.append({
            "claim": "General investment representation",
            "status": "NEEDS VERIFICATION",
            "explanation": "Verify any financial product or recommendation through official regulatory registries before investing.",
            "source": "SEBI Investor Education",
            "source_url": "https://investor.sebi.gov.in"
        })

    structured_analysis = {
        "id": analysis_id,
        "risk_level": final_level,
        "risk_score": fused_score,
        "summary": summary,
        "red_flags": combined_flags,
        "claims": combined_claims,
        "recommended_actions": recommended_actions,
        "action_dos": dos,
        "action_donts": donts,
        "why_flagged": combined_why,
        "trusted_sources": trusted_sources_formatted,
        "raw_text": text,
        "created_at": created_at,
        "language": "en",
        "language_name": "English"
    }

    # Step 5: Translate / Explain in the selected Indian language
    final_result = translate_analysis_findings(structured_analysis, language)
    return final_result
