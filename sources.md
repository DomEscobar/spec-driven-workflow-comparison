# Quellen, Stand und Lesetiefe

Stand: **27. Oktober 2026**, erste HEAD-Abfrage 06:49:54 UTC. Beide HEADs wurden mit `git ls-remote … HEAD` ermittelt und als getrennte, flache Git-Checkouts gelesen. Die Pins sind Quellstände, **keine Behauptung über die installierte oder veröffentlichte Paketversion**.

| Projekt | Vollständiger Git-Pin |
|---|---|
| Fission-AI/OpenSpec | `6d04a1b58dedc95729d34e4f223d9d483aae210a` |
| github/spec-kit | `ee94598c3c87ae231027b22fb2be2b5a13e8820f` |

## Evidenzregeln

- **Quellenbefund:** Dokumentation oder Prompt beschreibt Verhalten; Quellcode zeigt einen konkreten Kontrollpfad. Das beweist noch nicht, dass ein Agent die Anweisung befolgt.
- **Ableitung/Bewertung:** Unsere bedingte Einschätzung für den angegebenen Anwendungsfall, kein Herstellerbenchmark.
- **Ausgeführt:** Nur die in [Verifikation](docs/verification.md) protokollierten Repository-/Dokumentationsprüfungen. Kein Framework installiert, kein fremder Projektcode ausgeführt, kein Produktworkflow oder Benchmark nachgestellt.
- Registry maschinenlesbar: [evidence/sources.json](evidence/sources.json). Zeilenbereiche kennzeichnen die tatsächlich gelesenen Teile; ein Quellenlink bedeutet keinen Vollaudit des Repositories.
- Dieses Dossier enthält ausschließlich eigenständig formulierte Synthese öffentlicher Primärquellen und ein synthetisches Beispiel. Keine internen Brain-Dokumente, Chats, Betriebsdaten oder Hersteller-Codekopien. Ein interner Wissensabgleich ist keine zitierbare öffentliche Evidenz und wurde nicht exportiert.

## Dokumentationsunterschiede, die relevant sind

