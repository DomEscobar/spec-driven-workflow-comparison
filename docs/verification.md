# Verifikation und Reichweite

**Prüfdatum: 27.10.2026 (UTC).** Dieses Protokoll trennt ausgeführte Dossier-Prüfungen von lediglich gelesenen Produktquellen. [Quellenregister](../sources.md).

## Tatsächlich ausgeführt

- Beide offiziellen HEADs mit `git ls-remote … HEAD` ermittelt und getrennte Git-Checkouts auf diese Commits fixiert. OpenSpec: `6d04a1b58dedc95729d34e4f223d9d483aae210a`; Spec Kit: `ee94598c3c87ae231027b22fb2be2b5a13e8820f`.
- `python3 scripts/check_docs.py --network`: **PASS**, keine Fehler. Geprüft wurden 11 Markdown-Dateien, 14 Tabellen, 35 Datenzeilen der Detailmatrix, zwei JSON-Beispielblöcke und 25 gepinnte Quellenregistrierungen. Acht ausgewählte Primärquellen lieferten nichtleeren Inhalt mit HTTP 200.
- Netzwerk-Auswahl, vorab festgelegt im Checker: O2, O3, O4, O11, S1, S2, S6, S14. Abgerufen wurden die zu den GitHub-Permalinks gehörigen Raw-Dateien am exakten Commit. Kein Ausführen der abgerufenen Inhalte.
- `python3 scripts/check_docs.py`: **PASS**, offline, keine Fehler. Interne Dateilinks und explizite Quellenanker aufgelöst; Matrixbreite, Belegzellen, geschlossene Codeblöcke und JSON-Syntax geprüft. Python-Dateien mit `ast.parse` syntaktisch geprüft.
- `python3 scripts/test_check_docs.py`: **8 Tests bestanden**. Positiver unveränderter Bestand sowie negative Kontrollen für kaputten Link, fehlenden Anker, Tabellenbreite, Platzhalter-URL, offenen Codeblock, ungültiges JSON und privaten Pfadmarker. Mutationen erfolgen nur in temporären Kopien.
- GitHub-Readback nach Erstellung: `nameWithOwner` exakt `DomEscobar/spec-driven-workflow-comparison`, `isPrivate: true`. Commit und Push werden separat gegen Remote-SHA und sauberen Arbeitsbaum verifiziert; der endgültige SHA steht im externen Übergabebericht, nicht als selbstreferenzierender Commitwert in dieser Datei.

## Reproduzieren

Im Repository-Root mit Python 3, ohne Drittbibliotheken:

```bash
python3 scripts/check_docs.py
python3 scripts/test_check_docs.py
python3 scripts/check_docs.py --network
git diff --check
```

Der Offline-Checker verändert keine Dokumente. Der Netzwerkmodus benötigt HTTPS-Zugang zu GitHub Raw und ist naturgemäß von dessen Erreichbarkeit abhängig. Ein späterer Netzausfall widerlegt nicht rückwirkend den hier protokollierten erfolgreichen Abruf.

## Präzise Grenzen

- **Nicht ausgeführt:** Installation von OpenSpec/Spec Kit, deren Test-Suites, Agentenworkflows, Framework-CLI-Befehle, Produktbenchmarks oder Export-Anwendungstests. Beispielausgaben sind ausdrücklich synthetische Erwartungen.
- **Kein Vollaudit:** Quellen wurden in den in der Registry genannten Bereichen gelesen. Prompt-Anweisungen sind keine beobachtete Agentenbefolgung; gelesene Kontrollpfade keine Laufzeitvalidierung.
- **Linkprüfung ist keine Inhaltsprüfung:** Beleg in jeder Matrixzeile bedeutet nicht, dass ein Automat deren fachliche Schlussfolgerung bewiesen hat. Diese wurde redaktionell gegen die angegebenen Quellen formuliert.
- **Markdown-Prüfung ist bewusst begrenzt:** Tabellenstruktur, Fences, explizite Anker, interne Inline-Links und eingebettetes JSON; kein vollständiger CommonMark-/GFM-Renderer. Mermaid wurde nicht mit einem Browser oder einer Mermaid-Engine gerendert.
- **Privacy-Prüfung ist heuristisch:** Der Checker lehnt bestimmte Betriebs-/Secret-Marker in Markdown ab. Das ersetzt keinen universellen Secret-Scanner. Das Dossier wurde aus einer Allowlist neu geschriebener Dateien aufgebaut, ohne private Quelldokumente oder Vendor-Checkouts zu übernehmen.
- **Keine Produkt-Gates eingerichtet:** Branch Protection, Anwendungstests, CI-Runner und Publikationsfreigaben sind Empfehlungen für einen späteren Pilot, nicht angeblich aktive Schutzmaßnahmen dieses Repositories.

Die [Abnahmecheckliste](requirements-and-tests.md) bleibt absichtlich offen: Sie gehört zu einer noch nicht gebauten Beispielanwendung, nicht zu den oben bestandenen Dokumentationsprüfungen.
