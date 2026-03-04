#!/bin/sh
# install-template.sh — Cross-platform skill installation script
# This file is a template. During skill generation, {{SKILL_NAME}} is replaced
# with the actual skill name and the result is shipped as install.sh inside
# every generated skill package.
#
# POSIX-compatible (works in bash, dash, zsh, ash, etc.)
# Exit codes:
#   0 — Success
#   1 — Validation failed (missing or malformed SKILL.md)
#   2 — Platform not detected
#   3 — Permission denied

set -eu

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SKILL_NAME="{{SKILL_NAME}}"
VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ---------------------------------------------------------------------------
# Colors (disabled when stdout is not a terminal)
# ---------------------------------------------------------------------------
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    BOLD=''
    NC=''
fi

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
info()    { printf "${BLUE}[INFO]${NC}  %s\n" "$1"; }
success() { printf "${GREEN}[OK]${NC}    %s\n" "$1"; }
warn()    { printf "${YELLOW}[WARN]${NC}  %s\n" "$1"; }
error()   { printf "${RED}[ERROR]${NC} %s\n" "$1" >&2; }

# ---------------------------------------------------------------------------
# Usage / help
# ---------------------------------------------------------------------------
show_help() {
    cat <<EOF
${BOLD}install.sh${NC} — Install the ${BOLD}${SKILL_NAME}${NC} skill (v${VERSION})

USAGE
    ./install.sh [OPTIONS]

OPTIONS
    --platform PLATFORM   Explicit platform selection. One of:
                          claude-code, copilot, cursor, windsurf,
                          cline, codex, gemini, kiro, trae, goose,
                          opencode, roo-code, antigravity, universal
    --project             Install at project level (current directory)
    --path PATH           Custom install path (overrides detection)
    --all                 Install to ALL detected tool paths at once
    --dry-run             Show what would happen without making changes
    -h, --help            Show this help message

EXAMPLES
    ./install.sh                          # Auto-detect platform, user-level
    ./install.sh --project                # Auto-detect platform, project-level
    ./install.sh --platform cursor        # Force Cursor, user-level
    ./install.sh --path ~/my-skills/      # Custom destination
    ./install.sh --all                    # Install to every detected tool
    ./install.sh --dry-run                # Preview without installing
EOF
}

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
PLATFORM=""
PROJECT_LEVEL=false
CUSTOM_PATH=""
DRY_RUN=false
INSTALL_ALL=false

parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            --platform)
                [ $# -ge 2 ] || { error "Missing value for --platform"; exit 1; }
                PLATFORM="$2"
                shift 2
                ;;
            --project)
                PROJECT_LEVEL=true
                shift
                ;;
            --path)
                [ $# -ge 2 ] || { error "Missing value for --path"; exit 1; }
                CUSTOM_PATH="$2"
                shift 2
                ;;
            --all)
                INSTALL_ALL=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# ---------------------------------------------------------------------------
# SKILL.md validation
# ---------------------------------------------------------------------------
validate_skill_md() {
    skill_md="${SCRIPT_DIR}/SKILL.md"

    if [ ! -f "$skill_md" ]; then
        error "SKILL.md not found in ${SCRIPT_DIR}"
        error "Every skill package must contain a valid SKILL.md file."
        exit 1
    fi

    # Check that the file starts with YAML frontmatter delimiter
    first_line="$(head -n 1 "$skill_md")"
    if [ "$first_line" != "---" ]; then
        error "SKILL.md must start with YAML frontmatter (---)"
        exit 1
    fi

    # Verify required frontmatter fields: name and description
    in_frontmatter=false
    found_name=false
    found_description=false
    line_num=0

    while IFS= read -r line; do
        line_num=$((line_num + 1))

        if [ "$line_num" -eq 1 ]; then
            in_frontmatter=true
            continue
        fi

        if $in_frontmatter && [ "$line" = "---" ]; then
            break
        fi

        if $in_frontmatter; then
            case "$line" in
                name:*) found_name=true ;;
                description:*) found_description=true ;;
            esac
        fi
    done < "$skill_md"

    if ! $found_name; then
        error "SKILL.md frontmatter is missing required field: name"
        exit 1
    fi

    if ! $found_description; then
        error "SKILL.md frontmatter is missing required field: description"
        exit 1
    fi

    success "SKILL.md validated (name and description present)"
}

# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------
SUPPORTED_PLATFORMS="claude-code, copilot, cursor, windsurf, cline, codex, gemini, kiro, trae, goose, opencode, roo-code, antigravity, universal"

detect_platform() {
    # If explicitly provided, validate and return it.
    if [ -n "$PLATFORM" ]; then
        case "$PLATFORM" in
            claude-code|copilot|cursor|windsurf|cline|codex|gemini|\
            kiro|trae|goose|opencode|roo-code|antigravity|universal)
                info "Platform explicitly set to: ${PLATFORM}"
                return 0
                ;;
            *)
                error "Unknown platform: ${PLATFORM}"
                error "Supported: ${SUPPORTED_PLATFORMS}"
                exit 2
                ;;
        esac
    fi

    # Auto-detection: check user-level config directories.
    # Order matters — check most specific / least ambiguous first.
    if [ -d "${HOME}/.claude" ]; then
        PLATFORM="claude-code"
    elif [ -d "${HOME}/.cursor" ] || [ -d ".cursor" ]; then
        PLATFORM="cursor"
    elif [ -d "${HOME}/.codeium/windsurf" ] || [ -d ".windsurf" ]; then
        PLATFORM="windsurf"
    elif [ -d "${HOME}/.cline" ] || [ -d ".clinerules" ]; then
        PLATFORM="cline"
    elif [ -d "${HOME}/.gemini" ]; then
        PLATFORM="gemini"
    elif [ -d ".kiro" ]; then
        PLATFORM="kiro"
    elif [ -d ".trae" ]; then
        PLATFORM="trae"
    elif [ -d ".roo" ]; then
        PLATFORM="roo-code"
    elif [ -d "${HOME}/.config/goose" ]; then
        PLATFORM="goose"
    elif [ -d "${HOME}/.config/opencode" ]; then
        PLATFORM="opencode"
    elif [ -d "${HOME}/.agents" ]; then
        PLATFORM="universal"
    elif [ -d "${HOME}/.copilot" ] || [ -d ".github" ]; then
        PLATFORM="copilot"
    else
        error "Could not auto-detect any supported AI coding platform."
        error "Use --platform PLATFORM to specify one explicitly."
        error "Supported: ${SUPPORTED_PLATFORMS}"
        exit 2
    fi

    info "Auto-detected platform: ${PLATFORM}"
}

# ---------------------------------------------------------------------------
# Detect all installed platforms (for --all)
# ---------------------------------------------------------------------------
detect_all_platforms() {
    ALL_PLATFORMS=""
    if [ -d "${HOME}/.claude" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} claude-code"
    fi
    if [ -d "${HOME}/.cursor" ] || [ -d ".cursor" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} cursor"
    fi
    if [ -d "${HOME}/.codeium/windsurf" ] || [ -d ".windsurf" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} windsurf"
    fi
    if [ -d "${HOME}/.cline" ] || [ -d ".clinerules" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} cline"
    fi
    if [ -d "${HOME}/.gemini" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} gemini"
    fi
    if [ -d ".kiro" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} kiro"
    fi
    if [ -d ".trae" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} trae"
    fi
    if [ -d ".roo" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} roo-code"
    fi
    if [ -d "${HOME}/.config/goose" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} goose"
    fi
    if [ -d "${HOME}/.config/opencode" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} opencode"
    fi
    if [ -d "${HOME}/.copilot" ] || [ -d ".github" ]; then
        ALL_PLATFORMS="${ALL_PLATFORMS} copilot"
    fi
    # Always include universal
    ALL_PLATFORMS="${ALL_PLATFORMS} universal"

    # Trim leading space
    ALL_PLATFORMS="$(printf '%s' "$ALL_PLATFORMS" | sed 's/^ //')"

    if [ -z "$ALL_PLATFORMS" ]; then
        ALL_PLATFORMS="universal"
    fi
}

