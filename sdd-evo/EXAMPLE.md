# Durchgehendes Beispiel: öffentlicher Katalogexport

[Übersicht](README.md) · **Vollständig synthetisches Entwurfsbeispiel.** Keine privaten Daten, kein realer Export und keine Veröffentlichung. Die dargestellten Anwendungstests/Worker/Releaseereignisse sind illustrative Sollabläufe, nicht ausgeführte Pipelinebelege. Tatsächlich ausgeführt wurde nur der Fixture-Validator in [VERIFICATION](docs/VERIFICATION.md).

## 1. Auftrag und erster Vertrag

Ein erfundener Katalog hat Einträge mit `id`, `title`, `visibility`. Auftrag: „Erzeuge lokal eine JSON-Datei mit ausschließlich öffentlichen Einträgen und verständlicher CLI-Hilfe.“ Der Builder darf `src/export.py`, `src/cli.py`, Entwicklerchecks und Hilfe ändern, nicht Publikationscredentials, Policies oder geschützte Abnahme. Abschlussziel: lokal integriertes Artefakt, kein Push/Upload.

| ID | Autorisiertes Soll v1 | Positive / negative Beobachtung |
|---|---|---|
| R1 | Nur `visibility == "public"` exportieren | public enthalten; private ausgeschlossen |
| R2 | Deterministisches JSON aus allen freigegebenen Einträgen | Gemischte Liste ergibt exakt erlaubte IDs; kein Hardcoding einzelner Beispiele |
| R3 | CLI führt den wirklichen Export aus, verständliche Hilfe/Leermeldung | Öffentlicher Entry Point statt nur Helpertest; Hilfe nennt lokale Ausgabe und keine Veröffentlichung |
| R4 | Kein Netzwerk, keine Zusatzfelder mit internen Daten | Keine Telemetrie/Upload; Fehlermeldungen enthalten keine vertraulichen Inhalte |

Streaming oder Batch sind erlaubt, sofern Ergebnis, Privacygrenzen und Nutzerführung stimmen. Die gewünschte Ausgabeordnung wird explizit festgelegt; keine zufällige Oraclestandardannahme. Im Beispiel gilt Sortierung nach ID. Der Baselinecheck zeigt: Helper und CLI verwenden bisher unterschiedliche Filter. Dieser Istbefund wird dokumentiert, nicht als Soll legitimiert.

## 2. Fehlende Grenzfälle → echtes Amendment

Während der Abnahmereview tauchen fehlende und unbekannte Labels auf:

```json
[
  {"id":"a","title":"Alpha","visibility":"public"},
  {"id":"b","title":"Beta","visibility":"private"},
  {"id":"c","title":"Gamma","visibility":"future-label"},
  {"id":"d","title":"Delta"}
]
```

Der Builder möchte fehlend = public interpretieren. **Block:** Das war nicht delegiert und widerspricht der positiven Publicgrenze. Der Intent Owner bestätigt v2 ausdrücklich: R1 gilt auch für unknown/missing; nur `a` darf erscheinen. Die unabhängige Oracleverantwortung ergänzt Fälle für unknown, missing und Kombinationen. Keine Privacyabschwächung.

Warum als Amendment und nicht stiller Testpatch? Die normative Grenzfallbehandlung und verbindliche Prüfbasis werden sichtbar präzisiert. Neue Contract-/Spec-/Oracleidentitäten; ältere Plan-/Coverage-/Runbelege sind stale. Historisches v1-Grün bleibt historisch erhalten. Ein bereits vorhandener Kandidat darf als Material weiterleben, muss aber unter v2 neu integriert und geprüft werden. Ein unabhängiger vorab delegierter Domain-Owner könnte diese Präzisierung autorisieren; nicht zwingend ein neuer Human-Dialog.

**Gegenbeispiel:** v1-Test „private fehlt“ grün → v2-Datei speichern → alte Receipt kopieren. Gate blockiert wegen Inputmismatch. Nur Hashes neu berechnen ersetzt weder neue Tests noch Autorisierung.

## 3. Begrenzte Umsetzung und Parallelresultate

Optional arbeiten zwei Worker auf derselben Basis/Generation:
- A: Exportfilter und Entwicklerregression; Write-Set `src/export.py`.
- B: CLI-Verkabelung und Hilfe; Write-Set `src/cli.py`, `docs/help.md`.

A ist solo grün. B ist solo grün, weil sein Fixture den alten Helper mockt. Der Merge ist konfliktfrei, ruft aber noch die alte Filterfunktion auf. **Nicht fertig:** Integration Owner friert den kombinierten Tree I1 ein; der echte CLI-Mixed-Case zeigt `c` und `d` in der Ausgabe. Workerreceipts können diese Lücke nicht schließen.

**Repair 1:** B verbindet den neuen Filter. Intent v2 und geschützte Abnahme bleiben unverändert; Generation steigt. Alter verspäteter A-Report wird als stale abgelegt, nicht angehängt. I2 wird auf aktueller Basis neu gebildet und vollständig geprüft. Auch die bisherigen Anforderungen bleiben Regressionpflichten. Wenn danach die Zielbasis wechselt, entsteht I3 mit neuer vollständiger Prüfung — kein „war gestern grün“.

