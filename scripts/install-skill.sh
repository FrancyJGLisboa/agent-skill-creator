#!/bin/sh
# install-skill.sh — Install any skill (git URL or local path) to all detected platforms
#
# Usage:
#   ./scripts/install-skill.sh https://github.com/someone/sales-report-skill.git
#   ./scripts/install-skill.sh ./sales-report-skill
#   ./scripts/install-skill.sh ./sales-report-skill --platform cursor --project
#   ./scripts/install-skill.sh ./sales-report-skill --dry-run
#   ./scripts/install-skill.sh ./sales-report-skill --uninstall
#
# POSIX-compatible (works in bash, dash, zsh, ash).

set -eu

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
SOURCE=""
PLATFORM=""
PROJECT_LEVEL=false
DRY_RUN=false
UNINSTALL=false

usage() {
    cat <<'USAGE'
Usage: install-skill.sh <source> [options]

Arguments:
  <source>              Git URL (https://... or *.git) or local directory path

Options:
  --platform <name>     Install to a specific platform only
  --project             Use project-level paths (for Cursor, Windsurf, etc.)
  --all                 Install to all detected platforms (default)
  --dry-run             Preview without making changes
  --uninstall           Remove the skill from all platforms
  -h, --help            Show this help message

Examples:
  install-skill.sh https://github.com/someone/sales-report-skill.git
  install-skill.sh ./sales-report-skill
  install-skill.sh ./sales-report-skill --platform cursor --project
USAGE
}

while [ $# -gt 0 ]; do
    case "$1" in
        --platform)
            shift
            PLATFORM="${1:-}"
            if [ -z "$PLATFORM" ]; then
                error "--platform requires a value"
                exit 1
            fi
            ;;
        --project)   PROJECT_LEVEL=true ;;
        --all)       PLATFORM="" ;;
        --dry-run)   DRY_RUN=true ;;
        --uninstall) UNINSTALL=true ;;
        -h|--help)   usage; exit 0 ;;
        -*)          error "Unknown option: $1"; exit 1 ;;
        *)
            if [ -z "$SOURCE" ]; then
                SOURCE="$1"
            else
                error "Unexpected argument: $1"
                exit 1
            fi
            ;;
    esac
    shift
done

if [ -z "$SOURCE" ]; then
    error "Missing required argument: <source>"
    usage
    exit 1
fi

# ---------------------------------------------------------------------------
# Resolve source: git clone or validate local path
# ---------------------------------------------------------------------------
is_git_url() {
    case "$1" in
        *://*) return 0 ;;
        *.git) return 0 ;;
    esac
    return 1
}

resolve_source() {
    if is_git_url "$SOURCE"; then
        # Extract skill name from URL
        skill_basename="$(basename "$SOURCE" .git)"
        canonical_dir="$HOME/.agents/skills/$skill_basename"

        if [ -d "$canonical_dir/.git" ]; then
            info "Updating existing install at $canonical_dir"
            if [ "$DRY_RUN" = false ]; then
                cd "$canonical_dir" && git pull --ff-only 2>/dev/null || true
                cd - >/dev/null
            fi
        else
            info "Cloning $SOURCE"
            if [ "$DRY_RUN" = false ]; then
                mkdir -p "$(dirname "$canonical_dir")"
                rm -rf "$canonical_dir"
                git clone "$SOURCE" "$canonical_dir"
            fi
        fi
        SOURCE_DIR="$canonical_dir"
    else
        # Local path
        if [ ! -d "$SOURCE" ]; then
            error "Source directory not found: $SOURCE"
            exit 1
        fi
        SOURCE_DIR="$(cd "$SOURCE" && pwd)"
    fi
}

# ---------------------------------------------------------------------------
# Extract skill name from directory or SKILL.md frontmatter
# ---------------------------------------------------------------------------
extract_skill_name() {
    skill_name=""
    skill_md="$SOURCE_DIR/SKILL.md"

    # Try to extract from SKILL.md frontmatter
    if [ -f "$skill_md" ]; then
        in_fm=false
        lnum=0
        while IFS= read -r line; do
            lnum=$((lnum + 1))
            if [ "$lnum" -eq 1 ] && [ "$line" = "---" ]; then
                in_fm=true
                continue
            fi
            if $in_fm && [ "$line" = "---" ]; then break; fi
            if $in_fm; then
                case "$line" in
                    name:*)
                        skill_name="$(echo "$line" | sed 's/^name:[[:space:]]*//' | sed 's/^["'"'"']//' | sed 's/["'"'"']$//')"
                        ;;
                esac
            fi
        done < "$skill_md"
    fi

    # Fallback to directory basename
    if [ -z "$skill_name" ]; then
        skill_name="$(basename "$SOURCE_DIR")"
    fi

    SKILL_NAME="$skill_name"
}

