#!/usr/bin/env python3
"""Emit deterministic Semantic Recon source declarations into discovery.json."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Any, Mapping

def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "source"

def derive(discovery: Mapping[str, Any]) -> list[dict[str, str]]:
    interfaces=discovery.get("data_interfaces", {})
    if not isinstance(interfaces, Mapping) or not interfaces.get("applies"): return []
    kinds=interfaces.get("interface_types", [])
    if not isinstance(kinds, list): return []
    triggers=" ".join(str(x).lower() for x in discovery.get("trigger", []) if isinstance(x, str))
    reuse="recurring" if any(word in triggers for word in ("daily","weekly","monthly","annual","yearly","every ","recurring","scheduled")) else "one-off"
    risk=discovery.get("risk", {})
    impact=str(risk.get("tier", "low")).lower() if isinstance(risk, Mapping) else "low"
    sources=interfaces.get("authoritative_sources", [])
    labels=[str(x) for x in sources if isinstance(x, str)] or [str(kind) for kind in kinds]
    return [{"id":slug(label), "type":str(kind), "reuse":reuse, "impact":impact} for kind,label in zip(kinds, labels)]

def emit(path: Path) -> dict[str, Any]:
    data=json.loads(path.read_text(encoding="utf-8")); recon=data.get("semantic_recon")
    if not isinstance(recon, dict): recon={"applies": bool(derive(data))}
    derived = derive(data)
    existing = recon.get("sources", [])
    existing_by_id = {
        str(source.get("id")): source for source in existing
        if isinstance(source, Mapping) and source.get("id")
    } if isinstance(existing, list) else {}
    # A resumed run may have a contract binding that discovery cannot derive
    # again (for example, an imported or earlier-version discovery record).
    # Never erase it; otherwise a healthy contract triggers duplicate recon.
    if not derived and existing_by_id:
        recon["sources"] = list(existing_by_id.values())
    else:
        recon["sources"] = [
            {**existing_by_id.get(source["id"], {}), **source}
            for source in derived
        ]
    data["semantic_recon"]=recon
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    return data

if __name__=="__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("discovery_json"); args=parser.parse_args()
    result=emit(Path(args.discovery_json)); print(json.dumps(result["semantic_recon"], ensure_ascii=False))
