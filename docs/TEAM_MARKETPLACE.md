# Governed Team Skill Marketplace — Complete Timeline

Use this page from top to bottom. It contains every command needed to create an
ACME marketplace, admit individual skills, release approved bundles, install them
in VS Code Copilot Agent Mode, and update or roll them back.

```text
ONE-TIME SETUP                         REPEATED FOR EACH CHANGE

Prerequisites → Initialize → Protect   Create skill → Add → Review → Release
                                                            ↓
Correction ← Use ← Pinned install ← Approved semantic-version tag
```

![ACME governed skill marketplace lifecycle](assets/acme-skill-marketplace-lifecycle.png)

## What each component does

| Component | Responsibility |
|---|---|
| `agent-skill-creator` | Creates and verifies one individual skill from workflow evidence. |
| Governed Git repository | Catalogs skills by department, runs gates, records approval, and builds bundles. |
| `gh skill` | Installs exact approved skill paths from a pinned repository release. |
| ACME device management | Runs the managed install command on approved endpoints. |

Plugins are a secondary compatibility channel for supported CLI hosts. For VS Code
Copilot Agent Mode, the primary path is a pinned `gh skill install` operation.

## Phase A — One-time platform setup

### A1. Confirm prerequisites

Run these commands on the platform developer's machine:

```bash
python3 --version
gh --version
gh auth status
gh skill --help
```

Required state:

- Python 3.10 or newer.
- Authenticated GitHub CLI 2.90 or newer.
- `gh skill` available. It remains a public-preview command.
- Permission to create and protect the target GitHub repository.

### A2. Initialize the marketplace

Run from the `agent-skill-creator` repository:

```bash
python3 scripts/team_marketplace.py init \
  --name "ACME Skills" \
  --repository ACME/acme-skills \
  --marketplace ./acme-skills
```

This creates:

```text
acme-skills/
├── skills/<department>/<skill>/
├── bundles/
├── scripts/team_marketplace.py
├── registry.json
├── CATALOG.md
├── CODEOWNERS
├── GOVERNANCE.md
└── .github/workflows/
```

To migrate an existing schema-v1 registry, initialize with one additional option:

```bash
python3 scripts/team_marketplace.py init \
  --name "ACME Skills" \
  --repository ACME/acme-skills \
  --from-registry ./legacy-registry \
  --marketplace ./acme-skills
```

Migration never grants approval. Migrated skills remain `draft` until their source,
owners, scripts, and quality evidence are reviewed.

### A3. Put the scaffold in GitHub

```bash
cd ./acme-skills
git init
git add -A
git commit -m "feat: initialize governed ACME skill marketplace"
gh repo create ACME/acme-skills --private --source=. --push
```

Do not add individual skills before the repository governance is configured.

### A4. Protect releases and reviews

Open `GOVERNANCE.md` in the generated repository. Configure the GitHub default
branch ruleset to require:

- Pull requests and CODEOWNER review.
- The `governed-marketplace` status check.
- Department-owner plus platform/security approval.
- No force pushes or branch deletion.

Configure a tag ruleset for `v*.*.*` that restricts tag creation, updates, and
deletion to release administrators. GitHub settings are required here; there is no
local command that can prove the organization applied its rulesets correctly.

## Phase B — Repeat for each individual skill

### B1. Create and verify one skill

In an installed agent environment, provide the real workflow evidence:

```text
/agent-skill-creator Create a skill from the attached ACME monthly reporting workflow.
```

The factory must finish with a representative result—not only generated files. The
skill is ready for marketplace intake only after validation, pipeline, security, and
eval gates pass.

Before `add`, its `SKILL.md` metadata must include real values:

```yaml
metadata:
  author: ACME Finance
  version: 1.2.0
  approval_status: approved
  owners: [acme-finance-skills]
```

Do not declare `allowed-tools: shell` or `allowed-tools: bash`. Copilot must request
runtime permission when a reviewed script actually needs execution.

