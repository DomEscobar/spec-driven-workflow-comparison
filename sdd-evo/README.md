# SDD-evo — bauen, wirklich prüfen, bewusst abschließen

**Ein lokaler Workflow für Coding-Agenten:** Auftrag festhalten → Code bauen → echte Tests ausführen → manuellen Review dokumentieren → genau diesen Stand abschließen. Änderungen machen alte Nachweise ungültig.

**Jetzt implementiert:** Python-CLI, echte Subprocess-Tests, versionsgebundene lokale Belege und sechs portable Agent-Skills. **MVP, kein geschütztes CI-Gate:** Builder und Runner haben denselben Benutzer; das ist keine authentifizierte Attestation. `finish` bedeutet lokale Abnahme, niemals Deployment oder Release.

## In einer Minute ausprobieren

Voraussetzungen: POSIX-System (Linux/macOS), Python 3.10+, Git. Keine Pakete, Modelle, API-Schlüssel oder Netzwerkaufrufe. Vom Repository-Hauptverzeichnis:

```sh
python3 sdd-evo/examples/run_e2e.py
```

Das Beispiel erstellt ein temporäres echtes Git-Repo mit einer kaputten Additionsfunktion und einem echten unittest. Es führt die CLI aus: Testfehler → Codefix → bestandener Test → exemplarischer lokaler Review → `ACCEPTED_LOCAL` → erneute Codeänderung → `STALE_EVIDENCE`. Das temporäre Repo wird entfernt. Der Beispielreview ist keine unabhängige menschliche Freigabe.

## Mit deinem Coding-Agenten

Die Skills liegen unter `.agents/skills/evo-start`, `evo-build`, `evo-check`, `evo-change`, `evo-finish`, `evo-critic` im Repository. [Installation und echte Codex-/Claude-Aufrufe](INTEGRATION.md).

- **start:** Nutzerziel, Anforderungen mit IDs, Nichtziele und vertrauenswürdige lokale Prüfkommandos festlegen.
- **build:** Der Agent implementiert echten Code. Die CLI selbst ruft kein LLM auf.
- **check:** Der Runner startet ausschließlich die akzeptierten argv-Kommandos, ohne Shell.
- **change:** Bewusst akzeptierte Auftrags-/Test-/Konfigurationsänderung mit Grund; alte Belege verfallen.
- **finish:** Frische Maschinenprüfung **und** expliziter manueller Review erforderlich.

Nicht „Test rot → Anforderung leichter machen“, sondern Fehler beheben oder mit konkretem Entscheidungsbedarf stoppen.

## Quickstart im eigenen Repo

Kopiere `sdd-evo/evo.py` nach `sdd-evo/evo.py` deines Ziel-Repos; für Agentennutzung zusätzlich die sechs Skill-Verzeichnisse nach `.agents/skills/`. Keine globalen Agenteneinstellungen ändern. Das Ziel braucht bereits einen Git-Commit. Ergänze `.sdd/` in seiner `.gitignore`; der Runner verweigert sonst die Arbeit. Ignoriere dort auch normale Build-/Cache-Ausgaben, **nicht** relevante Quelldateien.

Alle folgenden Befehle laufen am Ziel-Repo-Root:

```sh
python3 sdd-evo/evo.py init
```

Bearbeite die erzeugten Dateien, bevor du irgendetwas ausführst:

- `evo-contract.json`: `id`, `outcome`, `accepted_basis`, `requirements` (z. B. `R1`), `non_goals`, `checks`, `manual_review: true`. Alle `REPLACE`-Platzhalter ersetzen.
- `evo-config.json`: explizite lokale Command-Allowlist `checks`, absolute ausführbare Datei in `argv[0]`, `cwd`, `timeout`, `min_tests`, `protected_files`, `output_limit`, `max_runs`, `env`. Das Template erwartet `test_app.py` und startet `python -m unittest -v test_app`; **passe es an deine tatsächlichen Tests an**. Alle Abnahmetest-/Hilfsdateien explizit unter `protected_files` aufführen.

Der MVP unterstützt bewusst **nur Python-unittest-Textausgaben**: genau ein `Ran N tests` und finales `OK`, Mindestanzahl erfüllt, keine Skips/Expected-Failures. Pytest, Jest, beliebige JSON-PASS-Dateien und automatische Adaptererkennung sind nicht implementiert. Ein Kommando mit Exit 0 ohne diesen Testnachweis reicht nicht. Testprogramme können ihre Ausgabe fälschen; das ist keine neue Vertrauensgrenze.

