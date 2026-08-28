# Capability Resolver Contract v1

The capability resolver turns a verified runtime identity and execution context
into the exact skill artifacts an agent may use. It is a **read-only control-plane
API**: it decides and records an authorized view; it never executes a skill,
edits a workspace, or silently installs an update.

The authoritative source remains the governed marketplace release. A resolver is
an adapter over that release, not a second mutable registry.

## Resolution invariant

For one request, the resolver returns a deterministic, auditable set:

```text
authorized skills = published ∩ policy-permitted ∩ environment-compatible
```

Every returned artifact is pinned to an immutable marketplace release, exact skill
version, and content hash. A runtime must execute only the returned artifact, or
reject it when its hash does not match.

## API

### Request

`POST /v1/skill-resolutions`

```json
{
  "agent": {
    "id": "codex-cli",
    "version": "1.0.0",
    "platform": "codex",
    "attestation": "opaque-runtime-attestation"
  },
  "user": {
    "subject": "user:alice@example.com",
    "groups": ["finance-analysts"]
  },
  "project": {
    "id": "github:acme/quarterly-close",
    "ref": "refs/heads/main",
    "trust_tier": "internal"
  },
  "environment": {
    "id": "workstation:managed-macos",
    "class": "managed",
    "network_zone": "corporate"
  },
  "requested_skills": ["finance/report-skill"],
  "channel": "stable"
}
```

`agent`, `user`, `project`, and `environment` are required. `requested_skills` is
optional: omitted means discover the authorized catalog; supplied means resolve
only those canonical skill IDs. `channel` defaults to `stable` and may be
`stable`, `pilot`, or `latest` when the caller is eligible for that channel.

Identity claims must come from the authenticated transport or a verified
attestation. The service must not trust caller-supplied group, project, device, or
environment claims without verification.

### Local signed-attestation adapter

The repository's local adapter accepts a signed JSON attestation instead of identity
flags. It verifies a canonical JSON HMAC-SHA-256 using the server-side
`SKILL_RESOLVER_ATTESTATION_SECRET`. The registry configures its trusted issuer,
audience (the marketplace repository), and maximum TTL; new marketplaces default to
five minutes. The token must include:

```json
{
  "issuer": "local-development",
  "audience": "ACME/acme-skills",
  "issued_at": "2026-08-28T14:00:00Z",
  "expires_at": "2026-08-28T14:05:00Z",
  "nonce": "at-least-16-unique-characters",
  "claims": {
    "agent": "codex-cli",
    "user": "user:alice@example.com",
    "groups": ["finance-analysts"],
    "project": "github:acme/quarterly-close",
    "environment": "managed-macos",
    "platform": "codex"
  },
  "device": {"id": "device:mdm-123", "managed": true},
  "signature": "lowercase-hex-hmac-sha256"
}
```

The HMAC key must never be distributed to agents or employee workstations. A hosted
production resolver should replace this adapter with OIDC/JWT verification against
the identity and device-management providers, plus server-side nonce replay control.

### Successful response

```json
{
  "resolution_id": "res_01JQ7F5GMDDAYWZTW2E9Q5P4QH",
  "resolved_at": "2026-08-28T14:00:00Z",
  "policy": {
    "id": "policy_finance_managed_v3",
    "revision": "sha256:3f0b..."
  },
  "marketplace_release": {
    "repository": "ACME/acme-skills",
    "ref": "v2026.08.3",
    "commit_sha": "a1b2c3d4..."
  },
  "skills": [
    {
      "id": "finance/report-skill",
      "version": "1.2.3",
      "artifact": {
        "uri": "https://registry.example/v1/artifacts/sha256:8a9b...",
        "sha256": "8a9b...",
        "media_type": "application/vnd.agent-skill+tar"
      },
      "compatibility": {
        "platform": "codex",
        "certification_id": "cert_01J..."
      },
      "permissions": {
        "declared": ["read:repository", "read:finance-ledger"],
        "runtime_approval_required": ["shell"]
      },
      "lifecycle": "published",
      "expires_at": "2026-08-28T15:00:00Z"
    }
  ],
  "denied": []
}
```

The `artifact.uri` is a short-lived, authenticated retrieval URL. It is not a
permission grant: the artifact service rechecks authorization on download.
`expires_at` controls cache freshness, not artifact validity. The returned hash and
marketplace commit remain valid evidence after expiry.

## Decision rules

1. Accept only published skills from an immutable marketplace release.
2. Match policy using verified identity, project, and environment attributes.
3. Require passing compatibility certification for the calling platform and exact
   skill version.
4. Select the channel’s approved version; never substitute an unpinned “current”
   version after resolution.
5. Exclude quarantined, deprecated, retired, or policy-denied skills.

If a later quarantine or emergency revocation occurs, the resolver stops issuing new
results immediately. Runtimes must revalidate at expiry and may receive a signed
revocation event before expiry.

## Denials and errors

The endpoint returns `200` for a valid request, including partial results. Each
unavailable requested skill appears in `denied` with a stable machine-readable code:

```json
{
  "id": "finance/report-skill",
  "code": "POLICY_DENIED",
  "message": "This skill is not authorized for the current project environment."
}
```

Allowed codes: `NOT_FOUND`, `POLICY_DENIED`, `NOT_PUBLISHED`,
`INCOMPATIBLE_PLATFORM`, `QUARANTINED`, `REVOKED`, and `CHANNEL_UNAVAILABLE`.
Malformed or unverifiable identity/context receives `400` or `401`; service failure
receives `503`. Do not disclose whether a policy-denied private skill exists beyond
the requested identifier.

## Audit event

Persist one append-only resolution event containing: `resolution_id`, authenticated
subject, agent/platform, project/environment identifiers, policy revision,
marketplace commit, returned `(skill_id, version, sha256)` tuples, denials, and time.
Do not store prompts, workspace contents, credentials, or skill execution output.

## v1 boundary

v1 resolves **skill packages**, not arbitrary MCP tools, secrets, or execution
permissions. MCP may expose this API as `skills.search` and `skills.resolve`, but
the HTTP contract remains canonical so Codex, ChatGPT, Claude, CI agents, and future
adapters share the same policy decision.

The repository ships a `skills.resolve` CLI adapter for local `registry.json`
marketplaces. It filters to published, platform-certified, policy-authorized skills
and emits an artifact directory hash. Local policies are deny-by-default and can
match user or group, agent, project, environment, platform, and skill. The CLI is
still not an identity provider: callers must supply only verified identity claims.

## Acceptance checks

- The same verified context and marketplace/policy revisions yield the same tuple set.
- A returned artifact hash matches the downloaded package before it is loaded.
- A quarantined skill is absent from new resolutions within the configured revocation
  target.
- A request from an uncertified platform returns `INCOMPATIBLE_PLATFORM`.
- An audit event can reconstruct exactly which capability view an agent received.
