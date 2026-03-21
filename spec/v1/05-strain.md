# 05. Strain - Reference Convention Pattern

A **strain** is a spore that defines an enforceable convention for other spores to follow. The term comes from mycology — spores of the same strain share fundamental characteristics.

## 1. Overview

This chapter describes a **reference pattern** for expressing shared conventions on top of CMN. Core CMN publication, discovery, replication, spawning, growth, and absorption do not require strains. Implementers MAY adopt this pattern, adapt it, or define a different convention system entirely.

In the strain pattern, a convention is packaged as a spore: it carries a `convention.md` that defines requirements, and other spores declare `follows` bonds to adopt those requirements. Within this pattern, the `follows` bond is a contract — a spore claiming to follow a strain MUST conform to every MUST-level requirement in that strain's convention.

Strains enable:

- **Discovery** — agents find services and tools by searching for spores that follow a known strain
- **Interoperability** — independent implementations conform to the same requirements
- **Enforcement** — non-conformance is reportable via [taste](04-taste.md) verdicts; indexers such as Synapse may flag or deprioritize non-conformant spores

## 2. Defining a Strain

A strain spore MUST contain:

| File | Purpose |
| :--- | :--- |
| `spore.core.json` | Standard CMN manifest with the required `follows` bonds (see §2.2 and §3) |
| `convention.md` | The convention definition. MUST clearly distinguish normative requirements, including `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY`. |

### 2.1 Requirement Levels

- **MUST** / **MUST NOT** — mandatory / prohibited. Violation is a conformance failure reportable via taste.
- **SHOULD** / **SHOULD NOT** — recommended / discouraged. Deviation is acceptable with good reason but may affect taste verdict.
- **MAY** — optional. No conformance expectation.

### 2.2 Identifying Strains

Each strain system chooses its own root strain or root lineage. The `strain` spore published by `cmn.dev` is one reference root, not a protocol-wide singleton.

Within a given strain system, the root strain follows nothing. Non-root strains in that system MUST include a `follows` bond to that system's root strain URI. This distinguishes a strain definition from an ordinary follower.

Example:

```
strain (root)     follows nothing
strain-chat       follows [root]               # strain definition
my-chat-bot       follows [strain-chat]        # follower
```

An indexer implementing the strain pattern MAY treat a spore with a direct `follows` bond to a configured root strain as a strain definition within that strain system; one without that bond is a follower.

Indexers MAY track strain lineage via `spawned_from` bonds so updated strain releases remain discoverable after the strain is revised.

## 3. Hierarchy & Composition

### 3.1 Child Strains

A child strain extends a parent strain: it satisfies all of the parent's MUST requirements and adds its own. A spore following the child MUST satisfy requirements from both.

A child strain in a given strain system MUST include `follows` bonds to both:
- that system's root strain URI
- its direct parent strain URI

```
strain (root)         follows nothing
strain-synapse        follows [root]
strain-synapse-search follows [root, strain-synapse]
```

### 3.2 Composition

Hierarchy defines how strains extend each other. Composition defines how spores and services can use them. A service follows multiple strains as independent, equal capabilities:

```
my-synapse   follows [strain-synapse-search, strain-synapse,
                      strain-service,
                      strain-account-pow, strain-account,
                      strain-payment-prepaid, strain-payment-order, strain-payment]
```

A spore MUST conform to every MUST-level requirement from every followed strain.

### 3.3 Explicit Declaration

Within the reference strain pattern, `follows` is not transitive. A spore MUST explicitly declare every non-root strain it follows, including parent strains in the hierarchy chain.

```
strain-account-pow       follows [root, strain-account]

my-service   follows [strain-account-pow]
             ✗ missing strain-account — not discoverable in strain-account searches

my-service   follows [strain-account-pow, strain-account]
             ✓ discoverable under both strains
```

Why explicit:

1. Indexers such as Synapse can index direct `follows` bonds without recursive inference. If the parent bond is missing, the spore is invisible to searches for that parent strain.
2. Consumers can read one spore's bonds and see its full interface contract without recursively resolving strain inheritance.

## 4. Conformance

### 4.1 The follows Contract

A `follows` declaration is a checkable contract within a strain system. A spore can be fully valid CMN without following any strain. But when a spore declares that it follows a strain:

1. The spore MUST conform to every MUST-level requirement in the strain's convention
2. Non-conformance is reportable via [taste](04-taste.md) — a taster finding violations may record a `rotten` (warn) or `toxic` (block) verdict
3. Indexers implementing the strain pattern, including Synapse, may flag, deprioritize, or delist spores with non-conformance reports

### 4.2 Enforcement

Conformance enforcement is distributed, not centralized:

- **Tasters** evaluate whether a spore meets its declared conventions and publish signed taste reports
- **Indexers such as Synapse** aggregate taste reports and may use them to inform search ranking
- **Visitors** decide which tasters to trust and how to interpret verdicts

If a creator needs different behavior than what a strain requires, they create their own strain rather than violating the convention they declared.

## 5. Worked Example: Service Pattern & Synapse Family

This section shows one application of the strain pattern: service conventions, and one convention family built on top of them. `strain-service`, `strain-synapse`, and their children are examples, not core CMN requirements.

### 5.1 strain-service

One simple strain. It defines what it means to publish a deployed HTTP service on the CMN network.

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

