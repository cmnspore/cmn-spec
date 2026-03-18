# CMN Conformance Vectors (v1)

This directory provides implementation-neutral conformance vectors for:

- `signature`: Ed25519 verification over canonical JSON bytes
- `uri`: CMN URI parse/normalization behavior
- `merkle`: Merkle root behavior from a virtual file tree

Passing all vectors indicates baseline protocol compatibility for these areas.

## Vector Schema

Each vector file is JSON:

```json
{
  "version": "cmn-conformance-v1",
  "cases": [ ... ]
}
```

### `signature` case

```json
{
  "id": "valid_signature",
  "canonical_json": "{\"k\":\"v\"}",
  "public_key": "ed25519....",
  "signature": "ed25519....",
  "valid": true
}
```

### `uri` case

```json
{
  "id": "valid_spore",
  "uri": "cmn://example.com/b3....",
  "parse_ok": true,
  "normalized_uri": "cmn://example.com/b3...."
}
```

For invalid input:

```json
{
  "id": "invalid_hash",
  "uri": "cmn://example.com/not-a-hash",
  "parse_ok": false,
  "error_code": "invalid_hash"
}
```

### `merkle` case

```json
{
  "id": "basic_tree",
  "entries": [
    { "path": "README.md", "content": "hello\n" }
  ],
  "exclude_names": [],
  "follow_rules": [],
  "expect_ok": true,
  "root_hash": "b3...."
}
```

For invalid input:

```json
{
  "id": "nfc_conflict",
  "entries": [ ... ],
  "exclude_names": [],
  "follow_rules": [],
  "expect_ok": false,
  "error_code": "filename_nfc_conflict"
}
```

