#!/usr/bin/env python3
"""
Security Scanner for Generated Agent Skills.

Scans a skill directory for hardcoded API keys, sensitive files, and dangerous
Python patterns that could pose security risks.

Usage:
    python3 scripts/security_scan.py path/to/skill/
    python3 scripts/security_scan.py path/to/skill/ --json

Exit codes:
    0 - Clean (no issues found)
    1 - Issues found (one or more security issues detected)
"""

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skill_document import SkillDoc  # noqa: E402


# --- API Key Patterns ---
# Each entry: (pattern_name, compiled_regex, description, severity)

API_KEY_PATTERNS: list[tuple[str, re.Pattern, str, str]] = [
    (
        "OpenAI API Key",
        re.compile(r"sk-[a-zA-Z0-9]{20,}"),
        "Hardcoded OpenAI API key detected",
        "high",
    ),
    (
        "AWS Access Key",
        re.compile(r"AKIA[A-Z0-9]{16}"),
        "Hardcoded AWS access key ID detected",
        "high",
    ),
    (
        "GitHub Personal Access Token",
        re.compile(r"ghp_[a-zA-Z0-9]{36}"),
        "Hardcoded GitHub personal access token detected",
        "high",
    ),
    (
        "GitHub Fine-Grained Personal Access Token",
        re.compile(r"github_pat_[a-zA-Z0-9_]{22,255}"),
        "Hardcoded GitHub fine-grained personal access token detected",
        "high",
    ),
    (
        "GitHub OAuth/App Token",
        re.compile(r"gh[ousr]_[a-zA-Z0-9]{36,255}"),
        "Hardcoded GitHub OAuth, user-to-server, server, or refresh token detected",
        "high",
    ),
    (
        "GitLab Personal Access Token",
        re.compile(r"glpat-[a-zA-Z0-9\-]{20}"),
        "Hardcoded GitLab personal access token detected",
        "high",
    ),
    (
        "Slack Token",
        re.compile(r"xox[bprs]-[a-zA-Z0-9\-]+"),
        "Hardcoded Slack token detected",
        "high",
    ),
    (
        "Anthropic API Key",
        # Listed before the OpenAI "sk-" pattern; the hyphens in "sk-ant-"
        # stop the OpenAI regex from matching, so order is for clarity only.
        re.compile(r"sk-ant-[a-zA-Z0-9_\-]{20,}"),
        "Hardcoded Anthropic API key detected",
        "high",
    ),
    (
        "Stripe Secret Key",
        re.compile(r"[sr]k_live_[0-9a-zA-Z]{16,}"),
        "Hardcoded Stripe live secret/restricted key detected",
        "high",
    ),
    (
        "npm Access Token",
        re.compile(r"npm_[A-Za-z0-9]{36}"),
        "Hardcoded npm access token detected",
        "high",
    ),
    (
        "Google API Key",
        re.compile(r"AIza[0-9A-Za-z_\-]{35}"),
        "Hardcoded Google API key detected",
        "high",
    ),
    (
        "Hugging Face Token",
        re.compile(r"hf_[a-zA-Z0-9]{34,}"),
        "Hardcoded Hugging Face access token detected",
        "high",
    ),
    (
        "JSON Web Token",
        # Three base64url segments; the first two header/payload parts of a
        # JWT both start with "eyJ" (base64 of '{"'). Medium severity: a JWT
        # is not always a long-lived secret and can appear legitimately in docs.
        re.compile(r"eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+"),
        "Possible hardcoded JSON Web Token (JWT) detected",
        "medium",
    ),
    (
        "Generic Secret",
        re.compile(
            r"""(api[_\-]?key|secret|token|password)\s*[:=]\s*["'][^"']{8,}["']""",
            re.IGNORECASE,
        ),
        "Possible hardcoded secret (generic key/token/password pattern)",
        "medium",
    ),
]


# --- Sensitive File Names ---

