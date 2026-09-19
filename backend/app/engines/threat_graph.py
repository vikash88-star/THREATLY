from urllib.parse import urlparse


def add_node(
    nodes,
    node_id,
    node_type,
    label,
    risk="INFO",
):
    if any(node["id"] == node_id for node in nodes):
        return

    nodes.append(
        {
            "id": node_id,
            "type": node_type,
            "label": label,
            "risk": risk,
        }
    )


def add_relationship(
    relationships,
    source,
    relationship,
    target,
):
    relationships.append(
        {
            "source": source,
            "relationship": relationship,
            "target": target,
        }
    )


def build_threat_graph(investigation: dict) -> dict:
    input_type = investigation["input_type"].upper()
    input_value = investigation["input"]
    risk_level = investigation["risk_level"]

    nodes = []
    relationships = []

    # ---------------------------------------------------------
    # Investigation root
    # ---------------------------------------------------------

    add_node(
        nodes,
        "investigation",
        "investigation",
        "Investigation",
        risk_level,
    )

    # ---------------------------------------------------------
    # URL investigation
    # ---------------------------------------------------------

    if input_type == "URL":

        parsed = urlparse(
            input_value
            if "://" in input_value
            else f"https://{input_value}"
        )

        hostname = parsed.hostname or "unknown-host"
        path = parsed.path or "/"

        add_node(
            nodes,
            "url",
            "url",
            input_value,
            risk_level,
        )

        add_node(
            nodes,
            "domain",
            "domain",
            hostname,
            risk_level,
        )

        add_relationship(
            relationships,
            "investigation",
            "analyzes",
            "url",
        )

        add_relationship(
            relationships,
            "url",
            "uses",
            "domain",
        )

        if path != "/":
            add_node(
                nodes,
                "path",
                "path",
                path,
                risk_level,
            )

            add_relationship(
                relationships,
                "url",
                "contains",
                "path",
            )

        parent_node = "url"

    # ---------------------------------------------------------
    # Text investigation
    # ---------------------------------------------------------

    elif input_type == "TEXT":

        add_node(
            nodes,
            "message",
            "message",
            "Suspicious Message",
            risk_level,
        )

        add_relationship(
            relationships,
            "investigation",
            "analyzes",
            "message",
        )

        parent_node = "message"

    # ---------------------------------------------------------
    # Screenshot / image investigation
    # ---------------------------------------------------------

    elif input_type == "IMAGE":

        add_node(
            nodes,
            "screenshot",
            "image",
            "Uploaded Screenshot",
            risk_level,
        )

        add_node(
            nodes,
            "ocr",
            "ocr",
            "OCR Extracted Text",
            risk_level,
        )

        add_relationship(
            relationships,
            "investigation",
            "analyzes",
            "screenshot",
        )

        add_relationship(
            relationships,
            "screenshot",
            "processed_by",
            "ocr",
        )

        parent_node = "ocr"

    else:

        add_node(
            nodes,
            "input",
            "input",
            input_type,
            risk_level,
        )

        add_relationship(
            relationships,
            "investigation",
            "analyzes",
            "input",
        )

        parent_node = "input"

    # ---------------------------------------------------------
    # Evidence
    # ---------------------------------------------------------

    for evidence in investigation.get("evidence", []):

        evidence_id = evidence["id"]

        severity = evidence.get(
            "severity",
            "info",
        ).upper()

        add_node(
            nodes,
            evidence_id,
            "evidence",
            evidence.get(
                "title",
                "Security Finding",
            ),
            severity,
        )

        add_relationship(
            relationships,
            parent_node,
            "has_evidence",
            evidence_id,
        )

    # ---------------------------------------------------------
    # Classification
    # ---------------------------------------------------------

    classification = investigation.get(
        "classification",
        "Unknown",
    )

    add_node(
        nodes,
        "classification",
        "threat",
        classification,
        risk_level,
    )

    add_relationship(
        relationships,
        "investigation",
        "classified_as",
        "classification",
    )

    return {
        "investigation_id": investigation["id"],
        "input_type": input_type,
        "risk_level": risk_level,
        "nodes": nodes,
        "relationships": relationships,
    }
