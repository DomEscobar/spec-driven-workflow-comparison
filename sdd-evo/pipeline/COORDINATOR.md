# Dauerhafte Aufgaben statt Chat-Gedächtnis

Der Coordinator ergänzt **dieselbe `jobs.db` und denselben Controller-Lock** um Aufgaben,
versionierte Aufträge, Eingangsereignisse und eine lokale Outbox. Keine zweite Worker-Plattform.
`submit` speichert nur den Auftrag; `tick` ordnet einen Job zu und prüft Zustand/Evidenz;
`run` führt die vorhandene SDD-Pipeline aus. Alle Prozesse können danach enden.

**Lokaler, trusted-operator MVP.** Keine Telegram-Anbindung, kein GitHub-Listener,
kein installierter Scheduler, keine neuen Credentials und kein autonomer Modellaufruf
im External-Modus. `pr-ready` heißt nicht menschlich akzeptiert oder released.

## Sofort ausführbares Beispiel

Vom Repository-Root, mit einem noch nicht existierenden absoluten Verzeichnis:

```bash
python3 sdd-evo/pipeline/demo.py /tmp/sdd-task-demo --coordinator --adapter fixture
```

Echtes Git, tatsächlich fehlgeschlagener Test, Reparatur, bestandener Test und separate
**geskriptete** Kritik. Die Ausgabe enthält verschiedene `task_id` und Job-`id`,
`local_notified: true`, `accepted: false`, `released: false`. Die Zustellung ist eine
nachgelesene JSON-Datei unter `/tmp/sdd-task-demo/local-delivery`, keine Telegram-Nachricht.
Für echte Parent-Worker stattdessen `--adapter external` und ein neues Verzeichnis:
der Job wartet dann auf den Builder. [Exaktes Worker-Protokoll](PROTOCOL.md).

## Einmalige Einrichtung für das eigene Repo

Zuerst die bestehende [Pipeline-Policy](README.md)
mit `controller.py configure` anlegen. Keine bestehende Runtime umkonfigurieren.
Danach eine explizite Coordinator-Policy, z. B. `/absolute/private/tasks.json`:

```json
{
  "tenant": "oc-architect",
  "repo": "/absolute/path/to/repo",
  "stall_seconds": 300,
  "routes": [{
    "source": "local",
    "thread": "approved-local-thread",
    "authors": ["operator"],
    "destination": {"kind": "local", "path": "/absolute/private/task-delivery"}
  }]
}
```

`tenant` muss dem Pipeline-Profil entsprechen, `repo` exakt dem konfigurierten Repo.
Zielverzeichnis und Thread sind **explizite Operator-Freigaben**, keine aus Chattext
abgeleiteten IDs. Lokales Ziel muss außerhalb des Repos, im Besitz der aktuellen UID
und nicht gruppen-/weltbeschreibbar sein. Keine Symlinks. State außerhalb des Repos.

```bash
python3 sdd-evo/pipeline/coordinator.py --state /absolute/private/controller configure /absolute/private/tasks.json
python3 sdd-evo/pipeline/coordinator.py --state /absolute/private/controller submit 'Implement add(a,b) as addition; preserve its name.' --thread approved-local-thread --author operator --session my-session-1 --event my-request-1
```

Die zweite Zeile ist der normale **einzelne Anforderungsaufruf**, ohne Worker-Wartezeit.
Ausgegebene Task-ID übernehmen; Event-ID bei Retry unverändert lassen:

```bash
python3 sdd-evo/pipeline/coordinator.py --state /absolute/private/controller tick
python3 sdd-evo/pipeline/coordinator.py --state /absolute/private/controller run TASK_ID
python3 sdd-evo/pipeline/coordinator.py --state /absolute/private/controller status TASK_ID
python3 sdd-evo/pipeline/coordinator.py --state /absolute/private/controller deliver
python3 sdd-evo/pipeline/coordinator.py --state /absolute/private/controller outbox
```

`run` ist bewusst der separate blockierende Worker-Aufruf. External-Responses werden
mit `controller.py submit RUN_ID result.json` importiert; danach wieder Coordinator
`run TASK_ID`. Keine Abkürzung um Kritik oder geschützte Tests herum. Bei laufendem
Controller antworten konkurrierende Commands mit `CONTROLLER_BUSY`; mit derselben
Event-ID erneut versuchen. `controller cancel RUN_ID` bleibt der unabhängige Abbruchweg.
`status` führt einen deterministischen Tick aus (kann einen queued Job zuordnen), nie
Modellinferenz. `last_verified` bezeichnet die letzte erfolgreiche lokale Guard-Prüfung,
nicht semantische Vollständigkeit. `progress.checks` kommt aus echten Controller-Checks.

## Ingress, Revision und Grenzen

`ingest /absolute/event.json` akzeptiert JSON nach diesem vollständigen lokalen Beispiel:

```json
{
  "event_id": "request-2",
  "source": "local",
  "thread": "approved-local-thread",
  "author": "operator",
  "session_id": "new-session",
  "tenant": "oc-architect",
  "repo": "/absolute/path/to/repo",
  "kind": "revise",
  "task_id": "TASK_ID",
  "objective": "Revised explicitly accepted objective.",
  "provenance": {"verification": "local-operator", "uid": 1000}
}
```

UID durch die tatsächliche Operator-UID ersetzen. Das ist **lokale Operator-Attribution**,
keine kryptographische Nutzeridentität. `submit` erzeugt die passende UID selbst.
Entfernte `source: telegram/github` werden momentan abgelehnt, auch mit `verified: true`.
Der JSON-Inhalt ist Daten, kein Prompt für Routing oder Shell-Befehle.