# ---------------------------------------------------------------------------
# Validate SKILL.md exists
# ---------------------------------------------------------------------------
validate_source() {
    if [ ! -f "$SOURCE_DIR/SKILL.md" ]; then
        error "No SKILL.md found in $SOURCE_DIR"
        error "A valid skill must contain a SKILL.md file."
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# Platform detection and path resolution
# ---------------------------------------------------------------------------
detect_all_global_platforms() {
    platforms=""
    if [ -d "$HOME/.claude" ]; then platforms="$platforms claude-code"; fi
    if [ -d "$HOME/.gemini" ]; then platforms="$platforms gemini"; fi
    if [ -d "$HOME/.config/goose" ]; then platforms="$platforms goose"; fi
    if [ -d "$HOME/.config/opencode" ]; then platforms="$platforms opencode"; fi
    if [ -d "$HOME/.copilot" ]; then platforms="$platforms copilot"; fi
    echo "$platforms"
}

detect_all_project_platforms() {
    platforms=""
    if [ -d ".cursor" ]; then platforms="$platforms cursor"; fi
    if [ -d ".windsurf" ]; then platforms="$platforms windsurf"; fi
    if [ -d ".clinerules" ] || [ -d ".cline" ]; then platforms="$platforms cline"; fi
    if [ -d ".kiro" ]; then platforms="$platforms kiro"; fi
    if [ -d ".trae" ]; then platforms="$platforms trae"; fi
    if [ -d ".roo" ]; then platforms="$platforms roo-code"; fi
    if [ -d ".github" ]; then platforms="$platforms copilot"; fi
    echo "$platforms"
}

resolve_platform_path() {
    plat="$1"
    name="$2"
    if [ "$PROJECT_LEVEL" = true ]; then
        case "$plat" in
            claude-code) echo ".claude/skills/$name" ;;
            copilot)     echo ".github/skills/$name" ;;
            cursor)      echo ".cursor/rules/$name" ;;
            windsurf)    echo ".windsurf/rules/$name" ;;
            cline)       echo ".clinerules/$name" ;;
            gemini)      echo ".gemini/skills/$name" ;;
            kiro)        echo ".kiro/skills/$name" ;;
            trae)        echo ".trae/rules/$name" ;;
            roo-code)    echo ".roo/rules/$name" ;;
            goose)       echo ".agents/skills/$name" ;;
            opencode)    echo ".agents/skills/$name" ;;
            *)           echo ".agents/skills/$name" ;;
        esac
    else
        case "$plat" in
            claude-code) echo "$HOME/.claude/skills/$name" ;;
            copilot)     echo "$HOME/.copilot/skills/$name" ;;
            cursor)      echo "$HOME/.cursor/rules/$name" ;;
            windsurf)    echo "$HOME/.codeium/windsurf/skills/$name" ;;
            cline)       echo "$HOME/.cline/rules/$name" ;;
            gemini)      echo "$HOME/.gemini/skills/$name" ;;
            goose)       echo "$HOME/.config/goose/skills/$name" ;;
            opencode)    echo "$HOME/.config/opencode/skills/$name" ;;
            kiro)        echo "$HOME/.agents/skills/$name" ;;
            trae)        echo "$HOME/.agents/skills/$name" ;;
            roo-code)    echo "$HOME/.agents/skills/$name" ;;
            *)           echo "$HOME/.agents/skills/$name" ;;
        esac
    fi
}

platform_display() {
    case "$1" in
        claude-code) echo "Claude Code" ;;
        gemini)      echo "Gemini CLI" ;;
        goose)       echo "Goose" ;;
        opencode)    echo "OpenCode" ;;
        copilot)     echo "GitHub Copilot" ;;
        cursor)      echo "Cursor" ;;
        windsurf)    echo "Windsurf" ;;
        cline)       echo "Cline" ;;
        kiro)        echo "Kiro" ;;
        trae)        echo "Trae" ;;
        roo-code)    echo "Roo Code" ;;
        *)           echo "$1" ;;
    esac
}

