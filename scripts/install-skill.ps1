# install-skill.ps1 — Install any skill (git URL or local path) to all detected platforms (Windows)
#
# Usage:
#   .\scripts\install-skill.ps1 https://github.com/someone/sales-report-skill.git
#   .\scripts\install-skill.ps1 .\sales-report-skill
#   .\scripts\install-skill.ps1 .\sales-report-skill -Platform cursor -Project
#   .\scripts\install-skill.ps1 .\sales-report-skill -DryRun
#   .\scripts\install-skill.ps1 .\sales-report-skill -Uninstall
#
# Works on PowerShell 5.1+ and PowerShell Core 7+.

param(
    [Parameter(Position=0)]
    [string]$Source = "",

    [string]$Platform = "",
    [switch]$Project,
    [switch]$DryRun,
    [switch]$Uninstall,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
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
install-skill.ps1 — Install any skill to all detected platforms

USAGE
    .\install-skill.ps1 <source> [OPTIONS]

ARGUMENTS
    <source>            Git URL (https://... or *.git) or local directory path

OPTIONS
    -Platform <name>    Install to a specific platform only
    -Project            Use project-level paths (for Cursor, Windsurf, etc.)
    -DryRun             Preview without making changes
    -Uninstall          Remove the skill from all platforms
    -Help               Show this help message

EXAMPLES
    .\install-skill.ps1 https://github.com/someone/sales-report-skill.git
    .\install-skill.ps1 .\sales-report-skill
    .\install-skill.ps1 .\sales-report-skill -Platform cursor -Project
"@
    exit 0
}

if (-not $Source) {
    Write-Err "Missing required argument: <source>"
    Write-Host "Usage: .\install-skill.ps1 <source> [options]"
    Write-Host "Use -Help for full usage information."
    exit 1
}

# ---------------------------------------------------------------------------
# Resolve source: git clone or validate local path
# ---------------------------------------------------------------------------
function Test-GitUrl {
    param([string]$Url)
    return ($Url -match "://") -or ($Url -match "\.git$")
}

$SourceDir = ""
$SkillName = ""

function Resolve-Source {
    $script:SourceDir = ""

    if (Test-GitUrl $Source) {
        $skillBasename = [System.IO.Path]::GetFileNameWithoutExtension($Source)
        if ($skillBasename -eq "") { $skillBasename = ($Source -split "/")[-1] -replace "\.git$","" }
        $canonicalDir = Join-Path $HomeDir ".agents\skills\$skillBasename"

        if (Test-Path (Join-Path $canonicalDir ".git")) {
            Write-Info "Updating existing install at $canonicalDir"
            if (-not $DryRun) {
                Push-Location $canonicalDir
                try { git pull --ff-only 2>$null } catch {}
                Pop-Location
            }
        } else {
            Write-Info "Cloning $Source"
            if (-not $DryRun) {
                $parentDir = Split-Path $canonicalDir -Parent
                if (-not (Test-Path $parentDir)) {
                    New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
                }
                if (Test-Path $canonicalDir) {
                    Remove-Item $canonicalDir -Recurse -Force
                }
                git clone $Source $canonicalDir
                if ($LASTEXITCODE -ne 0) {
                    Write-Err "git clone failed."
                    exit 1
                }
            }
        }
        $script:SourceDir = $canonicalDir
    } else {
        if (-not (Test-Path $Source)) {
            Write-Err "Source directory not found: $Source"
            exit 1
        }
        $script:SourceDir = (Resolve-Path $Source).Path
    }
}

# ---------------------------------------------------------------------------
# Extract skill name
# ---------------------------------------------------------------------------
function Get-SkillName {
    $skillMd = Join-Path $script:SourceDir "SKILL.md"
    $name = ""

    if (Test-Path $skillMd) {
        $lines = Get-Content $skillMd -TotalCount 30
        $inFm = $false
        foreach ($line in $lines) {
            if (-not $inFm -and $line -eq "---") { $inFm = $true; continue }
            if ($inFm -and $line -eq "---") { break }
            if ($inFm -and $line -match "^name:\s*[`"']?([^`"']+)[`"']?\s*$") {
                $name = $Matches[1].Trim()
            }
        }
    }

    if (-not $name) {
        $name = Split-Path $script:SourceDir -Leaf
    }

    return $name
}

# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------
function Test-Source {
    $skillMd = Join-Path $script:SourceDir "SKILL.md"
    if (-not (Test-Path $skillMd)) {
        Write-Err "No SKILL.md found in $($script:SourceDir)"
        Write-Err "A valid skill must contain a SKILL.md file."
        exit 1
    }
}

# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------
function Find-AllGlobalPlatforms {
    $platforms = @()
    $checks = @(
        @{ Dir = ".claude";          Name = "claude-code" },
        @{ Dir = ".copilot";         Name = "copilot" },
        @{ Dir = ".gemini";          Name = "gemini" },
        @{ Dir = ".kiro";            Name = "kiro" },
        @{ Dir = ".cline";           Name = "cline" },
        @{ Dir = ".roo";             Name = "roo-code" },
        @{ Dir = ".kilocode";        Name = "kilo-code" },
        @{ Dir = ".factory";         Name = "factory" },
        @{ Dir = ".cursor";          Name = "cursor" },
        @{ Dir = ".config\goose";    Name = "goose" },
        @{ Dir = ".config\opencode"; Name = "opencode" }
    )
    foreach ($check in $checks) {
        if (Test-Path (Join-Path $HomeDir $check.Dir)) {
            $platforms += $check.Name
        }
    }
    return $platforms
}

function Find-AllProjectPlatforms {
    $platforms = @()
    $checks = @(
        @{ Dir = ".claude";     Name = "claude-code" },
        @{ Dir = ".github";     Name = "copilot" },
        @{ Dir = ".cursor";     Name = "cursor" },
        @{ Dir = ".windsurf";   Name = "windsurf" },
        @{ Dir = ".clinerules"; Name = "cline" },
        @{ Dir = ".cline";      Name = "cline" },
        @{ Dir = ".gemini";     Name = "gemini" },
        @{ Dir = ".kiro";       Name = "kiro" },
        @{ Dir = ".trae";       Name = "trae" },
        @{ Dir = ".roo";        Name = "roo-code" },
        @{ Dir = ".kilocode";   Name = "kilo-code" },
        @{ Dir = ".factory";    Name = "factory" },
        @{ Dir = ".junie";      Name = "junie" },
        @{ Dir = ".agent";      Name = "antigravity" }
    )
    foreach ($check in $checks) {
        if ((Test-Path $check.Dir) -and ($check.Name -notin $platforms)) {
            $platforms += $check.Name
        }
    }
    return $platforms
}

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
function Resolve-PlatformPath {
    param([string]$Plat, [string]$Name)

    if ($Project) {
        $base = switch ($Plat) {
            "claude-code"   { ".claude\skills" }
            "copilot"       { ".github\skills" }
            "cursor"        { ".cursor\rules" }
            "windsurf"      { ".windsurf\rules" }
            "cline"         { ".clinerules\skills" }
            "codex"         { ".agents\skills" }
            "gemini"        { ".gemini\skills" }
            "kiro"          { ".kiro\skills" }
            "trae"          { ".trae\rules" }
            "roo-code"      { ".roo\skills" }
            "kilo-code"     { ".kilocode\skills" }
            "factory"       { ".factory\skills" }
            "junie"         { ".junie\skills" }
            "goose"         { ".goose\skills" }
            "opencode"      { ".opencode\skills" }
            "antigravity"   { ".agent\skills" }
            default         { ".agents\skills" }
        }
        return Join-Path (Get-Location) $base $Name
    } else {
        $base = switch ($Plat) {
            "claude-code"   { Join-Path $HomeDir ".claude\skills" }
            "copilot"       { Join-Path $HomeDir ".copilot\skills" }
            "cursor"        { Join-Path $HomeDir ".cursor\rules" }
            "windsurf"      { Join-Path $HomeDir ".codeium\windsurf\skills" }
            "cline"         { Join-Path $HomeDir ".cline\skills" }
            "codex"         { Join-Path $HomeDir ".agents\skills" }
            "gemini"        { Join-Path $HomeDir ".gemini\skills" }
            "kiro"          { Join-Path $HomeDir ".kiro\skills" }
            "trae"          { Join-Path $HomeDir ".trae\rules" }
            "roo-code"      { Join-Path $HomeDir ".roo\skills" }
            "kilo-code"     { Join-Path $HomeDir ".kilocode\skills" }
            "factory"       { Join-Path $HomeDir ".factory\skills" }
            "junie"         { Join-Path $HomeDir ".junie\skills" }
            "goose"         { Join-Path $HomeDir ".config\goose\skills" }
            "opencode"      { Join-Path $HomeDir ".config\opencode\skills" }
            "antigravity"   { Join-Path $HomeDir ".gemini\antigravity\skills" }
            default         { Join-Path $HomeDir ".agents\skills" }
        }
        return Join-Path $base $Name
    }
}

function Get-PlatformDisplay {
    param([string]$Plat)
    switch ($Plat) {
        "claude-code"   { "Claude Code" }
        "copilot"       { "GitHub Copilot" }
        "cursor"        { "Cursor" }
        "windsurf"      { "Windsurf" }
        "cline"         { "Cline" }
        "codex"         { "Codex CLI" }
        "gemini"        { "Gemini CLI" }
        "kiro"          { "Kiro" }
        "trae"          { "Trae" }
        "roo-code"      { "Roo Code" }
        "kilo-code"     { "Kilo Code" }
        "factory"       { "Factory Droid" }
        "junie"         { "Junie" }
        "goose"         { "Goose" }
        "opencode"      { "OpenCode" }
        "antigravity"   { "Antigravity" }
        default         { $Plat }
    }
}

# ---------------------------------------------------------------------------
# Create a directory junction
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
# Format adapters
# ---------------------------------------------------------------------------
function Get-SkillBody {
    $skillMd = Join-Path $script:SourceDir "SKILL.md"
    $lines = Get-Content $skillMd
    $delimCount = 0
    $bodyLines = @()
    foreach ($line in $lines) {
        if ($line -eq "---") { $delimCount++; continue }
        if ($delimCount -ge 2) { $bodyLines += $line }
    }
    return ($bodyLines -join "`n")
}

function Get-SkillDescription {
    $skillMd = Join-Path $script:SourceDir "SKILL.md"
    $lines = Get-Content $skillMd -TotalCount 30
    $inFm = $false
    foreach ($line in $lines) {
        if (-not $inFm -and $line -eq "---") { $inFm = $true; continue }
        if ($inFm -and $line -eq "---") { break }
        if ($inFm -and $line -match "^description:\s*(.+)") { return $Matches[1] }
    }
    return ""
}

function Invoke-Adapters {
    param([string]$Plat, [string]$Dest)

    $body = Get-SkillBody
    $desc = Get-SkillDescription

    switch ($Plat) {
        "cursor" {
            $mdcFile = Join-Path $Dest "$SkillName.mdc"
            if ($DryRun) {
                Write-Info "[dry-run] Would generate Cursor .mdc: $mdcFile"
            } else {
                if (-not (Test-Path $Dest)) { New-Item -ItemType Directory -Path $Dest -Force | Out-Null }
                @"
---
description: $desc
globs:
alwaysApply: true
---
$body
"@ | Set-Content -Path $mdcFile -Encoding UTF8
                Write-Ok "Generated Cursor .mdc: $mdcFile"
            }
        }
        "windsurf" {
            if ($Project) {
                $ruleFile = Join-Path (Get-Location) ".windsurf\rules\$SkillName.md"
                if ($DryRun) {
                    Write-Info "[dry-run] Would generate Windsurf rule: $ruleFile"
                } else {
                    $ruleDir = Split-Path $ruleFile -Parent
                    if (-not (Test-Path $ruleDir)) { New-Item -ItemType Directory -Path $ruleDir -Force | Out-Null }
                    Set-Content -Path $ruleFile -Value $body -Encoding UTF8
                    Write-Ok "Generated Windsurf rule: $ruleFile"
                }
            } else {
                $globalFile = Join-Path $HomeDir ".codeium\windsurf\memories\global_rules.md"
                if ($DryRun) {
                    Write-Info "[dry-run] Would append to Windsurf global_rules.md"
                } else {
                    $gDir = Split-Path $globalFile -Parent
                    if (-not (Test-Path $gDir)) { New-Item -ItemType Directory -Path $gDir -Force | Out-Null }
                    if (Test-Path $globalFile) {
                        $existing = Get-Content $globalFile -Raw
                        $pattern = "(?s)<!-- BEGIN $SkillName -->.*?<!-- END $SkillName -->\r?\n?"
                        $existing = $existing -replace $pattern, ""
                        Set-Content -Path $globalFile -Value $existing -Encoding UTF8
                    }
                    @"

<!-- BEGIN $SkillName -->
$body
<!-- END $SkillName -->
"@ | Add-Content -Path $globalFile -Encoding UTF8
                    Write-Ok "Appended to Windsurf global_rules.md"
                }
            }
        }
        { $_ -in "cline", "roo-code", "kilo-code", "trae" } {
            $plainFile = Join-Path $Dest "$SkillName.md"
            if ($DryRun) {
                Write-Info "[dry-run] Would generate plain rule: $plainFile"
            } else {
                if (-not (Test-Path $Dest)) { New-Item -ItemType Directory -Path $Dest -Force | Out-Null }
                Set-Content -Path $plainFile -Value $body -Encoding UTF8
                Write-Ok "Generated plain rule: $plainFile"
            }
        }
        "junie" {
            $guidelineFile = Join-Path $Dest "guidelines.md"
            if ($DryRun) {
                Write-Info "[dry-run] Would generate Junie guideline: $guidelineFile"
            } else {
                if (-not (Test-Path $Dest)) { New-Item -ItemType Directory -Path $Dest -Force | Out-Null }
                Set-Content -Path $guidelineFile -Value $body -Encoding UTF8
                Write-Ok "Generated Junie guideline: $guidelineFile"
            }
        }
    }
}

# ---------------------------------------------------------------------------
# Install to a single platform
# ---------------------------------------------------------------------------
function Install-ToPlatform {
    param([string]$Plat)

    $dest = Resolve-PlatformPath $Plat $SkillName
    $display = Get-PlatformDisplay $Plat

    if ($DryRun) {
        Write-Info "[dry-run] Would install to ${display}: $dest"
        Invoke-Adapters $Plat $dest
        return
    }

    New-SkillLink -Target $script:SourceDir -LinkPath $dest
    Write-Ok "Installed for $display -> $dest"
    Invoke-Adapters $Plat $dest
}

# ---------------------------------------------------------------------------
# Uninstall
# ---------------------------------------------------------------------------
function Remove-Skill {
    Write-Host ""
    Write-Host "Uninstalling skill: $SkillName" -ForegroundColor White
    Write-Host ""

    $canonical = Join-Path $HomeDir ".agents\skills\$SkillName"
    if (Test-Path $canonical) {
        if ($DryRun) {
            Write-Info "[dry-run] Would remove: $canonical"
        } else {
            Remove-Item $canonical -Recurse -Force
            Write-Ok "Removed: $canonical"
        }
    }

    $globalPlatforms = @("claude-code","copilot","gemini","kiro","cline","roo-code","kilo-code","factory","cursor","goose","opencode")
    foreach ($plat in $globalPlatforms) {
        $dest = Resolve-PlatformPath $plat $SkillName
        if (Test-Path $dest) {
            if ($DryRun) {
                Write-Info "[dry-run] Would remove: $dest"
            } else {
                Remove-Item $dest -Recurse -Force
                Write-Ok "Removed: $dest ($(Get-PlatformDisplay $plat))"
            }
        }
    }

    $projectPlatforms = @("claude-code","copilot","cursor","windsurf","cline","gemini","kiro","trae","roo-code","kilo-code","factory","junie","antigravity")
    foreach ($plat in $projectPlatforms) {
        $script:Project = $true
        $dest = Resolve-PlatformPath $plat $SkillName
        if (Test-Path $dest) {
            if ($DryRun) {
                Write-Info "[dry-run] Would remove: $dest"
            } else {
                Remove-Item $dest -Recurse -Force
                Write-Ok "Removed: $dest ($(Get-PlatformDisplay $plat))"
            }
        }
    }

    Write-Host ""
    Write-Host "Done."
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "Universal Skill Installer (Windows)" -ForegroundColor White
Write-Host ""

Resolve-Source

if (-not $DryRun) {
    Test-Source
} elseif ($script:SourceDir -and (Test-Path $script:SourceDir)) {
    Test-Source
}

$SkillName = Get-SkillName
Write-Info "Skill: $SkillName"
Write-Info "Source: $($script:SourceDir)"

if ($Uninstall) {
    Remove-Skill
    exit 0
}

# Install to canonical location first
$canonical = Join-Path $HomeDir ".agents\skills\$SkillName"
if (-not (Test-GitUrl $Source) -and ($script:SourceDir -ne $canonical)) {
    if ($DryRun) {
        Write-Info "[dry-run] Would copy to canonical: $canonical"
    } else {
        $cParent = Split-Path $canonical -Parent
        if (-not (Test-Path $cParent)) { New-Item -ItemType Directory -Path $cParent -Force | Out-Null }
        if (Test-Path $canonical) { Remove-Item $canonical -Recurse -Force }
        Copy-Item -Path $script:SourceDir -Destination $canonical -Recurse -Force
        Write-Ok "Copied to canonical: $canonical"
    }
}

# Determine which platforms to install to
if ($Platform) {
    Install-ToPlatform $Platform
} else {
    if ($Project) {
        $platforms = Find-AllProjectPlatforms
    } else {
        $platforms = Find-AllGlobalPlatforms
    }

    $count = 0
    foreach ($plat in $platforms) {
        Install-ToPlatform $plat
        $count++
    }

    if ($count -eq 0) {
        Write-Warn "No platforms detected. Skill installed at canonical path only."
    }
}

# Summary
Write-Host ""
Write-Host "Done!" -ForegroundColor Green
Write-Host "  Canonical: $canonical"
Write-Host "  Invoke with: /$SkillName"
Write-Host ""

if ($DryRun) {
    Write-Warn "Dry run - no changes made."
    Write-Host ""
}
