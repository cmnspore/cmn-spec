# 08. Security Model

This chapter is the single reference for CMN trust policy and threat analysis. Data formats remain in their protocol chapters: `cmn.json` in [01-substrate](./01-substrate.md), mycelium timestamps in [02-mycelium](./02-mycelium.md), spore hashing in [03-spore](./03-spore.md), and taste gates in [04-taste](./04-taste.md).

## 1. Threat Model

CMN assumes the network, mirrors, caches, Synapse nodes, and archive transports may be hostile. Clients therefore verify signatures and content hashes after every fetch.

| Threat | Mitigation |
| :--- | :--- |
| Network attacker modifies manifests or archives | HTTPS protects `cmn.json` discovery; all signed capsules and content hashes are verified after download. |
| CA compromise or domain TLS mis-issuance | Capsule signatures and cached key trust make previously verified content detectable; Certificate Transparency gives operators an audit trail. |
| Synapse operator serves forged data | Synapse is not authoritative. Clients verify signatures, URI hashes, and key trust; Synapse witness is second-class trust only. |
| Domain hijack or DNS takeover | A hijacker can publish a new `cmn.json` while control lasts. Clients pin serial/digest/key state per domain, reject rollback or same-serial forks, and require outgoing-key rotation proof before accepting key changes. |
| Cache poisoning on shared hosts/containers | Clients must verify cached `cmn.json` signatures before reuse and should isolate `CMN_HOME` per user/container. |
| Archive path traversal or symlink attacks | Archive extractors must reject absolute paths, `..`, symlinks, hardlinks, and special files before writing to disk. |
| Archive permission drift | Archive producers preserve executable bits; archive consumers restore them on Unix-like systems and include mode in tree-hash verification. |
| Portable filename collapse | Git and Linux filesystems can represent case- or Unicode-distinct sibling paths that collapse on common macOS/Windows configurations. CMN rejects such content on publish and receive using the portable filename rule in [03-spore §4.6.3](./03-spore.md#4-6-3-unicode-nfc-normalization-and-portable-filename-validation). |

### 1.1 Parser and Extension Field Safety

CMN schemas may allow unknown fields for forward compatibility. Unknown fields MUST be ignored by default and MUST NOT influence trust decisions, filesystem writes, network fetches, algorithm choice, revocation handling, taste gates, or any other security-sensitive behavior unless a future specification explicitly defines those fields and places them inside the relevant signed payload.

Security-sensitive behavior MUST come only from recognized fields whose values are covered by the appropriate signature and pass schema, registry, and semantic validation. Top-level fields outside a signed payload are metadata unless the specification explicitly says otherwise.

Implementations SHOULD reject duplicate JSON object keys at security-critical parse boundaries to avoid parser differentials where one implementation keeps the first value and another keeps the last.

## 2. Key Trust Model

Spores, mycelium, and taste reports embed the author's public key in `capsule.core.key`. This makes the signed core self-describing: any holder can verify `core_signature` without a network fetch. Signature validity alone does not establish domain trust because anyone can generate a key and claim a domain.

### 2.1 Trust Tiers

| Tier | Source | Trust Level | Cached | TTL |
| :--- | :--- | :--- | :--- | :--- |
| Domain confirmation | `cmn.json` from the HTTPS domain | First-class | Yes | 7 days by default |
| Synapse witness | Synapse key witness | Second-class | No | Re-verified each cycle |

Domain confirmation fetches `cmn.json`, verifies its `capsule_signature`, applies domain-state pinning, and checks that the content key is either `capsules[0].key` or an acceptable `history` entry with a valid rotation proof and signing-time cutoff. Confirmed bindings may be cached until TTL expiry.

Synapse witness is only a fallback when the domain is unavailable. It helps survive outages but does not create durable local trust.

### 2.2 Verification Flow

For any signed capsule:

1. Verify `core_signature` against embedded `capsule.core.key`.
2. If a fresh local key-trust cache binds that key to `core.domain`, accept first-class trust.
3. Otherwise fetch the domain `cmn.json`, verify signature, verify serial/digest/key pinning, and confirm the key.
4. If the domain is unreachable and policy allows it, use Synapse witness as second-class trust.
5. Verify `capsule_signature` against the host domain key from the source capsule entry.
6. Verify the content-addressed URI hash.

### 2.3 Policy Knobs

Refresh policies:

| Policy | Behavior |
| :--- | :--- |
| `expired` | Use cached trust while TTL is valid; refresh only when expired/missing. |
| `always` | Re-confirm key trust every verification cycle. |
| `offline` | Never refresh from network; missing/expired cache fails closed. |

Synapse witness policies:

| Policy | Behavior |
| :--- | :--- |
| `allow` | Permit Synapse witness as second-class trust when the domain is unavailable. |
| `require_domain` | Do not use Synapse witness; fail unless domain confirmation or fresh cache exists. |

Implementations that expose `require_domain_first_key=false` must document that the first trust binding for a domain may come from Synapse or another non-domain source. This is convenient for bootstrapping but weakens protection against malicious indexes.

### 2.4 Sense Is Not Trust

`sense` is read-only inspection of metadata and availability. It may report signature/hash status, but it does not create key trust, taste trust, or permission to execute code.

## 3. Key Rotation and Revocation

The `history` format and `cmn-key-rotation-v1` statement are defined in [01-substrate §1.2.3](./01-substrate.md#1-2-3-key-rotation).

- `retired` means normal rotation: historical signatures remain valid only when the old key's `rotation_signature` authorizes the successor and the content signing time is not later than `retired_at_epoch_ms`.
- `revoked` means compromise: signatures produced at or after `revoked_at_epoch_ms` must be rejected. If signing time cannot be established, conservative clients should reject all signatures by the revoked key.

Revocation is domain-authored data. Clients must still obtain it through a trusted `cmn.json` path and should refresh key trust before high-risk operations such as spawn and absorb when cached data is stale.

Revocation primarily protects against a compromised key when the attacker does not also control the domain's service path. If an attacker controls the domain, HTTPS serving path, or `cmn.json` distribution path, they can attempt to replay an older signed `cmn.json` that omits the revocation; clients with a local domain-state pin reject lower serials and same-serial digest forks. Clients should still treat revocation freshness as bounded by their first-seen pin, domain-confirmation, and witness-refresh policy.

## 4. Replay and Rollback Analysis

### 4.1 Domain Entry (`cmn.json`)

`cmn.json` is mutable and fetched from the domain. Clients should revalidate cached `cmn.json` signatures on every read and maintain a local domain-state pin:

- Reject lower `capsules[0].serial` as `domain_state_rollback`.
- Reject the same serial with a different signed `capsules` digest as `domain_state_equivocation`.
- Reject unusually large forward jumps (default threshold `1000`) as `domain_state_jump` unless the user deliberately resets trust.
- If `capsules[0].key` differs from the pinned key, require a verified `history` chain from pinned key to current key or reject as `domain_key_rotation_unproven`.

These checks do not replace HTTPS for first discovery; they harden subsequent fetches against rollback and key substitution.

### 4.2 Mycelium

Synapse nodes use the four timestamp rules in [02-mycelium §8](./02-mycelium.md#8-pulse-publishing-updates): newer timestamps replace older ones, duplicate hashes are ignored, same timestamp with different hash is rejected, and older timestamps are rejected. This blocks replay of older domain manifests in an append/update index.

### 4.3 Spores and Taste

Spore and taste capsules are immutable and content-addressed. Replay of an older valid spore hash is not a mutation attack; it is a request for that historical object. Taste correction is handled by latest-verdict selection: for one taster and target, clients use the greatest `tasted_at_epoch_ms`.

## 5. Credentials and Local State

Synapse tokens are bearer credentials. If stored on disk, files must be owner-only readable (for example `0600`) and should be treated like API keys. Environment variables such as `SYNAPSE_TOKEN_SECRET` override config for process scope; implementations should avoid logging them.

Multi-user or container deployments should isolate `CMN_HOME` per security principal. Shared caches turn local key trust, cmn.json, taste verdicts, and tokens into shared mutable state.

## 6. Mechanism References

- Domain entry and key rotation: [01-substrate](./01-substrate.md)
- Mycelium update ordering: [02-mycelium §8](./02-mycelium.md#8-pulse-publishing-updates)
- Spore tree hash and distribution verification: [03-spore §4.6](./03-spore.md#4-6-tree-hash-merkle-tree) and [§5](./03-spore.md#5-content-verification)
- Taste gate rules: [04-taste §3](./04-taste.md#3-gate-rules)
- Algorithm downgrade protection: [07-algorithm-registry](./07-algorithm-registry.md)