# ---------------------------------------------------------------------------
# Format adapters (for Tier 2 platforms)
# ---------------------------------------------------------------------------
generate_cursor_mdc() {
    target_dir="$1"
    skill_md="$SOURCE_DIR/SKILL.md"

    desc=""
    in_fm=false
    lnum=0
    while IFS= read -r line; do
        lnum=$((lnum + 1))
        if [ "$lnum" -eq 1 ]; then in_fm=true; continue; fi
        if $in_fm && [ "$line" = "---" ]; then break; fi
        if $in_fm; then
            case "$line" in
                description:*) desc="$(echo "$line" | sed 's/^description:[[:space:]]*//')" ;;
            esac
        fi
    done < "$skill_md"

    mdc_file="${target_dir}/${SKILL_NAME}.mdc"
    if [ "$DRY_RUN" = true ]; then
        info "[dry-run] Would generate Cursor .mdc: $mdc_file"
        return 0
    fi

    body="$(awk 'BEGIN{c=0} /^---$/{c++;next} c>=2{print}' "$skill_md")"
    mkdir -p "$target_dir"
    cat > "$mdc_file" <<MDCEOF
---
description: ${desc}
globs:
alwaysApply: true
---
${body}
MDCEOF
    success "Generated Cursor .mdc: $mdc_file"
}

generate_windsurf_rule() {
    target_dir="$1"
    is_global="$2"
    skill_md="$SOURCE_DIR/SKILL.md"

    body="$(awk 'BEGIN{c=0} /^---$/{c++;next} c>=2{print}' "$skill_md")"

    if [ "$is_global" = "true" ]; then
        global_file="$HOME/.codeium/windsurf/memories/global_rules.md"
        if [ "$DRY_RUN" = true ]; then
            info "[dry-run] Would append to Windsurf global_rules.md: $global_file"
            return 0
        fi
        mkdir -p "$(dirname "$global_file")"
        if [ -f "$global_file" ]; then
            awk -v begin_marker="<!-- BEGIN ${SKILL_NAME} -->" \
                -v end_marker="<!-- END ${SKILL_NAME} -->" '
                BEGIN { skip=0 }
                $0 == begin_marker { skip=1; next }
                $0 == end_marker   { skip=0; next }
                !skip { print }
            ' "$global_file" > "${global_file}.tmp"
            mv "${global_file}.tmp" "$global_file"
        fi
        cat >> "$global_file" <<WSEOF

<!-- BEGIN ${SKILL_NAME} -->
${body}
<!-- END ${SKILL_NAME} -->
WSEOF
        success "Appended to Windsurf global_rules.md"
    else
        rule_file="${target_dir}/${SKILL_NAME}.md"
        if [ "$DRY_RUN" = true ]; then
            info "[dry-run] Would generate Windsurf rule: $rule_file"
            return 0
        fi
        mkdir -p "$target_dir"
        printf '%s\n' "$body" > "$rule_file"
        success "Generated Windsurf rule: $rule_file"
    fi
}

generate_plain_rule() {
    target_dir="$1"
    filename="$2"
    skill_md="$SOURCE_DIR/SKILL.md"

    plain_file="${target_dir}/${filename}"
    if [ "$DRY_RUN" = true ]; then
        info "[dry-run] Would generate plain rule: $plain_file"
        return 0
    fi
    mkdir -p "$target_dir"
    awk 'BEGIN{c=0} /^---$/{c++;next} c>=2{print}' "$skill_md" > "$plain_file"
    success "Generated plain rule: $plain_file"
}

run_adapters() {
    plat="$1"
    dest="$2"
    case "$plat" in
        cursor)
            generate_cursor_mdc "$dest"
            ;;
        windsurf)
            if [ "$PROJECT_LEVEL" = true ]; then
                generate_windsurf_rule "$(pwd)/.windsurf/rules" "false"
            else
                generate_windsurf_rule "" "true"
            fi
            ;;
        cline|roo-code|trae)
            generate_plain_rule "$dest" "${SKILL_NAME}.md"
            ;;
    esac
}

