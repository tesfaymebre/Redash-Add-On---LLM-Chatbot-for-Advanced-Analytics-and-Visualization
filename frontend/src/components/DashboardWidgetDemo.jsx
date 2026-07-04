import { useMemo, useState } from "react";
import ChatPanel from "./ChatPanel";
import { CHATBOT_BACKEND_URL } from "../api/chatClient";
import { buildWidgetChatContext } from "../lib/widgetContext";
import "./DashboardWidgetDemo.css";

/** Mock Redash widget for Step 3d dev sandbox. */
function createMockWidget() {
  const resultData = [
    { country_code: "ET", views: 8420 },
    { country_code: "US", views: 5210 },
    { country_code: "GB", views: 3180 },
    { country_code: "DE", views: 2940 },
    { country_code: "IN", views: 2710 },
    { country_code: "CA", views: 2100 },
    { country_code: "FR", views: 1980 },
    { country_code: "AU", views: 1650 },
  ];

  return {
    id: 101,
    visualization: { type: "CHART", name: "Bar Chart" },
    getQuery() {
      return {
        id: 42,
        name: "Top Countries by Views",
        query:
          "SELECT country_code, SUM(views) AS views FROM youtube.dimension_snapshots WHERE snapshot_key = 'Geography' GROUP BY 1 ORDER BY 2 DESC LIMIT 10",
        data_source_id: 1,
      };
    },
    getQueryResult() {
      return {
        getStatus: () => "done",
        getData: () => resultData,
        getColumns: () => [{ name: "country_code" }, { name: "views" }],
      };
    },
  };
}

const mockDashboard = { id: 7, name: "YouTube Channel Overview" };

export default function DashboardWidgetDemo() {
  const [chatOpen, setChatOpen] = useState(false);
  const widget = useMemo(() => createMockWidget(), []);
  const contextExtras = useMemo(
    () => buildWidgetChatContext(widget, mockDashboard),
    [widget],
  );

  return (
    <div className="widget-demo">
      <div className="widget-demo__card">
        <header className="widget-demo__header">
          <h2>Top Countries by Views</h2>
          <span className="widget-demo__viz">Bar Chart</span>
        </header>

        <div className="widget-demo__chart" aria-hidden="true">
          {widget.getQueryResult().getData().slice(0, 5).map((row) => (
            <div key={row.country_code} className="widget-demo__bar-row">
              <span>{row.country_code}</span>
              <div
                className="widget-demo__bar"
                style={{ width: `${(row.views / 8420) * 100}%` }}
              />
              <span>{row.views.toLocaleString()}</span>
            </div>
          ))}
        </div>

        <footer className="widget-demo__footer">
          <button type="button" className="widget-demo__ask" onClick={() => setChatOpen(true)}>
            Ask AI about this chart
          </button>
        </footer>
      </div>

      {chatOpen && (
        <div className="widget-demo__overlay" role="presentation" onClick={() => setChatOpen(false)}>
          <div
            className="widget-demo__modal"
            role="dialog"
            aria-label="Widget chat"
            onClick={(e) => e.stopPropagation()}
          >
            <header className="widget-demo__modal-header">
              <h3>Widget Assistant — Top Countries by Views</h3>
              <button type="button" onClick={() => setChatOpen(false)} aria-label="Close">
                ×
              </button>
            </header>
            <ChatPanel
              key={widget.id}
              contextType="dashboard_widget"
              contextExtras={contextExtras}
              backendUrl={CHATBOT_BACKEND_URL}
              title="Widget Assistant"
              placeholder="e.g. Which country leads and by how much?"
              welcomeMessage='Hi! I can help explain "Top Countries by Views". What would you like to know about this visualization?'
            />
          </div>
        </div>
      )}
    </div>
  );
}
