#!/usr/bin/env python3
"""Synthetic consistency demonstrator, NOT an authenticated acceptance service.
No commands are executed. The caller supplies the trust context and observations.
"""
import argparse
import hashlib
import json
from pathlib import PurePosixPath
import sys

BINDINGS = ('contract', 'spec', 'oracle', 'policy', 'environment', 'commands',
            'config', 'instructions', 'base', 'candidate', 'integration', 'generation')
PROTECTED = ('contract', 'spec', 'oracle', 'policy')


def digest(value):
    """Hash a JSON envelope; source strings retain whitespace and line endings."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def load(path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError('duplicate JSON key: ' + key)
            out[key] = value
        return out
    with open(path, encoding='utf-8') as stream:
        return json.load(stream, object_pairs_hook=unique,
                         parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def safe_path(path):
    return (isinstance(path, str) and bool(path) and '\\' not in path
            and not PurePosixPath(path).is_absolute()
            and all(p not in ('', '.', '..') for p in path.split('/')))


def binding(subject):
    return {key: subject[key] if key == 'generation' else digest(subject[key])
            for key in BINDINGS}


def result(reasons):
    return {'eligible': not reasons, 'state': 'BLOCKED' if reasons else 'ACCEPTED',
            'released': False, 'reason_codes': sorted(set(reasons)),
            'assurance': 'synthetic-consistency-only'}


def gate(approved, current, evidence):
    """Pure gate. approved/current must originate outside the builder in real use."""
    reasons = []
    if approved['schema'] != 1 or current['schema'] != 1:
        return result(['INVALID_SCHEMA'])
    if current['phase'] != 'VERIFYING' or current['status'] != 'active':
        reasons.append('INVALID_STATE')
    for key in PROTECTED:
        if digest(current[key]) != approved['pins'][key]:
            reasons.append('UNAUTHORIZED_' + key.upper())
    if current['contract']['scope'] != approved['scope']:
        reasons.append('SCOPE_MUTATION')
    if current['effect_outcome'] != 'none':
        reasons.append('EFFECT_RECONCILIATION_REQUIRED')
    for name in ('base', 'candidate', 'integration'):
        if not isinstance(current[name], dict) or not all(safe_path(p) for p in current[name]):
            return result(['INVALID_PATH'])
    # Actual synthetic file maps, not builder-declared changed_paths.
    for tree in ('candidate', 'integration'):
        changed = {p for p in set(current['base']) | set(current[tree])
                   if current['base'].get(p) != current[tree].get(p)}
        if not changed <= set(approved['scope']):
            reasons.append('OUT_OF_SCOPE')
    if not set(approved['deliverables']) <= set(current['integration']):
        reasons.append('MISSING_DELIVERABLE')
    required = approved['checks']
    if not required or any(v['kind'] not in ('test', 'review') for v in required.values()):
        return result(['INVALID_CHECK_POLICY'])
    if current['contract']['required_checks'] != list(required):
        reasons.append('CHECK_POLICY_MUTATION')
    expected = binding(current)
    if not isinstance(evidence, dict):
        return result(reasons + ['EVIDENCE_MISSING'])
    if evidence.get('schema') != 1:
        reasons.append('INVALID_EVIDENCE_SCHEMA')
    if evidence.get('producer') != approved['runner']:
        reasons.append('IDENTITY_MISMATCH')
    if evidence.get('binding') != expected:
        reasons.append('STALE_EVIDENCE')
    checks = evidence.get('checks', [])
    if not isinstance(checks, list) or any(not isinstance(c, dict) for c in checks):
        return result(reasons + ['INVALID_CHECKS'])
    ids = [c.get('id') for c in checks]
    if len(ids) != len(set(ids)) or set(ids) != set(required):
        reasons.append('CHECK_SET_MISMATCH')
    for check in checks:
        if check.get('id') not in required:
            continue
        rule = required[check['id']]
        if check.get('status') != 'pass' or type(check.get('exit_code')) is not int or check['exit_code'] != 0:
            reasons.append('CHECK_NOT_PASS')
        observed = check.get('observations')
        if not isinstance(observed, list) or not observed or len(set(observed)) != len(observed):
            reasons.append('EMPTY_OR_DUPLICATE_DISCOVERY')
        elif not set(rule['observations']) <= set(observed):
            reasons.append('INCOMPLETE_DISCOVERY')
        if check.get('command') != rule['command']:
            reasons.append('COMMAND_MISMATCH')
        if not isinstance(check.get('witness'), str) or not check['witness']:
            reasons.append('WITNESS_MISSING')
    if evidence.get('findings') != []:
        reasons.append('OPEN_OR_UNKNOWN_FINDINGS')
    if evidence.get('terminal_binding') != expected:
        reasons.append('TERMINAL_STATE_MISMATCH')
    if evidence.get('reviewer') != approved['reviewer'] or evidence.get('decision') != 'approve':
        reasons.append('REVIEW_MISSING')
    return result(reasons)


def reserve_repair(ledger, limit, finding):
    """Model cumulative reservation only; persistence/authorization are NOT provided."""
    if type(ledger.get('used')) is not int or ledger['used'] < 0:
        return {'allowed': False, 'reason': 'UNKNOWN_BUDGET', 'ledger': ledger}
    if ledger['used'] >= limit:
        return {'allowed': False, 'reason': 'BUDGET_EXHAUSTED', 'ledger': ledger}
    if not finding or finding == ledger.get('last_fingerprint'):
        return {'allowed': False, 'reason': 'NO_PROGRESS', 'ledger': ledger}
    return {'allowed': True, 'reason': 'RESERVED',
            'ledger': {'used': ledger['used'] + 1, 'last_fingerprint': finding}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--approved', required=True)
    parser.add_argument('--current', required=True)
    parser.add_argument('--evidence', required=True)
    parser.add_argument('--demo', action='store_true', help='acknowledge unauthenticated fixture mode')
    args = parser.parse_args()
    if not args.demo:
        print(json.dumps(result(['DEMO_MODE_REQUIRED']), sort_keys=True))
        return 2
    try:
        decision = gate(load(args.approved), load(args.current), load(args.evidence))
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        print(json.dumps(result(['INVALID_INPUT']), sort_keys=True))
        return 2
    print(json.dumps(decision, sort_keys=True))
    return 0 if decision['eligible'] else 3


if __name__ == '__main__':
    sys.exit(main())
