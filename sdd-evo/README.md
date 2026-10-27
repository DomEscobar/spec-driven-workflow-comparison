# SDD-evo Framework

SDD-evo ist der Name dieses eigenen Entwurfs; „Evidence-bound SDD“ bezeichnet sein Grundprinzip. Dieses Paket ergänzt den OpenSpec-/Spec-Kit-Vergleich, ersetzt ihn aber nicht.

**Ein vorgeschlagener, evidenzgebundener Entwicklungsloop — kein nachgewiesen überlegenes Produkt.** Arbeitsstand: konsolidierter Entwurf auf Basis des Quellenstands 2026-10-27. Enthalten ist ein ausgeführter Python-Referenzdemonstrator für Konsistenzregeln, keine Agentenruntime und kein produktiver Sicherheitsdienst.

## Entscheidung

Wir bauen nicht den längsten Spec-Prozess. Wir definieren, **wann eine konkrete Lieferung unter einer autorisierten Absicht tatsächlich als abgenommen gelten darf — und wann diese Aussage veraltet ist**. Planung bleibt flexibel; die Abnahmebasis nicht heimlich veränderbar.

Die kleinste Einheit ist ein Change mit **Vertrag, begrenztem Kandidaten und versionsgebundenem Nachweis**. Bestehendes Ticket, OpenSpec oder Spec Kit können die Eingabe liefern. Ein kleiner Gateadapter zu vorhandenen Tests/CI wäre der vorgeschlagene technische Kern. Keine Datenbank, Vektorsuche, Swarm-Plattform oder neue Modellinstallation ist erforderlich.

## Der vollständige Loop

```text
Auftrag + Istzustand + Befugnis + Risikoprofil
  → Vertrag: Ergebnis, Non-goals, Alternativen, Prüfkriterien, Grenzen
  → Baseline: echte Fehler, Teststärke, Versionen, verfügbare Budgets
  → begrenzte Umsetzung und Entwicklungstests
  → alle Teile auf aktueller Basis integrieren, Ergebnis einfrieren
  → unabhängige Checks + Intent-/UX-Review genau dieses Ergebnisses
  → Befund klassifizieren:
       Implementierungsfehler → REPAIR, gleiche Absicht, begrenztes Budget ↺
       Solländerung/Oraclefehler → AMENDMENT, getrennte Autorisierung ↺
       fehlende Evidenz/Befugnis → BLOCKED, benannte Auflösebedingung
       keine Fortschritte/Budgetende → STOPPED, ehrlicher Nicht-Erfolg
       vollständig und frisch → ACCEPTED für genau diesen Stand
  → optional: gesonderte Releasebefugnis → Wirkung → Readback → RELEASED
       Wirkung ungewiss → RECONCILIATION, niemals blind wiederholen
  → Beobachtung → Fehlerursache → separater Harness-Verbesserungsloop
```

**Drei Unterscheidungen tragen den Entwurf:**
- *Planänderung* innerhalb delegierter Grenzen ist normal; *Amendment* ändert die autorisierte Sollbasis; *Repair* behebt einen Fehler unter unverändertem Soll.
- *Worker fertig*, *integriert*, *verifiziert*, *abgenommen* und *veröffentlicht* sind verschiedene Aussagen.
- *Struktur gültig*, *Tests ausgeführt*, *Verhalten ausreichend belegt*, *Freigabe autorisiert* und *Wirkung bestätigt* sind verschiedene Nachweise.

## Nicht für jeden Fix dieselbe Zeremonie

| Profil (vorgeschlagen) | Minimaler Ablauf | Harte Grenze |
|---|---|---|
| **Korrektur-Fast-Lane** | Ticket als Kurzvertrag, enger Diff, vorhandener relevanter Check und Diff-/Darstellungsreview; ein Task genügt | Nur bekannte Absicht, reversible lokale Änderung, keine Auth-/Privacy-/Effektänderung. Ein begrenzter Reparaturversuch; danach neu klassifizieren, nicht endlos nachbessern. |
| **Normales Feature** | Ergebnisvertrag mit IDs, positive/negative/kombinierte Fälle, Plan nur soweit nötig, vollständige Integration und Review | Zwei Reparaturen und eine Infrastrukturwiederholung als expliziter Startvorschlag; echte Versionen und kumulatives Budget. |
| **Riskante externe Wirkung** | Zusätzlich unabhängige Befugnisprüfung, geschütztes Oracle, Effect-Ledger, Readback, Recovery-/Kompensationsplan | Veröffentlichung, Migration, Rechteänderung oder neue Kosten nicht aus erfolgreicher Abnahme ableiten. Unknown stoppt weitere Wirkung. |

