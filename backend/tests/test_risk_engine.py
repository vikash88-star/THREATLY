from app.engines.risk_engine import (
    calculate_risk,
    classify_threat,
)


def test_high_risk():
    findings = [
        {
            "type": "domain",
            "severity": "high",
        },
        {
            "type": "credential",
            "severity": "high",
        },
        {
            "type": "url_pattern",
            "severity": "medium",
        },
    ]

    result = calculate_risk(findings)

    assert result["risk_score"] == 50
    assert result["risk_level"] == "HIGH"


def test_credential_classification():
    findings = [
        {
            "type": "credential",
            "severity": "high",
        }
    ]

    result = classify_threat(findings, "HIGH")

    assert result == "Potential Credential Phishing"