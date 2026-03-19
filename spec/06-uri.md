# 06. URI - Addressing Scheme

The CMN URI is the **primary identifier** for all entities in the Code Mycelial Network.

## 1. URI Forms

CMN has four URI forms:

```
cmn://{domain}                 # Domain root
cmn://{domain}/mycelium/{hash} # Content-addressed mycelium (site descriptor)
cmn://{domain}/{hash}          # Content-addressed spore (code unit)
cmn://{domain}/taste/{hash}    # Content-addressed taste report (safety evaluation)
```

### 1.1 Domain URI

The domain's root identity.

```
cmn://cmn.dev
```

**Properties:**
- Identifies the domain as a CMN node
- Resolves to `cmn.json` at `https://{domain}/.well-known/cmn.json`

### 1.2 Mycelium URI

Content-addressed identifier for a domain's site descriptor.

```
cmn://{domain}/mycelium/{hash}
```

**Examples:**
```
cmn://cmn.dev/mycelium/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2
```

**Properties:**
- Hash ensures mycelium integrity
- Each update produces a new hash
- Hash stored in `cmn.json` as the `hash` field on the `type: "mycelium"` endpoint

### 1.3 Spore URI

Content-addressed identifier for code units.

```
cmn://{domain}/{hash}
```

**Examples:**
```
cmn://cmn.dev/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2
```

**Properties:**
- Hash ensures content integrity
- Different content = different hash
- Same content across mirrors = same hash

### 1.4 Taste URI

Content-addressed identifier for safety evaluation reports.

```
cmn://{domain}/taste/{hash}
```

**Examples:**
```
cmn://alice.dev/taste/b3.7kLmN2pQrS4tUvWx8yZaB3cD5eF6gH9iJ1kL2mN3o
```

**Properties:**
- Domain identifies the taster (evaluator), not the spore being evaluated
- Hash is computed from taste core + core_signature (same pattern as spore hashing)

### 1.5 Replicate Identification

Replicates use the same URI forms as ordinary spores/mycelia/tastes. A replicate is identified during verification, not by a special URI prefix:

- Parse URI domain as the **host domain**
- Read manifest `capsule.core.domain` as the **author domain**
- If `capsule.core.domain != URI domain`, the object is a replicate/mirror

This keeps URI parsing simple and keeps lineage/authorship in signed core metadata.

## 2. Hash Format

### 2.1 Syntax

```
{algorithm}.{base58_value}
```

| Algorithm | Output Size | Example |
|-----------|-------------|---------|
| `b3` (BLAKE3) | 32 bytes (~44 base58 chars) | `b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2` |

Base58 uses the alphabet `123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz` (no `0`, `O`, `I`, `l`).

### 2.2 Consistency

Hashes use dot as separator everywhere: `b3.<base58>`. This format is used consistently across URIs, JSON fields, filenames, and API paths. No conversion is needed.

## 3. URI Resolution

### 3.1 Spore Resolution

```
Input:  cmn://cmn.dev/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2
Output: https://cdn.cmn.dev/cmn/spore/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2.json
```

**Steps:**
1. Extract domain: `cmn.dev`
2. Fetch `https://cmn.dev/.well-known/cmn.json`
3. Read primary capsule `capsules[0]`
4. Get spore endpoint template: `https://cdn.cmn.dev/cmn/spore/{hash}.json`
5. Replace `{hash}` with spore hash
6. Fetch spore manifest

### 3.2 Domain Resolution

```
Input:  cmn://cmn.dev
Output: (full mycelium manifest)
```

**Steps:**
1. Extract domain: `cmn.dev`
2. Fetch `https://cmn.dev/.well-known/cmn.json`
3. Read primary capsule `capsules[0]`
4. Find `type: "mycelium"` endpoint, get its `url` template and `hash`
5. Replace `{hash}` → fetch full mycelium manifest

### 3.3 Replicate Verification

When verifying a fetched manifest:

