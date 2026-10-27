# Minimale Artefakte und Autorität

[Übersicht](README.md) · **Vorgeschlagene Verträge; Demo-Untermenge unten ausdrücklich abgegrenzt.**

## 1. Eine maßgebliche Quelle pro Aussage

Kein Pflichtordnerbaum bis zur Funktionsebene. Drei changebezogene Artefaktklassen plus bestehende Projektchecks reichen zunächst:

| Artefakt | Mindestinhalt | Schreib-/Entscheidungsautorität |
|---|---|---|
| **Contractrevision** | Originalauftrag-Referenz; Revision/Parent; Ziel; Scope und Non-goals; Requirements mit stabilen IDs; erlaubte Alternativen; Daten-/Effektgrenzen; Acceptance-Mapping; Abschlussziel; Authority-Referenz | Auftraggeber oder vorab delegierter Intent Owner; Builder nur Vorschläge |
| **Work-/Finding-Sicht** | Tasks, Abhängigkeiten, Write-Sets, Generation/Basis; Findings mit Klasse, betroffener Requirement-ID, Witness, Disposition; offene Entscheidungen | Builder innerhalb Scope; Status bleibt abgeleitet |
| **Evidence-/Decision-Historie** | Ausführungsreceipts, Reviews, Amendments, Budgetreservierungen, Abschluss-/Widerrufsentscheidungen | Vertrauenswürdiger Runner/Controller und autorisierte Reviewer; nicht vom Builder selbst bescheinigt |

Die projektweite **Policy** bestimmt erforderliche Checks, Schreibflächen, Principalrechte, Budgets und Releasegrenzen. Die existierende Testsuite plus ein unabhängig aufgenommenes Acceptance-Bundle bildet das **Oracle**. Markdown kann eine gerenderte Ansicht des Vertrags sein, darf aber nicht still eine zweite widersprüchliche Sollquelle werden. Kleine Korrekturen verwenden dasselbe Modell in einem Ticket mit Referenzen statt umfangreicher Dokumente.

### Requirement-Vertrag (illustratives Datenmodell, kein zusätzlicher CLI-Befehl)

```text
id, statement, polarity=require|forbid|preserve|remove,
source_intent_ref, allowed_alternatives[], acceptance_ids[],
baseline_ref_for_removal?, residual_review_owner?
```

Jede Pflichtanforderung braucht ein erwartetes beobachtbares Ergebnis und einen relevanten Negativfall. Entfernen von Verhalten prüft die Baseline und verbleibende Regressionpflichten, nicht nur die Abwesenheit eines Keywords. Pflichtreviews für Verständlichkeit, Designkonsistenz oder UX tragen eigene IDs, Rubrik und genaue Subjectbindung. Kein künstlicher maschineller Wahrheitsanspruch für Geschmack.

### Receipt-Vertrag (Zielbild)

```text
schema_version, run_id, attempt_id, generation,
subject{repo, base, candidate, actual_integration_tree, target_ref},
inputs{contract, spec, oracle, policy, runner, commands_with_versions,
       dependencies, fixtures, environment_allowlist, critical_config,
       effective_instructions},
checks[{id, requirement_ids, command_id, exit_code, status,
        discovered_test_ids, skipped_ids, log_digest, terminal_witness}],
producer{channel_identity, invocation_ref}, findings[],
review{actor, decision, subject_binding}, budget_used
```

Hashwerte müssen abrufbare unveränderliche Bytes/Objekte referenzieren, nicht bloß Zeichenketten ohne Herkunft. Geheimnisse gehören nicht in Environmentmanifeste; nur freigegebene Konfigurationsidentitäten und nichtgeheime relevante Werte. Ungepinntes Remoteverhalten bleibt eine Frische-/Replaygrenze. Schema- oder Parserfehler, fehlende Reports, skip/error/unknown und Null-Testdiscovery sind Nicht-Erfolg. Vorab als Review definierte Checks verlangen stattdessen ihren konkreten Beobachtungswitness; sie sind keine Ausrede für leere Testläufe.

## 2. Autorität statt Rollentheater

- **Intent Owner** autorisiert Soll und delegierte Änderungen. Ein klarer Nutzerauftrag kann die initiale Freigabe sein; keine zusätzliche Klickpflicht erfinden.
- **Builder** editiert genehmigte Produktpfade und Entwicklungstests, schlägt Amendments vor und bearbeitet Findings. Keine Selbstfreigabe neuer Rechte oder schwächerer Acceptance.
- **Verifier** beobachtet die tatsächliche Ausführung auf eingefrorenem Stand. Identität kommt aus dem kontrollierten Kanal, nicht aus `producer: trusted` in einer Agentendatei.
- **Integrator/Controller** prüft Schreibfläche, Generation, Budget, Vollständigkeit und atomare Übergänge. Er ist keine zusätzliche Pflicht-LLM-Rolle.
- **Reviewer** prüft fachlichen Intent, Oraclelücken und Nutzerqualität. Ein zweites Modell ohne unabhängige Rechte/Evidenz ist keine Sicherheitsgrenze.
- **Release Operator** hat gesonderte, begrenzte Befugnis; Builder bekommt keine Publikations-/Deploymentcredentials.

Eine modulbezogene „Groundtruth“ kann als kleiner Schnittstellenvertrag nützlich sein, ist aber **nur ein Vorschlag**, bis sie unabhängig anhand Nutzerintent und bekannter richtiger/falscher Fälle autorisiert wurde. As-built-Code, automatisch erzeugte Spec und vom selben Agenten generierte Tests bilden keinen unabhängigen Dreifachbeweis. Oracleänderungen haben eigene Aufnahme und neue Epoche; zusätzliche Entwicklerfälle werden nicht heimlich zur schwächeren verbindlichen Abnahme.