## 4. Fachliche und Nutzerabnahme

Vorgeschlagene unabhängige Prüfungen auf I2:
- R1/R2: public/private/unknown/missing/mixed sowie Kombinationen und Nicht-Hardcoding; Mutant „alles außer private“ muss scheitern.
- R3: echter CLI-Aufruf erzeugt genau die erwartete lokale JSON-Datei; `--help`, leerer Export, ungültige Eingabe und verständliche Exitmeldung werden beurteilt.
- R4: unerlaubte Netzwerkversuche und Zusatzfelder blockieren; Logs/Fehler dürfen keine ausgeschlossenen Inhalte verraten.
- Review: Hilfe unterscheidet **Datei erstellt** von **veröffentlicht**, erklärt Ausschlüsse ohne vertrauliche Details und erhält bestehende Nutzerführung. Eine grüne Helper-Suite ohne diese Integration/Guidance ist unvollständig.

Bekannt-richtiger Kontrollfall muss bestehen, bekannt-falscher Mutant scheitern, fehlender Testreport blockieren. Ein anderer korrekter Streamingalgorithmus besteht ebenfalls; Tracegleichheit ist keine Anforderung. Sind Oracle oder UI-Rubrik fraglich, benannter Entscheidungsbedarf statt automatischem PASS.

Jetzt bindet eine vertrauenswürdige Receipt v2, I2, Base, Candidate, Oracle, Policy, Config, Commands, Environment, Instructions und Generation; Review bindet denselben Stand. **ACCEPTED für I2, nicht RELEASED.**

## 5. Späte Änderungen, Budgets und ehrlicher Stop

| Ereignis | Richtige Entscheidung |
|---|---|
| Nach Grün noch CLI-Datei ändern | Alte Abnahme stale; neu einfrieren und prüfen. Genau diese Form zeigt `stale-current.json`. |
| Testfile hinzufügen oder geschützten Test abschwächen | Entwickleränderung invalidiert Treeevidenz; Oraclemutation braucht unabhängige Aufnahme und kann nicht selbst freigeben. |
| Alle Tasks abhaken, keine Receipt | `EVIDENCE_MISSING`; Schedulingdaten sind kein Verhaltensnachweis. |
| Teststatus skip/error/unknown | Nicht akzeptiert; Pflichtumfang nicht nachträglich verkleinern. |
| Zum Reparieren Telemetrie hinzufügen | Out-of-scope und gegebenenfalls verbotener Effekt, selbst wenn Exportdatei stimmt. |
| Zweite Reparatur verbraucht, nächster Fehler unverändert | Kein dritter Versuch; `BUDGET_EXHAUSTED` beziehungsweise `NO_PROGRESS`, offene Verpflichtungen berichten. |
| Alternative Datenstruktur, gleiche erlaubte Semantik, neue frische Belege | Akzeptabel; kein goldener Implementierungspfad. |

Die JSON-Fixtures verwenden beschreibende Strings statt ausführbarer Exportimplementation. `test_valid_alternative_with_fresh_evidence` belegt, dass der **Gate** keine bestimmte Implementierungszeichenkette erzwingt; es beweist nicht die fachliche Korrektheit eines Streamingexporters. Gleiches gilt für die modellierten Review-/PASS-Belege.

## 6. Optionaler späterer Release — hier ausdrücklich nicht erfolgt

Ein eigener Auftrag könnte I2 an eine öffentliche Zieladresse veröffentlichen. Dafür: aktuelles Exportmanifest/Audience nochmals prüfen, exakten Artefaktdigest und Ziel binden, separate Befugnis samt Ablauf, Idempotency-Key, Payload, Health-/Readbackplan und Removalzuständigkeit festhalten.

Illustrativer Fehler: Upload timeout, lokale Receipt fehlt. Möglicherweise wurde die Datei veröffentlicht. **RECOVERY_REQUIRED**: Operations-ID und Zielzustand auslesen; kein zweiter Upload auf Verdacht. Erst bestätigter Zustand erlaubt RELEASED oder autorisierte Wiederholung. Ein Rollback der Software entfernt die veröffentlichte Datei nicht automatisch. Späterer Sichtbarkeitswiderruf braucht Removal-/Rebuild-/Cachemaßnahmen mit überprüfter Reichweite; fremde Kopien bleiben eine Grenze.

## 7. Lernen ohne Selbstrechtfertigung

Die übersehene CLI-Verkabelung wird als Fehlerereignis erhalten. Mögliche Harnessänderung: Entry-Point-Check früher vorschlagen. Nicht automatisch dauerhaft übernehmen: mit unveränderter Abnahme gegen den bisherigen Workflow auf mehreren passenden Aufgaben und gleichem Budget vergleichen. Wenn es nur mehr Text erzeugt, verwerfen. Aktuellen Export reparieren und künftige Arbeitsweise verbessern bleiben getrennte Entscheidungen.