Nach tatsächlicher Akzeptanz durch den Auftraggeber:

```sh
python3 sdd-evo/evo.py start --accept "owner/request-123"
# Jetzt mit Agent oder Editor implementieren; keine eingebaute Modell-API.
python3 sdd-evo/evo.py check
python3 sdd-evo/evo.py status
```

`VERIFIED` heißt: Maschinenprüfung frisch, manueller Review noch offen. Bei Fehlern: Logs lokal ansehen, Code reparieren, erneut `check`. Jeder Versuch verbraucht Budget, auch bei Fehler/Abbruch. Standard: fünf Versuche; keine automatische Endlosschleife. Bei fehlendem Fortschritt stoppen. Budget lässt sich durch `change` nicht erhöhen oder zurücksetzen.

### Manueller Review und Abschluss

Prüfe Ergebnis und Nichtziele fachlich; bei UI auch tatsächliche Bedienung/UX. Schreibe etwa `review.md` mit Reviewer, betroffenen Anforderungen, Beobachtungen und offenen Punkten. Der Runner bewertet die Qualität dieser Aussagen nicht. Er verlangt explizite lokale Dokumentation, keinen automatisch objektiven UX-Nachweis.

**Reviewnote vor dem letzten Check schreiben:** Neue/geänderte Quelldateien invalidieren die alte Identität.

```sh
python3 sdd-evo/evo.py check
python3 sdd-evo/evo.py review --by "actual-reviewer" --evidence review.md
python3 sdd-evo/evo.py finish
```

Nur Exit 0 und `ACCEPTED_LOCAL` bedeuten lokalen Abschluss. Fehlender Review blockiert. Kein Push, Merge, Deployment oder Release wird ausgeführt. `status` überprüft aktuelle Evidenz; vor dem ersten Check oder bei fehlenden Belegen meldet es `BLOCKED`, nicht „fertig“. CLI-Exitcodes: `0` erfolgreich, `3` blockiert, `2` ungültige Argumente. Jede JSON-Ausgabe enthält `released: false` und eine nächste Handlung.

### Explizites Amendment statt stiller Drift

Änderung erst mit dem zuständigen Owner besprechen: altes/neues Soll, Grund, Test-/Scopeauswirkung. Dann akzeptierte Änderungen an Vertrag, Referenzspec, geschützten Tests oder Config eintragen:

```sh
python3 sdd-evo/evo.py change --accept "owner/request-124" --reason "Accepted scope change and test impact"
python3 sdd-evo/evo.py check
```

Neue Contract-/Config-/Spec-/Test-Digests invalidieren Receipt, Review und Finish. Historie und kumulative Versuche bleiben in `.sdd/state.json`. Namen und Gründe sind lokale Zuschreibungen, keine unabhängige Autorisierung. Keine automatische Specmutation; kein Reset durch Start über einen laufenden Change.

## Optional: frischer Critic vor dem Abschluss

Für semantische Lücken trotz grüner Tests: Original-Nutzerbrief + Vertrag + exakte Quelle/Diff → frischer Critic → strukturierte Findings → Builder-Repair → finale Tests, Findings-Disposition und manueller Review. **Kein Modellaufruf durch die CLI, keine automatische Abnahme.**

Aktiviere `critique.enabled` mit autorisiertem `task_brief` und getrennten Review-/Repairbudgets vor `start` oder per explizitem Amendment. Dann `critique-prepare`, neue `$evo-critic`-/`/evo-critic`-Sitzung, `critique-import` und `critique-dispose`. Nach Prepare ist Abschalten/Amendment im laufenden Change blockiert; offene Findings lassen sich nicht wegschalten.

[Ausführbare Befehle, Formate und Grenzen](docs/CRITIQUE.md). Modellfreier Ablaufcheck: `python3 sdd-evo/examples/run_critique_e2e.py`. Dieser verwendet geskriptete Critic-Fixtures, keinen echten unabhängigen Review. Read-only ist beratend, nicht host-erzwungen.

## Was wird gebunden?

