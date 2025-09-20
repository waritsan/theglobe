#!/bin/bash
echo "Clearing VS Code workspace cache..."
rm -rf .vscode/settings.json 2>/dev/null || true
mkdir -p .vscode
cat > .vscode/settings.json << EOF
{
    "bicep.enablePreviewFeatures": false,
    "bicep.trace.server": "off"
}
EOF
echo "VS Code settings reset. Please reload VS Code window."

