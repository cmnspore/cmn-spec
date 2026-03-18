+++
title = "Specification"
description = "Directory of the normative CMN documents and the shortest reading paths for publishers, implementers, and indexers."
template = "directory-page.html"
[extra]
eyebrow = "Protocol Directory"
+++

Use this page as the map of the protocol itself. If you want operational docs or reference implementations, continue to [Tools](/tools/); if you want the protocol contracts, start here.

## Start with the path that matches your role

- **New to CMN:** Read [01. Substrate](./01-substrate.md), [02. Mycelium](./02-mycelium.md), and [03. Spore](./03-spore.md) in order.
- **Publishing from your own domain:** Focus on [02. Mycelium](./02-mycelium.md), [03. Spore](./03-spore.md), and [06. URI](./06-uri.md).
- **Consuming or verifying foreign spores:** Read [01. Substrate](./01-substrate.md), [04. Taste](./04-taste.md), and [07. Algorithm Registry](./07-algorithm-registry.md).
- **Defining conventions:** Start with [05. Strain](./05-strain.md).
- **Running a Synapse-compatible indexer:** Read [05. Strain](./05-strain.md) for the convention model, then the Synapse convention documents in the tools docs.

## Core documents

### [01. Substrate - Discovery & Identity](./01-substrate.md)
Domain discovery, `cmn.json`, Ed25519 key binding, and the sovereignty model.

### [02. Mycelium - Domain Manifest](./02-mycelium.md)
How a domain publishes its signed inventory of spores and related metadata.

### [03. Spore - Package Format](./03-spore.md)
The immutable package format, bonds, and content-addressed release model.

### [04. Taste - Safety Evaluation](./04-taste.md)
Verdict vocabulary, gate rules, and the subjective trust layer for foreign code.

### [05. Strain - Conventions & Conformance](./05-strain.md)
How interoperable conventions are declared, composed, and checked.

### [06. URI - Addressing Scheme](./06-uri.md)
The `cmn://` address format for domains, spores, and related resources.

### [07. Algorithm Registry](./07-algorithm-registry.md)
Canonical identifiers for hashes, signatures, key types, and tree algorithms.

## Supporting references

### [Glossary](./glossary.md)
Definitions for the protocol vocabulary used throughout the spec.

### [End-to-End Example](./example.md)
Walkthrough of publishing, indexing, discovering, spawning, and re-releasing a spore.

## Versioning

The protocol version lives in the `$schema` URL path, for example `https://cmn.dev/schemas/v1/spore.json`.

- **Major version changes** (`v1` to `v2`) mean a compatibility break.
- **Clarifications and backward-compatible optional fields** stay within the same version.

All CMN schema documents for a given release share the same version segment.

### Protocol Version Negotiation

Domains MAY advertise supported protocol versions in `cmn.json`:

```json
{
  "protocol_versions": ["v1"],
  "capsules": [...]
}
```

Consumers SHOULD use the highest mutually-supported version. If `protocol_versions` is absent, consumers MUST assume `["v1"]`.

### Migration Rules

1. **Major version** (`v1` → `v2`): Breaking changes. Consumers MUST support both versions during a transition period of at least 12 months. Domains SHOULD publish under both versions concurrently.
2. **Minor additions**: New optional fields within the same major version. Consumers MUST ignore unknown fields. Producers MUST NOT require consumers to understand new optional fields for correct operation.
3. **Deprecation**: Fields marked deprecated in one major version MAY be removed in the next. Implementations SHOULD log warnings when deprecated fields are encountered.

### Algorithm Migration

When new algorithms are added to the [Algorithm Registry](./07-algorithm-registry.md):

1. New algorithm is added with status **active**.
2. Old algorithm status changes to **deprecated** — consumers SHOULD warn on use.
3. After a transition period, old algorithm status changes to **retired** — consumers MAY reject content using retired algorithms.

## License

This specification is released under CC0-1.0 (Public Domain).