### B2. Add the skill to a department and bundle

Run from the `agent-skill-creator` repository, pointing at the marketplace clone:

```bash
python3 scripts/team_marketplace.py add ./report-skill \
  --department finance \
  --bundle analyst-starter \
  --marketplace ./acme-skills
```

`add` runs the gates before copying. A failure stops intake. A successful add writes
the skill to `skills/finance/report-skill/`, updates `registry.json`, regenerates the
bundle manifest and catalog, and updates CODEOWNERS.

### B3. Run the repository check

```bash
python3 scripts/team_marketplace.py check \
  --marketplace ./acme-skills
```

The check refuses draft skills, failed gates, duplicate identities, missing owners,
unsafe tool pre-approval, path traversal, inconsistent metadata, and broken bundle
manifests.

### B4. Submit the governed change

```bash
cd ./acme-skills
git switch -c feat/add-finance-report-skill
git add -A
git commit -m "feat: add ACME finance report skill"
git push -u origin feat/add-finance-report-skill
gh pr create --fill
```

Department, platform, and security owners review the pull request. Merge only after
the generated GitHub Actions checks and required reviews pass.

## Phase C — Release and deliver approved bundles

### C1. Release an immutable version

After the approved pull request reaches the protected default branch:

```bash
git switch main
git pull --ff-only
python3 scripts/team_marketplace.py release \
  --tag v1.2.0 \
  --marketplace .
```

`release` reruns marketplace checks, requires a semantic-version tag, and calls
`gh skill publish`. Do not reuse or move an existing release tag.

### C2. Install the approved bundle

User scope makes the bundle available across the analyst's projects:

```bash
python3 scripts/team_marketplace.py install \
  --bundle analyst-starter \
  --scope user \
  --pin v1.2.0 \
  --marketplace ./acme-skills
```

Project scope installs it only for the current repository:

```bash
python3 scripts/team_marketplace.py install \
  --bundle analyst-starter \
  --scope project \
  --pin v1.2.0 \
  --marketplace ./acme-skills
```

The wrapper issues one exact command per bundled skill:

```bash
gh skill install ACME/acme-skills skills/finance/report-skill \
  --agent github-copilot \
  --scope user \
  --pin v1.2.0
```

The marketplace controls what may be installed. ACME endpoint management controls
how that command reaches 200 managed devices.

### C3. Update or roll back

Update by explicitly installing a newer approved release:

```bash
python3 scripts/team_marketplace.py install \
  --bundle analyst-starter \
  --scope user \
  --pin v1.3.0 \
  --force \
  --marketplace ./acme-skills
```

Roll back by reinstalling the last known-good tag:

```bash
python3 scripts/team_marketplace.py install \
  --bundle analyst-starter \
  --scope user \
  --pin v1.2.0 \
  --force \
  --marketplace ./acme-skills
```

There is no moving “latest” channel in the governed workflow. Every managed change
names the exact release that should be present.

### C4. Correct a skill through the repository

Never edit an installed copy. Capture the correction in the skill source:

```bash
python3 ./report-skill/scripts/evolve.py \
  --correct "ACME UK revenue closes one business day later"
```

Then repeat Phase B: run the skill's tests, add the corrected version, open a pull
request, obtain approval, publish a new semantic-version release, and install the new
pin. Corrections therefore follow the same evidence and governance path as the first
release.

## Command map

| When | Command | Result |
|---|---|---|
| Once | `team_marketplace.py init` | Creates the governed repository scaffold. |
| Every intake | `team_marketplace.py add` | Gates and copies one skill into a department and bundle. |
| Before PR/release | `team_marketplace.py check` | Verifies the complete marketplace state. |
| After approved merge | `team_marketplace.py release --tag vX.Y.Z` | Publishes an immutable approved release. |
| Deployment/update/rollback | `team_marketplace.py install --pin vX.Y.Z` | Installs exact bundled skills for Copilot. |
