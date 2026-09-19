import re

from app.core.security import validate_text_length


URGENCY_KEYWORDS = {
    "urgent",
    "immediately",
    "act now",
    "expires",
    "suspended",
    "blocked",
    "within 24 hours",
    "final warning",
}

CREDENTIAL_KEYWORDS = {
    "password",
    "username",
    "login",
    "sign in",
    "verify your account",
    "verification code",
    "otp",
    "pin",
    "credential",
}

FINANCIAL_KEYWORDS = {
    "bank",
    "account",
    "payment",
    "refund",
    "transaction",
    "upi",
    "credit card",
    "debit card",
    "wallet",
}

THREAT_KEYWORDS = {
    "suspended",
    "blocked",
    "legal action",
    "police",
    "arrest",
    "penalty",
    "fine",
}


def extract_urls(text: str) -> list[str]:
    pattern = r"https?://[^\s]+"
    return re.findall(pattern, text, re.IGNORECASE)


def find_keyword_matches(text: str, keywords: set[str]) -> list[str]:
    text_lower = text.lower()

    return sorted(
        keyword
        for keyword in keywords
        if keyword in text_lower
    )


def analyze_text(text: str) -> dict:
    """
    Analyze suspicious text using deterministic security indicators.

    The engine does not make an autonomous claim that a message
    is malicious. It identifies observable indicators.
    """

    text = validate_text_length(text)

    findings = []

    urls = extract_urls(text)

    if urls:
        findings.append({
            "type": "url",
            "severity": "medium",
            "title": "URL detected",
            "description": f"Detected {len(urls)} URL(s) in the message.",
            "urls": urls,
        })

    urgency_matches = find_keyword_matches(
        text,
        URGENCY_KEYWORDS,
    )

    if urgency_matches:
        findings.append({
            "type": "urgency",
            "severity": "medium",
            "title": "Urgency language detected",
            "description": (
                "The message contains language that may pressure "
                "the recipient into acting quickly."
            ),
            "matches": urgency_matches,
        })

    credential_matches = find_keyword_matches(
        text,
        CREDENTIAL_KEYWORDS,
    )

    if credential_matches:
        findings.append({
            "type": "credential",
            "severity": "high",
            "title": "Credential-related language detected",
            "description": (
                "The message contains terms associated with "
                "authentication or credential collection."
            ),
            "matches": credential_matches,
        })

    financial_matches = find_keyword_matches(
        text,
        FINANCIAL_KEYWORDS,
    )

    if financial_matches:
        findings.append({
            "type": "financial",
            "severity": "medium",
            "title": "Financial language detected",
            "description": (
                "The message contains financial or payment-related terms."
            ),
            "matches": financial_matches,
        })

    threat_matches = find_keyword_matches(
        text,
        THREAT_KEYWORDS,
    )

    if threat_matches:
        findings.append({
            "type": "threat_language",
            "severity": "medium",
            "title": "Threatening language detected",
            "description": (
                "The message contains language that may create "
                "fear or pressure."
            ),
            "matches": threat_matches,
        })

    return {
        "input_type": "TEXT",
        "text_length": len(text),
        "urls": urls,
        "findings": findings,
    }