SENSITIVE_FILES: dict[str, str] = {
    ".env": "Environment file may contain secrets",
    "credentials.json": "Credentials file may contain API keys or passwords",
    "secrets.json": "Secrets file may contain sensitive data",
    "api_keys.json": "API keys file may contain hardcoded keys",
}


# --- Dangerous Python Patterns ---
# Each entry: (pattern_name, compiled_regex, description, severity)

PYTHON_DANGER_PATTERNS: list[tuple[str, re.Pattern, str, str]] = [
    (
        "eval() usage",
        re.compile(r"\beval\s*\("),
        "Use of eval() can execute arbitrary code; avoid unless strictly necessary",
        "high",
    ),
    (
        "exec() usage",
        re.compile(r"\bexec\s*\("),
        "Use of exec() can execute arbitrary code; avoid unless strictly necessary",
        "high",
    ),
    (
        "os.system() with concatenation",
        re.compile(r"os\.system\s*\([^)]*[\+f\"']"),
        "os.system() with string concatenation is vulnerable to shell injection",
        "high",
    ),
    (
        "subprocess with shell=True",
        re.compile(r"subprocess\.call\s*\([^)]*shell\s*=\s*True"),
        "subprocess.call() with shell=True is vulnerable to shell injection",
        "high",
    ),
    (
        "__import__() dynamic import",
        re.compile(r"__import__\s*\("),
        "Dynamic imports via __import__() can load arbitrary modules",
        "medium",
    ),
]


# --- Instruction-body injection patterns (markdown/prose files) ---
# Skill-file prompt injection executes at LOAD time, before any code runs, so
# the instruction body is scanned as an attack surface in its own right.

INSTRUCTION_INJECTION_PATTERNS: list[tuple[str, re.Pattern, str, str]] = [
    (
        "Instruction override",
        re.compile(
            r"(?i)\b(?:ignore|disregard|forget)\s+(?:all\s+|any\s+)?"
            r"(?:previous|prior|above|earlier)\s+(?:instructions?|rules?|prompts?|guidance)"
        ),
        "Instruction-override phrase in skill prose (prompt-injection marker)",
        "high",
    ),
    (
        "Concealment directive",
        re.compile(
            r"(?i)(?:\b(?:do\s+not|don't|never)\s+(?:tell|inform|notify)\s+the\s+user"
            r"|\bwithout\s+(?:telling|informing|asking|notifying)\s+the\s+user)"
        ),
        "Directive to hide behavior from the user",
        "high",
    ),
    (
        "Exfiltration directive",
        re.compile(
            r"(?i)\b(?:send|post|upload|transmit|forward|exfiltrate)\b[^.\n]{0,60}"
            r"\b(?:api[\s_-]?keys?|credentials?|tokens?|secrets?|passwords?|"
            r"environment\s+variables?)\b"
        ),
        "Directive to transmit secrets/credentials",
        "high",
    ),
]

# Invisible/bidi characters that can hide instructions from human review.
# Escaped on purpose: the scanner's own source must not contain hidden unicode.
HIDDEN_UNICODE_RE = re.compile(
    "[\\u200b-\\u200f\\u202a-\\u202e\\u2060-\\u2064\\u2066-\\u2069\\ufeff]"
)

# Long base64-shaped runs in prose files (possible encoded payload).
ENCODED_BLOB_RE = re.compile(r"[A-Za-z0-9+/=]{200,}")

PROSE_EXTENSIONS: set[str] = {".md", ".markdown", ".rst", ".txt"}

# Hosts a script may reach without declaring them in SKILL.md frontmatter.
# api.anthropic.com is the platform's own API (the shipped judge harness in
# run_evals.py calls it), not a third-party dependency.
ENDPOINT_SKIP_HOSTS: set[str] = {"localhost", "127.0.0.1", "0.0.0.0", "example.com", "www.example.com", "api.anthropic.com"}  # noqa: S104

