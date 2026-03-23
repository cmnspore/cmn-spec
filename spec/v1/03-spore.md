# 03. Spore - Package Format

The **Spore** is a **Logic Capsule**. It relies on its URI for identity and carries the logic DNA.

**Location:** Defined by the `type: "spore"` endpoint in `cmn.json` (e.g., `https://cmn.dev/cmn/spore/{hash}.json`)
**Schema:** `https://cmn.dev/schemas/v1/spore.json`

## 1. The `spore.json` Manifest

```json
{
  "$schema": "https://cmn.dev/schemas/v1/spore.json",
  "capsule": {
    "uri": "cmn://cmn.dev/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2",
    "core": {
      "id": "cmn-spec",
      "name": "CMN Protocol Specification",
      "domain": "cmn.dev",
      "key": "ed25519.5XmkQ9vZP8nL3xJdFtR7wNcA6sY2bKgU1eH9pXb4",
      "synopsis": "Code Mycelial Network - A sovereign-first protocol for code distribution",
      "intent": ["add intent and changes array fields to spore core"],
      "license": "CC0-1.0",
      "mutations": [
        "§2.2 Core Fields: intent type String → Array",
        "§2.2 Core Fields: add mutations field (Array)",
        "§2.4 Bond Types: add optional reason field",
        "§1, §4.1, §6 example JSON updated"
      ],
      "size_bytes": 142857,
      "updated_at_epoch_ms": 1700000000000,
      "bonds": [],
      "tree": {
        "algorithm": "blob_tree_blake3_nfc",
        "exclude_names": [".git"],
        "follow_rules": [".gitignore"]
      }
    },
    "core_signature": "ed25519.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa23yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2",
    "dist": [
      { "type": "archive" }
    ]
  },
  "capsule_signature": "ed25519.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa23yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2"
}
```

## 2. Field Definitions

### 2.1 Common Fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `$schema` | String | Schema URL: `https://cmn.dev/schemas/v1/spore.json` |
| `capsule` | Object | The capsule container. |
| `capsule.uri` | String | Full URI: `cmn://{domain}/{hash}` |
| `capsule_signature` | String | Ed25519 signature of entire `capsule` object (`ed25519.<base58>`, JCS canonical). |

### 2.2 Core Fields (Immutable)

| Field | Type | Description |
| :--- | :--- | :--- |
| `capsule.core` | Object | Immutable metadata (part of spore identity). |
| `capsule.core.name` | String | Human-readable display name (e.g., `CMN Protocol Specification`). |
| `capsule.core.domain` | String | The domain of the publisher (e.g., `cmn.dev`). |
| `capsule.core.key` | String | Author's Ed25519 public key (`ed25519.<base58>`). Embedded at release time — enables offline signature verification without fetching `cmn.json`. See [01-substrate §1.2.4](./01-substrate.md#1-2-4-key-trust-model) for trust model. |
| `capsule.core.synopsis` | String | One-line summary — a visitor reads this alone and understands what the spore does. |
| `capsule.core.intent` | Array | The spore's reason for being — why it exists, what problem it solves, who it serves. Each array element is a paragraph. Permanent across releases — a reader understands the spore's purpose from intent alone, without reading source code. |
| `capsule.core.mutations` | Array | What changed in this release relative to the `spawned_from` parent. Each entry is a concise change description — specific, factual, reviewable. Rewritten on each release. |
| `capsule.core.size_bytes` | Number | Total uncompressed source size in bytes — sum of all blob content sizes from tree hash computation. Populated by release tooling, not present in `spore.core.json` draft. |
| `capsule.core.license` | String | SPDX License Identifier. |
| `capsule.core.bonds` | Array | List of `{uri, relation, id?, reason?}` (See §2.4 Bond Types). |
| `capsule.core.tree` | Object | Tree hash configuration. |
| `capsule.core.tree.algorithm` | String | Tree hash algorithm (e.g., `blob_tree_blake3_nfc`). |
| `capsule.core.tree.exclude_names` | Array | Files/patterns to skip (e.g., `[".git"]`). |
| `capsule.core.tree.follow_rules` | Array | Ignore systems to honor (e.g., `[".gitignore"]`). |
| `capsule.core.updated_at_epoch_ms` | Number | Content update timestamp (milliseconds since Unix epoch). Publishers SHOULD derive it from the latest Git commit time for the source tree when available, with max file mtime as fallback. |
| `capsule.core_signature` | String | Ed25519 signature of `capsule.core` (`ed25519.<base58>`, JCS canonical). |

