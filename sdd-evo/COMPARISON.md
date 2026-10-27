# OpenSpec, Spec Kit und Evidence-bound SDD

> **Einordnung:** Dieses Dokument beschreibt den ursprünglichen Design-/Demo-Stand. Der jetzt ausführbare, bewusst kleinere lokale MVP ist im [Quickstart](README.md) und [MVP-Prüfbericht](docs/MVP-VERIFICATION.md) abgegrenzt; der Entwurf ist nicht vollständig implementiert.

[Übersicht](README.md) · Produktbefunde beziehen sich auf [S01/S02](EVIDENCE.md), nicht jede Version oder Erweiterung. **Die dritte Spalte ist unser vorgeschlagener Entwurf**, kein gleichwertig fertiges Produkt und kein gemessener Sieger.

## Drei Flows

**OpenSpec:** Projektkontext und Capability-Sollstand → Changevorschlag mit Specdeltas, Design und Tasks → Review/gegebenenfalls Update → Apply → bewusst genutztes Verify → Sync des akzeptierten Capability-Solls und Archivierung. Optionale Workflows und Profile beeinflussen den installierten Ablauf. Verify ist beratend; CLI-Struktur-/Archivprüfungen sind reale lokale Kontrollen, keine universelle Verhaltens-/Mergegarantie.

**Spec Kit:** Constitution → Specify → Clarify → Plan → Tasks → Analyze/Checklists → Implement → Converge → gegebenenfalls neue korrektive Tasks und Implement → Review/PR. Converge ergänzt Restarbeit, statt Spec/Plan passend zum Code umzuschreiben; eine saubere Convergence-Aussage bleibt Agentenbeurteilung. Separate Workflow-Gates können konfiguriert sein; Prerequisite-Prüfungen sind real, aber nicht identisch mit geschützter Abnahme.

**Evidence-bound SDD (Vorschlag):** Ergebnis/Authority festhalten → Contract und Oracle autorisieren → begrenzter Kandidat → tatsächlicher Integrationstree → frische Check- und Reviewreceipts → Repair / Amendment / Block / Stop / Acceptance → separat Release und Beobachtung. Planung kann aus einem der beiden Produkte oder einem Ticket kommen. Der Zusatz liegt unterhalb der Oberfläche: abgeleitete Gültigkeit und kontrollierte Übergänge.

## Fallbezogene Matrix

| Kriterium | OpenSpec am Pin | Spec Kit am Pin | Evidence-bound SDD, vorgeschlagen |
|---|---|---|---|
| Führende Einheit | Capability-Hauptspec und Change-Delta | Feature-Dossier mit Constitution, Spec, Plan, Tasks | Autorisierte Verpflichtung plus exakter Ergebnisnachweis |
| Besonders gut passend | Laufende Evolution eines bestehenden Systemvertrags | Neue/komplexe Features mit Klärungs- und Entwurfsbedarf | Agentenchanges, bei denen stale Grün, Scope- oder Integrationsfehler ein konkretes Problem sind |
| Nicht gut passend | Delta-/Sync-Zeremonie für trivialen Tippfehler oder schlecht gepflegte Hauptspecs | Voller Planungsapparat für winzige, eindeutige Korrektur | Als selbstgebaute Plattform, wenn Ticket + geschützte CI die Probleme bereits lösen |
| Prävention | Scope, Anforderungen/Szenarien, Kontextregeln und Review | Constitution, Clarify, Plan und Anforderungschecklisten | Dieselben Grundideen, zusätzlich explizite Nichtziele, zulässige Alternativen und Delegation |
| Detektion | Strukturvalidierung, Verify von Vollständigkeit/Korrektheit/Kohärenz | Analyze von Artefakten; Converge: missing/partial/contradicts/unrequested | Pflichtchecks plus fachliches Review; zusätzliche stale/unknown/authority Findings |
| Enforcement | Lokale Struktur-/Archive-Sperren mit dokumentierten Bypässen; Verify advisory | Prerequisite-Skripte, optional konfigurierbare Workflow-Gates | Ziel: externer Gateadapter vor Merge/Effekt. Geliefert: nur lokaler Fixture-Konsistenzcheck |
| Testpflicht | Schema fordert Verifikationsweg; keine allgemeine TDD-Garantie | Tasktemplate erklärt Tests optional, sofern nicht angefordert | Vorab autorisierte, risikobasierte Pflichtcheckliste; kein stilles Entfernen fehlender Checks |
| Amendment/Repair | Update revidiert Planung, Apply implementiert | Converge ergänzt korrektive Tasks; Intent separat ändern | Getrennte Autorisierung neuer Sollrevision versus Repair unter gleichem Soll |
| Frische und Drift | Team-/CI-Ergänzung für exakte Code-/Test-/Environmentbindung nötig | Team-/CI-Ergänzung ebenso nötig | Konservativer versionsgebundener Graph, ganze Changegeneration stale bei unbekanntem Impact |
| Parallelität | Separate Changeverzeichnisse; Konflikte auf Hauptspecs möglich | Taskmarker; aktive Featureauswahl muss je Kontext stimmen | Optional disjunkte Write-Sets, Generation und ein Integration Owner; final kombinierter Tree |
| Abnahme | Archiv/Verify nicht automatisch Release | Converged/Taskdone nicht automatisch Release | ACCEPTED historisch auf Subject gebunden; RELEASED separat mit Readback |
| UI/Nutzerführung | Szenarien und Design können sie festhalten | Stories und Erfolgskriterien können sie festhalten | Explizites UX-/Guidance-Review bleibt erforderlich, nicht auf Unitchecks reduzieren |
| Pflegekosten | Hauptspecs, Deltas, Sync, installierte Profile | Dossier, Templates/Overrides, Featurestate, Convergence | Verträge, Runneradapter, Oraclepflege, False-Blocks; breite Invalidierung kostet CI-Zeit |
| Wirksamkeitsnachweis hier | Kein Vergleichsbenchmark | Kein Vergleichsbenchmark | Deterministische Modelltests; kein Produktivitäts-/Qualitätsbenchmark |

