# Optionaler unabhängiger Critic

[Quickstart](../README.md) · [Integration](../INTEGRATION.md) · [Quellen](../EVIDENCE.md)

Ein frischer Task-first-Critic sucht nach Lücken zwischen **Originalauftrag**, Vertrag und tatsächlichem Ergebnis, nachdem die Pflichtsuite bestanden ist. Die CLI bereitet Kontext vor, importiert strukturierte Findings und verlangt deren abschließende Disposition. Sie startet kein Modell, führt keine Findings-Kommandos aus und ersetzt keinen manuellen Fachreview.

## Aktivieren und verwenden

Im Ziel-Repo: Runner unter `sdd-evo/evo.py`, Critic-Skill unter `.agents/skills/evo-critic/SKILL.md` (Codex) beziehungsweise `.claude/skills/evo-critic/SKILL.md` (Claude). Installation **vor** dem ersten Check, weil auch Skills zur Quellidentität gehören.

1. Den tatsächlich autorisierten externen Nutzerauftrag unverändert in `task-brief.md` aufbewahren, nicht aus der Builder-Spec rekonstruieren. Im Contract `"task_brief": "task-brief.md"` ergänzen. Der Pfad ist repo-relativ und seine Bytes werden separat geschützt. `BRIEF` in Findings bezeichnet eine Lücke, die nicht in R-IDs übersetzt wurde; der Critic darf sie nicht selbst autorisieren.
2. In `evo-config.json` explizit setzen:

```json
{"critique": {"enabled": true, "max_reviews": 1, "max_repairs": 1}}
```

Der Initialwert ist `enabled: false`. Akzeptiere dies beim `start`; bei einem bereits gestarteten Change ist die Änderung ein autorisiertes Amendment:

```sh
python3 sdd-evo/evo.py change --accept "owner/request-124" --reason "Authorized original brief and bounded critique"
python3 sdd-evo/evo.py check
python3 sdd-evo/evo.py critique-prepare
```

`critique-prepare` erzeugt `.sdd/critique-package-1.json`: Originalbrief, vollständiger Contract/Nichtziele, Subject-/Contract-/Promptidentität, beim Start festgehaltener Git-Basiscommit, Diff gegen diese Basis und exakte aktuelle Dateibytes als Base64 einschließlich neuer Dateien, Löschungen und Executable-Bit. Geschützte Inputs werden auch dann aufgenommen, wenn Git sie ignoriert. Symlinks im Paket blockieren; maximal 200 Dateien und 2 MiB JSON, keine stillschweigende Kürzung. Größere Repos brauchen eine separat entworfene Paketstrategie, nicht einfach eine unvollständige Zusammenfassung. Pakete können private Quelldaten enthalten: vor manueller Weitergabe prüfen, keine automatische Übertragung.

3. **Neue Sitzung**, nicht Builder-Fortsetzung; keine Trajectory nachladen. Starte einen bereits autorisierten Agenten im Ziel-Repo. Die folgenden Texte gehören in dessen Prompt, nicht in die Shell:

```text
Codex: $evo-critic Read .sdd/critique-package-1.json; write only .sdd/critic-result.json.
Claude: /evo-critic Read .sdd/critique-package-1.json; write only .sdd/critic-result.json.
```

Der Critic darf nur Paketdateien beziehungsweise die darin benannten aktuellen Quelldateien lesen. Vor Live-Inspektion Übereinstimmung mit Paketbytes prüfen. Bei Drift stoppen. Read-only ist **Promptregel, nicht OS-erzwungen**; frischer Kontext und Modellnamen sind deklarierte Labels, keine authentifizierte Unabhängigkeit. Keine Providerkosten werden durch die CLI ausgelöst; tatsächliche Modellnutzung braucht die bestehende separate Erlaubnis. Operator-approved Probes in einer isolierten Umgebung sind vorzuziehen; bei fehlender sicherer Ausführung `unverified` statt erfundener Beobachtung. Keine temporären Dateien im Quellrepo, keine Source-/Test-/Configänderungen durch den Critic.

4. Tatsächliches Ergebnis importieren, relevante Findings als Builder reproduzieren, nur autorisierten Code reparieren. Bei Mehrdeutigkeit oder notwendiger Scopeänderung stoppen.

```sh
python3 sdd-evo/evo.py critique-import --result .sdd/critic-result.json
# Builder: Findings prüfen, Reparatur und tatsächliche Fachreviewnote schreiben.
python3 sdd-evo/evo.py check
# .sdd/dispositions.json mit finaler receipt.identity und allen Findings erstellen.
python3 sdd-evo/evo.py critique-dispose --by "actual-domain-reviewer" --evidence .sdd/dispositions.json
python3 sdd-evo/evo.py review --by "actual-domain-reviewer" --evidence review.md
python3 sdd-evo/evo.py finish
```

Reviewnote **vor** dem finalen Check schreiben. Alle Änderungen nach Import (auch Notes/Index/Commit) zählen beim nächsten Check als ein neuer Repair-Kandidat; Änderungen gesammelt prüfen. Bei unverändertem Code darf eine belegte Widerlegung statt Repair erfolgen. Nach Repair laufen alle akzeptierten Checks tatsächlich erneut. Ein `fixed`-Eintrag ohne geänderten, frisch geprüften Subject blockiert.

## Ergebnisformat

Das ist eine **Schemaschablone, kein ausgeführtes Critic-Ergebnis**. Identitäten aus dem Paket kopieren, Labels wahrheitsgemäß setzen; keine Platzhalter als Befunde importieren. `fresh_context` darf nur bei tatsächlich frischer Sitzung `true` sein.

