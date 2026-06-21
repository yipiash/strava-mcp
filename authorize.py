#!/usr/bin/env python3
"""
One-time Strava OAuth Authorization
Run this script once to connect your Strava account.
"""

import json
import webbrowser
import http.server
import urllib.parse
import urllib.request
from pathlib import Path

# ── You fill these in during setup ──────────────────────────────────────────
CLIENT_ID = "PASTE_YOUR_CLIENT_ID_HERE"
CLIENT_SECRET = "PASTE_YOUR_CLIENT_SECRET_HERE"
# ────────────────────────────────────────────────────────────────────────────

REDIRECT_PORT = 5478
REDIRECT_URI = "http://localhost:" + str(REDIRECT_PORT)
TOKENS_FILE = Path(__file__).parent / "tokens.json"
SCOPES = "read,read_all,profile:read_all,profile:write,activity:read,activity:read_all,activity:write"

AUTH_URL = (
    "https://www.strava.com/oauth/authorize"
    "?client_id=" + CLIENT_ID
    + "&redirect_uri=" + REDIRECT_URI
    + "&response_type=code"
    + "&approval_prompt=auto"
    + "&scope=" + SCOPES
)


class OAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)

        if "code" not in params:
            self.send_response(400)
            self.end_headers()
            self.wfile.write("Authorization failed - no code received.".encode())
            self.server.auth_code = None
            return

        self.server.auth_code = params["code"][0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(
            b"<html><body style='font-family:-apple-system,sans-serif;display:flex;"
            b"justify-content:center;align-items:center;height:100vh;margin:0;"
            b"background:#f5f5f5;'><div style='text-align:center;padding:40px;"
            b"background:white;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.1);'>"
            b"<h1 style='color:#fc4c02;'>Connected to Strava!</h1>"
            b"<p style='color:#666;font-size:18px;'>You can close this tab and go back to Claude Desktop.</p>"
            b"</div></body></html>"
        )

    def log_message(self, format, *args):
        pass


def exchange_code_for_tokens(code):
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }).encode()
    req = urllib.request.Request("https://www.strava.com/oauth/token", data=data)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def main():
    # Check if credentials are still placeholders
    if "PASTE_YOUR_CLIENT_ID_HERE" in CLIENT_ID:
        print("")
        print("  You need to add your Strava API credentials first!")
        print("  Open this file (authorize.py) in TextEdit and replace:")
        print("    - PASTE_YOUR_CLIENT_ID_HERE      with your Client ID")
        print("    - PASTE_YOUR_CLIENT_SECRET_HERE   with your Client Secret")
        print("")
        print("  Get these from: https://www.strava.com/settings/api")
        print("")
        return

    print("")
    print("  Strava Authorization")
    print("  " + "=" * 38)
    print("")
    print("  Opening Strava in your browser...")
    print("  (If it doesn't open, copy this URL into your browser:)")
    print("")
    print("  " + AUTH_URL)
    print("")

    webbrowser.open(AUTH_URL)

    server = http.server.HTTPServer(("localhost", REDIRECT_PORT), OAuthHandler)
    server.auth_code = None
    server.handle_request()

    if not server.auth_code:
        print("  Authorization failed. Please try again.")
        return

    print("  Exchanging code for tokens...")
    tokens = exchange_code_for_tokens(server.auth_code)
    TOKENS_FILE.write_text(json.dumps(tokens, indent=2))

    athlete = tokens.get("athlete", {})
    name = (athlete.get("firstname", "") + " " + athlete.get("lastname", "")).strip()

    print("")
    print("  Success! Connected as: " + (name or "Strava Athlete"))
    print("  Tokens saved to: " + str(TOKENS_FILE))
    print("")
    print("  You're all set! Quit and reopen Claude Desktop now.")
    print("")


if __name__ == "__main__":
    main()
