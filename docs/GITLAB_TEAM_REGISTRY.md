# GitLab Team Skill Registry — Supported Workflow

Use this workflow when ACME stores code in GitLab or cannot use GitHub CLI's
public-preview `gh skill` command.

## Current support boundary

| Capability | GitHub governed marketplace | GitLab workflow today |
|---|---|---|
| Central private Git repository | Yes | Yes |
| Validation and security intake | Yes | Yes, through `skill_registry.py` |
| Department bundles and schema-v2 catalog | Yes | Not implemented |
| Generated CI and governance files | GitHub Actions and CODEOWNERS | Not generated; configure GitLab separately |
| Protected semantic-version releases | Yes | Git tags plus GitLab protected-tag settings |
| Copilot installation | Exact pinned `gh skill install` | Copy-based install from a clone at an exact tag |

`team_marketplace.py` is currently a GitHub provider. It generates GitHub Actions,
stores a GitHub `OWNER/REPO`, publishes through `gh skill`, and installs through
`gh skill install`. Do not run it against GitLab and assume equivalent behavior.

## Phase A — Create the GitLab registry

### A1. Initialize locally

```bash
mkdir -p ~/work
cd ~/work/agent-skill-creator

python3 scripts/skill_registry.py init \
  --name "ACME Skills" \
  --registry ~/work/acme-skills-gitlab
```

The lightweight registry contains `registry.json` plus its `skills/` tree. It
retains the existing 17-platform copy-based installer.

### A2. Create the GitLab remote

Create a private empty project named `ACME/acme-skills` in GitLab. Then run:

```bash
cd ~/work/acme-skills-gitlab

git init
git add -A
git commit -m "feat: initialize ACME GitLab skill registry"
git branch -M main
git remote add origin git@gitlab.com:ACME/acme-skills.git
git push -u origin main
```

For self-managed GitLab, replace `gitlab.com` with the approved instance hostname.

### A3. Configure GitLab governance

In GitLab repository settings:

- Protect `main` and require merge requests.
- Configure approval rules for department, platform, and security reviewers.
- Add a root `CODEOWNERS` file when the GitLab tier supports required Code Owner approval.
- Protect tags matching `v*.*.*` and restrict tag creation to release maintainers.

The current factory does not generate `.gitlab-ci.yml`. If ACME requires automated
registry checks in GitLab CI, the platform team must add and maintain that pipeline.

## Phase B — Publish an individual skill

### B1. Run the individual gates

```bash
cd ~/work/agent-skill-creator

python3 scripts/validate.py ~/work/report-skill
python3 scripts/security_scan.py ~/work/report-skill
python3 scripts/check_pipeline.py ~/work/report-skill
python3 ~/work/report-skill/scripts/run_evals.py
```

Do not publish when a required gate fails.

### B2. Publish into the registry

```bash
python3 scripts/skill_registry.py publish ~/work/report-skill \
  --registry ~/work/acme-skills-gitlab \
  --tags finance,reports
```

`skill_registry.py publish` reruns validation and its security gate before copying.
It does not create department bundles, schema-v2 approval evidence, or GitLab CI.

### B3. Submit a merge request

```bash
cd ~/work/acme-skills-gitlab

git switch -c feat/add-acme-finance-report-skill
git add -A
git commit -m "feat: add ACME finance report skill"
git push -u origin feat/add-acme-finance-report-skill
```

Open the GitLab merge request, obtain the configured approvals, and merge it into
protected `main` after the GitLab pipeline passes.

## Phase C — Tag and distribute a reviewed version

### C1. Create an immutable tag

```bash
cd ~/work/acme-skills-gitlab

git switch main
git pull --ff-only
git tag -a v1.2.0 -m "ACME skill registry v1.2.0"
git push origin v1.2.0
```

The protected-tag rule is the enforcement boundary. Never move or reuse the tag.
A GitLab release record may be created from this tag through the GitLab UI or the
organization's approved `glab release create` workflow.

### C2. Install from the exact tag

```bash
git clone \
  --branch v1.2.0 \
  --depth 1 \
  git@gitlab.com:ACME/acme-skills.git \
  ~/work/acme-skills-v1.2.0

python3 ~/work/agent-skill-creator/scripts/skill_registry.py install report-skill \
  --registry ~/work/acme-skills-v1.2.0 \
  --platform copilot \
  --force
```

This installs one named skill. The lightweight GitLab registry does not currently
implement named bundles, so ACME deployment automation must enumerate the approved
skills for a release.

## Phase D — Update, roll back, and correct

### Update

Clone the new tag into a new directory and install from that registry:

```bash
git clone --branch v1.3.0 --depth 1 \
  git@gitlab.com:ACME/acme-skills.git \
  ~/work/acme-skills-v1.3.0

python3 ~/work/agent-skill-creator/scripts/skill_registry.py install report-skill \
  --registry ~/work/acme-skills-v1.3.0 \
  --platform copilot \
  --force
```

### Roll back

Reinstall from the previous immutable clone:

```bash
python3 ~/work/agent-skill-creator/scripts/skill_registry.py install report-skill \
  --registry ~/work/acme-skills-v1.2.0 \
  --platform copilot \
  --force
```

### Correct

Never edit an installed copy:

```bash
python3 ~/work/report-skill/scripts/evolve.py \
  --correct "ACME UK revenue closes one business day later"
```

Then rerun the gates, publish the corrected skill, submit a merge request, create a
new tag, and reinstall from that new tag.

## Future first-class GitLab provider

Equivalent GitHub/GitLab governance requires a new provider interface such as:

```bash
python3 scripts/team_marketplace.py init \
  --provider gitlab \
  --name "ACME Skills" \
  --repository ACME/acme-skills \
  --marketplace ./acme-skills
```

That option does not exist today. A complete implementation must generate GitLab CI,
use GitLab repository URLs and release operations, preserve schema-v2 bundles and
approvals, and replace `gh skill install` with a pinned GitLab-compatible installer.