# ---------------------------------------------------------------------------
# Install path resolution
# ---------------------------------------------------------------------------
# Sets INSTALL_DIR based on platform, project-level flag, or custom path.
resolve_install_path() {
    # Custom path takes precedence over everything.
    if [ -n "$CUSTOM_PATH" ]; then
        INSTALL_DIR="${CUSTOM_PATH}"
        info "Using custom install path: ${INSTALL_DIR}"
        return 0
    fi

    base=""

    if $PROJECT_LEVEL; then
        # Project-level: paths are relative to the current working directory.
        case "$PLATFORM" in
            claude-code)   base=".claude/skills" ;;
            copilot)       base=".github/skills" ;;
            cursor)        base=".cursor/rules" ;;
            windsurf)      base=".windsurf/rules" ;;
            cline)         base=".clinerules" ;;
            codex)         base=".agents/skills" ;;
            gemini)        base=".gemini/skills" ;;
            kiro)          base=".kiro/skills" ;;
            trae)          base=".trae/rules" ;;
            goose)         base=".agents/skills" ;;
            opencode)      base=".agents/skills" ;;
            roo-code)      base=".roo/rules" ;;
            antigravity)   base=".agents/skills" ;;
            universal)     base=".agents/skills" ;;
        esac
        INSTALL_DIR="$(pwd)/${base}/${SKILL_NAME}"
    else
        # User-level: paths are under the home directory.
        case "$PLATFORM" in
            claude-code)   base="${HOME}/.claude/skills" ;;
            copilot)       base="${HOME}/.copilot/skills" ;;
            cursor)        base="${HOME}/.cursor/rules" ;;
            windsurf)      base="${HOME}/.codeium/windsurf/skills" ;;
            cline)         base="${HOME}/.cline/rules" ;;
            codex)         base="${HOME}/.agents/skills" ;;
            gemini)        base="${HOME}/.gemini/skills" ;;
            kiro)          base="${HOME}/.agents/skills" ;;
            trae)          base="${HOME}/.agents/skills" ;;
            goose)         base="${HOME}/.config/goose/skills" ;;
            opencode)      base="${HOME}/.config/opencode/skills" ;;
            roo-code)      base="${HOME}/.agents/skills" ;;
            antigravity)   base="${HOME}/.agents/skills" ;;
            universal)     base="${HOME}/.agents/skills" ;;
        esac
        INSTALL_DIR="${base}/${SKILL_NAME}"
    fi

    info "Install directory: ${INSTALL_DIR}"
}

# ---------------------------------------------------------------------------
# Format adapters — convert SKILL.md to platform-native formats
# ---------------------------------------------------------------------------

# Generate a .mdc file for Cursor from SKILL.md
generate_cursor_mdc() {
    target_dir="$1"
    skill_md="${SCRIPT_DIR}/SKILL.md"

    # Extract description from frontmatter
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

    if $DRY_RUN; then
        info "Would generate Cursor .mdc: ${mdc_file}"
        return 0
    fi

    # Extract body (everything after second ---)
    body="$(awk 'BEGIN{c=0} /^---$/{c++;next} c>=2{print}' "$skill_md")"

    cat > "$mdc_file" <<MDCEOF
---
description: ${desc}
globs:
alwaysApply: true
---
${body}
MDCEOF
    success "Generated Cursor .mdc: ${mdc_file}"
}

# Generate a .md rule file for Windsurf (.windsurf/rules/ or global_rules.md)
generate_windsurf_rule() {
    target_dir="$1"
    is_global="$2"  # "true" or "false"
    skill_md="${SCRIPT_DIR}/SKILL.md"

    # Extract body (everything after second ---)
    body="$(awk 'BEGIN{c=0} /^---$/{c++;next} c>=2{print}' "$skill_md")"

    if [ "$is_global" = "true" ]; then
        # Append to global_rules.md with idempotent markers
        global_file="${HOME}/.codeium/windsurf/memories/global_rules.md"

        if $DRY_RUN; then
            info "Would append to Windsurf global_rules.md: ${global_file}"
            return 0
        fi

        mkdir -p "$(dirname "$global_file")"

        # Remove existing block if present (idempotent, exact match)
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

        # Append new block
        cat >> "$global_file" <<WSEOF

<!-- BEGIN ${SKILL_NAME} -->
${body}
<!-- END ${SKILL_NAME} -->
WSEOF
        success "Appended to Windsurf global_rules.md"
    else
        # Project-level: create a .md rule file
        rule_file="${target_dir}/${SKILL_NAME}.md"

        if $DRY_RUN; then
            info "Would generate Windsurf rule: ${rule_file}"
            return 0
        fi

        mkdir -p "$target_dir"
        printf '%s\n' "$body" > "$rule_file"
        success "Generated Windsurf rule: ${rule_file}"
    fi
}