```json
{
  "schema": 1,
  "package_id": "COPY_FROM_PACKAGE",
  "subject": "COPY_FROM_PACKAGE",
  "contract_id": "COPY_FROM_PACKAGE",
  "prompt_id": "COPY_FROM_PACKAGE",
  "critic": "actual-session-label",
  "model": "actual-provider/model-version",
  "fresh_context": true,
  "findings": [{
    "id": "F1",
    "requirement": "R1",
    "deviation": "Concrete expected versus observed behavior",
    "probe": "What was actually inspected/executed; not a command to auto-run",
    "observation": "Actual observation, or explicitly not executed",
    "support": "unverified",
    "severity": "major",
    "uncertainty": "What is unknown and why"
  }]
}
```

`support`: `supported`, `contradicted`, `unverified`. `severity`: `minor`, `major`, `critical`. `requirement`: existierende R-ID oder `BRIEF`. IDs `F1`, `F2`, … eindeutig pro Runde; maximal 100 Findings. Leere Findingsliste ist zulässig, aber **keine Abnahme**. Der Import prüft Form/Bindung, nicht die Wahrheit oder Vollständigkeit eines Befunds.

Disposition in `.sdd/dispositions.json`:

```json
{
  "schema": 1,
  "subject": "COPY_IDENTITY_FROM_FINAL_SDD_RECEIPT",
  "findings": {
    "1/F1": {
      "status": "fixed",
      "rationale": "Why this resolves the original finding",
      "probe": "Actual final-state recheck",
      "observation": "Actual result",
      "uncertainty": "Remaining limitations"
    }
  }
}
```

Der Schlüssel ist `Rundennummer/Finding-ID`. **Alle** Findings aus allen importierten Runden müssen vorkommen, auch widersprochene/unverifizierte. `fixed` und `refuted` brauchen konkrete Evidenzfelder. `open` blockiert immer; `accepted_risk` ist ausschließlich für `minor` zulässig. Major/critical müssen repariert oder begründet widerlegt werden. Bei leerem Critic-Ergebnis trotzdem explizit `"findings": {}` disponieren. Die CLI attestiert keine semantische Qualität dieser Aussagen; der Fachreview bleibt zuständig.

## Budgets, Fehler und Abschalten

- Drei getrennte kumulative Zähler: echte Testläufe (`max_runs`), vorbereitete Reviewrunden (`max_reviews`) und unterschiedliche nach Import geprüfte Repair-Subjects (`max_repairs`). Review/Repair jeweils 1–3, Default 1/1, keine Behauptung eines optimalen Budgets. Fehlgeschlagener Test verbraucht Run und gegebenenfalls Repair; Wiederholung desselben Subjects nur Run. Vor Import ist Repair blockiert.
- Vorbereitete Runden werden vor Übergabe gezählt. Ein unterbrochener Critic bekommt keinen Gratis-Reset. Noch nicht importierte Resultate dürfen nach Schemafehler korrigiert werden, aber nur für dasselbe unveränderte Paket/Subject. Mehrere vorbereitete Runden nur im vorab akzeptierten Budget; die Disposition muss sämtliche alten Findings enthalten.
- Veraltete Maschinen-/Critic-/Dispositionbelege, fehlende oder geänderte Paket-/Ergebnis-/Dispositiondateien, unvollständige Findings und fehlender manueller Review blockieren. Keine Wiederherstellung durch fingiertes PASS. Nach unerwartetem Stateverlust stoppen und anhand echter Originalartefakte untersuchen.
- `enabled` umstellen erfordert ein explizites `change --accept … --reason …`; nicht still umschalten. Budgets lassen sich im Change nicht erhöhen oder zurücksetzen. **Nach dem ersten Prepare sind sämtliche Amendments in diesem kleinen Adapter blockiert**, auch Disable. So bleiben offene Findings unvermeidbar. Bei notwendigem Amendment zum Owner eskalieren; nicht State löschen oder einen neuen Change als Budgetumgehung beginnen. Ein normal abgeschlossener/abgebrochener Change kann nach bewusster externer Archivierung durch einen separat autorisierten Folgeauftrag ersetzt werden. Der Abschaltpfad vor Prepare erhält immer die manuelle Abnahmepflicht.
- Alte laufende MVP-States ohne Critique-Ledger werden nicht still migriert (`LEGACY_OR_INCOMPLETE_STATE_REQUIRES_ARCHIVE`). Den bisherigen Runner für deren Abschluss behalten oder den Auftrag bewusst stoppen/extern archivieren; keine verlorenen Counter rekonstruieren.

Same-UID kann State, Runner und Belege manipulieren. Hashes dienen Drift-/Verlustkontrolle, nicht Signaturen. Lock und Anfangs-/Endhash verhindern keine zwischenzeitliche Mutation mit Restore. Abhängigkeiten außerhalb der erfassten Quellen bleiben unvollständig gebunden. UI benötigt echte fachliche/visuelle Beurteilung; dieser Adapter liefert keinen automatischen UX-Grader.

## Lokal prüfen

```sh
python3 -m unittest discover -s sdd-evo/tests -v
python3 sdd-evo/examples/run_critique_e2e.py
```

Die Tests verwenden echte temporäre Git-Repos, CLI-Prozesse, fehlschlagende/bestandene unittest-Läufe und einen tatsächlich ausgeführten Negativzahlen-Probe. Critic- und Humanlabels sind ausdrücklich **geskriptete Protokollfixtures**, keine unabhängige LLM-/Menschenprüfung und keine Wirksamkeitsmessung.