_URL_HOST_RE = re.compile(r"https?://([a-zA-Z0-9.-]+)")


# File extensions to scan for content patterns
TEXT_EXTENSIONS: set[str] = {
    ".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".cfg",
    ".ini", ".sh", ".bash", ".zsh", ".env", ".conf", ".xml", ".html",
    ".css", ".js", ".ts", ".jsx", ".tsx", ".sql", ".csv", ".rst",
}

# Maximum file size to scan (skip very large files to avoid performance issues)
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

# Directories to skip during scanning
SKIP_DIRS: set[str] = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "env",
    ".pytest_cache", ".mypy_cache", "dist", "build",
}


def _is_text_file(file_path: Path) -> bool:
    """
    Determine if a file is likely a text file that should be scanned.

    Uses the file extension to decide. Falls back to attempting to read
    a small portion of the file if the extension is unrecognized.

    Args:
        file_path: Path to the file.

    Returns:
        True if the file should be scanned for content patterns.
    """
    if file_path.suffix.lower() in TEXT_EXTENSIONS:
        return True

    # For files with no extension or unrecognized extensions, try reading a sample
    if file_path.suffix == "" or file_path.suffix.lower() not in {
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg",
        ".pdf", ".zip", ".tar", ".gz", ".bz2", ".xz",
        ".exe", ".dll", ".so", ".dylib", ".whl", ".egg",
        ".pyc", ".pyo", ".class", ".o", ".a",
        ".mp3", ".mp4", ".wav", ".avi", ".mov",
        ".ttf", ".otf", ".woff", ".woff2", ".eot",
        ".sqlite", ".db",
    }:
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1024)
            # Check for null bytes (binary indicator)
            if b"\x00" in chunk:
                return False
            return True
        except (OSError, PermissionError):
            return False

    return False


def _scan_file_content(
    file_path: Path,
    skill_dir: Path,
) -> list[dict]:
    """
    Scan a single file for security issues in its content.

    Args:
        file_path: Absolute path to the file.
        skill_dir: Root directory of the skill (for relative path display).

    Returns:
        List of issue dictionaries found in this file.
    """
    issues: list[dict] = []
    relative_path = str(file_path.relative_to(skill_dir))

    try:
        file_size = file_path.stat().st_size
    except OSError:
        return issues

    if file_size > MAX_FILE_SIZE_BYTES:
        return issues

    if not _is_text_file(file_path):
        return issues

    try:
        lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except (OSError, PermissionError):
        return issues

    is_python = file_path.suffix.lower() == ".py"
    is_prose = file_path.suffix.lower() in PROSE_EXTENSIONS

    for line_num, line in enumerate(lines, start=1):
        # Hidden/bidi unicode is suspicious anywhere: it can conceal
        # instructions or reorder what a human reviewer sees.
        if HIDDEN_UNICODE_RE.search(line):
            issues.append({
                "severity": "high",
                "file": relative_path,
                "line": line_num,
                "pattern": "Hidden unicode",
                "description": "Invisible/bidirectional unicode character (can hide instructions from review)",
            })

        if is_prose:
            for pattern_name, regex, description, severity in INSTRUCTION_INJECTION_PATTERNS:
                if regex.search(line):
                    issues.append({
                        "severity": severity,
                        "file": relative_path,
                        "line": line_num,
                        "pattern": pattern_name,
                        "description": description,
                    })
            if ENCODED_BLOB_RE.search(line):
                issues.append({
                    "severity": "medium",
                    "file": relative_path,
                    "line": line_num,
                    "pattern": "Encoded blob",
                    "description": "Long base64-shaped run in instruction file (possible encoded payload)",
                })

        # Check API key patterns against all text files
        for pattern_name, regex, description, severity in API_KEY_PATTERNS:
            match = regex.search(line)
            if match:
                issues.append({
                    "severity": severity,
                    "file": relative_path,
                    "line": line_num,
                    "pattern": pattern_name,
                    "description": description,
                })

        # Check Python-specific patterns only in .py files
        if is_python:
            for pattern_name, regex, description, severity in PYTHON_DANGER_PATTERNS:
                match = regex.search(line)
                if match:
                    issues.append({
                        "severity": severity,
                        "file": relative_path,
                        "line": line_num,
                        "pattern": pattern_name,
                        "description": description,
                    })

    return issues


