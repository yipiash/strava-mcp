# Strava MCP for Claude

Talk to Claude about your Strava data — your activities, stats, segments, clubs, gear, routes, and more. Just chat naturally and Claude pulls the data for you.

This is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that connects the **Claude Desktop app** to the **Strava API**. It works on both **Mac and Windows**, with a one-command setup script for each. It runs locally on your machine — your data and your Strava keys never leave your computer.

**Examples of what you can ask:**
- "What were my last 10 rides?"
- "How many km did I run this month?"
- "Show me my heart rate data for yesterday's ride"
- "What are my all-time stats?"
- "Which clubs am I in?"

**Topics this helps with:** Strava + Claude integration · Strava MCP server · chat with your Strava data · query activities, stats & segments in natural language · build a Strava AI assistant · Strava API v3 · Model Context Protocol (MCP).

---

## Features

- Browse your activities with pagination, and get full detail on any single activity
- Create new activities and update existing ones (name, type, description, gear, commute/trainer flags)
- Pull raw activity streams — heart rate, power, cadence, speed, altitude, GPS, temperature, and more
- View activity laps, segment/zone breakdowns, kudos, and comments
- Explore and star segments, browse your starred segments, and analyze your segment efforts over time
- Read athlete profile, all-time and recent stats, and heart-rate / power zones
- Update athlete weight
- Browse clubs you belong to, plus their members, admins, and recent activity feeds
- Look up gear (bikes and shoes) and your saved routes, including route streams
- Check the status of an upload
- Everything runs locally — your Strava Client ID, Secret, and tokens never leave your machine

---

## Tool Coverage

This MCP server implements **31 tools** covering the read and write endpoints of the [Strava API v3](https://developers.strava.com/docs/reference/) that matter for everyday training questions:

- ✅ Athlete & Profile (4 tools) — authenticated athlete, all-time stats, zones, update weight
- ✅ Activities (9 tools) — list, detail, create, update, laps, zones, streams, kudos, comments
- ✅ Segments (8 tools) — get, explore, star, list starred, efforts, effort detail, effort streams, segment streams
- ✅ Clubs (5 tools) — list clubs, club detail, members, admins, activity feed
- ✅ Routes (3 tools) — list routes, route detail, route streams
- ✅ Gear (1 tool) — look up a bike or pair of shoes by gear ID
- ✅ Uploads (1 tool) — check upload status

> **Note:** The data available depends on the OAuth scopes you grant during setup and on your Strava plan. Some fields (such as detailed power and heart-rate streams) require a recording device that captured them. Write actions (creating/updating activities, starring segments) require the matching `activity:write` / `profile:write` scopes, which the setup flow requests by default.

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

Originally built for TeamBDC, but now made public, by Yanur Islam Piash. Shut Up Legs! 🚴
