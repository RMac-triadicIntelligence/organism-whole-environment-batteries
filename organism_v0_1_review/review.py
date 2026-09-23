"""Supplemental checks; original organism implementation is unchanged."""
import json,hashlib,platform
from pathlib import Path
from dataclasses import asdict
import numpy as np
import organism as m

ROOT=Path(__file__).parent

def serial(v):
 if isinstance(v,np.ndarray):return v.tolist()
 if isinstance(v,np.generic):return v.item()
 raise TypeError(type(v).__name__)

def main():
 arms=['naive','erred','restored','erased']
 out={a:[m.run_arm(a,s) for s in range(8)] for a in arms}
 details={a:[{**{k:v for k,v in r.items() if k not in ('org','checkpoints')},
              'checkpoints':[asdict(c) for c in r['checkpoints']],
              'final_weights':r['org'].w,'final_XtX':r['org'].XtX,'final_Xty':r['org'].Xty}
             for r in runs] for a,runs in out.items()}
 (ROOT/'full_checkpoints_and_curves.json').write_text(json.dumps(details,default=serial,indent=2)+'\n')
 rng_checks=[]
 for seed in range(8):
  world=m.World(seed);shadow=m.World(seed)
  for _ in range(400):world.sample(True);shadow.sample(False)
  x,y=world.sample(False);xs,ys=shadow.sample(False)
  rng_checks.append({'seed':seed,'post_window_x_identical':np.array_equal(x,xs),'post_window_y_identical':y==ys})
 org=m.Organism('release-probe');world=m.World(0)
 for _ in range(400):org.observe(*world.sample(True))
 commit_weights=org.w.copy();org.commit_error('E1',m.TRAP_RULE,'error')
 for _ in range(301):org.observe(*world.sample(False))
 before=org.w.copy();loss=org.loss_history.copy();took,required=org.release('E1',True,1.)
 summary={'python':platform.python_version(),'numpy':np.__version__,
          'source_sha256':hashlib.sha256((ROOT/'organism.py').read_bytes()).hexdigest(),
          'mean_capture':{a:float(np.mean([r['second_trap_captured'] for r in runs])) for a,runs in out.items()},
          'checkpoint_warrant':{a:{'n':sum(len(r['checkpoints']) for r in out[a]),
                                 'warranted':sum(c.warranted for r in out[a] for c in r['checkpoints'])} for a in ['erred','restored']},
          'restored_erased_exact_final_weights':[np.array_equal(out['restored'][i]['org'].w,out['erased'][i]['org'].w) for i in range(8)],
          'shadow_stream_checks':rng_checks,
          'seed0_release':{'took':took,'required':required,'weights_unchanged':np.array_equal(before,org.w),
                           'stored_losses_unchanged':loss==org.loss_history,
                           'weights_at_forced_commit':commit_weights.tolist()},
          'last_burden_step':out['restored'][0]['burden_curve'][-1][0]}
 (ROOT/'review_results.json').write_text(json.dumps(summary,default=serial,indent=2)+'\n')
 print(json.dumps(summary,default=serial,indent=2))
if __name__=='__main__':main()
