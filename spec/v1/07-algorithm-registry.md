# 07. Algorithm Registry

This chapter defines the canonical algorithm identifiers used across CMN.

## 1. Purpose

CMN uses text algorithm identifiers in hashes, signatures, keys, and tree configuration. A shared registry ensures:

- deterministic verification across implementations
- safe extensibility without field redesign
- downgrade resistance when an implementation encounters unknown or deprecated algorithms

## 2. Registry Entries

### 2.1 Value Prefix Algorithms (`algorithm.value`)

These identifiers appear as prefixes in values such as `b3.<base58>` and `ed25519.<base58>`.

| Kind | Identifier | Meaning | Status | Deprecated after |
| :--- | :--- | :--- | :--- | :--- |
| Hash | `b3` | BLAKE3 32-byte digest, Base58-encoded | Active | - |
| Key | `ed25519` | Ed25519 public key, Base58-encoded. This is the v1 Ed25519 identifier. | Active | - |
| Signature | `ed25519` | Ed25519 signature, Base58-encoded. This is the v1 Ed25519 identifier. | Active | - |

## 2.2 Tree Algorithms (`capsule.core.tree.algorithm`)

| Identifier | Meaning | Status | Deprecated after |
| :--- | :--- | :--- | :--- |
| `blob_tree_blake3_nfc` | Git-like blob/tree construction + BLAKE3 hashing + NFC filename normalization, with CMN portable sibling-collision rejection | Active | - |

`blob_tree_blake3_nfc` encodes and sorts tree entry names using NFC-normalized UTF-8 bytes as defined in [03-spore §4.6](./03-spore.md#4-6-tree-hash-merkle-tree). Before content is accepted, implementations MUST also reject sibling path components that collide under CMN portable filename matching (`filename_portable_conflict`). This stricter validity rule does not change the hash bytes for valid trees.

## 3. Processing Rules

Implementations MUST reject values with unknown `algorithm.value` prefixes when verification is required.

Implementations MUST reject values or content that declare an algorithm whose registry status is `deprecated` and the verification time is after `deprecated_after`.

Implementations MUST fail content verification when `tree.algorithm` is unknown or deprecated after its `deprecated_after` time.

Implementations SHOULD return explicit machine-readable errors for unknown or deprecated algorithms (for example, `unsupported_algorithm` or `deprecated_algorithm`).

These rules are downgrade protection: an attacker must not be able to move content from a stronger/current algorithm to an unknown, legacy, or deprecated one and have it accepted.

## 4. Registry Evolution

Adding a new optional algorithm identifier is non-breaking when existing identifiers remain supported.

Removing support for an active identifier is a breaking change unless the identifier has first moved through the deprecation lifecycle below.

New identifiers SHOULD be documented here before production use.

Future algorithm identifiers use a single token before the dot and SHOULD include a version or suite marker when that avoids ambiguity, for example `ed25519v2`, `mldsa44`, or `ed25519mldsa44`. Existing `ed25519` is retained as the v1 Ed25519 identifier to avoid re-signing already published content.

### 4.1 Algorithm Migration

When new algorithms are added to the registry:

1. New algorithm is added with status **active**.
2. Old algorithm status changes to **deprecated** with a `deprecated_after` timestamp or protocol release identifier.
3. Before `deprecated_after`, consumers MAY warn on use.
4. After `deprecated_after`, consumers MUST reject content using the deprecated algorithm.

### 4.2 Post-Quantum Migration Position

CMN v1 keeps Ed25519 as the active signature algorithm. Ed25519 remains small, fast, widely implemented, and well understood. Post-quantum signature schemes are larger and still maturing operationally, and CMN signatures do not create a meaningful "store now, decrypt later" confidentiality risk.

If ecosystem signals justify a migration, CMN can register a new algorithm identifier (for example ML-DSA or a hybrid Ed25519+ML-DSA suite) and use the lifecycle above. No protocol flag day is required.
