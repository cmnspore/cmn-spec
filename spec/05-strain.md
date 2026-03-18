# 05. Strain - Conventions & Conformance

A **strain** is a spore that defines an enforceable convention for other spores to follow. The term comes from mycology — spores of the same strain share fundamental characteristics.

## 1. Overview

Protocols need enforceable conventions. A strain packages a convention as a spore: it carries a `convention.md` that defines requirements, and other spores declare `follows` bonds to adopt those requirements. The `follows` bond is a contract — a spore claiming to follow a strain MUST conform to every MUST-level requirement in that strain's convention.

Strains enable:

- **Discovery** — agents find services and tools by searching for spores that follow a known strain
- **Interoperability** — independent implementations conform to the same requirements
- **Enforcement** — non-conformance is reportable via [taste](04-taste.md) verdicts; Synapse may flag or deprioritize non-conformant spores

## 2. Defining a Strain

A strain spore MUST contain:

| File | Purpose |
| :--- | :--- |
| `spore.core.json` | Standard CMN manifest with the required `follows` bonds (see §2.2 and §3) |
| `convention.md` | The convention definition. MUST clearly distinguish MUST, SHOULD, and MAY requirements. |

### 2.1 Requirement Levels

- **MUST** — mandatory. Violation is a conformance failure reportable via taste.
- **SHOULD** — recommended. Omission is acceptable with good reason but may affect taste verdict.
- **MAY** — optional. No conformance expectation.

### 2.2 Identifying Strains

The "root strain" is a **lineage**, not a single fixed URI. Because spores are content-addressed, every root-strain update gets a new URI and links backward via `spawned_from`.

Each Synapse/visitor chooses a policy for which root lineage to accept (for example: one or more configured seed root URIs, plus their `spawned_from` descendants).

A spore is treated as a **strain definition** when it declares `follows` to at least one URI accepted as part of the root lineage by that verifier policy. Without such a bond, the spore is treated as a follower.

This distinguishes strain definitions from ordinary followers:

```
strain-root-v3    follows [strain-root-v2]      # still root lineage
strain-chat       follows [strain-root-v3]      # IS a strain (defines a convention)
my-chat-bot       follows [strain-chat]         # follower (implements a convention)
```

When Synapse returns search results, a spore that follows an accepted root-lineage URI is a strain definition; one that does not is a follower.

Synapse tracks strain lineage via `spawned_from` bonds — spores following an older root-lineage URI are still discoverable after root updates.

## 3. Hierarchy & Composition

### 3.1 Child Strains

A child strain extends a parent strain: it satisfies all of the parent's MUST requirements and adds its own. A spore following the child MUST satisfy requirements from both.

A child strain MUST `follows` both:
- at least one accepted root-lineage URI
- its direct parent strain URI

```
strain (root lineage)
strain-synapse        follows [root-lineage]
strain-synapse-search follows [root-lineage, strain-synapse]
```

### 3.2 Composition

Hierarchy defines how strains extend each other. Composition defines how services use them. A service follows multiple strains as independent, equal capabilities:

```
my-synapse   follows [strain-synapse-search, strain-synapse,
                      strain-service,
                      strain-account-pow, strain-account,
                      strain-payment-prepaid, strain-payment-order, strain-payment]
```

A spore MUST conform to every MUST-level requirement from every followed strain.

### 3.3 Explicit Declaration

`follows` is not transitive. A spore MUST explicitly declare every strain it follows — including all parent strains in the hierarchy chain.

```
strain-account-pow       follows [root-lineage, strain-account]

my-service   follows [strain-account-pow]
             ✗ missing strain-account — will not appear in strain-account searches

my-service   follows [strain-account-pow, strain-account]
             ✓ correct — discoverable under both strains
```

**Why explicit:**

1. **Simple bond index.** Synapse uses a flat bond index — searching for `strain-account` followers returns spores with a direct `follows` bond to `strain-account`. If the bond is missing, the spore is invisible to that search. Implicit inheritance would require Synapse to maintain and traverse a strain hierarchy tree on every query, adding complexity to every indexer implementation.

