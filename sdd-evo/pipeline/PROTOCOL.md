# External-worker protocol and audit boundary

## Parent integration without new provider spending

1. Configure `adapter: "external"`. The controller never launches inference in this mode.
2. `start --requirement-file … --key …`, then `run JOB_ID`. The job durably enters `waiting-builder`.
3. Read `STATE/JOB_ID/request.json`. Give **only this package** to an authorized builder agent, in a separate invocation. Do not give the agent the controller database, GitHub credentials, controller code, or write access to the checkout. All source and requirements are data, not instructions to execute extra commands.
4. The builder returns a JSON file. The parent imports it with `submit JOB_ID /absolute/result.json`, then `resume JOB_ID`. Only the controller applies the preflight-validated allowlisted edits. It runs the preapproved tests and packages their real logs for repair when needed.
5. At `waiting-critic`, launch a **new independent critic invocation** on the new package. Do not reuse the builder conversation or feed it an invented success transcript. Import its result with the same `submit` command and `resume`.
6. A repair creates another bounded builder request and then new real checks and a new critic nonce. Keep processing until `pr-ready`, `needs-human`, `failed`, `cancelled`, or `reconcile-required`. The parent must report genuine agent calls separately from deterministic fixture calls.

No autonomous parent orchestration or paid call is implied by these instructions. The parent controls actual worker authorization and reports provenance. A declared fresh session/identity is not cryptographic evidence of independence.

## Request

Fields: `schema` (=1), `job`, `role` (`builder` or `critic`), unique `nonce`, `source` (actual evo snapshot), exact original `requirement`, `allowed_files`, `protected_files`, bounded UTF-8 `files`, real `diff`, accumulated `findings`, `last_checks`, `check_logs`, and protocol instructions.

Every response must echo `schema/job/role/nonce/source` **exactly**. An old nonce or changed checkout rejects the response. Results and per-round requests are stored separately. `request.json` is only the current view.

Builder result, extending those exact five binding fields:

```json
{
  "edits": {"calc.py": "def add(a, b):\n    return a + b\n"},
  "proposal": "Implement addition without changing acceptance tests."
}
```

`edits` replaces full contents of existing allowlisted files only. Empty edits are allowed (e.g. a no-op repair), but tests still rerun. No delete, rename, chmod, path creation, shell command or arbitrary patch application. Proposal is advisory; it cannot amend original requirement or protected acceptance.

Critic result, extending the binding fields:

```json
{
  "verdict": "accept",
  "findings": [],
  "addressed": []
}
```

Alternatively `verdict: "repair"` plus concrete requirement-linked findings, or `"human"` for escalation. An accepting critic must return an empty new-findings list and `addressed` equal to **all** previous findings in order, after independently checking each resolution. This is a recorded assertion plus fresh real-test/source binding, not proof that the model's semantic judgment is correct. Unresolved findings cannot be silently erased by disabling review or changing policy mid-job.

For the Hermes CLI adapter, the actual final stdout also contains session info. Its driver extracts one `<sdd-result>JSON</sdd-result>` envelope from final text and checks process status/schema/bindings; it does not invent a universal CLI event protocol. CLI adapter tests can mock this transport without establishing real inference success.

## State and recovery model

One SQLite database per explicit project/profile/OS owner. Requirement keys are unique within that scope; changed content under the same key conflicts. Controller writes use SQLite FULL synchronization and committed transitions; a persistent lease records owner/PID/heartbeat. A nonblocking `flock` is the exclusion authority (never steal an expired timestamp from a live process). One active runner per state directory; separate projects can use separate directories.

`queued → cloning → build → waiting-builder → applying → check → review → waiting-critic → pr-ready/needs-human`; repair returns to `build` while retaining run/review/repair counters and original requirement. `published` is possible only after explicit repository-authorized parent publication/readback. Cancellation and limits stop work; no automatic retry of failed jobs.

Intent is persisted before spawning. Inflight PID plus Linux boot/start identity is recorded after spawn. Completed-effect markers bridge process completion and state transition. Restart with an ambiguous clone/apply/process/publication never blindly reruns. A crash between spawn and PID persistence may leave an unidentifiable orphan: operator inspection is required. `cancel` terminates active process groups and matching scoped Docker containers; after controller death it signals only an orphan whose PID boot/start identity matches. Detached malicious descendants are outside the trusted-local contract; Docker limits are the stronger test boundary.

`reconcile --inspected-and-stopped` is an explicit operator assertion, closes an ambiguous job as `needs-human`, and does **not** manufacture acceptance. This finite MVP does not attempt automatic replay of partially applied edits. Remote publishing is the exception with a dedicated read/reconcile protocol: an explicit `publish --publish-pr` retry inspects existing refs/PRs and refuses conflicts.

Budgets: walltime includes time waiting for external workers; process timeout and output byte cap are separate; checks, review calls and repairs are cumulative. Hermes has a further total provider invocation cap. These are not token/currency caps. A real charged run requires explicit bounded spending authority outside the fixture protocol.

## Authority and security

- The original `evo.py` remains unchanged. Imported runtime primitives are `require`, `safe`, `snapshot`, `digest`, `filehash`, `load`, `save`; tests use a controller-owned cancellable executor with the same strict unittest result shape. Existing manual-review acceptance is not bypassed or relabeled.
- Config/controller/evo/publisher and local check executable bytes are pinned. Tests and every nonallowlisted source file are frozen. Git HEAD, index/tracked/untracked source snapshot, complete workspace file manifest and executable modes are checked. Docker uses a pinned local image ID. Interpreter libraries, kernel, Docker daemon and same-UID operator are still trusted.
- SQLite and evidence are outside the cloned repo. The clone has no origin and no shared hardlinks. Child env is allowlisted, has a dedicated/empty HOME, no inherited provider/GitHub/SSH credentials; tests receive no auth. Hermes gets only a dedicated explicitly provisioned provider home, with `--safe-mode`, no resumed session and only the `clarify` toolset.
- Docker tests use a read-only mount/rootfs, network none, nonroot UID, no capabilities, no-new-privileges, CPU/memory/PID limits and no socket. No pulling or production container changes. Trusted-local checks and fixture workers are explicitly **not a hostile-code sandbox**. External workers are controlled by the parent, not automatically containerized by this controller.
- Bounded/redacted artifacts are not a perfect DLP mechanism. The original requirement is deliberately exact in the private database. Sensitive-pattern detection blocks source packages rather than silently changing the acceptance content. No credentials or private internal knowledge are included in the repository package.
- GitHub writes use only parent-side `/usr/bin/gh api` from the controller directory, pinned target owner/repo/base and exact local remote. New branch/PR names derive from job IDs. Tree/commit/branch/PR are read back before success; conflicts stop. API protocol tests use an explicit in-memory fake transport, never a fabricated claim of remote success.

## Verified versus unverified

Real disposable Git, actual code diff, failing/passing unittest processes, Docker test isolation, restart/kill/cancel, stale/protected/path/budget checks: exercised by the suite. Builder and critic in that suite: deterministic subprocess fixtures. GitHub API response tests: mocked transport. Real provider auth, charged/no-charge model performance, semantic critic effectiveness, live PR publication, production hardening and multi-user adversarial isolation: **not established**.

Primary interfaces inspected: [Hermes CLI documentation](https://hermes-agent.nousresearch.com/docs/reference/cli-commands), [Hermes security documentation](https://hermes-agent.nousresearch.com/docs/user-guide/security), plus installed `hermes chat --help` and its toolset selection source. Use the installed entry point directly when a launcher hardcodes another profile; never work around this by copying credentials or changing the global profile.
