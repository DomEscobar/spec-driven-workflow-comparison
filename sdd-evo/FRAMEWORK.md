# Zustände, Entscheidungen und Gültigkeit

[Übersicht](README.md) · **Normativer Entwurf, vorgeschlagen; nur der in ARTIFACTS beschriebene Ausschnitt ist implementiert.**

## 1. Gegenstand und Abschluss

Ein Change verspricht ein beobachtbares Ergebnis in definiertem Scope, nicht eine Anzahl Dateien. Vor dem Start sind Auftrag, Istzustand, Nichtziele, zulässige Effekte, Qualitätskriterien, Verantwortliche und Grenzen bekannt. Bestehendes Verhalten ist eine Beobachtung, nicht automatisch gewünschtes Verhalten. Brownfield-Baselinefehler werden erfasst; sie dürfen weder verschwinden noch als neu verursachte Regression ausgegeben werden.

`completion_target` ist vorab entweder ein lokales integriertes Artefakt oder ein geschützter Merge. Der hier gelieferte Entwurf/Demonstrator beansprucht nur lokale Artefakte. Bei einem späteren Merge muss die Prüfung den tatsächlichen Integrations-/Merge-Tree binden. Ein PR-Head auf alter Basis genügt nicht.

## 2. Zustandsmodell

Phase: `DRAFT → READY → BUILDING → INTEGRATING → VERIFYING → VERIFIED → ACCEPTED`.
Separater Laufstatus: `active | blocked | stopped | cancelled`.
Nur `active` darf voranschreiten. Tasks haben lediglich `pending/running/candidate/integrated`; kein Taskstatus erteilt Abnahme.

| Ereignis | Übergang | Notwendige Bedingung / Wirkung |
|---|---|---|
| Vertrag autorisieren | DRAFT → READY | Outcome und Prüfkriterien hinreichend klar; gültige Auftraggeber-/Delegationsbefugnis; Oracle und Policy aufgenommen; keine blockierende Unklarheit. |
| Versuch reservieren | READY → BUILDING | Basis und Generation aktuell; erlaubte Schreibfläche; Budget kumulativ reserviert. |
| Kandidat einreichen | BUILDING → INTEGRATING | Snapshot einfrieren; Diff gegen erlaubte Fläche prüfen; alle benötigten Teile benannt. |
| Integration einfrieren | INTEGRATING → VERIFYING | Aktuelle Zielbasis; Konflikte gelöst; Entry Point, Wiring, Konfiguration, Dokumentation und verlangte Migration enthalten. |
| Pflichtprüfungen beenden | VERIFYING → VERIFIED | Alle erforderlichen Checks tatsächlich ausgeführt; freigegebenes Oracle; passende Runidentität; keine offenen blockierenden Befunde; Terminalzustand erhalten. |
| Abnahme festhalten | VERIFIED → ACCEPTED | Fach-/UX-Review vorhanden; alle Abhängigkeiten direkt vor Abschluss erneut aktuell; passendes Abschlussziel und Befugnis. |
| Repair | BUILDING/INTEGRATING/VERIFYING/VERIFIED → BUILDING | Konkreter Produktfehler unter unverändertem Vertrag; Restbudget; neue Generation; abhängige Nachweise stale. |
| Amendment vorschlagen | Jede nicht abgeschlossene Phase → DRAFT, blocked | Aktive Arbeit stoppen/fencen; Änderung mit Grund, altem/neuem Soll und Impact vorlegen. Bloßer Vorschlag ist keine Freigabe. |
| Amendment autorisieren | DRAFT → READY, active | Neue unveränderliche Revision und unabhängige Befugnis; Oraclewirkung prüfen; kumulative Budgets bleiben erhalten. |
| Block / Stop / Cancel | Jede nicht abgeschlossene Phase, Phase bleibt | Grund festhalten. Block hat Resume-Bedingung; Stop/Cancel ist terminaler Nicht-Erfolg dieses Laufs. |
| Resume | blocked → früheste noch gültige Phase, active | Befugnisse, Basis, Effekte, Budget und Writer neu abgleichen; Generation erhöhen. |

Nicht aufgeführte Übergänge sind unzulässig. `VERIFIED` ist eine widerrufbare aktuelle Eigenschaft. `ACCEPTED` ist ein historischer Entscheidungsbeleg für einen exakten Stand, **keine ewige Eigenschaft des beweglichen Branches**. Spätere Änderungen eröffnen einen Nachfolger; Incident/Widerruf bleibt als neues Ereignis sichtbar. Die Demo fasst VERIFYING→VERIFIED→ACCEPTED in einer reinen Prüfentscheidung zusammen; sie persistiert diese Übergänge nicht.

## 3. Repair, Amendment oder Blocked?

**Repair:** Der Vertrag sagt „nur explizit public“, die Implementation lässt fehlende Labels durch. Code korrigieren, Regression ergänzen, dieselbe unabhängige Abnahme erneut ausführen. Neue Entwicklungstests sind erlaubt; geschützte Abnahme abschwächen ist kein Repair.

