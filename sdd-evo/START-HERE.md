# SDD-evo mit deinem Coding-Agenten verwenden

Kopiere den folgenden Auftrag in deinen Coding-Agenten im Zielprojekt. Er soll SDD-evo **verwenden**, nicht neu entwickeln. Ersetze am Ende nur das Requirement.

Das Framework-Repository ist privat: Der Agent benötigt autorisierten GitHub-Zugang oder eine von dir bereitgestellte lokale Kopie. Keine Tokens in den Prompt schreiben. Die Anleitung ist agentenübergreifend; konkrete Skill-Pfade und Befehle muss der Agent anhand der vorhandenen Integration prüfen.

## Copy-paste-Auftrag

```text
Richte SDD-evo für dieses Projekt ein und nutze es anschließend,
um mein Requirement umzusetzen.

Framework-Repository:
https://github.com/DomEscobar/spec-driven-workflow-comparison

Framework-Unterordner:
sdd-evo/

Das Repository ist privat. Nutze vorhandenen autorisierten GitHub-Zugang
oder eine von mir bereitgestellte lokale Kopie.
Wenn der Zugriff fehlt, melde den konkreten Fehler. Frage nicht nach
Tokens im Chat und erfinde keine Frameworkdateien oder Befehle.

DEIN AUFTRAG

1. Framework und Projekt prüfen
- Lies die Projektregeln und untersuche Stack, Architektur und vorhandene
  Build-, Test-, Lint- und gegebenenfalls Browserprüfungen.
- Lade das Framework in ein separates Verzeichnis, ohne vorhandene
  Projektdateien zu überschreiben.
- Lies sdd-evo/README.md, INTEGRATION.md und die für deinen Ablauf
  relevanten Dokumente und Skills.
- Prüfe die tatsächlich vorhandene CLI mit --help.
- Halte den verwendeten Framework-Commit fest.
- Verwende nur vorhandene Funktionen. Behandle geplante Funktionen
  nicht als implementiert.

2. SDD-evo für dieses Projekt nutzbar machen
- Integriere die passenden Skills anhand von INTEGRATION.md in die
  von deinem Coding-Agenten unterstützte Struktur.
- Bestehende Projektanweisungen erhalten; keine globalen Einstellungen
  verändern und keine bestehenden Skills ungefragt überschreiben.
- Nutze die echten Prüfkommandos dieses Projekts.
- Falls der Runner unseren Stack noch nicht unterstützt, melde die
  konkrete Lücke. Verwende die vorhandenen Projektchecks separat,
  aber behaupte keine vollständige SDD-evo-Runnerintegration.
- Halte die Einrichtung klein: keine neue Agentenplattform und keine
  unnötigen Dependencies.

3. Requirement bearbeiten
- Bewahre meinen Originalauftrag unverändert auf.
- Leite daraus Ziel, Nicht-Ziele und überprüfbare Abnahmekriterien ab.
- Prüfe diese gegen den vorhandenen Code und das tatsächliche
  Nutzerbedürfnis, nicht nur gegen deine eigene Zusammenfassung.
- Entscheide kleine technische Details selbst im bestehenden
  Projektstil. Frage nur, wenn eine Unklarheit Produktverhalten,
  Sicherheit, Datenverlust, Kosten oder Auftragsumfang wesentlich
  beeinflusst.
- Arbeite auf einem eigenen Branch und erhalte fremde Änderungen.
- Implementiere das Feature vollständig, einschließlich notwendiger
  Integration, Tests und knapper Dokumentation.

4. Prüfen und reparieren
- Führe echte Tests aus. Eine Beschreibung eines Tests ist kein Test.
- Prüfe bei UI-Änderungen, sofern die Werkzeuge verfügbar sind,
  auch die tatsächliche Bedienung und Darstellung.
- Nutze die vorhandenen SDD-evo-Kommandos für Nachweise und Frischeprüfung.
- Setze, wenn deine Umgebung es unterstützt, einen separaten Reviewer
  mit frischem Kontext ein. Gib ihm Originalauftrag, Abnahmekriterien,
  aktuellen Diff und Zugriff auf das zu prüfende Ergebnis.
- Der Reviewer sucht konkrete Fehler und fehlende Anforderungen.
  Er darf weder den Auftrag abschwächen noch Änderungen freigeben.
- Ein zweiter Durchgang in deinem eigenen Kontext ist Selbstreview,
  kein unabhängiges Review. Kennzeichne diesen Unterschied.
- Repariere belegte Fehler innerhalb des Auftrags und führe danach
  die erforderlichen Checks auf dem finalen Code erneut aus.
- Ändere keine Abnahmekriterien oder geschützten Tests nur,
  um einen grünen Status zu erhalten.

5. Grenzen und Abschluss
- Keine neuen kostenpflichtigen Dienste oder Modellabonnements.
- Kein Deployment, Push, Merge oder PR ohne bestehende ausdrückliche
  Berechtigung dafür.
- Keine unbegrenzten Reparaturschleifen: nutze vorhandene Projektlimits.
  Fehlen sie, begrenze dich auf drei Reparaturrunden und melde danach
  verbleibende Blocker. Bestehende strengere Limits bleiben gültig;
  Zähler nicht durch Neuinitialisierung zurücksetzen.
- Trage dich nicht als menschlichen Prüfer ein. Wenn das Framework
  eine menschliche Abnahme verlangt, die nicht vorliegt, bleibt
  dieser Schritt offen.
- Melde niemals „fertig“, nur weil Tasks abgehakt oder Tests grün sind.

LIEFERE AM ENDE KURZ
- Was funktioniert jetzt aus Nutzersicht?
- Welche Dateien wurden wesentlich geändert?
- Welche Checks wurden tatsächlich ausgeführt und mit welchem Ergebnis?
- Gab es unabhängiges Review oder nur Selbstreview?
- Was bleibt offen oder benötigt meine Entscheidung?
- Welcher Branch/Commit und welcher Framework-Commit wurden verwendet?

Beginne mit der tatsächlichen Projekt- und Frameworkprüfung.
Stoppe nicht bei einem Plan. Arbeite innerhalb dieser Grenzen bis
zum geprüften Ergebnis oder einem konkreten, belegten Blocker.

MEIN REQUIREMENT:
[Hier eintragen, was gebaut oder geändert werden soll]
```

## Was dieser Auftrag leistet

- Ein Agent übernimmt Einrichtung, Umsetzung und Prüfungen ohne manuelle Schrittsteuerung innerhalb des autorisierten Umfangs.
- Er funktioniert als Arbeitsauftrag auch ohne automatischen Pipeline-Controller. Er beweist weder Agentenkompatibilität noch technische Isolation.
- Der Agent muss fehlende Adapter, fehlende Reviewer und offene Freigaben sichtbar lassen. Selbstreview ersetzt keine unabhängige Prüfung.

Weiter: [Framework und Quickstart](README.md) · [Agentenintegration](INTEGRATION.md) · [Critic-Protokoll](docs/CRITIQUE.md)