# Generate plain markdown (strip YAML frontmatter) for Cline/Roo/Trae
generate_plain_rule() {
    target_dir="$1"
    filename="$2"
    skill_md="${SCRIPT_DIR}/SKILL.md"

    plain_file="${target_dir}/${filename}"

    if $DRY_RUN; then
        info "Would generate plain rule: ${plain_file}"
        return 0
    fi

    mkdir -p "$target_dir"
    awk 'BEGIN{c=0} /^---$/{c++;next} c>=2{print}' "$skill_md" > "$plain_file"
    success "Generated plain rule: ${plain_file}"
}

# ---------------------------------------------------------------------------
# Universal .agents/skills/ secondary install (symlink or copy)
# ---------------------------------------------------------------------------
install_universal_secondary() {
    # Skip if primary target is already .agents/
    case "$PLATFORM" in
        codex|antigravity|universal) return 0 ;;
    esac

    universal_dir="${HOME}/.agents/skills/${SKILL_NAME}"

    if $DRY_RUN; then
        info "Would create universal symlink: ${universal_dir} -> ${INSTALL_DIR}"
        return 0
    fi

    mkdir -p "${HOME}/.agents/skills"

    # Remove existing entry if present
    if [ -e "$universal_dir" ] || [ -L "$universal_dir" ]; then
        rm -rf "$universal_dir"
    fi

    # Try symlink first, fallback to copy
    if ln -s "$INSTALL_DIR" "$universal_dir" 2>/dev/null; then
        success "Universal symlink: ${universal_dir} -> ${INSTALL_DIR}"
    elif cp -R "$INSTALL_DIR" "$universal_dir" 2>/dev/null; then
        success "Universal copy: ${universal_dir}"
    else
        warn "Could not create universal path at ${universal_dir}"
    fi
}