**Planrevision:** Zwei Tasks zusammenlegen, Hilfsfunktion umbenennen oder eine erlaubte Alternative wählen. Innerhalb des vorab delegierten Scopes ohne neue menschliche Bestätigung möglich. Der Plan ist eine Ableitung; Änderungen der Ausführungs-/Integrationsabhängigkeiten invalidieren seine Nachweise, nicht automatisch den ursprünglichen Intent.

**Amendment:** Die Anforderung verlangt jetzt zusätzlich JSONL, oder ein akzeptierter Test widerspricht nachweislich der Nutzerabsicht. Neue Sollrevision mit Entscheidung, nicht nachträglich alte Tests passend machen. Der Builder darf vorschlagen, aber **nicht in derselben Implementierungstransaktion Ziel, Oracle oder Gates zu seinen Gunsten abschwächen**. Ein unabhängiger, bereits delegierter Domain-Owner darf klar begrenzte Amendments autorisieren; nicht jede Laufzeitänderung braucht einen Human-Dialog. Scopeexpansion, neue Wirkung oder Policyausnahme außerhalb dieser Delegation braucht die zuständige Instanz. Eine geänderte Produktabsicht kann kein Safetyverbot überschreiben.

**Blocked:** Fachentscheidung fehlt, Oracle nicht verfügbar, Reviewer nicht autorisiert, Evidence fehlt, Budgetverbrauch unbekannt oder externer Effekt ungewiss. Ausgabe enthält Reasoncode, betroffene Verpflichtung, Witness und genau die Auflösebedingung. Kein „best effort done“.

**Stop:** Budget erschöpft, gleicher Fehler ohne neue Evidenz, Deadline oder Abbruch. Offene Anforderungen und brauchbare Teilresultate bleiben erhalten, aber kein Acceptance-Fallback.

## 4. Invalidierung als endlicher Abhängigkeitsgraph

```text
Originalauftrag → autorisierte Contractrevision + normative Spec
                     ├→ Plan / Tasks / Handoffs → Kandidat
                     └→ Abnahmemapping + freigegebenes Oracle
Basis + Kandidat + Integrationsentscheidung → tatsächlicher Integrationstree
Integrationstree + Oracle + Policy + Environment + Config + Commandversionen
  + effektive Instructions + Generation + echte Runbeobachtung
    → Checkreceipts → Review auf diesem Stand → Acceptance
Acceptance + gesonderte Releasebefugnis + Artefakt + Zielumgebung
    → Effectreceipt + Readback → Releaseentscheidung
```

Eine abgeleitete Aussage ist aktuell, wenn **alle** gebundenen Eingaben aktuell, zulässig und abrufbar sind. Contentgleichheit ersetzt keine Befugnis. Zeitstempel, Dateiname oder Taskanzahl ersetzen keine Contentidentität. Pflichtumfang kommt aus der autorisierten Checkliste, nicht aus dem zufällig gelieferten Report.

| Änderung | Was bleibt? | Was muss neu geprüft werden? |
|---|---|---|
| Contract/Spec/Non-goals/Acceptance | Originalauftrag, historische Belege, wiederverwendbare Codebytes | Autorisierung der Revision, Plan-/Testzuordnung, ganze Abnahme; DRAFT→READY. |
| Plan innerhalb Soll | Vertrag und Oracle | Taskcoverage, betroffene Outputs und Integration; konservativ ganze Changeabnahme. |
| Code, Entwicklungstests, Assets, Lockfile, kritische Config | Autorisierter Vertrag | Kandidat/Integration einfrieren, gesamte Ausführung und Review neu. |
| Zielbasis oder Merge-Tree | Patch als Material | Reconciliation, neue Integration, gesamte Pflichtsuite. Solotests der Worker reichen nicht. |
| Geschützte Tests/Oracle/Runner/Kommandosemantik | Code als Kandidat | Unabhängige Aufnahme der Änderung; Ausführung neu. Oracle-Semantikwechsel erzeugt neue Evaluationsepoche. |
| Environment/Toolversionen/effektive Instructions | Historischer Lauf | Neue Bindung und gesamte MVP-Abnahme; geänderte Umgebung bedeutet nicht automatisch falschen Code. |
| Policy/Delegation/Widerruf/Budget | Historische Entscheidungen | Neue Berechtigung, betroffene Gates und Effekte; bei Unklarheit blockieren. |
| Evidence fehlt, beschädigt oder Terminalzustand abweichend | Übrige Historie | Betroffene Aussage UNKNOWN, keine Abnahme. |

MVP-Regel: **ganze Changegeneration invalidieren**, wenn der Impact nicht vollständig bekannt ist. Selektive Testwiederverwendung ist eine spätere, selbst zu prüfende Optimierung. Nur ausdrücklich nichtnormative Kommentare außerhalb der Identitätsfläche dürfen ohne Retest wechseln. Keine heuristische Behauptung „nur kosmetisch“ für normative Spectexte.

