# 01. Substrate - Discovery & Identity

The **Code Mycelial Network (CMN)** is a **domain-sovereign, distributed network** for code sharing and evolution. Each domain is a sovereign node with full control over its content, identity, and distribution.

## 1. Core Principles

### 1.1 Domain Sovereignty

**Every domain is an independent, self-governing node:**

- **Identity**: The Ed25519 key is the cryptographic identity; the domain is the discovery and name resolution layer
- **Control**: Full authority over published content and endpoints
- **Responsibility**: Maintains its own cryptographic keys and content
- **Independence**: No central authority, no permission required

**FQDN Sovereignty:**
- Each **Fully Qualified Domain Name** is a sovereign node (e.g., `cmn.dev`, `api.cmn.dev`)
- Subdomains are independent - no automatic trust inheritance from parent domains
- Each domain publishes its own Ed25519 public key via `cmn.json`
- A single keypair MAY be shared across multiple domains (operational choice, not protocol requirement)

**Why a domain, not a bare public key (design rationale):**

A bare Ed25519 public key would be a more *portable* identity, but public keys can be generated for free in unlimited quantity. That gives an indexing and discovery layer no way to resist sybil and spam floods — a free identity costs an attacker nothing to mint a million of. (Nostr, which uses bare-pubkey identities, retrofitted NIP-05 — domain verification — for exactly this reason.) CMN deliberately anchors identity to a domain: registration and renewal impose a continuous, real-world cost and an accountable owner. **This is the network's primary sybil-resistance mechanism, and it is a deliberate trade-off, not inherited centralization.**

The cost of the trade-off is that identity **continuity** is tied to domain control. If a domain lapses, is seized, or is transferred, a fresh client can no longer establish *first-class* trust in that identity, and the new owner of the name becomes the authority for it. This is intentional: stop paying the sovereignty cost, stop holding the sovereign name.

This does **not** weaken the **verifiability** of already-published content. Spores, mycelium, and taste reports are content-addressed and embed `core.key`, so any holder of the bytes (from a mirror or a Synapse cache) can still verify signatures and hashes without the origin domain being reachable. What a dead or transferred domain forfeits is *first-class trust bootstrapping for new clients* and *discovery* — not the integrity of content already in hand, and not the validity of signatures a client has already pinned.

### 1.2 Trust Anchor: Domain Identity

**Domain ownership is verified through the domain entry point:**

#### 1.2.1 Domain Entry Point (cmn.json)

Every CMN domain publishes a `cmn.json` file at the domain root. This lightweight entry point (~200 bytes) serves two purposes:

1. **Identity Verification**: Provides `key` — the domain's Ed25519 public key, authenticated by the transport layer (e.g., HTTPS with TLS certificate)
2. **Content Discovery**: Typed endpoint array declares where to fetch mycelium, spores, archives, and taste reports

**Location:** `https://{domain}/.well-known/cmn.json`

