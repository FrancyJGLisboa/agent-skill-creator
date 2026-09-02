from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_runner_uses_codex_exec_with_workspace_safeguards():
 text=(ROOT/'scripts/semantic_recon_runner.py').read_text()
 assert "'codex','exec'" in text
 assert '"SEMANTIC_RECON_SANDBOX", "workspace-write"' in text
 assert "'--ask-for-approval'" not in text
 assert "--result-json" in text

def test_runner_only_allows_explicit_known_sandboxes():
 text=(ROOT/'scripts/semantic_recon_runner.py').read_text()
 assert 'SEMANTIC_RECON_SANDBOX' in text
 assert '"danger-full-access"' in text

def test_runner_always_writes_a_parseable_fail_handoff():
 text=(ROOT/'scripts/semantic_recon_runner.py').read_text()
 assert "def write_failure" in text
 assert '"status": "FAIL"' in text

def test_runner_has_a_bounded_execution_time():
 text=(ROOT/'scripts/semantic_recon_runner.py').read_text()
 assert "SEMANTIC_RECON_TIMEOUT_SECONDS" in text
 assert "TimeoutExpired" in text
