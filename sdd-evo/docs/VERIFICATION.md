# Tatsächliche lokale Verifikation

**Ausgeführt:** Standardbibliothek-Unitchecks und CLI des Konsistenzdemonstrators. **Nicht ausgeführt:** Public-Export-App, Agentenworkflow, authentifizierte CI, Release oder Benchmark.

Zeit: `2026-10-27T10:30:15.057415+00:00`; Python `3.13.5`, `Linux/aarch64`.

Ergebnis: **33 Tests erfolgreich**, Unit-Test-Exitcode 0; positive CLI 0; stale CLI erwartungsgemäß 3.

Die Suite prüft u. a. Spec-/Code-/Test-/Integrationsdrift, Environment/Config/Command-/Policywechsel, stale Generation, fehlende/übersprungene/unvollständige Checks, Oracle-/Scopemutation, Identitätsmismatch, fehlende Deliverables, Taskcheckbox ohne Receipt, Review, Terminalbindung, Unknown-Effekte, begrenzte Repairs und zulässige Alternativen. Jeder Gateaufruf prüft außerdem Eingabereinheit und `released: false`.

**Wichtig:** Die PASS-Fixtures wurden synthetisch erstellt. Ihr erfolgreicher Konsistenzcheck ist keine Attestation ausgeführter Anwendungstests. Gleichnamige gefälschte Identitäten werden nicht authentifiziert; nur Abweichungen vom extern vorgegebenen Fixturekontext erkannt. Repairzähler sind modelliert, nicht geschützt persistiert. Kein TOCTOU-/Sandbox-/Recovery-Enforcement.

Reproduzieren: `python3 scripts/verify_package.py` im Paketverzeichnis. Der Runner schreibt diese Datei und [verification-results.json](verification-results.json) mit tatsächlich erfassten Ausgaben und SHA-256 der Code-/Fixtureinputs neu. Dokumentations-/Resultdateien sind nicht Teil dieser Inputidentität; keine rekursive Evidencehashbildung.

## `python3 -m unittest discover -s tests -v`

Exitcode: `0`

```text
test_all_input_versions_invalidate (test_sdd_gate.GateTests.test_all_input_versions_invalidate) ... ok
test_authorized_spec_still_requires_fresh_evidence (test_sdd_gate.GateTests.test_authorized_spec_still_requires_fresh_evidence) ... ok
test_blocked_cannot_accept (test_sdd_gate.GateTests.test_blocked_cannot_accept) ... ok
test_cli_positive_and_negative (test_sdd_gate.GateTests.test_cli_positive_and_negative) ... ok
test_deletion_out_of_scope (test_sdd_gate.GateTests.test_deletion_out_of_scope) ... ok
test_duplicate_check (test_sdd_gate.GateTests.test_duplicate_check) ... ok
test_duplicate_json_keys_reject (test_sdd_gate.GateTests.test_duplicate_json_keys_reject) ... ok
test_empty_discovery (test_sdd_gate.GateTests.test_empty_discovery) ... ok
test_identity_mismatch_not_authentication (test_sdd_gate.GateTests.test_identity_mismatch_not_authentication) ... ok
test_incomplete_discovery (test_sdd_gate.GateTests.test_incomplete_discovery) ... ok
test_invalid_phase (test_sdd_gate.GateTests.test_invalid_phase) ... ok
test_missing_check (test_sdd_gate.GateTests.test_missing_check) ... ok
test_missing_deliverable (test_sdd_gate.GateTests.test_missing_deliverable) ... ok
test_no_progress_and_unknown_budget (test_sdd_gate.GateTests.test_no_progress_and_unknown_budget) ... ok
test_old_worker_generation (test_sdd_gate.GateTests.test_old_worker_generation) ... ok
test_oracle_mutation_with_reforged_bindings (test_sdd_gate.GateTests.test_oracle_mutation_with_reforged_bindings) ... ok
test_out_of_scope (test_sdd_gate.GateTests.test_out_of_scope) ... ok
test_path_escape (test_sdd_gate.GateTests.test_path_escape) ... ok
test_raw_whitespace_change_is_not_normalized (test_sdd_gate.GateTests.test_raw_whitespace_change_is_not_normalized) ... ok
test_repair_budget_bound (test_sdd_gate.GateTests.test_repair_budget_bound) ... ok
test_required_checks_cannot_be_removed (test_sdd_gate.GateTests.test_required_checks_cannot_be_removed) ... ok
test_review_missing (test_sdd_gate.GateTests.test_review_missing) ... ok
test_scope_mutation (test_sdd_gate.GateTests.test_scope_mutation) ... ok
test_stale_code (test_sdd_gate.GateTests.test_stale_code) ... ok
test_stale_developer_tests (test_sdd_gate.GateTests.test_stale_developer_tests) ... ok
test_stale_integration (test_sdd_gate.GateTests.test_stale_integration) ... ok
test_stale_spec (test_sdd_gate.GateTests.test_stale_spec) ... ok
test_task_checkbox_not_evidence (test_sdd_gate.GateTests.test_task_checkbox_not_evidence) ... ok
test_terminal_mutation (test_sdd_gate.GateTests.test_terminal_mutation) ... ok
test_unknown_effect (test_sdd_gate.GateTests.test_unknown_effect) ... ok
test_unknown_fail_skip_error (test_sdd_gate.GateTests.test_unknown_fail_skip_error) ... ok
test_valid_alternative_with_fresh_evidence (test_sdd_gate.GateTests.test_valid_alternative_with_fresh_evidence) ... ok
test_valid_not_released (test_sdd_gate.GateTests.test_valid_not_released) ... ok

----------------------------------------------------------------------
Ran 33 tests in 0.154s

OK
```

## `python3 scripts/sdd_gate.py --demo --approved fixtures/approved.json --current fixtures/current.json --evidence fixtures/evidence.json`

Exitcode: `0`

```text
{"assurance": "synthetic-consistency-only", "eligible": true, "reason_codes": [], "released": false, "state": "ACCEPTED"}
```

## `python3 scripts/sdd_gate.py --demo --approved fixtures/approved.json --current fixtures/stale-current.json --evidence fixtures/evidence.json`

Exitcode: `3`

```text
{"assurance": "synthetic-consistency-only", "eligible": false, "reason_codes": ["STALE_EVIDENCE", "TERMINAL_STATE_MISMATCH"], "released": false, "state": "BLOCKED"}
```
