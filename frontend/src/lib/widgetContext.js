/**
 * Build POST /api/chat context for a dashboard widget (Task 3d).
 *
 * @param {object} widget - Redash widget model
 * @param {object} [dashboard] - Redash dashboard model
 * @param {number} [previewRows=5] - Max rows to include in result_preview
 */
export function buildWidgetChatContext(widget, dashboard, previewRows = 5) {
  const query = widget && widget.getQuery ? widget.getQuery() : null;
  const queryResult = widget && widget.getQueryResult ? widget.getQueryResult() : null;

  let resultPreview = null;
  if (queryResult && queryResult.getStatus && queryResult.getStatus() === "done") {
    const data = queryResult.getData ? queryResult.getData() || [] : [];
    const columns = queryResult.getColumns
      ? (queryResult.getColumns() || []).map((col) => col.name)
      : [];

    resultPreview = {
      columns,
      rows: data.slice(0, previewRows),
      total_rows: data.length,
    };
  }

  return {
    dashboard_id: dashboard && dashboard.id ? dashboard.id : null,
    widget_id: widget && widget.id ? widget.id : null,
    query_id: query && query.id ? query.id : null,
    query_name: query && query.name ? query.name : null,
    query_sql: query && query.query ? query.query : null,
    data_source_id: query && query.data_source_id ? query.data_source_id : null,
    visualization_type:
      widget && widget.visualization && widget.visualization.type
        ? widget.visualization.type
        : null,
    visualization_name:
      widget && widget.visualization && widget.visualization.name
        ? widget.visualization.name
        : null,
    result_preview: resultPreview,
  };
}

function getBackendUrl() {
  return window.CHATBOT_BACKEND_URL || "http://localhost:8000";
}

export { getBackendUrl };
