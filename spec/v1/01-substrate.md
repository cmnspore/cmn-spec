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

**Schema:** `https://cmn.dev/schemas/v1/cmn.json`

```json
{
  "$schema": "https://cmn.dev/schemas/v1/cmn.json",
  "capsules": [
    {
      "uri": "cmn://cmn.dev",
      "key": "ed25519.5XmkQ9vZP8nL3xJdFtR7wNcA6sY2bKgU1eH9pXb4",
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
| `$schema` | String | Schema URL: `https://cmn.dev/schemas/v1/cmn.json` |
| `capsules` | Array | Array of capsule entries. First entry (`capsules[0]`) is the domain's own capsule; additional entries are replicated capsules from other domains. |
| `capsules[].uri` | String | Domain URI of the capsule origin: `cmn://{origin_domain}`. The first entry (`capsules[0]`) is always this host domain. |
| `capsules[].key` | String | Ed25519 public key of the entry's origin domain in `{algorithm}.{base58}` format. |
| `capsules[].previous_keys` | Array | Retired public keys for verifying historical content (see [§1.2.3](#1-2-3-key-rotation)). Empty array if no key rotation has occurred. |
| `capsules[].endpoints` | Array | Typed array of endpoint definitions. Each entry has a `type` field (`mycelium`, `spore`, `archive`, `taste`, or extension types). Taste-only domains provide only a taste endpoint. |
| `capsule_signature` | String | Ed25519 signature of the `capsules` array, verified with `capsules[0].key` (format: `ed25519.<base58>`, JCS canonical). |

**Endpoint types:**

| Type | Required fields | Description |
|------|----------------|-------------|
| `mycelium` | `url`, `hash` | Mycelium manifest. `hash` is the primary mycelium content hash — authoritative source for domain metadata and featured spores. Optional `hashes` array for additional overflow shards (large domains). `url` template includes `{hash}`. |
| `spore` | `url` | Spore manifests. `url` template includes `{hash}`. |
| `archive` | `url`, `format` | Archive downloads. `url` template includes `{hash}` (the template itself carries the file extension). Optional `delta_url` includes `{hash}` and `{old_hash}`. Multiple archive entries with different formats are allowed. |
| `taste` | `url` | Taste reports. `url` template includes `{hash}`. |

The `key` is inside each capsule entry, so the `capsule_signature` covers the key binding — all entries, their public keys, and endpoints are signed together as a single authorized unit.

**Note:** Endpoints use a uniform typed-array pattern (same as `dist` in spores and `nutrients` in mycelium). Replicators can add additional capsule entries with different endpoints while preserving the original entry.

**Resolution Flow:**

```
1. Download cmn.json
2. Find endpoint with type "mycelium" in capsules[0].endpoints
3. Compare mycelium endpoint's hash with cached hash
4. If same → Skip download (efficient)
5. If different → Download full mycelium using the endpoint's url template
6. Resolve spore/archive/taste by finding the matching type in endpoints
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

Domains MAY rotate their Ed25519 key at any time by updating `cmn.json` with a new `key` and moving the old key to `previous_keys`:

```json
{
  "$schema": "https://cmn.dev/schemas/v1/cmn.json",
  "capsules": [
    {
      "uri": "cmn://example.com",
      "key": "ed25519.NEW_KEY_BASE58",
      "previous_keys": [
        { "key": "ed25519.OLD_KEY_BASE58", "retired_at_epoch_ms": 1772000000000 }
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

**Verification of historical content:**

1. Try `capsule.key` first
2. If signature fails, try each key in `previous_keys` (ordered newest-first)
3. `retired_at_epoch_ms` indicates when each key was retired

**Rotation hardening (implementation guidance):**

1. Keep retired keys in `previous_keys` for at least the key-trust TTL window (default 7 days) plus allowed clock skew, so cached/historical content remains verifiable during rollout.
2. During rotation windows, clients SHOULD prefer live domain confirmation over Synapse witness when available.
3. If key rotation coincides with other high-risk changes (for example: endpoint template changes + sudden mycelium replacement), clients SHOULD surface a high-risk warning (`key_rotation_review`) before treating new trust as first-class.

**Why this works:** The key is the cryptographic identity; the domain is the name resolution layer. HTTPS authenticates the domain, the domain declares its keys (current and previous) in `cmn.json`, and all content is verified against these keys. CMN domains can rotate keys freely because the domain remains the stable discovery anchor while the key provides cryptographic proof of authorship.

**Synapse behavior:** A Synapse node that offers key witness MUST cache `key` alongside every verified mycelium. When verifying historical content (e.g., a replicate whose original domain is offline), it uses that cached key rather than requiring a live fetch.

#### 1.2.4 Key Trust Model

Spores embed the author's public key in `capsule.core.key`. This makes spores self-describing: any holder can verify `core_signature` without network access. However, signature validity alone does not establish trust — someone could generate a keypair and claim any domain. Trust requires confirming that the key belongs to the claimed domain.

**Trust tiers:**

| Tier | Source | Trust Level | Cached | TTL |
|------|--------|-------------|--------|-----|
| Domain confirmation | `cmn.json` from HTTPS domain | First-class | Yes | 7 days (configurable) |
| Synapse witness | Synapse witness endpoint | Second-class | No | Re-verified each cycle |

**Refresh policies (implementation guidance):**

| Policy | Behavior |
|--------|----------|
| `expired` (default) | Use cached trust while TTL is valid. Re-confirm from network only when expired/missing. |
| `always` | Re-confirm key trust from network every verification cycle. |
| `offline` | Never refresh from network. Only cached trust entries are accepted. |

In `offline`, a missing/expired key trust cache MUST fail verification (for example: `key_untrusted`) instead of silently downgrading to untrusted network sources.

**Synapse witness fallback policy (implementation guidance):**

| Policy | Behavior when domain confirmation is unavailable |
|--------|--------------------------------------------------|
| `allow` (default) | Permit Synapse witness as second-class trust (not cached). |
| `require_domain` | Do not use Synapse witness for key trust. Verification fails if domain confirmation is unavailable and cache is insufficient. |

**Domain confirmation (first-class trust):**
- Fetch `cmn.json` from the domain via HTTPS
- Verify that `capsules[0].key` matches `core.key` (or appears in `previous_keys`)
- Cache the key-domain binding with a TTL (default: 7 days)
- Subsequent verifications within the TTL skip the network fetch

**Synapse witness (second-class trust):**
- When the domain is offline or unreachable, ask a Synapse node for the domain's known public key
- The Synapse node returns a key it cached during previous successful verification cycles
- This trust is NOT cached locally — it must be re-verified each time
- Provides resilience against domain outages without creating permanent trust from a third party

**Offline verification workflow (no network required at verification time):**
1. Online preflight: verify one spore from each trusted domain, so `core.key ↔ domain` is cached from live `cmn.json`.
2. Enter offline mode in the client implementation.
3. Verify spores using embedded `core.key` + cached key trust only.
4. If cache is expired/missing, fail and require an online refresh cycle.

**Legacy spores:** Spores without `core.key` fall back to the original verification flow: fetch `cmn.json` first, extract the public key, then verify signatures.

### 1.3 Value Formats

**Hashes, public keys, and signatures** use a unified `algorithm.value` format with dot separator and base58 encoding:

- **Hash**: `b3.<base58>` (e.g., `b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2`)
- **Public key**: `ed25519.<base58>` (e.g., `ed25519.5XmkQ9vZP8nL3xJdFtR7wNcA6sY2bKgU1eH9pXb4`)
- **Signature**: `ed25519.<base58>` (e.g., `ed25519.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa23yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2`)

Base58 uses the alphabet `123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz` (no `0`, `O`, `I`, `l`). Hash values encode to ~44 base58 characters; signatures encode to ~88 characters.

This format is used consistently across URIs, JSON fields, filenames, and API paths.

**Canonical JSON (JCS):** All signatures and hashes use **JSON Canonicalization Scheme (JCS, RFC 8785)**:

- Keys sorted alphabetically
- No whitespace
- Deterministic number formatting
- JSON strings serialized as-is per RFC 8785 (no Unicode normalization step)

This ensures identical input produces identical bytes for signing and hashing, regardless of implementation.

**Important:** Unicode NFC normalization is applied to filenames in Merkle tree hashing (see [03-spore §4.6.3](./03-spore.md#4-6-3-unicode-nfc-normalization)), not to JSON string values in JCS.

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

## 6. Protocol Versioning

The protocol version lives in the `$schema` URL path, for example `https://cmn.dev/schemas/v1/spore.json`. All CMN schema documents for a given release share the same version segment. This repository publishes the corresponding prose and conformance bundles under matching versioned paths such as `spec/v1/` and `conformance/v1/`.

### 6.1 Version Negotiation

Domains MUST declare supported protocol versions in `cmn.json`:

```json
{
  "protocol_versions": ["v1"],
  "capsules": [...]
}
```

Consumers SHOULD use the highest mutually-supported version.

### 6.2 Migration Rules

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
