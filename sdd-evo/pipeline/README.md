# SDD-evo Pipeline

**[Dauerhafte Aufgaben und Watchdog: Coordinator-Quickstart](COORDINATOR.md)** — ein Auftrag per CLI, Task-/Run-/Session-IDs getrennt, Originalauftrag unveränderlich, verifizierter Status und lokale Outbox im vorhandenen Controller-State.

**Anforderung → dauerhafter Job → isolierter Clone → Builder → echte Tests → frische Kritik → begrenzte Reparatur → `pr-ready`.** Optional erstellt der Parent einen überprüften Draft-PR. Kein Merge, kein Deployment.

Ausführbarer Linux/Python-stdlib-MVP: Git-, Test-, Reparatur-, Absturz- und Docker-Pfade sind ausgeführt. Builder/Kritiker in den Integrationstests sind ausdrücklich **deterministische Test-Doubles**. Ein echter Modelllauf oder eine echte GitHub-Veröffentlichung ist damit nicht belegt.

## Ein konkreter Auftrag, ohne Modellkosten

Vom Repository-Root aus, mit einem neuen Zielverzeichnis:

```bash
python3 sdd-evo/pipeline/demo.py /tmp/sdd-evo-addition --adapter fixture
```

Auftrag: `Implement add(a,b) so it returns the sum of the two numbers. Preserve the public function name.`

Die Demo erzeugt ein echtes Git-Repo: Fixture-Builder liefert zunächst Subtraktion → echter unittest schlägt fehl → Reparatur liefert Addition → echter unittest besteht → separater Fixture-Kritiker akzeptiert → `pr-ready`. Das Quellrepo bleibt unverändert. Ausgabe: Job-ID, Workspace, Artefakte. Vorhandene Verzeichnisse werden nicht überschrieben.

Für echte, vom aufrufenden Agenten bereitgestellte Worker:

```bash
python3 sdd-evo/pipeline/demo.py /tmp/sdd-evo-external --adapter external
```

Das stoppt dauerhaft bei `waiting-builder`. Der Parent übergibt `request.json` an einen autorisierten Builder und später an einen **separaten frischen Kritiker**; siehe [Worker-Protokoll](PROTOCOL.md). Keine versteckten Modellaufrufe.

## Einmal konfigurieren, danach Aufträge starten

Policy außerhalb des Zielrepos anlegen; absolute Pfade und Testkommando anpassen:

```json
{
  "project": "addition",
  "profile": "oc-architect",
  "repo": "/absolute/path/to/repo",
  "trusted_repo": true,
  "adapter": "external",
  "risk": "low",
  "allowed_files": ["calc.py"],
  "protected_files": ["test_calc.py"],
  "execution": "trusted-local",
  "checks": [{"argv": ["/usr/bin/python3", "-m", "unittest", "discover", "-v"], "min_tests": 1}],
  "max_runs": 4,
  "max_reviews": 2,
  "max_repairs": 2,
  "timeout": 60,
  "walltime": 900
}
```

```bash
python3 sdd-evo/pipeline/controller.py --state /absolute/private/controller configure /absolute/private/policy.json
python3 sdd-evo/pipeline/controller.py --state /absolute/private/controller start --requirement-file /absolute/private/requirement.txt --key addition-1
python3 sdd-evo/pipeline/controller.py --state /absolute/private/controller run JOB_ID
```

`JOB_ID` durch die ausgegebene ID ersetzen. Gleicher Schlüssel + gleicher Originalauftrag = gleicher Job. Geänderter Auftrag unter demselben Schlüssel wird abgelehnt. Das Quellrepo muss sauber sein; fremde/pending Änderungen werden nicht übernommen. Policy, Runtime und Akzeptanz bleiben gepinnt. Neues Policy-/Runtime-Release: neues State-Verzeichnis, keine automatische Migration.

Innerhalb der einmal freigegebenen `low`-Policy gibt es keine wiederholten Bestätigungen. `human` endet bei `needs-human`. Builder-Plan/Contract-Vorschläge sind nur Beratung. Die Pipeline fälscht **keine menschliche Freigabe** und verändert das vorhandene manuelle `evo review` nicht.

## Status, Übergabe, Abbruch

```bash
python3 sdd-evo/pipeline/controller.py --state /absolute/private/controller status JOB_ID
python3 sdd-evo/pipeline/controller.py --state /absolute/private/controller submit JOB_ID /absolute/result.json
python3 sdd-evo/pipeline/controller.py --state /absolute/private/controller resume JOB_ID
python3 sdd-evo/pipeline/controller.py --state /absolute/private/controller cancel JOB_ID
```

