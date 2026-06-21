@echo off
setlocal enabledelayedexpansion

echo.
echo   Strava MCP Server Setup (Windows)
echo   ==================================
echo.

:: ── Step 1: Install uv ─────────────────────────────────────────────────────
echo   Step 1: Checking for uv...
where uv >nul 2>nul
if %errorlevel%==0 (
    echo   [ok] uv is installed
) else (
    echo   [..] Installing uv...
    powershell -ExecutionPolicy ByPass -NoProfile -Command "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
    where uv >nul 2>nul
    if !errorlevel!==0 (
        echo   [ok] uv installed
    ) else (
        echo   [!!] Failed to install uv.
        echo        Close this window, reopen it, and try again.
        echo        If it still fails, visit https://docs.astral.sh/uv/
        pause
        exit /b 1
    )
)

:: ── Step 2: Copy files ─────────────────────────────────────────────────────
echo.
echo   Step 2: Setting up files...
set "INSTALL_DIR=%USERPROFILE%\strava-mcp"
set "SCRIPT_DIR=%~dp0"

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
copy /y "%SCRIPT_DIR%strava_server.py" "%INSTALL_DIR%\" >nul
copy /y "%SCRIPT_DIR%authorize.py" "%INSTALL_DIR%\" >nul
echo   [ok] Files saved to %INSTALL_DIR%

:: ── Step 3: Strava API credentials ─────────────────────────────────────────
echo.
echo   Step 3: Strava API Credentials
echo.

findstr /c:"PASTE_YOUR_CLIENT_ID_HERE" "%INSTALL_DIR%\authorize.py" >nul 2>nul
if %errorlevel%==0 (
    echo   You need a free Strava API application.
    echo.
    echo   1. Go to: https://www.strava.com/settings/api
    echo   2. Fill in:
    echo        Application Name:   Claude MCP
    echo        Category:           Other
    echo        Website:            http://localhost
    echo        Authorization Callback Domain:  localhost
    echo   3. Note your Client ID and Client Secret
    echo.
    set /p CLIENT_ID="  Enter your Client ID: "
    set /p CLIENT_SECRET="  Enter your Client Secret: "

    if "!CLIENT_ID!"=="" (
        echo   [!!] Client ID is required.
        pause
        exit /b 1
    )
    if "!CLIENT_SECRET!"=="" (
        echo   [!!] Client Secret is required.
        pause
        exit /b 1
    )

    rem Replace placeholders in authorize.py - only the variable lines.
    rem Uses delayed expansion exclamation-VAR-exclamation; percent-VAR-percent would be empty here.
    powershell -Command "(Get-Content '%INSTALL_DIR%\authorize.py') -replace '^CLIENT_ID = \"PASTE_YOUR_CLIENT_ID_HERE\"', 'CLIENT_ID = \"!CLIENT_ID!\"' | Set-Content '%INSTALL_DIR%\authorize.py'"
    powershell -Command "(Get-Content '%INSTALL_DIR%\authorize.py') -replace '^CLIENT_SECRET = \"PASTE_YOUR_CLIENT_SECRET_HERE\"', 'CLIENT_SECRET = \"!CLIENT_SECRET!\"' | Set-Content '%INSTALL_DIR%\authorize.py'"
    echo.
    echo   [ok] Credentials saved
) else (
    echo   [ok] Credentials already configured
    for /f "tokens=3 delims= " %%a in ('findstr /b "CLIENT_ID = " "%INSTALL_DIR%\authorize.py"') do set "CLIENT_ID=%%~a"
    for /f "tokens=3 delims= " %%a in ('findstr /b "CLIENT_SECRET = " "%INSTALL_DIR%\authorize.py"') do set "CLIENT_SECRET=%%~a"
)

:: ── Step 4: Authorize with Strava ──────────────────────────────────────────
echo.
echo   Step 4: Connecting to Strava...
echo.

if exist "%INSTALL_DIR%\tokens.json" (
    echo   [ok] Already authorized (tokens.json exists)
    echo   To re-authorize, delete %INSTALL_DIR%\tokens.json and run this again.
) else (
    echo   Opening your browser to authorize with Strava...
    echo   (Log in and click 'Authorize' when prompted.)
    echo.
    uv run --python 3.12 "%INSTALL_DIR%\authorize.py"
)

:: ── Step 5: Configure Claude Desktop ───────────────────────────────────────
echo.
echo   Step 5: Configuring Claude Desktop...
echo.

:: Find uv path
for /f "tokens=*" %%i in ('where uv') do set "UV_PATH=%%i"
set "CONFIG_DIR=%APPDATA%\Claude"
set "CONFIG_FILE=%CONFIG_DIR%\claude_desktop_config.json"

if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

:: Use PowerShell to write the config - PowerShell is always present on Windows 10/11.
:: Calls configure-claude.ps1 which sits next to this bat file.
powershell -ExecutionPolicy Bypass -NoProfile -File "%SCRIPT_DIR%configure-claude.ps1" -InstallDir "%INSTALL_DIR%" -ConfigFile "%CONFIG_FILE%" -UvPath "%UV_PATH%" -ClientId "%CLIENT_ID%" -ClientSecret "%CLIENT_SECRET%"

if errorlevel 1 (
    echo.
    echo   [!!] Failed to write Claude Desktop config.
    echo        See the error above. Aborting before claiming success.
    pause
    exit /b 1
)

echo   [ok] Claude Desktop configured

:: ── Done! ──────────────────────────────────────────────────────────────────
echo.
echo   ==================================
echo   All done!
echo.
echo   Now just:
echo   1. Fully quit Claude Desktop
echo   2. Reopen Claude Desktop
echo   3. Ask Claude: "What were my last 5 Strava activities?"
echo.
echo   Files: %INSTALL_DIR%
echo   Config: %CONFIG_FILE%
echo.
pause