1. **OpenSpec hat zwei Dokumentationsbäume am selben Pin.** `docs-lab/README.md` sagt, dass die Website aus `docs-lab/` entsteht; `docs/` ist älteres Quellenmaterial. Deshalb wird der aktuelle Quickstart zusätzlich zu detaillierten alten Referenzen und konkreten Templates gelesen. Plain-Language-Beispiele im neuen Quickstart ersetzen nicht die integrationsabhängige Kommandosyntax. [O9](#o9), [O10](#o10), [O1](#o1).
2. **„Archive aktualisiert die Specs“ ist der Normalfall, keine Invariante.** Der Quickstart vereinfacht; das Skill-Template bietet explizit Archivieren ohne Sync und Fortfahren nach Warnungen. Der direkte CLI-Pfad besitzt andere, teilweise blockierende Prüfungen. [O10](#o10), [O3](#o3), [O4](#o4).
3. **OpenSpec-Design ist kontextabhängig, aber Schema-Abhängigkeiten sind real.** Der Quickstart und die Schema-Prosa beschreiben Design nach Bedarf; im gelesenen Standardschema hängt `tasks` dennoch von `specs` und `design` ab. Nicht blind Dateien weglassen: aufgelösten Status prüfen bzw. Schema bewusst anpassen. Kein Laufzeittest dieses Randfalls. [O2](#o2), [O10](#o10).
4. **Spec-Kit-Templates tragen noch „Feature Branch“/„Branch“ als Metadaten.** Der aktuelle Quickstart und Python-Resolver bestimmen die aktive Feature-Auswahl dagegen über `.specify/feature.json` oder `SPECIFY_FEATURE_DIRECTORY`, nicht den ausgecheckten Git-Branch. Ein Feldname ist kein Routing-Beweis. [S1](#s1), [S6](#s6), [S9](#s9), [S11](#s11).
5. **Constitution-Pfade nicht ungeprüft aus einzelnen Prompts übernehmen.** `constitution` schreibt `.specify/memory/constitution.md`; andere gelesene Prompts enthalten `/memory/constitution.md`. Dies ist eine sichtbare Inkonsistenz der Quelltexte. Für einen Pilot die tatsächlich erzeugten Agent-Dateien und den geladenen Pfad prüfen; hier keine Behauptung, die Installation behebe dies automatisch. [S12](#s12), [S2](#s2), [S3](#s3).
6. **„Full SDD Cycle“ ist nicht identisch mit dem vollen Quickstart.** Die mitgelieferte Workflow-YAML führt specify/plan/tasks/implement mit Review-Gates aus, enthält aber nicht automatisch alle clarify/checklist/analyze/converge-Schritte. [S13](#s13), [S1](#s1).
7. **„Tests first“ ist keine allgemeine Testgarantie.** Implement enthält Testreihenfolge-Anweisungen; das Task-Template nennt Tests explizit optional, sofern nicht angefordert. Testpflicht gehört in die eigene Spec und in ausführbare Gates. [S4](#s4), [S10](#s10).

## Quellenregister

<a id="o1"></a>

### O1 — Kommandos, Syntaxvarianten, core/optional, sync/archive

- Primärquelle am Pin: [docs/commands.md](https://github.com/Fission-AI/OpenSpec/blob/6d04a1b58dedc95729d34e4f223d9d483aae210a/docs/commands.md)
- Gelesen: 1-779. Status: **quellengeprüft, nicht ausgeführt**.

<a id="o2"></a>

### O2 — Artefakte, Anforderungen, Szenarien, Abhängigkeiten

- Primärquelle am Pin: [schemas/spec-driven/schema.yaml](https://github.com/Fission-AI/OpenSpec/blob/6d04a1b58dedc95729d34e4f223d9d483aae210a/schemas/spec-driven/schema.yaml)
- Gelesen: 1-272. Status: **quellengeprüft, nicht ausgeführt**.

<a id="o3"></a>

### O3 — Skill-Prompt, Bestätigungen, Sync und Verschieben; Command-Hälfte nicht geprüft

- Primärquelle am Pin: [src/core/templates/workflows/archive-change.ts](https://github.com/Fission-AI/OpenSpec/blob/6d04a1b58dedc95729d34e4f223d9d483aae210a/src/core/templates/workflows/archive-change.ts)
- Gelesen: 1-240. Status: **quellengeprüft, nicht ausgeführt**.

<a id="o4"></a>

### O4 — CLI-Validierung, Task-Bestätigung, Merge-Vorprüfung; kein Vollaudit

- Primärquelle am Pin: [src/core/archive.ts](https://github.com/Fission-AI/OpenSpec/blob/6d04a1b58dedc95729d34e4f223d9d483aae210a/src/core/archive.ts)
- Gelesen: 1296-2000. Status: **quellengeprüft, nicht ausgeführt**.

<a id="o5"></a>

### O5 — Advisory-Prüfung, drei Dimensionen, Evidenzgrenzen

- Primärquelle am Pin: [src/core/templates/workflows/verify-change.ts](https://github.com/Fission-AI/OpenSpec/blob/6d04a1b58dedc95729d34e4f223d9d483aae210a/src/core/templates/workflows/verify-change.ts)
- Gelesen: 1-155. Status: **quellengeprüft, nicht ausgeführt**.

<a id="o6"></a>

### O6 — Kontext, Regeln, advisory guidance, Schemas

- Primärquelle am Pin: [docs/customization.md](https://github.com/Fission-AI/OpenSpec/blob/6d04a1b58dedc95729d34e4f223d9d483aae210a/docs/customization.md)
- Gelesen: 1-190. Status: **quellengeprüft, nicht ausgeführt**.

<a id="o7"></a>

### O7 — validate und archived-Scope

- Primärquelle am Pin: [docs/cli.md](https://github.com/Fission-AI/OpenSpec/blob/6d04a1b58dedc95729d34e4f223d9d483aae210a/docs/cli.md)
- Gelesen: 578-667. Status: **quellengeprüft, nicht ausgeführt**.

<a id="o8"></a>

### O8 — Installationswege; gezielte Textsuche, kein Installationsversuch

- Primärquelle am Pin: [docs/installation.md](https://github.com/Fission-AI/OpenSpec/blob/6d04a1b58dedc95729d34e4f223d9d483aae210a/docs/installation.md)
- Gelesen: Suche: Installation, Node, npm, Version. Status: **quellengeprüft, nicht ausgeführt**.

<a id="o9"></a>

### O9 — Dokumentationsmigration und Website-Quelle

- Primärquelle am Pin: [docs-lab/README.md](https://github.com/Fission-AI/OpenSpec/blob/6d04a1b58dedc95729d34e4f223d9d483aae210a/docs-lab/README.md)
- Gelesen: 1-130. Status: **quellengeprüft, nicht ausgeführt**.

<a id="o10"></a>

### O10 — Aktueller Quickstart, Review, Archiv und Aufbewahrung

- Primärquelle am Pin: [docs-lab/start/quickstart.md](https://github.com/Fission-AI/OpenSpec/blob/6d04a1b58dedc95729d34e4f223d9d483aae210a/docs-lab/start/quickstart.md)
- Gelesen: 1-187. Status: **quellengeprüft, nicht ausgeführt**.

<a id="o11"></a>

### O11 — Core und optionale Workflows; Profile und Delivery

- Primärquelle am Pin: [docs-lab/customize/profiles.md](https://github.com/Fission-AI/OpenSpec/blob/6d04a1b58dedc95729d34e4f223d9d483aae210a/docs-lab/customize/profiles.md)
- Gelesen: 1-88. Status: **quellengeprüft, nicht ausgeführt**.

<a id="s1"></a>

### S1 — Kompletter Quickstart einschließlich converge und Feature-State

- Primärquelle am Pin: [docs/quickstart.md](https://github.com/github/spec-kit/blob/ee94598c3c87ae231027b22fb2be2b5a13e8820f/docs/quickstart.md)
- Gelesen: 1-181. Status: **quellengeprüft, nicht ausgeführt**.

<a id="s2"></a>

### S2 — Append-only-Vertrag und vier Gap-Typen

- Primärquelle am Pin: [templates/commands/converge.md](https://github.com/github/spec-kit/blob/ee94598c3c87ae231027b22fb2be2b5a13e8820f/templates/commands/converge.md)
- Gelesen: 1-279. Status: **quellengeprüft, nicht ausgeführt**.

<a id="s3"></a>

### S3 — Read-only-Analyse, Coverage und Empfehlung statt Merge-Sperre

- Primärquelle am Pin: [templates/commands/analyze.md](https://github.com/github/spec-kit/blob/ee94598c3c87ae231027b22fb2be2b5a13e8820f/templates/commands/analyze.md)
- Gelesen: 55-244. Status: **quellengeprüft, nicht ausgeführt**.

<a id="s4"></a>

### S4 — Checklist-Gate, Zustimmung, Task-Ausführung und Hooks

- Primärquelle am Pin: [templates/commands/implement.md](https://github.com/github/spec-kit/blob/ee94598c3c87ae231027b22fb2be2b5a13e8820f/templates/commands/implement.md)
- Gelesen: 55-209. Status: **quellengeprüft, nicht ausgeführt**.

<a id="s5"></a>

### S5 — Datei-/Plan-Prüfungen; restliche Ausgabe nicht auditiert

- Primärquelle am Pin: [scripts/python/check_prerequisites.py](https://github.com/github/spec-kit/blob/ee94598c3c87ae231027b22fb2be2b5a13e8820f/scripts/python/check_prerequisites.py)
- Gelesen: 1-260. Status: **quellengeprüft, nicht ausgeführt**.

<a id="s6"></a>

### S6 — Feature-State, Override, No-persist

- Primärquelle am Pin: [scripts/python/common.py](https://github.com/github/spec-kit/blob/ee94598c3c87ae231027b22fb2be2b5a13e8820f/scripts/python/common.py)
- Gelesen: 79-190. Status: **quellengeprüft, nicht ausgeführt**.

<a id="s7"></a>

### S7 — Aufrufsyntax, Integrationen, Trust-Grenze

- Primärquelle am Pin: [docs/integrations/cli.md](https://github.com/github/spec-kit/blob/ee94598c3c87ae231027b22fb2be2b5a13e8820f/docs/integrations/cli.md)
- Gelesen: 1-190. Status: **quellengeprüft, nicht ausgeführt**.

<a id="s8"></a>

### S8 — Extensions, Presets, Overrides, Workflows und Bundles

- Primärquelle am Pin: [docs/guides/customization.md](https://github.com/github/spec-kit/blob/ee94598c3c87ae231027b22fb2be2b5a13e8820f/docs/guides/customization.md)
- Gelesen: 1-119. Status: **quellengeprüft, nicht ausgeführt**.

<a id="s9"></a>

### S9 — Plan, Constitution-Check, ergänzende Artefakte

- Primärquelle am Pin: [templates/plan-template.md](https://github.com/github/spec-kit/blob/ee94598c3c87ae231027b22fb2be2b5a13e8820f/templates/plan-template.md)
- Gelesen: 1-113. Status: **quellengeprüft, nicht ausgeführt**.

<a id="s10"></a>

### S10 — Story-Tasks, Parallelmarker, Tests optional

- Primärquelle am Pin: [templates/tasks-template.md](https://github.com/github/spec-kit/blob/ee94598c3c87ae231027b22fb2be2b5a13e8820f/templates/tasks-template.md)
- Gelesen: 1-120. Status: **quellengeprüft, nicht ausgeführt**.

<a id="s11"></a>

### S11 — Stories, FR, SC, Annahmen

- Primärquelle am Pin: [templates/spec-template.md](https://github.com/github/spec-kit/blob/ee94598c3c87ae231027b22fb2be2b5a13e8820f/templates/spec-template.md)
- Gelesen: 1-131. Status: **quellengeprüft, nicht ausgeführt**.

<a id="s12"></a>

### S12 — Zielpfad der Constitution; gezielte Prüfung

- Primärquelle am Pin: [templates/commands/constitution.md](https://github.com/github/spec-kit/blob/ee94598c3c87ae231027b22fb2be2b5a13e8820f/templates/commands/constitution.md)
- Gelesen: Suche: constitution.md, Kontextzeilen 75-129. Status: **quellengeprüft, nicht ausgeführt**.

<a id="s13"></a>

### S13 — Separater ausführbarer Workflow mit Review-Gates

- Primärquelle am Pin: [workflows/speckit/workflow.yml](https://github.com/github/spec-kit/blob/ee94598c3c87ae231027b22fb2be2b5a13e8820f/workflows/speckit/workflow.yml)
- Gelesen: 1-74. Status: **quellengeprüft, nicht ausgeführt**.

<a id="s14"></a>

### S14 — Gate-Konfiguration, non-TTY PAUSED; kein Engine-End-to-End-Test

- Primärquelle am Pin: [src/specify_cli/workflows/step/gate/__init__.py](https://github.com/github/spec-kit/blob/ee94598c3c87ae231027b22fb2be2b5a13e8820f/src/specify_cli/workflows/step/gate/__init__.py)
- Gelesen: 1-190. Status: **quellengeprüft, nicht ausgeführt**.

## Rechte und Aktualisierung

Originale Analyse und kurze, selbst formulierte Anwendungsbeispiele; keine Übernahme vollständiger Vendor-Templates. Die verlinkten Originale bleiben bei ihren jeweiligen Rechteinhabern. Für dieses private Dossier wird keine pauschale Neulizenzierung fremder Inhalte erklärt.

Bei Aktualisierung beide neuen Pins separat ermitteln, Quellenänderungen prüfen, Konfliktliste fortschreiben und Checks wiederholen. Ein bloßes Austauschen der Commit-IDs würde die vorhandenen Aussagen nicht neu validieren.
