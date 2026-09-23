"""Boundary diagnostics on exact original pre-offering organism states."""
import copy,hashlib,json,math,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'reference'))
import system as old
from observer import digest

LIMIT=2/(3*math.sqrt(3))
def saddle(a):
    if not math.isfinite(a) or abs(a)>=LIMIT:raise ValueError('no bistable separatrix')
    lo,hi=-1/math.sqrt(3),1/math.sqrt(3)
    for _ in range(80):
        mid=(lo+hi)/2
        if mid-mid**3+a>0:hi=mid
        else:lo=mid
    return (lo+hi)/2

def snapshot(o):
    return {'id':o.id,'w':o.w.tolist(),'commitment':list(o.commitment) if o.commitment else None,
            'x':o.x,'a':o.a,'revision':o.revision,'records':[{'id':r.id,'payload':r.payload,'root':r.root} for r in o.records],
            'offered':o.offered,'offer_id':o.offer_id,'episode':o.episode,'windows':list(o.windows),'replay_steps':o.replay_steps}

def recover():
    saved=json.loads((ROOT/'reference/histories.json').read_text());captures=[]
    original=old.Organism.receive
    def intercept(self,record,envelope,signature,authority):
        captures.append({'organism':copy.deepcopy(self),'record':copy.deepcopy(record),
                         'envelope':copy.deepcopy(envelope),'signature':signature})
        return original(self,record,envelope,signature,authority)
    old.Organism.receive=intercept
    try:
        for seed in range(12):
            h,_,_=old.run_history(seed)
            if h!=saved[seed]:raise AssertionError('original replay differs: '+str(seed))
    finally:old.Organism.receive=original
    for cap in captures:
        h=next(h for h in saved if h['history_id']==cap['organism'].id)
        approval=next(i for i,e in enumerate(h['events']) if e['kind']=='approval' and e['signature']==cap['signature'])
        cap['future_tilts']=[e['a'] for e in h['events'][approval+1:] if e['kind']=='dwelling']
        cap['original_assay']=next(e['x'] for e in h['events'][approval+1:] if e['kind']=='assay')
    return captures

class Branch(old.Organism):
    def configure(self,record,dose):
        self.bound={'organism':self.id,'record_root':record.root,'state_sha256':digest(snapshot(self)),
                    'impulse':float(dose),'steps':80,'dt':.05,'criterion':'x > instantaneous unstable root',
                    'scope':'one diagnostic delivery and assay; release requires terminal basin membership'}
    def envelope(self,record):
        e=copy.deepcopy(self.bound);e['state_sha256']=digest(snapshot(self));e['record_root']=record.root
        return e
    def release(self):
        if not self.offered or self.x<=saddle(self.a):raise ValueError('no right-basin assay endpoint')
        self.commitment=None;self.revision+=1

def step(x,a):
    def f(z):return z-z**3+a
    dt=.05;k1=f(x);k2=f(x+dt*k1/2);k3=f(x+dt*k2/2);k4=f(x+dt*k3)
    return x+dt*(k1+2*k2+2*k3+k4)/6

def trajectory(x,a,dose,future):
    x+=dose;t=0.;rows=[]
    def save(stage):rows.append({'t':t,'x':x,'a':a,'saddle':saddle(a),'right':bool(x>saddle(a)),'stage':stage})
    save('impulse')
    for _ in range(80):x=step(x,a);t+=.05;save('assay')
    for aa,n in future:
        a=aa;save('tilt_update')
        for _ in range(n):x=step(x,a);t+=.05;save('followup')
    flags=[r['right'] for r in rows];first=next((i for i,v in enumerate(flags) if v),None)
    tail=flags[max(0,len(flags)-max(1,math.ceil(len(flags)*.2))):]
    return rows,{'initial_right':flags[0],'assay_right':flags[80],
                 'terminal_right':flags[-1],'first_right_t':None if first is None else rows[first]['t'],
                 'recrossed_after_right':False if first is None else not all(flags[first:]),
                 'right_through_final_20pct_samples':all(tail),'observed_duration':rows[-1]['t'],
                 'assay_old_zero_rule':bool(rows[80]['x']>0)}

def branch(cap,dose):
    o=Branch.__new__(Branch);o.__dict__=copy.deepcopy(cap['organism'].__dict__)
    record=cap['record'];before=snapshot(o);o.configure(record,dose)
    auth=old.Authority(b'diagnostic-authority-reproducible-not-secure')
    env=o.envelope(record);sig=auth.sign(env,record);o.receive(record,env,sig,auth)
    released=False
    if o.x>saddle(o.a):o.release();released=True
    preserved=snapshot(o)
    memory_ok=all(before[k]==preserved[k] for k in ['w','records','windows','replay_steps'])
    probe=np.eye(4)
    residual=float(np.mean((o.predict(probe)-probe@o.w)**2))
    return {'released':released,'memory_and_weights_preserved':memory_ok,'direct_anchor_difference_after':residual,
            'envelope':env,'signature':sig,'assay_x':o.x,'post_state':preserved}

def run():
    out=ROOT/'results';out.mkdir(exist_ok=True);caps=recover();results=[];snapshots=[];traces={}
    for cap in caps:
        o=cap['organism'];distance=saddle(o.a)-o.x
        snapshots.append({'state':snapshot(o),'record_root':cap['record'].root,'original_envelope':cap['envelope'],
                          'original_signature':cap['signature'],'future_tilts':cap['future_tilts'],
                          'saddle':saddle(o.a),'distance':distance})
        for name,dose in [('original',.60),('below',distance-.02),('above',distance+.02),('oversized',distance+.5)]:
            if dose<=0:raise ValueError('nonpositive dose')
            b=branch(cap,dose)
            for mode,future in [('frozen',[(o.a,1600)]),('recorded',[(a,16) for a in cap['future_tilts']])]:
                raw,stats=trajectory(o.x,o.a,dose,future)
                if not np.isclose(raw[80]['x'],b['assay_x'],rtol=0,atol=1e-13):raise AssertionError('branch/trajectory mismatch')
                if name=='original' and not np.isclose(raw[80]['x'],cap['original_assay'],rtol=0,atol=1e-13):raise AssertionError('original assay mismatch')
                key=o.id+'_'+name+'_'+mode;traces[key]=raw
                results.append({'key':key,'organism':o.id,'dose_name':name,'dose':dose,'mode':mode,
                                'pre_x':o.x,'pre_a':o.a,'saddle':saddle(o.a),'distance':distance,
                                'margin':dose-distance,**stats,**b})
    summary={'origin':'actual-state diagnostic branches, not new independent histories',
             'original_histories_exactly_reproduced':12,'offering_states':len(caps),
             'branches':len(results)//2,'trajectory_observations':len(results),
             'protocol_sha256':hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest(),
             'results':results,'emergence_verdict':'unassigned'}
    for name,obj in [('snapshots',snapshots),('summary',summary),('trajectories',traces)]:
        (out/(name+'.json')).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
    for s in snapshots:print(s['state']['id'],'x',s['state']['x'],'a',s['state']['a'],'boundary',s['saddle'],'distance',s['distance'])
    for name in ['original','below','above','oversized']:
        rows=[r for r in results if r['dose_name']==name and r['mode']=='frozen']
        print(name,'released',sum(r['released'] for r in rows),'of',len(rows))
if __name__=='__main__':run()