Defines one convention family, `strain-synapse`, for a Synapse-style CMN indexer and discovery service.

**Convention requires:**
- `POST /synapse/pulse` — accept signed `cmn.json` domain-entry notifications plus signed spore, mycelium, and taste manifests; verify each according to its type
- `GET /synapse/spore/:hash` — retrieve a spore by content hash, including `replicates` (mirror domains, origin excluded)
- `GET /synapse/spore/:hash/bonds` — traverse bond relationships (inbound/outbound, by relation, recursive depth)
- `GET /synapse/spore/:hash/tastes` — retrieve aggregated taste reports with verdict counts
- `GET /synapse/mycelium/:domain` — retrieve a domain's indexed mycelium with endpoints and public key
- `GET /synapse/mycelium/:domain/tastes` — retrieve aggregated taste reports for domain + current mycelium target

The pulse interface lets publishers push signed manifests, and `cmn.json` refresh notifications, to any service that follows `strain-synapse`. For spore, mycelium, and taste documents, the receiver verifies both signature layers (author key for core, host key for capsule) before storing anything. For `cmn.json`, the receiver treats the pulse as a notification and fetches the live domain entry from the publisher's domain before caching. Replicates are detected when `capsule.core.domain` differs from the URI domain.

All responses follow a consistent structure: `{code, result}` on success, `{code, error}` on failure.

The authoritative API details (request/response formats, error codes, query parameters) live in the strain-synapse convention.

### 5.3 strain-synapse-search

A child strain extending strain-synapse. Adds semantic search over indexed spores.

**Convention requires:**
- `GET /synapse/search` — full-text semantic search with filters (domain, license, bonds) and cursor-based pagination

Search results include relevance scores and aggregated taste verdict counts. The `bonds` filter enables convention-aware discovery — find all spores that follow a specific strain, or all forks of a specific spore.

Follows: `[root, strain-synapse]`

### 5.4 strain-synapse-nostr

A sibling child strain at the same level as search. Adds Nostr relay integration for real-time event propagation.

**Convention requires:**
- `GET /synapse/nostr` (WebSocket) — a NIP-01 Nostr relay serving CMN events (kind 30078, NIP-78)
- Pulse forwarding to external Nostr relays
- Subscription to external relays for cross-instance synchronization

CMN events on Nostr carry the full signed capsule as content, with tags for type (`cmn-spore`, `cmn-mycelium`, `cmn-taste`), domain, URI, and hash. Events received via Nostr undergo the same verification as HTTP pulses.

**Recommended for inter-Synapse synchronization.** Nostr's pub/sub model allows Synapse nodes following `strain-synapse` to synchronize without establishing pairwise connections — all instances publish to and subscribe from shared relays. Operators that do not follow `strain-synapse-nostr` MAY fall back to HTTP polling peer Synapse nodes via `GET /synapse/mycelium/:domain`.

Follows: `[root, strain-synapse]`

### 5.5 Hierarchy

```
strain (root)                   follows nothing
├── strain-service              follows [root]
│     Convention: service.json + GET /health
│
├── strain-synapse              follows [root]
│     Convention: pulse + spore/mycelium/taste query endpoints
│     │
│     ├── strain-synapse-search follows [root, strain-synapse]
│     │     Convention: GET /synapse/search
│     │
│     └── strain-synapse-nostr  follows [root, strain-synapse]
│           Convention: GET /synapse/nostr (WebSocket)
│
├── strain-chat                 follows [root]
│     Convention: chat parent (child strains define protocols)
│     │
│     └── strain-chat-llm      follows [root, strain-chat]
│           Convention: POST /chat/llm
│
├── strain-account              follows [root]
│     Convention: POST /account, GET /account, Bearer auth
│     │
│     ├── strain-account-pow    follows [root, strain-account]
│     ├── strain-account-domain follows [root, strain-account]
│     └── strain-account-invite follows [root, strain-account]
│
└── strain-payment              follows [root]
      Convention: payment parent (child strains define protocols)
      │
      ├── strain-payment-order    follows [root, strain-payment]
      └── strain-payment-prepaid follows [root, strain-payment, strain-payment-order, strain-account]
```

This is an example hierarchy, not a protocol-wide taxonomy. Each node in the hierarchy is an independently releasable spore. Strains at the same level are independent — strain-service, strain-synapse, strain-account, and strain-payment have no parent–child relationship between them. A service composes them flat by following whichever strains it needs. See §5.6.

### 5.6 Synapse as an Open Service

A Synapse implementation is one example of a convention-driven open service. The base convention defines the minimum: accept pulses, verify signatures, serve queries. Everything beyond that is the operator's choice — expressed through strain composition.

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

Anti-spam, rate limiting, domain allowlists, trust-graph-based admission — these are all operator policies. Core CMN does not prescribe a specific strategy. Each Synapse operator decides its own, and declares its choices through the strains it follows.

**Discovery:** Agents inspect a Synapse node's bonds via `GET /health` to see which strains it follows. A Synapse following `strain-account-pow` tells agents: "solve a PoW challenge before submitting pulses." Agents adapt automatically — no out-of-band configuration needed.

**No privileged instance:** Different Synapse nodes serve different communities with different strain compositions. Visitors choose the Synapse that fits their needs, just as they choose which tasters to trust.
