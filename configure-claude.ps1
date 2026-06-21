param(
    [Parameter(Mandatory=$true)][string]$InstallDir,
    [Parameter(Mandatory=$true)][string]$ConfigFile,
    [Parameter(Mandatory=$true)][string]$UvPath,
    [Parameter(Mandatory=$true)][string]$ClientId,
    [Parameter(Mandatory=$true)][string]$ClientSecret
)

$ErrorActionPreference = 'Stop'

$configDir = Split-Path -Parent $ConfigFile
if (-not (Test-Path $configDir)) {
    New-Item -Path $configDir -ItemType Directory -Force | Out-Null
}

if (Test-Path $ConfigFile) {
    $raw = Get-Content -Path $ConfigFile -Raw
    # Strip UTF-8 BOM if present - any prior PS5 write may have added one.
    if ($raw.Length -gt 0 -and $raw[0] -eq [char]0xFEFF) {
        $raw = $raw.Substring(1)
    }
    if ([string]::IsNullOrWhiteSpace($raw)) {
        $config = [pscustomobject]@{}
    } else {
        $config = $raw | ConvertFrom-Json
    }
} else {
    $config = [pscustomobject]@{}
}

if (-not ($config.PSObject.Properties.Name -contains 'mcpServers')) {
    $config | Add-Member -MemberType NoteProperty -Name 'mcpServers' -Value ([pscustomobject]@{})
}

$stravaEntry = [pscustomobject]@{
    command = $UvPath
    args = @(
        'run',
        '--python', '3.12',
        '--with', 'mcp[cli]',
        '--with', 'httpx',
        (Join-Path $InstallDir 'strava_server.py')
    )
    env = [pscustomobject]@{
        STRAVA_CLIENT_ID     = $ClientId
        STRAVA_CLIENT_SECRET = $ClientSecret
        STRAVA_TOKENS_PATH   = (Join-Path $InstallDir 'tokens.json')
    }
}

if ($config.mcpServers.PSObject.Properties.Name -contains 'strava') {
    $config.mcpServers.strava = $stravaEntry
} else {
    $config.mcpServers | Add-Member -MemberType NoteProperty -Name 'strava' -Value $stravaEntry
}

$json = $config | ConvertTo-Json -Depth 10
# Write UTF-8 WITHOUT BOM. PS5's Set-Content -Encoding UTF8 adds a BOM that
# Claude Desktop's JSON parser refuses. Use .NET directly to be explicit.
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($ConfigFile, $json, $utf8NoBom)
Write-Host "  Done!"
