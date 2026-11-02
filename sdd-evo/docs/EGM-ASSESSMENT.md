# Elephant-Goldfish Model: vorerst nicht übernehmen

## Entscheidung

**EGM bleibt eine Forschungsreferenz. Kein Plugin-Install, keine neue Abhängigkeit und kein zusätzlicher Pflichtreview in SDD-evo.** Die Prüfung zeigt interessante Reviewfragen, aber keinen nachgewiesenen Zusatznutzen gegenüber unserem bestehenden Ablauf. Teile der Erledigungs- und Wiederprüfungsregeln passen nicht zu unseren versionsgebundenen Nachweisen.

Geprüfte Stände:

- [EGM: 403d8881d62022490637d740657b33f01e321ea8](https://github.com/google/elephant-goldfish-model/tree/403d8881d62022490637d740657b33f01e321ea8).
- SDD-evo: `9c1c3328f43bb60de74d26f913cf3ad03163d124`.

Diese Entscheidung betrifft diese Stände. Sie ist weder ein pauschales Qualitätsurteil über das Projekt noch eine Aussage über spätere Versionen. Die erste positive Einschätzung wurde nach unabhängiger Gegenprüfung auf **Übernahme zurückstellen** korrigiert.

## Was EGM anbietet

Der kontextreiche **Elephant** entwickelt den Entwurf. Frische **Goldfish**-Reviewer prüfen das Dokument und referenzierte Quellen ohne das vorausgehende Gespräch. Der Mensch entscheidet Architekturabwägungen und genehmigt den Entwurf.

EGM ist ein Skill-/Prompt-/Rubrikpaket, kein eigener deterministischer Abnahmecontroller. „Zero-context“ bedeutet hier nicht kontextlos: Reviewer erhalten Dokumente, Rubriken, Quellen und Hostinstruktionen. Frische Sessions beweisen keine statistisch unabhängigen Fehler.

Der mögliche Zusatz zu SDD-evo wäre der **Zeitpunkt vor der Implementierung**. Originalauftragsschutz, fachliche Zielarbeit und frische Kritik nach tatsächlichen Tests existieren bereits. Das Fehlen eines separaten Pre-Code-Kommandos beweist noch keine Qualitätslücke.

## Entscheidende Befunde

### 1. Frische Reviewer können denselben falsch übersetzten Auftrag prüfen

Der Draft-Ablauf bevorzugt einen Concepts Brief beziehungsweise eine Discussion Summary. Den Abgleich gegen diesen Vorgänger übernimmt der Elephant; Goldfish erhalten ihn nicht standardmäßig als unabhängigen Originalanforderungsanker. Der Comprehension-Reviewer paraphrasiert den Dokumentinhalt, während der Intentvergleich beim Autor bleibt.

Eine klare, konsistente, aber falsch verstandene Spezifikation kann deshalb gute Reviews erhalten. Zusätzliche Quelldateien sind möglich; ein Dateipfad allein beweist jedoch weder ursprüngliche Autorität noch Unverändertheit.

Quellen: [Draft](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-draft/SKILL.md#L143-L161), [Abgleich durch den Autor](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-draft/SKILL.md#L249-L267), [Comprehension](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/agents/comprehension.md#L37-L57).

### 2. Erledigte Widersprüche sind nicht ausreichend versionsgebunden

Der Review-Loop behandelt widersprochene oder ohne Fix als Risiko akzeptierte Findings als `settled`. Dieselbe Frage im selben Bereich soll später nicht wieder geöffnet werden. Für diese Regel fehlt eine verpflichtende erneute Prüfung bei geänderten Quellen oder Voraussetzungen.

Ein ursprünglich korrekter Contest kann nach einer API-/Specänderung falsch werden. Finding-ID und Zeilennummer reichen nicht als Evidenzidentität. Das ist ein aus der Regel abgeleiteter Fehlerfall, kein beobachteter Live-Agentenfehler.

Quelle: [Settled Findings und Konvergenz](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-review-loop/SKILL.md#L149-L173).

### 3. „Resolved“ und „converged“ sind keine Produktabnahme

Der Resolver enthält sinnvolle Anforderungen an Contest-Evidenz und Eskalation. Sein Dokumentstatus `resolved` kann trotzdem unadressierte Punkte enthalten. Zwei saubere Runden beziehen sich auf nicht bereits als erledigt eingestufte Findings; sie belegen keine bekannte Restfehlerrate. Der Reviewcap ist ein Eskalationspunkt mit erlaubter Fortsetzung, kein harter kumulativer Kostendeckel. Erneute Prüfung nach Änderungen ist nicht durchgehend verpflichtend.

**Nicht in SDD-Acceptance übersetzen:** Ein Dokumentstatus ersetzt weder frische Tests noch aktuelle Finding-Dispositionen oder autorisierte Risikoentscheidungen.

Quellen: [Resolve](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-resolve/SKILL.md#L138-L187), [Review nach Änderungen](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-review/SKILL.md#L370-L402).

### 4. Kontexttrennung hängt vom Host ab

EGM verlangt frische Subagenten und einen Stop, wenn diese Fähigkeit fehlt. Das ist zunächst ein Promptvertrag. Die Hostguides enthalten konkrete Konfigurationsvorgaben, grenzen aber Datei-, Memory- und Instruktionsisolation selbst ein. Read-only verhindert keine falsche Interpretation einer referenzierten Quelle.

Automatisch gelesene Quellen bleiben eine mögliche Kontaminationsfläche. Im geprüften Pfad gibt es kein allgemein durchgesetztes geschlossenes Quellenmanifest. Das ist eine zu prüfende Vertrauensgrenze, **kein hier demonstrierter Prompt-Injection-Exploit**. Auch SDD-evo ist im lokalen Same-UID-Modus keine vollständige Sicherheitsgrenze.

Quellen: [Review-Voraussetzungen](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/skills/egm-review/SKILL.md#L19-L28), [Claude-Kontextgrenzen](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/docs/claude.md#L125-L151), [Codex-Kontextgrenzen](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/docs/codex.md#L44-L67).

### 5. Der zusätzliche Nutzen ist nicht gemessen

Im geprüften Material fehlt ein kontrollierter Vergleich gegen SDD-evo: keine gepaarten Endprodukte bei vergleichbarem Gesamtaufwand, keine belastbare Fehlerreduktion und keine Messung zusätzlicher falscher Blocker oder menschlicher Entscheidungsarbeit. Nutzungszahlen sind kein Wirksamkeitsbenchmark. Unbekannter Nutzen bedeutet nicht bewiesene Nutzlosigkeit.

Die Tests prüfen unter anderem Paketverträge und korrelierte Tool-Reads. Ein erfolgreicher Read beweist weder vollständiges Verständnis noch gute Designkritik. Die Claude-Liveprobe überschreibt den normalen Workflow und prüft einen engen Delegations-/Lesevertrag, nicht die vollständige Designqualität.

Quellen: [Testing und Grenzen](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/TESTING.md), [Claude-Probe](https://github.com/google/elephant-goldfish-model/blob/403d8881d62022490637d740657b33f01e321ea8/tests/integration/test_claude.py#L94-L110).

## Was als Reviewfrage nützlich bleibt

Bei einem konkreten schwierigen Entwurf können Reviewer fragen:

- Kann ein frischer Leser das gewünschte Verhalten korrekt wiedergeben?
- Stimmen Architekturannahmen mit dem aktuellen Code überein?
- Werden bestehende Fähigkeiten übersehen und unnötig neu gebaut?
- Sind Alternativen, Risiken und offene Entscheidungen nachvollziehbar?

Das ist keine neue Pflichtpipeline und keine Übernahme des EGM-Resolvers. Für kleine klare Änderungen bleibt der bestehende kleine Ablauf der konservative Aufwanddefault, nicht ein empirisch bewiesener universeller Sieger.

## Wann erneut prüfen?

Erst bei wiederholt beobachteten, teuren Designfehlern vor dem Coding einen begrenzten Vergleich erwägen:

1. Unveränderten SDD-Ablauf gegen denselben Ablauf mit **einem** frischen Pre-Code-Reviewer vergleichen.
2. Originalauftrag und seine Autorität getrennt vom Spec-Autor erhalten; Quellen bleiben Daten, keine neuen Anweisungen.
3. Bekannte Defekte und akzeptable Gegenbeispiele verwenden; auch falsche Blocker messen.
4. Geänderte Evidenz muss frühere Contests invalidieren; fehlende Pflichtreads bleiben unvollständig.
5. Gesamtkosten, Zeit, Owneraufwand und verbleibende Endfehler berücksichtigen, nicht nur die Anzahl produzierter Findings.

Keine Übernahme bei unautorisierter Sollabschwächung, falscher Clean-Meldung, veralteter Contest-Evidenz oder zusätzlicher Reviewlast ohne relevanten Nutzen. Ein positives kleines Screening wäre noch kein allgemeiner Wirksamkeitsnachweis.

## Prüfumfang und Status

- Statischer Quellaudit von Skills, Reviewer-Personas, Standards, Hostguides und Tests; Abgleich mit den genannten SDD-Artefakten.
- Separate unabhängige Gegenprüfung; nicht verblindet und keine statistische Studie.
- Sechs zusätzliche synthetische Offline-Tests eines zuvor inspizierten Tracehelpers bestanden und erneut ausgeführt. Sie prüfen Lese-/Denial-Korrelation und deren Grenzen, nicht das Verhalten eines echten Modells. Die lokalen Auditfixtures sind nicht Teil dieses Repositorypakets; aus dieser Notiz allein ist keine Reproduktion dieser Zusatztests behauptet.
- Kein eigener nativer EGM-Modelllauf, kein Qualitätsbenchmark, keine Installation und keine Integration.
- Der Google-Namespace ist kein Supportversprechen: Das Projekt bezeichnet sich als nicht offiziell unterstütztes Google-Produkt.

**Status: dokumentierte Nichtübernahme.** Die Veröffentlichung dieser Bewertung ändert keine Skills, Gates oder Laufzeitregeln von SDD-evo.