def security_scan(skill_path: str) -> dict:
    """
    Perform a security scan on a skill directory.

    Checks for hardcoded API keys, sensitive files, and dangerous code patterns.

    Args:
        skill_path: Path to the skill directory to scan.

    Returns:
        Dictionary with keys:
            - ``clean`` (bool): True if no issues were found.
            - ``issues`` (list[dict]): List of issue dictionaries. Each has:
                - ``severity`` (str): "high", "medium", or "low"
                - ``file`` (str): Relative file path
                - ``line`` (int): Line number (0 for file-level issues)
                - ``pattern`` (str): Pattern name that triggered the issue
                - ``description`` (str): Human-readable description
    """
    issues: list[dict] = []

    skill_dir = Path(skill_path).resolve()

    # --- Check: directory exists ---
    if not skill_dir.exists():
        return {
            "clean": False,
            "issues": [{
                "severity": "high",
                "file": str(skill_dir),
                "line": 0,
                "pattern": "missing_directory",
                "description": f"Path does not exist: {skill_dir}",
            }],
        }

    if not skill_dir.is_dir():
        return {
            "clean": False,
            "issues": [{
                "severity": "high",
                "file": str(skill_dir),
                "line": 0,
                "pattern": "not_a_directory",
                "description": f"Path is not a directory: {skill_dir}",
            }],
        }

    # --- Check: sensitive files ---
    for sensitive_name, description in SENSITIVE_FILES.items():
        sensitive_path = skill_dir / sensitive_name
        if sensitive_path.exists():
            issues.append({
                "severity": "high",
                "file": sensitive_name,
                "line": 0,
                "pattern": "Sensitive file",
                "description": description,
            })

    # Also check subdirectories for .env files
    for root, dirs, files in os.walk(skill_dir):
        root_path = Path(root)

        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in files:
            file_path = root_path / filename
            relative = str(file_path.relative_to(skill_dir))

            # Check for .env files anywhere in the tree
            if filename == ".env" and relative != ".env":
                issues.append({
                    "severity": "high",
                    "file": relative,
                    "line": 0,
                    "pattern": "Sensitive file",
                    "description": "Environment file may contain secrets",
                })

            # Check for sensitive JSON files in subdirectories
            if filename in ("credentials.json", "secrets.json", "api_keys.json"):
                if relative != filename:  # Not already caught at root level
                    issues.append({
                        "severity": "high",
                        "file": relative,
                        "line": 0,
                        "pattern": "Sensitive file",
                        "description": SENSITIVE_FILES.get(
                            filename, "Sensitive file detected"
                        ),
                    })

    # --- Scan file contents ---
    for root, dirs, files in os.walk(skill_dir):
        root_path = Path(root)

        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in files:
            file_path = root_path / filename
            file_issues = _scan_file_content(file_path, skill_dir)
            issues.extend(file_issues)

    # --- Least-privilege cross-check: script URLs must be declared ---
    issues.extend(_scan_undeclared_endpoints(skill_dir))

    # Sort issues: high first, then medium, then low
    severity_order = {"high": 0, "medium": 1, "low": 2}
    issues.sort(key=lambda x: (severity_order.get(x["severity"], 3), x["file"], x["line"]))

    return {
        "clean": len(issues) == 0,
        "issues": issues,
    }


