# Coding-Agent-Integration

[Quickstart](README.md). Die Skills sind portable Markdown-Anweisungen; der Python-Runner führt Tests aus. Kein installierter Agent, Modellaufruf oder kostenpflichtiger Dienst ist Voraussetzung. Diese Lieferung ändert keine globalen Hermes-, Codex- oder Claude-Einstellungen.

## Codex CLI / IDE

Die offiziellen [Codex-Skill-Dokumente](https://developers.openai.com/codex/skills) beschreiben Repo-Skills unter `.agents/skills/`, explizite Auswahl über `/skills` oder eine `$`-Skill-Erwähnung. Starte Codex im Ziel-Repo. Die fünf Dateien liegen hier bereits am richtigen Ort.

Beispiel **im Codex-Prompt**, nicht in deiner Shell:

```text
$evo-start Implement the requested change; first establish the accepted contract.
$evo-build Implement R1 without changing acceptance.
$evo-check
$evo-change Propose the necessary amendment; do not apply before acceptance.
$evo-finish
```

Wenn Skills nicht erscheinen, `/skills` prüfen und gegebenenfalls die Sitzung neu starten. Prompts sind keine technische Erzwingung der Regeln; Approval- und Ausführungsrechte hängen vom Agenten-Setup ab.

## Claude Code

Die offiziellen [Claude-Code-Skill-Dokumente](https://code.claude.com/docs/en/skills) beschreiben Projekt-Skills unter `.claude/skills/<name>/SKILL.md` und direkte Aufrufe als `/skill-name`. `.agents/skills/` wird hier nicht als universell unterstützter Claude-Pfad behauptet.

Kopiere die fünf Verzeichnisse einmalig **ohne bestehende Zielskills zu überschreiben**, vom Repo-Root:

```sh
python3 -c 'from pathlib import Path; import shutil; src=Path(".agents/skills"); dst=Path(".claude/skills"); names=["evo-start","evo-build","evo-check","evo-change","evo-finish"]; assert all(not (dst/n).exists() for n in names), "destination exists; review manually"; dst.mkdir(parents=True, exist_ok=True); [shutil.copytree(src/n,dst/n) for n in names]'
```

Dann **im Claude-Code-Prompt**:

```text
/evo-start
/evo-build
/evo-check
/evo-change
/evo-finish
```

`/evo:start` war eine illustrative frühere Schreibweise; sie ist **kein** hier installierter universeller Slash-Command. Keine Plugin-Namespace-Installation wird behauptet. Die kopierten Skills müssen bei Updates bewusst synchronisiert werden.

## Andere Agenten / ohne Agent

Lass den Agenten die passende `SKILL.md` explizit lesen und befolgen; behaupte keine automatische Discovery. Oder führe die CLI aus dem [Quickstart](README.md) selbst aus. Der Builder schreibt Code mit seinen vorhandenen Tools, die CLI generiert keinen Code.

## Verifizierter Umfang

Offizielle Skill-Pfade und Aufrufsyntax wurden live in den oben verlinkten Herstellerdokumenten geprüft. Die CLI, reale lokale Tests und die Claude-Kopieranweisung wurden ausgeführt; **keine interaktive Codex-/Claude-Sitzung und keine Agenten-Autonomiequalität** wurden getestet. Kein externes CI/Branch-Protection-Setup oder Deployment wurde eingerichtet.
