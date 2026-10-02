import re
from typing import Dict, Any, List, Optional

# The 10 Core Deterministic Rules for TrustLens
RULES_CATALOG = [
    {
        "rule_id": "RF01",
        "title": "Guaranteed/Fixed Return Claim",
        "severity": "HIGH",
        "points": 25,
        "icon": "TrendingUp",
        "explanation": "Promises of fixed, guaranteed, or unusually high returns can be a warning sign. Financial markets fluctuate, and legitimate investments carry market risk.",
        "verification_action": "Verify whether the entity is offering unauthorized fixed return schemes; all market investments are subject to risk.",
        "patterns": [
            r"\b100%\s+profit\b",
            r"\bdouble\s+(?:your\s+)?money\b",
            r"\bdouble\s+(?:your\s+investment\s+)?in\s+\d+\s+(?:days|months|weeks)\b",
            r"\bguarantee(?:d)?\s+(?:return|returns|profit|monthly|gain|yield)\b",
            r"\bfixed\s+(?:return|returns|profit|income)\b",
            r"\bno\s+loss\b",
            r"\brisk[\s\-]free\s+(?:profit|return|investment)\b",
            r"\bassured\s+(?:profit|return|returns|income)\b",
            r"\bguaranteed\s+\d+%\s*(?:monthly|daily|weekly|annual)?\b",
            r"\b(?:1[5-9]|[2-9]\d)%\s+monthly\s+(?:return|returns|profit)?\b",
            r"\bsure\s+shot\s+(?:profit|gain)\b"
        ]
    },
    {
        "rule_id": "RF02",
        "title": "Urgency / Pressure",
        "severity": "MEDIUM",
        "points": 15,
        "icon": "Clock",
        "explanation": "The message pressures you to make a fast financial decision. Pressure to act immediately without independent verification is a common warning sign.",
        "verification_action": "Do not act under artificial time pressure. Take time to independently investigate before committing capital.",
        "patterns": [
            r"\blast\s+\d+\s+minutes\b",
            r"\bonly\s+today\b",
            r"\bact\s+now\b",
            r"\blimited\s+time\b",
            r"\boffer\s+expires?\s+(?:today|soon|in\s+\d+)\b",
            r"\boffer\s+valid\s+only\s+today\b",
            r"\bdon'?t\s+miss\s+(?:this|out)\b",
            r"\bsend\s+payment\s+immediately\b",
            r"\bonly\s+\d+\s+slots?\s+left\b",
            r"\bhurry\b",
            r"\bimmediate\s+action\s+required\b",
            r"\bvalid\s+(?:for\s+)?today\s+only\b",
            r"\burgent(?:ly)?(?:\s*!|\b)"
        ]
    },
    {
        "rule_id": "RF03",
        "title": "Insider / Exclusive Information Claim",
        "severity": "HIGH",
        "points": 25,
        "icon": "Eye",
        "explanation": "The message claims access to exclusive or insider information. Such claims should be treated cautiously and independently verified.",
        "verification_action": "Be cautious of claims regarding non-public information. Trading on unverified tips carries severe risk.",
        "patterns": [
            r"\binsider\s+(?:information|info|news|tip|call|deal)\b",
            r"\boperator\s+(?:news|call|info|stock|movement)\b",
            r"\bsecret\s+tip\b",
            r"\binside\s+source\b",
            r"\bexclusive\s+(?:information|info|leak)\b",
            r"\bmy\s+source\s+inside\s+the\s+company\b",
            r"\bguaranteed\s+insider\s+tip\b"
        ],
        "negative_patterns": [
            r"insider\s+trading\s+is\s+(?:illegal|prohibited|a\s+crime)",
            r"beware\s+of\s+insider"
        ]
    },
    {
        "rule_id": "RF04",
        "title": "Private Group / Off-Platform Move",
        "severity": "MEDIUM",
        "points": 15,
        "icon": "Users",
        "explanation": "The message encourages moving to a private group or another app. Moving discussions off public platforms can make independent verification more difficult.",
        "verification_action": "Verify whether group managers are SEBI-registered Research Analysts or Investment Advisers.",
        "patterns": [
            r"\bjoin\s+(?:our\s+)?vip\s+group\b",
            r"\bprivate\s+investment\s+group\b",
            r"\bexclusive\s+telegram\s+group\b",
            r"\bwhatsapp\s+vip\s+group\b",
            r"\bmove\s+to\s+telegram\b",
            r"\bcontact\s+(?:me\s+)?privately\b",
            r"\bdm\s+(?:me\s+)?for\s+entry\b",
            r"\bjoin\s+(?:our\s+)?private\s+channel\b",
            r"\bjoin\s+(?:our\s+)?telegram\s+group\b",
            r"\btelegram\s+channel\s+link\b",
            r"\bjoin\s+vip\b"
        ]
    },
    {
        "rule_id": "RF05",
        "title": "Suspicious App / Remote Access Request",
        "severity": "HIGH",
        "points": 25,
        "icon": "Download",
        "explanation": "The message asks you to install an application or provide remote access. This can expose devices or accounts to security risks.",
        "verification_action": "Never install APKs from outside official app stores or provide remote screen access to unknown parties.",
        "patterns": [
            r"\binstall\s+(?:unknown\s+)?apk\b",
            r"\bdownload\s+(?:an?\s+)?apk\b",
            r"\binstall\s+unknown\s+application\b",
            r"\binstall\s+remote\s+(?:desktop|access)\b",
            r"\binstall\s+remote\s+access\s+tool\b",
            r"\banydesk\b",
            r"\bteamviewer\b",
            r"\bscreen[\s\-]sharing\s+application\b",
            r"\bunknown\s+trading\s+application\b",
            r"\bdownload\s+an\s+apk\s+from\s+(?:a\s+)?link\b",
            r"\binstall\s+this\s+app\s+for\s+(?:trading|profit|support)\b"
        ]
    },
    {
        "rule_id": "RF06",
        "title": "Credential / OTP Request",
        "severity": "CRITICAL",
        "points": 30,
        "icon": "ShieldAlert",
        "explanation": "Never share OTPs, PINs, passwords or account credentials in response to unsolicited financial messages.",
        "verification_action": "Banks and official institutions never ask for OTPs or PINs. Terminate communication immediately.",
        "patterns": [
            r"(?:send|share|tell|provide|enter|disclose|give|input|submit)\s+(?:your\s+)?(?:otp|pin|upi\s+pin|banking\s+password|login\s+credentials?|verification\s+code|cvv)",
            r"(?:requesting|asking\s+for)\s+(?:your\s+)?(?:otp|pin|upi\s+pin|password|credentials)",
            r"\bshare\s+(?:your\s+)?screen\s+to\s+verify\b",
            r"\botp\s+is\s+required\s+to\s+(?:activate|receive|claim|unfreeze)\b"
        ],
        # Contextual false positive control:
        # e.g. "Learn what OTP means in financial security" must NOT trigger.
        "negative_patterns": [
            r"learn\s+what\s+otp\s+means",
            r"never\s+share\s+(?:your\s+)?otp",
            r"do\s+not\s+share\s+(?:your\s+)?otp",
            r"awareness\s+about\s+otp",
            r"definition\s+of\s+otp"
        ]
    },
    {
        "rule_id": "RF07",
        "title": "Suspicious / Shortened Link",
        "severity": "MEDIUM",
        "points": 15,
        "icon": "ExternalLink",
        "explanation": "The link format makes the destination harder to verify. Open official websites directly rather than relying on links received in unsolicited messages.",
        "verification_action": "Navigate directly to official web domains rather than clicking shortened or forwarded hyperlinks.",
        "patterns": [
            r"https?://(?:bit\.ly|tinyurl\.com|shorturl\.at|t\.co|is\.gd|ow\.ly|buff\.ly)/[^\s]+",
            r"https?://(?:[a-z0-9\-]+-sebi|sebi-[a-z0-9\-]+)\.[a-z]+",
            r"https?://(?:[a-z0-9\-]+-rbi|rbi-[a-z0-9\-]+)\.[a-z]+",
            r"https?://sebi-support[^\s]*",
            r"https?://rbi-verification[^\s]*"
        ]
    },
    {
        "rule_id": "RF08",
        "title": "SEBI Registration Claim",
        "severity": "MEDIUM",
        "points": 15,
        "icon": "FileCheck",
        "status": "VERIFY ON OFFICIAL SOURCE",
        "explanation": "The message contains a SEBI registration claim. TrustLens can check whether the number appears to follow a registration-number format, but it cannot confirm that the registration is genuine. Verify the entity and registration directly on SEBI's official website.",
        "verification_action": "Verify the registration claim on SEBI's official intermediary directory (sebi.gov.in).",
        "patterns": [
            r"\bsebi\s+registered\b",
            r"\bsebi\s+approved\b",
            r"\bsebi\s+registration\b",
            r"\bsebi\s+reg(?:\.|\s+no)?(?:\s*[:#]\s*|\s+)\w+",
            r"\bsebi\s+registration\s+number\b",
            r"\bsebi\s+registered\s+advisor\b",
            r"\b(?:IN[AHZ]\d{6,10}|IN[A-Z]\d{8,10})\b"
        ],
        # Contextual false positive control:
        # "SEBI provides investor education" or "SEBI is regulator" should not trigger as suspicious claim
        "negative_patterns": [
            r"sebi\s+provides\s+investor\s+education",
            r"sebi\s+is\s+the\s+regulator",
            r"visit\s+sebi\s+website",
            r"official\s+sebi\s+guidelines"
        ]
    },
    {
        "rule_id": "RF09",
        "title": "Specific Trading Tip",
        "severity": "MEDIUM",
        "points": 15,
        "icon": "Crosshair",
        "explanation": "The message provides a specific trading instruction. TrustLens does not evaluate or recommend whether the trade should be taken.",
        "verification_action": "Check whether the advisor issuing trading signals holds a valid SEBI Research Analyst registration.",
        "patterns": [
            r"\bbuy\s+(?:at\s+)?(?:rs\.?|₹)?\s*\d+",
            r"\btarget\s+(?:rs\.?|₹)?\s*\d+",
            r"\b(?:stop\s*loss|sl)\s+(?:at\s+)?(?:rs\.?|₹)?\s*\d+",
            r"\bentry\s+(?:at\s+)?(?:rs\.?|₹)?\s*\d+",
            r"\bbuy\s+[a-z]{2,10}\s+at\s+(?:rs\.?|₹)?\s*\d+",
            r"\bbuy\s+call\s+option\b",
            r"\bjackpot\s+call\b"
        ]
    },
    {
        "rule_id": "RF10",
        "title": "Personal Payment Request",
        "severity": "HIGH",
        "points": 20,
        "icon": "CreditCard",
        "explanation": "The message requests a financial payment to a personal or directly provided payment identifier. Independently verify the recipient and purpose before making any transaction.",
        "verification_action": "Independently verify beneficiary identity and account ownership before sending money.",
        "patterns": [
            r"\b[\w\.\-]+@(ok[a-z]+|paytm|ybl|ibl|axl|upi|barodampay|icici|sbi|postbank|fbl)\b",
            r"\bpay\s+this\s+upi\b",
            r"\btransfer\s+to\s+my\s+upi\b",
            r"\bpersonal\s+upi\b",
            r"\bsend\s+payment\s+to\s+(?:activate|join|this)\b",
            r"\bsend\s+payment\b",
            r"\bsend\s+(?:rs\.?|₹)\s*[\d,]+",
            r"\btransfer\s+(?:rs\.?|₹)\s*[\d,]+",
            r"\bpay\s+(?:rs\.?|₹)\s*[\d,]+\s+to\s+join\b",
            r"\bdeposit\s+(?:rs\.?|₹)\s*[\d,]+"
        ]
    }
]

