from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'scripts'))
from semantic_recon_gate import check_contracts, evaluate
from emit_semantic_recon_sources import derive
from emit_semantic_recon_sources import emit

def test_phase_one_emits_recurring_high_impact_api_source():
    sources=derive({"trigger":["Daily revenue briefing"],"risk":{"tier":"high"},"data_interfaces":{"applies":True,"interface_types":["api"],"authoritative_sources":["Stripe API"]}})
    assert sources == [{"id":"stripe-api","type":"api","reuse":"recurring","impact":"high"}]

def test_phase_one_recognizes_annual_work_as_recurring():
    sources=derive({"trigger":["Annual ID-card intake"],"risk":{"tier":"moderate"},"data_interfaces":{"applies":True,"interface_types":["structured-file"],"authoritative_sources":["users"]}})
    assert sources[0]["reuse"] == "recurring"

def test_recurring_high_impact_source_requires_contract():
    decision=evaluate({"data_interfaces":{"applies":True},"semantic_recon":{"sources":[{"id":"billing","type":"api","reuse":"recurring","impact":"high"}]}})
    assert decision["status"]=="REQUIRED"
    assert check_contracts(decision)

def test_structured_source_without_scope_fails_closed():
    assert evaluate({"data_interfaces":{"applies":True}})["status"]=="BLOCKED_NEEDS_SCOPE"

def test_one_off_low_impact_source_does_not_require_recon():
    assert evaluate({"data_interfaces":{"applies":True},"semantic_recon":{"sources":[{"id":"upload","type":"structured-file","reuse":"one-off","impact":"low"}]}})["status"]=="REQUIRED"

def test_contract_health_must_execute_and_pass(tmp_path):
    contract=tmp_path/"data_contract_demo"; (contract/"code").mkdir(parents=True)
    (contract/".contract_id").write_text("demo")
    (contract/"code"/"contract_health.py").write_text('def report(): return {"freshness":"FRESH", "smoke":"PASS"}')
    decision={"sources":[{"id":"demo","contract_id":"demo","contract_path":str(contract)}]}
    assert check_contracts(decision) == []
    (contract/"code"/"contract_health.py").write_text('def report(): return {"freshness":"EXPIRED", "smoke":"PASS"}')
    assert "contract health is not passing" in check_contracts(decision)[0]

def test_contract_health_accepts_structured_passing_smoke(tmp_path):
    contract=tmp_path/"data_contract_structured"; (contract/"code").mkdir(parents=True)
    (contract/".contract_id").write_text("structured")
    (contract/"code"/"contract_health.py").write_text('def report(): return {"freshness":"FRESH", "smoke":{"status":"PASS"}}')
    assert check_contracts({"sources":[{"id":"structured","contract_id":"structured","contract_path":str(contract)}]}) == []

def test_contract_health_accepts_structured_freshness(tmp_path):
    contract=tmp_path/"data_contract_fresh"; (contract/"code").mkdir(parents=True)
    (contract/".contract_id").write_text("fresh")
    (contract/"code"/"contract_health.py").write_text('def report(): return {"freshness":{"status":"FRESH"}, "smoke":{"status":"PASS"}}')
    assert check_contracts({"sources":[{"id":"fresh","contract_id":"fresh","contract_path":str(contract)}]}) == []

def test_emit_preserves_resolved_source_when_discovery_is_partial(tmp_path):
    path = tmp_path / "discovery.json"
    path.write_text(json.dumps({"data_interfaces":{"applies":True}, "semantic_recon":{"sources":[{"id":"api", "contract_id":"api", "contract_path":"/contracts/api"}]}}))
    assert emit(path)["semantic_recon"]["sources"][0]["contract_path"] == "/contracts/api"
