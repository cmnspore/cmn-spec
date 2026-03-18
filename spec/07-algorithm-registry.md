# 07. Algorithm Registry

This chapter defines the canonical algorithm identifiers used across CMN.

## 1. Purpose

CMN uses text algorithm identifiers in hashes, signatures, keys, and tree configuration. A shared registry ensures:

- deterministic verification across implementations
- safe extensibility without field redesign
- clear behavior when an implementation encounters unknown algorithms

## 2. Registry Entries

### 2.1 Value Prefix Algorithms (`algorithm.value`)

These identifiers appear as prefixes in values such as `b3.<base58>` and `ed25519.<base58>`.

| Kind | Identifier | Meaning | Status |
| :--- | :--- | :--- | :--- |
| Hash | `b3` | BLAKE3 32-byte digest, Base58-encoded | Active |
| Key | `ed25519` | Ed25519 public key, Base58-encoded | Active |
| Signature | `ed25519` | Ed25519 signature, Base58-encoded | Active |

## 2.2 Tree Algorithms (`capsule.core.tree.algorithm`)

| Identifier | Meaning | Status |
| :--- | :--- | :--- |
| `blob_tree_blake3_nfc` | Git-like blob/tree construction + BLAKE3 hashing + NFC filename normalization | Active |

## 3. Processing Rules

Implementations MUST reject values with unknown `algorithm.value` prefixes when verification is required.

Implementations MUST fail content verification when `tree.algorithm` is unknown.

Implementations SHOULD return explicit machine-readable errors for unknown algorithms (for example, `unsupported_algorithm`).

## 4. Registry Evolution

Adding a new optional algorithm identifier is non-breaking when existing identifiers remain supported.

Removing support for an active identifier is a breaking change.

New identifiers SHOULD be documented here before production use.

### 4.1 Algorithm Migration

When new algorithms are added to the registry:

1. New algorithm is added with status **active**.
2. Old algorithm status changes to **deprecated** — consumers SHOULD warn on use.
3. After a transition period, old algorithm status changes to **retired** — consumers MAY reject content using retired algorithms.
