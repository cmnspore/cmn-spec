# End-to-End Example

This walkthrough uses **cmn-spec** (the CMN Protocol Specification itself) as a real-world example, tracing the full lifecycle from publishing through discovery to consumption.

## 1. Publisher (cmn.dev)

### 1.1 Establish Mycelium Root

```bash
hypha mycelium root cmn.dev
```

This creates the site structure under `~/.cmn/mycelium/cmn.dev/`:

```
~/.cmn/mycelium/cmn.dev/
├── keys/private.pem          # Ed25519 private key (mode 0600)
├── keys/public.pem           # Ed25519 public key
└── public/
    └── .well-known/cmn.json  # Domain entry point
```

### 1.2 Prepare the Spore

In the `cmn-spec` source directory, create `spore.core.json`:

```bash
hypha hatch --id cmn-spec \
  --name "CMN Protocol Specification" \
  --domain cmn.dev \
  --synopsis "Code Mycelial Network - A sovereign-first protocol for code distribution" \
  --license CC0-1.0 \
  --intent "initial release of protocol spec"
```

This produces `spore.core.json`:

```json
{
  "$schema": "https://cmn.dev/schemas/v1/spore-core.json",
  "id": "cmn-spec",
  "name": "CMN Protocol Specification",
  "domain": "cmn.dev",
  "synopsis": "Code Mycelial Network - A sovereign-first protocol for code distribution",
  "intent": ["initial release of protocol spec"],
  "mutations": [],
  "license": "CC0-1.0",
  "bonds": [],
  "tree": {
    "algorithm": "blob_tree_blake3_nfc",
    "exclude_names": [".git"],
    "follow_rules": [".gitignore"]
  }
}
```

### 1.3 Release

```bash
hypha release --domain cmn.dev
```

The release command:
1. Reads `spore.core.json`
2. Computes Merkle Tree root hash from code content (BLAKE3)
3. Signs `core` with Ed25519 → `core_signature`
4. Constructs the hash input: `{"code":"<merkle_root>","core":<core>,"core_signature":"<sig>"}`
5. Computes final hash → `b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2`
6. Builds `capsule` with URI, core, core_signature, dist
7. Signs `capsule` → `capsule_signature`
8. Writes `spore.json` to site's `public/cmn/spore/` directory
9. Updates `mycelium.json` with new spore entry
10. Updates `cmn.json` capsule entry with new mycelium hash

**Resulting `cmn.json`:**

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
        {"type": "archive",  "url": "https://cmn.dev/cmn/archive/{hash}.tar.zst", "format": "tar+zstd"},
        {"type": "taste",    "url": "https://cmn.dev/cmn/taste/{hash}.json"}
      ]
    }
  ],
  "capsule_signature": "ed25519.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa23yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2"
}
```

**Resulting `mycelium.json`:**

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
        }
      ]
    },
    "core_signature": "ed25519.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa23yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2"
  },
  "capsule_signature": "ed25519.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa23yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2"
}
```

**Resulting `spore.json`:**

```json
{
  "$schema": "https://cmn.dev/schemas/v1/spore.json",
  "capsule": {
    "uri": "cmn://cmn.dev/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2",
    "core": {
      "name": "CMN Protocol Specification",
      "domain": "cmn.dev",
      "synopsis": "Code Mycelial Network - A sovereign-first protocol for code distribution",
      "intent": ["initial release of protocol spec"],
      "license": "CC0-1.0",
      "mutations": [],
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

### 1.4 Pulse (Optional)

Notify a Synapse instance for immediate indexing:

```bash
hypha mycelium pulse --synapse https://synapse.cmn.dev \
  --file ~/.cmn/mycelium/cmn.dev/public/cmn/spore/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2.json
```

## 2. Synapse (Indexer)

When the Synapse receives the pulse (or discovers cmn.dev via crawl):

```
1. Receive POST /synapse/pulse with signed spore manifest
2. Parse $schema → determine type (spore)
3. Extract domain from capsule.core.domain → "cmn.dev"
4. Fetch cmn.json from cmn.dev → get key from capsules[0].key
5. Verify core_signature against public key ✓
6. Verify capsule_signature against public key ✓
7. Store spore manifest in database
8. Update lineage graph (no bonds → root node)
9. Return: {"code": "ok", "result": {"action": "indexed"}}
```

The spore is now discoverable via Synapse query endpoints:

```bash
# By hash
GET /synapse/spore/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2

# By domain
GET /synapse/mycelium/cmn.dev

