import {
  CheckCircle2,
  Brain,
  Database,
  Search,
  ShieldAlert,
  Activity,
} from "lucide-react";

function getEventIcon(type) {
  switch (type) {
    case "created":
      return <Activity size={16} />;

    case "analysis_completed":
      return <Search size={16} />;

    case "evidence_detected":
      return <Database size={16} />;

    case "risk_calculated":
      return <ShieldAlert size={16} />;

    case "classified":
      return <CheckCircle2 size={16} />;

    case "ai_report":
      return <Brain size={16} />;

    case "completed":
      return <CheckCircle2 size={16} />;

    default:
      return <Activity size={16} />;
  }
}

function formatTime(timestamp) {
  if (!timestamp) return "";

  return new Date(timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function InvestigationTimeline({ timeline }) {
  if (!timeline?.length) {
    return (
      <div className="timeline-empty">
        No investigation timeline available.
      </div>
    );
  }

  return (
    <div className="investigation-timeline">
      {timeline.map((event) => (
        <div className="timeline-item" key={event.id}>
          <div className="timeline-marker">
            {getEventIcon(event.event_type)}
          </div>

          <div className="timeline-line" />

          <div className="timeline-content">
            <div className="timeline-header">
              <strong>{event.message}</strong>
              <span>{formatTime(event.created_at)}</span>
            </div>

            <small>
              {event.event_type.replaceAll("_", " ").toUpperCase()}
            </small>
          </div>
        </div>
      ))}
    </div>
  );
}

export default InvestigationTimeline;
