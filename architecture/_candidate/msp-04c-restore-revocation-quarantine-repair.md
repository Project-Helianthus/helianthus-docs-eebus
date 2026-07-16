---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-04c-restore-revocation-quarantine-repair.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "An accepted architecture review or conformance result demonstrates that MSP-04C can silently restore trust, reach a concrete network dial before durable attempt reservation and coordinator permit, bypass production-composed persistent quarantine, accept a stale attempt callback, report revocation before authoritative runtime withdrawal, lose a tombstone, rely on an unreviewed dependency fork, or expose a public mutation or identity surface under this contract."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate MSP-04C-R2 Restore, Revocation, Quarantine, Repair, And Pre-Dial Composition Contract

## Status And Authority

This is the pre-implementation candidate contract for MSP-04C. It constrains
the [companion source issue][code-issue] but does not claim that restore,
revocation, quarantine, or repair is implemented or supported. It follows the
[MSP-04A store contract][store-contract], the [MSP-04B trust contract][trust-contract],
the locked [MSP-04C execution-plan row][plan-row], and exact
[EEBUS-G10/G11/G16 gate definitions][gate-contract]. The active cruise run is
tracked by [meta issue 58][meta-issue].

The MSP-04C-R correction is tracked by [docs issue 26][corrective-docs-issue]
and [corrective source issue 30][corrective-source-issue]. The earlier MSP-04C
source merge is a predecessor, not evidence that the production callback on
the SHIP path, registration, reconnect, and revocation withdrawal lifecycle
satisfies this corrected contract.

MSP-04C-R2 is tracked by [docs issue 28][r2-docs-issue]. R2 adds the
dependency-level pre-dial authority required to make the coordinator's permit
the immediate predecessor of every concrete websocket dial. It does not claim
that any of the three dependency forks or the eebusreg adoption stage exists,
is tagged, is merged, or is supported.

The four-stage dependency-closure amendment is tracked by
[docs issue 30][r2-closure-docs-issue].

These are project security and ownership decisions, not protocol claims.
Stable API, navigation, search, sitemap, versioned-bundle, and release-bundle
outputs intentionally omit this candidate.

## Corrective Source Evidence Status