2. **One-level readability.** A consumer reads a spore's bonds once and sees every strain the service implements — no recursive resolution needed. The full list of strains is the complete interface contract, readable in a single query.

In practice, agents search by business strain (`strain-synapse`, `strain-chat`) to find services, then inspect `GET /health` to discover which account, payment, and other capability strains the service supports. Parent strains rarely drive the initial search — but they MUST be declared so the bond index stays correct and complete.

## 4. Conformance

### 4.1 The follows Contract

A `follows` declaration is a checkable contract. When a spore declares that it follows a strain:

1. The spore MUST conform to every MUST-level requirement in the strain's convention
2. Non-conformance is reportable via [taste](04-taste.md) — a taster finding violations may record a `rotten` (warn) or `toxic` (block) verdict
3. Synapse may flag, deprioritize, or delist spores with non-conformance reports

### 4.2 Enforcement

Conformance enforcement is distributed, not centralized:

- **Tasters** evaluate whether a spore meets its declared conventions and publish signed taste reports
- **Synapse** aggregates taste reports and may use them to inform search ranking
- **Visitors** decide which tasters to trust and how to interpret verdicts

If a creator needs different behavior than what a strain requires, they create their own strain rather than violating the convention they declared.

## 5. Worked Example: Service & Synapse

This section traces the strain hierarchy from a simple service convention through the full Synapse indexer, showing how each layer extends the previous one.

### 5.1 strain-service

The simplest strain. It defines what it means to be a deployed HTTP service on the CMN network.

**Convention requires:**
- A `service.json` file declaring the service's base URLs
- A `GET /health` endpoint returning the service's bonds (so agents can verify which conventions the service follows)

**How it works:**

A spore declares `follows: strain-service` and includes `service.json`:

```json
{
  "urls": ["https://api.example.com/my-service"]
}
```

Agents discover services by searching for spores that follow strain-service. The health endpoint returns the service's bonds at build time — agents compare bond hashes against expected strain URIs to detect version mismatches.

### 5.2 strain-synapse

Defines the Synapse indexer convention — what it means to be a CMN indexer and discovery node.

**Convention requires:**
- `POST /synapse/pulse` — ingest signed spore, mycelium, and taste manifests with two-layer signature verification
- `GET /synapse/spore/:hash` — retrieve a spore by content hash, including `replicates` (mirror domains, origin excluded)
- `GET /synapse/spore/:hash/bonds` — traverse bond relationships (inbound/outbound, by relation, recursive depth)
- `GET /synapse/spore/:hash/tastes` — retrieve aggregated taste reports with verdict counts
- `GET /synapse/mycelium/:domain` — retrieve a domain's indexed mycelium with endpoints and public key
- `GET /synapse/mycelium/:domain/tastes` — retrieve aggregated taste reports for domain + current mycelium target

The pulse protocol is the core innovation: publishers push signed manifests to any Synapse instance for immediate indexing. Synapse verifies both signature layers (author key for core, host key for capsule) before storing anything. Replicates are detected when `capsule.core.domain` differs from the URI domain.

All responses follow a consistent structure: `{code, result}` on success, `{code, error}` on failure.

The authoritative API details (request/response formats, error codes, query parameters) live in the strain-synapse convention.

### 5.3 strain-synapse-search

A child strain extending strain-synapse. Adds semantic search over indexed spores.

**Convention requires:**
- `GET /synapse/search` — full-text semantic search with filters (domain, license, bonds) and cursor-based pagination

Search results include relevance scores and aggregated taste verdict counts. The `bonds` filter enables convention-aware discovery — find all spores that follow a specific strain, or all forks of a specific spore.

Follows: `[root-lineage, strain-synapse]`

### 5.4 strain-synapse-nostr

A sibling child strain at the same level as search. Adds Nostr relay integration for real-time event propagation.

**Convention requires:**
- `GET /synapse/nostr` (WebSocket) — a NIP-01 Nostr relay serving CMN events (kind 30078, NIP-78)
- Pulse forwarding to external Nostr relays
- Subscription to external relays for cross-instance synchronization

