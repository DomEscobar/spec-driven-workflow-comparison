#!/usr/bin/env python3
"""Run real local model checks and save observed output; no network."""
import datetime
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    commands = [
        [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
        [sys.executable, 'scripts/sdd_gate.py', '--demo', '--approved', 'fixtures/approved.json',
         '--current', 'fixtures/current.json', '--evidence', 'fixtures/evidence.json'],
        [sys.executable, 'scripts/sdd_gate.py', '--demo', '--approved', 'fixtures/approved.json',
         '--current', 'fixtures/stale-current.json', '--evidence', 'fixtures/evidence.json'],
    ]
    runs = []
    for args in commands:
        p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
        runs.append({'command': ['python3'] + args[1:], 'exit_code': p.returncode,
                     'stdout': p.stdout, 'stderr': p.stderr})
    assert [r['exit_code'] for r in runs] == [0, 0, 3], runs
    count = int(re.search(r'Ran (\d+) tests', runs[0]['stderr']).group(1))
    positive, negative = [json.loads(r['stdout']) for r in runs[1:]]
    assert positive['eligible'] and not positive['released']
    assert not negative['eligible'] and 'STALE_EVIDENCE' in negative['reason_codes']
    inputs = sorted(p for folder in ('scripts', 'tests', 'fixtures')
                    for p in (ROOT / folder).rglob('*')
                    if p.is_file() and p.suffix in ('.py', '.json'))
    hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    report = {'observed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'python': platform.python_version(), 'platform': platform.system() + '/' + platform.machine(),
              'tests_run': count, 'runs': runs, 'input_sha256': hashes,
              'scope': 'Actual validator execution on synthetic fixtures; not application or pipeline execution'}
    docs = ROOT / 'docs'
    docs.mkdir(exist_ok=True)
    (docs / 'verification-results.json').write_text(json.dumps(report, indent=2) + '\n')
    text = '# Tatsächliche lokale Verifikation\n\n'
    text += '**Ausgeführt:** Standardbibliothek-Unitchecks und CLI des Konsistenzdemonstrators. '
    text += '**Nicht ausgeführt:** Public-Export-App, Agentenworkflow, authentifizierte CI, Release oder Benchmark.\n\n'
    text += f"Zeit: `{report['observed_at_utc']}`; Python `{report['python']}`, `{report['platform']}`.\n\n"
    text += f'Ergebnis: **{count} Tests erfolgreich**, Unit-Test-Exitcode 0; positive CLI 0; stale CLI erwartungsgemäß 3.\n\n'
    text += 'Die Suite prüft u. a. Spec-/Code-/Test-/Integrationsdrift, Environment/Config/Command-/Policywechsel, '
    text += 'stale Generation, fehlende/übersprungene/unvollständige Checks, Oracle-/Scopemutation, '
    text += 'Identitätsmismatch, fehlende Deliverables, Taskcheckbox ohne Receipt, Review, Terminalbindung, '
    text += 'Unknown-Effekte, begrenzte Repairs und zulässige Alternativen. Jeder Gateaufruf prüft außerdem Eingabereinheit und `released: false`.\n\n'
    text += '**Wichtig:** Die PASS-Fixtures wurden synthetisch erstellt. Ihr erfolgreicher Konsistenzcheck '
    text += 'ist keine Attestation ausgeführter Anwendungstests. Gleichnamige gefälschte Identitäten werden nicht '
    text += 'authentifiziert; nur Abweichungen vom extern vorgegebenen Fixturekontext erkannt. '
    text += 'Repairzähler sind modelliert, nicht geschützt persistiert. Kein TOCTOU-/Sandbox-/Recovery-Enforcement.\n\n'
    text += 'Reproduzieren: `python3 scripts/verify_package.py` im Paketverzeichnis. '
    text += 'Der Runner schreibt diese Datei und [verification-results.json](verification-results.json) '
    text += 'mit tatsächlich erfassten Ausgaben und SHA-256 der Code-/Fixtureinputs neu. '
    text += 'Dokumentations-/Resultdateien sind nicht Teil dieser Inputidentität; keine rekursive Evidencehashbildung.\n\n'
    for run in runs:
        text += '## `' + ' '.join(run['command']) + '`\n\n'
        text += f"Exitcode: `{run['exit_code']}`\n\n```text\n{run['stdout']}{run['stderr']}```\n\n"
    (docs / 'VERIFICATION.md').write_text(text)
    print(json.dumps({'tests_run': count, 'exit_codes': [r['exit_code'] for r in runs],
                      'saved': ['docs/VERIFICATION.md', 'docs/verification-results.json']}))


if __name__ == '__main__':
    main()
