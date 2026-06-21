#!/bin/bash
#
# Strava MCP Server — Setup Script for Mac
# Run it by opening Terminal and typing:
#   bash ~/Downloads/strava-mcp/setup.sh
#

set -e

GREEN='\033[0;32m'
ORANGE='\033[0;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${BOLD}  Strava MCP Server Setup${NC}"
echo "  =================================="
echo ""

# ── Step 1: Install uv ──────────────────────────────────────────────────────
echo -e "${BOLD}  Step 1: Checking for uv...${NC}"
if command -v uv &>/dev/null; then
    echo -e "  ${GREEN}ok${NC} uv is installed"
else
    echo -e "  ${ORANGE}--${NC} Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    if command -v uv &>/dev/null; then
        echo -e "  ${GREEN}ok${NC} uv installed"
    else
        echo -e "  ${RED}!!${NC} Failed to install uv. Visit https://docs.astral.sh/uv/"
        exit 1
    fi
fi

# ── Step 2: Copy files ──────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}  Step 2: Setting up files...${NC}"
INSTALL_DIR="$HOME/strava-mcp"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$INSTALL_DIR"
cp "$SCRIPT_DIR/strava_server.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/authorize.py" "$INSTALL_DIR/"
echo -e "  ${GREEN}ok${NC} Files saved to ~/strava-mcp/"

# ── Step 3: Strava API credentials ──────────────────────────────────────────
echo ""
echo -e "${BOLD}  Step 3: Strava API Credentials${NC}"
echo ""

if grep -q "PASTE_YOUR_CLIENT_ID_HERE" "$INSTALL_DIR/authorize.py"; then
    echo "  You need a free Strava API application."
    echo ""
    echo "  1. Go to: https://www.strava.com/settings/api"
    echo "  2. Fill in:"
    echo "       Application Name:   Claude MCP"
    echo "       Category:           Other"
    echo "       Website:            http://localhost"
    echo "       Authorization Callback Domain:  localhost"
    echo "  3. Note your Client ID and Client Secret"
    echo ""
    read -p "  Enter your Client ID: " CLIENT_ID
    read -p "  Enter your Client Secret: " CLIENT_SECRET

    if [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ]; then
        echo -e "\n  ${RED}!!${NC} Both Client ID and Client Secret are required."
        exit 1
    fi

    # Only replace the variable assignment lines (not the check or error messages)
    sed -i '' "s/^CLIENT_ID = \"PASTE_YOUR_CLIENT_ID_HERE\"/CLIENT_ID = \"$CLIENT_ID\"/" "$INSTALL_DIR/authorize.py"
    sed -i '' "s/^CLIENT_SECRET = \"PASTE_YOUR_CLIENT_SECRET_HERE\"/CLIENT_SECRET = \"$CLIENT_SECRET\"/" "$INSTALL_DIR/authorize.py"
    echo -e "\n  ${GREEN}ok${NC} Credentials saved"
else
    echo -e "  ${GREEN}ok${NC} Credentials already configured"
    CLIENT_ID=$(grep '^CLIENT_ID = ' "$INSTALL_DIR/authorize.py" | head -1 | cut -d'"' -f2)
    CLIENT_SECRET=$(grep '^CLIENT_SECRET = ' "$INSTALL_DIR/authorize.py" | head -1 | cut -d'"' -f2)
fi

# ── Step 4: Authorize with Strava ───────────────────────────────────────────
echo ""
echo -e "${BOLD}  Step 4: Connecting to Strava...${NC}"
echo ""

if [ -f "$INSTALL_DIR/tokens.json" ]; then
    echo -e "  ${GREEN}ok${NC} Already authorized (tokens.json exists)"
    echo "  To re-authorize, delete ~/strava-mcp/tokens.json and run this again."
else
    echo "  Opening your browser to authorize with Strava..."
    echo "  (Log in and click 'Authorize' when prompted.)"
    echo ""
    uv run --python 3.12 "$INSTALL_DIR/authorize.py"
fi

# ── Step 5: Configure Claude Desktop ────────────────────────────────────────
echo ""
echo -e "${BOLD}  Step 5: Configuring Claude Desktop...${NC}"
echo ""

UV_PATH=$(which uv)
CONFIG_DIR="$HOME/Library/Application Support/Claude"
CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"

mkdir -p "$CONFIG_DIR"

# Write config using Python to avoid JSON escaping issues
python3 << PYEOF
import json
from pathlib import Path

config_file = Path("$CONFIG_FILE")
uv_path = "$UV_PATH"
install_dir = "$INSTALL_DIR"
client_id = "$CLIENT_ID"
client_secret = "$CLIENT_SECRET"

# Load existing config or start fresh
if config_file.exists():
    config = json.loads(config_file.read_text())
else:
    config = {}

if "mcpServers" not in config:
    config["mcpServers"] = {}

config["mcpServers"]["strava"] = {
    "command": uv_path,
    "args": [
        "run",
        "--python", "3.12",
        "--with", "mcp[cli]",
        "--with", "httpx",
        install_dir + "/strava_server.py"
    ],
    "env": {
        "STRAVA_CLIENT_ID": client_id,
        "STRAVA_CLIENT_SECRET": client_secret,
        "STRAVA_TOKENS_PATH": install_dir + "/tokens.json"
    }
}

config_file.write_text(json.dumps(config, indent=2))
print("  Done!")
PYEOF

echo -e "  ${GREEN}ok${NC} Claude Desktop configured"

# ── Done! ───────────────────────────────────────────────────────────────────
echo ""
echo "  =================================="
echo -e "  ${GREEN}${BOLD}All done!${NC}"
echo ""
echo "  Now just:"
echo "  1. Fully quit Claude Desktop (Cmd+Q)"
echo "  2. Reopen Claude Desktop"
echo "  3. Ask Claude: \"What were my last 5 Strava activities?\""
echo ""
echo "  Files: ~/strava-mcp/"
echo "  Config: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo ""