CMN events on Nostr carry the full signed capsule as content, with tags for type (`cmn-spore`, `cmn-mycelium`, `cmn-taste`), domain, URI, and hash. Events received via Nostr undergo the same verification as HTTP pulses.

**Recommended for inter-Synapse synchronization.** Nostr's pub/sub model allows Synapse instances to synchronize without establishing pairwise connections — all instances publish to and subscribe from shared relays. Synapse operators that do not follow `strain-synapse-nostr` MAY fall back to HTTP polling other Synapse instances via `GET /synapse/mycelium/:domain`.

Follows: `[root-lineage, strain-synapse]`

### 5.5 Hierarchy

```
strain (root lineage)
├── strain-service              follows [root-lineage]
│     Convention: service.json + GET /health
│
├── strain-synapse              follows [root-lineage]
│     Convention: pulse + spore/mycelium/taste query endpoints
│     │
│     ├── strain-synapse-search follows [root-lineage, strain-synapse]
│     │     Convention: GET /synapse/search
│     │
│     └── strain-synapse-nostr  follows [root-lineage, strain-synapse]
│           Convention: GET /synapse/nostr (WebSocket)
│
├── strain-chat                 follows [root-lineage]
│     Convention: chat parent (child strains define protocols)
│     │
│     └── strain-chat-llm      follows [root-lineage, strain-chat]
│           Convention: POST /chat/llm
│
├── strain-account              follows [root-lineage]
│     Convention: POST /account, GET /account, Bearer auth
│     │
│     ├── strain-account-pow    follows [root-lineage, strain-account]
│     ├── strain-account-domain follows [root-lineage, strain-account]
│     └── strain-account-invite follows [root-lineage, strain-account]
│
└── strain-payment              follows [root-lineage]
      Convention: payment parent (child strains define protocols)
      │
      ├── strain-payment-order    follows [root-lineage, strain-payment]
      └── strain-payment-prepaid follows [root-lineage, strain-payment, strain-payment-order, strain-account]
```

Each node in the hierarchy is an independently releasable spore. Strains at the same level are independent — strain-service, strain-synapse, strain-account, and strain-payment have no parent–child relationship between them. A service composes them flat by following whichever strains it needs. See §5.6.

### 5.6 Synapse as an Open Service

Synapse is an open, self-governing service. The base convention (strain-synapse) defines the minimum: accept pulses, verify signatures, serve queries. Everything beyond that is the operator's choice — expressed through strain composition.

An operator composes capabilities by following multiple strains. Each strain is independent, and all parent strains MUST be declared explicitly:

```
my-synapse   follows [strain-synapse-search, strain-synapse,
                      strain-service,
                      strain-account-pow, strain-account,
                      strain-payment-prepaid, strain-payment-order, strain-payment]
```

This declares: "I am a Synapse with search, PoW registration, and prepaid billing."

**Examples:**

- A minimal open Synapse follows `[strain-synapse, strain-service]` — accepts all pulses, no registration, no payment.
- A curated Synapse follows `[strain-synapse-search, strain-synapse, strain-service, strain-account-domain, strain-account]` — requires domain-verified registration, offers search.
- A commercial Synapse follows `[strain-synapse-search, strain-synapse, strain-service, strain-account-pow, strain-account, strain-payment-prepaid, strain-payment-order, strain-payment]` — PoW to register, prepaid credits for search queries.

Anti-spam, rate limiting, domain allowlists, trust-graph-based admission — these are all operator policies. The protocol does not prescribe a specific strategy. Each Synapse decides its own, and declares its choices through the strains it follows.

**Discovery:** Agents inspect a Synapse's bonds via `GET /health` to see which strains it follows. A Synapse following `strain-account-pow` tells agents: "solve a PoW challenge before submitting pulses." Agents adapt automatically — no out-of-band configuration needed.

**No privileged instance:** Different Synapse instances serve different communities with different strain compositions. Visitors choose the Synapse that fits their needs, just as they choose which tasters to trust.
