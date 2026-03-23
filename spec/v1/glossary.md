# Glossary

Core terms used across the CMN Protocol Specification, alphabetically ordered.

## Absorb

Merge code from another [Spore](#spore) into your working copy. Creates an `absorbed_from` [bond](./03-spore.md#2-4-bond-types).

## Bond

Fetch bonded spores referenced in `spore.core.json`, making them locally available. Each bond goes through the [Taste](#taste) gate before being fetched. Excludes `spawned_from` (handled by [Grow](#grow)) and `absorbed_from` (historical — merge already done).

## Capsule

The signed container within `spore.json` or `mycelium.json`. Holds [Core](#core), signatures, URI, and distribution info. The [Capsule Signature](#capsule-signature) covers the entire capsule.

## Capsule Signature

Ed25519 signature over the entire [Capsule](#capsule) object (JCS-canonical). Validates distribution info and URI. Replicate hosts re-sign with their own key. See [03-spore §4.4](./03-spore.md#4-4-capsule-signature).

## Core

The immutable metadata object inside a [Capsule](#capsule). For [Spores](#spore): name, domain, synopsis, intent, mutations, license, bonds, tree. For [Mycelium](#mycelium): name, domain, spore inventory. Protected by [Core Signature](#core-signature).

## Core Signature

Ed25519 signature over the [Core](#core) object (JCS-canonical). Protects immutable metadata — replicate hosts cannot alter core without breaking this signature. See [03-spore §4.2](./03-spore.md#4-2-core-signature).

## Domain

The domain name serving as the root of trust and identity for a publisher. Each domain is a sovereign node with its own Ed25519 keypair published via `cmn.json`. See [01-substrate](./01-substrate.md).

## Grow

Sync a spawned working copy with its upstream `spawned_from` source. Commonly implemented for Git-backed spores.

## Hatch

Prepare a [Spore](#spore) draft for release by creating or updating `spore.core.json`.

## JCS

JSON Canonicalization Scheme ([RFC 8785](https://datatracker.ietf.org/doc/html/rfc8785)). Deterministic JSON serialization used for all signatures and hashes. See [01-substrate §1.3](./01-substrate.md#1-3-value-formats).

## Merkle Tree

Git-like content-addressing structure using BLAKE3. Files become blobs, directories become trees. The root hash represents the full release tree content. See [03-spore §4.6](./03-spore.md#4-6-tree-hash-merkle-tree).

## Mycelium

A [Domain](#domain)'s signed inventory of all published [Spores](#spore). Versioned by `updated_at_epoch_ms` timestamp. The single source of truth for what a domain offers. See [02-mycelium](./02-mycelium.md).

## Publisher

A [Domain](#domain) owner who releases [Spores](#spore) and maintains a [Mycelium](#mycelium). Publishers form the CMN network — they serve content from their infrastructure, may send [Pulses](#pulse) to Synapse nodes, and evolve code through [Spawn](#spawn) and [Absorb](#absorb) across domains.

## Pulse

A signed notification sent to a Synapse node. Depending on the document type, it carries a complete [Spore](#spore), [Mycelium](#mycelium), or [Taste](#taste) manifest for immediate indexing, or a signed `cmn.json` domain-entry notification that triggers a live refresh from the domain. The concrete transport and interface are defined by the strains followed by the receiving Synapse node. See [05-strain §5.2](./05-strain.md).

## Release

Sign and publish a [Spore](#spore) to your [Mycelium](#mycelium). Computes content hash, signs the manifest, updates inventory, and may send a [Pulse](#pulse).

## Replicate

An exact copy of a [Spore](#spore) hosted on a different domain with the same content hash. The [Core](#core) and [Core Signature](#core-signature) remain from the original publisher; the replicate re-signs the [Capsule](#capsule) with its own key. See [03-spore §6.1](./03-spore.md#6-1-replicate-same-hash).

## Sense

Resolve a CMN URI and inspect metadata without downloading content. Often the first step in the visitor pipeline.

## Spawn

Create a working copy of a [Spore](#spore) under your own domain. Adds a `spawned_from` bond for lineage tracking. Every spawn is a first-class fork. See [03-spore §6.2](./03-spore.md#6-2-spawn-different-hash).

## Spore

An immutable code capsule. Content-addressed by BLAKE3 hash, signed by the publisher's Ed25519 key. Once released, the content never changes. See [03-spore](./03-spore.md).

## Substrate

The identity and discovery layer. Ed25519 keys are published via `cmn.json`, binding identity to domains. The foundation everything else builds on. See [01-substrate](./01-substrate.md).

## Strain

A [Spore](#spore) that defines an enforceable convention. Other spores declare `follows` bonds to adopt the convention. Strains themselves declare explicit `extends` bonds to their parent strain family members. Both `follows` and `extends` are non-transitive in the reference strain pattern. See [05-strain](./05-strain.md).

## Synapse

Shorthand in this spec for the optional indexer/discovery role in CMN. Synapse nodes receive [Pulses](#pulse), crawl domains, track lineage, and serve discovery queries. Self-hostable, optional, read-only — no instance is required or privileged. See [05-strain §5.2–5.6](./05-strain.md).

## Taste

The safety evaluation step before using a spore or service. The visitor analyzes the code (reading source, comparing with parent, checking intent consistency), then records a verdict on a 5-level taste scale: `sweet` (used it, great, endorsed), `fresh` (reviewed thoroughly, no issues), `safe` (quick scan, nothing obvious), `rotten` (unusable — broken, won't compile), or `toxic` (confirmed dangerous — malware, data theft, backdoor). Processing rules: `toxic` blocks, `rotten` warns then proceeds, `safe`/`fresh`/`sweet` proceed. Taste results are cached locally and checked by [Spawn](#spawn), [Grow](#grow), [Absorb](#absorb), and [Bond](#bond) before proceeding. Visitors with domains can sign and share taste reports through optional discovery services for others to reference. See [04-taste](./04-taste.md).

## URI

The `cmn://` addressing scheme. Four base forms: domain, spore, mycelium, and taste. See [06-uri](./06-uri.md).

## Visitor

Anyone who discovers, inspects, and uses spores — **no domain or keys required**. The typical visitor pipeline: search → [Sense](#sense) → [Taste](#taste) → [Spawn](#spawn) → develop. Visitors taste locally, spawn working copies, sync updates via [Grow](#grow), and merge from siblings via [Absorb](#absorb) — all without publishing infrastructure. Sharing [Taste](#taste) reports and releasing spores require a [Domain](#domain), at which point a visitor becomes a [Publisher](#publisher).

## Well-Known URI

Standard path prefix for discovery endpoints ([RFC 8615](https://datatracker.ietf.org/doc/html/rfc8615)). CMN uses `/.well-known/cmn.json` as the domain entry point, following the same convention as ACME, WebFinger, OAuth, and Nostr. Makes CMN discoverable via standard Web infrastructure. See [01-substrate §1.2.1](./01-substrate.md#1-2-1-domain-entry-point-cmn-json).
