#!/usr/bin/env python3
"""Bounded documentation checks; stdlib only, no vendor execution."""
import ast
import json
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ['README.md', 'sources.md', 'docs/openspec.md', 'docs/spec-kit.md',
            'docs/comparison-matrix.md', 'docs/drift-and-gates.md',
            'docs/example-workflow.md', 'docs/requirements-and-tests.md',
            'docs/adoption-and-cost.md', 'docs/verification.md', 'STATUS.md']
LINK = re.compile(r'\[[^\]]+\]\(([^\s)]+)\)')
PIN = re.compile(r'https://github.com/(Fission-AI/OpenSpec|github/spec-kit)/blob/([0-9a-f]{40})/(.+)')
NETWORK_IDS = ['O2', 'O3', 'O4', 'O11', 'S1', 'S2', 'S6', 'S14']


def check(root=ROOT, network=False):
    errors = []
    stats = {'markdown_files': 0, 'internal_links': 0, 'tables': 0,
             'matrix_rows': 0, 'json_blocks': 0, 'sources': 0, 'network_ok': 0}
    for name in REQUIRED:
        if not (root / name).is_file():
            errors.append('missing: ' + name)
    registry = json.loads((root / 'evidence/sources.json').read_text())
    sources = registry['sources']
    ids = set()
    for source in sources:
        assert source['id'] not in ids, 'duplicate source ID'
        ids.add(source['id'])
        match = PIN.fullmatch(source['url'])
        pin = registry['pins'][source['product']]
        if not match or match.group(1) != pin['repository'] or match.group(2) != pin['commit']:
            errors.append('un-pinned source: ' + source['id'])
    stats['sources'] = len(sources)
    for file in sorted(root.rglob('*.md')):
        if '.git' in file.parts:
            continue
        stats['markdown_files'] += 1
        text = file.read_text(encoding='utf-8')
        relative = file.relative_to(root).as_posix()
        fence = None
        code = []
        width = None
        table_line = 0
        for number, line in enumerate(text.splitlines(), 1):
            if line.startswith('```'):
                if fence is None:
                    fence = line[3:].strip()
                    code = []
                else:
                    if fence == 'json':
                        try:
                            json.loads('\n'.join(code))
                            stats['json_blocks'] += 1
                        except ValueError:
                            errors.append(f'{relative}:{number}: invalid JSON block')
                    fence = None
                width = None
                continue
            if fence is not None:
                code.append(line)
                continue
            if line.startswith('|') and line.endswith('|'):
                cells = re.split(r'(?<!\\)\|', line)[1:-1]
                if width is None:
                    width = len(cells)
                    stats['tables'] += 1
                    table_line = 1
                else:
                    table_line += 1
                    if len(cells) != width:
                        errors.append(f'{relative}:{number}: table width')
                    if table_line == 2 and not all(re.fullmatch(r'\s*:?-+:?\s*', c) for c in cells):
                        errors.append(f'{relative}:{number}: table separator')
                    if relative == 'docs/comparison-matrix.md' and table_line > 2:
                        stats['matrix_rows'] += 1
                        if '](' not in cells[-1]:
                            errors.append(f'{relative}:{number}: matrix row lacks citation')
            else:
                width = None
            for href in LINK.findall(line):
                parsed = urlsplit(href)
                if parsed.scheme:
                    if parsed.scheme != 'https' or any(x in parsed.netloc for x in ('example.com', 'example.org', 'localhost')):
                        errors.append(f'{relative}:{number}: unsupported or placeholder URL')
                    if parsed.netloc == 'github.com' and '/blob/' in parsed.path and not re.fullmatch(r'/[^/]+/[^/]+/blob/[0-9a-f]{40}/.+', parsed.path):
                        errors.append(f'{relative}:{number}: unpinned source link')
                    continue
                target = (file.parent / unquote(parsed.path)).resolve() if parsed.path else file.resolve()
                if not target.is_relative_to(root.resolve()) or not target.is_file():
                    errors.append(f'{relative}:{number}: broken internal link {href}')
                elif parsed.fragment:
                    # This dossier uses explicit HTML IDs for fragment links.
                    content = target.read_text()
                    if f'id="{unquote(parsed.fragment)}"' not in content:
                        errors.append(f'{relative}:{number}: missing explicit anchor {href}')
                stats['internal_links'] += 1
        if fence is not None:
            errors.append(relative + ': unclosed fence')
        if any(token in text for token in ('/root/', 'brain.huecki.com', 'BEGIN PRIVATE KEY', 'ghp_')):
            errors.append(relative + ': forbidden private-data marker')
    for file in sorted((root / 'scripts').glob('*.py')):
        ast.parse(file.read_text(), filename=str(file))
    if stats['matrix_rows'] < 30:
        errors.append('comparison matrix too short')
    if network:
        by_id = {s['id']: s for s in sources}
        for ident in NETWORK_IDS:
            source = by_id[ident]
            match = PIN.fullmatch(source['url'])
            url = f'https://raw.githubusercontent.com/{match.group(1)}/{match.group(2)}/{match.group(3)}'
            try:
                request = urllib.request.Request(url, headers={'User-Agent': 'spec-comparison-doc-check/1.0'})
                with urllib.request.urlopen(request, timeout=30) as response:
                    body = response.read()
                    if response.status != 200 or not body:
                        raise ValueError('empty or non-200 response')
                stats['network_ok'] += 1
            except Exception as exc:
                errors.append(f'network {ident}: {type(exc).__name__}')
    return stats, errors


if __name__ == '__main__':
    if any(arg != '--network' for arg in sys.argv[1:]):
        raise SystemExit('usage: python3 scripts/check_docs.py [--network]')
    result, failures = check(network='--network' in sys.argv[1:])
    print(json.dumps({'status': 'FAIL' if failures else 'PASS', 'counts': result,
                      'errors': failures}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(failures))
