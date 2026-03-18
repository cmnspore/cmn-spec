# 02. Mycelium - Domain Manifest

The **Mycelium** is a **Site Descriptor**. It represents a developer or organization and their published spores.

## 1. Overview

The domain entry point (`cmn.json`) is documented in [01-substrate.md](./01-substrate.md#1-2-1-domain-entry-point-cmn-json). This document covers the full mycelium manifest that contains the complete site metadata.

**Location:** Defined by `capsules[].endpoints.mycelium` in `cmn.json` (e.g., `https://cmn.dev/cmn/mycelium/{hash}.json`)
**Schema:** `https://cmn.dev/schemas/v1/mycelium.json`
**Size:** ~1-10 KB

```json
{
  "$schema": "https://cmn.dev/schemas/v1/mycelium.json",
  "capsule": {
    "uri": "cmn://cmn.dev/mycelium/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2",
    "core": {
      "name": "cmn.dev",
      "domain": "cmn.dev",
      "key": "ed25519.5XmkQ9vZP8nL3xJdFtR7wNcA6sY2bKgU1eH9pXb4",
      "synopsis": "",
      "updated_at_epoch_ms": 1769777183174,
      "spores": [
        {
          "id": "cmn-spec",
          "hash": "b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2",
          "name": "CMN Protocol Specification",
          "synopsis": "Code Mycelial Network - A sovereign-first protocol for code distribution"
        },
        {
          "id": "cmn-tools",
          "hash": "b3.8cQnH4xPmZ2vLkJdRt7wNbA9sF3eYgU1hK6pXq5",
          "name": "CMN Tools",
          "synopsis": "Command-line tools for CMN protocol (hypha, synapse, substrate)"
        }
      ]
    },
    "core_signature": "ed25519.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa23yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2"
  },
  "capsule_signature": "ed25519.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa23yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2"
}
```

**Note:** Content endpoints (`spore`, `archive[]`, optional `taste`) are defined in `cmn.json` capsule entries, not in the mycelium manifest. See [01-substrate §1.2.1](./01-substrate.md#1-2-1-domain-entry-point-cmn-json).

## 2. Field Definitions

### 2.1 Mycelium Fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `$schema` | String | Schema URL: `https://cmn.dev/schemas/v1/mycelium.json` |
| `capsule` | Object | The capsule container. |
| `capsule.uri` | String | Mycelium URI: `cmn://{domain}/mycelium/{hash}` |
| `capsule.core` | Object | The mycelium content. |
| `capsule.core.name` | String | Developer or organization name. |
| `capsule.core.domain` | String | The domain (e.g., `cmn.dev`). |
| `capsule.core.key` | String | Ed25519 public key of the content author. Enables offline signature verification via Synapse without fetching cmn.json. |
| `capsule.core.synopsis` | String | Brief description of the developer/org. |
| `capsule.core.bio` | String? | Multiline markdown with full details about this domain. |
| `capsule.core.nutrients` | Array? | Nutrient methods, ordered by preference (first = preferred). See §2.3. |
| `capsule.core.updated_at_epoch_ms` | Number | Unix timestamp in milliseconds. Used for version ordering. |
| `capsule.core.spores` | Array | List of published spores. |
| `capsule.core.tastes` | Array? | Optional list of published taste reports (`{hash, target_uri}`) for mirror discovery and re-submission. |
| `capsule.core_signature` | String | Ed25519 signature of the `core` object (`ed25519.<base58>`, JCS canonical). |
| `capsule_signature` | String | Ed25519 signature of the `capsule` object (`ed25519.<base58>`, JCS canonical). |

### 2.2 Spore Entry

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | String | Stable identifier for the spore (e.g., `cmn-tools`). Used for deduplication across releases. **Required.** |
| `hash` | String | BLAKE3 hash with prefix (e.g., `b3.3yMR7vZQ9hL2x...`). **Required.** |
| `name` | String | Human-readable name of the spore. **Required.** |
| `synopsis` | String? | Optional short description. |

**Note:** Spore entries use `hash` instead of full `uri` to keep the file size small. Clients can construct the full URI as `cmn://{domain}/{hash}`. The `id` field matches the `id` in `spore.core.json` and ensures that re-releasing a spore replaces the previous entry rather than appending a duplicate.

### 2.3 Nutrients

Optional array of nutrient methods, ordered by preference (first entry = preferred). Each entry is a typed method object with `type` as the only required field. All entries MAY include `label` for UI display.

```json
{
  "nutrients": [
    {"type": "lightning", "address": "user@example.com"},
    {"type": "lightning", "offer": "lno1qgsq..."},
    {"type": "onchain_btc", "address": "bc1q..."},
    {"type": "evm", "chain_id": 8453, "token": "native", "recipient": "0x1a2b..."},
    {"type": "webpage", "url": "https://github.com/sponsors/alice", "label": "GitHub Sponsors"}
  ]
}
```

Nutrient types align with `strain-payment-method-*` conventions. Each type below corresponds to a strain (e.g., `lightning` → `strain-payment-method-lightning`), and field names match the strain's payment request fields where applicable.

The base `mycelium.json` schema only requires `type` for nutrient entries. Type-specific required fields below are convention-level requirements enforced by corresponding `strain-payment-method-*` conventions and tooling.

**Direct payment types** — static addresses for voluntary donations:

| Type | Required Fields | Optional Fields | Description |
| :--- | :--- | :--- | :--- |
| `lightning` | `address` or `offer` | | Lightning address (user@domain, compatible with Nostr zaps) or BOLT12 offer (`lno1...`). One entry per form. |
| `onchain_btc` | `address` | | Bitcoin L1 address. |
| `liquid` | `address` | `asset_id` | Liquid sidechain address. |
| `evm` | `chain_id`, `recipient` | `token` | Ethereum or L2 (Arbitrum, Base, Optimism, etc.). `token`: ERC-20 contract address or `"native"` (default). |
| `solana` | `recipient` | `token` | Solana address. `token`: SPL mint address or `"native"` (default). |
| `monero` | `address` | | Monero address. |

**Webpage type** — any nutrient page, platform profile, or checkout:

| Type | Required Fields | Description |
| :--- | :--- | :--- |
| `webpage` | `url` | Human-facing payment page (GitHub Sponsors, Open Collective, Polar.sh, etc.). |

The `type` field is an open string — any value is valid. New payment networks require no protocol update.

**Design notes:**
- Nutrient type names match `strain-payment-{type}` — a tool can map a nutrient entry to the corresponding strain convention without a lookup table.
- No amounts — nutrient entries declare *where* to pay, not *how much*. Donation amounts are the donor's choice.
- No dependency splits — nutrients declares "how to pay this domain." Dependency-aware distribution is a tool-layer concern: Synapse can traverse the bond graph (`depends_on`, `spawned_from`, `absorbed_from`) and collect nutrient methods from each domain's mycelium.
- Nutrients is inside `core` and protected by `core_signature` — mirrors cannot tamper with the original author's nutrient addresses.

## 3. Schema Validation

**Schema URL:** `https://cmn.dev/schemas/v1/mycelium.json`

Validators SHOULD embed schemas for offline validation. No network fetch should be required.

## 4. Signing and Hashing

### 4.1 Core Signature

The `core_signature` signs the `core` object:

1. Serialize `core` using JCS (RFC 8785)
2. Sign the canonical bytes with Ed25519 private key
3. Format as `ed25519.<base58>`

**Purpose:**
- Protects mycelium metadata (name, synopsis, updated_at_epoch_ms, spore list) from tampering
- The `updated_at_epoch_ms` timestamp is included to prevent replay attacks

### 4.2 Content Hash Calculation

The hash in `capsule.uri` is calculated from `core` + `core_signature`:

1. Construct hash input: `{"core": <core>, "core_signature": "<signature>"}`
2. Serialize hash input using JCS
3. Hash with BLAKE3 → `b3.<base58>`
4. The mycelium URI is `cmn://{domain}/mycelium/{hash}` (the hash is also stored in `cmn.json` as `capsules[0].mycelium_hash` for change detection)

**Key Properties:**
- Changing any core field (name, synopsis, spores) changes the hash
- Hash includes the core_signature (tamper-proof)
- URI contains the hash for content addressing

### 4.3 Capsule Signature

The `capsule_signature` signs the entire `capsule` object (including `uri`):

1. Build capsule: `{"uri": <uri>, "core": <core>, "core_signature": "<signature>"}`
2. Serialize using JCS
3. Sign with Ed25519 private key → `ed25519.<base58>`

**Purpose:**
- Verifies entire capsule including URI
- Prevents tampering with any field
- URI is protected by signature

### 4.4 Canonical JSON (JCS)

All signatures and hashes use JCS (see [01-substrate §1.3](./01-substrate.md#1-3-value-formats)).

## 5. Publishing Workflow

**Publishing implementations MUST:**
1. Build the `core` object
2. Sign core → `core_signature`
3. Compute hash from core + core_signature
4. Construct `uri` with hash: `cmn://{domain}/mycelium/{hash}`
5. Build `capsule` with uri, core, core_signature
6. Sign capsule → `capsule_signature`
7. Save full mycelium to `/cmn/mycelium/{hash}.json`
8. Generate cmn.json capsule entry with mycelium_hash and endpoints
9. Sign cmn.json capsules array → `capsule_signature`
10. Save to `cmn.json`

## 6. File Organization

```
site_root/
├── .well-known/
│   └── cmn.json                                          # Domain entry point (~150 bytes)
└── cmn/
    └── mycelium/
        └── b3.3yMR7vZQ9hL2x...pTa2.json                  # Current version
```

**Benefits:**
- Old versions retained for history (optional)
- CDN can cache full mycelium files indefinitely (hash-based URLs)
- Capsule is always at the same path (easy to find)

## 7. Content Resolution

### 7.1 Hash Lookup

The mycelium hash is stored in `cmn.json` as `capsules[0].mycelium_hash`. Use this value from the domain entry point for change detection and content verification.

### 7.2 Mycelium Resolution

When fetching the full mycelium content:

Use `capsules[0].endpoints.mycelium` template from `cmn.json`:
- Take `capsules[0].mycelium_hash`
- Replace `{hash}` in template
- Example:
  - Hash = `b3.3yMR7vZQ9hL2x...pTa2`
  - URL = `https://cmn.dev/cmn/mycelium/b3.3yMR7vZQ9hL2x...pTa2.json`

If endpoints are missing, return an error - there are no default fallback URLs.

### 7.3 Spore Resolution

When a client needs to fetch a specific spore:

Use `capsules[0].endpoints.spore` template from `cmn.json`:
- Replace `{hash}` with the spore hash

Resolution flow: cmn.json → use `capsules[0].endpoints.spore` → fetch spore.

If endpoints are missing, return an error. Synapse is only used as a **backup** when the domain is unreachable, not as a default endpoint.

**Static Deployment:** This design allows static file hosting without any server-side logic.

## 8. Pulse (Publishing Updates)

When mycelium is updated, publishing tools MUST regenerate both the capsule and full mycelium files.

**Optional notification:**

Publishing implementations MAY send a Pulse notification to registered Synapse instances (see [05-strain §5.2](05-strain.md)).

**Synapse Validation:**

1. **Schema Validation**: Validate against embedded schema
2. **Signature Verification**: Verify `core_signature` and `capsule_signature` against the domain's public key
3. **Version Check**: Compare `updated_at_epoch_ms` with cached version
   - `new > cached` → Accept (newer version)
   - `new == cached`, same hash → Ignore (duplicate)
   - `new == cached`, different hash → **Reject** (conflict — publisher MUST increment timestamp to correct)
   - `new < cached` → **Reject** (older version)

**Content Correction:** If a publisher needs to fix a mistake (e.g., typo in synopsis, wrong spore entry), they MUST increment `updated_at_epoch_ms` before re-signing and re-publishing. This produces a new hash and a newer timestamp, which Synapse accepts as an ordinary update. The monotonic timestamp requirement ensures that corrections are unambiguous and prevents conflicting edits.

**Protection Against:**
- Replay attacks (old versions rejected by timestamp)
- Version rollback (timestamp must strictly increase)
- Ambiguous edits (same timestamp, different hash = rejected)

## 9. Example

**Entry Point (`cmn.json`):**
```json
{
  "$schema": "https://cmn.dev/schemas/v1/cmn.json",
  "capsules": [
    {
      "uri": "cmn://cmn.dev",
      "key": "ed25519.5XmkQ9vZP8nL3xJdFtR7wNcA6sY2bKgU1eH9pXb4",
      "mycelium_hash": "b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2",
      "endpoints": {
        "mycelium": "https://cmn.dev/cmn/mycelium/{hash}.json",
        "spore": "https://cmn.dev/cmn/spore/{hash}.json",
        "archive": [
          {
            "format": "tar+zstd",
            "url": "https://cmn.dev/cmn/archive/{filename}",
            "delta_url": "https://cmn.dev/cmn/archive/delta/{hash}/{old_hash}.zdict"
          }
        ]
      }
    }
  ],
  "capsule_signature": "ed25519.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa23yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2"
}
```

**Client resolution:** Take `capsules[0].mycelium_hash`, replace `{hash}` in `capsules[0].endpoints.mycelium` template → fetch full mycelium.

**Full (`/cmn/mycelium/b3.3yMR7vZQ9hL2x...pTa2.json`):**
```json
{
  "$schema": "https://cmn.dev/schemas/v1/mycelium.json",
  "capsule": {
    "uri": "cmn://cmn.dev/mycelium/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2",
    "core": {
      "name": "cmn.dev",
      "domain": "cmn.dev",
      "key": "ed25519.5XmkQ9vZP8nL3xJdFtR7wNcA6sY2bKgU1eH9pXb4",
      "synopsis": "",
      "updated_at_epoch_ms": 1769777183174,
      "spores": [
        {
          "id": "cmn-spec",
          "hash": "b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2",
          "name": "CMN Protocol Specification",
          "synopsis": "Code Mycelial Network - A sovereign-first protocol for code distribution"
        },
        {
          "id": "cmn-tools",
          "hash": "b3.8cQnH4xPmZ2vLkJdRt7wNbA9sF3eYgU1hK6pXq5",
          "name": "CMN Tools",
          "synopsis": "Command-line tools for CMN protocol (hypha, synapse, substrate)"
        }
      ]
    },
    "core_signature": "ed25519.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa23yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2"
  },
  "capsule_signature": "ed25519.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa23yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2"
}
```