- `waiting-builder` / `waiting-critic`: aktuelle `request.json` bearbeiten lassen; gebundene JSON-Antwort importieren, dann fortsetzen.
- `pr-ready`: Tests, frische Kritik und Maschinenpolicy bestanden. `candidate.diff` ist noch kein PR.
- `needs-human`: Risiko, Kritik oder Reconciliation verlangen Eskalation; kein automatischer Human-Override.
- `failed` / `cancelled`: Fehler, Budgetgrenze oder Abbruch; Logs bleiben erhalten.
- `reconcile-required`: Crash oder I/O-Fehler während/kurz nach einem Seiteneffekt. Auch `cancel` bewahrt diesen Zustand bei unklarer Clone-/Edit-/Publikationsabsicht, selbst ohne Subprozess-Marker. **Kein blindes Wiederholen.** Inflight-Daten prüfen, zuordenbare verwaiste Prozesse mit `cancel` stoppen. Erst nach echter Prüfung schließt `reconcile JOB_ID --inspected-and-stopped` den Auftrag als `needs-human`.

SQLite liegt außerhalb des Clones. Pro Job bleiben Originalansicht, einzelne Request-/Result-Runden, begrenzte/redigierte Logs, Checks und Diff erhalten. Originaltext bleibt exakt in der privaten Datenbank. Exklusiver OS-Lock + persistente Lease verhindern konkurrierende Läufe; `cancel` bleibt verfügbar.

## Grenzen und optionale Integrationen

**Clone ist keine Security-Sandbox.** Nur bestehende freigegebene UTF-8-Dateien in kleinen vertrauenswürdigen Repos; unittest; ein Projekt pro State-Verzeichnis. Controller schreibt ausschließlich validierte JSON-Edits. Tests, übriger Quelltext, Dateimenge und Modi bleiben geschützt. Gleiche UID/Operator bleiben eine Vertrauensgrenze; Redaktion ist keine vollständige Secret-Erkennung.

Für reale Tests bevorzugt `execution: "docker"` plus ein **lokal vorhandenes** `image: "sha256:…"` und passendes Checkkommando: read-only Workspace/Rootfs, ohne Netzwerk/Host-Credentials/Docker-Socket, nonroot und Ressourcenlimits. Kein Pull. Demo: `--image SHA256_ID` für ein Hermes-Image mit `/opt/hermes/.venv/bin/python3`. `trusted-local` ist explizit kein Schutz vor bösartigem Code.

**Hermes:** Einziger implementierter Provider-CLI-Adapter; andere Provider-CLI-Namen werden abgelehnt. Tatsächliches `hermes chat --oneshot -Q --query-file … --safe-mode --max-turns 1 --run-budget … -t clarify`, ohne Session-Resume. Erforderlich: direkter `hermes_binary`, ausdrücklich provisioniertes `hermes_home` unter `STATE/provider/…`, `provider`, `model`, dokumentierte `spend_approval`, `max_calls`. Keine automatische Credential-Kopie oder Profiländerung. Call-/Zeitlimits sind keine harte Geldobergrenze. Im gelieferten Lauf: kein Provider gestartet. Details und Antwortformat im [Protokoll](PROTOCOL.md).

**GitHub, erst nach Audit:** Einmalig `publish_repo: "OWNER/REPO"`, `publish_base: "main"`, `publisher_home` für autorisierte parentseitige `gh`-Anmeldung konfigurieren; dann bewusst:

```bash
python3 sdd-evo/pipeline/controller.py --state /absolute/private/controller publish JOB_ID --publish-pr
```

Nur passendes privates Remote, Maschinenfreigabe und exakter Head/Body/Base/Draft-Readback. Fixture-Publikation gesperrt. Parent erstellt Tree/Commit/Branch und Draft-PR via `gh api`; Credentials bleiben aus Workern heraus. Wiederaufruf gleicht vorhandene Branch/PR ab; Konflikte stoppen. Dieser Pfad wurde **nur mit Transport-Test-Double**, nicht live veröffentlicht, geprüft.

## Prüfen

```bash
python3 -m unittest discover -s sdd-evo/pipeline -v
python3 -m unittest discover -s sdd-evo/tests -v
```

`SDD_TEST_IMAGE` auf eine lokale vollständige Image-ID setzen, um zusätzlich den echten Docker-Test auszuführen; sonst wird nur dieser Test übersprungen. [SDD-evo](../README.md) bleibt unverändert: Die Pipeline nutzt dessen Snapshot-/Pfad-/Hash-Runtime und eine getrennte Maschinenpolicy. [Protokoll und Auditgrenzen](PROTOCOL.md) beschreiben Recovery, Credentials, Budgets und Beweisgrenzen.