### 2.2.1 Common Extensions

The following fields are **optional** and not required by the protocol. When present in `core`, they participate in the hash like any other core field.

| Field | Type | Description |
| :--- | :--- | :--- |
| `capsule.core.id` | String | Opaque publisher-defined identifier (e.g., `cmn-spec`). Useful for mycelium deduplication and tooling. |
| `capsule.core.version` | String | Human-readable version (e.g., `1.0.0`). Meaningful to the publisher; visitors address by hash. |

**id vs name:**
- `id`: Consumers MUST treat it as opaque and MUST NOT use raw `id` directly as a filesystem path, shell token, or URL path segment.
- Implementations MAY derive a local-safe name from `id`. If that derivation is unsafe or collides, they MUST fall back to the spore hash.
- `name`: Displayed to users. Can contain spaces and special characters.

### 2.3 Distribution Fields (Mutable)

| Field | Type | Description |
| :--- | :--- | :--- |
| `capsule.dist` | Array | Physical source locations (e.g., `git`, `ipfs`). Replicate-friendly. MUST contain at least one entry. |

Each `dist` entry MUST be one of:
- `{ "type": "archive" }` — archive download, resolved via `cmn.json` endpoints
- `{ "type": "git", "url": "<url>", "ref"?: "<ref>" }`
- `{ "type": "ipfs", "cid": "<cid-or-uri>" }`
- `{ "type": "<extension>", ... }` (protocol extension entry)

The first three are built-in v1 entries. `archive` uses endpoint indirection: the spore's hash is resolved through the `type: "archive"` endpoint's `url` template in `cmn.json` (e.g., `https://example.com/cmn/archive/{hash}.tar.zst`). No `filename` field is needed — the URL template includes the file extension. For future protocols, use the extension form with a `type` field (for example, `{ "type": "s3", "url": "..." }`). Consumers that do not understand an extension `type` MAY skip that entry and continue trying other `dist` entries.

**Incremental delivery note:**
- `type=archive` is a full content snapshot transport.
- Delta discovery is endpoint-driven (not dist-driven): clients MAY attempt the archive endpoint's `delta_url` first when present.
- `delta_url` MUST include `{hash}` (target hash) and `{old_hash}` (local cached base hash). Delta direction is always `old_hash -> hash`.
- Clients MUST use the archive endpoint's `format` field to select decoders, not URL suffix guessing.
- The examples in this spec use `format = tar+zstd`, but the protocol does not privilege any single archive format.
- If delta fetch/apply fails, or no valid base is available, clients SHOULD fall back to full `type=archive`.
- Any optimization path (delta or full) MUST converge to the same final verified content hash (see §5.1).

### 2.4 Bond Types

Bonds declare relationships to other spores:

```json
{
  "bonds": [
    {
      "relation": "spawned_from",
      "uri": "cmn://cmn.dev/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2"
    },
    {
      "relation": "depends_on",
      "uri": "cmn://lib.dev/b3.8cQnH4xPmZ2vLkJdRt7wNbA9sF3eYgU1hK6pXq5",
      "id": "signing-lib",
      "reason": "Provides Ed25519 signature verification for spore manifests and domain key validation"
    },
    {
      "relation": "follows",
      "uri": "cmn://cmn.dev/b3.8cQnH4xPmZ2vLkJdRt7wNbA9sF3eYgU1hK6pXq5",
      "id": "agent-first-data",
      "reason": "Implements agent-first-data naming conventions for all field names"
    },
    {
      "relation": "absorbed_from",
      "uri": "cmn://other.dev/b3.8cQnH4xPmZ2vLkJdRt7wNbA9sF3eYgU1hK6pXq5",
      "reason": "Merged authentication module with OAuth and domain verification support"
    }
  ]
}
```

**Bond fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `uri` | String | Yes | CMN URI of the bonded spore (e.g., `cmn://{domain}/{hash}`) |
| `relation` | String | Yes | Relationship type (see predefined types below) |
| `id` | String | No | Optional opaque alias for this bond. See `id` handling in §2.2.1. |
| `reason` | String | No | Why this bond exists and what role it plays in this spore |
| `with` | Object | No | Bond-specific parameters defined by the bonded spore's convention |

