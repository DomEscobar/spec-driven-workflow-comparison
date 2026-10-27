# Evidenz, Ableitung und Grenzen

> **Einordnung:** Dieses Dokument beschreibt den ursprünglichen Design-/Demo-Stand. Der jetzt ausführbare, bewusst kleinere lokale MVP ist im [Quickstart](README.md) und [MVP-Prüfbericht](docs/MVP-VERIFICATION.md) abgegrenzt; der Entwurf ist nicht vollständig implementiert.

[Übersicht](README.md) · Quellenstand der abgeschlossenen Recherche: **2026-10-27**. Diese Konsolidierung erweitert die Recherche nicht. Die öffentlichen Quellen wurden in den vorangehenden Workstreams geprüft; hier wurden deren vollständige Reports und Inventare ausgewertet. Kein neuer Frameworklauf oder Paperbenchmark wird behauptet.

## Claim-Regeln

- **Befund:** Was Primärtext oder begrenzte statische Codeinspektion tatsächlich sagt.
- **Autorenresultat:** Fremdes Experiment, nicht von uns reproduziert.
- **Design:** Unsere vorgeschlagene Übertragung, nicht als Quellenfeature oder Wirksamkeitsnachweis ausgegeben.
- **Ausgeführt:** Nur die in [VERIFICATION](docs/VERIFICATION.md) dokumentierten lokalen Konsistenztests/CLI-Aufrufe. Synthetische Fixtures sind keine echten Pipelineattestationen.

„Evidence-bound SDD“ ist ein Arbeitsname für diese Kombination, **kein Neuheitsanspruch**. Eine vollständig neue Zustandsbenennung ist kein wissenschaftlicher Fortschritt. Öffentliche Primärquellen tragen die hier aufgeführten Claims; private Quelltexte, Brain-Auszüge, interne IDs und rohe Forschungstraces sind nicht Bestandteil dieses Pakets.

## Entscheidungsbezogene Evidenz

| Eigene vorgeschlagene Entscheidung | Öffentliche Grundlage | Grenze / Gegenargument |
|---|---|---|
| Kleine deterministische Gültigkeitsprüfung unter flexibler Planung | S03 deterministischer Validator und Lifecycle; S04 artefaktgebundene Gates | Lokale Marker/Hashhelper sind kein nachgewiesenes End-to-End-Enforcement. Unsere konkrete Zustands-/Invalidierungssemantik ist Design. |
| Unabhängige Acceptance und starke Negativ-/Kombinationsfälle | S05 trennt adaptives Entwicklungsfeedback und Audit; S06 Testvalidität ≠ Teststärke; S07 sichtbare Tests ≠ Generalisierung | Endliche Tests beweisen keine Vollständigkeit, falsches Oracle bleibt möglich. Kein universeller Vorteil zusätzlicher Testeragenten. |
| Rohe Contentbindung, echte Producer-/Subjectidentität | S04 Hashbindung; S11 Subject/Dependencies/Builder; S08 Hostdurchsetzung | Ein Digest authentifiziert keinen Actor; erfundene PASS-JSON bleibt erfunden. |
| Finale Integration statt Worker-Done | S11 Subjectbindung, S12 Checks auf relevantem Stand; konkrete Integrationsgegenbeispiele unseres Entwurfs | Kein hier gemessener Parallelitätsgewinn oder natürliche Fehlerquote. |
| Unknown/skip blockiert Pflichtabnahme | S12 kann skipped/neutral als akzeptable Statuszustände behandeln; deshalb eigener strenger Aggregator vorgeschlagen | Das verschärft die Teamabnahme; ist nicht automatisch GitHub-Default. |
| Release/Reconciliation separat | S10 dokumentiert Replay/Taskgrenzen; S08 liefert Entscheidung, Host muss Wirkung kontrollieren | Historische LangGraph-Doku, kein aktueller Runtimeaudit. Genaues Effect-Ledger ist eigener Entwurf. |
| Zulässige Alternativen und UX-Review erhalten | Produkt-Szenarien/Stories S01/S02; semantische Oraclegrenzen S06/S07 | Kein maschineller Komplettnachweis subjektiver Qualität; Rubrik braucht verantwortliche Beurteilung. |
| Fast Lane, konservative Gesamtinvalidierung und begrenzte Runden | Architekturentscheidung zur Begrenzung von Aufwand und Fehlfreigaben | Kein empirisch optimales Rundenziel, keine gemessene Wirtschaftlichkeit. |

## Quellenregister mit Pins und Prüftiefe

### S01 — OpenSpec

