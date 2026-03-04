#!/bin/sh
# install.sh — Symlink agent-skill-creator to all detected global platforms
#
# For users who already cloned the repo. Creates symlinks so `git pull` in the
# cloned directory updates all tools automatically.
#
# Usage:
#   ./install.sh              # Symlink to all detected platforms
#   ./install.sh --dry-run    # Preview without making changes
#   ./install.sh --uninstall  # Remove all symlinks pointing to this repo
#
# POSIX-compatible (works in bash, dash, zsh, ash).

set -eu

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SKILL_NAME="agent-skill-creator"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

# ---------------------------------------------------------------------------
# Colors (disabled when stdout is not a terminal)
# ---------------------------------------------------------------------------
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    RED='\033[0;31m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    GREEN='' YELLOW='' BLUE='' RED='' BOLD='' NC=''
fi

info()    { printf "${BLUE}[INFO]${NC}  %s\n" "$1"; }
success() { printf "${GREEN}[OK]${NC}    %s\n" "$1"; }
warn()    { printf "${YELLOW}[WARN]${NC}  %s\n" "$1"; }
error()   { printf "${RED}[ERROR]${NC} %s\n" "$1" >&2; }

# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------
DRY_RUN=false
UNINSTALL=false

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run)   DRY_RUN=true ;;
        --uninstall) UNINSTALL=true ;;
        -h|--help)
            printf "Usage: %s [--dry-run] [--uninstall]\n\n" "$0"
            printf "Options:\n"
            printf "  --dry-run     Preview without making changes\n"
            printf "  --uninstall   Remove all symlinks pointing to this repo\n"
            printf "  -h, --help    Show this help message\n"
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

# ---------------------------------------------------------------------------
# All global platform paths (user-level only)
# ---------------------------------------------------------------------------
all_platform_entries() {
    # Format: <detection_dir>|<install_path>|<display_name>
    cat <<'PLATFORMS'
$HOME/.claude|$HOME/.claude/skills/$SKILL_NAME|Claude Code
$HOME/.gemini|$HOME/.gemini/skills/$SKILL_NAME|Gemini CLI
$HOME/.config/goose|$HOME/.config/goose/skills/$SKILL_NAME|Goose
$HOME/.config/opencode|$HOME/.config/opencode/skills/$SKILL_NAME|OpenCode
$HOME/.copilot|$HOME/.copilot/skills/$SKILL_NAME|GitHub Copilot
PLATFORMS
}

# Expand variables in platform entries
eval_path() {
    eval echo "$1"
}

# ---------------------------------------------------------------------------
# Create a symlink (with fallback to copy)
# ---------------------------------------------------------------------------
create_symlink() {
    target="$1"
    link_path="$2"

    if [ "$target" = "$link_path" ]; then
        return 0
    fi

    mkdir -p "$(dirname "$link_path")"

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
# Uninstall: remove all symlinks pointing to REPO_DIR
# ---------------------------------------------------------------------------
do_uninstall() {
    printf "\n${BOLD}Uninstalling agent-skill-creator symlinks${NC}\n\n"

    canonical="$HOME/.agents/skills/$SKILL_NAME"
    removed=0

    # Check canonical location
    if [ -L "$canonical" ]; then
        link_target="$(readlink "$canonical" 2>/dev/null || true)"
        if [ "$link_target" = "$REPO_DIR" ]; then
            if [ "$DRY_RUN" = true ]; then
                info "[dry-run] Would remove: $canonical"
            else
                rm "$canonical"
                success "Removed: $canonical"
            fi
            removed=$((removed + 1))
        fi
    fi

    # Check each platform path
    all_platform_entries | while IFS='|' read -r detect_dir install_path display_name; do
        dest="$(eval_path "$install_path")"
        if [ -L "$dest" ]; then
            link_target="$(readlink "$dest" 2>/dev/null || true)"
            if [ "$link_target" = "$REPO_DIR" ]; then
                if [ "$DRY_RUN" = true ]; then
                    info "[dry-run] Would remove: $dest"
                else
                    rm "$dest"
                    success "Removed: $dest ($display_name)"
                fi
            fi
        fi
    done

    if [ "$DRY_RUN" = true ]; then
        printf "\n${YELLOW}Dry run — no changes made.${NC}\n"
    else
        printf "\nDone. Symlinks removed.\n"
    fi
}

# ---------------------------------------------------------------------------
# Install: create symlinks to all detected platforms
# ---------------------------------------------------------------------------
do_install() {
    printf "\n${BOLD}Agent Skill Creator — Symlink Installer${NC}\n\n"
    info "Source: $REPO_DIR"

    count=0
    installed=""

    # Always install to canonical location
    canonical="$HOME/.agents/skills/$SKILL_NAME"
    if [ "$DRY_RUN" = true ]; then
        info "[dry-run] Would symlink: $canonical → $REPO_DIR"
    else
        create_symlink "$REPO_DIR" "$canonical"
        success "Canonical: $canonical"
    fi
    count=$((count + 1))

    # Install to each detected global platform
    all_platform_entries | while IFS='|' read -r detect_dir install_path display_name; do
        dir="$(eval_path "$detect_dir")"
        dest="$(eval_path "$install_path")"

        if [ -d "$dir" ]; then
            if [ "$DRY_RUN" = true ]; then
                info "[dry-run] Would symlink: $dest → $REPO_DIR ($display_name)"
            else
                create_symlink "$REPO_DIR" "$dest"
                success "Symlinked for $display_name → $dest"
            fi
        fi
    done

    # Summary
    printf "\n${BOLD}Done!${NC}\n\n"

    if [ "$DRY_RUN" = true ]; then
        printf "${YELLOW}Dry run — no changes made.${NC}\n\n"
    else
        printf "  Symlinks point to: ${BOLD}%s${NC}\n" "$REPO_DIR"
        printf "  Run ${BOLD}git pull${NC} from that directory to update all tools.\n\n"
    fi

    printf "${BOLD}How to use:${NC}\n"
    printf "  Open your AI agent and type:\n"
    printf "    /agent-skill-creator <describe your workflow>\n\n"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if [ "$UNINSTALL" = true ]; then
    do_uninstall
else
    do_install
fi
