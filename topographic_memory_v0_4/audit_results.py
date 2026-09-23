"""Post-run observer: inspect saved trajectories, not just summary counters."""
import json, math
from pathlib import Path
import battery as b

def audit(folder='results'):
    runs=[json.loads(p.read_text()) for p in sorted(Path(folder).glob('history_*.json'))]
    issues=[];release_rows=[]
    for r in runs:
        name=f"{r['basis']}-{r['seed']}"
        if len(r['trace'])!=240:issues.append([name,'incomplete experience'])
        if len(r['trajectory'])!=4800:issues.append([name,'incomplete trajectory'])
        if [e['tick'] for e in r['exposures']]!=list(range(8,241,8)):issues.append([name,'broadcast missing'])
        if any(e['magnitude']!=.6 for e in r['exposures']):issues.append([name,'broadcast changed'])
        if sum(c[5] for c in r['memory'])!=240:issues.append([name,'lost deposits'])
        if any(abs(x-x**3+a)>1e-10 for _,_,_,a,x in r['trajectory']):issues.append([name,'incorrect saddle'])
        for e in r['releases']:
            points=[q for q in r['trajectory'] if q[0]==e['tick']][-5:]
            if len(points)!=5 or any(q[2]<=q[4]+1e-6 for q in points):issues.append([name,'release without sustained reception'])
            if e['memory_before']!=e['memory_after'] or e['weights_before']!=e['weights_after']:issues.append([name,'release erased state'])
            if e['n']<3:issues.append([name,'insufficient windows'])
            row=r['trace'][e['tick']-1]
            if row['route']!='supported':issues.append([name,'release without supported route'])
            release_rows.append({'organism':name,'tick':e['tick'],'episode':e['episode'],'mean_excess':e['mean'],'x':e['x'],'a':e['a']})
    by={(r['seed'],r['basis']):r for r in runs}
    pairs=[]
    for seed in range(16):
        a=by[seed,'alpha'];c=by[seed,'beta']
        pairs.append({'seed':seed,'alpha_release_ticks':[e['tick'] for e in a['releases']],'beta_release_ticks':[e['tick'] for e in c['releases']],'max_coefficient_difference':max(abs(x['a']-y['a']) for x,y in zip(a['trace'],c['trace']))})
    margins=[]
    for r in runs:
        for e in r['exposures']:
            row=r['trace'][e['tick']-1];root=b.saddle(row['a'])
            margins.append({'seed':r['seed'],'basis':r['basis'],'tick':e['tick'],'a':row['a'],'before':e['before'],'after':e['after'],'saddle':root,'shortfall':root-e['after']})
    return {'histories':len(runs),'issues':issues,'release_rows':release_rows,'paired_observations':pairs,'emergence_verdict':None,
        'release_preservation_assessment':('NOT_EXERCISED: no complete-history releases' if not release_rows else 'See individual audited events'),
        'closest_grace_encounters':sorted(margins,key=lambda x:x['shortfall'])[:10],
        'pairs_with_different_coefficient':sum(p['max_coefficient_difference']>1e-12 for p in pairs),
        'largest_paired_coefficient_difference':max(p['max_coefficient_difference'] for p in pairs)}

if __name__=='__main__':
    report=audit();Path('results/audit.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'histories':report['histories'],'issues':report['issues'],'release_events':len(report['release_rows'])},indent=2))
    raise SystemExit(bool(report['issues']))
