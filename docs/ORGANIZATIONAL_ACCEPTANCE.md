# Blind Organizational Acceptance Protocol

Use this protocol to decide whether an unfamiliar organization can operate a governed
skill marketplace without help from the product's implementers. It is an acceptance
test, not a guided demo.

## Pass condition

Four independent roles must complete this lifecycle using only published product
documentation and legitimate marketplace artifacts:

```text
create → publish → discover → install → invoke → invoke → update → rollback
       → quarantine → blocked install → retire → recreate
```

The run fails when a role receives an undocumented command, reads implementation or
test code to discover intended behavior, edits `registry.json` manually, or asks the
product team for procedural assistance. Record the failure and improve the product or
documentation before starting a new run. Do not coach the active run.

## Isolation contract

Create four separate agent sessions: organizational administrator, workflow expert,
marketplace operator, and cross-department consumer. Give every session:

- A distinct temporary `HOME` and clean working directory.
- No conversation history or private notes from another role.
- Only the repository README, linked public documentation, its role brief, and
  artifacts the previous role legitimately published.
- Separate command and output logs, including errors and requests for assistance.

Do not share local source paths, unpublished registry contents, intended commands, or
expected fixes. Do not allow implementation inspection until a documented operation
has failed. After failure, a diagnostic agent may inspect implementation, but the
acceptance run remains failed and must be restarted from clean state after the fix.

For local automation, create isolated homes and workspaces under one temporary root.
Never point a role at a developer's real home directory. A local Git bare repository
may stand in for the remote, but handoffs must occur through commits and immutable
tags, not shared working-tree files.

## Role briefs and gates

### 1. Organizational administrator

Goal: initialize a marketplace with at least two departments, real owner identities,
an approval policy, supported platforms, and a starter bundle.

Use repeatable initialization options so this policy is generated rather than written
into `registry.json` by hand:

```bash
python3 scripts/team_marketplace.py init \
  --name "ACME Skills" --repository ACME/acme-skills \
  --department finance=finance-owner \
  --department operations=operations-owner \
  --approver acme-platform --approver acme-security \
  --supported-platform github-copilot \
  --starter-bundle analyst-starter \
  --marketplace ./acme-skills
```

The administrator passes when the governed repository is committed and published for
the operator. An empty starter bundle is valid and has this shape:

```json
{
  "name": "analyst-starter",
  "skills": []
}
```

Do not seed the bundle with a nonexistent skill merely to make it non-empty.

### 2. Workflow expert

Goal: create a complete skill from workflow evidence, confirm its decision contract,
pass the factory gates and representative run, and submit it through the documented
marketplace intake path.

For a skill whose answer depends on organizational meaning, this role is also the
domain authority or must obtain recorded approval from the named domain owner. It
defines scope, grain, units, source precedence, ambiguity behavior, and review timing.
The agent may structure and test those statements; the marketplace operator may
enforce their presence and freshness. Neither may invent or approve the meaning.

When the target marketplace is known, the generated submission must carry the exact
published `owners` and `approval_status` required by that marketplace. When it is not
known, the factory must not invent organizational identities or approval.

### 3. Marketplace operator

Goal: review the submitted evidence, admit the skill into its department and starter
bundle, publish an immutable semantic-version release, publish a strictly newer
version, quarantine it, retire it, and recreate it as a fresh generation.

The operator must block release when a semantic definition is overdue, but must return
it to the named domain owner for review rather than editing the definition.

Releases are immutable snapshots. A release tag is created only from the reviewed,
committed marketplace state; it is never moved or reused. Update requires a strictly
newer skill version and a new release tag. Rollback selects the old tag—it does not
rewrite the newer release.

Recreation is not an update. It retires the previous generation and admits a new
generation with a fresh lineage identity, version reset to `1.0.0`, no inherited
attestations or compatibility certification, and a recorded reason linking it to its
predecessor. Repository history remains available; sensitive-data erasure is a
separate privileged process and is outside this test.

After retiring the existing identity, run:

```bash
python3 scripts/team_marketplace.py recreate ./replacement-skill \
  --department finance \
  --reason "The original decision model is no longer valid" \
  --marketplace ./acme-skills
```

`recreate` requires the replacement source to be exactly version `1.0.0` and pass
fresh validation, security, pipeline, eval, clean-commit, and representative-run
attestation gates. It produces approved generation 2 with a new `lineage_id`, retains
the prior bundle membership, clears certifications, and records the predecessor
lineage and reason as a tombstone.

### 4. Cross-department consumer

Goal: from a clean project, discover the skill by its question or outcome without
knowing its repository path, install the exact published release, invoke it twice,
install the newer release, roll back to the original release, and prove quarantine
blocks another installation.

Project-scoped installs must run from the consumer project, never the marketplace
clone. In a local Git test, check out or shallow-clone the exact immutable tag into a
temporary source directory, then run the documented local install from the consumer
project. A copy from an untagged or dirty marketplace checkout is not release proof.

```bash
git -C /tmp/acme-skills checkout --detach v1.2.0
cd /tmp/clean-consumer-project
python3 /tmp/acme-skills/scripts/team_marketplace.py install \
  --bundle analyst-starter --scope project --local --pin v1.2.0 \
  --marketplace /tmp/acme-skills
```

## Evidence record

For every gate, retain the role, clean-workspace identifier, command, exit status,
relevant output, source commit, release tag, installed version, and whether assistance
was requested. The final report must distinguish:

- **Passed:** every gate completed from documentation alone.
- **Product defect:** documented behavior failed or contradicted the implementation.
- **Documentation defect:** the capability existed but the role could not find or
  execute it from published instructions.
- **Environment blocked:** an external service or credential was unavailable; do not
  count this as product success.

Agent success is evidence of documentation-driven operability, not proof of human
usability. After this protocol passes, repeat the same roles with people who did not
build the product.

See the first completed run and the defects it exposed in
[the 2026-08-25 four-role report](acceptance/2026-08-25-organizational-run.md).