# By search
GET /synapse/search?q=protocol+specification
```

## 3. Visitor (bob.dev)

### 3.1 Discover

Bob searches for protocol specifications via Synapse:

```bash
hypha search "protocol specification" --synapse https://synapse.cmn.dev
```

```json
{
  "code": "ok",
  "result": {
    "query": {
      "text": "protocol specification"
    },
    "spores": [
      {
        "uri": "cmn://cmn.dev/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2",
        "domain": "cmn.dev",
        "name": "CMN Protocol Specification",
        "synopsis": "Code Mycelial Network - A sovereign-first protocol for code distribution",
        "relevance": 0.95
      }
    ]
  }
}
```

### 3.2 Inspect

```bash
hypha sense cmn://cmn.dev/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2
```

The `sense` command resolves the URI without downloading:

```
1. Parse URI → domain: cmn.dev, hash: b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2
2. Fetch https://cmn.dev/.well-known/cmn.json → public key + endpoints from capsules[0]
3. Fetch spore manifest via spore endpoint template
5. Verify core_signature ✓
6. Verify capsule_signature ✓
7. Display metadata
```

### 3.3 Taste

Before spawning, the visitor evaluates the spore:

```bash
hypha taste cmn://cmn.dev/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2
```

The `taste` command fetches the spore (and its parent, if `spawned_from` exists) to cache and outputs paths for the visitor to review. The visitor reads the code, then records a verdict — see [04-taste](04-taste.md) for the full verdict scale and processing rules:

```bash
hypha taste cmn://cmn.dev/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2 --taste safe
```

### 3.4 Spawn

```bash
hypha spawn cmn://cmn.dev/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2
cd cmn-spec
```

The `spawn` command (checks taste verdict first — blocked if untasted or `toxic`; `rotten` warns and continues):
1. Verifies the spore has been tasted (any verdict except `toxic` and untasted)
2. Clones from git dist endpoint to local cache bare repo
3. Clones from cache to `./cmn-spec`
4. Adds `spawned_from` bond to `spore.core.json`

Bob now has a working copy with lineage:

```json
{
  "$schema": "https://cmn.dev/schemas/v1/spore-core.json",
  "id": "cmn-spec",
  "name": "CMN Protocol Specification",
  "domain": "cmn.dev",
  "synopsis": "Code Mycelial Network - A sovereign-first protocol for code distribution",
  "intent": [],
  "mutations": [],
  "license": "CC0-1.0",
  "bonds": [
    {
      "uri": "cmn://cmn.dev/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2",
      "relation": "spawned_from"
    }
  ],
  "tree": {
    "algorithm": "blob_tree_blake3_nfc",
    "exclude_names": [".git"],
    "follow_rules": [".gitignore"]
  }
}
```

## 4. Becoming a Publisher (bob.dev)

Bob modifies the code and releases it under his own domain — transitioning from visitor to publisher:

```bash
# Update metadata for bob's domain
hypha hatch --domain bob.dev \
  --name "CMN Spec - Bob's Fork" \
  --intent "add examples for edge cases" \
  --mutations "Added §3 edge case examples"

# Release under bob.dev
hypha release --domain bob.dev
```

Bob's `spore.json` now has a different hash (because core changed) and traces back to the original:

```json
{
  "$schema": "https://cmn.dev/schemas/v1/spore.json",
  "capsule": {
    "uri": "cmn://bob.dev/b3.8cQnH4xPmZ2vLkJdRt7wNbA9sF3eYgU1hK6pXq5",
    "core": {
      "name": "CMN Spec - Bob's Fork",
      "domain": "bob.dev",
      "synopsis": "Code Mycelial Network - A sovereign-first protocol for code distribution",
      "intent": ["add examples for edge cases"],
      "mutations": ["Added §3 edge case examples"],
      "license": "CC0-1.0",
      "bonds": [
        {
          "uri": "cmn://cmn.dev/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2",
          "relation": "spawned_from"
        }
      ],
      "tree": {
        "algorithm": "blob_tree_blake3_nfc",
        "exclude_names": [".git"],
        "follow_rules": [".gitignore"]
      }
    },
    "core_signature": "ed25519.<bob_sig>",
    "dist": [
      { "type": "archive" }
    ]
  },
  "capsule_signature": "ed25519.<bob_capsule_sig>"
}
```

Both signatures verify against `bob.dev`'s public key. The `spawned_from` bond creates a traceable link back to the original `cmn.dev` release.

## Summary

```
Publisher (cmn.dev)          Synapse                    bob.dev
─────────────────           ─────────                  ───────
mycelium root
hatch
release ─── pulse ──────→ verify + index
                                                       ── Visitor (read-only) ──
                                            search ←── "protocol spec"
                                            sense  ←── inspect metadata (from cmn.dev)
                                            taste  ←── evaluate safety
                                            spawn  ←── create working copy
                                                       ── Publisher ──
                                                       modify code
                                                       hatch
                          verify + index ←── pulse ─── release
```

Each domain is sovereign. Each fork is first-class. Lineage is traceable. No central authority required.
