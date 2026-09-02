#!/bin/sh
# install.sh — Symlink agent-skills-platform to all detected global platforms
#
# For users who already cloned the repo. Creates symlinks so `git pull` in the
# cloned directory updates all tools automatically.
#
# Usage:
#   ./install.sh              # Symlink to all detected platforms
#   ./install.sh --without-semantic-recon  # Skip the pinned dependency (explicit opt-out)
#   ./install.sh --dry-run    # Preview without making changes
#   ./install.sh --uninstall  # Remove all symlinks pointing to this repo
#
# POSIX-compatible (works in bash, dash, zsh, ash).

set -eu

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SKILL_NAME="agent-skills-platform"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SEMANTIC_RECON_NAME="semantic-recon"
SEMANTIC_RECON_URL="https://github.com/FrancyJGLisboa/semantic-recon.git"
# Update deliberately after verifying the new revision with Semantic Recon's gates.
SEMANTIC_RECON_COMMIT="78234a37ebfff4b046e299d703b9b1cf39133600"
SEMANTIC_RECON_DIR="$HOME/.agents/skills/$SEMANTIC_RECON_NAME"

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
WITH_SEMANTIC_RECON=true

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run)   DRY_RUN=true ;;
        --uninstall) UNINSTALL=true ;;
        --with-semantic-recon) WITH_SEMANTIC_RECON=true ;;
        --without-semantic-recon) WITH_SEMANTIC_RECON=false ;;
        -h|--help)
            printf "Usage: %s [--dry-run] [--uninstall] [--with-semantic-recon|--without-semantic-recon]\n\n" "$0"
            printf "Options:\n"
            printf "  --dry-run     Preview without making changes\n"
            printf "  --uninstall   Remove all symlinks pointing to this repo\n"
            printf "  --with-semantic-recon     Install Semantic Recon at its pinned revision (default)\n"
            printf "  --without-semantic-recon  Explicitly skip Semantic Recon installation\n"
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
$HOME/.copilot|$HOME/.copilot/skills/$SKILL_NAME|GitHub Copilot
$HOME/.gemini|$HOME/.gemini/skills/$SKILL_NAME|Gemini CLI
$HOME/.kiro|$HOME/.kiro/skills/$SKILL_NAME|Kiro
$HOME/.cline|$HOME/.cline/skills/$SKILL_NAME|Cline
$HOME/.roo|$HOME/.roo/skills/$SKILL_NAME|Roo Code
$HOME/.kilocode|$HOME/.kilocode/skills/$SKILL_NAME|Kilo Code
$HOME/.factory|$HOME/.factory/skills/$SKILL_NAME|Factory Droid
$HOME/.cursor|$HOME/.cursor/rules/$SKILL_NAME|Cursor
$HOME/.config/goose|$HOME/.config/goose/skills/$SKILL_NAME|Goose
$HOME/.config/opencode|$HOME/.config/opencode/skills/$SKILL_NAME|OpenCode
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
# Optional Semantic Recon installation
# ---------------------------------------------------------------------------
install_semantic_recon() {
    if [ "$DRY_RUN" = true ]; then
        info "[dry-run] Would install $SEMANTIC_RECON_NAME at $SEMANTIC_RECON_DIR"
        info "[dry-run] Would pin to: $SEMANTIC_RECON_COMMIT"
        return 0
    fi

    if ! command -v git >/dev/null 2>&1; then
        error "--with-semantic-recon requires git. Install git and run this command again."
        return 1
    fi

    if [ -e "$SEMANTIC_RECON_DIR" ] && [ ! -d "$SEMANTIC_RECON_DIR/.git" ]; then
        error "Refusing to replace $SEMANTIC_RECON_DIR: it is not a Git checkout."
        return 1
    fi

    if [ -d "$SEMANTIC_RECON_DIR/.git" ]; then
        origin="$(git -C "$SEMANTIC_RECON_DIR" config --get remote.origin.url 2>/dev/null || true)"
        if [ "$origin" != "$SEMANTIC_RECON_URL" ] && [ "$origin" != "${SEMANTIC_RECON_URL%.git}" ]; then
            error "Refusing to modify $SEMANTIC_RECON_DIR: origin is not $SEMANTIC_RECON_URL."
            return 1
        fi
        info "Updating existing $SEMANTIC_RECON_NAME checkout"
    else
        info "Cloning $SEMANTIC_RECON_NAME to $SEMANTIC_RECON_DIR"
        mkdir -p "$(dirname "$SEMANTIC_RECON_DIR")"
        git init --quiet "$SEMANTIC_RECON_DIR"
        git -C "$SEMANTIC_RECON_DIR" remote add origin "$SEMANTIC_RECON_URL"
    fi

    git -C "$SEMANTIC_RECON_DIR" fetch --depth 1 origin "$SEMANTIC_RECON_COMMIT" >/dev/null
    git -C "$SEMANTIC_RECON_DIR" checkout --detach "$SEMANTIC_RECON_COMMIT" >/dev/null

    installed_commit="$(git -C "$SEMANTIC_RECON_DIR" rev-parse HEAD)"
    if [ "$installed_commit" != "$SEMANTIC_RECON_COMMIT" ]; then
        error "Semantic Recon pin verification failed: expected $SEMANTIC_RECON_COMMIT, got $installed_commit."
        return 1
    fi

    "$SEMANTIC_RECON_DIR/scripts/install.sh"
    success "Semantic Recon installed and pinned: $installed_commit"
}

# ---------------------------------------------------------------------------
# Uninstall: remove all symlinks pointing to REPO_DIR
# ---------------------------------------------------------------------------
do_uninstall() {
    printf "\n${BOLD}Uninstalling agent-skills-platform symlinks${NC}\n\n"

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
    printf "\n${BOLD}Agent Skills Platform — Symlink Installer${NC}\n\n"
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

    if [ "$WITH_SEMANTIC_RECON" = true ]; then
        install_semantic_recon
    fi

    printf "${BOLD}How to use:${NC}\n"
    printf "  Open your AI agent and type:\n"
    printf "    /agent-skills-platform <describe your workflow>\n\n"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if [ "$UNINSTALL" = true ]; then
    do_uninstall
else
    do_install
fi