Konkrete Zeit-/Tool-/Tokenobergrenzen legt der Auftraggeber oder eine vorher delegierte Policy **vor Beginn** fest. Fehlen sie bei autonomen Wiederholungen, bleibt der Start blockiert. Die Rundenzahlen sind konservative Designwerte, keine empirischen Optima. Auch bei erreichtem Reparaturlimit darf ein bereits fertig geprüfter Kandidat abgenommen werden; verboten ist die nächste unreservierte Reparatur.

## Wozu dieser Zusatz — und wann nicht?

Der Entwurf adressiert fünf konkrete Fehlerklassen: alte Tests nach Specänderung, Grün auf einem anderen Tree, selbst abgeschwächte Abnahme, unvollständige Parallelresultate und unbeabsichtigte externe Wirkung. Seine vorgeschlagene Stärke liegt in expliziten Abhängigkeiten und Entscheidungen, nicht in schöneren Prompts. TestSuiteBench/SpecBench motivieren stärkere unabhängige Tests; SGE/Consort motivieren deterministische Zustände und Artefaktbindung. Keine dieser Quellen beweist den Nutzen unseres Gesamtloops ([Evidenz](EVIDENCE.md)).

Ein gut gepflegtes Ticket plus geschützte CI und Review kann bereits genügen. Dann nur die fehlende Bindung ergänzen, keine parallele Prozessplattform schaffen. Für explorative Prototypen ohne stabile Ziele zunächst Exploration ausweisen, nicht einen Scheinvertrag einfrieren. Für subjektives Design fachliche Beurteilung erhalten; maschinelle Tests ersetzen weder Verständlichkeit noch Nutzerführung.

## Inhalt und Lesereihenfolge

1. [FRAMEWORK.md](FRAMEWORK.md): Zustandsautomat, Invalidierung, Reparatur-/Änderungslogik, Release und Evolution.
2. [ARTIFACTS.md](ARTIFACTS.md): kleinste Verträge, Autoritäten, Nachweise und ausführbarer Demo-Umfang.
3. [COMPARISON.md](COMPARISON.md): OpenSpec, Spec Kit und unser Vorschlag mit passenden/unpassenden Bedingungen.
4. [EXAMPLE.md](EXAMPLE.md): ein durchgehender synthetischer Public-Export mit Amendment und Parallelfehler.
5. [EVIDENCE.md](EVIDENCE.md): öffentliche Primärquellen, Pins, Claimgrenzen.
6. [docs/VERIFICATION.md](docs/VERIFICATION.md): tatsächlich ausgeführte Tests und CLI-Ausgaben.

## Jetzt ausführbar: nur der Konsistenzdemonstrator

Im Verzeichnis dieses Pakets, Python 3 mit Standardbibliothek:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/sdd_gate.py --demo --approved fixtures/approved.json --current fixtures/current.json --evidence fixtures/evidence.json
python3 scripts/sdd_gate.py --demo --approved fixtures/approved.json --current fixtures/stale-current.json --evidence fixtures/evidence.json
```

Der letzte Aufruf soll mit Exitcode **3** blockieren. Die JSON-Fixtures sind ausdrücklich **synthetisch**, insbesondere ihre PASS-Belege. Der Demonstrator prüft deren Konsistenz, führt aber keine Anwendungstests aus und authentifiziert keinen Runner. `ACCEPTED` bedeutet hier nur: die modellierten Regeln lassen diesen Fixture-Satz passieren. Alle Ergebnisse enthalten `released: false`.

## Kleinster weiterer Implementierungsplan — nicht ausgeführt

1. Vorhandene CI liest autorisierten Vertrag und geschützte Checkliste, baut einen eingefrorenen Integrationstree; Builder kann diese Quellen nicht ersetzen.
2. Ein Adapter erfasst tatsächliche Ausführung, Testdiscovery, Umgebungs-/Toolidentität, Logs und Reviewentscheidung; er erzeugt die Receipt selbst.
3. Ein obligatorischer Aggregator prüft Frische und Vollständigkeit am exakten Mergeziel. Required Checks ohne Builder-Bypass sperren die Wirkung; skipped/neutral genügt dem Aggregator nicht.
4. Erst bei Bedarf haltbare Ereignisse, Wiederaufnahme und separate Releaseintegration hinzufügen. Parallelität erst bei belegtem Engpass; kein Pflichtteam.

**Nicht geliefert:** Produktionsruntime, Sandbox, Signaturdienst, externe CI-/Branch-Konfiguration, echte Public-Export-App, Deployment oder Benchmark. Das Designpaket wird im bestehenden Vergleichsrepository versioniert; das ist keine Produktivfreigabe. Gleicher Unix-User plus freie Shell ist **keine Sicherheitsgrenze**. Bessere Produktivität, weniger Fehler und geringerer Reviewaufwand bleiben zu prüfende Hypothesen.