- Git HEAD + tatsächlicher HEAD-Tree + Index, Inhalte/Executable-Bit aller getrackten und nicht ignorierten ungetrackten Dateien; getrackte Löschungen und Symlink-Zieltexte. Symlinks werden nicht zum Lesen ihrer Ziele verfolgt; Submodule/Spezialdateien blockieren. Contract/Config/geschützte Dateien dürfen keine Symlinks sein.
- Vertrag, Config, explizit geschützte Tests und optionale `spec_files`.
- Runnerbytes, Pythonversion, Plattform, Bytes des direkten Executables und die explizite Config-Umgebung. Es wird **keine Prozessumgebung mit geerbten Credentials** weitergereicht.
- Anfangs- und Endidentität, tatsächlicher Prozess-Exitcode, Testanzahl, Laufnummer und Hashes der begrenzten stdout-/stderr-Artefakte.

`.sdd/` ist absichtlich nicht Teil des Snapshots: keine rekursive Selbsthashbildung. Belege/Logs sind ignoriert, lokal und mit restriktiven Dateirechten. Fehlende/abweichende Logs, unbekannte Resultate, Timeout, Outputlimit, fehlende Tests und Änderungen während des Laufs blockieren. Ganze Quelle wird konservativ invalidiert, auch Dokumentations- und Indexänderungen. Nach Commit/Staging neu prüfen.

OpenSpec/Spec Kit können weiter planen: trage konkrete lokale Spec-Dateien als repo-relative `spec_files` ein. Es werden nur ihre Bytes gehasht, keine Inhalte ausgeführt, synchronisiert oder semantisch adaptiert.

## Grenzen, die du kennen musst

- **Keine Sandbox oder Sicherheitsgrenze.** Vertrauenswürdige lokale Kommandos haben Benutzerrechte, einschließlich Netzwerk/Dateizugriff. Niemals fremde/fetched Contracts automatisch ausführen. Keine Shell als Standard, aber ein explizit akzeptiertes Executable kann selbstverständlich selbst eine Shell starten.
- Gleicher Benutzer kann Tool, Tests, State und Logs manipulieren. Digests erkennen Drift, authentifizieren weder PASS noch menschliche Zustimmung. Lock schützt nur kooperierende CLI-Aufrufe; keine Sperre gegen parallel schreibende Editoren/Angreifer. Kein Anspruch auf TOCTOU-Freiheit, hermetische Ausführung oder kurzzeitig veränderte/zurückgesetzte Inputs.
- Ignorierte Abhängigkeiten, Systembibliotheken, Toolchains hinter Wrappern, Services, Container und sonstige externe Ressourcen sind nicht vollständig erfasst. Pinne benötigte Versionen zusätzlich im Repo/Config; für hohe Sicherheit nutze geschützte CI und isolierte, reproduzierbare Umgebungen.
- Keine Secrets in argv, Config, Reviews oder Tests ausgeben. Der Runner erbt keine Secrets und druckt Logs nicht in die Konsole, aber speichert **tatsächliche begrenzte Testausgaben**, keinen perfekten Secretfilter. Lokale Logs nicht veröffentlichen. Ein bewusst Dateien lesender Test bleibt vertrauenswürdiger Code, kein abgeschirmter Gast.
- Ein aktiver Change pro Repo, keine neue Change-/Archivverwaltung, keine automatische Reparatur, kein Scope-Enforcement und keine semantische Testabdeckungsprüfung. `min_tests` ersetzt kein Review der richtigen Anforderungen. Für nächste Changes State nur nach bewusstem Archivieren außerhalb des aktuellen Runs verwalten; nicht als Budgetumgehung.

## Verifizieren und tiefer lesen

```sh
python3 -m unittest discover -s sdd-evo/tests -v
python3 sdd-evo/examples/run_e2e.py
python3 scripts/check_docs.py
```

[Implementierte Prüfung](docs/MVP-VERIFICATION.md) · [Integrationen](INTEGRATION.md) · [Designzustände](FRAMEWORK.md) · [Designartefakte](ARTIFACTS.md) · [Vergleich](COMPARISON.md) · [Designbeispiel](EXAMPLE.md) · [Quellen](EVIDENCE.md).

Die bisherige [synthetische Konsistenzdemo](docs/VERIFICATION.md) und `scripts/sdd_gate.py --demo` bleiben unverändert getrennt. Ihre PASS-Fixtures sind **keine** Belege des neuen Runners. Das umfassendere FRAMEWORK beschreibt weiterhin vorgeschlagene Mechanismen, nicht vollständig implementierte Laufzeitgarantien.
