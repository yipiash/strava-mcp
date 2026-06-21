# Strava MCP for Claude

Talk to Claude about your Strava data — your activities, stats, segments, clubs, gear, routes, and more. Just chat naturally and Claude pulls the data for you.

This is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that connects the **Claude Desktop app** to the **Strava API**. It runs locally on your machine — your data and your Strava keys never leave your computer.

**Examples of what you can ask:**
- "What were my last 10 rides?"
- "How many km did I run this month?"
- "Show me my heart rate data for yesterday's ride"
- "What are my all-time stats?"
- "Which clubs am I in?"

---

## What You Need

- **Claude Desktop app** (free download from [claude.ai/download](https://claude.ai/download))
- **A Strava account** (free or paid — both work)
- **A Claude account** (free plan works with 1 custom connector; Pro/Max gives unlimited)
- ~5 minutes

You do **not** need Python installed, coding experience, or any technical knowledge. The setup script handles everything automatically (it installs [`uv`](https://docs.astral.sh/uv/), which manages Python for you).

---

## Get the Code

Pick whichever is easiest:

- **Download ZIP:** Click the green **Code** button at the top of this page → **Download ZIP**, then unzip it.
- **Or clone with git:**
  ```
  git clone https://github.com/yipiash/strava-mcp.git
  ```

Either way you'll end up with a folder called `strava-mcp`.

---

## Setup (Mac)

### Step 1: Get the folder ready

Move the `strava-mcp` folder into your **Downloads** folder so it's at:

```
~/Downloads/strava-mcp/
```

### Step 2: Open Terminal

Press **Cmd + Space**, type **Terminal**, press **Enter**.

You'll see a window with a blinking cursor. This is where you'll paste the command in the next step.

### Step 3: Run the setup

Copy this line, paste it into Terminal, and press **Enter**:

```
bash ~/Downloads/strava-mcp/setup.sh
```

### Step 4: Create your Strava API app

The script will ask for a **Client ID** and **Client Secret**. To get these:

1. Go to [strava.com/settings/api](https://www.strava.com/settings/api) in your browser
2. You'll see a form to create an API application. Fill it in:
   - **Application Name:** `Claude MCP`
   - **Category:** `Other`
   - **Website:** `http://localhost`
   - **Authorization Callback Domain:** `localhost`
3. Click **Create**
4. The page will now show your **Client ID** (a number) and **Client Secret** (a long string of letters and numbers)
5. Go back to Terminal and paste them when prompted

### Step 5: Authorize with Strava

The script will automatically open your browser to a Strava page. Click **Authorize**. You'll see a "Connected to Strava!" message. Close that tab.

### Step 6: Restart Claude Desktop

Fully quit Claude Desktop (**Cmd + Q** — not just close the window) and reopen it.

### Step 7: Try it!

Open a new conversation and ask:

> "What were my last 5 Strava activities?"

---

## Setup (Windows)

### Step 1: Get the folder ready

Move the `strava-mcp` folder into your **Downloads** folder so it's at:

```
C:\Users\YourName\Downloads\strava-mcp\
```

### Step 2: Run the setup

Open the `strava-mcp` folder and double-click **`setup-windows.bat`**.

If Windows asks "Do you want to allow this app to make changes?" — click **Yes**.

### Step 3: Create your Strava API app

The script will ask for a **Client ID** and **Client Secret**. To get these:

1. Go to [strava.com/settings/api](https://www.strava.com/settings/api) in your browser
2. You'll see a form to create an API application. Fill it in:
   - **Application Name:** `Claude MCP`
   - **Category:** `Other`
   - **Website:** `http://localhost`
   - **Authorization Callback Domain:** `localhost`
3. Click **Create**
4. The page will now show your **Client ID** (a number) and **Client Secret** (a long string of letters and numbers)
5. Go back to the setup window and type them in when prompted

### Step 4: Authorize with Strava

The script will automatically open your browser to a Strava page. Click **Authorize**. You'll see a "Connected to Strava!" message. Close that tab.

### Step 5: Restart Claude Desktop

Fully close Claude Desktop and reopen it.

### Step 6: Try it!

Open a new conversation and ask:

> "What were my last 5 Strava activities?"

---

## What's in this repo

| File | What it does |
|------|--------------|
| `strava_server.py` | The MCP server — exposes Strava API v3 endpoints as tools Claude can call |
| `authorize.py` | One-time Strava OAuth flow; saves your tokens locally to `tokens.json` |
| `setup.sh` | Mac installer — installs `uv`, copies files, runs auth, configures Claude Desktop |
| `setup-windows.bat` | Windows installer (same as above) |
| `configure-claude.ps1` | Helper used by the Windows installer to write the Claude Desktop config |

---

## Privacy & Security

- Everything runs **locally** on your computer. Your Strava data is sent only between your machine and Strava's official API.
- Your **Client ID**, **Client Secret**, and **access tokens** are stored locally (in your Claude Desktop config and a `tokens.json` file in your install folder). They are **never** committed to this repo — `tokens.json` is gitignored, and the `authorize.py` in this repo contains only placeholders.
- **Never share your `tokens.json` or your Client Secret**, and never paste them into a public issue or pull request.
- To disconnect, delete `~/strava-mcp/tokens.json` (Mac) and remove the `strava` entry from your Claude Desktop config, or revoke access at [strava.com/settings/apps](https://www.strava.com/settings/apps).

---

## Troubleshooting

- **Claude doesn't see Strava tools:** Make sure you fully quit Claude Desktop (Cmd+Q / right‑click → Quit) and reopened it.
- **"Not authenticated" errors:** Delete `~/strava-mcp/tokens.json` and re-run the setup script to re-authorize.
- **Rate limits:** Strava's API has rate limits (200 requests/15 min, 2,000/day by default). If you hit them, wait a bit and try again.

---

## License

[MIT](LICENSE) © Yanur Islam Piash

---

Built for TeamBDC, by Yanur Islam Piash. Shut Up Legs! 🚴