**Predefined relation types:**

- **`spawned_from`** — Source this spore was cloned/derived from. The URI includes the hash of the version spawned from.
- **`absorbed_from`** — Source that was merged into this spore. Unlike `spawned_from`, represents a one-time merge. A spore can have multiple `absorbed_from` bonds.
- **`depends_on`** — Runtime, build, or protocol dependency required by this spore.
- **`follows`** — Convention or standard that this spore adheres to (e.g., data format conventions, API guidelines).
- **`extends`** — Direct parent convention or family relationship declared by this spore. Used for explicit, non-transitive hierarchy between strain definitions. See [05-strain](./05-strain.md).

> **Note**: Custom relation types are allowed (the `relation` field accepts any string). The predefined types above provide semantic meaning for tooling. For custom values, namespaced names are recommended to avoid collisions (e.g., `example.com/deploys_to`).

**The `reason` field:**

The optional `reason` field explains why this bond exists from the bonding spore's perspective. It is most useful for:
- **`depends_on`** — what role the dependency plays (e.g., "Provides cryptographic signing")
- **`follows`** — which parts of the convention are implemented (e.g., "Implements payment protocol with Cashu support")
- **`extends`** — the direct parent relationship (e.g., "Extends strain-payment-method")
- **`absorbed_from`** — what was merged (e.g., "Merged authentication module")

**Note:** `spawned_from` typically does NOT need `reason` because the `mutations` field already documents what was modified in this spawn.

Visitors can read the `reason` field to understand the purpose and context of each bond without needing to fetch the bonded spore's metadata.

**The `with` field:**

The optional `with` field carries bond-specific parameters whose schema is defined by the bonded spore's convention. It allows a spore to declare details about how it uses the bonded spore:

```json
{
  "relation": "follows",
  "uri": "cmn://cmn.dev/b3.xxx",
  "id": "strain-payment-method-evm",
  "reason": "Accepts EVM payments",
  "with": {
    "chains": [8453, 42161],
    "tokens": ["native", "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"]
  }
}
```

The `with` value is an opaque object to the CMN protocol — its structure is defined entirely by the bonded spore. For example, `strain-payment-method-evm` defines that `with` may contain `chains` and `tokens`; `strain-payment-method-cashu` defines that `with` may contain `mints`.

### 2.5 Dependency Model

**Taste gate:** All operations that place code into a visitor's working directory — spawning, growing, absorbing, and bonding — require the target spore to have been tasted. See [04-taste](04-taste.md) for verdict definitions, processing rules, and the taste capsule format.

