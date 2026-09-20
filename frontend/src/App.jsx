import { useState } from "react";
import {
  Shield,
  Link,
  MessageSquare,
  Image,
  Search,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Upload,
  Network,
} from "lucide-react";

import ThreatGraph from "./components/ThreatGraph";
import InvestigationTimeline from "./components/InvestigationTimeline";

import "./index.css";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const DEMO_SCENARIOS = {
  phishingUrl: {
    name: "Phishing URL",
    type: "URL",
    value:
      "https://secure-account-verification.xyz/login",
  },

  fakeBankSms: {
    name: "Fake Bank SMS",
    type: "TEXT",
    value:
      "URGENT: Your bank account has been suspended. Verify your password and OTP immediately to avoid permanent blocking. Confirm your account within 24 hours: https://secure-account-verification.xyz/login",
  },

  credentialPhishing: {
    name: "Credential Phishing",
    type: "TEXT",
    value:
      "FINAL WARNING: Your account verification expires today. Sign in immediately to prevent account suspension. Enter your username, password and verification code at https://account-security-check.top/verify",
  },
};

function App() {
  const [inputType, setInputType] = useState("URL");
  const [inputValue, setInputValue] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [graph, setGraph] = useState(null);
  const [report, setReport] = useState(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [timeline, setTimeline] = useState([]);

  const loadDemoScenario = async (scenario) => {
    setShowHistory(false);
    setInputType(scenario.type);
    setInputValue(scenario.value);
    setSelectedFile(null);
    setResult(null);
    setGraph(null);
    setTimeline([]);
    setReport(null);

    await new Promise((resolve) =>
      setTimeout(resolve, 150)
    );

    setLoading(true);

    try {
      const response = await fetch(
        `${API_BASE}/api/investigations`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            input_type: scenario.type,
            input_value: scenario.value,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Demo investigation failed."
        );
      }

      setResult(data);

      if (data.id) {
        const graphResponse = await fetch(
          `${API_BASE}/api/investigations/${data.id}/graph`
        );

        if (graphResponse.ok) {
          const graphData = await graphResponse.json();
          setGraph(graphData);
        }

        const timelineResponse = await fetch(
          `${API_BASE}/api/investigations/${data.id}/timeline`
        );

        if (timelineResponse.ok) {
          const timelineData = await timelineResponse.json();
          setTimeline(timelineData.timeline || []);
        }
      }
    } catch (error) {
      setResult({
        error: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  const investigate = async () => {
    if (inputType === "IMAGE" && !selectedFile) {
      return;
    }

    if (inputType !== "IMAGE" && !inputValue.trim()) {
      return;
    }

    setLoading(true);
    setResult(null);
    setGraph(null);
    setReport(null);
    setTimeline([]);

    try {
      let response;

      if (inputType === "IMAGE") {
        const formData = new FormData();
        formData.append("file", selectedFile);

        response = await fetch(
          `${API_BASE}/api/analyze/image`,
          {
            method: "POST",
            body: formData,
          }
        );
      } else {
        response = await fetch(
          `${API_BASE}/api/investigations`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              input_type: inputType,
              input_value: inputValue,
            }),
          }
        );
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Investigation failed."
        );
      }

      setResult(data);

      if (data.id) {
        const graphResponse = await fetch(
          `${API_BASE}/api/investigations/${data.id}/graph`
        );

        if (graphResponse.ok) {
          const graphData = await graphResponse.json();
          setGraph(graphData);
        }

        const timelineResponse = await fetch(
          `${API_BASE}/api/investigations/${data.id}/timeline`
        );

        if (timelineResponse.ok) {
          const timelineData = await timelineResponse.json();
          setTimeline(timelineData.timeline || []);
        }
      }
    } catch (error) {
      setResult({
        error: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async () => {
    if (!result?.id) {
      return;
    }

    setReportLoading(true);
    setReport(null);

    try {
      const response = await fetch(
        `${API_BASE}/api/reports/${result.id}`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "AI report generation failed."
        );
      }

      setReport(data.report);

    } catch (error) {
      setReport({
        error: error.message,
      });
    } finally {
      setReportLoading(false);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await fetch(
        `${API_BASE}/api/investigations`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to load history."
        );
      }

      setHistory(data.investigations || []);
      setShowHistory(true);

    } catch (error) {
      console.error(
        "History loading failed:",
        error
      );
    }
  };

  const openInvestigation = async (
    investigationId
  ) => {
    setLoading(true);
    setShowHistory(false);
    setReport(null);
    setGraph(null);
    setTimeline([]);

    try {
      const response = await fetch(
        `${API_BASE}/api/investigations/${investigationId}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to load investigation."
        );
      }

      setResult(data);

      const graphResponse = await fetch(
        `${API_BASE}/api/investigations/${investigationId}/graph`
      );

      if (graphResponse.ok) {
        const graphData = await graphResponse.json();
        setGraph(graphData);
      }

      const timelineResponse = await fetch(
        `${API_BASE}/api/investigations/${investigationId}/timeline`
      );

      if (timelineResponse.ok) {
        const timelineData = await timelineResponse.json();
        setTimeline(timelineData.timeline || []);
      }

      setInputType(data.input_type);

      if (
        data.input_type === "URL" ||
        data.input_type === "TEXT"
      ) {
        setInputValue(data.input);
      } else {
        setInputValue("");
      }

      setSelectedFile(null);

    } catch (error) {
      setResult({
        error: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  const getRiskClass = (level) => {
    switch (level?.toUpperCase()) {
      case "CRITICAL":
        return "risk-critical";

      case "HIGH":
        return "risk-high";

      case "MEDIUM":
        return "risk-medium";

      case "LOW":
        return "risk-low";

      default:
        return "risk-unknown";
    }
  };

  const getStatusLabel = (status) => {
    switch (status?.toLowerCase()) {
      case "analyzing":
        return "ANALYZING";

      case "completed":
        return "COMPLETED";

      case "failed":
        return "FAILED";

      default:
        return "READY";
    }
  };

  const handleTypeChange = (type) => {
    setInputType(type);
    setResult(null);
    setGraph(null);
    setReport(null);
    setTimeline([]);
    setInputValue("");
    setSelectedFile(null);
  };

  return (
    <div className="app">

      <aside className="sidebar">

        <div className="brand">
          <div className="brand-icon">
            <Shield size={25} />
          </div>

          <div>
            <h1>Threatly</h1>
            <span>Digital Threat Investigation</span>
          </div>
        </div>

        <nav>
          <button
            className={
              showHistory
                ? "nav-item"
                : "nav-item active"
            }
          >
            <Activity size={18} />
            Investigation
          </button>

          <button
            className={
              showHistory
                ? "nav-item active"
                : "nav-item"
            }
            onClick={loadHistory}
          >
            <Clock size={18} />
            History
          </button>
        </nav>

        <div className="sidebar-footer">
          <div className="status-dot"></div>
          Threatly Engine Online
        </div>

      </aside>

      <main className="main">

        <header className="topbar">

          <div>
            <h2>Threat Investigation</h2>
            <p>
              Detect. Investigate. Explain.
            </p>
          </div>

          <div className="engine-status">
            <span className="status-dot"></span>
            Engine Online
          </div>

        </header>

        {showHistory ? (

          <section className="history-section">

            <div className="section-heading">

              <div>
                <span className="eyebrow">
                  CASE MANAGEMENT
                </span>

                <h3>
                  Investigation History
                </h3>

                <p>
                  Previously analyzed security investigations.
                </p>
              </div>

              <Clock size={22} />

            </div>

            <div className="history-list">

              {history.length === 0 ? (

                <div className="history-empty">
                  No investigations yet.
                </div>

              ) : (

                history.map((item) => (

                  <button
                    className="history-item"
                    key={item.id}
                    onClick={() =>
                      openInvestigation(item.id)
                    }
                  >

                    <div className="history-icon">
                      {item.input_type === "IMAGE"
                        ? "IMG"
                        : item.input_type === "TEXT"
                          ? "MSG"
                          : "URL"}
                    </div>

                    <div className="history-content">

                      <strong>
                        {item.classification}
                      </strong>

                      <span>
                        {item.input}
                      </span>

                      <small>
                        {item.input_type}
                        {" · "}
                        {item.confidence}% confidence
                      </small>

                    </div>

                    <div className="history-risk">

                      <span
                        className={`risk-badge ${getRiskClass(
                          item.risk_level
                        )}`}
                      >
                        {item.risk_level}
                      </span>

                      <strong>
                        {item.risk_score}/100
                      </strong>

                    </div>

                  </button>

                ))

              )}

            </div>

          </section>

        ) : (

          <>

        <section className="investigation-card">

          <div className="section-heading">

            <div>
              <h3>New Investigation</h3>

              <p>
                Analyze suspicious URLs, messages,
                and digital evidence.
              </p>
            </div>

            <div className="investigation-heading-tools">
              <Search size={22} />
              <div className="investigation-status">
                <span className="status-dot" />
                {getStatusLabel(result?.status)}
              </div>
            </div>

          </div>

          <section className="demo-scenarios">
            <div className="demo-header">
              <div>
                <span className="eyebrow">LIVE DEMO</span>
                <h3>Quick Investigation Scenarios</h3>
              </div>

              <span className="demo-hint">
                Safe synthetic test data
              </span>
            </div>

            <div className="demo-grid">
              <button
                className="demo-card"
                onClick={() =>
                  loadDemoScenario(DEMO_SCENARIOS.phishingUrl)
                }
              >
                <div className="demo-card-icon">URL</div>

                <div>
                  <strong>Run Phishing URL</strong>
                  <span>
                    Suspicious domain + credential path
                  </span>
                </div>
              </button>

              <button
                className="demo-card"
                onClick={() =>
                  loadDemoScenario(DEMO_SCENARIOS.fakeBankSms)
                }
              >
                <div className="demo-card-icon">SMS</div>

                <div>
                  <strong>Run Fake Bank SMS</strong>
                  <span>
                    Urgency + financial + credential indicators
                  </span>
                </div>
              </button>

              <button
                className="demo-card"
                onClick={() =>
                  loadDemoScenario(
                    DEMO_SCENARIOS.credentialPhishing
                  )
                }
              >
                <div className="demo-card-icon">AUTH</div>

                <div>
                  <strong>Run Credential Phishing</strong>
                  <span>
                    Login + password + verification indicators
                  </span>
                </div>
              </button>
            </div>
          </section>

          <div className="input-types">

            <button
              className={
                inputType === "URL"
                  ? "input-type active"
                  : "input-type"
              }
              onClick={() => handleTypeChange("URL")}
            >
              <Link size={19} />
              URL
            </button>

            <button
              className={
                inputType === "TEXT"
                  ? "input-type active"
                  : "input-type"
              }
              onClick={() => handleTypeChange("TEXT")}
            >
              <MessageSquare size={19} />
              Message
            </button>

            <button
              className={
                inputType === "IMAGE"
                  ? "input-type active"
                  : "input-type"
              }
              onClick={() => handleTypeChange("IMAGE")}
            >
              <Image size={19} />
              Screenshot
            </button>

          </div>

          {inputType === "IMAGE" ? (

            <div className="upload-box">

              <Upload size={32} />

              <h4>
                Upload suspicious screenshot
              </h4>

              <p>
                PNG, JPEG or WEBP · Maximum 5 MB
              </p>

              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                onChange={(event) => {
                  setSelectedFile(
                    event.target.files?.[0] || null
                  );
                }}
              />

              {selectedFile && (
                <div className="selected-file">
                  <CheckCircle size={17} />
                  {selectedFile.name}
                </div>
              )}

            </div>

          ) : (

            <textarea
              value={inputValue}
              onChange={(event) =>
                setInputValue(event.target.value)
              }
              placeholder={
                inputType === "URL"
                  ? "Paste a suspicious URL..."
                  : "Paste a suspicious message..."
              }
            />

          )}

          <div className="action-row">

            <span>
              {inputType === "IMAGE"
                ? selectedFile
                  ? `${(
                      selectedFile.size / 1024
                    ).toFixed(1)} KB`
                  : "No screenshot selected"
                : `${inputValue.length} characters`}
            </span>

            <button
              className="primary-action"
              onClick={investigate}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="loading-spinner" />
                  Investigating...
                </>
              ) : (
                "Investigate Threat"
              )}
            </button>

          </div>

        </section>

        {!result && !loading && !showHistory && (
          <div className="empty-investigation">
            <div className="empty-icon">T</div>

            <h3>Ready to investigate</h3>

            <p>
              Submit a suspicious URL, message, or screenshot.
              Threatly will analyze the input, correlate evidence,
              calculate risk, and build an investigation trail.
            </p>

            <div className="empty-flow">
              <span>Input</span>
              <b>→</b>
              <span>Evidence</span>
              <b>→</b>
              <span>Risk</span>
              <b>→</b>
              <span>Explanation</span>
            </div>
          </div>
        )}

        {result && !result.error && (

          <section className="result-section">

            <div className="result-header">

              <div>
                <span className="eyebrow">
                  INVESTIGATION COMPLETE
                </span>

                <h3>
                  Threat Assessment
                </h3>
              </div>

              <div
                className={`risk-badge ${getRiskClass(
                  result.risk_level
                )}`}
              >
                {result.risk_level}
              </div>

            </div>

            <div className="risk-score-card">
              <div className="risk-score-header">
                <div>
                  <span className="eyebrow">THREAT SCORE</span>
                  <h3>Risk Assessment</h3>
                </div>

                <span
                  className={`risk-badge ${getRiskClass(
                    result.risk_level
                  )}`}
                >
                  {result.risk_level}
                </span>
              </div>

              <div className="risk-score-main">
                <div className="risk-score-number">
                  {result.risk_score}
                  <span>/100</span>
                </div>

                <div className="risk-score-meta">
                  <strong>{result.classification}</strong>

                  <span>
                    Assessment confidence: {result.confidence}%
                  </span>
                </div>
              </div>

              <div className="risk-progress">
                <div
                  className={`risk-progress-fill ${getRiskClass(
                    result.risk_level
                  )}`}
                  style={{
                    width: `${Math.min(
                      result.risk_score || 0,
                      100
                    )}%`,
                  }}
                />
              </div>

              <div className="risk-scale">
                <span>LOW</span>
                <span>MEDIUM</span>
                <span>HIGH</span>
                <span>CRITICAL</span>
              </div>
            </div>

            <div className="result-grid">

              <div className="result-card">

                <span className="card-label">
                  CLASSIFICATION
                </span>

                <h4>
                  {result.classification}
                </h4>

                <div className="confidence">
                  <CheckCircle size={16} />
                  {result.confidence || 0}% confidence
                </div>

              </div>

              <div className="result-card">

                <span className="card-label">
                  STATUS
                </span>

                <h4>
                  Investigation Completed
                </h4>

                <div className="confidence">
                  <Activity size={16} />
                  {result.evidence?.length || 0}
                  {" "}evidence indicators
                </div>

              </div>

            </div>

            {result?.status === "completed" && (
              <div className="completion-banner">
                <div className="completion-icon">
                  ✓
                </div>

                <div>
                  <strong>Investigation completed</strong>

                  <span>
                    Threatly correlated the available evidence and
                    generated a deterministic risk assessment.
                  </span>
                </div>
              </div>
            )}

            <section className="reasoning-card">
              <div className="reasoning-header">
                <div>
                  <span className="eyebrow">DECISION TRACE</span>

                  <h3>
                    How Threatly reached this assessment
                  </h3>
                </div>
              </div>

              <div className="reasoning-flow">
                <div className="reasoning-step">
                  <span>01</span>
                  <strong>Detect</strong>
                  <small>
                    Analyze the submitted indicator.
                  </small>
                </div>

                <div className="reasoning-arrow">→</div>

                <div className="reasoning-step">
                  <span>02</span>
                  <strong>Correlate</strong>
                  <small>
                    Convert findings into security evidence.
                  </small>
                </div>

                <div className="reasoning-arrow">→</div>

                <div className="reasoning-step">
                  <span>03</span>
                  <strong>Score</strong>
                  <small>
                    Calculate the deterministic risk score.
                  </small>
                </div>

                <div className="reasoning-arrow">→</div>

                <div className="reasoning-step">
                  <span>04</span>
                  <strong>Explain</strong>
                  <small>
                    Generate an analyst-friendly explanation.
                  </small>
                </div>
              </div>
            </section>

            {result.ocr?.text && (

              <div className="evidence-panel">

                <div className="panel-title">
                  <Image size={19} />
                  OCR Extracted Text
                </div>

                <div className="ocr-text">
                  {result.ocr.text}
                </div>

              </div>

            )}

            <div className="evidence-panel">

              <div className="panel-title">
                <AlertTriangle size={19} />
                Evidence Detected
              </div>

              {result.evidence?.length ? (
                <div className="evidence-list">
                  {result.evidence.map((item) => (

                    <div
                      className="evidence-item"
                      key={item.id}
                    >

                      <div
                        className={`evidence-severity ${getRiskClass(
                          item.severity
                        )}`}
                      >
                        {item.severity}
                      </div>

                      <div className="evidence-body">
                        <strong>{item.title}</strong>

                        <p>{item.description}</p>

                        <small>
                          {item.id} · {item.source}
                        </small>
                      </div>

                    </div>

                  ))}
                </div>
              ) : (
                <p className="empty-state">
                  No strong security indicators detected.
                </p>
              )}

            </div>

            {result?.id && (
              <section className="panel timeline-panel">
                <div className="panel-header">
                  <div>
                    <span className="eyebrow">INVESTIGATION</span>
                    <h2>Investigation Timeline</h2>
                  </div>
                </div>

                <InvestigationTimeline timeline={timeline} />
              </section>
            )}

            {result.id && (

              <div className="ai-report-action">

                <div>
                  <span className="eyebrow">
                    AI INVESTIGATION
                  </span>

                  <h3>
                    Generate Analyst Report
                  </h3>

                  <p>
                    Let Threatly explain the detected evidence,
                    threat classification, and recommended
                    defensive actions.
                  </p>
                </div>

                <button
                  className="report-button"
                  onClick={generateReport}
                  disabled={reportLoading}
                >
                  {reportLoading ? (
                    <>
                      <Activity size={18} />
                      Generating Report...
                    </>
                  ) : (
                    <>
                      <Search size={18} />
                      Generate AI Report
                    </>
                  )}
                </button>

              </div>

            )}

            {report && !report.error && (

              <div className="ai-report">

                <div className="panel-title">
                  <Shield size={19} />
                  AI Investigation Report
                </div>

                <div className="report-section">

                  <span className="card-label">
                    EXECUTIVE SUMMARY
                  </span>

                  <p>
                    {report.executive_summary}
                  </p>

                </div>

                <div className="report-section">

                  <span className="card-label">
                    THREAT ASSESSMENT
                  </span>

                  <p>
                    {report.threat_assessment}
                  </p>

                </div>

                <div className="report-section">

                  <span className="card-label">
                    ATTACK TYPE
                  </span>

                  <div className="attack-type">
                    {report.attack_type}
                  </div>

                </div>

                <div className="report-section">

                  <span className="card-label">
                    KEY FINDINGS
                  </span>

                  <ul className="report-list">

                    {report.key_findings?.map(
                      (finding, index) => (
                        <li key={index}>
                          <CheckCircle size={16} />
                          <span>{finding}</span>
                        </li>
                      )
                    )}

                  </ul>

                </div>

                <div className="report-section">

                  <span className="card-label">
                    RECOMMENDED ACTIONS
                  </span>

                  <ul className="report-list">

                    {report.recommended_actions?.map(
                      (action, index) => (
                        <li key={index}>
                          <AlertTriangle size={16} />
                          <span>{action}</span>
                        </li>
                      )
                    )}

                  </ul>

                </div>

                <div className="analyst-note">

                  <strong>
                    Analyst Note
                  </strong>

                  <p>
                    {report.analyst_note}
                  </p>

                </div>

              </div>

            )}

            {report?.error && (

              <div className="ai-report-error">
                <strong>AI report unavailable</strong>

                <p>{report.error}</p>

                <small>
                  The deterministic Threatly analysis remains available above.
                </small>
              </div>

            )}

            {graph && (

              <div className="graph-panel">

                <div className="panel-title">
                  <Network size={19} />
                  Threat Relationship Graph
                </div>

                <div className="graph-summary">

                  <div>
                    <strong>
                      {graph.nodes?.length || 0}
                    </strong>
                    <span>Nodes</span>
                  </div>

                  <div>
                    <strong>
                      {graph.relationships?.length || 0}
                    </strong>
                    <span>Relationships</span>
                  </div>

                </div>

                <ThreatGraph graph={graph} />

              </div>

            )}

          </section>
        )}

        {result?.error && (

          <div className="error-box">
            <AlertTriangle size={20} />
            {result.error}
          </div>

        )}

          </>

        )}

      </main>

    </div>
  );
}

export default App;