- `kind: submit` erzeugt eine Task-ID; optional `evidence_requirement` als Beschreibung,
  niemals als Änderung der geschützten Akzeptanztests. `kind: status` fragt eine bekannte
  Aufgabe ab. Ohne Task-ID muss genau eine Aufgabe im bekannten Thread existieren;
  mehrere Aufgaben verlangen eine explizite ID. Keine semantische Raterei oder LLM nötig.
- Dedupe nach Source/Event-ID; gleicher Inhalt liefert dieselbe Aufgabe, abweichender
  Inhalt kollidiert. Sessions sind Attribution, keine Aufgaben-/Run-Identität.
- `revise` darf nur der ursprüngliche autorisierte Task-Owner im gleichen Thread.
  Der alte Originalauftrag bleibt unverändert mit Autor, Version, Event und Session.
  Die angenommene Revision setzt atomar einen Cancel-Wunsch für den alten Job.
  Erst nach sicherem Stop wird eine neue Version mit neuem Run aktiv.
- Ambige Inflight-/Completed-Effects verhindern Ersatz. Erst tatsächliches
  `cancel`, `resume` (exponiert `reconcile-required`) und nach Inspektion
  `reconcile --inspected-and-stopped` erlauben den nächsten Tick. Keine Timestamp-Tricks.
- Mehrere Tasks erhalten separate Clones; ein State-Lock serialisiert Ausführung.
  Keine parallelen Main-Checkout-Edits, kein Cross-Tenant-Routing.

## Watchdog und Zustellung

Ein periodisch **extern aufgerufener** `tick` prüft Runtime-, Source- und Receipt-Pins,
Cancel-/Walltime-Grenzen, fehlenden Worker, ambige Effekte und unreviewte Ergebnisse.
Er erzeugt deduplizierte Zustandsalarme statt Agenten-Prompts. `deliver` prüft die
Evidenz erneut und stellt nur den aktuellsten Status je Aufgabe lokal zu; überholte
Outbox-Einträge bleiben als unzugestellt auditierbar. Kein veralteter Erfolgsalarm
nach erkannter Source-Manipulation. Lokale Zustellung: voll geschriebene/fsync-Datei,
atomarer No-Clobber-Link, exaktes Readback, dann DB-Acknowledgement. Ein Crash zwischen
Datei und Ack wird anhand derselben Notification-ID ohne Doppeldatei aufgeholt.
`notified` bedeutet ausschließlich **aktuell lokal zugestellt**, nicht vom Nutzer gelesen.

Ein Operator kann genau `tick` und `deliver` in einen bereits genehmigten Scheduler
eintragen; hier wird **kein** Cron/Systemd/Hermes-Gateway verändert. Ohne Scheduler
oder expliziten Aufruf gibt es keine proaktive Aktivität während ausgeschaltetem Prozess.
Budgetablauf wird sichtbar blockiert, nicht still durch neuen Run umgangen. Keine
automatische Reparatur eigener Prompts oder Policies. Crash-Recovery nutzt die bestehenden
Controller-Markierungen; unklare Seiteneffekte erfordern Inspektion.

## Späterer Adaptervertrag, keine heimliche Installation

Vor echtem Telegram-/GitHub-Ingress muss ein ausdrücklich freigegebener Adapter außerhalb
des Workers Transportauthentizität prüfen (Telegram-Webhook/Account oder GitHub-Signatur),
Original-Event-ID, exakten Chat/Thread bzw. Repository/Issue und Autor binden sowie die
Operator-Allowlist prüfen. Er muss verifizierte Provenienz auditierbar liefern und die
hier bewusst gesperrten Remote-Sources implementieren/testen. Ein vom Event behauptetes
`verified` reicht nicht. Zielidentitäten niemals aus Modelltext ableiten. Remote-Outbox
braucht separat genehmigte Credentials, Transport-Receipt, Retry/Dedupe und exaktes
Readback; lokale Zustellung darf nicht als Remote-Ack umetikettiert werden.

Die aktuelle Parent-Agent-Rückmeldung kann nativ im bestehenden Chat erfolgen; sie ist
kein Nachweis eines dauerhaften Telegram-Dienstes. Ebenso bleibt `published` der vorhandenen
Pipeline nur ein Draft-PR, niemals Abnahme, Merge oder Release. `accepted` und `released`
bleiben in diesem Ledger bewusst false; es gibt keinen Worker- oder Ingress-Override.
Menschliche Abnahme erfolgt über den vorhandenen separaten Review-Workflow, nicht durch
Selbstdeklaration des Builders. Same-UID-State-Manipulation ist keine abgewehrte Bedrohung.

## Prüfung

```bash
python3 -m unittest discover -s sdd-evo/pipeline -v
python3 -m unittest discover -s sdd-evo/tests -v
python3 -m unittest discover -s scripts -v
python3 scripts/check_docs.py
```

Tests umfassen echte Git-/Testprozesse, separate CLI-Prozesse, Prozessende vor DB-Commit,
Job-Link-Crash-Recovery, Outbox-Replay, Versionswechsel mit Cancel/Reconcile, Dedupe,
Thread-/Tenant-/Owner-Grenzen, stale evidence und fehlende Kritik. Modellqualität und
Remote-Zustellung sind damit ausdrücklich nicht bewiesen.
