from app.engines.risk_engine import calculate_risk, classify_threat
from urllib.parse import urlparse
import re


SUSPICIOUS_TLDS = {
    ".xyz",
    ".top",
    ".click",
    ".work",
    ".gq",
    ".tk",
    ".ml",
    ".ga",
    ".cf",
}

SUSPICIOUS_KEYWORDS = {
    "login",
    "verify",
    "verification",
    "secure",
    "account",
    "update",
    "password",
    "bank",
    "wallet",
    "payment",
    "signin",
    "confirm",
}


def analyze_url(url: str) -> dict:
    """
    Perform deterministic security analysis of a URL.

    This is an MVP heuristic engine.
    It does not visit or execute the target URL.
    """

    original_url = url.strip()
    findings = []

    # --------------------------------------------------
    # Parse URL
    # --------------------------------------------------

    if not re.match(r"^https?://", original_url, re.IGNORECASE):
        url_to_parse = "http://" + original_url
    else:
        url_to_parse = original_url

    parsed = urlparse(url_to_parse)
    hostname = parsed.hostname or ""

    if not hostname:
        return {
            "url": original_url,
            "valid": False,
            "risk_score": 0,
            "risk_level": "UNKNOWN",
            "classification": "Invalid URL",
            "findings": [
                {
                    "type": "validation",
                    "severity": "high",
                    "title": "Invalid URL",
                    "description": "The supplied value could not be parsed as a valid URL.",
                }
            ],
        }

    hostname_lower = hostname.lower()

    # --------------------------------------------------
    # HTTPS check
    # --------------------------------------------------

    if parsed.scheme.lower() != "https":
        findings.append({
            "type": "transport",
            "severity": "medium",
            "title": "No HTTPS",
            "description": "The URL does not use HTTPS.",
        })

    # --------------------------------------------------
    # Suspicious TLD
    # --------------------------------------------------

    if any(hostname_lower.endswith(tld) for tld in SUSPICIOUS_TLDS):
        findings.append({
            "type": "domain",
            "severity": "high",
            "title": "Suspicious TLD",
            "description": "The domain uses a TLD frequently associated with disposable or suspicious domains.",
        })

    # --------------------------------------------------
    # Suspicious keywords
    # --------------------------------------------------

    detected_keywords = []

    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword in hostname_lower or keyword in parsed.path.lower():
            detected_keywords.append(keyword)

    if detected_keywords:
        findings.append({
            "type": "url_pattern",
            "severity": "medium",
            "title": "Suspicious URL keywords",
            "description": f"Detected keywords: {', '.join(sorted(detected_keywords))}.",
        })

    # --------------------------------------------------
    # IP address instead of domain
    # --------------------------------------------------

    if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", hostname):
        findings.append({
            "type": "host",
            "severity": "high",
            "title": "IP address used as host",
            "description": "The URL uses an IP address instead of a conventional domain name.",
        })

    # --------------------------------------------------
    # Excessive subdomains
    # --------------------------------------------------

    subdomain_count = max(len(hostname.split(".")) - 2, 0)

    if subdomain_count >= 3:
        findings.append({
            "type": "domain",
            "severity": "medium",
            "title": "Excessive subdomains",
            "description": "The hostname contains an unusually large number of subdomain levels.",
        })

    # --------------------------------------------------
    # Credential-related path
    # --------------------------------------------------

    credential_words = {
        "password",
        "credential",
        "signin",
        "login",
        "verify",
    }

    if any(word in parsed.path.lower() for word in credential_words):
        findings.append({
            "type": "credential",
            "severity": "high",
            "title": "Credential-related path",
            "description": "The URL path appears related to authentication or credential collection.",
        })

    risk_result = calculate_risk(findings)

    risk_score = risk_result["risk_score"]
    risk_level = risk_result["risk_level"]

    classification = classify_threat(
        findings,
        risk_level,
    )

    return {
        "url": original_url,
        "valid": True,
        "hostname": hostname,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "classification": classification,
        "findings": findings,
    }