## Was wir bewusst übernehmen

Von OpenSpec: Sollstand und Änderung unterscheiden, gezielte Deltas, Entscheidungen nicht in Chats verlieren. Von Spec Kit: Klärung vor Detailplanung, nachvollziehbare Restarbeit, Korrektur nicht mit Umdefinition verwechseln. Von beiden: bestehende Tests/Review/CI ergänzen, keine erfundene Universalabnahme aus einem Kommando ableiten.

Nicht übernehmen: sämtliche Dateien und Rollen zu einem Hybrid stapeln, jedes Feature als volle Formalisierung behandeln oder „converged“ durch ein ähnlich ungeschütztes „accepted“ ersetzen. Ein anderer Name ohne unabhängige Evidenzquelle wäre kein Fortschritt.

## Dasselbe Public-Export-Beispiel in drei Modellen

- OpenSpec: Capability „Export“ um „nur explizit public“ als Delta ändern; Unknown-/Missing-Szenarien in Specs, Umsetzung/Verify und bewusster Soll-Sync. Eine CI-Receiptbindung wäre Zusatzarchitektur.
- Spec Kit: Story/FR für Public-Export, Privacy-Non-goals, Plan/Tasks; Analyze erkennt Inkonsistenz, Converge findet fehlenden Unknown-Fall und hängt Repairtask an. Schutz der Tests und endgültigen Wirkung bleibt separat.
- Unser Vorschlag: dieselbe fachliche Arbeit, aber grüne Evidenz für Contract v1 kann Contract v2 nicht abschließen; zwei grüne Worker können den ungeprüften Integrationstree nicht freigeben. Die genaue synthetische Folge steht in [EXAMPLE](EXAMPLE.md).

## Auswahlregel statt Punktesieger

1. Zuerst Daten-/Berechtigungs-/Effektgrenzen klären; gute UX kann einen Privacyverstoß nicht kompensieren.
2. Danach das passendste **Planungsmodell** wählen: lebender Capabilityvertrag, detailliertes Feature-Dossier oder kurzer Ticketvertrag.
3. Nur fehlende **Abnahmebindung** ergänzen. Für ein kleines Team zunächst ein Agent, bestehende CI, ein Integration Owner; kein neues Runtimeprojekt.
4. Nutzen gegen den gut eingerichteten Ticket-/CI-/Reviewbaseline messen, nicht gegen absichtlich schwache Prompts. Kein vergleichbarer Wirkungsnachweis liegt vor; unsere Auswahl ist eine konservative Designentscheidung.
