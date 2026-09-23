import csv,hashlib,json,platform
from pathlib import Path
import numpy as np
from core import Learner,FrozenRecord,attribution,coordinate_copy,mse
ROOT=Path(__file__).parent

def block(seed,stream,n,rho):
    # Identical draw counts for every rho. Only the feature transformation differs.
    rng=np.random.default_rng(np.random.SeedSequence([seed,stream]))
    x=rng.normal(0,.5,(n,8));noise=rng.normal(0,.05,n);injection=rng.normal(0,.5,n)
    signal=seed%2;other=1-signal
    y=x[:,signal]+noise
    x[:,other]=rho*x[:,signal]+(1-rho)*injection
    return x,y

def datahash(x,y):return hashlib.sha256(x.tobytes()+y.tobytes()).hexdigest()
def csvwrite(name,rows):
    with name.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def bootstrap(values):
    values=np.asarray(values,float);rng=np.random.default_rng(41011)
    res=values[rng.integers(0,len(values),(5000,len(values)))].mean(axis=1)
    return {'mean':float(values.mean()),'ci95_percentile':[float(v) for v in np.quantile(res,[.025,.975])],
            'n_seed_blocks':len(values)}

def main():
    out=ROOT/'results';out.mkdir(exist_ok=True)
    h2=[];h1=[];arrays={};records=[]
    for seed in range(24):
        for ci,rho in enumerate([0.,.8,.95]):
            xp,yp=block(seed,10+ci,256,rho);x,y=block(seed,20+ci,400,0.)
            xe,ye=block(seed,30+ci,1024,0.)
            prefix=f'h2_{seed}_{ci}'
            for name,a in [('pre_x',xp),('pre_y',yp),('x',x),('y',y),('eval_x',xe),('eval_y',ye)]:arrays[prefix+'_'+name]=a
            org=Learner.empty()
            for xi,yi in zip(xp,yp):org.observe(xi,yi)
            favored=org.preferred();initial=org.w.copy()
            for factor in [1.,.05,0.]:
                for alignment,held in [('favored',favored),('disfavored',1-favored)]:
                    clone=org.clone();loss=np.array([clone.observe(xi,yi,held,factor) for xi,yi in zip(x,y)])
                    tag=prefix+f'_{factor}_{alignment}';arrays[tag+'_loss']=loss;arrays[tag+'_final_w']=clone.w.copy()
                    arrays[tag+'_initial_w']=initial.copy()
                    h2.append({'seed':seed,'rho':rho,'factor':factor,'alignment':alignment,'held_feature':held,
                               'evidence_gap':org.gap(held),'prequential_mse':float(loss.mean()),
                               'final_eval_mse':mse(clone.w,xe,ye),'input_hash':datahash(x,y),
                               'initial_hash':hashlib.sha256(initial.tobytes()).hexdigest(),'array_prefix':tag})
        xr,yr=block(seed,100,128,.95);record=FrozenRecord.from_arrays(xr,yr,'Observed correlated context; no supplied accusation')
        xb,yb=block(seed,101,400,.95);xd,yd=block(seed,102,400,0.);xe,ye=block(seed,103,1024,.95)
        prefix=f'h1_{seed}'
        for name,a in [('record_x',xr),('record_y',yr),('reader_x',xb),('reader_y',yb),('later_x',xd),('later_y',yd),('eval_x',xe),('eval_y',ye)]:arrays[prefix+'_'+name]=a
        reader=Learner.empty();states={'unexposed':reader.w.copy()}
        for i,(xi,yi) in enumerate(zip(xb,yb),1):
            reader.observe(xi,yi)
            if i==32:states['early']=reader.w.copy()
        states['confounded']=reader.w.copy()
        for xi,yi in zip(xd,yd):reader.observe(xi,yi)
        states['later']=reader.w.copy()
        root=record.root();records.append({'seed':seed,'root':root,'description':record.description})
        for position,w in states.items():
            arrays[prefix+'_'+position+'_w']=w.copy();baseline=mse(w,xe,ye)
            gains=[baseline-mse(coordinate_copy(record,w,i),xe,ye) for i in range(8)]
            for mode in ['up','none','down']:
                a=attribution(record,w,mode);top=int(np.argmax(a))
                h1.append({'seed':seed,'position':position,'mode':mode,'top_feature':top,
                           'gain':gains[top],'baseline_mse':baseline,'post_action_mse':baseline-gains[top],
                           'best_coordinate_gain':max(gains),'regret':max(gains)-gains[top],
                           'attribution':json.dumps(a.tolist()),'record_root':record.root()})
            assert record.root()==root
    for r in h2:
        base=next(v for v in h2 if v['seed']==r['seed'] and v['rho']==r['rho'] and v['factor']==1. and v['alignment']=='favored')
        r['excess_prequential_mse']=r['prequential_mse']-base['prequential_mse']
        r['excess_final_mse']=r['final_eval_mse']-base['final_eval_mse']
    csvwrite(out/'h2_trials.csv',h2);csvwrite(out/'h1_trials.csv',h1)
    np.savez_compressed(out/'inputs_and_trajectories.npz',**arrays)
    (out/'record_roots.json').write_text(json.dumps(records,indent=2)+'\n')
    contrasts=[];h2_summary={}
    for factor in [.05,0.]:
        per_seed=[];covs=[]
        for seed in range(24):
            pairs=[];gap=[];excess=[]
            for rho in [0.,.8,.95]:
                rows=[r for r in h2 if r['seed']==seed and r['rho']==rho and r['factor']==factor]
                fav=next(r for r in rows if r['alignment']=='favored');dis=next(r for r in rows if r['alignment']=='disfavored')
                delta=dis['excess_prequential_mse']-fav['excess_prequential_mse'];pairs.append(delta)
                gap.append(dis['evidence_gap']);excess.append(dis['excess_prequential_mse'])
                contrasts.append({'hypothesis':'H2','seed':seed,'condition':f'{factor}:{rho}','contrast':delta})
            per_seed.append(float(np.mean(pairs)));covs.append(float(np.cov(gap,excess,ddof=0)[0,1]))
        h2_summary[str(factor)]={'disagreement_minus_agreement':bootstrap(per_seed),
                                'mean_within_seed_gap_cost_covariance':float(np.mean(covs))}
    h1_summary={}
    for alternative in ['none','down']:
        per_seed=[];by_position={}
        for pos in ['unexposed','early','confounded','later']:
            diffs=[]
            for seed in range(24):
                up=next(r for r in h1 if r['seed']==seed and r['position']==pos and r['mode']=='up')
                base=next(r for r in h1 if r['seed']==seed and r['position']==pos and r['mode']==alternative)
                diffs.append(up['gain']-base['gain'])
                contrasts.append({'hypothesis':'H1','seed':seed,'condition':f'up-{alternative}:{pos}','contrast':diffs[-1]})
            by_position[pos]=bootstrap(diffs)
        for seed in range(24):
            per_seed.append(float(np.mean([r['contrast'] for r in contrasts if r['hypothesis']=='H1' and r['seed']==seed and r['condition'].startswith('up-'+alternative+':')])))
        h1_summary['up_minus_'+alternative]={'overall':bootstrap(per_seed),'by_position':by_position}
    csvwrite(out/'paired_contrasts.csv',contrasts)
    summary={'H2':h2_summary,'H1':h1_summary,'n_h2_trials':len(h2),'n_h1_trials':len(h1),
             'runtime':{'python':platform.python_version(),'numpy':np.__version__},
             'protocol_sha256':hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest()}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
