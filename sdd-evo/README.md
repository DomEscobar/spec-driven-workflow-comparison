# SDD-evo

**Ein Entwicklungsablauf für Coding-Agenten: Auftrag klären, bauen, prüfen — und nicht nur behaupten, fertig zu sein.**

SDD-evo verbindet eine Spec mit der Frage: **Wurde genau das gebaut, und gelten die Tests noch für den aktuellen Code?**

> **Stand:** Framework-Entwurf mit lauffähiger Python-Demo. Noch keine fertige Integration in deinen Coding-Agenten oder deine CI.

## Welches Problem löst der Ansatz?

| Was heute schiefgeht | Regel in SDD-evo |
|---|---|
| Der Agent baut am eigentlichen Wunsch vorbei. | Vor dem Coding Ergebnis, Nicht-Ziele und Abnahmekriterien festhalten. |
| Alle Tasks sind abgehakt, aber das Feature funktioniert nicht zusammen. | Das integrierte Feature prüfen, nicht nur einzelne Arbeitspakete. |
| Tests waren grün, danach wurde Code geändert. | Betroffene Ergebnisse werden ungültig; den neuen Stand erneut prüfen. |
| Der Agent macht Tests leichter, damit die Lösung besteht. | Änderungen an der Abnahme getrennt prüfen und freigeben. |
| Der Agent repariert endlos. | Aufwand begrenzen; bei fehlendem Fortschritt mit konkretem Blocker stoppen. |
| „Fertig“ bedeutet mal Code, mal Deployment. | Abgenommen und live sind getrennte Zustände. |

Das sind die Regeln des Entwurfs. Die Demo prüft einen Teil davon mit Beispieldaten; sie setzt noch keinen vollständigen Entwicklungsprozess durch.

## Der Flow

```text
1. KLÄREN       Was soll für den Nutzer funktionieren? Was nicht?
      ↓
2. FESTLEGEN    Woran erkennen wir, dass es funktioniert?
      ↓
3. BAUEN        Kleine Änderung umsetzen und alle Teile integrieren.
      ↓
4. PRÜFEN      Tests + Review auf genau diesem Stand.
      ↓
      ├─ Fehler im Code?       → Reparieren → erneut prüfen
      ├─ Auftrag muss anders? → Änderung klären → neu festlegen
      ├─ Nachweis fehlt?       → Blocker nennen, nicht fertig melden
      └─ Anforderungen erfüllt? → Abnehmen
                                      ↓
5. AUSLIEFERN   Falls beauftragt: deployen und live prüfen.
                                      ↓
6. LERNEN       Wiederkehrende Fehler untersuchen; Prozessänderungen
                separat testen, statt die laufende Abnahme zu lockern.
```

**Der Unterschied zwischen Reparatur und Auftragsänderung:**
- „Der Download ist kaputt“ → Code reparieren, Anforderung bleibt.
- „Private Downloads brauchen erst eine Anmeldung“ → Scope ausdrücklich klären. Nicht still weglassen und „fertig“ melden.

## Beispiel: einen Export-Button bauen

**Auftrag:** Öffentliche Dokumente als ZIP herunterladen. Keine privaten Inhalte.

**Abnahme:** Download funktioniert; Inhalt stimmt; private Dokumente bleiben ausgeschlossen; Button ist auf Mobilgeräten bedienbar.

| Situation | Ergebnis |
|---|---|
| Button sichtbar, Download fehlt | Nicht fertig |
| Download funktioniert, enthält aber private Inhalte | Abgelehnt |
| Tests bestanden, Exportcode anschließend verändert | Erneut prüfen |
| Tests bestanden, mobile Bedienung noch ungeprüft | Abnahme offen |
| Aktueller Stand geprüft und fachlich akzeptiert | Abgenommen — noch nicht automatisch live |

[Das vollständige Beispiel →](EXAMPLE.md)

## Warum nicht einfach OpenSpec oder Spec Kit?

| Ansatz | Schwerpunkt |
|---|---|
| **OpenSpec** | Änderungen an bestehenden Specs planen, umsetzen und zurückführen. |
| **Spec Kit** | Anforderungen, Plan und Tasks strukturieren; Widersprüche und Umsetzungslücken finden. |
| **SDD-evo** | Festhalten, für welchen Stand eine Abnahme gilt und wann sie erneut nötig ist. |

**Kein Entweder-oder:** OpenSpec oder Spec Kit können die Planung liefern. SDD-evo ist als ergänzende Prüfschicht gedacht. Ein Vorteil gegenüber gut eingerichteter CI und Review ist bisher nicht gemessen.

[Vergleich mit Stärken und Nachteilen →](COMPARISON.md)

## Wann lohnt sich der Aufwand?

- **Kleiner Fix:** kurzer Auftrag, enger Diff, passender Test und Review. Kein großes Spec-Paket.
- **Feature über mehrere Komponenten:** Anforderungen festhalten, zusammenführen und gemeinsam prüfen.
- **Rechte, Datenmigration oder Deployment:** zusätzlich Befugnisse, Ergebnisprüfung und Wiederherstellung absichern.
- **Ziel noch unklar:** erst explorieren. Nicht so tun, als gäbe es bereits eine verbindliche Spec.

## Demo ausprobieren

Python 3 genügt. Keine Pakete, API-Schlüssel oder Modellaufrufe erforderlich.

Vom Repository-Hauptverzeichnis:

```sh
cd sdd-evo
python3 -m unittest discover -s tests -v
```

Einen passenden Nachweis prüfen:

```sh
python3 scripts/sdd_gate.py --demo \
  --approved fixtures/approved.json \
  --current fixtures/current.json \
  --evidence fixtures/evidence.json
```

Erwartung: `ACCEPTED`, Exitcode `0`, `released: false`.

Denselben Nachweis gegen einen veränderten Stand prüfen:

```sh
python3 scripts/sdd_gate.py --demo \
  --approved fixtures/approved.json \
  --current fixtures/stale-current.json \
  --evidence fixtures/evidence.json
```

Erwartung: `STALE_EVIDENCE`, Exitcode `3` — keine Abnahme.

**Die Demo prüft synthetische Nachweise.** Sie führt keine Anwendungstests aus und kann nicht beweisen, dass ein eingetragenes „PASS“ echt ist. Für echten Einsatz fehlen die Anbindung an einen vertrauenswürdigen Test-Runner und verbindliche CI-/Merge-Gates. Ein Agent mit freien Schreibrechten darf nicht zugleich seine eigenen Freigaben ausstellen.

## Weiterführend

| Du willst … | Datei |
|---|---|
| Zustände, Rücksprünge und Abbruchregeln verstehen | [FRAMEWORK.md](FRAMEWORK.md) |
| Dateien, Versionen und Zuständigkeiten sehen | [ARTIFACTS.md](ARTIFACTS.md) |
| Die drei Ansätze vergleichen | [COMPARISON.md](COMPARISON.md) |
| Einen Change komplett durchspielen | [EXAMPLE.md](EXAMPLE.md) |
| Quellen und offene Annahmen prüfen | [EVIDENCE.md](EVIDENCE.md) |
| Tatsächliche Testergebnisse nachlesen | [VERIFICATION.md](docs/VERIFICATION.md) |