**Replicate convention:** When releasing a spore, publishers SHOULD replicate all bonds that point to other domains (see [§6.1 Replicate](#6-1-replicate-same-hash)). A replicate hosts the same spore (identical hash, identical `core` and `core_signature`) under the publisher's own domain, re-signed with the publisher's capsule key. The bond URI then points to the publisher's replicate:

```json
{
  "bonds": [
    {
      "relation": "depends_on",
      "uri": "cmn://mydomain.com/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2",
      "reason": "Parsing library"
    },
    {
      "relation": "depends_on",
      "uri": "cmn://mydomain.com/b3.8cQnH4xPmZ2vLkJdRt7wNbA9sF3eYgU1hK6pXq5",
      "reason": "Agent-first-data naming conventions"
    }
  ]
}
```

The hash is identical to the original — `core.domain` still identifies the original author. Visitors can reach all bonded spores from a single domain, and verify authorship via `core_signature` against the original domain's key. This ensures:

- Visitors only need to reach the publisher's domain for all bonds
- The publisher's spores remain functional if upstream domains go offline
- Authorship is preserved in `core.domain` — replicates cannot alter it

**Working directory (`.cmn/`):** A visitor's spawned project uses a `.cmn/` directory for CMN operational data. This directory is project-local, gitignored, and fully regenerable from `spore.core.json`:

```
my-project/
├── src/
├── spore.core.json
└── .cmn/                       ← gitignored, regenerable
    ├── bonds/                  ← bonded spores (from bond)
    │   ├── bonds.json          ← index of all bonds
    │   └── {id-or-hash}/       ← id when present, hash otherwise
    │       ├── spore.json      ← spore manifest
    │       └── content/
    └── absorb/                 ← absorb staging (temporary)
        ├── ABSORB.md
        └── {hash}/
            └── content/
```

The **bond** operation reads `spore.core.json` bonds and fetches tasted-safe bonded spores to `.cmn/bonds/`. It excludes `spawned_from` (handled by `grow`) and `absorbed_from` (historical — the merge is already done). Each bond is stored under an implementation-defined local-safe name derived from `id` when present; if absent, unsafe, or colliding, implementations fall back to the hash. A `bonds.json` index maps dir names to hashes, URIs, relations, and names for quick lookup by build systems and tools.

## 3. Schema Validation

### 3.1 Schema URL

| Type | Schema URL |
| :--- | :--- |
| Spore | `https://cmn.dev/schemas/v1/spore.json` |

### 3.2 Embedded Schemas

Validators SHOULD embed schemas for offline validation. No network fetch should be required.

## 4. Signing and Hashing

### 4.1 Two-Layer Signature

The spore uses a **two-layer signature** scheme:

```
┌─────────────────────────────────────────────────────┐
│ capsule                                             │
│  ┌───────────────────────────────────────────────┐  │
│  │ core (immutable)                              │  │
│  │  name, domain, key, synopsis, intent,         │  │
│  │  mutations, size_bytes, license, bonds, tree, │  │
│  │  updated_at_epoch_ms, id?, version?           │  │
│  └───────────────────────────────────────────────┘  │
│  core_signature ← signs core                        │
│  uri ← contains hash (computed from code+core+sig) │
│  dist (mutable by replicators)                      │
└─────────────────────────────────────────────────────┘
capsule_signature ← signs entire capsule
```

### 4.2 Core Signature

The `capsule.core_signature` signs the immutable metadata:

1. Serialize `core` using JCS (RFC 8785)
2. Sign with domain's Ed25519 private key → `ed25519.<base58>`

**Purpose:**
- Protects immutable metadata (name, synopsis, license, etc.)
- Can be verified independently without dist information
- Replicators cannot change core without breaking this signature

### 4.3 URI Hash Calculation

The hash in `capsule.uri` is calculated from **tree hash** (Merkle Tree) + **core** + **core_signature**:

1. Compute tree hash (see §4.6)
2. Construct hash input: `{"tree_hash": "<tree_hash>", "core": <core>, "core_signature": "<signature>"}`
3. Serialize hash input using JCS
4. Hash with BLAKE3 → `b3.<base58>`
5. Construct URI: `cmn://{domain}/b3.<base58>`

**Key Properties:**
- `capsule.dist` does **NOT** participate in the hash (replicators can change distribution URLs)
- `capsule_signature` does **NOT** participate in the hash (can be re-signed by replicators)
- Changing `core` metadata changes the hash
- Code hash is based on Merkle Tree

### 4.4 Capsule Signature

The `capsule_signature` signs the entire capsule object (including `uri`, `core`, `core_signature`, `dist`):

1. Serialize `capsule` using JCS
2. Sign with domain's (or replicate host's) Ed25519 private key → `ed25519.<base58>`

**Purpose:**
- Validates the complete capsule including dist and uri
- Ensures dist information is authorized
- When a replicate host changes dist, they re-sign with their key (but cannot change core)

### 4.5 Canonical JSON (JCS)

All signatures and hashes use JCS (see [01-substrate §1.3](./01-substrate.md#1-3-value-formats)).

### 4.6 Tree Hash (Merkle Tree)

The tree hash uses a **Git-like Merkle Tree** approach for content-addressing.

#### 4.6.1 Hashing Configuration

The `capsule.core.tree` field controls the tree hash algorithm and which files are included:

**`algorithm` (String):**
- Declares the tree hash algorithm used (e.g., `blob_tree_blake3_nfc`)
- Components: `blob_tree` (object format) + `blake3` (hash function) + `nfc` (Unicode normalization)
- Visitors that don't recognize the algorithm cannot verify the content hash
- Registered algorithm names are listed in [07-algorithm-registry](./07-algorithm-registry.md)

**`exclude_names` (Name List):**
- Exact basename match list for directory/file names to skip
- No implicit exclusions — all exclusions must be explicit in this list

**`follow_rules` (Engine List):**
- List of standard ignore file formats to honor (e.g., `".gitignore"`)
- Each item is resolved at the hashing root (for example, `<root>/.gitignore`)
- Existing files are parsed with gitignore-compatible semantics
- Missing files are ignored (no error)
- Files matching these rules are skipped during hashing

#### 4.6.2 Merkle Tree Construction (Git-compatible)

CMN uses **Git-like Merkle Tree** format with two differences:
1. **BLAKE3** (32 bytes) instead of SHA-1 (20 bytes)
2. **NFC normalization** for filenames (cross-platform consistency)

**Blobs (Files):**

Concatenate header and file content, then BLAKE3 hash the result:

```
blob <content_length>\0<file_content>
```

Example: A file containing `hello` (5 bytes) → `blob 5\0hello` → BLAKE3 → 32-byte hash.

**Trees (Directories):**

Build sorted entries, prepend header, then BLAKE3 hash:

```
tree <entries_length>\0<entry_1><entry_2>...
```

Each entry:
```
<mode> <name>\0<32-byte-binary-hash>
```

Processing rules:
- Traverse recursively from the selected root directory.
- Include regular files and directories.
- Skip symlinks and special files (device/socket/FIFO).
- Normalize each filename segment to NFC before tree entry encoding.
- If two sibling entries normalize to the same NFC name, hashing MUST fail (`filename_nfc_conflict`).
- Sort sibling entries by normalized-name UTF-8 byte order (ascending, locale-independent).

**Entry Format:**
- Git format: `<mode> <name>\0<32-byte-binary-hash>`
- Mode values:
  - `100644`: Regular file
  - `100755`: Executable file
  - `40000`: Directory
- On non-Unix platforms without executable bit semantics, regular files use `100644`.
- Hash is **binary** (32 bytes for BLAKE3)

#### 4.6.3 Unicode NFC Normalization

> **See also:** §4.6.4 below for a complete step-by-step worked example.



To prevent hash mismatches between operating systems (macOS NFD vs. Linux NFC):

- **Rule**: All filenames MUST be converted to Unicode Normalization Form C (NFC) before hashing
- **Example**: `á.txt` (combining character) → `á.txt` (precomposed character)

#### 4.6.4 Worked Example

A directory with two files:

```
my-project/
├── README.md    (13 bytes: "Hello, CMN!\n")
└── src/
    └── main.rs  (14 bytes: "fn main() {}\n")
```

**Step 1 — Hash blobs (files):**

Each file is prefixed with `blob <length>\0`:

```
README.md:
  Input bytes: "blob 13\0Hello, CMN!\n"   (5 + 2 + 1 + 13 = 21 bytes)
  BLAKE3 → readme_hash (32 bytes binary)

src/main.rs:
  Input bytes: "blob 14\0fn main() {}\n"  (5 + 2 + 1 + 14 = 22 bytes)
  BLAKE3 → main_hash (32 bytes binary)
```

**Step 2 — Build the `src/` tree:**

One entry for `main.rs`, sorted alphabetically (only one entry here):

```
Entry: "100644 main.rs\0" + main_hash (32 bytes binary)
```

Concatenate all entries to get `src_entries`. Prepend header:

```
Input bytes: "tree <len(src_entries)>\0" + src_entries
BLAKE3 → src_tree_hash (32 bytes binary)
```

**Step 3 — Build the root tree:**

Two entries sorted alphabetically: `README.md` (file), `src` (directory):

```
Entry 1: "100644 README.md\0" + readme_hash (32 bytes binary)
Entry 2: "40000 src\0" + src_tree_hash (32 bytes binary)
```

Concatenate entries to get `root_entries`. Prepend header:

```
Input bytes: "tree <len(root_entries)>\0" + root_entries
BLAKE3 → root_hash (32 bytes binary)
```

**Step 4 — Format root hash:**

Convert `root_hash` to base58 → `b3.<~44 base58 chars>`

This root hash is the **tree_hash** used in §4.3 (URI hash calculation).

**Key details:**
- File mode `100644` for regular files, `100755` for executables, `40000` for directories
- Hash bytes are **binary** (32 bytes), not hex — same as Git's tree entry format
- Filenames are NFC-normalized before sorting (§4.6.3)
- The `tree.exclude_names` and `tree.follow_rules` filters are applied before hashing — excluded files never appear in the tree

#### 4.6.5 Binary Format Reference

This section provides the definitive byte-level encoding for cross-implementation compatibility.

**Blob (file):**

| Offset | Content | Encoding |
| :--- | :--- | :--- |
| 0 | `blob ` | ASCII (5 bytes including trailing space 0x20) |
| 5 | `<length>` | ASCII decimal, no leading zeros (except `0` for empty files) |
| 5+len(length) | `\0` | NUL byte (0x00) |
| 5+len(length)+1 | `<content>` | Raw file bytes |

`hash = BLAKE3(entire blob from offset 0)`

**Tree entry:**

| Offset | Content | Encoding |
| :--- | :--- | :--- |
| 0 | `<mode>` | ASCII: `100644` (regular), `100755` (executable), `40000` (directory) |
| len(mode) | ` ` | Space (0x20) |
| len(mode)+1 | `<name>` | NFC-normalized filename, UTF-8 bytes |
| len(mode)+1+len(name) | `\0` | NUL byte (0x00) |
| len(mode)+1+len(name)+1 | `<hash>` | Raw binary BLAKE3 hash (32 bytes, NOT hex/base58) |

**Tree (directory):**

| Offset | Content | Encoding |
| :--- | :--- | :--- |
| 0 | `tree ` | ASCII (5 bytes including trailing space 0x20) |
| 5 | `<entries_length>` | ASCII decimal byte count of concatenated entries |
| 5+len(entries_length) | `\0` | NUL byte (0x00) |
| 5+len(entries_length)+1 | `<entries>` | Concatenated tree entries, sorted by NFC-name UTF-8 byte order (ascending) |

`hash = BLAKE3(entire tree from offset 0)`

**Root hash output:** Base58-encode the 32-byte root tree hash → `b3.<base58>`

**Implementor notes:**
- On non-Unix platforms without executable bit semantics, all regular files use mode `100644`
- `<decimal-ascii-length>` uses no leading zeros, except the value `0` itself for an empty blob or tree
- Entry sort order is locale-independent: compare NFC-normalized name bytes as unsigned integers

## 5. Content Verification

### 5.1 Integrity (MUST)

After obtaining spore content through **any** distribution channel (archive, git, IPFS, or any other `dist` source), the client **MUST** compute the Merkle Tree hash (§4.6) and verify it matches the hash in the spore URI. Content with mismatched hashes **MUST** be rejected.

### 5.2 Review (SHOULD)

Hash verification only proves "content has not been tampered with" — it does not prove "content is safe." Clients **SHOULD** review spore content before use. The [taste](./04-taste.md) system provides a framework for recording and sharing review results.

### 5.3 Key Trust Verification

Spores with `capsule.core.key` support offline signature verification. The embedded key allows clients to verify `core_signature` locally, then establish trust in the key through the tiered model described in [01-substrate §1.2.4](./01-substrate.md#1-2-4-key-trust-model).

For replicates (where `core.domain` differs from the URI domain), `core.key` is the original author's key — `core_signature` verifies against it. The `capsule_signature` still verifies against the hosting domain's key from `cmn.json`.

## 6. Replicating and Spawning

### 6.1 Replicate (Same Hash)

A **replicate** hosts the same spore with different `dist` URLs:

```json
{
  "$schema": "https://cmn.dev/schemas/v1/spore.json",
  "capsule": {
    "uri": "cmn://replicate.dev/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2",
    "core": {
      "name": "CMN Protocol Specification",
      "domain": "cmn.dev"
    },
    "core_signature": "ed25519.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa23yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2",
    "dist": [
      { "type": "archive" }
    ]
  },
  "capsule_signature": "ed25519...."
}
```

**Verification:**
1. If `core.key` is present, verify `core_signature` against `core.key` locally; otherwise fetch `cmn.dev` public key from `cmn.json`
2. Establish key trust via domain confirmation or Synapse witness (see [01-substrate §1.2.4](./01-substrate.md#1-2-4-key-trust-model))
3. URI hash matches (`b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2`)
4. `domain ≠ URI domain` → This is a replicate hosted by `replicate.dev`
5. `capsule_signature` verifies against `replicate.dev` public key

### 6.2 Spawn (Different Hash)

A **spawn** creates a new spore derived from an existing one (new domain, modified metadata):

```json
{
  "$schema": "https://cmn.dev/schemas/v1/spore.json",
  "capsule": {
    "uri": "cmn://fork.dev/b3.8cQnH4xPmZ2vLkJdRt7wNbA9sF3eYgU1hK6pXq5",
    "core": {
      "name": "CMN Spec Spawn",
      "domain": "fork.dev",
      "bonds": [
        {
          "relation": "spawned_from",
          "uri": "cmn://cmn.dev/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2"
        }
      ]
    },
    "core_signature": "ed25519....",
    "dist": [...]
  },
  "capsule_signature": "ed25519...."
}
```

**Properties:**
- Different hash (because core metadata changed)
- New domain and signatures
- Bonds to the original spore

## 7. spore.core.json

Each spore source directory includes a `spore.core.json` file containing the author-maintained portion of `capsule.core` (§2.2). It does not contain `dist`, signatures, `size_bytes`, or `updated_at_epoch_ms` — those are computed and added during release. Publishing implementations also populate `key` during release if absent from the draft.

**Schema:** `https://cmn.dev/schemas/v1/spore-core.json`

### 7.1 Field Reference

**Required fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | String | Human-readable display name. |
| `domain` | String | Publisher domain (e.g., `cmn.dev`). |
| `synopsis` | String | One-line summary — a visitor reads this alone and understands what the spore does. |
| `intent` | Array | Multi-paragraph description of this spore's functionality and purpose — what it does, how it works, why it exists. Each array item is a paragraph. Permanent — not cleared on release. Required for `release`. |
| `license` | String | SPDX License Identifier. |
| `tree` | Object | Tree hash configuration. Required for deterministic content hashing. |

**Optional fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | String | Opaque publisher-defined identifier (e.g., `cmn-spec`). Useful for mycelium deduplication and tooling. |
| `version` | String | Human-readable version (e.g., `1.0.0`). Informational only; visitors address by hash. |
| `key` | String | Author public key. If omitted in `spore.core.json`, the publishing implementation MUST populate it from the current signing domain identity during release. If present, it MUST match that domain identity. |
| `mutations` | Array | What changed relative to the `spawned_from` parent — describes the mutations applied to derive this spore from its ancestor. |
| `bonds` | Array | List of `{uri, relation, id?, reason?}` objects (see §2.4). |

**`tree` sub-fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `algorithm` | String | Tree hash algorithm (e.g., `blob_tree_blake3_nfc`). |
| `exclude_names` | Array | Directories or files to skip during hashing (e.g., `[".git"]`). |
| `follow_rules` | Array | Standard ignore file formats to honor (e.g., `[".gitignore"]`). |

### 7.2 Complete Example

```json
{
  "$schema": "https://cmn.dev/schemas/v1/spore-core.json",
  "id": "cmn-spec",
  "version": "1.2.0",
  "name": "CMN Protocol Specification",
  "domain": "cmn.dev",
  "synopsis": "Code Mycelial Network - A sovereign-first protocol for code distribution",
  "intent": ["add intent and changes array fields to spore core"],
  "license": "CC0-1.0",
  "mutations": [
    "§2.2 Core Fields: intent type String → Array",
    "§2.2 Core Fields: add mutations field (Array)",
    "§1, §4.1, §6 example JSON updated"
  ],
  "bonds": [
    {
      "relation": "spawned_from",
      "uri": "cmn://cmn.dev/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2"
    }
  ],
  "tree": {
    "algorithm": "blob_tree_blake3_nfc",
    "exclude_names": [".git"],
    "follow_rules": [".gitignore"]
  }
}
```

### 7.3 Lifecycle

```
spore.core.json (local draft, committed to git)
     │
     │  publish-preparation step  ← create or update metadata
     │
     ▼
release implementation
     │
     ├── Read spore.core.json
     ├── Compute Merkle Tree root hash and size_bytes (§4.6)
     ├── Sign core → core_signature
     ├── Compute URI hash (§4.3)
     ├── Add dist endpoints
     ├── Sign capsule → capsule_signature
     │
     ▼
spore.json (signed, published, immutable)
```

The `spore.core.json` file is the only file a developer edits directly. A release implementation reads it, populates `key` if absent, computes `size_bytes` and `updated_at_epoch_ms`, adds `dist`, signatures, and URI, and produces the final `spore.json`.
