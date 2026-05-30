@echo off
REM bootstrap.bat — One-liner bootstrap for agent-skill-creator (Windows CMD)
REM
REM Usage (paste into Command Prompt):
REM   curl -fsSL https://raw.githubusercontent.com/FrancyJGLisboa/agent-skill-creator/main/scripts/bootstrap.bat -o %TEMP%\bootstrap.bat && %TEMP%\bootstrap.bat
REM
REM This is a thin wrapper that launches the PowerShell bootstrap script.

echo.
echo Agent Skill Creator - Bootstrap Installer
echo.

REM Check if PowerShell is available
where powershell >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] PowerShell is not available on this system.
    echo         Please install PowerShell or use the PowerShell one-liner instead.
    echo         https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-windows
    exit /b 1
)

REM Run the PowerShell bootstrap directly from GitHub
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/FrancyJGLisboa/agent-skill-creator/main/scripts/bootstrap.ps1 | iex"

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Installation failed. See errors above.
    exit /b 1
)
