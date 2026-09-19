SEVERITY_WEIGHTS = {
    "critical": 25,
    "high": 20,
    "medium": 10,
    "low": 5,
    "info": 0,
}


def calculate_risk(findings: list[dict]) -> dict:
    """
    Calculate a deterministic risk score from security findings.

    This is an MVP heuristic model, not a statistically validated
    probability of maliciousness.
    """

    score = 0

    for finding in findings:
        severity = finding.get("severity", "info").lower()
        score += SEVERITY_WEIGHTS.get(severity, 0)

    score = min(score, 100)

    if score >= 75:
        level = "CRITICAL"
    elif score >= 50:
        level = "HIGH"
    elif score >= 25:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "risk_score": score,
        "risk_level": level,
        "finding_count": len(findings),
    }


def classify_threat(findings: list[dict], risk_level: str) -> str:
    """
    Determine a high-level threat classification from evidence.
    """

    finding_types = {
        finding.get("type", "").lower()
        for finding in findings
    }

    if "credential" in finding_types:
        return "Potential Credential Phishing"

    if "domain" in finding_types and risk_level in {"HIGH", "CRITICAL"}:
        return "Suspicious Domain Activity"

    if "url_pattern" in finding_types:
        return "Suspicious URL"

    if risk_level in {"HIGH", "CRITICAL"}:
        return "Potential Malicious URL"

    return "No Strong Threat Indicators"