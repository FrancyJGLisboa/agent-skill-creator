---
permalink: /GITLAB_TEAM_REGISTRY.html
---

# Governed GitLab Team Skill Marketplace

This is the GitLab backend for the same schema-v2 departmental marketplace used
on GitHub. It generates GitLab CI, preserves bundles and quality evidence, creates
GitLab releases with `glab`, and installs from an exact protected tag.

## Provider differences

| Operation | GitHub backend | GitLab backend |
|---|---|---|
| Initialize | `--provider github` (default) | `--provider gitlab` |
| CI | `.github/workflows/` | `.gitlab-ci.yml` |
| Release transport | `gh skill publish` | `glab release create` |
| Pinned install | `gh skill install --pin` | Shallow Git clone at the tag, then copy |
| Copilot user scope | Managed by `gh skill` | `~/.copilot/skills/<skill>` |
| Copilot project scope | Managed by `gh skill` | `.github/skills/<skill>` in the current directory |

The governance and intake gates are identical. Only repository hosting, release,
CI, and installation transport differ.

## 1. Check prerequisites

```bash
python3 --version
git --version
glab --version
glab auth status
```

Use Python 3.10 or newer and an authenticated `glab` session with permission to
create the project, push branches, and create releases.

## 2. Initialize the GitLab marketplace

GitLab.com:

```bash
python3 scripts/team_marketplace.py init \
  --provider gitlab \
  --name "ACME Skills" \
  --repository acme/acme-skills \
  --marketplace ./acme-skills
```

Self-managed GitLab or a nested group:

```bash
python3 scripts/team_marketplace.py init \
  --provider gitlab \
  --host gitlab.acme.test \
  --name "ACME Skills" \
  --repository acme/data-platform/acme-skills \
  --marketplace ./acme-skills
```

The provider and host are recorded in `registry.json`. Existing schema-v2
registries without those fields remain backward-compatible and default to GitHub.

## 3. Create and push the project

```bash
cd ./acme-skills
git init
git add -A
git commit -m "feat: initialize governed ACME skill marketplace"
glab repo create acme/acme-skills --private --defaultBranch main
git remote add origin git@gitlab.com:acme/acme-skills.git
git branch -M main
git push -u origin main
```

For self-managed GitLab, authenticate `glab` against that host and replace the
remote hostname. If `glab repo create` adds `origin`, omit `git remote add`.

## 4. Configure governance

Follow the generated `GOVERNANCE.md`:

1. Protect the default branch and require merge requests.
2. Require Code Owner, department, platform, and security approval.
3. Require the `marketplace-check` pipeline.
4. Protect `v*.*.*` tags so only release administrators can create them.

The generated `.gitlab-ci.yml` runs marketplace checks for merge requests, the
default branch, and tags. GitLab settings remain the enforcement boundary.

## 5. Add and review a skill

```bash
python3 scripts/team_marketplace.py add ./report-skill \
  --department finance \
  --bundle analyst-starter \
  --marketplace ./acme-skills

python3 scripts/team_marketplace.py check --marketplace ./acme-skills
```

Commit the generated skill, registry, bundle, catalog, and ownership changes on a
branch. Merge only after the pipeline and required approvals pass.

## 6. Release an immutable version

```bash
python3 scripts/team_marketplace.py release \
  --tag v1.2.0 \
  --marketplace ./acme-skills
```

The command reruns every gate, then runs `glab release create v1.2.0 --ref HEAD`
with governed release notes. Never move or reuse a release tag.

## 7. Install, update, or roll back a bundle

Run a project-scope install from the consuming repository:

```bash
python3 /path/to/acme-skills/scripts/team_marketplace.py install \
  --bundle analyst-starter \
  --scope project \
  --pin v1.2.0 \
  --marketplace /path/to/acme-skills
```

Use `--scope user` for `~/.copilot/skills`. The backend shallow-clones
`https://<host>/<repository>.git` at the exact tag, copies only bundle paths, and
removes the temporary clone.

Update with a newer tag and `--force`. Roll back with the previous tag:

```bash
python3 /path/to/acme-skills/scripts/team_marketplace.py install \
  --bundle analyst-starter \
  --scope project \
  --pin v1.1.0 \
  --force \
  --marketplace /path/to/acme-skills
```

Private HTTPS clones use the machine's Git credential helper. Device management
must provision credentials before managed installation.

## Legacy fallback

`scripts/skill_registry.py` remains available for older flat registries and
non-Copilot platforms. New governed GitLab marketplaces should use
`team_marketplace.py --provider gitlab`.