def check_sebi_format(text: str) -> Optional[str]:
    """Checks if a potential SEBI registration number matches known alphanumeric formats."""
    match = re.search(r"\b(IN[AHZ]\d{6,10}|IN[A-Z]\d{8,10})\b", text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None

def analyze_rules(text: str) -> Dict[str, Any]:
    """
    Executes the 10 deterministic rules on financial content.
    Returns:
    - score: integer 0-100
    - risk_level: 'LOW RISK' | 'NEEDS VERIFICATION' | 'HIGH RISK'
    - red_flags: List of structured red flag items (rule_id, title, severity, matched_text, explanation, verification_action, icon)
    - claims: List of detected claims
    - why_flagged: Sequential numbered timeline steps (01, 02, ...)
    - action_dos: General educational DOs (strictly no investment advice)
    - action_donts: General educational DON'Ts
    """
    total_score = 0
    matched_flags = []
    matched_rule_ids = set()
    why_flagged = []
    detected_claims = []
    detected_keywords = []

    step_counter = 1

    for rule in RULES_CATALOG:
        # Check negative patterns (false positive control)
        has_negative = False
        for neg in rule.get("negative_patterns", []):
            if re.search(neg, text, re.IGNORECASE):
                has_negative = True
                break

        if has_negative:
            continue

        matched_snippets = []
        is_matched = False

        for pat in rule["patterns"]:
            matches = list(re.finditer(pat, text, re.IGNORECASE))
            if matches:
                is_matched = True
                for m in matches:
                    snippet = m.group(0).strip()
                    if snippet not in matched_snippets:
                        matched_snippets.append(snippet)
                    detected_keywords.append(snippet)

        if is_matched:
            total_score += rule["points"]
            matched_rule_ids.add(rule["rule_id"])
            
            matched_text = matched_snippets[0] if matched_snippets else ""
            
            matched_flags.append({
                "rule_id": rule["rule_id"],
                "title": rule["title"],
                "severity": rule["severity"],
                "matched_text": matched_text,
                "explanation": rule["explanation"],
                "verification_action": rule["verification_action"],
                "icon": rule.get("icon", "AlertTriangle")
            })

            # Numbered timeline explanation step
            step_num = f"{step_counter:02d}"
            step_counter += 1
            sample_snip = f'"{matched_text}"' if matched_text else "relevant pattern"
            why_flagged.append({
                "step_number": step_num,
                "title": f"{rule['title']} detected",
                "description": f"Identified trigger phrasing: {sample_snip}. {rule['explanation']}"
            })

    # Specific Claim Extraction (with official safety standards)
    if "RF08" in matched_rule_ids:
        sebi_no = check_sebi_format(text)
        format_note = f" (Format '{sebi_no}' plausible, but requires official verification)" if sebi_no else ""
        detected_claims.append({
            "claim": f"SEBI approval or registration claim{format_note}",
            "status": "VERIFY ON OFFICIAL SOURCE",
            "explanation": "The message contains a SEBI registration claim. TrustLens can check whether the number appears to follow a registration-number format, but it cannot confirm that the registration is genuine. Verify the entity and registration directly on SEBI's official website.",
            "source": "SEBI Official Intermediary Directory",
            "source_url": "https://www.sebi.gov.in"
        })

    if "RF01" in matched_rule_ids:
        detected_claims.append({
            "claim": "Guaranteed or fixed return promise",
            "status": "NOT VERIFIED",
            "explanation": "Market securities cannot offer guaranteed returns under regulatory guidelines. Returns are contingent on market risk.",
            "source": "SEBI Investor Advisory on Guaranteed Returns",
            "source_url": "https://investor.sebi.gov.in"
        })

    if "RF09" in matched_rule_ids:
        detected_claims.append({
            "claim": "Specific buy / target / stop-loss instruction",
            "status": "NEEDS VERIFICATION",
            "explanation": "The message provides a specific trading instruction. TrustLens does not evaluate or recommend whether the trade should be taken. Verify advisor registration.",
            "source": "SEBI Research Analyst Regulations",
            "source_url": "https://www.sebi.gov.in"
        })

    if "RF03" in matched_rule_ids:
        detected_claims.append({
            "claim": "Claim of insider or exclusive operator information",
            "status": "NOT VERIFIED",
            "explanation": "The message claims access to exclusive or insider information. Such claims should be treated cautiously and independently verified.",
            "source": "SEBI Prohibition of Insider Trading Framework",
            "source_url": "https://investor.sebi.gov.in"
        })

    if "RF06" in matched_rule_ids:
        detected_claims.append({
            "claim": "Request for confidential credential or OTP",
            "status": "NOT VERIFIED",
            "explanation": "Banks, payment apps, and regulatory authorities never solicit OTPs, UPI PINs, or account passwords.",
            "source": "RBI Kehta Hai - Security Directives",
            "source_url": "https://rbikehtahai.rbi.org.in"
        })

    # Cap score at 100
    capped_score = min(100, max(0, total_score))

    # Categorize Risk
    if capped_score >= 60:
        risk_level = "HIGH RISK"
        summary = (
            "This message contains multiple high-risk indicators commonly associated with unauthorized solicitations, "
            "such as guaranteed return promises, artificial urgency, or direct payment requests. Independent verification is strongly recommended."
        )
    elif capped_score >= 30:
        risk_level = "NEEDS VERIFICATION"
        summary = (
            "This message contains claims or promotional language that require independent verification "
            "with official regulatory directories or licensed professionals before taking any action."
        )
    else:
        risk_level = "LOW RISK"
        summary = (
            "No prominent high-risk red flag patterns were detected in this message. "
            "Continue to exercise standard financial prudence and verify entity details through official sources."
        )

    # Neutral Educational Actions (STRICTLY NO INVESTMENT ADVICE)
    action_dos = [
        "Verify any registration claims directly on official regulatory websites (e.g. sebi.gov.in or rbi.org.in).",
        "Take at least 24 hours to independently investigate any unsolicited financial proposal.",
        "Check whether the individual or firm is a registered Investment Adviser or Research Analyst.",
        "Review official Scheme Information Documents (SID) or prospectuses before transferring funds."
    ]

    action_donts = [
        "Never share OTPs, UPI PINs, banking passwords, or identity credentials with anyone.",
        "Do not transfer money based on urgent deadlines or fear of missing out.",
        "Do not install APKs or grant remote screen-sharing access to unknown individuals.",
        "Do not rely on forwarded screenshots, certificates, or group testimonials as proof of legality."
    ]

    return {
        "score": capped_score,
        "risk_level": risk_level,
        "summary": summary,
        "red_flags": matched_flags,
        "claims": detected_claims,
        "why_flagged": why_flagged,
        "action_dos": action_dos,
        "action_donts": action_donts,
        "detected_keywords": detected_keywords
    }
