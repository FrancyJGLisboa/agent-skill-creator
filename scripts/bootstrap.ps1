# bootstrap.ps1 — One-liner bootstrap for agent-skill-creator (Windows)
#
# Usage (PowerShell):
#   irm https://raw.githubusercontent.com/FrancyJGLisboa/agent-skill-creator/main/scripts/bootstrap.ps1 | iex
#
# Usage (Command Prompt):
#   powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/FrancyJGLisboa/agent-skill-creator/main/scripts/bootstrap.ps1 | iex"
#
# Clones agent-skill-creator to ~/.agents/skills/ and creates junctions/symlinks
# to all detected global platforms. Works on PowerShell 5.1+ and PowerShell Core 7+.

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
$RepoUrl    = "https://github.com/FrancyJGLisboa/agent-skill-creator.git"
$SkillName  = "agent-skill-creator"
$HomeDir    = $env:USERPROFILE
$CanonicalDir = Join-Path $HomeDir ".agents" "skills" $SkillName

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
function Write-Info    { param($msg) Write-Host "[INFO]  $msg" -ForegroundColor Blue }
function Write-Ok      { param($msg) Write-Host "[OK]    $msg" -ForegroundColor Green }
function Write-Warn    { param($msg) Write-Host "[WARN]  $msg" -ForegroundColor Yellow }
function Write-Err     { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }

