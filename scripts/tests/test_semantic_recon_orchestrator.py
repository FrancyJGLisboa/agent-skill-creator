from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'scripts'))
from semantic_recon_orchestrator import orchestrate

def test_required_source_blocks_without_configured_runner(tmp_path):
 skill=tmp_path/'skill'; skill.mkdir(); (skill/'discovery.json').write_text(json.dumps({"data_interfaces":{"applies":True},"semantic_recon":{"sources":[{"id":"stripe","type":"api","reuse":"recurring","impact":"high"}]}}))
 assert orchestrate(skill, runner="")["status"] == "BLOCKED_NO_RUNNER"

def test_runner_contract_resumes_build(tmp_path):
 contract=tmp_path/'data_contract_stripe'; (contract/'code').mkdir(parents=True); (contract/'.contract_id').write_text('stripe'); (contract/'code/contract_health.py').write_text('def report(): return {"freshness":"FRESH", "smoke":"PASS"}')
 runner=tmp_path/'runner.py'; runner.write_text("import json,sys; p=sys.argv[sys.argv.index('--result-json')+1]; open(p,'w').write(json.dumps({'status':'PASS','contract_id':'stripe','contract_path':sys.argv[1]}))")
 skill=tmp_path/'skill'; skill.mkdir(); (skill/'discovery.json').write_text(json.dumps({"data_interfaces":{"applies":True},"semantic_recon":{"sources":[{"id":"stripe","type":"api","reuse":"recurring","impact":"high"}]}}))
 result=orchestrate(skill, f'{sys.executable} {runner} {contract}')
 assert result['status']=='RESUMED'
 assert json.loads((skill/'discovery.json').read_text())['semantic_recon']['sources'][0]['contract_path'] == str(contract)
