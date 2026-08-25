# AGENTS.md

## Purpose and ownership

`helianthus-docs-eebus` is the canonical public documentation repository for
eeBUS in Helianthus. It owns publishable protocol-native documentation for
SHIP, SPINE, pairing/trust lifecycle, runtime behavior, raw evidence, and
operator-facing contracts.

It does not own protocol-neutral semantic models, consumer-specific behavior,
gateway implementation, Home Assistant integration, or the SHIP/SPINE
implementations. Cross-protocol contracts must name their explicit public owner.

## Workflow

1. Reconcile the target branch, local changes, linked issue, and open pull
   requests before editing.
2. Work from a scoped `issue/<number>-<slug>` branch based on the repository's
   current integration branch.
3. Keep the change within the issue acceptance criteria and add focused
   documentation validation when a new invariant needs enforcement.
4. In a standalone clone, install the hashed validator dependencies with
   `python3 -m pip install --only-binary=:all: --require-hashes -r requirements-ci.txt`,
   then run `python3 scripts/validate_repository_policy.py`,
   `python3 scripts/validate_api_surface_v1.py`, and `git diff --check`.
   These are the mandatory repository-local baseline checks.
5. Open a linked pull request that records validation results, documentation
   scope, and residual risk.
6. Obtain a fresh, exact-HEAD blocker review; resolve P0-P2 findings or record
   an independently validated by-design decision.
7. Squash merge only when applicable checks and the exact-HEAD review are
   green, then verify the remote integration branch and stop at the requested
   boundary.

`./scripts/ci_local.sh` is the additional MSP-055 cross-repository provenance
gate. It requires `MSP055_SOURCE_CHECKOUT` to identify the exact detached
`helianthus-eebusreg` source revision. Run it when changing MSP-055 frozen API
material or the gate itself; it is not a prerequisite for unrelated work in a
standalone clone. GitHub CI provisions that checkout independently.

## Evidence and privacy

- Treat [EEBUS specifications](https://www.eebus.org/specifications-media/) and other
  publishable primary sources as evidence; clearly mark hypotheses and unknowns.
- Preserve the distinction between observed native evidence, inference, and
  promoted public contract. Do not turn candidate data into a stable claim.
- Do not publish credentials, private keys, trust-store bytes, serial numbers,
  account data, private captures, household schedules, private network details,
  or device fingerprints.
- Do not reproduce restricted-source material. Link to public sources instead.
- Keep connection management distinct from connected-only SPINE topology
  browsing; a trusted but offline partner is not evidence of browseable data.

## Public references

- [Helianthus eeBUS documentation](https://github.com/Project-Helianthus/helianthus-docs-eebus)
- [EEBUS Initiative](https://www.eebus.org/)
- [EEBUS specifications](https://www.eebus.org/specifications-media/)
