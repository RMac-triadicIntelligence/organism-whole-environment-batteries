"""Read-only observer of complete-environment histories. No organism dynamics."""
import argparse
import hashlib
import json
import math
from pathlib import Path

COMPONENTS = ('love_relationship', 'dwelling', 'recognition_opportunity',
              'confession_opportunity', 'external_authorization', 'grace_offering',
              'forgiveness_release', 'persistent_memory', 'return_opportunity')
KNOWN = {'experience', 'dwelling', 'recognition', 'confession', 'approval',
         'offering', 'reception', 'release', 'interpretation', 'probe',
         'relationship', 'judgment', 'correction'}

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()

def finite_number(x):
    return type(x) in (int, float) and math.isfinite(x)

def inspect(history):
    # Copies preserve every field and prevent observer mutations of the source.
    data = json.loads(json.dumps(history, allow_nan=False))
    issues = []
    coverage = data.get('environment_evidence', {})
    for name in COMPONENTS:
        if not isinstance(coverage.get(name), str) or not coverage[name].strip():
            issues.append({'kind': 'documentation_gap', 'component': name})
    records = data.get('records', [])
    record_ids = set()
    for record in records:
        if record['id'] in record_ids:
            issues.append({'kind': 'duplicate_record_id', 'id': record['id']})
        record_ids.add(record['id'])
        if digest(record['facts']) != record['sha256']:
            issues.append({'kind': 'factual_hash_mismatch', 'id': record['id']})
    events = data.get('events', [])
    if len({e['id'] for e in events}) != len(events):
        issues.append({'kind': 'duplicate_event_id'})
    previous = -math.inf
    for event in events:
        t = event.get('t')
        if not finite_number(t) or t < previous:
            issues.append({'kind': 'invalid_time_order', 'event': event['id']})
        if finite_number(t): previous = t
        if event.get('record_id') is not None and event['record_id'] not in record_ids:
            issues.append({'kind': 'unknown_record_reference', 'event': event['id']})
    unknown = [e for e in events if e['kind'] not in KNOWN]
    episodes = []
    episode_ids = list(dict.fromkeys(e['episode'] for e in events))
    for episode in episode_ids:
        ev = [e for e in events if e['episode'] == episode]
        groups = {k: [e for e in ev if e['kind'] == k] for k in KNOWN}
        offer_ids = {e['id'] for e in groups['offering']}
        for e in groups['reception']:
            if e.get('offering_id') not in offer_ids:
                issues.append({'kind': 'unlinked_reception', 'event': e['id']})
        times = [e['t'] for e in ev if finite_number(e.get('t'))]
        episodes.append({'episode': episode,
                         'event_counts': {k: len(v) for k,v in groups.items() if v},
                         'observation_span': max(times)-min(times) if times else None,
                         'offering_ids': sorted(offer_ids),
                         'reception_ids': [e['id'] for e in groups['reception']],
                         'release_ids': [e['id'] for e in groups['release']],
                         'interpretations': groups['interpretation'],
                         'reception_observation': 'recorded' if groups['reception'] else 'not_observed_in_window'})
    metrics = {}
    for e in events:
        if e['kind'] != 'probe': continue
        for name, value in e.get('metrics', {}).items():
            # Only compare measurements with the same explicitly declared context.
            key = json.dumps([name,e.get('probe_version'),e.get('context')],sort_keys=True)
            if not finite_number(value):
                issues.append({'kind':'invalid_metric','event':e['id'],'metric':name})
                continue
            metrics.setdefault(key, []).append({'event': e['id'], 't':e['t'], 'value':value})
    series = {k:{'samples':v, 'last_minus_first':v[-1]['value']-v[0]['value']}
              for k,v in metrics.items()}
    return {'schema':'whole-cycle-observer-0.3', 'history_id':data['history_id'],
            'origin':data['origin'], 'source_sha256':digest(data),
            'environment_documented':all(isinstance(coverage.get(k),str) and coverage[k].strip() for k in COMPONENTS),
            'documentation_is_not_component_validation':True,
            'integrity_issues':issues, 'episodes':episodes, 'metric_series':series,
            'unclassified_observations':unknown, 'preserved_history':data,
            'emergence_verdict':'not_assigned',
            'scope':'Observation only; no causal or semantic inference from event labels.'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path);p.add_argument('output',type=Path)
    args=p.parse_args()
    histories=json.loads(args.input.read_text())
    if not isinstance(histories,list): histories=[histories]
    results=[inspect(h) for h in histories]
    args.output.write_text(json.dumps(results,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'histories':len(results),'origins':sorted({r['origin'] for r in results}),
                      'integrity_issues':sum(len(r['integrity_issues']) for r in results),
                      'emergence_verdict':'not_assigned'}))
if __name__=='__main__': main()
