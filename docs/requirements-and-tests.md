# Anforderungs- und Testcheckliste

[Beispiel](example-workflow.md) · [Gates](drift-and-gates.md)

Diese Checkliste ist eine **Vorlage für den späteren Export-Pilot**. Die Kästchen sind bewusst offen: Es wurde hier kein Export implementiert und keiner dieser Anwendungstests ausgeführt. Die abgeschlossene Dossier-Prüfung steht separat in [verification.md](verification.md).

## Vor dem Implementieren: Requirements-Qualität

- [ ] Scope, Datenquelle, Freigabeverantwortung und Nicht-Ziele sind genehmigt.
- [ ] `public` und `approved` haben eindeutige Typen und Semantik; unklarer Status ist fail-closed.
- [ ] Anforderungen FR-001 bis FR-010 besitzen prüfbare Ergebnisse, einschließlich Negativfällen.
- [ ] Snapshot-Revision, erlaubte Felder und interne Referenzen sind im Vertrag definiert.
- [ ] Veröffentlichung, Archivierung, lokale Bereitstellung und Widerruf sind getrennt.
- [ ] Keine private Quelle wird als Fixture oder Logbeispiel benutzt.
- [ ] Jede Anforderung hat Owner, Task-Referenz und Test-/Review-Nachweis.
- [ ] Tatsächlicher Feature-/Change-Pfad und effektive Instruktionen wurden vor Schreiben geprüft.

Das entspricht einer Requirements-Review-Aufgabe. Insbesondere Spec-Kit-Checklisten sind keine ausführbaren Unit-Tests. [S1](../sources.md#s1), [S4](../sources.md#s4).

## Verbindliche Tests für beide Varianten

| Test-ID | Requirement | Prüffall | Erwarteter Nachweis |
|---|---|---|---|
| TST-01 | FR-001 | Matrix public/internal/sonstige gültige Labels × approved true/false. | Nur explizit öffentliche, freigegebene Artikel im Output. |
| TST-02 | FR-002 | Fehlendes Label, unknown-Label, string statt bool. | Fehlerstatus; keine neue Ausgabe; keine internen Inhalte im Log. |
| TST-03 | FR-003 | Zusätzliche Metadaten und verschachtelte Zusatzfelder. | Nur id/title/body; keine Weitergabe kompletter Eingabeobjekte. |
| TST-04 | FR-004 | Gleicher Snapshot wiederholt und mit permutierter Reihenfolge. | Bytegleiche kanonische Ausgabe. |
| TST-05 | FR-005 | Doppelte IDs, fehlender Titel, internes Linkziel. | Explizite Ablehnung statt Überschreiben oder Nachladen. |
| TST-06 | FR-006 | Erwartete Revision stimmt nicht mit Adapter-Snapshot überein. | Abbruch vor Austausch. |
| TST-07 | FR-007 | Schreibfehler, ungültiges Ziel, Unterbrechung vor Ersetzen. | Alte gültige Datei unverändert; kein halbfertiger Zielstand. |
| TST-08 | FR-008 | Manifest gegen fertige Bytes prüfen. | Digest, Revision und Anzahl passen; kein privates Metadatenfeld. |
| TST-09 | FR-009 | Netzwerkversuch und Upload-Aufruf instrumentieren. | Export-Kern funktioniert offline; keine externe Wirkung. |
| TST-10 | FR-010 | Freigabe im nächsten Snapshot widerrufen. | Neue Ausgabe ohne Artikel; separater Removal-Auftrag mit eigener Verifikation. |
| TST-11 | FR-001 bis FR-010 | Gesamter synthetischer Lauf vom Snapshot bis lokaler Datei. | Vertrag und Negativpfade gleichzeitig erfüllt. |
| TST-12 | Projektgrenze | Agent versucht Abnahmetest oder CI-Regel abzuschwächen. | Änderung benötigt unabhängige Freigabe; Agent kann Gate nicht selbst umgehen. |

Diese Matrix ist **von uns entworfen**, nicht Bestandteil eines Hersteller-Testpakets. Deterministische lokale Tests ergänzen semantisches Review; sie beweisen kein universelles Datenschutzverhalten.

## Done heißt nicht nur „alle Checkboxen gesetzt“

- [ ] Testcode vorhanden und tatsächlich entdeckt; kein leerer/grün übersprungener Lauf.
- [ ] Vollständige Ergebnisse und getesteter Commit aufgezeichnet; keine erfundenen Resultate.
- [ ] Review aller Änderungen an Anforderungen, Tests, CI und Berechtigungen.
- [ ] Kein offener kritischer Befund; akzeptierte Restrisiken mit Owner und Ablaufdatum.
- [ ] OpenSpec: Sync-Diff und Archivzustand nachgelesen, wenn diese Schritte erfolgt sind.
- [ ] Spec Kit: richtige Feature-Auswahl; Converge hat nur erlaubte Task-Anhänge erzeugt.
- [ ] Branch-Regeln und Required Checks tatsächlich eingerichtet und mit negativem Fall getestet.
- [ ] Publikationsfreigabe separat; Rollback und Kill-Switch getestet.

Produktbezogene Abschlussgrenzen: [O3](../sources.md#o3), [O4](../sources.md#o4), [S2](../sources.md#s2), [S6](../sources.md#s6). Alles darüber hinaus ist empfohlene Projekt-Governance.