# ---------------------------------------------------------------------------
# Check for git
# ---------------------------------------------------------------------------
function Test-GitInstalled {
    try {
        $null = Get-Command git -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# ---------------------------------------------------------------------------
# Create a directory junction (works without admin on Windows)
# Falls back to copying if junctions fail.
# ---------------------------------------------------------------------------
function New-SkillLink {
    param(
        [string]$Target,
        [string]$LinkPath
    )

    if ($Target -eq $LinkPath) { return }

    $parentDir = Split-Path $LinkPath -Parent
    if (-not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    # Remove existing item
    if (Test-Path $LinkPath) {
        Remove-Item $LinkPath -Recurse -Force
    }

    # Try directory junction first (no admin required)
    try {
        cmd /c mklink /J "`"$LinkPath`"" "`"$Target`"" 2>$null | Out-Null
        if (Test-Path $LinkPath) {
            return
        }
    } catch {}

    # Try symbolic link (may need admin)
    try {
        New-Item -ItemType SymbolicLink -Path $LinkPath -Target $Target -Force | Out-Null
        if (Test-Path $LinkPath) {
            return
        }
    } catch {}

    # Fallback: copy
    Write-Warn "Junction/symlink failed for $LinkPath - falling back to copy"
    Copy-Item -Path $Target -Destination $LinkPath -Recurse -Force
}

# ---------------------------------------------------------------------------
# Detect globally-installed platforms (user-level only)
# ---------------------------------------------------------------------------
function Get-DetectedPlatforms {
    $platforms = @()

    $checks = @(
        @{ Dir = ".claude";          Name = "claude-code"; Display = "Claude Code" },
        @{ Dir = ".copilot";         Name = "copilot";     Display = "GitHub Copilot" },
        @{ Dir = ".gemini";          Name = "gemini";      Display = "Gemini CLI" },
        @{ Dir = ".kiro";            Name = "kiro";        Display = "Kiro" },
        @{ Dir = ".cline";           Name = "cline";       Display = "Cline" },
        @{ Dir = ".roo";             Name = "roo-code";    Display = "Roo Code" },
        @{ Dir = ".kilocode";        Name = "kilo-code";   Display = "Kilo Code" },
        @{ Dir = ".factory";         Name = "factory";     Display = "Factory Droid" },
        @{ Dir = ".cursor";          Name = "cursor";      Display = "Cursor" }
    )

    foreach ($check in $checks) {
        $testPath = Join-Path $HomeDir $check.Dir
        if (Test-Path $testPath) {
            $platforms += $check
        }
    }

    # Config-based paths (Goose, OpenCode)
    $configDir = Join-Path $HomeDir ".config"
    if (Test-Path (Join-Path $configDir "goose")) {
        $platforms += @{ Dir = ".config/goose"; Name = "goose"; Display = "Goose" }
    }
    if (Test-Path (Join-Path $configDir "opencode")) {
        $platforms += @{ Dir = ".config/opencode"; Name = "opencode"; Display = "OpenCode" }
    }

    # Also check Windows-native AppData paths
    $appData = $env:APPDATA
    if ($appData) {
        if (Test-Path (Join-Path $appData "Claude")) {
            # Claude Desktop on Windows
            $platforms += @{ Dir = "AppData/Claude"; Name = "claude-desktop"; Display = "Claude Desktop" }
        }
    }

    return $platforms
}

# ---------------------------------------------------------------------------
# Resolve install path for a platform
# ---------------------------------------------------------------------------
function Get-PlatformPath {
    param([string]$PlatformName)

    switch ($PlatformName) {
        "claude-code"    { return Join-Path $HomeDir ".claude"          "skills" $SkillName }
        "copilot"        { return Join-Path $HomeDir ".copilot"         "skills" $SkillName }
        "gemini"         { return Join-Path $HomeDir ".gemini"          "skills" $SkillName }
        "kiro"           { return Join-Path $HomeDir ".kiro"            "skills" $SkillName }
        "cline"          { return Join-Path $HomeDir ".cline"           "skills" $SkillName }
        "roo-code"       { return Join-Path $HomeDir ".roo"             "skills" $SkillName }
        "kilo-code"      { return Join-Path $HomeDir ".kilocode"        "skills" $SkillName }
        "factory"        { return Join-Path $HomeDir ".factory"         "skills" $SkillName }
        "cursor"         { return Join-Path $HomeDir ".cursor"          "rules"  $SkillName }
        "goose"          { return Join-Path $HomeDir ".config" "goose"    "skills" $SkillName }
        "opencode"       { return Join-Path $HomeDir ".config" "opencode" "skills" $SkillName }
        default          { return Join-Path $HomeDir ".agents"          "skills" $SkillName }
    }
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
function Main {
    Write-Host ""
    Write-Host "Agent Skill Creator - Bootstrap Installer (Windows)" -ForegroundColor White -NoNewline
    Write-Host ""
    Write-Host ""

    # Check for git
    if (-not (Test-GitInstalled)) {
        Write-Err "git is not installed."
        Write-Host ""
        Write-Host "Install git from: https://git-scm.com/downloads/win" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Or with winget:  winget install Git.Git" -ForegroundColor Yellow
        Write-Host "Or with choco:   choco install git" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }

    # Clone or update the canonical location
    if (Test-Path (Join-Path $CanonicalDir ".git")) {
        Write-Info "Updating existing install at $CanonicalDir"
        Push-Location $CanonicalDir
        try { git pull --ff-only 2>$null } catch {}
        Pop-Location
    } else {
        Write-Info "Cloning $SkillName to $CanonicalDir"
        $parentDir = Split-Path $CanonicalDir -Parent
        if (-not (Test-Path $parentDir)) {
            New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
        }
        if (Test-Path $CanonicalDir) {
            Remove-Item $CanonicalDir -Recurse -Force
        }
        git clone $RepoUrl $CanonicalDir
        if ($LASTEXITCODE -ne 0) {
            Write-Err "git clone failed. Check your internet connection and try again."
            exit 1
        }
    }

    Write-Ok "Installed at $CanonicalDir"

    # Detect global platforms and create junctions
    $platforms = Get-DetectedPlatforms
    $count = 0

    foreach ($platform in $platforms) {
        $dest = Get-PlatformPath $platform.Name
        New-SkillLink -Target $CanonicalDir -LinkPath $dest
        Write-Ok "Linked for $($platform.Display) -> $dest"
        $count++
    }

    # ---------------------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------------------
    Write-Host ""
    Write-Host "Done!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Canonical location: $CanonicalDir"

    if ($count -gt 0) {
        $names = ($platforms | ForEach-Object { $_.Display }) -join ", "
        Write-Host "  Linked to $count platform(s): $names"
    }

    Write-Host ""
    Write-Host "How to use:" -ForegroundColor White
    Write-Host "  Open your AI agent and type:"
    Write-Host "    /agent-skill-creator <describe your workflow>"
    Write-Host ""
    Write-Host "  To update later:"
    Write-Host "    cd $CanonicalDir; git pull"
    Write-Host ""

    if ($count -eq 0) {
        Write-Warn "No global platforms detected. The skill is installed at the universal path."
        Write-Host "  Tools like Codex CLI, Gemini CLI, Kiro, and others"
        Write-Host "  read from ~/.agents/skills/ automatically."
        Write-Host ""
    }
}

Main