All source-controlled fields below remain pending until the corrective source
merges from [source issue 30](https://github.com/Project-Helianthus/helianthus-eebusreg/issues/30).
This candidate does not predict a source head, CI run, artifact identity, or
closure verdict.

| Evidence field | Candidate value | Required closure evidence |
| --- | --- | --- |
| `corrective_source_head_sha` | `pending` | Full reviewed 40-character source head that implements this correction. |
| `corrective_source_merge_sha` | `pending` | Full 40-character squash merge on source `main`. |
| `corrective_source_exact_head_ci_run` | `pending` | Successful exact-head source CI run identifier. |
| `corrective_source_post_merge_ci_run` | `pending` | Successful post-merge source `main` CI run identifier. |
| `eebus_g10_integration_artifact` | `pending` | Immutable redacted artifact from executed production-composed G10 cases. |
| `eebus_g11_integration_artifact` | `pending` | Immutable redacted artifact from executed production callback, restart, retry, and terminal-quarantine cases. |
| `eebus_g16_integration_artifact` | `pending` | Immutable redacted scan artifact over the executed integration behavior and its outputs. |
| `m4_architecture_closure_verdict` | `pending` | Bounded post-merge architecture review result, `PASS` or `PASS_WITH_CARRIED_EVIDENCE`. |
| `platform_provider_attestation` | `pending_ssh_only_non_normative` | Provider-specific no-export, host-binding, and backup-exclusion attestation from an eligible platform lane. |

An existing MSP-04C merge, unit helper, or synthetic helper result does not
satisfy or replace any executed integration field. SSH-only platform
observations remain supporting, non-normative evidence. They cannot clear
`platform_provider_attestation`, claim a portable provider, or substitute for
the deterministic integration gates.

## R2 Dependency Evidence Status

Immutable upstream and published-API baseline rows are fixed below. Every
closure output remains pending until the four repository stages merge in
order: ship-go fork, spine-go fork, eebus-go fork, then eebusreg adoption. No
branch name, local checkout, callback transcript, mutable default-branch name,
or unmerged head may fill a pending field.

| Evidence field | Candidate value | Required closure evidence |
| --- | --- | --- |
| `ship_go_upstream_tag_object_sha` | `machine.baselines.ship_go.tag_object.oid` | Exact annotated `v0.6.0` tag object. |
| `ship_go_upstream_peeled_commit_sha` | `machine.baselines.ship_go.peeled_commit.commit` | Exact commit peeled from annotated `v0.6.0`; never the tag object. |
| `ship_go_upstream_tree_sha` | `machine.baselines.ship_go.tree.oid` | Exact tree of the peeled upstream commit. |
| `ship_go_upstream_license_sha256` | `machine.baselines.ship_go.license.sha256` | SHA-256 of the exact `LICENSE` blob byte stream at the peeled commit. |
| `spine_go_upstream_tag_object_sha` | `machine.baselines.spine_go.tag_object.oid` | Exact annotated `v0.7.0` tag object. |
| `spine_go_upstream_peeled_commit_sha` | `machine.baselines.spine_go.peeled_commit.commit` | Exact commit peeled from annotated `v0.7.0`; never the tag object. |
| `spine_go_upstream_tree_sha` | `machine.baselines.spine_go.tree.oid` | Exact tree of the peeled upstream commit. |
| `spine_go_upstream_license_sha256` | `machine.baselines.spine_go.license.sha256` | SHA-256 of the exact `LICENSE` blob byte stream at the peeled commit. |
| `eebus_go_upstream_tag_object_sha` | `machine.baselines.eebus_go.tag_object.oid` | Exact annotated `v0.7.0` tag object. |
| `eebus_go_upstream_peeled_commit_sha` | `machine.baselines.eebus_go.peeled_commit.commit` | Exact commit peeled from annotated `v0.7.0`; never the tag object. |
| `eebus_go_upstream_tree_sha` | `machine.baselines.eebus_go.tree.oid` | Exact tree of the peeled upstream commit. |
| `eebus_go_upstream_license_sha256` | `machine.baselines.eebus_go.license.sha256` | SHA-256 of the exact `LICENSE` blob byte stream at the peeled commit. |
| `eebusreg_public_api_baseline_source_sha` | `machine.baselines.eebusreg_public_api.source_sha` | Exact source commit named by the supported API publication predicate. |
| `eebusreg_published_api_manifest_sha256` | `machine.baselines.eebusreg_public_api.manifest.sha256` | SHA-256 of `api/eebusruntime-v1/manifest.json` in the supported publication. |
| `ship_go_fork_head_sha` | `pending` | Full reviewed 40-character fork head. |
| `ship_go_fork_merge_sha` | `pending` | Full 40-character merge on the fork default branch. |
| `ship_go_prerelease_tag` | `pending` | Reviewed immutable semver prerelease naming the merged gate revision. |
| `ship_go_prerelease_tag_object_sha` | `pending` | Full 40-character annotated prerelease tag object id. |
| `ship_go_prerelease_peeled_commit_sha` | `pending` | Full 40-character commit peeled from that prerelease tag. |
| `ship_go_license_provenance_manifest_sha256` | `pending` | Digest of the canonical license, notice, header, remote, and baseline manifest. |
| `ship_go_module_graph_sha256` | `pending` | Digest of the canonical readonly module graph at the peeled prerelease commit. |
| `ship_go_exact_head_ci_run` | `pending` | Successful exact-head fork CI run identifier. |
| `ship_go_post_merge_ci_run` | `pending` | Successful post-merge fork CI run identifier. |
| `spine_go_fork_head_sha` | `pending` | Full reviewed 40-character fork head. |
| `spine_go_fork_merge_sha` | `pending` | Full 40-character merge on the fork default branch. |
| `spine_go_prerelease_tag` | `pending` | Reviewed immutable semver prerelease naming the merged mechanical rewrite. |
| `spine_go_prerelease_tag_object_sha` | `pending` | Full 40-character annotated prerelease tag object id. |
| `spine_go_prerelease_peeled_commit_sha` | `pending` | Full 40-character commit peeled from that prerelease tag. |
| `spine_go_license_provenance_manifest_sha256` | `pending` | Digest of the canonical license, notice, header, remote, and baseline manifest. |
| `spine_go_module_graph_sha256` | `pending` | Digest of the canonical readonly module graph at the peeled prerelease commit. |
| `spine_go_exact_head_ci_run` | `pending` | Successful exact-head fork CI run identifier. |
| `spine_go_post_merge_ci_run` | `pending` | Successful post-merge fork CI run identifier. |
| `eebus_go_fork_head_sha` | `pending` | Full reviewed 40-character bridge head. |
| `eebus_go_fork_merge_sha` | `pending` | Full 40-character merge on the fork default branch. |
| `eebus_go_prerelease_tag` | `pending` | Reviewed immutable semver prerelease naming the merged bridge revision. |
| `eebus_go_prerelease_tag_object_sha` | `pending` | Full 40-character annotated prerelease tag object id. |
| `eebus_go_prerelease_peeled_commit_sha` | `pending` | Full 40-character commit peeled from that prerelease tag. |
| `eebus_go_license_provenance_manifest_sha256` | `pending` | Digest of the canonical license, notice, header, remote, and baseline manifest. |
| `eebus_go_module_graph_sha256` | `pending` | Digest of the canonical readonly module graph at the peeled prerelease commit. |
| `eebus_go_exact_head_ci_run` | `pending` | Successful exact-head bridge CI run identifier. |
| `eebus_go_post_merge_ci_run` | `pending` | Successful post-merge bridge CI run identifier. |
| `eebusreg_adoption_head_sha` | `pending` | Full reviewed 40-character eebusreg adoption head. |
| `eebusreg_adoption_merge_sha` | `pending` | Full 40-character eebusreg squash merge. |
| `eebusreg_adoption_module_graph_sha256` | `pending` | Digest of the canonical readonly module graph at the exact adoption head. |
| `eebusreg_adoption_api_manifest_sha256` | `pending` | API manifest generated from the exact adoption head. |
| `eebusreg_public_api_comparison` | `pending` | Byte-identical comparison against the fixed published API manifest hash. |
| `eebusreg_adoption_exact_head_ci_run` | `pending` | Successful exact-head eebusreg CI run identifier. |
| `eebusreg_adoption_post_merge_ci_run` | `pending` | Successful post-merge eebusreg CI run identifier. |
| `eebus_g10_predial_artifact` | `pending` | Immutable redacted G10 artifact binding durable reservation to actual dial/accept observations. |
| `eebus_g11_predial_artifact` | `pending` | Immutable redacted G11 artifact binding retry state and reservation to actual dial/accept observations. |
| `eebus_g16_predial_artifact` | `pending` | Immutable redacted G16 scan artifact over the same executed observations. |
| `m4_r2_architecture_closure_verdict` | `pending` | Post-adoption closure result, `PASS` or `PASS_WITH_CARRIED_EVIDENCE`. |
| `r2_platform_provider_attestation` | `pending_ssh_only_non_normative` | The only evidence class that may remain carried at R2 closure. |
| `upstream_neutral_proposal_evidence_pack` | `pending_nonblocking_post_M4` | Public redacted M4 evidence pack suitable for both upstreams. |
| `ship_go_upstream_discussion_url_status` | `pending_nonblocking_post_M4` | Discussion URL and positive-maintainer-feedback status required before upstream issue/PR. |
| `ship_go_upstream_issue_or_draft_pr_url_status` | `pending_nonblocking_post_M4` | Accepted issue or draft PR URL/status for the optional gate and test seam. |
| `ship_go_upstream_release_tag` | `pending_nonblocking_post_M4` | Tagged upstream release with equivalent gate behavior. |
| `eebus_go_upstream_discussion_url_status` | `pending_nonblocking_post_M4` | Discussion URL and positive-maintainer-feedback status after ship-go release. |
| `eebus_go_upstream_issue_or_draft_pr_url_status` | `pending_nonblocking_post_M4` | Accepted issue or draft PR URL/status for the dependent configuration bridge. |
| `eebus_go_upstream_release_tag` | `pending_nonblocking_post_M4` | Tagged upstream release with equivalent bridge behavior. |
| `final_repatriation_evidence` | `pending_nonblocking_post_M4` | Exact upstream tags, module graph, rerun gates, API checks, and fork archive proof. |

For each fork, the annotated prerelease tag object, peeled commit, merge SHA,
module graph, provenance digest, and CI head MUST agree. The eebusreg adoption
head MUST resolve all three reviewed prerelease peeled commits without a
`replace` directive and MUST generate an API manifest byte-identical to the
fixed published manifest. SSH-only provider observations remain non-normative
and may carry only `r2_platform_provider_attestation`; they cannot fill a fork,
adoption, pre-dial artifact, or closure field.

The `pending_nonblocking_post_M4` lifecycle rows are explicitly excluded from
the current M4 closure and MSP-045 applicable-field population. They become
mandatory only for fork repatriation and retirement.

## Normative Language And Boundary

`MUST`, `MUST NOT`, `SHOULD`, and `MAY` define MSP-04C acceptance. Names in
this page are private conformance vocabulary, not exported Go declarations or
a stable disk/admin format.

The private trust coordinator owns restore classification, trust-state
transitions, revocation, quarantine, retry policy, and repair authorization.
`internal/eebusstore` remains mechanical and policy-free: it validates a
closed internal schema, canonical bytes, bounds, generations, and durability;
it never interprets a reason, selects a repair, computes backoff, clears a
tombstone, or decides trust. Any new coordinator-owned records require an
explicit internal schema version and deterministic MSP-04A migration. The
store persists the caller's complete proposed generation atomically and
returns one existing deterministic store outcome.

A separate internal host-anchor provider owns only sealed, non-restorable
anchor bytes and deterministic durability outcomes. It has no remote identity,
pairing, trust, quarantine, or repair policy. The coordinator is the sole
writer across store, anchor, facade effects, and AF_UNIX commands.

## Dependency Fork Provenance And Release Policy

R2 uses four serialized repository stages. The forks are source dependencies,
not protocol-documentation owners, and do not move coordinator policy out of
eebusreg.

| Stage | Upstream baseline | Canonical module | Required provenance | Release rule |
| --- | --- | --- | --- | --- |
| `ship_go_fork` | `github.com/enbility/ship-go@v0.6.0^{commit}` | `github.com/Project-Helianthus/helianthus-ship-go` | `tag_object+peeled_commit+tree+license_provenance_digest` | `reviewed_semver_prerelease` |
| `spine_go_fork` | `github.com/enbility/spine-go@v0.7.0^{commit}` | `github.com/Project-Helianthus/helianthus-spine-go` | `tag_object+peeled_commit+tree+license_provenance_digest` | `reviewed_semver_prerelease` |
| `eebus_go_fork` | `github.com/enbility/eebus-go@v0.7.0^{commit}` | `github.com/Project-Helianthus/helianthus-eebus-go` | `tag_object+peeled_commit+tree+license_provenance_digest` | `reviewed_semver_prerelease` |
| `eebusreg_adoption` | `Project-Helianthus/helianthus-eebusreg@machine.baselines.eebusreg_public_api.source_sha` | `internal_bridge_only` | `exact_peeled_fork_commits+module_graph+api_manifest_comparison` | `merge_after_all_three_dependency_tags` |

Each fork preserves every upstream license file, notice, and applicable source
header. `origin` names the Project-Helianthus fork and a read-only `upstream`
remote names the source project. The fork records the exact upstream tag,
commit, and tree from which it started. Upstream synchronization uses a reviewed
merge or cherry-pick with retained provenance; published fork tags are never
retargeted, and default-branch history is never rewritten to hide divergence.

The spine-go fork divergence is mechanical only. Its module declaration uses
the canonical `github.com/Project-Helianthus/helianthus-spine-go` path and
every ship-go import points to the reviewed Project ship-go prerelease. It
changes no SPINE model, feature, semantic, wire, runtime, or logging behavior.

The ship-go fork uses reviewed prereleases in the
`v0.6.1-helianthus.<positive_integer>` line. The spine-go and eebus-go forks
each use reviewed prereleases in the
`v0.7.1-helianthus.<positive_integer>` line. A tag is created only after
exact-head CI and review, resolves to the reviewed merge content, and is
immutable. A later upstream sync receives a later prerelease and a new
provenance record.

All committed module, workspace, vendor, and release dependency graphs plus CI
commands consume the canonical fork module paths and reviewed tags directly.
Any direct or transitive return to the upstream
`github.com/enbility/ship-go`, `github.com/enbility/spine-go`, or
`github.com/enbility/eebus-go` module identity fails the R2 gate. A `replace`
directive, local override including a filesystem override, untagged
pseudo-version, or branch dependency also fails the gate. The eebus-go stage
cannot merge or tag before both reviewed ship-go and spine-go prerelease tags
exist; eebusreg adoption cannot merge before all three reviewed dependency
tags exist.

A private eebus-go adapter is insufficient because retaining an upstream
module identity beside a canonical fork creates duplicate module identities.
That split produces distinct SHIP logger singletons and distinct nominal type
universes even if structural interfaces compile, so it cannot establish one
closed runtime dependency graph.

### Committed Dependency And Control Surface Closure

The tracked-surface inventory is closed and precedes every resolved Go graph
command. The required `scripts/verify_dependency_closure.py` verifier uses
`git ls-files -z`, not the filesystem view, so ignored or generated files
cannot fill an inventory row. It emits the NUL-delimited path inventory and one
canonical JSON verdict. An empty optional path class is recorded as empty; an
unclassified tracked dependency or release-control input is a failure.

| Closure rule | Exact requirement |
| --- | --- |
| `tracked_inventory_source` | `git_ls_files_NUL_only` |
| `module_surfaces` | `all_tracked_**/go.mod+all_tracked_**/go.sum` |
| `workspace_surfaces` | `all_tracked_**/go.work+all_tracked_**/go.work.sum` |
| `vendor_surfaces` | `all_tracked_**/vendor/modules.txt` |
| `ci_surfaces` | `all_tracked_.github/workflows/**/*.yml+all_tracked_.github/workflows/**/*.yaml+all_tracked_.github/actions/**` |
| `build_release_scripts` | `all_tracked_Makefile+**/Makefile+**/*.mk+scripts/**+build/**+release/**` |
| `build_release_configs` | `all_tracked_.goreleaser.*+Dockerfile*+**/Dockerfile*+Containerfile*+**/Containerfile*+Taskfile*.yml+**/Taskfile*.yml+**/*build*.yml+**/*build*.yaml+**/*build*.json+**/*build*.toml+**/*release*.yml+**/*release*.yaml+**/*release*.json+**/*release*.toml` |
| `declared_release_surfaces` | `closure_manifest.dependency_control_inputs[]+recursive_tracked_local_references` |
| `scan_order` | `tracked_surface_closure_before_any_GOWORK_off_command` |
| `upstream_identity_policy` | `zero_enbility_ship_go+zero_enbility_spine_go+zero_enbility_eebus_go_in_tracked_and_resolved_graphs` |
| `replace_policy` | `zero_replace_in_go.mod+go.work+dependency_controls_including_canonical_module_replace` |
| `workspace_local_policy` | `zero_committed_go.work_use+zero_local_filesystem_override` |
| `fork_selection_policy` | `manifest_reviewed_immutable_tags+exact_peeled_commits+ship_v0.6.1_helianthus_positive_integer+spine_eebus_v0.7.1_helianthus_positive_integer` |
| `fork_selection_denials` | `upstream_identity+pseudo_version+branch_query+local_override+non_reviewed_fork_tag` |
| `third_party_pseudo_versions` | `unrelated_module_identities_out_of_scope` |
| `spine_divergence` | `module_path_and_ship_import_rewrite_only+zero_SPINE_model_feature_semantic_wire_runtime_logging_change` |
| `duplicate_identity` | `private_adapter_insufficient+single_SHIP_logger_singleton+single_nominal_type_universe` |

The verifier parses every tracked `go.mod` and `go.work` rather than accepting
a textual allowlist. Any `replace` directive fails, including a replace whose
left and right module identities are both canonical. A committed `go.work`
`use` directive and any module, workspace, CI, build, release, or declared
input that selects a local path fail as local overrides. `GOWORK=off` is set
only after this tracked workspace scan passes and cannot hide a committed
`go.work` or `go.work.sum`.

Every canonical fork selection in the tracked surfaces must equal the reviewed
immutable tag recorded by the closure manifest, match its required prerelease
line, and peel to the recorded reviewed commit. A branch query, branch-derived
pseudo-version, untagged pseudo-version, or any other fork tag fails. A
legitimate pseudo-version for an unrelated third-party module is outside this
identity-specific selection rule and does not fail solely for being a
pseudo-version. Vendor metadata, GitHub workflows and local actions, Makefiles,
build/release scripts and configuration, and recursively declared release
inputs receive the same identity and override checks as module files.

### Immutable Baseline And Closure Commands

The closure runner executes these commands in a detached checkout of the named
source SHA. `TAG` is the reviewed tag name, `SOURCE_SHA` is first set from the
corresponding peeled commit command, and `SCRATCH` is an empty runner-owned
ephemeral directory that is deleted after the evidence bundle is sealed.
Commands never resolve `main`, a branch, a pseudo-version, or a moving module
query. Table order is normative and fail-fast: tracked dependency/control
closure completes before any command that sets `GOWORK=off`.

| Closure field | Exact canonical command or comparison |
| --- | --- |
| `upstream_tag_object_sha` | `git rev-parse "refs/tags/$TAG^{tag}"` |
| `upstream_peeled_commit_sha` | `git rev-parse "refs/tags/$TAG^{commit}"` |
| `upstream_tree_sha` | `git rev-parse "refs/tags/$TAG^{tree}"` |
| `upstream_license_sha256` | `git cat-file blob "$SOURCE_SHA:LICENSE" > "$SCRATCH/LICENSE.bytes" && sha256sum "$SCRATCH/LICENSE.bytes"` |
| `license_provenance_manifest_sha256` | `git cat-file blob "$SOURCE_SHA:provenance/closure-manifest.json" > "$SCRATCH/provenance.json" && sha256sum "$SCRATCH/provenance.json"` |
| `prerelease_tag_object_sha` | `git rev-parse "refs/tags/$TAG^{tag}"` |
| `prerelease_peeled_commit_sha` | `git rev-parse "refs/tags/$TAG^{commit}"` |
| `tracked_dependency_control_closure` | `GOTOOLCHAIN=local python3 scripts/verify_dependency_closure.py --repo . --manifest provenance/closure-manifest.json --inventory-output "$SCRATCH/dependency-control-paths.nul" --evidence-output "$SCRATCH/dependency-control-closure.json"` |
| `module_graph_sha256` | `GOWORK=off GOTOOLCHAIN=local go list -mod=readonly -m -json all > "$SCRATCH/modules.json" && jq -S -c . "$SCRATCH/modules.json" > "$SCRATCH/modules.canonical.json" && sha256sum "$SCRATCH/modules.canonical.json"` |
| `module_identity_closure` | `GOWORK=off GOTOOLCHAIN=local GOFLAGS=-mod=readonly go list -m all > "$SCRATCH/go-list-m-all.txt" && ! grep -q 'github.com/enbility/ship-go' "$SCRATCH/go-list-m-all.txt" && ! grep -q 'github.com/enbility/spine-go' "$SCRATCH/go-list-m-all.txt" && ! grep -q 'github.com/enbility/eebus-go' "$SCRATCH/go-list-m-all.txt"` |
| `module_edge_closure` | `GOWORK=off GOTOOLCHAIN=local GOFLAGS=-mod=readonly go mod graph > "$SCRATCH/go-mod-graph.txt" && ! grep -q 'github.com/enbility/ship-go' "$SCRATCH/go-mod-graph.txt" && ! grep -q 'github.com/enbility/spine-go' "$SCRATCH/go-mod-graph.txt" && ! grep -q 'github.com/enbility/eebus-go' "$SCRATCH/go-mod-graph.txt"` |
| `eebus_go_service_dependency_closure` | `GOWORK=off GOTOOLCHAIN=local GOFLAGS=-mod=readonly go list -deps ./service > "$SCRATCH/go-list-deps-service.txt" && ! grep -q 'github.com/enbility/ship-go' "$SCRATCH/go-list-deps-service.txt" && ! grep -q 'github.com/enbility/spine-go' "$SCRATCH/go-list-deps-service.txt" && ! grep -q 'github.com/enbility/eebus-go' "$SCRATCH/go-list-deps-service.txt"` |
| `eebusreg_adoption_source_sha` | `git rev-parse HEAD` in the clean detached adoption checkout. |
| `eebusreg_adoption_api_manifest_sha256` | `GOWORK=off GOTOOLCHAIN=local go run ./internal/apisurface -output "$SCRATCH/api.json" && sha256sum "$SCRATCH/api.json"` |
| `eebusreg_public_api_comparison` | Generated digest equals `machine.baselines.eebusreg_public_api.manifest.sha256`, whose publication predicate binds `machine.baselines.eebusreg_public_api.source_sha`; byte comparison reports identical. |

After eebus-go pins the canonical forks, `go list -m all`, `go mod graph`, and
`go list -deps ./service` MUST each reject the upstream ship-go identity. The
same checks reject upstream spine-go and eebus-go identities so no transitive
edge can reintroduce a split dependency graph.

The canonical provenance manifest is closed and records the upstream remote,
upstream annotated tag object, peeled commit, tree, exact license digest,
notice inventory, and applicable source-header inventory. The closure artifact
records command versions and the exact source SHA beside every digest.

### ship-go Baseline Dial Inventory

At the fixed `v0.6.0` peeled commit, production has exactly two direct calls to
`(*websocket.Dialer).Dial`, both in `hub/hub_connections.go`: first the selected
path and then the root/no-path fallback. The migration intentionally preserves
that fallback trigger and order while routing both calls through one helper.

| Inventory item | Baseline | Required fork result |
| --- | --- | --- |
| `selected_path_call` | `hub/hub_connections.go:websocket.Dial(selected_path)` | `fresh_Prepare+fresh_AuthorizeLaunch+gatedDialContext` |
| `root_no_path_fallback_call` | `hub/hub_connections.go:websocket.Dial(root_no_path)` | `fresh_Prepare+fresh_AuthorizeLaunch+gatedDialContext` |
| `direct_websocket_Dial_calls` | `2` | `0` |
| `direct_DialContext_calls` | `0` | `1_in_gatedDialContext_only` |
| `fallback_semantics` | `selected_path_then_root_no_path_on_same_error_condition` | `preserved_exactly` |

A Go AST inventory test MUST reject every residual direct `Dial` call and every
direct `DialContext` call outside `gatedDialContext`. It MUST find exactly one
concrete `DialContext` call in that helper. Source inventory additionally
rejects aliasing or wrapper indirection that hides either selector. Every host,
IPv4, IPv6, selected-path call, and root/no-path fallback call obtains a fresh
lease and a fresh single-use permit; none reuses the failed call's handle.

### Temporary Fork Upstreaming And Retirement

All three Project-Helianthus forks are temporary downstream patch carriers, not
permanent product forks. Current M4 execution, review, merge, VR940f proof, and
closure do not depend on an upstream maintainer response, Discussion outcome,
PR schedule, or release schedule. Until repatriation, each fork maintains the
smallest reviewable divergence needed by this contract and prohibits unrelated
features, opportunistic refactors, protocol changes, and product-only APIs.

The post-M4 external sequence is closed and follows each upstream repository's
CONTRIBUTING prerequisite:

| Sequence | Required action | Entry condition | Current-M4 blocking |
| --- | --- | --- | --- |
| `1_m4_proof` | `stabilize_on_VR940f+G10_G11_G16+M4_PASS` | `current_execution` | `required` |
| `2_proposal_pack` | `publish_upstream_neutral_optional_gate_test_seam_evidence` | `M4_PASS` | `no_post_M4` |
| `3_ship_discussion` | `open_ship_go_GitHub_Discussion+obtain_positive_feedback` | `proposal_pack_ready` | `no_post_M4` |
| `4_ship_issue_or_draft_pr` | `open_accepted_issue_or_draft_PR` | `ship_positive_feedback` | `no_post_M4` |
| `5_ship_release` | `obtain_tagged_upstream_release_with_equivalent_behavior` | `ship_change_accepted_and_merged` | `no_post_M4` |
| `6_eebus_discussion` | `open_eebus_go_GitHub_Discussion+obtain_positive_feedback` | `ship_tagged_release` | `no_post_M4` |
| `7_eebus_issue_or_draft_pr` | `open_accepted_issue_or_draft_PR_for_configuration_bridge` | `eebus_positive_feedback` | `no_post_M4` |
| `8_eebus_release` | `obtain_tagged_upstream_release_with_equivalent_behavior` | `eebus_change_accepted_and_merged` | `no_post_M4` |
| `9_repatriation` | `migrate_to_github.com/enbility_modules+rerun_exit_gates+archive_forks_read_only` | `both_tagged_upstream_releases` | `no_post_M4` |

The repatriation exit gate binds both upstream annotated release tags, peeled
commits, trees, license digests, and module-graph digest. It removes all three
Project-Helianthus module paths and every `replace`, reruns G10, G11, G16,
public-API anti-leak comparison, and coexistence checks against the exact
repatriation source SHA, and requires equivalent fallback, lease, permit,
revocation, and recovery behavior. Only then are all three forks archived
read-only. They are never deleted, because their tags, review history, and
provenance are immutable evidence.

## R2 Normative Machine Contract

This closed YAML object is normative. Unknown keys, missing values, reordered
state transitions, or disagreement with the normative tables fail the R2
validator.

```yaml
schema_id: helianthus.docs.eebus.msp-04c-r2
schema_version: 1
baselines:
  ship_go:
    tag: v0.6.0
    tag_object:
      oid: c2b94943a0106e90f603a2ee0e155c1f6ac0b54b
    peeled_commit:
      commit: 760c312bf723d726d8882af3bb06650ddcd11ca9
    tree:
      oid: 958ddf185fc09dd4d3b382fc108641513412d927
    license:
      sha256: c853996135802c50b3048937e48022bc00b41ff5f56a31cebe7d686bf91f87db
  spine_go:
    tag: v0.7.0
    tag_object:
      oid: 30aeb9ac51c3212d280acd93a9afaf58bc63bd92
    peeled_commit:
      commit: 0eef075cb6e8f697355a2850344333452f5590cf
    tree:
      oid: e070b8272e357643ec855c4eab22be4dd03cb89b
    license:
      sha256: c853996135802c50b3048937e48022bc00b41ff5f56a31cebe7d686bf91f87db
  eebus_go:
    tag: v0.7.0
    tag_object:
      oid: e4677eb9c46f1cc46c2559027c35fbf39766bcfb
    peeled_commit:
      commit: 99f07ff79819b728dd2fe37472c4a26865d8076c
    tree:
      oid: fee9de0ecb34dcb7c4165922fd49fedd42d8df23
    license:
      sha256: 0871acb60d194272cd91ad02dcaf0102d8047a993f1b00973da4c9c2cba845a4
  eebusreg_public_api:
    source_sha: 59cbea0593f27caf558bc4cc9b665c52fc50b683
    manifest:
      path: api/eebusruntime-v1/manifest.json
      sha256: c93492bd275b5e14d3c9e05da701730d6d34a197e0653e6b169d103418bfcc8c
dependency_policy:
  required_version: reviewed_semver_prerelease
  forbidden_versions:
    - replace
    - local_override
    - pseudo_version
    - branch
    - upstream_module_return
  closure_bindings:
    - annotated_tag_object
    - peeled_commit
    - tree
    - license_provenance_digest
    - module_graph_digest
    - exact_source_ci
    - public_api_manifest_comparison
fork_lifecycle:
  classification: temporary_downstream_patch_carriers
  current_m4_upstream_dependency: nonblocking
  divergence: minimal_gate_and_bridge_only
  unrelated_features: forbidden
  sequence:
    - m4_vr940f_proof_and_PASS
    - upstream_neutral_proposal_evidence_pack
    - ship_go_Discussion_positive_feedback
    - ship_go_accepted_issue_or_draft_PR
    - ship_go_tagged_release
    - eebus_go_Discussion_positive_feedback
    - eebus_go_accepted_issue_or_draft_PR
    - eebus_go_tagged_release
    - repatriation_gate
  repatriation:
    module_paths: github.com/enbility
    replace_directives: zero
    rerun_gates:
      - G10
      - G11
      - G16
      - public_API_anti_leak
      - coexistence
    retirement: archive_read_only_never_delete
ship_go_dial_inventory:
  baseline_file: hub/hub_connections.go
  baseline_direct_Dial_calls: 2
  baseline_order:
    - selected_path
    - root_no_path_fallback
  fork_direct_Dial_calls: 0
  fork_direct_DialContext_calls: 1
  allowed_DialContext_owner: gatedDialContext
  fallback_semantics: preserve_exactly
  fresh_attempts:
    - selected_path
    - root_no_path_fallback
    - hostname
    - ipv4
    - ipv6
attempt_contract:
  prepare:
    request:
      - remote_ski
      - endpoint
      - path
    durable_transition: RETRY_READY_to_ATTEMPT_RESERVED
    handle_fields:
      - attempt_id
      - scope
      - control_epoch
      - attempt_context
    return_only_after: durable_reservation_and_anchor_finalize
  authorize_launch:
    handle_use: single
    gate: same_per_SKI
    rechecks:
      - active_reservation
      - scope
      - control_epoch
      - association_lineage
      - endpoint
      - path
      - retry_state
      - tombstone_set
    durable_transition: ATTEMPT_RESERVED_to_ATTEMPT_LAUNCH_AUTHORIZED
    linearization: launch
    stale_handle: DENY_without_mutation
  abort_prepared:
    handle_use: single_unconsumed
    gate: same_per_SKI
    durable_transition: ATTEMPT_RESERVED_to_BACKOFF_ACTIVE_or_ADMIN_HOLD
    charge: synthetic_failure_exactly_once_unless_terminal_already_won
    stale_handle: no_state_change
  dial:
    immediate_successor: DialContext
    invocations_per_permit: 1
    context: exact_permit_context
    canceled_context: invoke_once_with_zero_network_effect
    uninterrupted_cardinality: PERMIT_equals_DialContext
    crash_gap: restart_synthetic_failure_exactly_once
  bounded_failure:
    max_active_reservations_per_scope: 1
    handle_terminal_actions:
      - AuthorizeLaunch_once
      - AbortPrepared_once
      - lease_expiry_once
    abort_leak_panic: synthetic_failure_exactly_once_unless_terminal_already_won
  restart:
    unresolved_states:
      - ATTEMPT_RESERVED
      - ATTEMPT_LAUNCH_AUTHORIZED
    event: attempt_restart_synthetic_failure
    charge: exactly_once
    order: before_all_runtime_effects
  matching_revocation:
    before_launch: atomic_tombstone_deactivate_clear_without_charge
    after_launch: atomic_tombstone_deactivate_clear_then_cancel_exact_context_without_charge
    crash_after_descriptor: reconcile_revocation_before_restart_failure
    stale_callback: no_state_change_no_charge_no_trust
attempt_journal:
  rollback_domain: coordinated_store_and_anchor_publication
  operation_classes:
    - attempt_prepare
    - attempt_authorize_launch
    - attempt_terminal_success
    - attempt_terminal_failure
    - attempt_abort_synthetic_failure
    - attempt_restart_synthetic_failure
    - attempt_retry_ready
    - attempt_matching_revocation
  reconciliation_observations:
    - exact_target_selected
    - exact_previous_selected_and_target_absent
    - same_number_different_digest_or_reference
    - other_or_ambiguous
privacy_contract:
  private_root_allowed:
    - synthetic_private_key
    - synthetic_certificate
    - synthetic_SKI
    - synthetic_SHIP_ID
    - endpoint
    - IP
    - port
    - path
    - raw_store
    - anchor
  public_output_allowed:
    - repository_metadata
    - tool_versions
    - redacted_commands
    - independent_ordinal_labels
    - stable_enums
    - bounded_counts_durations
    - PASS_FAIL
  forbidden_escape_surfaces:
    - logs
    - errors
    - panic_text
    - stdout_stderr
    - artifacts
    - snapshots
    - diffs
    - evidence
    - public_output_root
  actual_attempt_id_publication: forbidden
  private_root_publication: forbidden
  private_root_deletion: required
```

## Durable Control And Host Anchor

The coordinator-owned control record is inside the selected store generation.
It contains a random store-instance value, a monotonic control epoch,
an association-lineage value, revocation tombstones, quarantine records,
bounded admin-operation receipts, and the state of any coordinated store/anchor
publication. Remote references remain opaque and sensitive. They never become
paths, errors, metrics, fixture names, or public fields.

The host anchor is outside the restorable store set and contains only:

- a provider version and random runtime-local anchor identity;
- the bound random store-instance value;
- high-water manifest generation and control epoch values; and
- at most one exact pending publication descriptor in the closed form below.

The pending descriptor contains exactly these fields. A generation binding is
the complete MSP-04A generation reference: sequence, filename, SHA-256, and
schema version. A manifest SHA-256 is the envelope's digest of the complete
canonical manifest payload, so a sequence number never identifies a branch by
itself.

| Field | Exact binding |
| --- | --- |
| `operation_id` | Bounded coordinator-issued idempotency identifier, never reused within one anchor identity. |
| `operation_class` | One closed coordinator operation kind from the complete table below. |
| `store_instance` | Exact random store-instance value observed before staging. |
| `previous_control_epoch` | Exact control epoch in the selected previous generation. |
| `target_control_epoch` | Exactly `previous_control_epoch + 1`, represented without overflow. |
| `previous_manifest_epoch` | Exact selected manifest epoch before the operation. |
| `previous_manifest_sha256` | Exact selected canonical manifest-payload digest before the operation. |
| `previous_generation` | Complete selected-current generation reference before the operation. |
| `target_manifest_epoch` | Exact epoch-plus-one manifest intended for publication. |
| `target_manifest_sha256` | Exact digest of the intended canonical target manifest payload. |
| `target_generation` | Complete intended target generation reference. |

Staging, finalization, clearing, and reconciliation compare every descriptor
field. The previous and target generation sequences MUST differ and the target
manifest epoch MUST advance by one, but those numeric checks never replace the
digest and complete-reference comparisons. A same-number generation or
manifest branch with different bytes is a mismatch, not a reconciliation
candidate.

The anchor contains no machine id, hostname, hardware serial, MAC/IP address,
account id, remote SKI, SHIP ID, certificate fingerprint, or peer-derived
digest. Clone detection compares independently durable random bindings; it
does not disclose or derive a host-global identity.

The provider MUST attest host/deployment binding, no-export access, monotonic
compare-and-advance, and a durability domain that cannot be rolled back with
the protected store. It must also attest anchor non-restorability or effective
exclusion from every supported backup path. A path name, mode bit,
configuration flag, or persisted `backup_excluded` boolean is not an
attestation. An unavailable or ambiguous capability fails closed.

The provider-specific host-anchor backend is a source implementation choice.
Every backend nevertheless MUST provide authenticated no-export access,
host/deployment binding, durable exact compare-and-stage, compare-and-finalize,
and compare-and-clear operations, monotonic high-water updates, and explicit
durability outcomes. An unsupported primitive or ambiguous result fails closed;
there is no weaker file-only fallback.

## Coordinated Store And Anchor Publication

Every operation that can change trust, revocation, lineage, or a high-water mark
uses one protocol. Under the coordinator's one-writer lock it validates the
complete request, constructs the exact target generation and descriptor, and
durably stages that descriptor in the anchor before calling MSP-04A Commit. It
then applies exactly this outcome map:

| Store result | Required exact anchor action | Allowed immediate result |
| --- | --- | --- |
| `commit_durable` | `compare_and_finalize(exact_descriptor)` atomically advances the bound high-water values and clears that descriptor. | `success_only_after_durable_finalize` |
| `commit_not_published` | `compare_and_clear(exact_descriptor)` without advancing a high-water value. | `failed_closed_unchanged_only_after_durable_clear` |
| `commit_applied_maintenance_failed` | `retain(exact_descriptor)` for explicit reconciliation after reopen. | `DURABILITY_UNKNOWN` |
| `commit_durability_unknown` | `retain(exact_descriptor)` for explicit reconciliation after reopen. | `DURABILITY_UNKNOWN` |
| `interruption_or_descriptor_mismatch` | `retain(exact_descriptor)` and disable mutation. | `DURABILITY_UNKNOWN` |

For `commit_not_published`, unchanged store state is reportable only after the
provider durably completes compare-and-clear against the byte-identical pending
descriptor. A compare mismatch, clear failure, ambiguous durability result, or
crash before durable clear makes durability unknown and enters `QUARANTINED`;
the coordinator MUST NOT infer rollback from the store result alone. An
unresolved pending descriptor at startup has the same result.

Reconciliation is an authenticated admin operation and never runs
automatically. After MSP-04A Open selects one current manifest, it uses this
closed decision table:

| Store observation | Required anchor action | Reconciliation result |
| --- | --- | --- |
| `exact_target_selected` | `compare_and_finalize(exact_descriptor)` | `operation_terminal_only_after_durable_finalize` |
| `exact_previous_selected_and_target_absent` | `compare_and_clear(exact_descriptor)` | `failed_closed_unchanged_only_after_durable_clear` |
| `same_number_different_digest_or_reference` | `none` | `DURABILITY_UNKNOWN/QUARANTINED` |
| `other_or_ambiguous` | `none` | `DURABILITY_UNKNOWN/QUARANTINED` |

`exact_target_selected` requires the target manifest epoch and digest, complete
target generation reference, target control epoch, operation id, class, and
store instance all to match. The previous-state case requires the complete
previous bindings to match and proof that the exact target is not selected or
publication-valid. Therefore reconciliation cannot bless a different branch
merely because it reuses a manifest epoch or generation sequence.

The coordinated publication journal is also the attempt journal. There is no
second rollback domain and no unjournaled attempt-state write. Its closed
operation classes and exact target mutations are:

| Operation class | Exact target mutation | Failure-charge rule |
| --- | --- | --- |
| `first_trust` | `publish_trusted_association` | `not_applicable` |
| `revoke_association` | `publish_tombstone+deactivate_association` | `no_attempt_charge` |
| `repair_publish_inactive_parent` | `publish_fresh_untrusted_lineage` | `not_applicable` |
| `repair_adopt_copied_current` | `publish_fresh_untrusted_lineage` | `not_applicable` |
| `repair_recover_unavailable_host_key` | `publish_fresh_untrusted_lineage` | `not_applicable` |
| `repair_release_retry_quarantine` | `publish_retry_ready` | `no_attempt_charge` |
| `attempt_prepare` | `RETRY_READY_to_ATTEMPT_RESERVED` | `no_attempt_charge` |
| `attempt_authorize_launch` | `ATTEMPT_RESERVED_to_ATTEMPT_LAUNCH_AUTHORIZED` | `no_attempt_charge` |
| `attempt_terminal_success` | `clear_matching_reservation` | `no_attempt_charge` |
| `attempt_terminal_failure` | `clear_matching_reservation+publish_backoff_or_hold` | `charge_exactly_once` |
| `attempt_abort_synthetic_failure` | `clear_matching_reservation+publish_backoff_or_hold` | `charge_exactly_once` |
| `attempt_restart_synthetic_failure` | `clear_unresolved_reservation+publish_backoff_or_hold` | `charge_exactly_once` |
| `attempt_retry_ready` | `BACKOFF_ACTIVE_to_RETRY_READY` | `no_attempt_charge` |
| `attempt_matching_revocation` | `publish_tombstone+deactivate_association+clear_matching_reservation` | `no_attempt_charge` |

All classes use the exact descriptor fields and generic outcome map above.
Attempt classes additionally bind attempt id, scope, control epoch, endpoint,
path, previous attempt state/count, and exact target attempt state/count in the
target generation. Reconciliation is closed by operation class:

| Pending class observation | Required reconciliation before runtime | Result |
| --- | --- | --- |
| `attempt_class+exact_target_selected` | `compare_and_finalize(exact_descriptor)` | `target_transition_terminal_once` |
| `attempt_class+exact_previous_selected_and_target_absent` | `compare_and_clear(exact_descriptor)` | `previous_state_retained+operation_may_be_reissued_once` |
| `attempt_matching_revocation+exact_previous_selected_and_target_absent` | `retry_exact_target_commit_without_clear_then_finalize` | `tombstone_and_clear_reservation_without_charge` |
| `attempt_class+same_number_different_digest_or_reference` | `none` | `DURABILITY_UNKNOWN/QUARANTINED` |
| `attempt_class+other_or_ambiguous` | `none` | `DURABILITY_UNKNOWN/QUARANTINED` |

`attempt_matching_revocation` is the sole previous-state exception: once its
descriptor is durable, the authenticated reconciliation path MUST resolve that
exact tombstone target before startup can consider restart synthetic failure or
enable runtime; startup itself remains inert and does not auto-reconcile. A
crash before descriptor staging has not linearized revocation and follows
ordinary unresolved-attempt recovery. A crash after staging, after target
publication, after anchor finalization, or before response is respectively
retried, finalized, or replayed from the terminal receipt without a failure
charge. Mismatch or ambiguous durability quarantines. No stale callback may
complete, charge, or trust the cleared attempt after any matching-revocation
target is selected.

## Startup Classification And Precedence

MSP-04A Open precedence remains authoritative through selection and validation
of the current generation. MSP-04C never falls back to a lower manifest or an
orphan. The table is the combined startup classification: store-owned
structural failure is decided before policy rows, and rows that inspect control
state are considered only after a mechanically valid current generation is
returned; the first matching row wins:

| Precedence | Reason | Distinguishing evidence | State |
| --- | --- | --- | --- |
| 1 | `CORRUPT_STORE` | Current state is structurally invalid under MSP-04A and no policy record is available. | `CORRUPT_STORE` |
| 2 | `DURABILITY_UNKNOWN` | Store durability is unknown, the host anchor has an unresolved pending publication, or store/anchor finalization cannot be proved. | `QUARANTINED` |
| 3 | `HOST_KEY_UNAVAILABLE` | The protected local signing capability or required anchor provider is absent/unavailable, without evidence that it belongs to another host. | `NO_LOCAL_IDENTITY` |
| 4 | `HOST_BINDING_MISMATCH` | Provider validation positively reports wrong-host or wrong-deployment protected material. | `QUARANTINED` |
| 5 | `CLONE_DETECTED` | A valid local host anchor binds a different random store-instance value. | `QUARANTINED` |
| 6 | `MANIFEST_GENERATION_ROLLBACK` | The selected manifest generation is below the anchor's durable high-water generation. | `QUARANTINED` |
| 7 | `CONTROL_EPOCH_ROLLBACK` | The selected coordinator control epoch is below the anchor's durable high-water control epoch. | `QUARANTINED` |
| 8 | `REVOKED_ASSOCIATION` | The otherwise matching association has a durable effective tombstone. | `REVOKED` |
| 9 | persisted quarantine reason | An exact active `ADMIN_HOLD` or `BACKOFF_ACTIVE` record applies. | `QUARANTINED` |

Absence is not positive clone evidence. A copied store on a fresh host with no
usable anchor is `HOST_KEY_UNAVAILABLE`; wrong-host key attestation is
`HOST_BINDING_MISMATCH`; an instance conflict is `CLONE_DETECTED`.
`CONTROL_EPOCH_ROLLBACK` is logical-state rollback, while
`MANIFEST_GENERATION_ROLLBACK` is rollback of the selected manifest's current
generation. Logical rollback, manifest rollback, and durability uncertainty
therefore remain separate terminal reasons. Errors and evidence report only
these stable reason labels and bounded counters.

## Production Runtime Composition And Authorization

Startup keeps listener creation, remote registration, reconnect scheduling,
and pairing callbacks inert. Store/anchor selection, tombstone precedence,
trust classification and retry restoration complete before any listener is
started or any remote effect is considered. A classification or restore
failure therefore disables those effects rather than allowing the production
runtime to start and attempting to withdraw them later.

| Runtime event | Required coordinator decision | Permitted effect |
| --- | --- | --- |
| `startup_restore` | `classify_startup_and_restore_retry` | `none_before_durable_classification` |
| `listener_start` | `authorize_listener_start(classified_state)` | `start_listener` |
| `pairing_handshake` | `authorize_handshake(exact_scope)` | `real_pairing_transport_callback` |
| `remote_registration` | `authorize_register_remote_ski(exact_association)` | `RegisterRemoteSKI` |
| `reconnect_attempt` | `authorize_reconnect(exact_association,exact_scope)` | `reconnect` |
| `handshake_failure` | `record_failure_and_checkpoint(exact_scope)` | `no_next_attempt_before_durable_result` |

Every call to `RegisterRemoteSKI` and every reconnect decision is
coordinator-authorized against the exact selected generation, control epoch,
association lineage, tombstone set, trust state, and retry scope. No runtime
adapter, restored configuration, library callback, or caller may infer that
authorization. Authorization and the corresponding effect are serialized
with revocation and repair; an asynchronous completion is revalidated before
it can make trust usable, and a stale completion is actively disconnected and
unregistered.

The real pairing callback on the SHIP path obtains admission before continuing
a handshake. Its terminal failure path records the failure into durable retry
state and completes a durable remaining-delay checkpoint before the callback
releases the scope for another attempt. The production checkpoint path
persists only a same-boot monotonic reduction, and startup restores the
persisted state and rearms it on the new monotonic clock before any effect. The
same listener, registration, handshake, and reconnect authorization path
observes that restored state after restart.

A helper-only backoff API, direct coordinator unit call, caller-provided
success/failure assertion, or transcript that does not execute this production
composition is not G11 proof. The real callback must drive the coordinator
record, checkpoint, restart restore, bounded backoff, and terminal quarantine.

## Outgoing Attempt Gate And Dial Sites

The ship-go fork adds one optional, additive `OutgoingAttemptGate` with three
methods: `Prepare`, `AuthorizeLaunch`, and `AbortPrepared`. Optionality preserves standalone
upstream-compatible use: absence retains the fork's normal behavior. Helianthus
composition is stricter. The eebusreg internal bridge MUST install a non-nil
gate before enabling listener, registration, discovery, or reconnect activity;
missing installation fails startup closed.

After ship-go selects the exact remote association, endpoint, and path, it
calls `Prepare(request)`. The request contains only those three private inputs.
The coordinator acquires the per-SKI gate, rechecks retry, quarantine,
tombstone, lineage, and epoch eligibility, allocates the attempt, and completes
the durable `attempt_prepare` publication. Only then may `Prepare` return one
opaque attempt lease/handle containing the allocated attempt id, exact scope,
control epoch, and exact cancellable context. A denial, error, panic, ambiguous
durability result, or missing gate returns no handle and cannot dial.

| Phase field | Phase | Direction | Exact binding |
| --- | --- | --- | --- |
| `remote_ski` | `Prepare` | `input` | Exact opaque remote key for the selected association; never logged or published. |
| `endpoint` | `Prepare` | `input` | Exact selected hostname, IPv4, or IPv6 endpoint plus port in private typed form. |
| `path` | `Prepare` | `input` | Exact selected websocket path, including root/no-path fallback when chosen. |
| `attempt_id` | `Prepare` | `output_handle` | Fresh bounded coordinator id, unique within the current store instance and control epoch. |
| `scope` | `Prepare` | `output_handle` | Exact coordinator retry/quarantine scope allocated for this concrete attempt. |
| `control_epoch` | `Prepare` | `output_handle` | Exact epoch committed by the durable reservation. |
| `attempt_context` | `Prepare` | `output_handle` | Exact per-attempt cancellable context retained by the coordinator until terminal resolution. |
| `attempt_handle` | `Prepare` | `output` | Opaque single-owner lease containing exactly the four output-handle fields. |
| `attempt_handle` | `AuthorizeLaunch` | `input` | Exact unconsumed handle returned by `Prepare`; copying does not create another use. |
| `permit` | `AuthorizeLaunch` | `output` | Exactly `PERMIT` or `DENY`; absence, error, panic, stale handle, or ambiguity is `DENY`. |
| `reason` | `AuthorizeLaunch` | `output` | One stable closed permit/deny reason with no endpoint, key, path, context, or private error text. |
| `attempt_handle` | `AbortPrepared` | `input` | Exact unconsumed handle returned by `Prepare`; only the bridge that owns it may abort. |
| `abort_result` | `AbortPrepared` | `output` | One durable synthetic-failure terminal result, or a stable stale-handle no-op; it never dials. |

`AuthorizeLaunch(handle)` reacquires the same per-SKI gate and atomically
consumes the handle. It rechecks the exact active reservation, scope, control
epoch, association lineage, endpoint, path, retry state, and tombstone set, and
durably publishes `ATTEMPT_LAUNCH_AUTHORIZED`. That transition is the one launch
linearization point. Immediately after `PERMIT` returns, with no callback,
logging, fallback selection, or user code between them, `gatedDialContext`
invokes exactly one concrete websocket `DialContext` with the exact context
from that permit. No wrapper-level admission, callback injection, or
once-per-peer check can replace these call-site phases.

`AbortPrepared(handle)` reacquires the same per-SKI gate and consumes only an
unlaunched `ATTEMPT_RESERVED` handle. It durably publishes the matching
synthetic failure exactly once unless another terminal transition already won.
A stale, copied, consumed, or already-authorized handle is a no-op and cannot
clear, charge, authorize, or dial another attempt.

### Dial Site Coverage

| Dial variant | Required gate placement | Required cardinality |
| --- | --- | --- |
| `selected_endpoint_selected_path` | `Prepare_then_AuthorizeLaunch_immediately_before_DialContext` | `one_fresh_lease+one_single_use_PERMIT+one_DialContext_call` |
| `same_endpoint_root_no_path_fallback` | `Prepare_then_AuthorizeLaunch_immediately_before_DialContext` | `one_new_lease+one_new_single_use_PERMIT+one_DialContext_call` |
| `hostname_retry` | `Prepare_then_AuthorizeLaunch_immediately_before_DialContext` | `one_new_lease+one_new_single_use_PERMIT+one_DialContext_call` |
| `ipv4_retry` | `Prepare_then_AuthorizeLaunch_immediately_before_DialContext` | `one_new_lease+one_new_single_use_PERMIT+one_DialContext_call` |
| `ipv6_retry` | `Prepare_then_AuthorizeLaunch_immediately_before_DialContext` | `one_new_lease+one_new_single_use_PERMIT+one_DialContext_call` |

A `DENY` returns without invoking the concrete dialer. Before launch it
produces zero `DialContext` calls, zero network effects, and no automatic
reannounce for that attempt. A fallback or retry is a new concrete attempt
with a fresh handle and independently durable reservation and permit; denial
cannot be converted into another path, address-family retry, or discovery
announcement by ship-go.

For every uninterrupted helper invocation, `PERMIT` returns equal concrete
`DialContext` invocations one-for-one, and each call has exactly one immediately
preceding single-use permit for the same attempt, endpoint, path, and context.
If revocation cancels the context after launch linearizes but before the call,
ship-go still invokes `DialContext` exactly once with that already-canceled
exact context; the call counts but has zero network effect. Process termination
in the instruction gap is the sole no-call exception: the durable
`ATTEMPT_LAUNCH_AUTHORIZED` record is resolved once as restart synthetic
failure. Thus durable launch authorizations equal dial calls plus those
explicit recovered process-termination gaps, never hidden bypasses.

## Durable Outgoing Attempt Reservation

`ATTEMPT_RESERVED` and `ATTEMPT_LAUNCH_AUTHORIZED` are coordinator-owned durable
states separate from `attempt_count`. Prepare reserves one concrete attempt
without charging a failure. The complete reservation generation and anchor
finalization MUST be durable before `Prepare` returns a handle; the launch
generation and anchor finalization MUST be durable before `AuthorizeLaunch`
returns `PERMIT`.

| Reservation field | Storage | Exact rule |
| --- | --- | --- |
| `state` | `durable` | Exactly `ATTEMPT_RESERVED` or `ATTEMPT_LAUNCH_AUTHORIZED` until one matching terminal outcome is committed. |
| `attempt_id` | `durable` | Same fresh id returned in the handle and carried through `ShipConnection` and terminal callbacks. |
| `remote_ski_scope` | `durable` | Exact opaque key and coordinator scope; never a public evidence value. |
| `control_epoch` | `durable` | Exact epoch at reservation linearization. |
| `endpoint_path` | `durable` | Private typed endpoint and path selected for the concrete dial. |
| `reservation_order` | `durable` | Monotonic coordinator sequence used as authoritative cross-event order. |
| `reservation_timestamp` | `durable_diagnostic` | Bounded injected-clock value used only to correlate test evidence, never for trust or deadlines. |
| `attempt_count_before` | `durable` | Exact unchanged count before this reservation. |
| `attempt_context` | `volatile` | Exact cancellable context keyed by attempt id; no context object or pointer is persisted. |
| `lease_state` | `volatile` | Exactly `fresh`, `consumed`, or `expired`; at most one active handle exists per scope. |
| `lease_deadline` | `volatile` | Bounded injected-monotonic deadline; expiry resolves as one synthetic failure, never silent clear. |

| Reservation event | Required durable transition | Dial/callback consequence |
| --- | --- | --- |
| `prepare_eligible` | `RETRY_READY -> ATTEMPT_RESERVED` | `zero_DialContext_calls_before_commit` |
| `prepare_commit_durable` | `ATTEMPT_RESERVED -> ATTEMPT_RESERVED` | `handle_may_return` |
| `prepare_not_published` | `RETRY_READY -> RETRY_READY` | `no_handle+zero_DialContext_calls` |
| `prepare_durability_unknown` | `ATTEMPT_RESERVED -> QUARANTINED` | `no_handle+zero_DialContext_calls` |
| `authorize_launch_matching` | `ATTEMPT_RESERVED -> ATTEMPT_LAUNCH_AUTHORIZED` | `single_use_PERMIT_is_launch_linearization` |
| `authorize_stale_consumed_or_mismatched` | `no_state_change` | `DENY+zero_DialContext_calls_for_that_handle` |
| `permit_context_already_canceled` | `ATTEMPT_LAUNCH_AUTHORIZED -> ATTEMPT_LAUNCH_AUTHORIZED` | `one_DialContext_call+zero_network_effect` |
| `matching_terminal_success` | `active_attempt -> clear_reservation_without_failure_charge` | `accept_only_if_epoch_and_tombstone_still_valid` |
| `matching_terminal_failure` | `active_attempt -> BACKOFF_ACTIVE_or_ADMIN_HOLD` | `charge_attempt_count_exactly_once` |
| `matching_abort_or_lease_expiry` | `active_attempt -> BACKOFF_ACTIVE_or_ADMIN_HOLD` | `synthetic_failure_charge_exactly_once` |
| `restart_with_unresolved_reservation` | `active_attempt -> BACKOFF_ACTIVE_or_ADMIN_HOLD` | `synthetic_failure_linearization+charge_exactly_once_before_runtime` |
| `durable_retry_ready` | `BACKOFF_ACTIVE -> RETRY_READY` | `no_new_Prepare_before_commit` |
| `matching_revocation` | `active_attempt -> tombstone+clear_reservation` | `atomic_no_failure_charge+DENY_or_cancel` |
| `stale_terminal_callback` | `no_state_change` | `discard_without_charge_or_trust` |

The attempt id is carried through `ShipConnection`, dial completion, transport
accept, handshake completion, cancellation, and terminal callbacks. Every
callback is checked against the active reservation's attempt id, control epoch,
scope, endpoint, and path. A delayed callback from an older attempt, earlier
epoch, restart, revoked association, consumed handle, or expired lease is stale;
it cannot clear, charge, or trust the active reservation.

The bridge owns every returned handle. It MUST invoke `AuthorizeLaunch` once or
`AbortPrepared` once before the bounded lease expires. Abort, lease expiry, a
recovered helper panic, or a dialer panic resolves the matching active attempt
as one synthetic failure unless a matching terminal outcome already won. A
panic before any durable reservation returns no handle and charges nothing. A
panic after durable reservation but before handle delivery is found by the
bounded per-scope watchdog or restart path. At most one active reservation per
scope bounds leaks; all terminal paths cancel the context and consume the
handle. Reuse or copying of a consumed, expired, earlier-epoch, restarted, or
otherwise stale handle always returns `DENY` without mutation.

On restart, each unresolved `ATTEMPT_RESERVED` or
`ATTEMPT_LAUNCH_AUTHORIZED` record is an explicit
`attempt_restart_synthetic_failure` linearization before listener setup,
discovery, registration, reannounce, reconnect, or another `Prepare`. The
coordinated transition clears that exact reservation and charges the count
exactly once using the existing bounded backoff formula. Its operation receipt
and attempt id make replay idempotent, including a crash during recovery. The
fourth charged failure in the deterministic vector enters terminal
`ADMIN_HOLD`. Reservation publication failure, backoff, quarantine, and
terminal hold all produce zero `DialContext` calls.

Matching revocation uses one `attempt_matching_revocation` publication in every
active-attempt phase. It atomically writes the tombstone, deactivates the
association, and clears the exact reservation without a failure charge. Before
launch it consumes the handle and returns `DENY`. After launch the same
publication also cancels the exact context; the immediate canceled-context
`DialContext` rule still applies if the call has not begun. The
coordinated-journal reconciliation rules above govern every crash boundary, and
stale callbacks remain no-ops.

The durable reservation timestamp and order are evidence correlation fields,
not caller assertions. G10/G11/G16 evidence binds their committed values and
attempt id to injectable-dialer call start and fake-peer accept observations.
The authoritative ordering is reservation commit, handle return, durable
launch authorization, permit return, exact-context `DialContext` call, then
optional accept. Callback injection without those observations is not pre-dial
evidence.

## eebus-go Bridge And Type Boundary

| Layer | Required additive change | Forbidden change |
| --- | --- | --- |
| `helianthus_ship_go` | `optional_Prepare+AuthorizeLaunch+AbortPrepared+one_gatedDialContext_helper` | `protocol_or_handshake_semantic_change` |
| `helianthus_spine_go` | `canonical_module_path+reviewed_ship_go_imports_only` | `SPINE_model_feature_semantic_wire_runtime_or_logging_change` |
| `helianthus_eebus_go` | `configuration_bridge_carries_attempt_handle_and_id` | `SPINE_or_semantic_model_change` |
| `helianthus_eebusreg_internal` | `coordinator_adapter+attempt_journal+callback_validation` | `fork_type_in_public_package` |
| `helianthus_eebusreg_public` | `unchanged` | `fork_import_or_new_public_surface` |

The eebus-go fork exposes enough configuration to install the two-phase
ship-go hook and carry the attempt handle and id through connection callbacks.
It does not change SPINE
models, feature discovery, semantic projection, subscription behavior, or
message interpretation. Its bridge imports the reviewed ship-go prerelease by
canonical module path and tag without `replace`.

Only an eebusreg internal adapter may translate between coordinator-owned
request/decision records and dependency hook types. No exported declaration,
public package field, method, alias, generic argument, error, or callback may
name a type from any dependency fork. The frozen public Go API and all
protocol/API docs remain unchanged.

## Revocation And Dial Race Linearization

Revocation, `Prepare`, and `AuthorizeLaunch` acquire the same per-SKI gate owned
by the coordinator. Reservation, launch authorization, tombstone publication,
context cancellation, concrete dial invocation, disconnect observation, and
unregistration therefore have one closed race order.

| Race order | Linearization | Required result |
| --- | --- | --- |
| `revocation_before_prepare` | `revocation_wins` | `tombstone+no_handle+zero_DialContext_calls+unregister` |
| `revocation_after_prepare_before_authorize` | `matching_revocation_wins` | `atomic_tombstone+clear_reservation+no_failure_charge+DENY+zero_DialContext_calls` |
| `revocation_after_authorize_before_DialContext` | `launch_wins_then_revocation` | `atomic_tombstone+clear_reservation+no_failure_charge+cancel_exact_context+one_canceled_DialContext_call+zero_network_effect+unregister` |
| `DialContext_invoked_before_revocation` | `launch_wins_then_revocation` | `atomic_tombstone+clear_reservation+no_failure_charge+cancel_exact_context+disconnect_observed+unregister+no_trust_accept` |
| `callback_after_tombstone` | `revocation_already_won` | `discard_stale_callback+no_state_change` |
| `withdrawal_failure_or_ambiguity` | `revocation_nonterminal` | `tombstone_effective+ADMIN_HOLD+no_success` |

`AuthorizeLaunch` holds the per-SKI gate through the durable launch
linearization and consumes the handle. Revocation that wins before it uses the
atomic matching-revocation transition and prevents the call. If launch wins,
the same transition durably tombstones, deactivates the association, clears the
exact reservation without a failure charge, and cancels its context. A
not-yet-started helper then makes its required one canceled-context
`DialContext` call with zero network effect; an already-started call is canceled
and disconnected. Revocation observes transport disconnect and invokes
`UnregisterRemoteSKI` before success. No accept or terminal callback after the
tombstone can make the association trusted. All withdrawal ambiguity remains
fail-closed under the existing revocation contract.

## Orthogonal Coordinator And Recovery State Machines

MSP-04B's coordinator FSM and MSP-04C's recovery/trust FSM are orthogonal axes,
not one replacement state list. The MSP-04B axis remains exactly `DISABLED`,
`PAIRING_CLOSED`, `OPEN_EMPTY`, `CANDIDATE_PENDING`, and `COMMITTING`, with its
existing candidate, window, and terminal rules unchanged. MSP-04C adds only the
second axis: `NO_LOCAL_IDENTITY`, `UNPAIRED_LOCKED`, `PAIRED_TRUSTED`, `REVOKED`,
`QUARANTINED`, and `CORRUPT_STORE`.

### Valid Cross-Product

Only these products are valid after startup classification has linearized. A
product not listed is forbidden and fails closed to
`DISABLED/QUARANTINED` unless MSP-04A has already selected `CORRUPT_STORE`.

| MSP-04B coordinator state | Allowed MSP-04C recovery/trust states |
| --- | --- |
| `DISABLED` | `NO_LOCAL_IDENTITY`, `QUARANTINED`, `CORRUPT_STORE` |
| `PAIRING_CLOSED` | `UNPAIRED_LOCKED`, `PAIRED_TRUSTED`, `REVOKED` |
| `OPEN_EMPTY` | `UNPAIRED_LOCKED`, `REVOKED` |
| `CANDIDATE_PENDING` | `UNPAIRED_LOCKED`, `REVOKED` |
| `COMMITTING` | `UNPAIRED_LOCKED`, `REVOKED` |

The one-writer lock may hold an operation in progress without publishing an
intermediate product. During that interval facade effects are denied and no
other event can observe or mutate either axis. The operation publishes only one
of the terminal products below.

### Recovery/Trust Axis Transitions

| MSP-04C state | Allowed next MSP-04C states |
| --- | --- |
| `NO_LOCAL_IDENTITY` | `UNPAIRED_LOCKED`, `QUARANTINED` |
| `UNPAIRED_LOCKED` | `PAIRED_TRUSTED`, `QUARANTINED`, `CORRUPT_STORE` |
| `PAIRED_TRUSTED` | `REVOKED`, `QUARANTINED`, `CORRUPT_STORE` |
| `REVOKED` | `PAIRED_TRUSTED`, `QUARANTINED` |
| `QUARANTINED` | `UNPAIRED_LOCKED`, `REVOKED`, `CORRUPT_STORE` |
| `CORRUPT_STORE` | `UNPAIRED_LOCKED`, `REVOKED`, `QUARANTINED` |

`UNPAIRED_LOCKED` or `REVOKED` reaches `PAIRED_TRUSTED` only through a later
explicit MSP-04B window, a new exact OOB confirmation, and durable coordinated
publication. A `REVOKED` transition uses a new association lineage and cannot
reuse a tombstoned association. Repair never takes either transition.

### Transition Precedence And Linearization

Every event acquires the same one-writer lock and has one coordinator
linearization point. Lock acquisition order decides between concurrent valid
events; within the winning event, these checks have strict precedence:

| Precedence | Rule at the linearization point |
| --- | --- |
| `1` | MSP-04A structural selection and unresolved store/anchor durability evidence disable the MSP-04B axis and select `CORRUPT_STORE` or `QUARANTINED`. |
| `2` | A staged coordinated publication is completed or classified before any new pairing, revocation, repair, retry, or startup effect. |
| `3` | An exact revocation or repair command closes/cancels MSP-04B window and candidate state before its store mutation begins. |
| `4` | An MSP-04B close, expiry, cancel, exact confirmation, open, or admission event applies its existing first-terminal-rule ordering if the current cross-product permits it. |

The exact confirmation path preserves the MSP-04B transition that MSP-04C
depends on:

| Confirmation phase/outcome | Required combined transition |
| --- | --- |
| `exact_confirmation_linearizes` | `CANDIDATE_PENDING/untrusted -> COMMITTING/same_untrusted` |
| `store_and_anchor_durable` | `COMMITTING/same_untrusted -> PAIRING_CLOSED/PAIRED_TRUSTED` |
| `commit_not_published_and_anchor_cleared` | `COMMITTING/same_untrusted -> PAIRING_CLOSED/same_untrusted` |
| `publication_unknown` | `COMMITTING/same_untrusted -> DISABLED/QUARANTINED` |

Here `untrusted` is exactly `UNPAIRED_LOCKED` or `REVOKED`. Confirmation closes
the window and moves `CANDIDATE_PENDING` to `COMMITTING` before any store or
anchor mutation. The recovery/trust axis remains unchanged until both durable
boundaries are known. Startup never enters `PAIRED_TRUSTED` from copied,
restored, rolled-back, legacy-anchorless, host-key-unavailable, or
durability-unknown state. A repair result never transitions directly to
`PAIRED_TRUSTED`, invokes `RegisterRemoteSKI`, or opens a pairing window.

## Durable Revocation Tombstones

Revocation is exactly the `revoke_association` command in the closed command set
of the existing MSP-04B AF_UNIX admin endpoint. Kernel-reported
same-effective-UID authentication succeeds before frame parsing. Unknown
commands and fields are rejected. There is no TCP, loopback, HTTP, CLI,
environment, file-drop, MCP, GraphQL, Portal, Home Assistant, exported Go, or
other public revocation path.

The request contains exactly one target and the following complete binding:

| Revocation request field | Exact binding |
| --- | --- |
| `operation_id` | Bounded idempotency identifier for this command. |
| `association_ref` | Exact opaque active association reference; no prefix, peer-only, or wildcard match. |
| `association_lineage` | Exact current lineage containing that association. |
| `expected_store_generation` | Complete selected-current MSP-04A generation reference. |
| `expected_manifest_epoch` | Exact selected manifest epoch. |
| `expected_manifest_sha256` | Exact selected canonical manifest-payload digest. |
| `expected_control_epoch` | Exact control epoch in that generation. |

The coordinator authenticates, parses, validates, and serializes revocation
with startup, pairing, retry, repair, facade effects, anchor operations, and
store Commit under the same one-writer lock. Any stale target, lineage,
generation reference, manifest binding, or control epoch returns conflict
without changing in-memory or durable state.

The control record durably retains the full request binding and terminal result
in a bounded receipt. Replay behavior is closed:

| Revocation request condition | Stable result | Additional mutation |
| --- | --- | --- |
| `new_exact_request` | `commit_once` | `one_coordinated_publication` |
| `identical_in_flight_replay` | `operation_in_progress` | `none` |
| `identical_terminal_replay` | `recorded_terminal_result` | `none` |
| `operation_id_with_changed_binding` | `idempotency_conflict` | `none` |
| `stale_association_or_generation` | `revocation_conflict` | `none` |
| `replay_at_or_below_compacted_high_water` | `idempotency_expired` | `none` |

Identical means byte-for-byte equality of every decoded request field, not only
the operation id. Terminal replay remains idempotent across restart. Receipt
compaction may retain only a non-identifying operation-id high water after its
bounded retention condition, but can never permit an old id to execute again.

Revocation first closes pairing and denies the target in memory, then proposes
one generation that both deactivates the association and appends an effective
tombstone. A tombstone binds the opaque association reference, revocation
epoch, operation id, and effective generation. Only after store and anchor
finalization are durable may runtime withdrawal begin. Durable publication is
necessary but not sufficient: the coordinator does not report `revoked` until
the exact runtime withdrawal below also completes.

### Authoritative Runtime Withdrawal

| Revocation phase | Required effect | Success condition |
| --- | --- | --- |
| `deny_in_memory` | `coordinator_deny_exact_association` | `registration_and_reconnect_denied` |
| `commit_tombstone` | `durable_coordinated_publication` | `tombstone_and_anchor_finalized` |
| `disconnect_active_session` | `DisconnectSKI(exact_remote_ski)` | `disconnected_or_authoritatively_absent` |
| `unregister_remote` | `UnregisterRemoteSKI(exact_remote_ski)` | `unregistered_or_authoritatively_absent` |
| `return_success` | `record_terminal_revoked` | `all_prior_phases_complete` |

The coordinator invokes both `DisconnectSKI` and `UnregisterRemoteSKI`; it does
not skip either call based only on cached liveness or registration state. An
authoritative already-absent result is idempotent success for that effect. If
either withdrawal fails or is ambiguous, the tombstone remains effective,
the association stays denied, the command reports
`revocation_withdrawal_incomplete`, and the receipt cannot record terminal
`revoked`. Exact replay may finish the missing withdrawal but cannot repeat or
undo the tombstone publication.

On startup, a tombstone takes precedence over a durable association and blocks
automatic reload. Startup must not call `RegisterRemoteSKI`, schedule
reconnect, restore allowlist trust, or admit a candidate for any tombstoned
association. Restart does not clear it or convert an incomplete withdrawal
into success.
`commit_not_published` plus exact durable anchor clear retains in-process denial
but reports unchanged durable state. Clear failure, crash before durable clear,
`commit_applied_maintenance_failed`, `commit_durability_unknown`, or other
anchor uncertainty enters `DURABILITY_UNKNOWN` quarantine with no trust effect.

Repair cannot delete, truncate, rewrite, or mark a tombstone ineffective.
Compaction may move old tombstones into a versioned deny set only if exact deny
behavior and revocation high-water evidence are preserved. Capacity exhaustion
fails closed; it never evicts the oldest tombstone. A later explicit OOB flow
creates a new association lineage and does not resurrect the tombstoned record.

## Persistent Quarantine And Backoff

Each quarantine record persists an opaque scope, stable reason, state
(`BACKOFF_ACTIVE`, `RETRY_READY`, or `ADMIN_HOLD`), saturating attempt count,
bounded backoff step, bounded remaining delay, bounded retention budget, and
last control epoch. Clone, rollback, host-binding, revocation-uncertainty, and
durability reasons use `ADMIN_HOLD` and never retry automatically.

For a new retryable scope the initial durable tuple is
`(state=RETRY_READY, attempt_count=0, remaining_delay=0)`. Admission does not
increment the count. If that admitted handshake fails, the coordinator
linearizes the failure, computes and atomically persists these values before it
releases the one-writer lock:

```text
next_attempt_count = min(attempt_count + 1, attempt_count_max)
if next_attempt_count == attempt_count_max:
    next = (ADMIN_HOLD, next_attempt_count, 0, HANDSHAKE_ATTEMPT_LIMIT)
else:
    exponent = min(next_attempt_count - 1, exponent_cap)
    delay = min(checked(base_backoff * 2^exponent), max_backoff)
    next = (BACKOFF_ACTIVE, next_attempt_count, delay)
```

When `attempt_count_max > 1`, the first nonterminal admitted failure uses
`base_backoff`. The count increments exactly at a matching terminal-failure
linearization or an explicit abort, lease-expiry, or unresolved-reservation
synthetic-failure linearization. It never increments on admission, denial,
ordinary restart without an unresolved reservation, deadline expiry, or
wall-clock change. At
`attempt_count_max`, that failure atomically enters terminal `ADMIN_HOLD` with
reason `HANDSHAKE_ATTEMPT_LIMIT` and zero remaining delay; no later handshake
or reconnect is automatically admitted. There is no admitted failure at an
already saturated count. Exponent saturation begins when
`next_attempt_count - 1 >= exponent_cap`; duration saturation occurs when the
checked product reaches `max_backoff`. A nonterminal retry is admitted only
after a durable `BACKOFF_ACTIVE -> RETRY_READY` transition with unchanged
attempt count. Leaving terminal hold requires the exact authenticated repair
contract and never follows elapsed time or restart.

`base_backoff`, `max_backoff`, `attempt_count_max`, and `exponent_cap` are
source implementation constants, not portable API values. They MUST satisfy
`base_backoff > 0`, `max_backoff >= base_backoff`,
`attempt_count_max >= 1`, and `exponent_cap >= 0`, fit the closed persisted
ranges, and be covered by boundary tests. Checked multiplication that would
overflow saturates to `max_backoff`; an invalid configured or decoded bound,
underflow, negative duration, or out-of-range persisted value enters
`ADMIN_HOLD` and admits no retry. There is no jitter.

Wall clock is never used to derive or shorten a deadline. The durable
representation is only `(state, attempt_count, remaining_delay)`; it contains
no wall timestamp and no monotonic timestamp from an earlier boot. While
running, the volatile representation is
`deadline_monotonic = monotonic_now + remaining_delay`. A checkpoint may reduce
the durable remainder only from elapsed time measured on that same monotonic
clock and only after the reduced remainder is durable. A crash before that
durability point leaves the earlier, greater remainder authoritative.

After restart the coordinator sets
`deadline_monotonic = new_monotonic_now + persisted_remaining_delay`. It first
persists `RETRY_READY` with zero remainder when that deadline is reached, then
may admit one retry. Restart or wall-clock change can extend a wait but can
never decrement attempt state, shorten the persisted remainder, admit early
retry, or restore trust. A checkpoint or ready-transition durability failure
fails closed in `BACKOFF_ACTIVE` or `ADMIN_HOLD`. The configured bound applies
to stored duration and each armed interval; repeated crashes may conservatively
extend elapsed wall time.

### EEBUS-G11 Deterministic Vector

The required synthetic vector injects
`base_backoff=3s`, `exponent_cap=2`, `max_backoff=10s`, and
`attempt_count_max=4`. These are fixture values and do not freeze production
policy constants.

| Step | Event | Previous count | Persisted count | Persisted delay | Persisted state |
| --- | --- | --- | --- | --- | --- |
| `0` | `new_scope` | `not_applicable` | `0` | `0s` | `RETRY_READY` |
| `1` | `first_admitted_failure` | `0` | `1` | `3s` | `BACKOFF_ACTIVE` |
| `2` | `second_admitted_failure` | `1` | `2` | `6s` | `BACKOFF_ACTIVE` |
| `3` | `third_admitted_failure` | `2` | `3` | `10s` | `BACKOFF_ACTIVE` |
| `4` | `fourth_admitted_failure` | `3` | `4` | `0s` | `ADMIN_HOLD` |

The restart arm in the same vector is exact:

| Checkpoint | Durable tuple | Volatile monotonic state | Required decision |
| --- | --- | --- | --- |
| `after_step_2` | `BACKOFF_ACTIVE,count=2,remainder=6s` | `now=20s,deadline=26s` | `deny_retry` |
| `durable_checkpoint_after_2s` | `BACKOFF_ACTIVE,count=2,remainder=4s` | `now=22s,deadline=26s` | `deny_retry` |
| `restart_with_arbitrary_wall_change` | `BACKOFF_ACTIVE,count=2,remainder=4s` | `new_now=100s,new_deadline=104s` | `deny_retry` |
| `probe_before_rearmed_deadline` | `BACKOFF_ACTIVE,count=2,remainder=4s` | `new_now=103.999s,new_deadline=104s` | `deny_retry` |
| `probe_at_rearmed_deadline` | `RETRY_READY,count=2,remainder=0s` | `new_now=104s` | `persist_ready_before_admit` |

Active records are never evicted to satisfy a count or retention bound. After
a successful trusted handshake or exact repair, detailed terminal history may
compact only after the bounded monotonic retention budget is consumed. The
compacted record retains reason class, saturated attempt summary, control-epoch
high water, and outcome without peer material. At capacity, the coordinator
enters `ADMIN_HOLD` and rejects new attempts rather than deleting evidence.

## Deterministic Admin-Local Repair

Repair extends the existing MSP-04B AF_UNIX endpoint only. Kernel-reported
same-effective-UID authentication occurs before frame parsing. There is no TCP,
loopback, HTTP, CLI, environment, file-drop, MCP, GraphQL, Portal, Home
Assistant, or remote repair path.

Every repair request binds exactly one repair kind and scope plus
`expected_state`, `expected_reason`, the complete selected manifest epoch,
digest, and current/parent generation references, control epoch, anchor
version/high-water values, a bounded operation/idempotency id, and the next
monotonic repair sequence. Supported kinds are limited to
`reconcile_pending_publication`, `publish_inactive_parent`,
`adopt_copied_current`, `recover_unavailable_host_key`, or
`release_retry_quarantine`. A stale, digest-incomplete, same-number or
different-branch binding, or broader binding returns `repair_conflict` with no
mutation.

The coordinator serializes repair with pairing, revocation, retry, startup,
and store commit under the existing one-writer lock. It durably records the
full request binding and terminal result in a bounded private repair receipt.
An identical replay, including after restart, returns that result without a
second mutation. Reuse of the key with any changed field returns
`idempotency_conflict`. Expired receipts may compact to a non-identifying
repair-sequence high-water summary. A replay at or below that high water returns
`idempotency_expired` with no mutation. Active evidence, tombstones, and
detection lineage remain intact.

Repair publishes a new generation; it never edits a manifest, generation,
anchor, tombstone, or recovery candidate in place. The new generation appends
the detection and repair result, preserves immutable prior evidence, and lands
in `UNPAIRED_LOCKED` or `REVOKED`. It cannot erase a reason, clear a tombstone,
approve/register a peer, synthesize an association, reuse an old pairing
candidate, or silently re-pair.

### Untrusted-Lineage Repair Invariant

For the three repairs that adopt inherited association content, the required
effects are closed:

| Repair kind | Exact source content | Target lineage | Inherited association effect | Success product |
| --- | --- | --- | --- | --- |
| `publish_inactive_parent` | `selected_manifest.parent` | `fresh_random` | `deactivate_all+effective_tombstone_each` | `PAIRING_CLOSED/UNPAIRED_LOCKED` |
| `adopt_copied_current` | `selected_manifest.current` | `fresh_random` | `deactivate_all+effective_tombstone_each` | `PAIRING_CLOSED/UNPAIRED_LOCKED` |
| `recover_unavailable_host_key` | `selected_manifest.current` | `fresh_random` | `deactivate_all+effective_tombstone_each` | `PAIRING_CLOSED/UNPAIRED_LOCKED` |

The inherited association set is every association record in the exact source
generation that is trusted, active, allowlisted, reconnectable, or otherwise
capable of causing present or future `RegisterRemoteSKI`. The coordinator MUST
enumerate that complete set without filtering by current reachability, expiry,
key availability, or peer liveness. If any record cannot be classified or a
tombstone cannot be represented within bounds, validation fails before
publication.

One target generation atomically records a fresh random association-lineage
value, marks every member of that inherited set inactive, and appends one
effective tombstone for each member. It is invalid to publish only the fresh
lineage, only deactivation, or only a subset of tombstones. The command cannot
report success until that complete generation and its exact anchor finalization
are durable. On restart the loader selects only the target generation,
tombstones dominate every inherited association, and zero inherited association
may reload trust, enter an allowlist, reconnect as trusted, or invoke
`RegisterRemoteSKI`.

Before store mutation, the provider durably stages the exact pending anchor
publication descriptor defined above. The coordinator then commits one store
generation and applies the coordinated outcome map, including exact
compare-and-clear for `commit_not_published`. Trust is usable only after both
durability domains are known. Any timeout, mismatch,
`commit_applied_maintenance_failed`, `commit_durability_unknown`, failed pending
clear, or anchor durability ambiguity returns `repair_outcome_unknown`, enters
`QUARANTINED`, keeps mutation disabled, and requires a new exact reconciliation
request after reopen. No automatic retry occurs.

## Backup And Unavailable-Key Recovery

Generic backup is not a trust-preserving operation. A host-bound protected key
cannot be unsealed on another host; a correctly backup-excluded key or anchor
is absent after restore. Both cases fail closed before association reload.
Backup exclusion may be claimed only by a provider-specific attestation and
platform conformance lane; MSP-04A's v1 records gain no portable key or trusted
`backup_excluded` metadata assertion.

When the host key is unavailable, the only recovery is the exact
`recover_unavailable_host_key` repair. It creates a fresh non-exporting local
identity and fresh host anchor and applies the complete untrusted-lineage
invariant to every inherited association from the restored generation.
Wrong-host key material is never exported, rebound, copied, or converted.
Success lands `UNPAIRED_LOCKED`; every peer requires a new explicit OOB flow.
If provider creation, tombstone publication, or either durability boundary is
unavailable, recovery remains `NO_LOCAL_IDENTITY` or `QUARANTINED`.

Legacy MSP-04B state without an enrolled host anchor is not grandfathered into
trusted state. It requires this same untrusted-lineage repair. This deliberately
trades automatic upgrade continuity for a falsifiable no-silent-restore rule.

## Public Surface And Evidence Privacy

The supported public Go API remains byte-for-byte frozen. Public `Runtime`,
`Snapshot`, and `PairingState` gain no restore reason, anchor, tombstone,
attempt, backoff, repair, idempotency, host-key, generation, or mutation field
or method. MSP-04C adds no semantic identity, raw write, MCP tool/resource,
GraphQL field/mutation, Portal action, Home Assistant entity/service, gateway
command, HTTP handler, network listener, or protocol behavior.

Private generated fixture inputs and publishable evidence are disjoint roots
with disjoint schemas. The harness may create synthetic private material only
inside its isolated per-run input/store root; that root is never an artifact,
evidence, snapshot, golden file, test failure attachment, or scan output.

| Data class | Allowed content | Required confinement |
| --- | --- | --- |
| `private_generated_test_input` | `synthetic_private_key+certificate+SKI+SHIP_ID+endpoint+IP+port+selected_path+root_fallback_path` | `isolated_ephemeral_input_root_only` |
| `private_generated_store` | `raw_store+anchor+attempt_endpoint_path+opaque_association` | `isolated_ephemeral_store_root_only` |
| `publishable_G16_output` | `repo+branch+commit+issue+tool_versions+redacted_commands+per_run_ordinal_labels+stable_enums+bounded_counts_durations+PASS_FAIL` | `public_output_root_only` |

The collector derives public ordinal case and attempt labels independently; it
never copies an actual attempt id, endpoint, path, key, certificate field, SKI,
SHIP ID, context value, store byte, or private filename. Before publication it
builds a forbidden canary set from every private generated input in raw, text,
hex, base64, full-digest, bounded-prefix, and bounded-suffix forms. It scans all
captured logs, structured and unstructured errors, recovered panic text,
stdout/stderr, public artifacts, snapshots, diffs, evidence rows, and the
entire public output root. Any match fails G16 and suppresses publication. The
private input/store roots themselves are deletion-verified after the scan; they
are not falsely treated as publishable scan results.

Hardware checks remain SSH-only and cannot replace the deterministic synthetic
gate cases. No hardware-derived value may seed private generated fixtures or
public labels.

## R2 Pre-Dial Falsification Matrix

The executable harness uses a fake TLS endpoint, a fake peer on the SHIP path,
an injectable websocket dialer, an injected clock, and a crashable deterministic
store/anchor pair. It observes the real dependency call sites and callbacks;
direct callback invocation is used only as a negative control.

| Case | Fixture/action | Required observation | Falsifier |
| --- | --- | --- | --- |
| `denied_prepare` | `Prepare_returns_no_handle` | `zero_DialContext_calls+zero_accepts+zero_reannounce` | `any_DialContext_call_or_reannounce` |
| `denied_authorize` | `AuthorizeLaunch_returns_DENY` | `zero_DialContext_calls_for_handle+zero_accepts` | `DialContext_call_for_denied_handle` |
| `reservation_publication_failure` | `commit_not_published_or_unknown` | `zero_DialContext_calls+DENY_or_quarantine` | `permit_or_network_call` |
| `backoff_active` | `persisted_BACKOFF_ACTIVE` | `zero_DialContext_calls_before_durable_RETRY_READY` | `early_network_call` |
| `quarantine_active` | `persisted_QUARANTINED` | `zero_DialContext_calls` | `any_network_call` |
| `admin_hold` | `persisted_ADMIN_HOLD` | `zero_DialContext_calls` | `any_network_call` |
| `path_fallback` | `selected_path_then_root_no_path` | `fresh_lease_and_PERMIT_each+PERMIT_count_equals_DialContext_count` | `changed_fallback_semantics_or_reused_handle_or_count_mismatch` |
| `endpoint_fallback` | `hostname_then_ipv4_then_ipv6` | `fresh_lease_and_PERMIT_each+exact_endpoint_binding` | `ungated_or_reused_hostname_IPv4_IPv6_attempt` |
| `canceled_context_after_permit` | `revocation_cancels_exact_context_before_call` | `one_DialContext_call_with_same_canceled_context+zero_network_effect` | `skipped_call_or_unrelated_context_or_network_effect` |
| `mdns_storm` | `concurrent_repeated_discovery_events` | `per_SKI_serialization+denied_events_zero_dials+no_auto_reannounce` | `parallel_unauthorized_dial_or_reannounce` |
| `crash_after_reservation` | `crash_after_durable_ATTEMPT_RESERVED_before_authorize` | `restart_synthetic_failure_charges_once_before_runtime` | `reservation_cleared_or_uncharged_or_double_charged` |
| `crash_after_launch_authorization` | `crash_after_PERMIT_before_DialContext` | `restart_synthetic_failure_charges_once+explicit_gap_observation` | `hidden_permit_bypass_or_clear_without_charge` |
| `abort_expiry_panic` | `abort+lease_expiry+panic_at_each_boundary` | `bounded_one_active_reservation+one_synthetic_failure_or_existing_terminal` | `leak_or_double_charge_or_stale_handle_permit` |
| `delayed_callback` | `old_attempt_callback_after_new_reservation` | `stale_callback_discarded+active_reservation_unchanged` | `old_callback_charges_clears_or_trusts` |
| `matching_revocation_crash_boundaries` | `crash_before_stage+after_stage+after_target+after_finalize` | `ordinary_recovery_before_stage+otherwise_tombstone_and_clear_without_charge_once` | `post_stage_failure_charge_or_missing_tombstone_or_double_terminal` |
| `revocation_race` | `revocation_at_each_Prepare_Authorize_DialContext_boundary` | `one_linearized_order+exact_context_cancel+disconnect_observed+unregister` | `post_tombstone_trust_or_success_before_withdrawal` |
| `fourth_failure_admin_hold` | `four_matching_terminal_failures` | `counts_1_2_3_4+fourth_enters_ADMIN_HOLD+zero_fifth_dial` | `fifth_permit_or_dial` |
| `dial_accept_order` | `one_permitted_fake_peer_connection` | `reservation_commit_before_handle_before_launch_commit_before_permit_before_DialContext_before_accept` | `missing_or_reordered_observation` |
| `ship_go_AST_inventory` | `scan_fixed_fork_source` | `zero_direct_Dial+one_DialContext_in_gatedDialContext_only` | `residual_Dial_or_other_DialContext_or_hidden_alias` |
| `private_public_split` | `generated_private_inputs_then_G16_collection` | `private_root_only+zero_canary_matches_in_all_public_surfaces+deletion_verified` | `private_value_in_log_error_panic_artifact_diff_evidence_or_public_output` |
| `callback_injection_negative_control` | `terminal_callback_without_dialer_or_accept_event` | `not_pre_dial_evidence+case_FAIL` | `case_PASS` |
| `race_detector` | `all_cases_under_go_test_race` | `zero_race_reports+deterministic_counts` | `race_report_or_nondeterministic_result` |

For every PASS case the private harness observes reservation order, bounded
injected timestamp, actual attempt id, handle, permit, dialer call, and accept
when acceptance occurs. G16 emits only independent ordinal labels and redacted
outcomes. Equality of permit and `DialContext` counts is checked separately for
selected-path and root/no-path fallback, hostname retry, IPv4 retry, IPv6 retry, and the
canceled-context call. The AST inventory and private/public split are mandatory
PASS cases, not supporting diagnostics.

## G10, G11, And G16 Evidence Contract

| Gate | Deterministic PASS | Deterministic FAIL |
| --- | --- | --- |
| `EEBUS-G10` | Executed startup/runtime integration behavior restores each clone-instance conflict, wrong-host binding, missing host key/anchor, older manifest generation, older control epoch, and durability-unknown fixture through the production composition; observed effects show zero trust registrations and cannot reach `PAIRED_TRUSTED` before or after restart; copied-current and inactive-parent repair publish a fresh lineage with every inherited trusted association inactive and tombstoned. R2 privately binds durable reservation and launch order to actual exact-context `DialContext` and fake-peer accept observations, with zero calls for pre-launch denial, publication failure, backoff, quarantine, and terminal hold. | Any copied/restored/rolled-back case reaches or reloads `PAIRED_TRUSTED`, invokes `RegisterRemoteSKI`, selects a lower manifest, conflates the required reasons, accepts a same-number/different-digest branch, repairs without complete durable deactivation and tombstones, relies only on a helper-returned decision, reaches a dial before durable reservation and launch permit, bypasses the fresh IPv6 lease, or treats callback injection as pre-dial evidence. |
| `EEBUS-G11` | Executed integration behavior drives the real pairing callback on the SHIP path through the exact vector: counts `0,1,2,3,4`, delays `0s,3s,6s,10s,0s`, the specified durable checkpoint and monotonic restart arm, no early retry, and terminal `ADMIN_HOLD` at the fourth failure; source-constant boundary cases stay within count, retention, exponent, and duration bounds. R2 privately binds reservation, handle, launch authorization, exact context, `DialContext`, and fake-peer observations across selected-path and root/no-path fallback, hostname/IPv4/IPv6 retry, crash recovery, delayed callback, discovery storm, abort/panic, and revocation races. | The real callback bypasses failure recording or checkpointing, ordinary restart clears or reduces state, unresolved reservation restart clears without one synthetic failure charge, a wall-clock change shortens delay, a retry occurs before durable `RETRY_READY`, an increment occurs outside matching terminal or explicit synthetic-failure linearization, the ceiling admits another handshake/reconnect, an active record is evicted, quarantine restores trust, permit count differs from `DialContext` count outside the explicit process-termination gap, a canceled-context call uses another context, or injected callbacks pass without dial/accept observations. |
| `EEBUS-G16` | Publishable integration artifacts contain only repository/branch/commit/issue metadata, tool versions, redacted command names, independent per-run ordinal labels, stable outcome/reason/state enums, bounded counts/durations, and PASS/FAIL. The private input/store root may contain generated synthetic SKI, certificate, endpoint, IP, and path values, but is never collected. Canary scans over captured callbacks, effects, logs, errors, recovered panic text, stdout/stderr, artifacts, snapshots, diffs, evidence, and the public output root find none of those values or representations. R2 publishes only redacted reservation/launch ordering and ordinal attempt labels bound to actual call/accept observations. | Any PEM, key, token, full fingerprint, raw/encoded/hashed/truncated SKI or SHIP ID, IP/MAC/serial, local identity, stable peer id/digest, pairing history, private filename, endpoint/path/context value, actual attempt id, or fork-internal type escapes the private root; the frozen API diff changes; scan input omits an output surface; private fixture/store bytes are published as scan output; a residual direct `Dial` or extra `DialContext` remains; or callback-only evidence is accepted without the reservation/launch/dial/accept binding. |

Only executed integration behavior from the production-composed lifecycle
supplies G10, G11, or G16 evidence. A result is rejected because caller
assertions and helper transcripts are not evidence. The collector derives
registration, reconnect, callback, disconnect, unregister, checkpoint,
restart, and terminal-state fields from observed effects and coordinator state;
a test caller cannot submit those fields as claimed booleans. Helper-only
transcripts may diagnose a failure but cannot produce a PASS row.

Each G10, G11, and G16 PASS row independently requires the same privately
observed attempt-bound chain: durable reservation order, handle return, durable
launch authorization, single-use permit, exact-context `DialContext`, and
fake-peer accept when the peer accepts. Callback injection is not pre-dial
evidence and cannot satisfy any one of the three rows. Public output replaces
the actual attempt id and private values with independent ordinal labels.

The compact public artifact identifies `MSP-04C`, exact commit and commands,
marks topology and credentials `not_applicable_synthetic`, marks temporary
paths `redacted`, and includes one PASS/FAIL row per required case. Raw store,
anchor, admin frames, transcripts, private generated inputs, and fixture
internals are never published. Case ordering and output bytes are independent of scheduler, map/directory
order, locale, wall clock, and failure wording.

## MSP-045 Entry Contract

The locked [MSP-045 row][freeze-plan-row] is an interface freeze after the M4
R2 correction, not permission to start downstream platform or consumer work.
MSP-045 must not start until the ship-go fork, spine-go fork, eebus-go fork,
and eebusreg adoption stages have all merged in that order; every applicable
R2 evidence field is populated; executed G10, G11, and G16 artifacts pass; and
a bounded architecture closure review returns `PASS` or
`PASS_WITH_CARRIED_EVIDENCE`. Carried evidence is limited to the explicit
SSH-only provider-attestation limitation. A dependency fork, module graph,
pre-dial runtime composition, reservation, revocation race, or gate failure
cannot be carried.

| Boundary | MSP-045 decision |
| --- | --- |
| `entry_precondition` | `four_repo_stages_merged+predial_evidence_bound+closure_pass` |
| `required_repo_stages` | `ship_go_fork+spine_go_fork+eebus_go_fork+eebusreg_adoption` |
| `closure_verdict` | `PASS_or_SSH_ONLY_CARRIED` |
| `carried_evidence` | `ssh_only_provider_attestation` |
| `freeze_scope` | `coordinator_ownership+combined_fsm+read_only_trust_admin_projection` |
| `platform_providers` | `deferred` |
| `consumers` | `deferred` |
| `post_freeze_change` | `explicit_contract_migration` |

MSP-045 may then freeze only coordinator ownership, the combined
MSP-04B/MSP-04C state machines, and the read-only trust/admin projection that
later consumers can use without ad hoc security decisions. A later change to
those frozen semantics requires explicit contract migration. MSP-045 does not
implement or freeze any dependency fork or a platform provider. It does not
implement a gateway, MCP, Portal, Home Assistant, or other consumer. Fork
maintenance, provider backends, and platform attestations remain separate
conformance work; consumer implementation remains in its downstream milestone
and repository.

## Required Tests And Exclusions

Focused code acceptance MUST cover every valid cross-product, precedence row,
and allowed transition; clone versus host mismatch; manifest versus control
rollback; exact pending-descriptor fields and same-number branch conflicts;
`commit_not_published` clear failure and crash; restart; complete inherited-trust
deactivation/tombstones; revocation authentication, exact binding, replay,
conflict, one-writer races, active `DisconnectSKI`, and
`UnregisterRemoteSKI`; startup-before-listener classification; coordinator
authorization of every registration and reconnect; the real pairing callback
on the SHIP path; exact backoff vectors, terminal attempt-limit quarantine,
checkpoint, restart rearm; and every store/anchor outcome. G10/G11 integration
tests exercise production composition rather than helper-only decisions.
R2 acceptance also runs the complete pre-dial falsification matrix through the
actual fork call sites with the fake TLS endpoint, fake peer on the SHIP path,
injectable dialer, crashable reservation store, delayed callbacks, revocation
races, abort/expiry/panic boundaries, matching-revocation crash boundaries, and
`go test -race`. It proves zero `DialContext` calls for every pre-launch denied
state and publication failure, exact prepare/permit/call cardinality for every
selected-path and root/no-path and hostname/IPv4/IPv6 attempt, exact canceled-context
identity with zero network effect, restart synthetic failure charged once,
stale-handle/callback denial, and one coordinated-journal terminal transition.
The ship-go AST/source inventory proves zero residual direct `Dial`, exactly one
direct `DialContext` in `gatedDialContext`, and preserved root fallback.
Public API and G16 scanners run over successes, failures, callbacks, effects,
logs, errors, recovered panics, stdout/stderr, fuzz output, artifacts, golden
diffs, evidence, test names, and the public output root while the private
input/store root stays isolated and deletion-verified. Full race-enabled source
CI and docs CI must pass at exact heads.

MSP-04C does not define a portable key, remote administration, automatic
re-trust, tombstone deletion, trust-preserving backup restore, protocol fact,
consumer behavior, or stable representation. Live hardware is not required
for G10/G11/G16; if an additional smoke run is performed, access remains
SSH-only and its redacted result is supporting evidence only.

[code-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/28
[corrective-docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/26
[corrective-source-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/30
[r2-docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/28
[r2-closure-docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/30
[gate-contract]: https://github.com/Project-Helianthus/helianthus-execution-plans/blob/f5c095935f8a8a67a7873ff349ddaff86eb41994/multi-runtime-semantic-platform.locked/93-eebus-transport-gate-v0.md#case-matrix
[meta-issue]: https://github.com/Project-Helianthus/helianthus-execution-plans/issues/58
[freeze-plan-row]: https://github.com/Project-Helianthus/helianthus-execution-plans/blob/f5c095935f8a8a67a7873ff349ddaff86eb41994/multi-runtime-semantic-platform.locked/92-m0-issue-matrix.yaml#L571-L589
[plan-row]: https://github.com/Project-Helianthus/helianthus-execution-plans/blob/f5c095935f8a8a67a7873ff349ddaff86eb41994/multi-runtime-semantic-platform.locked/92-m0-issue-matrix.yaml#L551-L570
[store-contract]: msp-04a-persistent-store.md
[trust-contract]: msp-04b-first-trust-admin-local.md
