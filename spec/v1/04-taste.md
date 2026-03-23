# 04. Taste - Safety Evaluation

**Taste** is the CMN safety evaluation mechanism. Before executing foreign code, a visitor analyzes it and records a verdict. There is no global authority — each visitor decides who to trust.

## 1. Overview

Code distribution requires trust decisions. A visitor downloading a spore must evaluate whether the code is safe before placing it in their working environment. CMN formalizes this through **taste** — a structured evaluation step that produces a signed verdict.

Taste is:
- **Required** — gated operations (spawn, grow, absorb, bond) check the taste verdict before proceeding
- **Subjective** — each visitor performs their own evaluation and chooses which tasters to trust
- **Shareable** — publishers can sign and distribute taste reports for others to reference

## 2. Verdict Scale

Verdicts use a 5-level scale:

| Verdict | Meaning |
| :--- | :--- |
| `sweet` | Used it, it's great. A personal endorsement from real-world usage. |
| `fresh` | Reviewed thoroughly, no issues found. Code quality is good. |
| `safe` | Quick scan, nothing obviously wrong. Enough to proceed. |
| `rotten` | Low-trust quality warning — broken, won't compile, or fundamentally flawed. Not treated as malicious by default. |
| `toxic` | Confirmed dangerous — malware, data exfiltration, backdoors, or destructive behavior. |

The scale is ordered from most positive (`sweet`) to most negative (`toxic`). The middle value (`safe`) represents basic review — enough to proceed but not a strong signal.

## 3. Gate Rules

All operations that place code into a visitor's working directory are **taste-gated**:

| Operation | Description |
| :--- | :--- |
| Spawn | Create a working copy of a spore |
| Grow | Sync a spawned copy with its upstream source |
| Absorb | Merge code from another spore |
| Bond | Fetch bonded spores to `.cmn/bonds/` |

**Processing rules:**

| Verdict | Action |
| :--- | :--- |
| `toxic` | **Block** — operation refuses to proceed |
| `rotten` | **Warn** — display warning, recommend sandboxed environment, then proceed |
| `safe` | Proceed |
| `fresh` | Proceed |
| `sweet` | Proceed |
| Untasted | **Block** — operation refuses to proceed |

Normative behavior:
- Implementations MUST run this gate before any operation writes foreign code into a working directory.
- Untasted targets MUST fail closed with a machine-readable error code.
- `toxic` verdicts MUST fail closed with a machine-readable error code.
- `rotten` verdicts MUST emit a warning and MAY proceed.
- `safe`, `fresh`, and `sweet` verdicts MAY proceed.

Tasting itself downloads code to the global cache for review — this cache step is not gated.

### 3.1 Sandboxed Override

When the execution environment provides verifiable isolation (container, WASM sandbox, VM), implementations MAY skip the taste gate entirely:

- Untasted and `rotten` spores proceed without warning or verdict recording
- `toxic` verdicts MUST still block — even in sandbox
- The spore remains untasted after the sandbox session (no fake verdict is persisted)
- All bypassed operations MUST emit a `taste_override_sandbox` trace event for auditability
- Activated via explicit opt-in (e.g., `--sandbox` flag or `CMN_SANDBOX=1` environment variable)

## 4. Taste Capsule

A taste report is a signed capsule using the [`taste.json`](https://cmn.dev/schemas/v1/taste.json) schema. When shared through Synapse, the concrete submission and query interfaces are defined by the strains that Synapse node follows.

### 4.1 Format

```json
{
  "$schema": "https://cmn.dev/schemas/v1/taste.json",
  "capsule": {
    "uri": "cmn://bob.dev/taste/b3.7tRkW2xPqL9nH4mYeZcFjA5sD8vBwKgU6pXb3",
    "core": {
      "target_uri": "cmn://cmn.dev/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2",
      "domain": "bob.dev",
      "key": "ed25519.5XmkQ9vZP8nL3xJdFtR7wNcA6sY2bKgU1eH9pXb4",
      "verdict": "safe",
      "notes": [],
      "tasted_at_epoch_ms": 1739280000000
    },
    "core_signature": "ed25519...."
  },
  "capsule_signature": "ed25519...."
}
```

### 4.2 Fields

| Field | Description |
| :--- | :--- |
| `capsule.uri` | Content-addressed URI: `cmn://{domain}/taste/{hash}` |
| `core.target_uri` | Full CMN URI of the target being tasted |
| `core.domain` | Domain of the publisher submitting the report |
| `core.key` | Taster's Ed25519 public key embedded in the signed core. Required for shared signed taste capsules; enables offline signature verification once key trust is established. |
| `core.verdict` | Verdict from the 5-level scale: `sweet`, `fresh`, `safe`, `rotten`, `toxic` (§2) |
| `core.notes` | Optional findings (e.g., `["eval() in src/init.rs:42"]`) |
| `core.tasted_at_epoch_ms` | When the evaluation was performed (milliseconds since Unix epoch) |

`core.target_uri` supports exactly three target kinds:

- `cmn://{domain}` (Domain)
- `cmn://{domain}/{hash}` (Spore)
- `cmn://{domain}/mycelium/{hash}` (Mycelium)

### 4.3 Two-Layer Signature

Taste capsules use the same two-layer signature scheme as spores and mycelium:

- **`core_signature`** — signs `capsule.core` with the taster's Ed25519 key (JCS canonical)
- **`capsule_signature`** — signs the entire `capsule` with the taster's key

For self-published reports, both signatures use the same key. For replicates (a different domain re-hosting a taste report), the `capsule_signature` uses the host's key while `core_signature` retains the original taster's signature.

## 5. Hash & Signature

### 5.1 Hash Calculation

The hash in `capsule.uri` is computed from `core` + `core_signature`:

1. Construct hash input: `{"core": <core>, "core_signature": "<signature>"}`
2. Serialize using JCS (RFC 8785)
3. Hash with BLAKE3 → `b3.<base58>`

The resulting URI: `cmn://{domain}/taste/b3.<base58>`

### 5.2 Verification

To verify a taste report:

1. Verify `core_signature` against `capsule.core.key` locally
2. Establish trust in `capsule.core.key` using the taster domain's `cmn.json` (or cached trust from a prior verification cycle)
3. Verify `capsule_signature` against the host domain's public key
4. Recompute the hash from `{core, core_signature}` and compare with the URI hash

## 6. Local vs Shared

### 6.1 Local Taste

Any visitor can taste a spore and cache the result locally — no domain or signing key required. Local taste results are stored on the visitor's machine and checked by gated operations (§3).

### 6.2 Shared Taste

Sharing taste reports with the network requires:

1. A domain with an Ed25519 signing key
2. Sign the taste capsule (§4.3)
3. Submit through a Synapse node using one of its supported strain-defined interfaces

Shared reports may be indexed by Synapse nodes and served to other visitors. The concrete query interfaces are defined by the strains that node follows. Reports are advisory — no global safety score is computed or enforced.

## 7. Trust Model

CMN taste operates on a **subjective trust** model:

- **No global authority** — there is no central entity that decides what is safe. Each visitor chooses which taster domains to trust and how to weigh their reports.
- **Independent verification** — any visitor can fetch a taste report from a Synapse node, mirror, or other intermediary, then independently verify the taster's signature against the taster domain's public key. Trust in the intermediary is not required.
- **Advisory only** — Synapse aggregates and serves taste reports but does not adjudicate. It does not compute global scores or enforce verdicts across visitors.
- **Reputation is emergent** — over time, visitors learn which taster domains produce reliable evaluations. This is a social property, not a protocol mechanism.