def _declared_hosts(skill_dir: Path) -> set[str]:
    """Hostnames the SKILL.md frontmatter declares (dependencies, schema
    expectations, and an optional metadata.permissions network list)."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return set()
    try:
        doc = SkillDoc.from_path(skill_md)
    except OSError:
        return set()
    hosts: set[str] = set()
    for parent, child in (("metadata", "dependencies"), ("metadata", "schema_expectations")):
        for entry in doc.list_of_objects(parent, child):
            url = entry.get("url", "")
            match = _URL_HOST_RE.match(url)
            if match:
                hosts.add(match.group(1).lower())
    return hosts


def _scan_undeclared_endpoints(skill_dir: Path) -> list[dict]:
    """Flag network endpoints reached by scripts but not declared in SKILL.md.

    Least-privilege gate: every host a skill's code talks to must appear in the
    frontmatter (dependencies / schema_expectations), so a reviewer can audit
    egress without reading every script.
    """
    declared = _declared_hosts(skill_dir)
    issues: list[dict] = []
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return issues
    for path in sorted(scripts_dir.rglob("*")):
        if path.suffix.lower() not in {".py", ".sh", ".bash"} or not path.is_file():
            continue
        if "tests" in path.relative_to(scripts_dir).parts:
            continue  # test fixtures legitimately contain URL literals
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line_num, line in enumerate(text.splitlines(), start=1):
            for match in _URL_HOST_RE.finditer(line):
                host = match.group(1).lower()
                if host in ENDPOINT_SKIP_HOSTS or host in declared:
                    continue
                if host == "example.com" or host.endswith(".example.com"):
                    continue  # RFC 2606 documentation domain
                issues.append({
                    "severity": "medium",
                    "file": str(path.relative_to(skill_dir)),
                    "line": line_num,
                    "pattern": "Undeclared network endpoint",
                    "description": (
                        f"Script reaches '{host}' but SKILL.md declares no such "
                        "dependency; declare it in metadata.dependencies or remove the call"
                    ),
                })
    return issues


def _print_human_readable(result: dict, skill_path: str) -> None:
    """
    Print security scan results in a human-readable format.

    Args:
        result: The scan result dictionary.
        skill_path: The path that was scanned (for display).
    """
    print(f"Security scan: {skill_path}")
    print(f"{'=' * 60}")

    if result["clean"]:
        print("Status: CLEAN")
        print("\nNo security issues found.")
    else:
        print(f"Status: ISSUES FOUND ({len(result['issues'])})")

        # Count by severity
        high = sum(1 for i in result["issues"] if i["severity"] == "high")
        medium = sum(1 for i in result["issues"] if i["severity"] == "medium")
        low = sum(1 for i in result["issues"] if i["severity"] == "low")
        print(f"\n  High: {high}  Medium: {medium}  Low: {low}")

        print()
        for issue in result["issues"]:
            severity_label = issue["severity"].upper().ljust(6)
            location = issue["file"]
            if issue["line"] > 0:
                location += f":{issue['line']}"
            print(f"  [{severity_label}] {location}")
            print(f"           Pattern: {issue['pattern']}")
            print(f"           {issue['description']}")
            print()

    print(f"{'=' * 60}")


def main() -> None:
    """CLI entry point for the security scanner."""
    if len(sys.argv) < 2:
        print(
            "Usage: python3 scripts/security_scan.py <skill-path> [--json]\n"
            "\n"
            "Arguments:\n"
            "  skill-path    Path to the skill directory to scan\n"
            "\n"
            "Options:\n"
            "  --json        Output results as JSON to stdout\n"
            "\n"
            "Exit codes:\n"
            "  0  Clean (no issues)\n"
            "  1  Issues found (one or more security issues)\n",
            file=sys.stderr,
        )
        sys.exit(1)

    skill_path = sys.argv[1]
    use_json = "--json" in sys.argv

    result = security_scan(skill_path)

    if use_json:
        print(json.dumps(result, indent=2))
    else:
        _print_human_readable(result, skill_path)

    sys.exit(0 if result["clean"] else 1)


if __name__ == "__main__":
    main()