# ---------------------------------------------------------------------------
# Create a symlink (with fallback to copy)
# ---------------------------------------------------------------------------
create_symlink() {
    target="$1"
    link_path="$2"

    if [ "$target" = "$link_path" ]; then return 0; fi

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
# Install to a single platform
# ---------------------------------------------------------------------------
install_to_platform() {
    plat="$1"
    dest="$(resolve_platform_path "$plat" "$SKILL_NAME")"
    display="$(platform_display "$plat")"

    if [ "$DRY_RUN" = true ]; then
        info "[dry-run] Would install to $display: $dest"
        run_adapters "$plat" "$dest"
        return 0
    fi

    create_symlink "$SOURCE_DIR" "$dest"
    success "Installed for $display → $dest"
    run_adapters "$plat" "$dest"
}

# ---------------------------------------------------------------------------
# Uninstall from all platforms
# ---------------------------------------------------------------------------
do_uninstall() {
    printf "\n${BOLD}Uninstalling skill: %s${NC}\n\n" "$SKILL_NAME"

    # Canonical location
    canonical="$HOME/.agents/skills/$SKILL_NAME"
    if [ -e "$canonical" ] || [ -L "$canonical" ]; then
        if [ "$DRY_RUN" = true ]; then
            info "[dry-run] Would remove: $canonical"
        else
            rm -rf "$canonical"
            success "Removed: $canonical"
        fi
    fi

    # Check all global platforms
    for plat in claude-code gemini goose opencode copilot; do
        dest="$(resolve_platform_path "$plat" "$SKILL_NAME")"
        if [ -e "$dest" ] || [ -L "$dest" ]; then
            if [ "$DRY_RUN" = true ]; then
                info "[dry-run] Would remove: $dest"
            else
                rm -rf "$dest"
                success "Removed: $dest ($(platform_display "$plat"))"
            fi
        fi
    done

    # Check project-level platforms
    for plat in cursor windsurf cline kiro trae roo-code copilot; do
        PROJECT_LEVEL=true
        dest="$(resolve_platform_path "$plat" "$SKILL_NAME")"
        if [ -e "$dest" ] || [ -L "$dest" ]; then
            if [ "$DRY_RUN" = true ]; then
                info "[dry-run] Would remove: $dest"
            else
                rm -rf "$dest"
                success "Removed: $dest ($(platform_display "$plat"))"
            fi
        fi
    done

    printf "\nDone.\n"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    printf "\n${BOLD}Universal Skill Installer${NC}\n\n"

    resolve_source
    if [ "$DRY_RUN" = false ]; then
        validate_source
    elif [ -d "$SOURCE_DIR" ]; then
        validate_source
    fi
    extract_skill_name
    info "Skill: $SKILL_NAME"
    info "Source: $SOURCE_DIR"

    if [ "$UNINSTALL" = true ]; then
        do_uninstall
        return 0
    fi

    # Install to canonical location first (if from git, already there)
    canonical="$HOME/.agents/skills/$SKILL_NAME"
    if ! is_git_url "$SOURCE" && [ "$SOURCE_DIR" != "$canonical" ]; then
        if [ "$DRY_RUN" = true ]; then
            info "[dry-run] Would copy to canonical: $canonical"
        else
            mkdir -p "$(dirname "$canonical")"
            rm -rf "$canonical"
            cp -R "$SOURCE_DIR" "$canonical"
            success "Copied to canonical: $canonical"
        fi
    fi

    # Determine which platforms to install to
    if [ -n "$PLATFORM" ]; then
        # Single platform
        install_to_platform "$PLATFORM"
    else
        # All detected platforms
        if [ "$PROJECT_LEVEL" = true ]; then
            platforms="$(detect_all_project_platforms)"
        else
            platforms="$(detect_all_global_platforms)"
        fi

        count=0
        for plat in $platforms; do
            install_to_platform "$plat"
            count=$((count + 1))
        done

        if [ $count -eq 0 ]; then
            warn "No platforms detected. Skill installed at canonical path only."
        fi
    fi

    # Summary
    printf "\n${BOLD}Done!${NC}\n"
    printf "  Canonical: %s\n" "$canonical"
    printf "  Invoke with: /${SKILL_NAME}\n\n"

    if [ "$DRY_RUN" = true ]; then
        printf "${YELLOW}Dry run — no changes made.${NC}\n\n"
    fi
}

main
