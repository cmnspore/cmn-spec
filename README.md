# CMN Protocol Specification

Code Mycelial Network — a sovereign-first protocol for code distribution where domains publish signed, hash-verified packages without central registries.

## Normative Language

The key words `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` in this specification are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in all capitals.

## Start with the path that matches your role

- **New to CMN:** Read [01. Substrate](spec/v1/01-substrate.md), [02. Mycelium](spec/v1/02-mycelium.md), and [03. Spore](spec/v1/03-spore.md) in order.
- **Publishing from your own domain:** Focus on [02. Mycelium](spec/v1/02-mycelium.md), [03. Spore](spec/v1/03-spore.md), and [06. URI](spec/v1/06-uri.md).
- **Consuming or verifying foreign spores:** Read [01. Substrate](spec/v1/01-substrate.md), [04. Taste](spec/v1/04-taste.md), [07. Algorithm Registry](spec/v1/07-algorithm-registry.md), and [08. Security Model](spec/v1/08-security.md).
- **Defining conventions:** Start with [05. Strain](spec/v1/05-strain.md).

## Document Map

### Sovereign Roots

- [01. Substrate](spec/v1/01-substrate.md) — Discovery & identity, `cmn.json`, Ed25519 key binding
- [02. Mycelium](spec/v1/02-mycelium.md) — Domain manifest, spore inventory, nutrient methods
- [03. Spore](spec/v1/03-spore.md) — Package format, two-layer signatures, Merkle tree hashing, bonds

### Taste & Trust

- [04. Taste](spec/v1/04-taste.md) — Safety evaluation, 5-level verdict scale, gate rules
- [08. Security Model](spec/v1/08-security.md) — Threat model, key trust, revocation, replay/rollback analysis

### Shared Strains

- [05. Strain](spec/v1/05-strain.md) — Reference convention pattern for shared conventions built on top of CMN

### Protocol References

- [06. URI](spec/v1/06-uri.md) — `cmn://` addressing scheme
- [07. Algorithm Registry](spec/v1/07-algorithm-registry.md) — Canonical identifiers for hashes, signatures, tree algorithms

## Supporting references

- [Glossary](spec/v1/glossary.md) — Protocol vocabulary
- [End-to-End Example](spec/v1/example.md) — Full walkthrough: publish → index → spawn → re-release

## Release bundles

- Prose specification bundle: [`spec/v1/`](spec/v1/)
- JSON Schema bundle: [`schemas/v1/`](schemas/v1/) — [cmn.json](schemas/v1/cmn.json), [mycelium.json](schemas/v1/mycelium.json), [spore-core.json](schemas/v1/spore-core.json), [spore.json](schemas/v1/spore.json), [taste.json](schemas/v1/taste.json)
- Conformance bundle: [`conformance/v1/`](conformance/v1/) — substrate, mycelium, spore, taste, strain, uri, algorithm_registry, signature, capsule, key_rotation, blob_tree_blake3_nfc, bond_traversal, taste_gating

## Versioning

Each release bundle shares the same major version segment so prose, schemas, and conformance vectors can be pinned together. See [01. Substrate §6](spec/v1/01-substrate.md#6-protocol-versioning) for protocol version negotiation and migration rules, and [07. Algorithm Registry §4](spec/v1/07-algorithm-registry.md#4-registry-evolution) for algorithm lifecycle.

## License

CC0-1.0 (Public Domain)
