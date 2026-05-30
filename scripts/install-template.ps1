# install-template.ps1 — Cross-platform skill installation script (Windows)
# This file is a template. During skill generation, {{SKILL_NAME}} is replaced
# with the actual skill name and the result is shipped as install.ps1 inside
# every generated skill package.
#
# Works on PowerShell 5.1+ and PowerShell Core 7+.
# Exit codes:
#   0 — Success
#   1 — Validation failed (missing or malformed SKILL.md)
#   2 — Platform not detected
#   3 — Permission denied

param(
    [string]$Platform = "",
    [switch]$Project,
    [string]$Path = "",
    [switch]$All,
    [switch]$DryRun,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
$SkillName = "{{SKILL_NAME}}"
$Version = "1.0.0"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
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
install.ps1 — Install the $SkillName skill (v$Version)

USAGE
    .\install.ps1 [OPTIONS]

OPTIONS
    -Platform <name>   Explicit platform selection. One of:
                       claude-code, copilot, cursor, windsurf,
                       cline, codex, gemini, kiro, trae, goose,
                       opencode, roo-code, kilo-code, factory,
                       junie, antigravity, universal
    -Project           Install at project level (current directory)
    -Path <path>       Custom install path (overrides detection)
    -All               Install to ALL detected tool paths at once
    -DryRun            Show what would happen without making changes
    -Help              Show this help message

EXAMPLES
    .\install.ps1                          # Auto-detect platform, user-level
    .\install.ps1 -Project                 # Auto-detect platform, project-level
    .\install.ps1 -Platform cursor         # Force Cursor, user-level
    .\install.ps1 -Path ~\my-skills\       # Custom destination
    .\install.ps1 -All                     # Install to every detected tool
    .\install.ps1 -DryRun                  # Preview without installing
"@
    exit 0
}

# ---------------------------------------------------------------------------
# SKILL.md validation
# ---------------------------------------------------------------------------
function Test-SkillMd {
    $skillMd = Join-Path $ScriptDir "SKILL.md"

    if (-not (Test-Path $skillMd)) {
        Write-Err "SKILL.md not found in $ScriptDir"
        Write-Err "Every skill package must contain a valid SKILL.md file."
        exit 1
    }

    $lines = Get-Content $skillMd -TotalCount 50
    if ($lines.Count -eq 0 -or $lines[0] -ne "---") {
        Write-Err "SKILL.md must start with YAML frontmatter (---)"
        exit 1
    }

    $foundName = $false
    $foundDesc = $false
    $inFrontmatter = $false

    foreach ($line in $lines) {
        if (-not $inFrontmatter -and $line -eq "---") {
            $inFrontmatter = $true
            continue
        }
        if ($inFrontmatter -and $line -eq "---") { break }
        if ($inFrontmatter) {
            if ($line -match "^name:") { $foundName = $true }
            if ($line -match "^description:") { $foundDesc = $true }
        }
    }

    if (-not $foundName) {
        Write-Err "SKILL.md frontmatter is missing required field: name"
        exit 1
    }
    if (-not $foundDesc) {
        Write-Err "SKILL.md frontmatter is missing required field: description"
        exit 1
    }

    Write-Ok "SKILL.md validated (name and description present)"
}

# ---------------------------------------------------------------------------
# Supported platforms
# ---------------------------------------------------------------------------
$SupportedPlatforms = @(
    "claude-code", "copilot", "cursor", "windsurf", "cline", "codex",
    "gemini", "kiro", "trae", "goose", "opencode", "roo-code",
    "kilo-code", "factory", "junie", "antigravity", "universal"
)

# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------
function Find-Platform {
    if ($Platform) {
        if ($Platform -notin $SupportedPlatforms) {
            Write-Err "Unknown platform: $Platform"
            Write-Err "Supported: $($SupportedPlatforms -join ', ')"
            exit 2
        }
        Write-Info "Platform explicitly set to: $Platform"
        return $Platform
    }

    $checks = @(
        @{ Dir = ".claude";           Name = "claude-code" },
        @{ Dir = ".copilot";          Name = "copilot" },
        @{ Dir = ".cursor";           Name = "cursor" },
        @{ Dir = ".codeium\windsurf"; Name = "windsurf" },
        @{ Dir = ".cline";            Name = "cline" },
        @{ Dir = ".gemini";           Name = "gemini" },
        @{ Dir = ".kiro";             Name = "kiro" },
        @{ Dir = ".roo";              Name = "roo-code" },
        @{ Dir = ".kilocode";         Name = "kilo-code" },
        @{ Dir = ".factory";          Name = "factory" },
        @{ Dir = ".config\goose";     Name = "goose" },
        @{ Dir = ".config\opencode";  Name = "opencode" },
        @{ Dir = ".agents";           Name = "universal" }
    )

    # Also check project-level dirs
    $projectChecks = @(
        @{ Dir = ".github";    Name = "copilot" },
        @{ Dir = ".cursor";    Name = "cursor" },
        @{ Dir = ".windsurf";  Name = "windsurf" },
        @{ Dir = ".clinerules"; Name = "cline" },
        @{ Dir = ".kiro";      Name = "kiro" },
        @{ Dir = ".trae";      Name = "trae" },
        @{ Dir = ".roo";       Name = "roo-code" },
        @{ Dir = ".kilocode";  Name = "kilo-code" },
        @{ Dir = ".factory";   Name = "factory" },
        @{ Dir = ".junie";     Name = "junie" }
    )

    foreach ($check in $checks) {
        $testPath = Join-Path $HomeDir $check.Dir
        if (Test-Path $testPath) {
            Write-Info "Auto-detected platform: $($check.Name)"
            return $check.Name
        }
    }

    foreach ($check in $projectChecks) {
        if (Test-Path $check.Dir) {
            Write-Info "Auto-detected platform: $($check.Name) (project-level)"
            return $check.Name
        }
    }

    Write-Err "Could not auto-detect any supported AI coding platform."
    Write-Err "Use -Platform <name> to specify one explicitly."
    Write-Err "Supported: $($SupportedPlatforms -join ', ')"
    exit 2
}

# ---------------------------------------------------------------------------
# Detect all installed platforms (for -All)
# ---------------------------------------------------------------------------
function Find-AllPlatforms {
    $found = @()

    $globalChecks = @(
        @{ Dir = ".claude";           Name = "claude-code" },
        @{ Dir = ".copilot";          Name = "copilot" },
        @{ Dir = ".cursor";           Name = "cursor" },
        @{ Dir = ".codeium\windsurf"; Name = "windsurf" },
        @{ Dir = ".cline";            Name = "cline" },
        @{ Dir = ".gemini";           Name = "gemini" },
        @{ Dir = ".kiro";             Name = "kiro" },
        @{ Dir = ".roo";              Name = "roo-code" },
        @{ Dir = ".kilocode";         Name = "kilo-code" },
        @{ Dir = ".factory";          Name = "factory" },
        @{ Dir = ".config\goose";     Name = "goose" },
        @{ Dir = ".config\opencode";  Name = "opencode" }
    )

    $projectChecks = @(
        @{ Dir = ".github";    Name = "copilot" },
        @{ Dir = ".cursor";    Name = "cursor" },
        @{ Dir = ".windsurf";  Name = "windsurf" },
        @{ Dir = ".clinerules"; Name = "cline" },
        @{ Dir = ".kiro";      Name = "kiro" },
        @{ Dir = ".trae";      Name = "trae" },
        @{ Dir = ".roo";       Name = "roo-code" },
        @{ Dir = ".kilocode";  Name = "kilo-code" },
        @{ Dir = ".factory";   Name = "factory" },
        @{ Dir = ".junie";     Name = "junie" }
    )

    foreach ($check in $globalChecks) {
        $testPath = Join-Path $HomeDir $check.Dir
        if ((Test-Path $testPath) -and ($check.Name -notin $found)) {
            $found += $check.Name
        }
    }

    foreach ($check in $projectChecks) {
        if ((Test-Path $check.Dir) -and ($check.Name -notin $found)) {
            $found += $check.Name
        }
    }

    # Always include universal
    if ("universal" -notin $found) {
        $found += "universal"
    }

    return $found
}

