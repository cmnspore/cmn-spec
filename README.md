# CMN Protocol Specification

**Code Mycelial Network** — a sovereign-first protocol for code distribution where domains publish signed, hash-verified packages without central registries.

## Specification

| Document | |
|----------|---|
| [Overview](spec/overview.md) | Reading paths by role, document map, versioning |
| [01. Substrate](spec/01-substrate.md) | Discovery & identity — `cmn.json`, Ed25519 key binding |
| [02. Mycelium](spec/02-mycelium.md) | Domain manifest — spore inventory, nutrient methods |
| [03. Spore](spec/03-spore.md) | Package format — two-layer signatures, Merkle tree hashing, bonds |
| [04. Taste](spec/04-taste.md) | Safety evaluation — 5-level verdict scale, gate rules |
| [05. Strain](spec/05-strain.md) | Conventions & conformance — composable interoperability contracts |
| [06. URI](spec/06-uri.md) | `cmn://` addressing scheme |
| [07. Algorithm Registry](spec/07-algorithm-registry.md) | Canonical identifiers for hashes, signatures, tree algorithms |
| [Glossary](spec/glossary.md) | Protocol vocabulary |
| [End-to-End Example](spec/example.md) | Full walkthrough: publish → index → spawn → re-release |

## Schemas

JSON Schema definitions in [`schemas/`](schemas/): [cmn.json](schemas/cmn.json), [mycelium.json](schemas/mycelium.json), [spore-core.json](schemas/spore-core.json), [spore.json](schemas/spore.json), [taste.json](schemas/taste.json).

## Conformance vectors

Machine-readable test vectors in [`conformance/v1/`](conformance/v1/) — merkle, signature, uri, capsule, taste gating, key rotation, bond traversal.

## License

CC0-1.0 (Public Domain)
