# 05. Strain - Reference Convention Pattern

A **strain** is a spore that defines an enforceable convention for other spores to follow.

## 1. Overview

This chapter describes a **reference pattern** for expressing shared conventions on top of CMN. Core CMN does not require strains — implementers MAY adopt, adapt, or replace this pattern entirely.

A convention is packaged as a spore carrying a `convention.md`. Two bond types connect strains and their users:

- **`follows`** — "I conform to this convention" (contract between service and strain)
- **`extends`** — "I belong to this strain family" (hierarchy between strain definitions)

Both are non-transitive by design.

## 2. Design Rationale

### 2.1 Why Conventions as Spores

Conventions could be defined as external documents, but packaging them as spores brings immediate benefits: they get content-addressed URIs, cryptographic signatures, version history via `spawned_from`, and discovery through the same infrastructure as any other code. A strain is not special infrastructure — it is just a spore whose content happens to define requirements for other spores.

### 2.2 Why Non-Transitive

Transitive bonds would let tools infer `follows strain-account` from `follows strain-account-pow`. This seems convenient but creates hidden coupling: renaming or restructuring a strain hierarchy would silently change what a service appears to implement. Explicit declaration means each spore's bond list is self-contained — no recursive resolution needed, no surprises when a parent strain changes.

### 2.3 Why Non-Recursive Conformance

A taster checking `follows strain-synapse-search` only evaluates `strain-synapse-search`'s convention, never its parent `strain-synapse`. If the service also needs to conform to the parent, it must declare `follows strain-synapse` separately. This avoids cascading validation and keeps each strain's conformance scope clear.

## 3. Structure

A strain spore MUST contain:

| File | Purpose |
| :--- | :--- |
| `spore.core.json` | Standard CMN manifest with `extends` bonds to parent strains |
| `convention.md` | Convention definition using RFC 2119 requirement levels |

Each strain system chooses its own root. The root has no `extends` bonds; non-root strains MUST include an `extends` bond to the root. A child strain MUST include `extends` bonds to both the root and its direct parent:

```
strain (root)         extends nothing
strain-synapse        extends [root]
strain-synapse-search extends [root, strain-synapse]
```

Conformance: `follows` is a checkable contract — non-conformance is reportable via [taste](04-taste.md). `extends` is a family edge — it declares hierarchy but does not imply `follows` for consumers.

## 4. Worked Example: Synapse

Synapse is CMN's optional indexing and discovery layer — it adds cross-domain search, aggregated taste, and bond traversal that no single domain can provide alone. It is not a central registry; anyone can deploy their own instance.

The key insight is that the entire Synapse API is defined as strains, not as a monolithic spec. This means:

**Modular by default.** The base `strain-synapse` defines the minimum (accept pulses, serve queries). Search, Nostr sync, account registration, payment — each is a separate strain an operator opts into. There is no "full Synapse" — only the combination each operator chooses.

**Self-describing.** Agents read a Synapse node's `follows` bonds to discover its capabilities. A node following `strain-account-pow` tells agents: solve a PoW challenge before submitting. No out-of-band documentation needed.

**Independently deployable.** Anyone can implement `strain-synapse` and deploy a compatible node. The convention.md is the contract — not the reference implementation.

```
# Open — no registration, no payment
my-synapse  follows [strain-synapse, strain-service]

# Curated — domain-verified registration, search
my-synapse  follows [strain-synapse-search, strain-synapse, strain-service,
                     strain-account-domain, strain-account]

# Commercial — PoW registration, prepaid billing, search
my-synapse  follows [strain-synapse-search, strain-synapse, strain-service,
                     strain-account-pow, strain-account,
                     strain-payment-prepaid, strain-payment-order]
```

## 5. Extending and Creating Strains

Strains are ordinary spores. You can:

- **Extend** an existing strain — publish a child that `extends` it with your own `convention.md`. For example, add a new authentication method by extending `strain-account`. No permission from the parent strain's author needed.
- **Modify** — `spawn` an existing strain, change its `convention.md`, and release as a new strain under your domain. The `spawned_from` bond preserves lineage.
- **Create from scratch** — publish a root strain (no `extends` bonds) and build your own family on top of it.

Because `follows` bonds are indexed, strains also serve as a discovery mechanism. An agent searching for all Synapse nodes queries for spores that `follows strain-synapse` — every compatible instance appears, regardless of who deployed it or where it runs.

There is no global registry of strains, no approval process, and no single root. Different communities can define overlapping or competing conventions — consumers choose which to follow.
