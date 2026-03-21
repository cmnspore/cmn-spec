# Specification

## Normative Language

The key words `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` in this specification are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in all capitals.

## Start with the path that matches your role

- **New to CMN:** Read [01. Substrate](./01-substrate.md), [02. Mycelium](./02-mycelium.md), and [03. Spore](./03-spore.md) in order.
- **Publishing from your own domain:** Focus on [02. Mycelium](./02-mycelium.md), [03. Spore](./03-spore.md), and [06. URI](./06-uri.md).
- **Consuming or verifying foreign spores:** Read [01. Substrate](./01-substrate.md), [04. Taste](./04-taste.md), and [07. Algorithm Registry](./07-algorithm-registry.md).
- **Defining conventions:** Start with [05. Strain](./05-strain.md).

## Document Map

### Sovereign Roots

- [01. Substrate](./01-substrate.md) — Discovery & identity, `cmn.json`, Ed25519 key binding
- [02. Mycelium](./02-mycelium.md) — Domain manifest, spore inventory, nutrient methods
- [03. Spore](./03-spore.md) — Package format, bonds, content-addressed releases

### Taste & Trust

- [04. Taste](./04-taste.md) — Safety evaluation, verdict scale, gate rules

### Shared Strains

- [05. Strain](./05-strain.md) — Reference convention pattern for shared conventions on CMN

### Protocol References

- [06. URI](./06-uri.md) — `cmn://` addressing scheme
- [07. Algorithm Registry](./07-algorithm-registry.md) — Canonical identifiers for hashes, signatures, tree algorithms

## Supporting references

- [Glossary](./glossary.md) — Protocol vocabulary
- [End-to-End Example](./example.md) — Full walkthrough: publish, index, spawn, re-release

## Versioning

This repository publishes matching release bundles under `spec/v1/`, `schemas/v1/`, and `conformance/v1/` so prose, schemas, and vectors can be pinned together.

See [01. Substrate §6](./01-substrate.md#6-protocol-versioning) for protocol version negotiation and migration rules, and [07. Algorithm Registry §4](./07-algorithm-registry.md#4-registry-evolution) for algorithm lifecycle.

## License

CC0-1.0 (Public Domain)