# ---------------------------------------------------------------------------
# File installation
# ---------------------------------------------------------------------------
install_files() {
    # Collect the list of files to install.
    # We copy everything in SCRIPT_DIR except the install script itself.
    file_count=0
    install_script_name="$(basename "$0")"

    if $DRY_RUN; then
        printf "\n${BOLD}Dry-run mode — no files will be copied.${NC}\n\n"
        info "Would create directory: ${INSTALL_DIR}"
        for file in "${SCRIPT_DIR}"/*; do
            [ -e "$file" ] || continue
            fname="$(basename "$file")"
            # Skip the install script itself
            [ "$fname" = "$install_script_name" ] && continue
            info "Would copy: ${fname}"
            file_count=$((file_count + 1))
        done
        # Also handle dotfiles
        for file in "${SCRIPT_DIR}"/.*; do
            [ -e "$file" ] || continue
            fname="$(basename "$file")"
            if [ "$fname" = "." ] || [ "$fname" = ".." ]; then continue; fi
            info "Would copy: ${fname}"
            file_count=$((file_count + 1))
        done
        printf "\n"
        info "Total files: ${file_count}"
        return 0
    fi

    # Clean existing install for idempotency (remove stale files from prior installs).
    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
    fi

    # Create destination directory.
    if ! mkdir -p "$INSTALL_DIR" 2>/dev/null; then
        error "Cannot create directory: ${INSTALL_DIR}"
        error "Check file permissions or run with appropriate privileges."
        exit 3
    fi

    # Copy files.
    for file in "${SCRIPT_DIR}"/*; do
        [ -e "$file" ] || continue
        fname="$(basename "$file")"
        [ "$fname" = "$install_script_name" ] && continue

        if ! cp -R "$file" "${INSTALL_DIR}/" 2>/dev/null; then
            error "Failed to copy ${fname} to ${INSTALL_DIR}/"
            error "Check file permissions."
            exit 3
        fi
        file_count=$((file_count + 1))
    done

    # Copy dotfiles (if any).
    for file in "${SCRIPT_DIR}"/.*; do
        [ -e "$file" ] || continue
        fname="$(basename "$file")"
        [ "$fname" = "." ] || [ "$fname" = ".." ] && continue

        if ! cp -R "$file" "${INSTALL_DIR}/" 2>/dev/null; then
            error "Failed to copy ${fname} to ${INSTALL_DIR}/"
            error "Check file permissions."
            exit 3
        fi
        file_count=$((file_count + 1))
    done

    success "Copied ${file_count} file(s) to ${INSTALL_DIR}"
}

# ---------------------------------------------------------------------------
# Run format adapters based on platform
# ---------------------------------------------------------------------------
run_adapters() {
    case "$PLATFORM" in
        cursor)
            generate_cursor_mdc "$INSTALL_DIR"
            ;;
        windsurf)
            if $PROJECT_LEVEL; then
                generate_windsurf_rule "$(pwd)/.windsurf/rules" "false"
            else
                generate_windsurf_rule "" "true"
            fi
            ;;
        cline)
            generate_plain_rule "$INSTALL_DIR" "${SKILL_NAME}.md"
            ;;
        roo-code)
            generate_plain_rule "$INSTALL_DIR" "${SKILL_NAME}.md"
            ;;
        trae)
            generate_plain_rule "$INSTALL_DIR" "${SKILL_NAME}.md"
            ;;
    esac
}

# ---------------------------------------------------------------------------
# Activation instructions
# ---------------------------------------------------------------------------
print_activation_instructions() {
    if $DRY_RUN; then
        return 0
    fi

    printf "\n${GREEN}${BOLD}Installation complete!${NC}\n\n"

    case "$PLATFORM" in
        claude-code)
            printf "To activate the skill in Claude Code:\n"
            printf "  1. Start a new Claude Code session.\n"
            printf "  2. The skill will be loaded automatically from:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. Use trigger phrases defined in the skill's description.\n"
            ;;
        copilot)
            printf "To activate the skill in GitHub Copilot:\n"
            printf "  1. Open your project in VS Code or the GitHub CLI.\n"
            printf "  2. The skill is available at:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. Reference the skill in your Copilot instructions.\n"
            ;;
        cursor)
            printf "To activate the skill in Cursor:\n"
            printf "  1. Open your project in Cursor.\n"
            printf "  2. The rule is loaded automatically from:\n"
            printf "     ${BOLD}${INSTALL_DIR}/${SKILL_NAME}.mdc${NC}\n"
            printf "  3. Use trigger phrases to invoke the skill.\n"
            ;;
        windsurf)
            printf "To activate the skill in Windsurf:\n"
            if $PROJECT_LEVEL; then
                printf "  1. Open your project in Windsurf.\n"
                printf "  2. The rule is loaded from .windsurf/rules/\n"
            else
                printf "  1. Open Windsurf.\n"
                printf "  2. The skill was added to global_rules.md.\n"
            fi
            printf "  3. Use trigger phrases to invoke the skill.\n"
            ;;
        cline)
            printf "To activate the skill in Cline:\n"
            printf "  1. Open your project in VS Code with Cline.\n"
            printf "  2. The rule is loaded from:\n"
            printf "     ${BOLD}${INSTALL_DIR}/${SKILL_NAME}.md${NC}\n"
            printf "  3. Cline will pick up the rule automatically.\n"
            ;;
        codex)
            printf "To activate the skill in OpenAI Codex CLI:\n"
            printf "  1. Start a new Codex CLI session.\n"
            printf "  2. The skill is available at:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. Codex reads from ~/.agents/skills/ automatically.\n"
            ;;
        gemini)
            printf "To activate the skill in Gemini CLI:\n"
            printf "  1. Start a new Gemini CLI session.\n"
            printf "  2. The skill is available at:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. The skill will be loaded automatically.\n"
            ;;
        kiro)
            printf "To activate the skill in Kiro:\n"
            printf "  1. Open your project in Kiro.\n"
            printf "  2. The skill is available at:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. Kiro reads from .kiro/skills/ automatically.\n"
            ;;
        trae)
            printf "To activate the skill in Trae:\n"
            printf "  1. Open your project in Trae.\n"
            printf "  2. The rule is loaded from:\n"
            printf "     ${BOLD}${INSTALL_DIR}/${SKILL_NAME}.md${NC}\n"
            printf "  3. Use trigger phrases to invoke the skill.\n"
            ;;
        goose)
            printf "To activate the skill in Goose:\n"
            printf "  1. Start a new Goose session.\n"
            printf "  2. The skill is available at:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. Goose reads from ~/.config/goose/skills/ automatically.\n"
            ;;
        opencode)
            printf "To activate the skill in OpenCode:\n"
            printf "  1. Start a new OpenCode session.\n"
            printf "  2. The skill is available at:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. OpenCode reads from ~/.config/opencode/skills/ automatically.\n"
            ;;
        roo-code)
            printf "To activate the skill in Roo Code:\n"
            printf "  1. Open your project in VS Code with Roo Code.\n"
            printf "  2. The rule is loaded from:\n"
            printf "     ${BOLD}${INSTALL_DIR}/${SKILL_NAME}.md${NC}\n"
            printf "  3. Roo Code will pick up the rule automatically.\n"
            ;;
        antigravity)
            printf "To activate the skill in Antigravity:\n"
            printf "  1. Open your project.\n"
            printf "  2. The skill is available at:\n"
            printf "     ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n"
            printf "  3. Antigravity reads from .agents/skills/ automatically.\n"
            ;;
        universal)
            printf "The skill is installed at the universal path:\n"
            printf "  ${BOLD}${INSTALL_DIR}/SKILL.md${NC}\n\n"
            printf "Tools that read ~/.agents/skills/ (Codex CLI, Gemini CLI,\n"
            printf "Kiro, Antigravity, and others) will discover it automatically.\n"
            ;;
    esac

    printf "\n"
}

# ---------------------------------------------------------------------------
# Install for a single platform
# ---------------------------------------------------------------------------
install_single() {
    detect_platform
    resolve_install_path
    install_files
    run_adapters
    install_universal_secondary
    print_activation_instructions

    if $DRY_RUN; then
        info "Dry run complete. No changes were made."
    else
        success "Skill '${SKILL_NAME}' installed successfully for ${PLATFORM}."
    fi
}

# ---------------------------------------------------------------------------
# Install for all detected platforms (--all)
# ---------------------------------------------------------------------------
install_all() {
    detect_all_platforms
    info "Installing to all detected platforms: ${ALL_PLATFORMS}"
    printf "%-40s\n" "----------------------------------------"

    installed_count=0
    first_non_agents_dir=""
    for plat in $ALL_PLATFORMS; do
        printf "\n"
        info "--- Installing for: ${plat} ---"
        PLATFORM="$plat"
        resolve_install_path
        install_files
        run_adapters
        installed_count=$((installed_count + 1))
        # Remember the first non-.agents/ install dir for universal symlink
        if [ -z "$first_non_agents_dir" ]; then
            case "$plat" in
                codex|antigravity|universal) ;;
                *) first_non_agents_dir="$INSTALL_DIR" ;;
            esac
        fi
    done

    # Create universal symlink from the first non-.agents/ install
    if [ -n "$first_non_agents_dir" ]; then
        INSTALL_DIR="$first_non_agents_dir"
        install_universal_secondary
    fi

    printf "\n"
    if $DRY_RUN; then
        info "Dry run complete. No changes were made."
    else
        success "Skill '${SKILL_NAME}' installed to ${installed_count} platform(s)."
    fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    printf "${BOLD}Installing skill: ${SKILL_NAME}${NC}\n"
    printf "%-40s\n" "----------------------------------------"

    parse_args "$@"
    validate_skill_md

    if $INSTALL_ALL; then
        install_all
    else
        install_single
    fi

    exit 0
}

main "$@"
