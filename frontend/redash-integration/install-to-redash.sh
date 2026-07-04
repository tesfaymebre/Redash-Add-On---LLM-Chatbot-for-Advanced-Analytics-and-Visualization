#!/usr/bin/env bash
# Copy chatbot add-on files into a local Redash clone.
#
# Usage:
#   ./frontend/redash-integration/install-to-redash.sh /path/to/redash
#
# Example (Sample project):
#   ./frontend/redash-integration/install-to-redash.sh Sample/redash

set -euo pipefail

REDASH_ROOT="${1:?Usage: $0 /path/to/redash}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRONTEND_SRC="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET="$REDASH_ROOT/client/app/components/chatbot"

echo "Installing chatbot add-on → $TARGET"

mkdir -p "$TARGET"

cp "$FRONTEND_SRC/src/components/ChatPanel.jsx" "$TARGET/"
sed -i '' 's|from "../api/chatClient"|from "./chatClient"|g' "$TARGET/ChatPanel.jsx" 2>/dev/null || \
  sed -i 's|from "../api/chatClient"|from "./chatClient"|g' "$TARGET/ChatPanel.jsx"
cp "$FRONTEND_SRC/src/components/ChatPanel.css" "$TARGET/"
cp "$SCRIPT_DIR/chatClient.js" "$TARGET/"
cp "$SCRIPT_DIR/QueryEditorChatSidebar.jsx" "$TARGET/"
cp "$SCRIPT_DIR/QueryEditorChatSidebar.less" "$TARGET/"
cp "$SCRIPT_DIR/DashboardWidgetChatDialog.jsx" "$TARGET/"
cp "$SCRIPT_DIR/DashboardWidgetChatDialog.less" "$TARGET/"
cp "$FRONTEND_SRC/src/lib/widgetContext.js" "$TARGET/"

# Webpack override — skip eslint-loader on Node 17+ builds
mkdir -p "$REDASH_ROOT/scripts/webpack"
cp "$SCRIPT_DIR/webpack-overrides.js" "$REDASH_ROOT/scripts/webpack/overrides.js"

# Allow yarn build on Node 18+ (Redash expects Node 16)
grep -q 'ignore-engines' "$REDASH_ROOT/.yarnrc" 2>/dev/null || echo 'ignore-engines true' >> "$REDASH_ROOT/.yarnrc"

echo "Copied:"
ls -la "$TARGET"

echo ""
echo "Next steps (manual — see docs/architecture/task-03d-dashboard-widget-chat.md):"
echo "  1. Patch QuerySource.jsx + QuerySource.less (Step 3c)"
echo "  2. Patch VisualizationWidget.jsx (Step 3d)"
echo "  3. Add window.CHATBOT_BACKEND_URL in client/app/config/index.js"
echo "  4. Rebuild Redash client: cd $REDASH_ROOT && yarn build"
