# install.ps1 — Link agent-skill-creator to all detected global platforms (Windows)
#
# For users who already cloned the repo. Creates directory junctions so
# `git pull` in the cloned directory updates all tools automatically.
#
# Usage:
#   .\install.ps1              # Link to all detected platforms
#   .\install.ps1 -DryRun     # Preview without making changes
#   .\install.ps1 -Uninstall  # Remove all links pointing to this repo

param(
    [switch]$DryRun,
    [switch]$Uninstall,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
$SkillName = "agent-skill-creator"
$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$HomeDir = $env:USERPROFILE

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
function Write-Info    { param($msg) Write-Host "[INFO]  $msg" -ForegroundColor Blue }
function Write-Ok      { param($msg) Write-Host "[OK]    $msg" -ForegroundColor Green }
function Write-Warn    { param($msg) Write-Host "[WARN]  $msg" -ForegroundColor Yellow }
function Write-Err     { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
if ($Help) {
    Write-Host @"
install.ps1 — Link agent-skill-creator to all detected platforms

USAGE
    .\install.ps1 [-DryRun] [-Uninstall] [-Help]

OPTIONS
    -DryRun      Preview without making changes
    -Uninstall   Remove all links pointing to this repo
    -Help        Show this help message
"@
    exit 0
}

# ---------------------------------------------------------------------------
# All global platform paths (user-level only)
# ---------------------------------------------------------------------------
function Get-AllPlatformEntries {
    return @(
        @{ DetectDir = ".claude";          InstallPath = ".claude\skills\$SkillName";          Display = "Claude Code" },
        @{ DetectDir = ".copilot";         InstallPath = ".copilot\skills\$SkillName";         Display = "GitHub Copilot" },
        @{ DetectDir = ".gemini";          InstallPath = ".gemini\skills\$SkillName";          Display = "Gemini CLI" },
        @{ DetectDir = ".kiro";            InstallPath = ".kiro\skills\$SkillName";            Display = "Kiro" },
        @{ DetectDir = ".cline";           InstallPath = ".cline\skills\$SkillName";           Display = "Cline" },
        @{ DetectDir = ".roo";             InstallPath = ".roo\skills\$SkillName";             Display = "Roo Code" },
        @{ DetectDir = ".kilocode";        InstallPath = ".kilocode\skills\$SkillName";        Display = "Kilo Code" },
        @{ DetectDir = ".factory";         InstallPath = ".factory\skills\$SkillName";         Display = "Factory Droid" },
        @{ DetectDir = ".cursor";          InstallPath = ".cursor\rules\$SkillName";           Display = "Cursor" },
        @{ DetectDir = ".config\goose";    InstallPath = ".config\goose\skills\$SkillName";    Display = "Goose" },
        @{ DetectDir = ".config\opencode"; InstallPath = ".config\opencode\skills\$SkillName"; Display = "OpenCode" }
    )
}

# ---------------------------------------------------------------------------
# Create a directory junction (works without admin)
# ---------------------------------------------------------------------------
function New-SkillLink {
    param([string]$Target, [string]$LinkPath)

    if ($Target -eq $LinkPath) { return }

    $parentDir = Split-Path $LinkPath -Parent
    if (-not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    if (Test-Path $LinkPath) {
        Remove-Item $LinkPath -Recurse -Force
    }

    try {
        cmd /c mklink /J "`"$LinkPath`"" "`"$Target`"" 2>$null | Out-Null
        if (Test-Path $LinkPath) { return }
    } catch {}

    try {
        New-Item -ItemType SymbolicLink -Path $LinkPath -Target $Target -Force | Out-Null
        if (Test-Path $LinkPath) { return }
    } catch {}

    Write-Warn "Junction/symlink failed for $LinkPath - falling back to copy"
    Copy-Item -Path $Target -Destination $LinkPath -Recurse -Force
}

# ---------------------------------------------------------------------------
# Check if a path is a junction/symlink pointing to our repo
# ---------------------------------------------------------------------------
function Test-IsOurLink {
    param([string]$TestPath)

    if (-not (Test-Path $TestPath)) { return $false }

    $item = Get-Item $TestPath -Force
    if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
        $target = $item.Target
        if ($target -and ($target -eq $RepoDir)) { return $true }
    }
    return $false
}

# ---------------------------------------------------------------------------
# Uninstall
# ---------------------------------------------------------------------------
function Remove-AllLinks {
    Write-Host ""
    Write-Host "Uninstalling agent-skill-creator links" -ForegroundColor White
    Write-Host ""

    # Check canonical location
    $canonical = Join-Path $HomeDir ".agents\skills\$SkillName"
    if (Test-IsOurLink $canonical) {
        if ($DryRun) {
            Write-Info "[dry-run] Would remove: $canonical"
        } else {
            Remove-Item $canonical -Recurse -Force
            Write-Ok "Removed: $canonical"
        }
    }

    # Check each platform path
    $entries = Get-AllPlatformEntries
    foreach ($entry in $entries) {
        $dest = Join-Path $HomeDir $entry.InstallPath
        if (Test-IsOurLink $dest) {
            if ($DryRun) {
                Write-Info "[dry-run] Would remove: $dest"
            } else {
                Remove-Item $dest -Recurse -Force
                Write-Ok "Removed: $dest ($($entry.Display))"
            }
        }
    }

    if ($DryRun) {
        Write-Host ""
        Write-Warn "Dry run - no changes made."
    } else {
        Write-Host ""
        Write-Host "Done. Links removed."
    }
}

# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------
function Install-AllLinks {
    Write-Host ""
    Write-Host "Agent Skill Creator - Link Installer (Windows)" -ForegroundColor White
    Write-Host ""
    Write-Info "Source: $RepoDir"

    $count = 0

    # Always install to canonical location
    $canonical = Join-Path $HomeDir ".agents\skills\$SkillName"
    if ($DryRun) {
        Write-Info "[dry-run] Would link: $canonical -> $RepoDir"
    } else {
        New-SkillLink -Target $RepoDir -LinkPath $canonical
        Write-Ok "Canonical: $canonical"
    }
    $count++

    # Install to each detected global platform
    $entries = Get-AllPlatformEntries
    foreach ($entry in $entries) {
        $detectPath = Join-Path $HomeDir $entry.DetectDir
        if (Test-Path $detectPath) {
            $dest = Join-Path $HomeDir $entry.InstallPath
            if ($DryRun) {
                Write-Info "[dry-run] Would link: $dest -> $RepoDir ($($entry.Display))"
            } else {
                New-SkillLink -Target $RepoDir -LinkPath $dest
                Write-Ok "Linked for $($entry.Display) -> $dest"
            }
            $count++
        }
    }

    # Summary
    Write-Host ""
    Write-Host "Done!" -ForegroundColor Green
    Write-Host ""

    if ($DryRun) {
        Write-Warn "Dry run - no changes made."
        Write-Host ""
    } else {
        Write-Host "  Links point to: $RepoDir"
        Write-Host "  Run 'git pull' from that directory to update all tools."
        Write-Host ""
    }

    Write-Host "How to use:" -ForegroundColor White
    Write-Host "  Open your AI agent and type:"
    Write-Host "    /agent-skill-creator <describe your workflow>"
    Write-Host ""
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if ($Uninstall) {
    Remove-AllLinks
} else {
    Install-AllLinks
}
