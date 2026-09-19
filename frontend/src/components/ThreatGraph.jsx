import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

function getNodeColor(risk) {
  switch (risk?.toUpperCase()) {
    case "CRITICAL":
      return "#ef4444";

    case "HIGH":
      return "#f97316";

    case "MEDIUM":
      return "#eab308";

    case "LOW":
      return "#22c55e";

    default:
      return "#64748b";
  }
}

function getNodePosition(node, index) {
  const positions = {
    investigation: {
      x: 0,
      y: 180,
    },

    url: {
      x: 300,
      y: 80,
    },

    domain: {
      x: 600,
      y: 20,
    },

    path: {
      x: 600,
      y: 160,
    },

    message: {
      x: 300,
      y: 180,
    },

    screenshot: {
      x: 300,
      y: 80,
    },

    ocr: {
      x: 600,
      y: 80,
    },

    classification: {
      x: 900,
      y: 180,
    },
  };

  if (positions[node.id]) {
    return positions[node.id];
  }

  return {
    x: 600 + (index % 2) * 250,
    y: 300 + Math.floor(index / 2) * 140,
  };
}

function ThreatGraph({ graph }) {
  if (!graph?.nodes?.length) {
    return (
      <div className="graph-empty">
        No relationship data available.
      </div>
    );
  }

  const nodes = graph.nodes.map((node, index) => {
    const position = getNodePosition(node, index);

    return {
      id: node.id,

      position,

      data: {
        label: (
          <div className="threat-node">
            <strong>{node.label}</strong>

            <span>
              {node.type}
            </span>
          </div>
        ),
      },

      style: {
        background: "#111827",
        color: "#e5e7eb",
        border: `2px solid ${getNodeColor(node.risk)}`,
        borderRadius: "12px",
        padding: "12px",
        width: 190,
        boxShadow: "0 8px 25px rgba(0, 0, 0, 0.25)",
      },
    };
  });

  const edges = graph.relationships.map(
    (relationship, index) => ({
      id: `edge-${index}`,

      source: relationship.source,

      target: relationship.target,

      label: relationship.relationship,

      animated: true,

      style: {
        stroke: "#64748b",
        strokeWidth: 1.5,
      },

      labelStyle: {
        fill: "#94a3b8",
        fontSize: 10,
      },

      labelBgStyle: {
        fill: "#080d17",
      },
    })
  );

  return (
    <div className="threat-flow">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        attributionPosition="bottom-left"
      >
        <Background />

        <Controls />

        <MiniMap />
      </ReactFlow>
    </div>
  );
}

export default ThreatGraph;