[Repository am Commit `6d04a1b58dedc95729d34e4f223d9d483aae210a`](https://github.com/Fission-AI/OpenSpec/tree/6d04a1b58dedc95729d34e4f223d9d483aae210a), insbesondere [Verify-Template](https://github.com/Fission-AI/OpenSpec/blob/6d04a1b58dedc95729d34e4f223d9d483aae210a/src/core/templates/workflows/verify-change.ts).

Übernommener gepinnter Produkt-/CLI-/Templateaudit aus dem Vergleichsdossier, ergänzend begrenzte Verify-Templateprüfung im Designworkstream. Capability-Hauptspecs, Deltas, Sync/Archive; beratendes Verify neben echten lokalen Strukturprüfungen. Nicht erneut installiert/ausgeführt. Kein Produktivitätsbenchmark und keine Behauptung über alle Erweiterungen.

### S02 — GitHub Spec Kit

[Repository am Commit `ee94598c3c87ae231027b22fb2be2b5a13e8820f`](https://github.com/github/spec-kit/tree/ee94598c3c87ae231027b22fb2be2b5a13e8820f), insbesondere [Converge-Template](https://github.com/github/spec-kit/blob/ee94598c3c87ae231027b22fb2be2b5a13e8820f/templates/commands/converge.md).

Übernommener Produkt-/Template-/Prerequisiteaudit; Converge-Template vollständig im Designworkstream gelesen. Append-only korrektive Tasks, kein Umschreiben von Spec/Plan durch Converge. Agentenurteil und konfigurierte Workflowgates unterscheiden. Keine Ausführung; installierte Overrides können vom Upstream abweichen.

### S03 — Spec Growth Engine

[Paper 2610.11725v1](https://arxiv.org/abs/2610.11725v1); [Code `242e0d10f38be11c2970b209a8de37635a589704`](https://github.com/grabow/spec-growth-engine/tree/242e0d10f38be11c2970b209a8de37635a589704). Methoden-/Ausführungs-/Beispielabschnitte und eng begrenzt `cockpit/engine/{evidence,lifecycle,migration}.py` geprüft.

Befund: deterministischer Boden, positive Testevidenz für verified und differenzierte Konvergenzausgänge. Grenzen: heuristische Importauflösung, lokale Vertrauensmarker und mtime-basierte Frische. Kleines Beispiel belegt nicht allgemeine Wirksamkeit. Übernommen wird das Prinzip, nicht die ganze Plattform.

### S04 — Consort

[Paper 2609.09671v1](https://arxiv.org/abs/2609.09671v1); [Code `ff864c7756f4c39ac2510cd4decff3303f5eaaf3`](https://github.com/databricks-solutions/consort/tree/ff864c7756f4c39ac2510cd4decff3303f5eaaf3). Methodenabschnitte IV-D–IV-G/VI sowie `gate-hash.ts`, `approve-gate.ts`, `verify-gate-integrity.ts` vollständig gezielt geprüft.

Befund: Artefaktnamen-/Hashbindung und Approvals. Grenzen: `hitlApproved`-Boolean ist kein Authentifizierungsbeweis; Integrityhelper delegiert Durchsetzung an Caller; Whitespace-/Zeilenendennormalisierung nicht universell semantikerhaltend. Qualitätsvergleich laut Paper zukünftige Arbeit. DB-Branches nicht als Pflicht übernommen.

### S05 — GTDD

[Paper 2610.02952v1](https://arxiv.org/abs/2610.02952v1), Methoden, Ergebnisse und relevante Appendices geprüft. Kein zurechenbarer Runner aus den geprüften Paperlinks verifiziert; keine Aussage, dass keiner existiere.

Autorenexperiment: ein Key-Value-Store, 30 gepaarte Startmodule, vier Codingrunden. Adaptive Fälle versus statische LLM-Fälle zeigen unter diesem Setup Vorteile; **kein nachweisbarer Vorsprung gegenüber Static property und kein nachweisbarer Zusatznutzen von Tester-Codezugriff**. Unterschiedliche angeforderte Fallbudgets und kaputte Endmodule begrenzen den Vergleich. In den Trajektorien lief keine aktive Acceptance-Gate. Keine pauschale Sicherheitsgarantie auf unser Framework übertragen.

### S06 — TestSuiteBench

[Paper 2610.13065v1](https://arxiv.org/abs/2610.13065v1); [Code `583d2eb1ffa19f3aa0c04b7455fd13d846b4c8d9`](https://github.com/eth-sri/testsuitebench/tree/583d2eb1ffa19f3aa0c04b7455fd13d846b4c8d9). Methoden, Hauptresultate, Limitationen/Appendix C und `src/programbench/eval/test_suite_eval.py` gezielt geprüft.

Autorenbefund: starke Testvalidität kann mit wesentlich schwächerer Mutationserkennung einhergehen. Referenzabgeleitete Specs/Mutanten und kompilierte CLI-Anwendungen begrenzen Transfer. Evaluator-Konstruktordefault ein Referenzlauf versus drei im Paper; tatsächliche experimentelle Aufrufkonfiguration nicht vollständig zurückverfolgt. Kein eigener Benchmarklauf.

### S07 — SpecBench

[Paper 2605.21384v2](https://arxiv.org/abs/2605.21384v2), Revision vom 2026-09-09; Methoden, Aufgabenaufteilung, Fallstudien und Grenzen geprüft. Sichtbare Einzelmerkmale und verborgene Kombinationen zeigen mögliche Scheinerfolge. Ein Holdoutgap beweist weder Absicht noch vollständige Fehlerfreiheit; niedrige Werte auf beiden Seiten können ebenfalls kleinen Gap ergeben. Ungeklärte Inkonsistenz in der Autoren-Budgettabelle; daher keine aggregierten Kostenränge übernommen. Kein Benchmarkrunner verifiziert oder ausgeführt.

### S08 — ToolContractGate

[Paper 2610.33108v1](https://arxiv.org/abs/2610.33108v1); [papergebundener Code `3eb1f67fe951a55339265b3b7765293581484d1a`](https://github.com/sachinkg12/toolcontractgate/tree/3eb1f67fe951a55339265b3b7765293581484d1a). Paper, `ToolContractGate.java` und archivierte `experiments/results.csv` geprüft.

Der Rechercheworkstream hat Archivzahlen mit Standardbibliothek nachgerechnet, **keinen neuen Gatewaylauf** gemacht. Konstruierte Cases, keine Produktionsaufgaben; Konfigurationszellen sind keine unabhängigen Workloads. Kein Provenienz-Mismatch im Korpus, Boot-Provenienzcache und optionale Metadatenpfade begrenzen Claims. `/v1/decide` liefert eine Entscheidung; tatsächliche Sperre ist Hostaufgabe.

### S09 — Hypothesis Stateful Testing

[Offizielle Dokumentation](https://hypothesis.readthedocs.io/en/latest/stateful.html), gelesen am 2026-10-27; mutable `latest`, **keine gepinnte Paketversion**. Regeln, Bundles, Invarianten und Shrinking unterstützen einfachen zustandsbasierten Testentwurf. Nicht installiert/ausgeführt. Metamorphe Relationen sind eigene zu autorisierende Annahmen, kein magischer Oracleersatz.

### S10 — LangGraph Durable Execution, historische Dokumentation

[Offizielle Quelldatei am Commit `5504076ee518b090577efb8f01cb505dc93570b5`](https://github.com/langchain-ai/docs/blob/5504076ee518b090577efb8f01cb505dc93570b5/src/oss/langgraph/durable-execution.mdx). Historischer Stand 2026-05-12, verwendet weil der aktuelle Pfad umleitete. Replay ist keine Fortsetzung exakt an der Abbruchzeile; Seiteneffekte/Taskgrenzen und Persistenzmodi unterscheiden. Kein Claim über aktuelle Runtimeausführung.

### S11 — SLSA Build Provenance v1.2

[Versionierte Primärspezifikation](https://slsa.dev/spec/v1.2/build-provenance), Predicate `https://slsa.dev/provenance/v1`. Subject, Builddefinition, Dependencies, Builder und Runmetadaten unterscheiden. Provenienz ersetzt weder fachliche Korrektheit noch Intentfreigabe. Das Paket beansprucht **kein SLSA-Level** und betreibt keinen Attestationdienst.

### S12 — GitHub Protected Branches

[Offizielle Dokumentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches), gelesen am 2026-10-27; mutable Docs ohne Releasepin. Required Checks, erwartete Statusquelle, stale Approvals und Merge Queue. Bypassrechte und Repository-/Accountkonfiguration separat prüfen. Kein Live-Regelaudit, keine Konfigurationsänderung erfolgt.

## Verbleibende Unsicherheit

Hohe Zuversicht gilt der logischen Notwendigkeit konsistenter Subject-/Inputbindung, nicht automatisch unserer konkreten Implementation. Mittlere Zuversicht gilt der Passung eines kleinen Adapters für ein Team mit bestehender CI. Unbekannt sind Pflegeaufwand, False-Block-Rate, Reviewlast, Sicherheitswirksamkeit gegen einen adversarialen Agenten und Netto-Produktivitätsgewinn. Kein Studienergebnis ersetzt die Prüfung der tatsächlichen Credential-/Runner-/Mergegrenze. Dieses Paket ist ein konsolidierter Designvorschlag mit lokal geprüfter Modelllogik, keine Produktionsfreigabe.
