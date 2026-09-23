import json,hashlib,platform
from pathlib import Path
import numpy as np
from system import run_history
from observer import inspect
ROOT=Path(__file__).parent

def main():
    out=ROOT/'results';out.mkdir(exist_ok=True)
    summaries=[];histories=[];observations=[];arrays={}
    for seed in range(12):
        h,a,s=run_history(seed);histories.append(h);summaries.append(s);observations.append(inspect(h))
        arrays.update({f'seed{seed}_{k}':v for k,v in a.items()})
    (out/'histories.json').write_text(json.dumps(histories,indent=2,allow_nan=False)+'\n')
    (out/'observations.json').write_text(json.dumps(observations,indent=2,allow_nan=False)+'\n')
    np.savez_compressed(out/'inputs.npz',**arrays)
    summary={'origin':'operational_proxy_v0.4','histories':summaries,
             'protocol_sha256':hashlib.sha256((ROOT/'RUN_PROTOCOL.md').read_bytes()).hexdigest(),
             'python':platform.python_version(),'numpy':np.__version__,
             'total_offerings':sum(s['offerings'] for s in summaries),
             'total_releases':sum(s['releases'] for s in summaries),
             'observer_issues':[{'seed':i,'issues':r['integrity_issues']} for i,r in enumerate(observations) if r['integrity_issues']],
             'emergence_verdict':'unassigned; exploratory trajectories retained'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
