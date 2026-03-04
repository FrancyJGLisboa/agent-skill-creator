#!/bin/sh
# bootstrap.sh — One-liner bootstrap for agent-skill-creator
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/FrancyJGLisboa/agent-skill-creator/main/scripts/bootstrap.sh | sh
#
# Clones agent-skill-creator to ~/.agents/skills/ and symlinks to all detected
# global platforms. POSIX-compatible (works in bash, dash, zsh, ash).

set -eu

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REPO_URL="https://github.com/FrancyJGLisboa/agent-skill-creator.git"
SKILL_NAME="agent-skill-creator"
CANONICAL_DIR="$HOME/.agents/skills/$SKILL_NAME"

# ---------------------------------------------------------------------------
# Colors (disabled when stdout is not a terminal)
# ---------------------------------------------------------------------------
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    GREEN='' YELLOW='' BLUE='' BOLD='' NC=''
fi

info()    { printf "${BLUE}[INFO]${NC}  %s\n" "$1"; }
success() { printf "${GREEN}[OK]${NC}    %s\n" "$1"; }
warn()    { printf "${YELLOW}[WARN]${NC}  %s\n" "$1"; }

# ---------------------------------------------------------------------------
# Detect globally-installed platforms (user-level only, skip project-level)
# ---------------------------------------------------------------------------
detect_global_platforms() {
    platforms=""
    # Claude Code
    if [ -d "$HOME/.claude" ]; then
        platforms="$platforms claude-code"
    fi
    # Gemini CLI
    if [ -d "$HOME/.gemini" ]; then
        platforms="$platforms gemini"
    fi
    # Goose
    if [ -d "$HOME/.config/goose" ]; then
        platforms="$platforms goose"
    fi
    # OpenCode
    if [ -d "$HOME/.config/opencode" ]; then
        platforms="$platforms opencode"
    fi
    # GitHub Copilot
    if [ -d "$HOME/.copilot" ]; then
        platforms="$platforms copilot"
    fi
    echo "$platforms"
}

# ---------------------------------------------------------------------------
# Resolve user-level install path for a platform
# ---------------------------------------------------------------------------
platform_path() {
    case "$1" in
        claude-code) echo "$HOME/.claude/skills/$SKILL_NAME" ;;
        gemini)      echo "$HOME/.gemini/skills/$SKILL_NAME" ;;
        goose)       echo "$HOME/.config/goose/skills/$SKILL_NAME" ;;
        opencode)    echo "$HOME/.config/opencode/skills/$SKILL_NAME" ;;
        copilot)     echo "$HOME/.copilot/skills/$SKILL_NAME" ;;
    esac
}

# ---------------------------------------------------------------------------
# Friendly display name for a platform
# ---------------------------------------------------------------------------
platform_display() {
    case "$1" in
        claude-code) echo "Claude Code" ;;
        gemini)      echo "Gemini CLI" ;;
        goose)       echo "Goose" ;;
        opencode)    echo "OpenCode" ;;
        copilot)     echo "GitHub Copilot" ;;
    esac
}

# ---------------------------------------------------------------------------
# Create a symlink (with fallback to copy)
# ---------------------------------------------------------------------------
create_symlink() {
    target="$1"   # what the link points to
    link_path="$2" # where the link lives

    # Skip if target and link are the same path
    if [ "$target" = "$link_path" ]; then
        return 0
    fi

    mkdir -p "$(dirname "$link_path")"

    # Remove existing (file, symlink, or directory)
    if [ -e "$link_path" ] || [ -L "$link_path" ]; then
        rm -rf "$link_path"
    fi

    if ln -s "$target" "$link_path" 2>/dev/null; then
        return 0
    else
        warn "Symlink failed for $link_path — falling back to copy"
        cp -R "$target" "$link_path"
    fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    printf "\n${BOLD}Agent Skill Creator — Bootstrap Installer${NC}\n\n"

    # Check for git
    if ! command -v git >/dev/null 2>&1; then
        warn "git is not installed. Please install git and try again."
        exit 1
    fi

    # Clone or update the canonical location
    if [ -d "$CANONICAL_DIR/.git" ]; then
        info "Updating existing install at $CANONICAL_DIR"
        cd "$CANONICAL_DIR" && git pull --ff-only 2>/dev/null || true
    else
        info "Cloning $SKILL_NAME to $CANONICAL_DIR"
        mkdir -p "$(dirname "$CANONICAL_DIR")"
        rm -rf "$CANONICAL_DIR"
        git clone "$REPO_URL" "$CANONICAL_DIR"
    fi

    success "Installed at $CANONICAL_DIR"

    # Detect global platforms and create symlinks
    platforms="$(detect_global_platforms)"
    installed=""
    count=0

    for platform in $platforms; do
        dest="$(platform_path "$platform")"
        create_symlink "$CANONICAL_DIR" "$dest"
        name="$(platform_display "$platform")"
        success "Symlinked for $name → $dest"
        installed="$installed $name,"
        count=$((count + 1))
    done

    # ---------------------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------------------
    printf "\n${BOLD}Done!${NC}\n\n"
    printf "  Canonical location: ${BOLD}%s${NC}\n" "$CANONICAL_DIR"

    if [ $count -gt 0 ]; then
        # Trim trailing comma
        installed="$(echo "$installed" | sed 's/,$//')"
        printf "  Symlinked to %d platform(s):%s\n" "$count" "$installed"
    fi

    printf "\n${BOLD}How to use:${NC}\n"
    printf "  Open your AI agent and type:\n"
    printf "    /agent-skill-creator <describe your workflow>\n\n"
    printf "  To update later:\n"
    printf "    cd %s && git pull\n\n" "$CANONICAL_DIR"

    if [ $count -eq 0 ]; then
        warn "No global platforms detected. The skill is installed at the universal path."
        printf "  Tools like Codex CLI, Gemini CLI, Kiro, and Antigravity\n"
        printf "  read from ~/.agents/skills/ automatically.\n\n"
    fi
}

main
