def findings_to_evidence(
    findings: list[dict],
    source: str = "Threatly Analyzer",
) -> list[dict]:
    evidence = []

    for index, finding in enumerate(
        findings,
        start=1,
    ):
        evidence.append(
            {
                "id": f"E-{index:03d}",
                "type": finding.get(
                    "type",
                    "unknown",
                ),
                "title": finding.get(
                    "title",
                    "Security Finding",
                ),
                "description": finding.get(
                    "description",
                    "A security-related indicator was detected.",
                ),
                "severity": finding.get(
                    "severity",
                    "info",
                ),
                "source": source,
            }
        )

    return evidence