# Auswahl, Aufwand, Einführung und Grenzen

[Übersicht](../README.md) · [Matrix](comparison-matrix.md)

## Entscheidungstrigger statt Siegerliste

| Ausgangslage | Konservativer Start | Wechsel-/Eskalationstrigger |
|---|---|---|
| Bestehendes System, klar begrenzte Capability-Änderungen | OpenSpec mit core, explizitem Review und echten Tests. | Viele widersprüchliche Anforderungen: mehr Klärung und inkrementelle Planung; ggf. Spec-Kit-Pilot. |
| Neues, mehrdeutiges Feature mit mehreren Verträgen | Spec Kit mit clarify/checklist/analyze und begrenzter converge-Schleife. | Artefaktpflege übersteigt Nutzen bei kleinen Folgeänderungen: kürzerer Pfad oder OpenSpec prüfen. |
| Kleine Korrektur ohne neues Verhalten | Ticket, kleiner Patch und Regressionstest können genügen. | Wiederholte Scope-/Abnahmefehler: schmalen Spec-Workflow ergänzen. |
| Langfristiger, teamübergreifender Systemvertrag | OpenSpec-Hauptspecs als mögliche Vertragsbasis. | Unklare Ownership oder dauernde Sync-Konflikte: zuerst Governance und Capability-Schnitt lösen. |
| Hoher Privacy-/Regulierungsdruck | Erst Abnahme, Rechte und Enforcement festlegen; Tool danach wählen. | Kein unabhängiges Gate oder zu breite Credentials: keine autonome Einführung. |
| Team nutzt schon eines erfolgreich | Nicht allein wegen neuer Features migrieren. | Wiederholt belegte Lücken, die Anpassung nicht wirtschaftlich behebt. |