**Lokale Grenze:** Gemeinsamer Unix-User mit beliebiger Shell kann Dateien, Interpreter, Importpfad, Runner und Receipts ändern. Read-only-Testdateien oder eine zweite Agentenrolle verhindern das nicht. Für tatsächliches Enforcement: bestehende geschützte CI, separater Ausführungskontext, geschützte Checkquelle und Merge-/Effektgrenze ohne Builder-Bypass. Signaturen sind optional, eine echte Herkunfts-/Berechtigungsgrenze nicht.

## 3. Qualitätsvertrag jenseits grüner Tests

Abnahme betrachtet Outcome **und** Safety-/Prozessinvarianten: korrekte Exportdatei bei verbotener Datenweitergabe bleibt falsch. Sie erzwingt aber keinen goldenen Trace: Streaming und Batch, andere zulässige Reihenfolge oder gleichwertige interne Implementierung dürfen bestehen.

UX-Vertrag nennt Benutzeraufgabe, Entry Point, hilfreiche Fehler-/Leermeldungen, Auffindbarkeit, Zugänglichkeit und verständliche Restgrenzen. Bestehende Nutzerführung darf nicht zugunsten eines Testtricks verschwinden. Manual Review bindet konkreten Build, Rubrik und Beobachtungen; ungelöste subjektive Fragen bleiben sichtbar. Ein Reviewmodell kann unterstützen, nicht die Verantwortlichkeit ersetzen.

## 4. Tatsächlich implementierter Demonstrator

`scripts/sdd_gate.py` ist absichtlich klein: eine reine `gate(approved, current, evidence)`-Funktion, Contentbinding, kumulative Repair-Reservierungsfunktion und CLI. Keine LLMs, keine Netzwerkzugriffe, keine Subprozesse aus Eingangsdaten, keine Installation.

- `fixtures/approved.json` modelliert **extern vorgegebene** Pins für Contract/Spec/Oracle/Policy, Scope, Deliverables, Checkliste und erwartete Runner-/Revieweridentitäten.
- `fixtures/current.json` modelliert aktuelle Inhalte einschließlich Base-, Kandidaten- und **Integrations**dateimap, Environment, Commands, Config, Instructions und Generation.
- `fixtures/evidence.json` modelliert fremd gelieferte Check-/Reviewbeobachtungen auf genau diesen Inputs.
- `fixtures/stale-current.json` ändert den Integrationstree nach dem modellierten Check.

Jede Bindung ist SHA-256 über ein deterministisch serialisiertes JSON-Envelope; **Stringinhalte behalten Whitespace/Zeilenenden**, keine semantische Prosanormalisierung. Filemaps sind synthetische Inhaltstrings, keine echte Dateisystemerfassung. Protected-Pins werden gegen das separate Approved-Objekt geprüft, Scopeänderungen und tatsächliche Filemap-Diffs werden kontrolliert. Evidence muss genau alle Pflichtchecks enthalten, mit vollständiger deklarierter Observationliste, Exitcode 0, PASS, Witness, frischer Anfangs-/Terminalbindung und passender Reviewentscheidung. Generation, Candidate und Integration sind separat gebunden. Taskcheckboxen werden nicht zur Evidenz.

**Identitätsmismatch wird erkannt; Identität wird nicht authentifiziert.** Wer alle drei Eingabedateien kontrolliert, kann passende PASS-Belege erfinden. Auch eine passende Witnesszeichenkette beweist keine semantische Korrektheit. Deshalb ist `--demo` obligatorisch und jedes Ergebnis trägt `assurance: synthetic-consistency-only`. Ein realer Adapter müsste genau diese Eingaben selbst aus geschützten Quellen und Ausführung gewinnen.

CLI-Exitcodes: `0` modellierte Abnahme zulässig, `3` blockiert, `2` ungültige Eingabe oder fehlendes `--demo`. Jeder Output hat `released: false`. Unbekannte Checkstatus werden abgewiesen; doppelte JSON-Schlüssel und nichtendliche JSON-Zahlen werden beim Laden abgewiesen. Dies ist kein vollständiger Schema-/Securityfuzzer.

`reserve_repair` zeigt nur die pure Reservierungsregel: Restlimit, bekannter kumulativer Verbrauch, neuer Befundfingerprint. Es persistiert keine Zähler und schützt sie nicht gegen Manipulation. Kein Claim über Restart-Sicherheit. Die CLI hat **keinen** `release`, `amend`, `replay` oder `run-tests`-Befehl; der umfassende Ablauf in FRAMEWORK ist ein Implementierungsentwurf.

## 5. Weg vom Demo zum Adapter, ohne Plattformbau

Zuerst das reale Subject-Manifest und echte Testreportadapter außerhalb der Builder-Schreibfläche; danach generationengebundene Decisions und geschützten Checkaggregator. Erst bei Bedarf Eventpersistenz/Resume, dann Releaseintegration. Der Integrator muss die Finalbasis unmittelbar vor Merge abgleichen oder Merge-Queue-/Postmerge-Checks verwenden. Wirkung vor Autorisierung wird nicht durch einen nachträglichen Report geheilt.

Einführungskriterium wäre nachweislich weniger falsche Abschlussmeldungen bei akzeptablem False-Block-/Reviewaufwand. Verifikation dieses Pakets zeigt nur, dass die konkrete pure Modelllogik ihre dokumentierten positiven und negativen Fixtures behandelt; kein Produktionsnutzen ist damit belegt.
