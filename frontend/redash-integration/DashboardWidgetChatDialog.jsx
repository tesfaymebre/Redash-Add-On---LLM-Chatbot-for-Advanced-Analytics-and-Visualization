/**
 * Modal chat for a dashboard visualization widget (Task 3d).
 *
 * Open via DashboardWidgetChatDialog.showModal({ widget, dashboard }).
 */
import React from "react";
import PropTypes from "prop-types";
import Modal from "antd/lib/modal";
import Button from "antd/lib/button";
import { wrap as wrapDialog, DialogPropType } from "@/components/DialogWrapper";
import VisualizationName from "@/components/visualizations/VisualizationName";
import ChatPanel from "./ChatPanel";
import { buildWidgetChatContext, getBackendUrl } from "./widgetContext";
import "./DashboardWidgetChatDialog.less";

function DashboardWidgetChatDialog({ dialog, widget, dashboard }) {
  const query = widget.getQuery();
  const contextExtras = buildWidgetChatContext(widget, dashboard);

  return (
    <Modal
      {...dialog.props}
      className="dashboard-widget-chat-dialog"
      title={
        <>
          <VisualizationName visualization={widget.visualization} />{" "}
          <span>{query.name}</span>
        </>
      }
      width={720}
      footer={<Button onClick={dialog.dismiss}>Close</Button>}>
      <p className="dashboard-widget-chat-dialog__hint">
        Ask about this chart — the assistant receives the query SQL and a preview of the
        result rows.
      </p>
      <ChatPanel
        key={widget.id}
        contextType="dashboard_widget"
        contextExtras={contextExtras}
        backendUrl={getBackendUrl()}
        title="Widget Assistant"
        placeholder="e.g. Summarize this chart or explain the trend…"
        welcomeMessage={`Hi! I can help explain "${query.name}". What would you like to know about this visualization?`}
      />
    </Modal>
  );
}

DashboardWidgetChatDialog.propTypes = {
  dialog: DialogPropType.isRequired,
  widget: PropTypes.object.isRequired, // eslint-disable-line react/forbid-prop-types
  dashboard: PropTypes.object, // eslint-disable-line react/forbid-prop-types
};

DashboardWidgetChatDialog.defaultProps = {
  dashboard: null,
};

export default wrapDialog(DashboardWidgetChatDialog);
