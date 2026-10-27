# OpenSpec: ändern, prüfen, konsolidieren

[Übersicht](../README.md) · [Matrix](comparison-matrix.md)

## Mentalmodell und Artefakte

Eine Capability beschreibt dauerhaftes, beobachtbares Systemverhalten. Ein Change beschreibt dessen beabsichtigte Änderung. Im Standardlayout liegen aktuelle Specs und offene Changes getrennt. Das folgende Layout ist illustrativ, nicht von einem ausgeführten OpenSpec-Lauf erzeugt. [O2](../sources.md#o2), [O10](../sources.md#o10).

```text
openspec/
  config.yaml
  specs/public-export/spec.md
  changes/add-public-export/
    .openspec.yaml
    proposal.md
    specs/public-export/spec.md
    design.md
    tasks.md
  changes/archive/
```

- `proposal.md`: Warum, welche Capabilities, welche Auswirkungen?
- Delta-Spec: neue, geänderte, entfernte oder umbenannte Requirements und Szenarien.
- `design.md`: Wie, warum diese Alternative, Risiken, Migration und Rückweg?
- `tasks.md`: Arbeit mit explizitem Verifikationsweg; Checkboxen sind Fortschritt, keine Testresultate.
- `.openspec.yaml`: Change-Metadaten wie Schema; Sonderfälle nicht mit erfundenen Requirements kaschieren.

Die Standard-Schema-Prosa sieht Design nach Bedarf vor; der deklarierte Task-Knoten hängt am Pin dennoch von Design und Specs ab. Deshalb `status` und tatsächlich aufgelöstes Schema prüfen, nicht einfach aus dem Baum löschen. [O2](../sources.md#o2).

## Schritt für Schritt

**Die folgenden Befehle sind Anleitung, hier nicht ausgeführt.** Installation ist ein eigener, genehmigungspflichtiger Schritt in einer echten Arbeitsumgebung. Die Installationsdoku beschreibt ein Standalone-Binary ohne Node und alternativ Paketmanager; der npm-Pfad verlangt dort Node 20.19.0 oder neuer. Nicht ungeprüft einen beweglichen `latest`-Stand mit diesem Quellpin gleichsetzen. Vor einem Pilot Release und Prüfsumme festlegen. [O8](../sources.md#o8).

1. **Initialisieren.** Nach geprüfter CLI-Installation im Zielprojekt `openspec init` aufrufen, Agent auswählen, erzeugte Dateien prüfen und versionieren. Kontext und Regeln in `openspec/config.yaml` klein halten: Domain, Testkommandos, Privacy-Grenze. Keine Secrets hinein. [O6](../sources.md#o6).
2. **Erkunden.** Im Agent-Chat `/opsx:explore public-export`. Klären, was öffentlich ist, wann ein Snapshot entsteht und was ausdrücklich nicht exportiert wird. Explore ist laut Vertrag kein Implementierungsmodus; das ist eine Agentenanweisung, keine Sandbox. [O1](../sources.md#o1).
3. **Change formulieren.** `/opsx:propose add-public-export`. Vorschlag, Specs, Design und Tasks prüfen. Erwartung: begrenzter Scope, Szenarien für Ablehnung und Fehler, keine unbegründete Architektur. [O1](../sources.md#o1), [O2](../sources.md#o2).
4. **Vor Code reviewen.** Proposal auf Ziel, Spec auf Abnahme und Tasks auf Abdeckung prüfen. Bei Revision `/opsx:update add-public-export`: vorhandene Planungsartefakte werden mit Bestätigung je Artefakt abgestimmt, nicht Anwendungscode. Noch nicht begonnene Artefakte gehören zum inkrementellen Erzeugen, nicht stillschweigend zu update. [O1](../sources.md#o1).
5. **Status abfragen.** Im Terminal `openspec status --change add-public-export --json`. Aufgelöste Pfade und Abhängigkeiten prüfen; bei Stores nicht blind Repo-Pfade annehmen. [O3](../sources.md#o3).
6. **Umsetzen.** Im Chat `/opsx:apply add-public-export`. Tests pro Arbeitsgruppe ausführen lassen und echte Ergebnisse prüfen. Bei Blockern anhalten und Scope klären. Neue Absicht zuerst freigeben, dann Artefakte und Code nachführen. [O1](../sources.md#o1), [O2](../sources.md#o2).
7. **Prüfen.** Struktur mit den CLI-Befehlen unten; Verhalten mit unabhängigen Anwendungstests. Optional `/opsx:verify add-public-export` für Vollständigkeit/Korrektheit/Kohärenz. Ein „not verified“ ist keine bestandene Prüfung. Verify ist beratend. [O5](../sources.md#o5), [O7](../sources.md#o7).
8. **Konsolidieren.** `/opsx:sync add-public-export` überträgt Delta-Requirements in Hauptspecs, ohne den Change zu archivieren. Diff prüfen. Nicht vorzeitig den Zustand „ausgeliefert“ behaupten, wenn nur Text synchronisiert wurde. [O1](../sources.md#o1).
9. **Abschließen.** `/opsx:archive add-public-export` nach Review und Tests. Sync-Status, Warnungen und tatsächlichen Archivpfad nachlesen. Danach Code, Artefakte und Testergebnisse gemeinsam im PR reviewen. Archivieren deployt nichts. [O3](../sources.md#o3).

```bash
# Strukturprüfung, kein Verhaltenstest; hier nicht ausgeführt
openspec validate --all --strict --no-interactive
openspec validate --archived --no-interactive
```

`--archived` hat einen eigenen Scope: unvollständige archivierte Task-Checkboxen, nicht erneute fachliche Validierung aller bereits angewandten Deltas. [O7](../sources.md#o7).

## Core, optionale Workflows und Syntax

| Ebene | Verfügbar bzw. Form | Wichtig |
|---|---|---|
| Core | explore, propose, apply, update, sync, archive | verify ist nicht Teil dieses Default-Satzes. |
| Optional/custom | new, continue, ff, verify, bulk-archive, onboard | Über `openspec config profile` wählen, dann `openspec update` im Projekt. |
| Kanonische Dokuform | `/opsx:propose` | Agent-Chat, nicht Terminal. |
| Cursor/Copilot-Beispiel | `/opsx-propose` | Installierte Integration entscheidet. |
| Codex-Skill | `$openspec-propose` | Nicht jede Integration besitzt Slash-Commands. |
| Skills-only-Beispiel | `/openspec-propose` | Generierte Skill-Namen prüfen; etwa apply-change statt apply. |

Quellen: [O1](../sources.md#o1), [O11](../sources.md#o11). Plain Language im neuen Quickstart ist eine weitere Bedienform, keine Garantie exakter Tool-Auswahl. [O10](../sources.md#o10).

## Nicht verwechseln: Agent-Archive und CLI-Archive

Das **Skill-Template** bewertet Status und Sync, fragt bei unvollständigen Tasks/Artefakten nach und kann auf Nutzerwahl ohne Sync archivieren. Wenn Sync gewählt wurde und fehlschlägt, soll es dagegen stoppen. Am Ende beschreibt es ein Verschieben des Change-Verzeichnisses. Das sind Prompt-Verträge. [O3](../sources.md#o3).

Der direkte **Terminalbefehl `openspec archive`** besitzt eigenen Code: Delta-Validierungsfehler und ungültige rekonstruierte Specs können blockieren; Proposal-Warnungen allein sind nicht blockierend. `--yes` kann Task-/Bestätigungsabfragen übergehen, `--no-validate` Validierung abschalten, `--skip-specs` Spec-Updates überspringen. JSON-Modus setzt bei Blockern einen Fehlerstatus. `--yes` allein ist nicht dasselbe wie `--no-validate`. Kein Pfad beweist, dass Anwendungstests bestanden sind. [O4](../sources.md#o4).

## Good / bad / conditional

- **Gut:** begrenzte, wiederholte Capability-Änderungen; nachvollziehbare Delta-Historie; getrennte Diskussion von Absicht und Implementierung.
- **Bedingt:** mehrere parallele Changes an derselben Capability. Vor Sync frische Basis lesen, Konflikte reviewen und Merge-Reihenfolge vereinbaren.
- **Schlecht eingesetzt:** Hauptspecs nie synchronisieren; Archive als Qualitätszertifikat ansehen; aus Formatvalidierung auf korrekte Privacy schließen.

Bewertung ist eine Ableitung aus dem Modell, kein Produktbenchmark. Konkrete [Gates](drift-and-gates.md) und das [gemeinsame Beispiel](example-workflow.md) machen die Grenzen überprüfbar.