1. Verify `capsule_signature` with the host domain key from `cmn.json`
2. Read `capsule.core.domain`
3. Verify `core_signature` with author domain key (`core.key` + trust model from [01-substrate](./01-substrate.md#1-2-4-key-trust-model), or domain confirmation fallback)
4. If author domain differs from URI domain, treat as replicate/mirror

## 4. URI Parsing

Split the URI by scheme and path:

1. Strip the `cmn://` scheme prefix
2. Split the remainder by `/` into `{domain}` and optional path
3. Validate domain (see §5)
4. Determine kind from path:
   - No path → Domain
   - `mycelium/{hash}` → Mycelium
   - `taste/{hash}` → Taste
   - `{hash}` → Spore
5. If hash is present, validate hash format (see §2)

### 4.1 Formal Grammar (ABNF)

The following ABNF (RFC 5234) defines the CMN URI syntax:

```abnf
cmn-uri       = "cmn://" domain [ "/" path ]

path          = "mycelium/" hash       ; Mycelium
              / "taste/" hash          ; Taste
              / hash                   ; Spore

domain        = label 1*("." label)
label         = ld-char [ *61(ld-char / "-") ld-char ]
ld-char       = %x30-39 / %x61-7A     ; 0-9 / a-z

hash          = algorithm "." base58-value
algorithm     = 1*ld-char              ; lowercase alphanumeric
base58-value  = 1*BASE58CHAR
BASE58CHAR    = %x31-39               ; 1-9
              / %x41-48               ; A-H
              / %x4A-4E               ; J-N
              / %x50-5A               ; P-Z
              / %x61-6B               ; a-k
              / %x6D-7A               ; m-z
```

**Length constraints** (not expressible in ABNF):
- Each `label` MUST be at most 63 characters
- Total `domain` length MUST be at most 253 characters
- No trailing dot after the final label

## 5. Domain Rules

### 5.1 Valid Domain Names

Domains MUST be **lowercase** and conform to RFC 1123 hostname rules:

- Each label matches `[a-z0-9]([a-z0-9-]*[a-z0-9])?`
- At least 2 labels (must contain `.`)
- Each label max 63 characters
- Total length max 253 characters
- No trailing dot

Uppercase characters are invalid — rejected as `INVALID_DOMAIN`, not normalized.

**Valid:**
```
example.com
sub.example.com
my-project.io
```

**Invalid:**
```
Example.com     (uppercase)
example.com.    (trailing dot)
-example.com    (starts with hyphen)
example         (no TLD / single label)
```

### 5.2 Subdomain Independence

Each subdomain is a separate sovereign node:

```
cmn://example.com/b3.3yMR7vZQ...       # Different from
cmn://sub.example.com/b3.3yMR7vZQ...   # These are independent
```

- No trust inheritance from parent domains
- Each subdomain has its own keys and `cmn.json`

## 6. URI Comparison

### 6.1 Equality Rules

Two URIs are equal if all components match exactly:
1. Domain matches (domains are always lowercase, see §5.1)
2. Kind matches (domain/spore/mycelium/taste)
3. Hash matches (if present)

## 7. Examples

| Entity | URI |
|--------|-----|
| Domain root | `cmn://cmn.dev` |
| Mycelium | `cmn://cmn.dev/mycelium/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2` |
| Spore | `cmn://cmn.dev/b3.3yMR7vZQ9hL2xKJdFtN8wPcB6sY1mXgU4eH5pTa2` |
| Taste report | `cmn://alice.dev/taste/b3.7kLmN2pQrS4tUvWx8yZaB3cD5eF6gH9iJ1kL2mN3o` |

## 8. Error Handling

| Error | Description |
|-------|-------------|
| `INVALID_SCHEME` | URI doesn't start with `cmn://` |
| `INVALID_DOMAIN` | Domain is not a valid FQDN |
| `INVALID_HASH` | Hash format is invalid |