Hashes werden nicht rekursiv über ihre eigenen Receipts gebildet: Quell-/Integrationstrees enthalten keine `.sdd/runs`-Ausgaben. Contractpayload ohne eigenes Digestfeld hashen; Receipt referenziert Inputdigests; Decision referenziert Receipt. Historische Eventketten zeigen nur rückwärts. Dateien nach rohen Bytes, Pfad und Modus identifizieren, einschließlich Hinzufügung/Löschung; formatspezifische Kanonisierung getrennt versionieren. Die Demo verwendet endliche inline JSON-Dateimaps, keine echte Git-Tree-Erfassung.

## 5. Begrenzung, Parallelität und Wiederaufnahme

Vorgeschlagene Normalpolicy: zwei Repair-Reservierungen, eine identische Infrastrukturwiederholung und vorab festgelegte Zeit-/Tool-/Tokenobergrenzen. Sämtliche Worker, verworfenen Versuche, Reviews und Amendments teilen dieses Budget. Restart setzt nichts zurück. Unbekannter Verbrauch blockiert neue Arbeit. Gleicher Befundfingerprint bei unveränderten relevanten Inputs stoppt als `NO_PROGRESS`; mehr Text ist kein Fortschritt. Flaky Checks benötigen vorab definierte Wiederholungs-/Aggregationsregeln und behalten Fehlläufe, statt bis zum ersten Grün zu würfeln.

Ein Integration Owner vergibt disjunkte Write-Sets und eine Generation mit Basisidentität. Workerantworten aus älteren Generationen werden quarantänisiert. Wiederverwendbare Patches werden ausdrücklich neu integriert, nie über die alte Receipt akzeptiert. Ein Konfliktfreier Merge ist nur ein Syntax-/Tree-Ergebnis, keine Verhaltensabnahme. Gemeinsame Interfaces brauchen mindestens einen kombinierten Entry-Point-Fall.

Für einen späteren lokalen Controller: unveränderliche Snapshots, exklusiver Writer, atomare Eventwrites und Sequenzprüfung unter Lock. Resume beendet/reconciliiert alte Writer oder nutzt einen frischen Workspace. Ein Lock nur um State-JSON schützt nicht vor einem alten Prozess, der Code weiter verändert. Ereignisse tragen ID, Payloaddigest, erwartete Sequenz, Actor, Generation und Budgetdelta; identische Retryevents wären idempotent, gleiche ID mit anderer Payload Konflikt. Diese Recoverymechanik ist **Design, nicht Demo-Implementation**.

## 6. Release ist ein eigener Wirkungsloop

`ACCEPTED → PREPARED → EXECUTING → OBSERVING → RELEASED`, nur mit separater capability. Release bindet Artefakt, Acceptance, Zielumgebung/Audience, Aktion/Argumente, Policyversion, Befugnis und Ablauf, Idempotency-Key, Payloaddigest und Rollback-/Kompensationsplan.

Vor Wirkung Intent dauerhaft speichern und Befugnis erneut prüfen. Danach exaktes Ziel und Gesundheit auslesen. Timeout/Crash zwischen Remotecommit und Receipt → `RECOVERY_REQUIRED`; Ziel und Operations-ID abgleichen, **kein blindes Retry**. Gleicher Key mit anderer Payload ist Konflikt. Nur nach bestätigter Nichtwirkung und weiterhin gültiger Befugnis darf eine zulässige Wiederholung erfolgen.

Fehlrelease: `ROLLING_BACK → ROLLED_BACK` erst nach bestätigtem Rückzustand; sonst `RECOVERY_REQUIRED`. Nicht reversible Datenmigration benötigt Restore/Forward-Compensation. Code-Rollback holt bereits kopierte öffentliche Daten nicht zurück. Widerruf braucht separaten Removal-/Purge-/Rebuildvertrag mit Grenzen. Ein Release-API-Erfolg allein genügt nicht. Die Demo führt keinerlei externe Effekte aus.

## 7. Harness-Evolution ohne Verschieben der Ziellinie

Nach Abschluss oder Stop: unveränderte Fehlerereignisse → Ursachenklasse → eine begrenzte Skill-/Regel-/Kontext-/Umgebungsänderung → gepaarter Vergleich mit unverändertem Incumbent → unabhängige Confirmation → übernehmen oder verwerfen → versioniert ausrollen, rollbackfähig halten.

Produktrepair ist keine Harnessverbesserung, eine Harnessverbesserung kein Beweis rekursiv besserer Optimierung. Der Optimizer darf Budget, Oracle, Berechtigungen oder Recoveryledger nicht mitoptimieren. Sichtbare Entwicklungsevidenz und unabhängige Promotionsdaten trennen; nicht jeden Einzelfehler als dauerhafte Always-loaded-Regel konservieren.

Zu messen wären vollständige Abnahmen, falsches Done, stale Acceptances, Scope-/Safetyverletzungen, Reviewzeit, Nacharbeit, Gesamtkosten, Latenz und False-Blocks. Gleiche Aufgaben, Modelle, Baselines, effektive Instruktionen, Budgets und unabhängige Abnahme; Wiederholungen und Unsicherheit berichten. Diese Messung wurde nicht durchgeführt. Der Entwurf darf verworfen werden, wenn er bestehende CI nur dupliziert oder ohne zusätzliche Fehlererkennung mehr Freigabelast erzeugt.