# ---------------------------------------------------------------------------
# Install path resolution
# ---------------------------------------------------------------------------
function Resolve-InstallPath {
    param([string]$Plat)

    if ($Path) {
        return $Path
    }

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
            "goose"         { ".goose\skills" }
            "opencode"      { ".opencode\skills" }
            "roo-code"      { ".roo\skills" }
            "kilo-code"     { ".kilocode\skills" }
            "factory"       { ".factory\skills" }
            "junie"         { ".junie\skills" }
            "antigravity"   { ".agent\skills" }
            "universal"     { ".agents\skills" }
        }
        return Join-Path (Get-Location) $base $SkillName
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
            "goose"         { Join-Path $HomeDir ".config\goose\skills" }
            "opencode"      { Join-Path $HomeDir ".config\opencode\skills" }
            "roo-code"      { Join-Path $HomeDir ".roo\skills" }
            "kilo-code"     { Join-Path $HomeDir ".kilocode\skills" }
            "factory"       { Join-Path $HomeDir ".factory\skills" }
            "junie"         { Join-Path $HomeDir ".junie\skills" }
            "antigravity"   { Join-Path $HomeDir ".gemini\antigravity\skills" }
            "universal"     { Join-Path $HomeDir ".agents\skills" }
        }
        return Join-Path $base $SkillName
    }
}

# ---------------------------------------------------------------------------
# Platform display names
# ---------------------------------------------------------------------------
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
        "goose"         { "Goose" }
        "opencode"      { "OpenCode" }
        "roo-code"      { "Roo Code" }
        "kilo-code"     { "Kilo Code" }
        "factory"       { "Factory Droid" }
        "junie"         { "Junie" }
        "antigravity"   { "Antigravity" }
        "universal"     { "Universal" }
        default         { $Plat }
    }
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

    # Try junction first (no admin), then symlink, then copy
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
# Extract SKILL.md body (everything after second ---)
# ---------------------------------------------------------------------------
function Get-SkillBody {
    $skillMd = Join-Path $ScriptDir "SKILL.md"
    $lines = Get-Content $skillMd
    $delimCount = 0
    $bodyLines = @()

    foreach ($line in $lines) {
        if ($line -eq "---") {
            $delimCount++
            continue
        }
        if ($delimCount -ge 2) {
            $bodyLines += $line
        }
    }
    return ($bodyLines -join "`n")
}

# ---------------------------------------------------------------------------
# Extract description from SKILL.md frontmatter
# ---------------------------------------------------------------------------
function Get-SkillDescription {
    $skillMd = Join-Path $ScriptDir "SKILL.md"
    $lines = Get-Content $skillMd -TotalCount 30
    $inFm = $false

    foreach ($line in $lines) {
        if (-not $inFm -and $line -eq "---") { $inFm = $true; continue }
        if ($inFm -and $line -eq "---") { break }
        if ($inFm -and $line -match "^description:\s*(.+)") {
            return $Matches[1]
        }
    }
    return ""
}