Das sind **unsere bedingten Empfehlungen** aus den beschriebenen Arbeitsmodellen, keine empirischen Gewinner. Beide können neue und bestehende Projekte bedienen. [O10](../sources.md#o10), [S1](../sources.md#s1).

## Wo Aufwand tatsächlich entsteht

| Kostenstelle | OpenSpec | Spec Kit | Was messen? |
|---|---|---|---|
| Einmaliger Einstieg | CLI, Integration, Capability-Schnitt und Schema verstehen. | CLI, Integration, Constitution, Feature-/Template-Modell verstehen. | Zeit bis erster unabhängig abgenommener Change, nicht bis Installation. |
| Laufende Planung | Deltas und Hauptspecs pflegen; bei Bedarf Design. | Spec/Plan/Tasks und ergänzende Artefakte pflegen. | Review-Minuten, Revisionen, ungeklärte Fragen. |
| Agentenverbrauch | Kontextlesen, Apply, Verify, Sync. | Klärung, Planung, Analyse, Implement-/Converge-Schleifen. | Gesamte Tokens/Toolaufrufe einschließlich Wiederholungen. |
| Integrationsaufwand | Sync- und Capability-Konflikte. | Feature-übergreifende Vertrags- und Zustandsabstimmung. | Konflikte, Nacharbeit, entkommene Regressionen. |
| Wartung | Profile, Schemas und generierte Agent-Dateien aktualisieren. | Overrides, Presets, Extensions und materialisierte Commands aktualisieren. | Upgrade-Aufwand und Abweichungen effektiver Instruktionen. |
| Betrieb/Security | Datenfreigabe, Agentenrechte, CI, Review. | Dieselben Grundkosten; zusätzliche Komponenten separat prüfen. | Datenabflussrisiko, Gate-Bypässe, Wiederherstellbarkeit. |

Mechanismen: [O1](../sources.md#o1), [O6](../sources.md#o6), [O11](../sources.md#o11), [S1](../sources.md#s1), [S2](../sources.md#s2), [S8](../sources.md#s8). Keine Euro-, Token- oder Zeitvorteile wurden gemessen. Open Source heißt nicht kostenloser Modellbetrieb. Preise hängen von der gewählten Agent-/Modellumgebung ab; hier keine aktuellen Tarifbehauptungen.

## Begrenzter Einführungsplan

1. **Vorher festlegen:** ein nichtproduktiver Change, unveränderte Akzeptanzfälle, Datenfreigabe, zulässige Schreibfläche und Budget. Das [Export-Beispiel](example-workflow.md) liefert einen gemeinsamen Fall, noch keine Implementierung.
2. **Minimal starten:** keine Community-Extension ohne konkreten Bedarf. CLI-Release, Upstream-Pin, Agent, effektive Skills/Prompts, Overrides und Modellkonfiguration aufzeichnen. Quellpin und Paketversion nicht verwechseln.
3. **Beide unter gleichen Bedingungen vergleichen:** gleiche Ausgangsbasis, gleicher Auftrag, gleiche unabhängige Abnahme, vergleichbares Modell-/Tool-/Reviewbudget. Getrennte Worktrees; Ergebnisse nicht unkontrolliert zwischen Varianten übertragen.
4. **Mehr als einen Durchlauf ansehen:** Aufgabenklassen und Wiederholungen vorab festlegen. Modellzufall und Lern-/Reihenfolgeeffekte offenlegen. Fehlgeschlagene Läufe und Abbrüche mitzählen.
5. **Akzeptieren nur bei belegtem Nutzen:** alle kritischen Tests bestanden, kein Privacy-Verstoß, weniger relevante Fehler oder vertretbarer Review-Aufwand. Eine schnellere Demo ohne Abnahme ist kein Gewinn.
6. **Rollout und Rückweg:** erst kleines Team/Teilmodul; bisherige Tests und PR-Regeln behalten. Workflow-Dateien per Git zurücknehmbar halten, keine automatische Produktionspublikation. Bei falscher Feature-Auswahl, unautorisiertem Scope oder Datenrisiko Runner stoppen und Credentials entziehen.

Dies ist ein vorgeschlagenes Evaluationsprotokoll, **kein bereits absolvierter Pilot**.

## Messprotokoll ohne Scheinergebnisse

Vor Versuchsbeginn aufzeichnen: Task-ID und Klasse, Ausgangscommit, Werkzeug-/Agent-/Modellstand, Instruktionsdigest, Budget, Run-ID, Ergebnis, unabhängige Testabdeckung, Fehlerklasse, gesamte Laufzeit, Reviewzeit, Tokenverbrauch und Nacharbeit. Fehlende Metriken als fehlend lassen.

Auswerten: Erfolg unter gleicher Abnahme, kritische Fehler, Scope-Verstöße, Reviewaufwand und Kosten pro akzeptiertem Ergebnis. Bei ungleichen Modellen, unterschiedlichen Tests oder nicht erfasster Nacharbeit keinen kausalen Produktvergleich behaupten. Die gleiche Modellfamilie allein macht Experimente noch nicht gleichwertig.

## Offene Fragen und Grenzen dieses Dossiers

- Keine Framework-Installation und keine aktuelle installierte Version geprüft; ausführbare Quellenkontrollpfade wurden gelesen, nicht ausgeführt.
- Kein vollständiger Security-Audit, kein Performance-/Token-/Fehlerratenbenchmark und keine Compliance-Zertifizierung.
- Quellenstände können weiterentwickelt werden. Integrationen, Custom-Schemas und Presets können Verhalten erheblich ändern.
- Die gelesenen Spec-Kit-Skripte repräsentieren vor allem die Python-Variante; Bash/PowerShell-Parität wurde nicht nachgetestet.
- OpenSpec hat eine laufende Dokumentationsmigration. Unterschiedliche Detailtiefe und beobachtete Spannungen sind in [sources.md](../sources.md) benannt, nicht still zusammengezogen.
- Syntax und Erreichbarkeit von Dateien/Links sind testbar; die fachliche Wahrheit jeder Aussage ist nicht automatisch durch unseren Dokumentationschecker bewiesen.
- Mermaid-Blöcke wurden strukturell erfasst, nicht mit einem Browser-/Mermaid-Renderer end-to-end getestet.

**Vertrauen:** hoch in die eng zitierten Text-/Quellbefunde am Pin; begrenzt in das reale Agentenverhalten ohne Ausführung; offen bei Produktivität und Kostenüberlegenheit. Aktualisieren, wenn konkrete installierte Stände oder Pilotresultate vorliegen.
