/**
 * Redash-aware chat sidebar for the query editor (Task 3c).
 *
 * Copy to: redash/client/app/components/chatbot/QueryEditorChatSidebar.jsx
 *
 * Props:
 *   query          - Redash query model (needs .query, .id, .data_source_id)
 *   onQueryChange  - callback(sql) to update Ace editor content
 *   dataSourceId   - active data source id
 */
import React, { useCallback, useState } from "react";
import PropTypes from "prop-types";
import ChatPanel from "./ChatPanel";
import "./QueryEditorChatSidebar.less";

function getBackendUrl() {
  // Set in redash/client/app/config/index.js (see integration guide)
  return window.CHATBOT_BACKEND_URL || "http://localhost:8000";
}

export default function QueryEditorChatSidebar({ query, onQueryChange, dataSourceId }) {
  const [open, setOpen] = useState(true);

  const handleSqlGenerated = useCallback(
    (sql) => {
      if (sql && onQueryChange) {
        onQueryChange(sql);
      }
    },
    [onQueryChange],
  );

  const contextExtras = {
    query_id: query && query.id ? query.id : null,
    query_sql: query && query.query ? query.query : null,
    data_source_id: dataSourceId || (query && query.data_source_id ? query.data_source_id : null),
  };

  return (
    <div className={`query-editor-chat ${open ? "query-editor-chat--open" : "query-editor-chat--collapsed"}`}>
      <button
        type="button"
        className="query-editor-chat__toggle"
        onClick={() => setOpen((v) => !v)}
        title={open ? "Hide assistant" : "Show assistant"}
        aria-expanded={open}>
        {open ? "›" : "‹"} AI
      </button>

      {open && (
        <div className="query-editor-chat__panel">
          <ChatPanel
            contextType="query_editor"
            contextExtras={contextExtras}
            backendUrl={getBackendUrl()}
            title="Query Assistant"
            placeholder="Ask in plain English…"
            onSqlGenerated={handleSqlGenerated}
          />
        </div>
      )}
    </div>
  );
}

QueryEditorChatSidebar.propTypes = {
  query: PropTypes.shape({
    id: PropTypes.number,
    query: PropTypes.string,
    data_source_id: PropTypes.number,
  }),
  onQueryChange: PropTypes.func.isRequired,
  dataSourceId: PropTypes.number,
};

QueryEditorChatSidebar.defaultProps = {
  query: null,
  dataSourceId: null,
};
