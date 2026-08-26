# Semantic-contract product-success experiment

Use this protocol to decide whether governed semantics improve reliable outcomes. It
does not permit a broad semantic-registry build and does not treat a synthetic score
as evidence of model improvement.

## Portfolio

Use one business domain and three independently discoverable skills:

1. `single_authority`: one definition and one authoritative source.
2. `context_resolution`: two legitimate meanings where an underspecified question
   must produce `ask` rather than a guessed answer.
3. `semantic_drift`: a source or definition changes after the initial successful run;
   the skill must detect staleness and produce `refuse_unknown` until owner review.

Collect real recurring questions from domain users. Do not generate the benchmark
questions with the model under test.

## Four isolated configurations

Run every question in a clean consumer session under exactly these conditions:

1. `model_data`: model and data tools only.
2. `model_data_documents`: add existing prose, dashboards, notebooks, and queries.
3. `model_semantic_contracts`: add the approved machine-readable contracts.
4. `model_contracts_skills_evals`: add governed skills and their eval behavior.

Keep model version, question wording, data snapshot, and permissions fixed. Store raw
transcripts and outputs outside the skill package and reference them using
`evidence_path` plus `evidence_sha256`; never paste sensitive content into marketplace
telemetry. Compute the lowercase digest with `shasum -a 256 <evidence-file>`.

## Expected and observed fields

For every case, the domain owner records the expected `skill`, `action`, `source`,
`definition_version`, `vintage`, and `drift_detected`. The independent consumer records
the same fields plus an immutable evidence path for every configuration.

Valid actions are `answer`, `ask`, and `refuse_unknown`. A case is reliable only when
all six dimensions match. This deliberately prevents a plausible answer with the
wrong definition, source, or vintage from receiving partial success.

Run:

```bash
python3 scripts/semantic_experiment.py experiment.json --output semantic-report.json
```

The report says `causal_claim: not_established_by_score_alone`. Review session
isolation, evidence quality, sample size, and repeated runs before attributing a delta
to semantic contracts.

## Stop rule

Stop after the three-skill portfolio produces inspectable evidence. Improve the core
only when a failure repeats across skills. Do not build a standalone semantic layer,
ontology editor, data catalog, warehouse query engine, or autonomous definition
generator. Those remain integrations unless repeated customer evidence shows the
control plane cannot govern them adequately.