CMN follows the **`.well-known` URI** standard ([RFC 8615](https://datatracker.ietf.org/doc/html/rfc8615)), which defines a path prefix for "well-known locations" in URI space. This is the same standard used by:
- **ACME** (Let's Encrypt): `/.well-known/acme-challenge/`
- **WebFinger**: `/.well-known/webfinger`
- **OAuth/OIDC**: `/.well-known/openid-configuration`
- **Nostr**: `/.well-known/nostr.json`

Using `.well-known` makes CMN discoverable via standard Web infrastructure, compatible with existing HTTP servers, CDNs, and caching layers without special configuration.

**Schema:** `https://cmn.dev/schemas/v1/cmn.json` (the hostname is not authoritative — see [§6](#6-protocol-versioning))

```json
{
  "$schema": "https://cmn.dev/schemas/v1/cmn.json",
  "capsules": [
    {
      "uri": "cmn://cmn.dev",
      "serial": 1,
      "key": "ed25519.5XmkQ9vZP8nL3xJdFtR7wNcA6sY2bKgU1eH9pXb4",
      "history": [],
      "endpoints": [
        {"type": "mycelium", "url": "https://cmn.dev/cmn/mycelium/{hash}.json", "hash": "b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2"},
        {"type": "spore",    "url": "https://cmn.dev/cmn/spore/{hash}.json"},
        {"type": "archive",  "url": "https://cmn.dev/cmn/archive/{hash}.tar.zst", "format": "tar+zstd",
                             "delta_url": "https://cmn.dev/cmn/archive/{hash}.from.{old_hash}.tar.zst"},
        {"type": "taste",    "url": "https://cmn.dev/cmn/taste/{hash}.json"}
      ]
    }
  ],
  "capsule_signature": "ed25519.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa23yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2"
}
```

**Field Definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `$schema` | String | `https://cmn.dev/schemas/v1/cmn.json` (hostname non-authoritative — see [§6](#6-protocol-versioning)). |
| `capsules` | Array | Array of capsule entries. First entry (`capsules[0]`) is the domain's own capsule; additional entries are replicated capsules from other domains. |
| `capsules[].uri` | String | Domain URI of the capsule origin: `cmn://{origin_domain}`. The first entry (`capsules[0]`) is always this host domain. |
| `capsules[].serial` | Integer | Monotonically increasing domain-state serial. Starts at `1` for newly initialized domains and MUST increase whenever the signed `capsules` array changes. |
| `capsules[].key` | String | Ed25519 public key of the entry's origin domain in `{algorithm}.{base58}` format. |
| `capsules[].history` | Array | Historical public keys with lifecycle status (`retired` or `revoked`; see [§1.2.3](#1-2-3-key-rotation) and [08-security §3](./08-security.md#3-key-rotation-and-revocation)). Use an empty array if no key rotation has occurred. |
| `capsules[].endpoints` | Array | Typed array of endpoint definitions. Each entry has a `type` field (`mycelium`, `spore`, `archive`, `taste`, or extension types). Use an empty array when the domain has no endpoints. |
| `capsule_signature` | String | Ed25519 signature of the `capsules` array, verified with `capsules[0].key` (format: `ed25519.<base58>`, JCS canonical). |

**Endpoint types:**

| Type | Required fields | Description |
|------|----------------|-------------|
| `mycelium` | `url`, `hash` | Mycelium manifest. `hash` is the primary mycelium content hash — authoritative source for domain metadata and featured spores. Optional `hashes` array for additional overflow shards (large domains). `url` template includes `{hash}`. |
| `spore` | `url` | Spore manifests. `url` template includes `{hash}`. |
| `archive` | `url`, `format` | Archive downloads. `url` template includes `{hash}` (the template itself carries the file extension). Optional `delta_url` includes `{hash}` and `{old_hash}`. Multiple archive entries with different formats are allowed. |
| `taste` | `url` | Taste reports. `url` template includes `{hash}`. |

The `key` is inside each capsule entry, so the `capsule_signature` covers the key binding — all entries, their public keys, and endpoints are signed together as a single authorized unit.

The top-level `protocol_versions` field and endpoint-level `protocol_version` field are removed in v1 hardening and are invalid in `cmn.json`. Protocol version is determined by the version segment of each payload's `$schema` URL path (`/v1/`), never by a hostname — see [§6](#6-protocol-versioning).

**Note:** Endpoints use a uniform typed-array pattern (same as `dist` in spores and `nutrients` in mycelium). Replicators can add additional capsule entries with different endpoints while preserving the original entry.

**Resolution Flow:**

```
1. Download cmn.json
2. Verify `capsule_signature` over the JCS-canonical `capsules` array with `capsules[0].key`
3. Check local domain-state pinning: serial must not roll back, same-serial digests must match, and key changes must have a valid rotation chain
4. Find endpoint with type "mycelium" in `capsules[0].endpoints`
5. Compare mycelium endpoint's hash with cached hash
6. If same → Skip download (efficient)
7. If different → Download full mycelium using the endpoint's url template
8. Resolve spore/archive/taste by finding the matching type in endpoints
```

**HTTPS Security Model:**
- HTTPS with valid TLS certificate proves domain ownership
- TLS certificate chain provides authentication (CA-signed)
- Certificate Transparency logs provide auditability

**Cross-Origin Access (CORS):**

CMN endpoints are public resources designed for any client — including web browsers. Domains MUST serve all CMN endpoints (`cmn.json`, mycelium, spore, archive, taste) with the following HTTP response header:

```
Access-Control-Allow-Origin: *
```

This is consistent with other `.well-known` standards (OpenID Connect, Nostr) that serve public discovery documents. Without CORS headers, browser-based CMN clients cannot function due to the same-origin policy.

#### 1.2.2 Identity Verification Flow

Spores embed the author's public key in `capsule.core.key`, enabling offline verification. Trust in the key is established through a tiered model (see §1.2.4).

```
Any spore, any source:
1. Read core.key → verify core_signature → signature matches ✓
2. Local cache has key + TTL valid → trusted ✓
3. Cache expired/missing → fetch domain cmn.json
   → key found → trusted ✓, cache key
   → key NOT found / domain down:
     → source is a Synapse node → second-class trust ✓, don't cache
     → source not Synapse → ask a Synapse node (key, domain) → second-class trust ✓, don't cache
   → nothing works → untrusted ✗
```

#### 1.2.3 Key Rotation

Domains MAY rotate their Ed25519 key by publishing a new `cmn.json` serial with a new `key` and a `history` entry in which the old key signs a rotation statement authorizing the successor key:

```json
{
  "$schema": "https://cmn.dev/schemas/v1/cmn.json",
  "capsules": [
    {
      "uri": "cmn://example.com",
      "serial": 42,
      "key": "ed25519.NEW_KEY_BASE58",
      "history": [
        {
          "key": "ed25519.OLD_KEY_BASE58",
          "status": "retired",
          "retired_at_epoch_ms": 1772000000000,
          "replaced_by": "ed25519.NEW_KEY_BASE58",
          "effective_serial": 42,
          "rotation_signature": "ed25519.SIGNATURE_BY_OLD_KEY"
        }
      ],
      "endpoints": [
        {"type": "mycelium", "url": "https://example.com/cmn/mycelium/{hash}.json", "hash": "b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2"},
        {"type": "spore",    "url": "https://example.com/cmn/spore/{hash}.json"},
        {"type": "archive",  "url": "https://example.com/cmn/archive/{hash}.tar.zst", "format": "tar+zstd"},
        {"type": "taste",    "url": "https://example.com/cmn/taste/{hash}.json"}
      ]
    }
  ],
  "capsule_signature": "ed25519.SIGNED_WITH_NEW_KEY"
}
```

**History states:**

| `status` | Meaning | Verification behavior |
| :--- | :--- | :--- |
| `retired` | Normal key rotation. The old private key is no longer used for new releases. | Historical signatures by this key remain valid up to `retired_at_epoch_ms`, if `rotation_signature` verifies. |
| `revoked` | Compromise or suspected compromise. | Signatures produced at or after `revoked_at_epoch_ms` MUST be rejected. If a verifier cannot determine signing time, it SHOULD reject the key conservatively. |

`retired_at_epoch_ms` records when the key left active use. `replaced_by` and `rotation_signature` are REQUIRED for `retired` entries. `effective_serial` records the `serial` at which the rotation became effective; when omitted, verifiers use the containing capsule's current `serial`. `revoked_at_epoch_ms` is REQUIRED when `status` is `revoked`. A key MUST NOT appear more than once in `history`.

The `rotation_signature` is made by the historical key over the JCS-canonical statement:

```json
{
  "purpose": "cmn-key-rotation-v1",
  "domain": "example.com",
  "from": "ed25519.OLD_KEY_BASE58",
  "to": "ed25519.NEW_KEY_BASE58",
  "effective_serial": 42,
  "retired_at_epoch_ms": 1772000000000
}
```

**Verification of historical content:**

1. Try `capsule.key` first.
2. If signature fails, try each `history` entry whose `status` is `retired`, whose `rotation_signature` verifies with that history key, and whose `retired_at_epoch_ms` is not earlier than the content signing time.
3. If an otherwise matching entry has `status: "revoked"`, apply the revocation rule above instead of trusting it.

For signed spore and mycelium content, signing time is the signed core's
`updated_at_epoch_ms` (taste uses `tasted_at_epoch_ms`). A verifier that cannot
determine this time MUST reject a retired key. The retirement cutoff is inclusive:
content declared at or before the cutoff can be accepted with a verified rotation.
This is a signer-declared timestamp, not proof of when the signature was created;
a holder of a retired private key can backdate content. Compromise requires
`revoked`, rather than relying on retirement to prevent forgery.

**Domain-state pinning:**

Clients SHOULD store, per domain, the highest accepted `capsules[0].serial`, a digest of the signed `capsules` array, and `capsules[0].key`.

1. A lower serial MUST be rejected as `domain_state_rollback`.
2. The same serial with a different capsules digest MUST be rejected as `domain_state_equivocation`.
3. A forward jump larger than the implementation threshold (default `1000`) SHOULD be rejected as `domain_state_jump`.
4. If the current key differs from the pinned key, clients MUST verify a `history` rotation chain from the pinned key to the current key or reject as `domain_key_rotation_unproven`.

**Rotation hardening (implementation guidance):**

1. Keep retired keys in `history` for at least the key-trust TTL window (default 7 days) plus allowed clock skew, so cached/historical content remains verifiable during rollout.
2. During rotation windows, clients SHOULD prefer live domain confirmation over Synapse witness when available.
3. If key rotation coincides with other high-risk changes (for example: endpoint template changes + sudden mycelium replacement), clients SHOULD surface a high-risk warning (`key_rotation_review`) before treating new trust as first-class.

**Why this works:** The key is the cryptographic identity; the domain is the name resolution layer. HTTPS authenticates initial discovery, the domain declares its current key in `cmn.json`, and each rotation is authorized by the outgoing key. Local serial/digest pinning prevents rollback and same-serial forks after first trust.

Cross-cutting trust policy, Synapse witness behavior, and replay analysis are specified in [08-security](./08-security.md).

#### 1.2.4 Key Trust Model

The cross-cutting key trust model applies to spores, mycelium, taste reports, and replicated capsules. It is specified in [08-security §2](./08-security.md#2-key-trust-model).

### 1.3 Value Formats

**Hashes, public keys, and signatures** use a unified `algorithm.value` format with dot separator and base58 encoding:

- **Hash**: `b3.<base58>` (e.g., `b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2`)
- **Public key**: `ed25519.<base58>` (e.g., `ed25519.5XmkQ9vZP8nL3xJdFtR7wNcA6sY2bKgU1eH9pXb4`)
- **Signature**: `ed25519.<base58>` (e.g., `ed25519.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa23yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2`)

Base58 uses the alphabet `123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz` (no `0`, `O`, `I`, `l`). Leading zero bytes MUST be encoded as leading `1` characters and decoders MUST restore them before length checks. A `b3` hash payload MUST decode to exactly 32 bytes (normally 43-44 Base58 characters); an Ed25519 public key payload MUST decode to exactly 32 bytes; an Ed25519 signature payload MUST decode to exactly 64 bytes (normally 87-88 Base58 characters).

This format is used consistently across URIs, JSON fields, filenames, and API paths.

**Canonical JSON (JCS):** All signatures and hashes use **JSON Canonicalization Scheme (JCS, RFC 8785)**:

- Keys sorted alphabetically
- No whitespace
- Deterministic number formatting
- JSON strings serialized as-is per RFC 8785 (no Unicode normalization step)

This ensures identical input produces identical bytes for signing and hashing, regardless of implementation.

**Important:** Unicode NFC normalization is applied to filenames in Merkle tree hashing (see [03-spore §4.6.3](./03-spore.md#4-6-3-unicode-nfc-normalization)), not to JSON string values in JCS. Producers SHOULD emit human-entered core strings in NFC for readability, but verifiers MUST NOT normalize JSON string values before JCS. Two visually similar JSON strings with different Unicode codepoint sequences are different signed bytes and can produce different hashes.

### 1.4 Distributed Architecture

**The Network:**

1. **Sovereign Nodes (Publishers)**
   - Primary source of truth
   - Publish Mycelium (site descriptor) and Spores (code units)
   - Control distribution endpoints
   - Evolve code through spawn and absorb across domains

2. **Synapse (Optional Indexing & Discovery)**
   - Crawl and cache Mycelium metadata from publisher domains
   - Build searchable index for discovery
   - Provide fallback when domains are offline
   - No write authority — read-only caches of verified content

**Visitors (read-only):**

- Discover spores via Synapse or direct URI
- Inspect metadata (sense) and evaluate safety (taste) before use
- Fetch and verify spores from publisher domains
- No domain, no keys, no infrastructure needed
- Can replicate and republish (becoming publishers)

## 2. Identity System

### 2.1 CMN URI Format

The URI is the **primary key** for all entities:

- **Domain root**: `cmn://{domain}` (domain identity)
- **Mycelium**: `cmn://{domain}/mycelium/{hash}` (content-addressed site descriptor)
- **Spore**: `cmn://{domain}/{hash}` (content-addressed code unit)
- **Taste report**: `cmn://{domain}/taste/{hash}` (content-addressed safety evaluation)

**Properties:**
- Domain identifies the publisher (or taster, for taste reports)
- Hash ensures content integrity (content-addressed)
- Use the `hash` field on the `type: "mycelium"` endpoint in `cmn.json` for change detection

For detailed URI specification, see [06-uri.md](./06-uri.md).

### 2.2 Synapse (Optional Indexing & Discovery)

CMN does not require any particular Synapse implementation. A Synapse is an optional service that caches verified metadata, answers discovery queries, and provides origin-offline fallbacks. Its concrete interfaces and extensions are defined by the strains it follows.

**Possible roles:**
- Crawl known domains periodically
- Cache Mycelium and Spore metadata
- Provide fallback when origin is offline
- Build searchable indexes for discovery

**Limitations:**
- Read-only - cannot modify domain content
- No authority - all content must verify against the domain's public key
- Optional - domains can operate without any such service

Concrete Synapse interfaces are defined by the strains each Synapse node follows.

## 3. Content Distribution

### 3.1 Multi-Source Distribution

Each capsule entry in `cmn.json` contains a typed endpoint array. Replicators can add additional capsule entries with different hosting endpoints.

```json
// cmn.json — endpoints per capsule entry
{
  "capsules": [
    {
      "uri": "cmn://example.com",
      "key": "ed25519...",
      "endpoints": [
        {"type": "mycelium", "url": "https://cdn.example.com/cmn/mycelium/{hash}.json", "hash": "b3..."},
        {"type": "spore",    "url": "https://cdn.example.com/cmn/spore/{hash}.json"},
        {"type": "archive",  "url": "https://cdn.example.com/cmn/archive/{hash}.tar.zst", "format": "tar+zstd",
                             "delta_url": "https://cdn.example.com/cmn/archive/{hash}.from.{old_hash}.tar.zst"},
        {"type": "taste",    "url": "https://cdn.example.com/cmn/taste/{hash}.json"}
      ]
    }
  ]
}
```

**Benefits:**
- CDN offloading (point endpoints to any CDN)
- Replicate support (same core, different endpoints)
- Geographic distribution
- Cost optimization

### 3.2 Distribution Sources (`capsule.dist`)

Spores can reference multiple source locations:

```json
{
  "capsule": {
    "dist": [
      { "type": "archive" },
      { "type": "git", "url": "https://github.com/user/repo", "ref": "v1.0.0" }
    ]
  }
}
```

**Supported Protocols:**
- **Archive (`type=archive`)**: Resolved via the `type: "archive"` endpoint's `url` template in `cmn.json`, replacing `{hash}` with the spore hash (default)
- **Git (`type=git`)**: `url` + optional `ref` for full history/context
- **IPFS (`type=ipfs`)**: `cid` for immutable content addressing

**Incremental behavior:** `git` and optional `delta_url` on archive endpoints provide incremental transfer paths. `delta_url` is endpoint-level discovery (not a separate dist entry). It MUST include `{hash}` (target hash) and `{old_hash}` (cached base hash); direction is always `old_hash -> hash`. Implementations SHOULD fall back to full `archive` when delta prerequisites are unavailable.

The protocol does not require filename-suffix parsing for format detection. Clients MUST use the `format` field on the `type: "archive"` endpoint to choose decoders. The examples in this spec use `tar+zstd`, but the protocol does not privilege any single archive format.

### 3.3 Pulse (Push Notification)

Domains MAY notify a Synapse node immediately after publishing by sending a Pulse notification (see [05-strain §5.2](05-strain.md)).

**What happens:**
- Sends signed mycelium to a Synapse node
- The receiver verifies signatures via the domain's public key
- The receiver updates its index immediately
- No waiting for crawler

**Optional:** Crawlers will eventually discover changes anyway.

## 4. Open Source Principles

### 4.1 Open Source Mandate

**CMN is inherently public and open source:**

- **Mandatory Licensing**: Every spore MUST declare a valid SPDX license
- **No Encryption**: Protocol has no built-in encryption
- **Private Code**: Keep it in private repos, outside CMN

### 4.2 Replicating

**Anyone can replicate any spore:**

A replicate hosts the same spore (identical hash) under a different domain. The `core` and `core_signature` remain unchanged from the original publisher:

- `core_signature` verifies against `original.dev` public key
- `core.domain` = `original.dev` (original author preserved)
- URI domain ≠ `core.domain` → this is a replicate
- Same hash = identical content

See [03-spore §6.1](./03-spore.md#6-1-replicate-same-hash) for the full replicate format.

### 4.3 Forking

**Modify and republish with attribution:**

A fork (spawn) creates a new spore with different hash, new domain, and a `spawned_from` bond:

- Different hash (because core metadata changed)
- `core.domain` = `fork.dev` (new publisher)
- Both signatures verify against `fork.dev` public key
- `bonds` track lineage back to the original

**Evolution Graph:**
- Bonds track lineage
- Synapse nodes may build evolution trees
- No single "canonical" version - visitor decides

See [03-spore §6.2](./03-spore.md#6-2-spawn-different-hash) for the full spawn format.

## 5. Conflict Resolution

### 5.1 The Sovereign Winner

In a decentralized network, multiple forks can exist:

```
Spore A
  ├─> Spore B1 (by domain-x.com)
  └─> Spore B2 (by domain-y.com)
```

**No Central Authority:**
- Both forks coexist in the network
- No protocol-level "winner"

**Visitor Decides:**
- Visitor chooses based on:
  - Trust in publisher domain
  - Bond chain length
  - Quality scores from auditors
  - User preferences

### 5.2 Spore Retention

**Domain Responsibility:**
- Retain all signed spores in archive (even if removed from active inventory)
- Never reuse hash for different content (enforced by BLAKE3)
- Replicate spore archives when migrating hosting

**Synapse Pruning:**
- May prune unbonded or low-reputation spores
- Popular spores (in inventories or bond chains) are preserved
- Mycelial structure keeps important content alive

### 5.3 Canonical Serialization and Formatting

While cryptographic signing and hash verification strictly use **JSON Canonicalization Scheme (JCS, RFC 8785)** with lexicographical key sorting and no whitespace, published human-readable files (`cmn.json`, `mycelium.json`, `spore.json`, `spore.core.json`, `taste.json`) apply deterministic **priority key ordering** before falling back to lexicographical sorting for unlisted keys.

#### Priority Key Ordering Tables

| Document / Object | Scope | Priority Key Order |
| :--- | :--- | :--- |
| **CMN Root (`CMN_KEY_ORDER`)** | `cmn.json` root | `$schema`, `capsules`, `capsule_signature` |
| **CMN Capsule Entry** | `/capsules[]` | `uri`, `serial`, `key`, `history`, `endpoints` |
| **CMN Endpoint** | `/capsules[]/endpoints[]` | `type`, `url`, `hash`, `hashes`, `format`, `delta_url` |
| **Key History Entry** | `/capsules[]/history[]` | `key`, `status`, `retired_at_epoch_ms`, `replaced_by`, `effective_serial`, `rotation_signature`, `revoked_at_epoch_ms` |
| **Spore Document** | `spore.json` root | `$schema`, `capsule`, `capsule_signature` |
| **Spore Capsule (`CAPSULE_KEY_ORDER`)** | `capsule` | `uri`, `core`, `core_signature`, `dist` |
| **Spore Core (`SPORE_CORE_KEY_ORDER`)** | `spore.core.json` or `capsule.core` | `$schema`, `id`, `name`, `version`, `domain`, `key`, `synopsis`, `intent`, `license`, `mutations`, `size_bytes`, `updated_at_epoch_ms`, `bonds`, `tree` |
| **Spore Tree** | `tree` | `algorithm`, `exclude_names`, `follow_rules` |
| **Bond (`BOND_KEY_ORDER`)** | `bonds[]` | `relation`, `uri`, `id`, `reason`, `with` |
| **Mycelium Document** | `mycelium.json` root | `$schema`, `capsule`, `capsule_signature` |
| **Mycelium Capsule** | `capsule` | `uri`, `core`, `core_signature` |
| **Mycelium Core (`MYCELIUM_CORE_KEY_ORDER`)** | `capsule.core` | `domain`, `key`, `name`, `synopsis`, `bio`, `nutrients`, `updated_at_epoch_ms`, `spores`, `tastes` |
| **Mycelium Spore Entry** | `capsule.core.spores[]` | `id`, `hash`, `name`, `synopsis` |
| **Mycelium Taste Entry** | `capsule.core.tastes[]` | `hash`, `target_uri` |
| **Nutrient Entry** | `nutrients[]` | `type`, `address`, `recipient`, `url`, `label`, `chain_id`, `token`, `asset_id` |
| **Taste Document** | `taste.json` root | `$schema`, `capsule`, `capsule_signature` |
| **Taste Capsule** | `capsule` | `uri`, `core`, `core_signature` |
| **Taste Core (`TASTE_CORE_KEY_ORDER`)** | `capsule.core` | `domain`, `key`, `target_uri`, `verdict`, `notes`, `tasted_at_epoch_ms` |

Any keys not explicitly specified in these priority tables are sorted alphabetically (lexicographical fallback) after the priority keys.

## 6. Protocol Versioning

### 6.1 Version Identity

A CMN protocol version is identified by the **version segment of the `$schema` URL path**, not by its hostname. Each document type's canonical `$schema` is:

| Document | `$schema` |
| :--- | :--- |
| Domain entry (`cmn.json`) | `https://cmn.dev/schemas/v1/cmn.json` |
| Mycelium | `https://cmn.dev/schemas/v1/mycelium.json` |
| Spore | `https://cmn.dev/schemas/v1/spore.json` |
| Spore draft (`spore.core.json`) | `https://cmn.dev/schemas/v1/spore-core.json` |
| Taste | `https://cmn.dev/schemas/v1/taste.json` |

**The hostname is not authoritative.** The protocol version is the `/v1/` path segment and the document type is the filename. The hostname — `cmn.dev` or any mirror — MUST NOT influence trust, version selection, or validation. `cmn.dev` is the reference publisher of the schema bundle, not the owner of the protocol namespace: anyone may mirror the schema documents at any host, and a payload's protocol version does not depend on which host (if any) served them. Implementations match `$schema` by version segment plus document-type filename and accept any hostname (the reference implementation also accepts a bare `…/v1/<type>.json` suffix from any host). This rule — not the literal string — is what keeps the protocol namespace from being bound to a single domain's continued existence, the same intent by which a spore binds identity to a content hash (§2.1) and treats endpoints as swappable locations (§3).

**The URL doubles as a real location, on purpose.** Unlike a content hash (whose identity is deliberately location-free), the `$schema` value is also the resolvable address where the JSON Schema is published, so standard JSON tooling — editors, CI validators — can fetch and validate against it without special configuration. Implementations MUST NOT depend on that fetch for correctness: schema validation MUST use an embedded copy of the schema (see each chapter's schema-validation section). The fetchable URL is a tooling affordance; the normative version-determination rule above is what carries protocol meaning.

### 6.2 Version Determination

Consumers select behavior from the **version segment** (`/v1/`) of the `$schema` URL path, never from its hostname. A payload whose `$schema` does not resolve — by version segment and document-type filename — to a recognized version and document type MUST be rejected.

A future major version is a new path segment (for example `https://cmn.dev/schemas/v2/spore.json`), introduced through the deprecation lifecycle in [07-algorithm-registry §4.1](./07-algorithm-registry.md#4-1-algorithm-migration).

There is no separate `cmn.json` protocol-version negotiation field. The removed top-level `protocol_versions` field and endpoint-level `protocol_version` field MUST be rejected rather than treated as deprecated compatibility hints.

### 6.3 Migration Rules

1. **Major version** (`v1` → `v2`): Breaking changes. Consumers MUST support both versions during a transition period of at least 12 months. Domains SHOULD publish under both versions concurrently.
2. **Minor additions**: New optional fields within the same major version. Consumers MUST ignore unknown fields. Producers MUST NOT require consumers to understand new optional fields for correct operation.
3. **Deprecation**: Fields marked deprecated in one major version MAY be removed in the next. Implementations SHOULD log warnings when deprecated fields are encountered.

## 7. Summary

**CMN is a domain-sovereign network:**
- Each domain is independent and self-governing
- cmn.json provides trust anchor
- Content is content-addressed and cryptographically signed
- No central authority - visitors choose what to trust
- Open source by design
- Resilient to domain and key loss through replicates and fallbacks

**Next Steps:**
- Read [02. Mycelium](./02-mycelium.md) for site descriptor format
- Read [03. Spore](./03-spore.md) for code unit specification
