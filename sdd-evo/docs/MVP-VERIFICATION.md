# MVP: tatsächlich ausgeführte Verifikation

[Quickstart](../README.md) · [Integration](../INTEGRATION.md)

## Ausgeführt

Vom Repository-Root:

```sh
python3 -m unittest discover -s sdd-evo/tests -v
python3 sdd-evo/examples/run_e2e.py
python3 -m unittest discover -s scripts -v
python3 scripts/check_docs.py
```

- **63 Tests erfolgreich:** 30 neue Runner-Integrationstests mit echten temporären Git-Repositories und tatsächlichen CLI-/Test-Subprozessen; 33 bestehende Tests des synthetischen Konsistenzdemonstrators unverändert erhalten.
- End-to-End-Walkthrough ausgeführt, Exit 0: kaputte Additionsfunktion erzeugt echten Testfehler; echte Codekorrektur besteht; exemplarischer lokaler Review ermöglicht `ACCEPTED_LOCAL`; anschließende Codemutation wird als `STALE_EVIDENCE` abgewiesen. Keine vorgefertigten PASS-Receipts.
- **Dokumentationsprüfung PASS; acht Regressionstests erfolgreich.** Der erste Zwischenlauf hatte einen fehlenden Link auf diese damals noch nicht geschriebene Datei; der abschließende Lauf prüfte alle Links ohne Fehler. Kein Runnerfehler und keine gelockerte Prüfung.
- Claude-Skill-Kopierbefehl aus der Integrationsanleitung in einem temporären Verzeichnis ausgeführt: fünf Skills kopiert, erneutes Überschreiben verweigert.

## Abgedeckte Negativfälle

Veränderter Code, Vertrag, Test, Kommando oder deklarierte Umgebung; externe Specdatei verändert; getrackte Löschung, ungetrackte neue Quelle, Indexänderung, ignorierte aber getrackte Datei; Mutation während des Testlaufs; wiederholte Checks ohne Selbsthash; Timeout und begrenzte Ausgabe; verlorene Receipts/Logs; unbekannte oder fehlende Checkresultate; leere Checkmenge, null Tests, übersprungene Tests; fehlender/veränderter manueller Review; Pfadtraversal, absolute/Reservatpfade, Symlinkinputs; erschöpftes Budget und verweigerter Budgetreset; keine geerbte private Prozessumgebung; keine Änderung des Git-Status durch den Runner selbst.

Die adversarial Receipt-Tests mutieren reale zuvor erzeugte Belege, um Fail-Closed-Verhalten zu testen. Das ist keine Behauptung, dass gleiche Benutzer keine vollständig passenden Fälschungen erstellen könnten.

## Nicht nachgewiesen

Keine unabhängige Authentifizierung, keine Sandbox oder umfassende Fuzzer-/Securityprüfung, kein hermetischer Build, keine temporären zurückgesetzten Dateimutationen, keine geschützte CI/Branch-Protection, keine Agenten-Performance, kein echter Nutzer-UX-Test, kein Deployment und kein Produktionsnutzen-Benchmark. Linux wurde ausgeführt; macOS ist vorgesehen, aber hier nicht getestet. Windows wird wegen POSIX-Lock/Prozessgruppen nicht unterstützt.

Der ursprüngliche [Demo-Prüfbericht](VERIFICATION.md) bleibt historisch getrennt. `scripts/verify_package.py` selektiert jetzt ausdrücklich `test_sdd_gate.py`, damit der Demo-Report nicht echte Runner-Tests fälschlich als reine synthetische Fixtures beschreibt.