# ---------------------------------------------------------------------------
# Format adapters
# ---------------------------------------------------------------------------
function New-CursorMdc {
    param([string]$TargetDir)

    $desc = Get-SkillDescription
    $body = Get-SkillBody
    $mdcFile = Join-Path $TargetDir "$SkillName.mdc"

    if ($DryRun) {
        Write-Info "[dry-run] Would generate Cursor .mdc: $mdcFile"
        return
    }

    if (-not (Test-Path $TargetDir)) {
        New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    }

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

function New-WindsurfRule {
    param([string]$TargetDir, [bool]$IsGlobal)

    $body = Get-SkillBody

    if ($IsGlobal) {
        $globalFile = Join-Path $HomeDir ".codeium\windsurf\memories\global_rules.md"

        if ($DryRun) {
            Write-Info "[dry-run] Would append to Windsurf global_rules.md: $globalFile"
            return
        }

        $parentDir = Split-Path $globalFile -Parent
        if (-not (Test-Path $parentDir)) {
            New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
        }

        # Remove existing block if present
        if (Test-Path $globalFile) {
            $existing = Get-Content $globalFile -Raw
            $pattern = "(?s)<!-- BEGIN $SkillName -->.*?<!-- END $SkillName -->\r?\n?"
            $existing = $existing -replace $pattern, ""
            Set-Content -Path $globalFile -Value $existing -Encoding UTF8
        }

        # Append new block
        @"

<!-- BEGIN $SkillName -->
$body
<!-- END $SkillName -->
"@ | Add-Content -Path $globalFile -Encoding UTF8
        Write-Ok "Appended to Windsurf global_rules.md"
    } else {
        $ruleFile = Join-Path $TargetDir "$SkillName.md"
        if ($DryRun) {
            Write-Info "[dry-run] Would generate Windsurf rule: $ruleFile"
            return
        }
        if (-not (Test-Path $TargetDir)) {
            New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
        }
        Set-Content -Path $ruleFile -Value $body -Encoding UTF8
        Write-Ok "Generated Windsurf rule: $ruleFile"
    }
}

function New-PlainRule {
    param([string]$TargetDir, [string]$FileName)

    $body = Get-SkillBody
    $plainFile = Join-Path $TargetDir $FileName

    if ($DryRun) {
        Write-Info "[dry-run] Would generate plain rule: $plainFile"
        return
    }

    if (-not (Test-Path $TargetDir)) {
        New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    }
    Set-Content -Path $plainFile -Value $body -Encoding UTF8
    Write-Ok "Generated plain rule: $plainFile"
}

function New-JunieGuideline {
    param([string]$TargetDir)

    $body = Get-SkillBody
    $guidelineFile = Join-Path $TargetDir "guidelines.md"

    if ($DryRun) {
        Write-Info "[dry-run] Would generate Junie guideline: $guidelineFile"
        return
    }

    if (-not (Test-Path $TargetDir)) {
        New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    }
    Set-Content -Path $guidelineFile -Value $body -Encoding UTF8
    Write-Ok "Generated Junie guideline: $guidelineFile"
}

function Invoke-Adapters {
    param([string]$Plat, [string]$InstallDir)

    switch ($Plat) {
        "cursor"    { New-CursorMdc $InstallDir }
        "windsurf"  {
            if ($Project) {
                New-WindsurfRule (Join-Path (Get-Location) ".windsurf\rules") $false
            } else {
                New-WindsurfRule "" $true
            }
        }
        { $_ -in "cline", "roo-code", "kilo-code", "trae" } {
            New-PlainRule $InstallDir "$SkillName.md"
        }
        "junie" { New-JunieGuideline $InstallDir }
    }
}

# ---------------------------------------------------------------------------
# AGENTS.md companion
# ---------------------------------------------------------------------------
function New-AgentsMd {
    param([string]$InstallDir)

    if (Test-Path (Join-Path $ScriptDir "AGENTS.md")) { return }
    if ($DryRun) {
        Write-Info "[dry-run] Would generate companion AGENTS.md"
        return
    }

    $desc = Get-SkillDescription
    $agentsMd = Join-Path $InstallDir "AGENTS.md"

    @"
# $SkillName

$desc

## Usage

Invoke this skill with ``/$SkillName`` or by describing a task that matches its description.

## Details

See [SKILL.md](./SKILL.md) for full implementation details, triggers, and configuration.
"@ | Set-Content -Path $agentsMd -Encoding UTF8
    Write-Ok "Generated companion AGENTS.md"
}

# ---------------------------------------------------------------------------
# Universal secondary install
# ---------------------------------------------------------------------------
function Install-UniversalSecondary {
    param([string]$Plat, [string]$InstallDir)

    if ($Plat -in "codex", "universal") { return }

    $universalDir = Join-Path $HomeDir ".agents\skills" $SkillName

    if ($DryRun) {
        Write-Info "[dry-run] Would create universal link: $universalDir -> $InstallDir"
        return
    }

    $parentDir = Split-Path $universalDir -Parent
    if (-not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    New-SkillLink -Target $InstallDir -LinkPath $universalDir
    Write-Ok "Universal link: $universalDir -> $InstallDir"
}

# ---------------------------------------------------------------------------
# File installation
# ---------------------------------------------------------------------------
function Install-Files {
    param([string]$InstallDir)

    $installScriptName = Split-Path $MyInvocation.ScriptName -Leaf
    $files = Get-ChildItem $ScriptDir -Force | Where-Object {
        $_.Name -ne $installScriptName -and
        $_.Name -ne "install.sh" -and
        $_.Name -ne "install.ps1" -and
        $_.Name -ne "." -and
        $_.Name -ne ".."
    }

    if ($DryRun) {
        Write-Host ""
        Write-Host "Dry-run mode - no files will be copied." -ForegroundColor White
        Write-Host ""
        Write-Info "Would create directory: $InstallDir"
        foreach ($file in $files) {
            Write-Info "Would copy: $($file.Name)"
        }
        Write-Host ""
        Write-Info "Total files: $($files.Count)"
        return
    }

    # Clean existing install
    if (Test-Path $InstallDir) {
        Remove-Item $InstallDir -Recurse -Force
    }

    try {
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    } catch {
        Write-Err "Cannot create directory: $InstallDir"
        Write-Err "Check file permissions or run as administrator."
        exit 3
    }

    $count = 0
    foreach ($file in $files) {
        try {
            Copy-Item -Path $file.FullName -Destination $InstallDir -Recurse -Force
            $count++
        } catch {
            Write-Err "Failed to copy $($file.Name) to $InstallDir"
            Write-Err "Check file permissions."
            exit 3
        }
    }

    Write-Ok "Copied $count file(s) to $InstallDir"
}

# ---------------------------------------------------------------------------
# Install for a single platform
# ---------------------------------------------------------------------------
function Install-Single {
    $detectedPlatform = Find-Platform
    $installDir = Resolve-InstallPath $detectedPlatform
    Write-Info "Install directory: $installDir"

    Install-Files $installDir
    Invoke-Adapters $detectedPlatform $installDir
    New-AgentsMd $installDir
    Install-UniversalSecondary $detectedPlatform $installDir

    if (-not $DryRun) {
        $display = Get-PlatformDisplay $detectedPlatform
        Write-Host ""
        Write-Host "Installation complete!" -ForegroundColor Green
        Write-Host ""
        Write-Host "  Installed for: $display"
        Write-Host "  Location: $installDir"
        Write-Host "  Invoke with: /$SkillName"
        Write-Host ""
    } else {
        Write-Info "Dry run complete. No changes were made."
    }
}

# ---------------------------------------------------------------------------
# Install for all detected platforms (-All)
# ---------------------------------------------------------------------------
function Install-All {
    $platforms = Find-AllPlatforms
    Write-Info "Installing to all detected platforms: $($platforms -join ', ')"
    Write-Host "----------------------------------------"

    $count = 0
    $firstNonAgentsDir = ""

    foreach ($plat in $platforms) {
        Write-Host ""
        Write-Info "--- Installing for: $plat ---"
        $installDir = Resolve-InstallPath $plat
        Write-Info "Install directory: $installDir"

        Install-Files $installDir
        Invoke-Adapters $plat $installDir
        New-AgentsMd $installDir
        $count++

        if (-not $firstNonAgentsDir -and $plat -notin "codex", "universal") {
            $firstNonAgentsDir = $installDir
        }
    }

    # Create universal link from first non-.agents/ install
    if ($firstNonAgentsDir) {
        Install-UniversalSecondary "placeholder" $firstNonAgentsDir
    }

    Write-Host ""
    if ($DryRun) {
        Write-Info "Dry run complete. No changes were made."
    } else {
        Write-Ok "Skill '$SkillName' installed to $count platform(s)."
    }
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
Write-Host "Installing skill: $SkillName" -ForegroundColor White
Write-Host "----------------------------------------"

Test-SkillMd

if ($All) {
    Install-All
} else {
    Install-Single
}

exit 0
