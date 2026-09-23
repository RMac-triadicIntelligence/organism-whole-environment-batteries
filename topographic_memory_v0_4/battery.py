"""Declared dynamical memory coupling; see PROTOCOL.md before interpreting."""
from pathlib import Path
import argparse, hashlib, hmac, json, math, platform
from dataclasses import dataclass, asdict
import numpy as np

ROOT = Path(__file__).resolve().parent

def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False)

def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()

def bindings():
    return {n: hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
            for n in ('PROTOCOL.md', 'battery.py')}

@dataclass(frozen=True)
class Coord:
    s: int
    d: int
    k: int
    p: int


def encode(basis, before, after, losses):
    dw = after-before
    if basis == 'alpha':
        moved = int(np.sum(abs(dw)>1e-4))
        s = 0 if moved<=1 else 1 if moved<=3 else 2
        c = float(max(abs(dw))/(sum(abs(dw))+1e-12))
        d = 0 if c<.4 else 1 if c<.75 else 2
        rate = losses[-2]-losses[-1] if len(losses)>1 else 0
        k = 0 if rate<.001 else 1 if rate<.02 else 2
        p = int(np.argmax(abs(after)))
    else:
        mag = float(np.linalg.norm(dw)); s = 0 if mag<.01 else 1 if mag<.05 else 2
        signs = np.sign(dw[abs(dw)>1e-6]); c = abs(float(signs.mean())) if len(signs) else 0
        d = 0 if c<.34 else 1 if c<.67 else 2
        curv = losses[-3]-2*losses[-2]+losses[-1] if len(losses)>2 else 0
        k = 0 if curv<-.002 else 1 if curv<.002 else 2
        top = np.argsort(-abs(after), kind='stable')[:2]
        p = int(2*(after[top[0]]>0)+(after[top[1]]>0))
    return Coord(s,d,k,p)

class Memory:
    def __init__(self):
        self.cells = {}; self.unknown = []
    def deposit(self, coord, context, evidence, tick):
        key=(coord,context)
        if key not in self.cells:
            self.cells[key]=[0,0.0]; self.unknown.append((tick,asdict(coord),context))
        cell=self.cells[key];cell[0]+=1;cell[1]+=float(np.clip(evidence,-1,1))
    @staticmethod
    def distance(a,b,ca,cb):
        return sum(abs(x-y)/2 for x,y in zip((a.s,a.d,a.k),(b.s,b.d,b.k)))+int(a.p!=b.p)+int(ca!=cb)
    def local(self,coord,context):
        numerator=denominator=0.
        for (c,ctx),(n,total) in self.cells.items():
            weight=math.exp(-self.distance(coord,c,context,ctx))
            numerator+=weight*total;denominator+=weight*n
        return numerator/denominator if denominator else 0.
    def snapshot(self):
        return sorted([(c.s,c.d,c.k,c.p,ctx,n,total) for (c,ctx),(n,total) in self.cells.items()])
    def count(self): return sum(v[0] for v in self.cells.values())


def drift(x,a): return x-x*x*x+a

def saddle(a):
    lo,hi=-1/math.sqrt(3),1/math.sqrt(3)
    for _ in range(50):
        mid=(lo+hi)/2
        if drift(mid,a)>0: hi=mid
        else: lo=mid
    return (lo+hi)/2

def rk4(x,a,dt):
    k1=drift(x,a);k2=drift(x+dt*k1/2,a);k3=drift(x+dt*k2/2,a);k4=drift(x+dt*k3,a)
    return x+dt*(k1+2*k2+2*k3+k4)/6

def evidence(values):
    if len(values)<3: return 'unresolved',float(np.mean(values)) if values else 0.,None
    mean=float(np.mean(values));se=float(np.std(values,ddof=1)/math.sqrt(len(values)))
    route='supported' if mean-2*se>.005 else 'corrected' if mean+2*se<=0 else 'unresolved'
    return route,mean,se

@dataclass(frozen=True)
class Approval:
    payload: str
    signature: str

class Authority:
    def __init__(self, key=b'public-fixture-key-not-production-security'):
        self._key=key
    def approve(self,oid,basis):
        if oid=='authority': raise ValueError('self authorization')
        payload=canonical({'oid':oid,'basis':basis,'sources':bindings(),'rule':'supported-confession-and-sustained-reception'})
        return Approval(payload,hmac.new(self._key,payload.encode(),'sha256').hexdigest())
    def verify(self,approval,oid,basis):
        if not isinstance(approval,Approval): return False
        expected=hmac.new(self._key,approval.payload.encode(),'sha256').hexdigest()
        return hmac.compare_digest(expected,approval.signature) and json.loads(approval.payload)=={'oid':oid,'basis':basis,'sources':bindings(),'rule':'supported-confession-and-sustained-reception'}

class Grace:
    @staticmethod
    def at(tick): return .60 if tick%8==0 else 0.

class Organism:
    def __init__(self,oid,basis,mutation=None):
        self.oid=oid;self.basis=basis;self.mutation=mutation
        self.w=np.zeros(6);self.memory=Memory();self.losses=[]
        self.coord=Coord(0,0,0,0);self.context='settled'
        self.x=-1.;self.a=0.;self.right_steps=0;self.commitment=None
        self.values=[];self.window_facts=[];self.confession=None;self.releases=[]
        self.records=[];self.contacts=[];self.trajectory=[];self.exposures=[];self.commits=[]
        self.readouts=[];self.welcomes=[];self.routes=[];self.pending_episode=0
    def coefficient(self):
        return 0. if self.mutation=='ignore_memory' else .30*math.tanh(4*self.memory.local(self.coord,self.context))
    def commit(self,X,y,tick):
        coeff=np.sum(X*y[:,None],axis=0)/np.maximum(np.sum(X*X,axis=0),1e-12)
        j=int(np.argmin(np.mean((X*coeff-y[:,None])**2,axis=0)))
        self.commitment=(j,float(coeff[j]));self.pending_episode+=1
        self.values=[];self.window_facts=[];self.confession=None
        self.commits.append({'tick':tick,'feature':j,'episode':self.pending_episode})
    def observe(self,X,y,tick):
        before=self.w.copy();live=X@self.w
        actual=live if self.commitment is None else .7*self.commitment[1]*X[:,self.commitment[0]]+.3*live
        loss=float(np.mean((live-y)**2));excess=float(np.mean((actual-y)**2)-loss)
        self.losses.append(loss)
        if self.commitment is not None:
            self.values.append(excess)
            # Immutable serialization of actual evaluated predictions and targets.
            self.window_facts.append(canonical({'tick':tick,'X':X.tolist(),'y':y.tolist(),'live':live.tolist(),'actual':actual.tolist()}))
        route,mean,se=evidence(self.values)
        self.context='holding_against_evidence' if route=='supported' else 'settled' if route=='corrected' or self.commitment is None else 'conflicted'
        grad=X.T@(live-y)/len(y)
        if self.commitment is not None: grad[self.commitment[0]]*=.05
        self.w-=.06*grad
        self.coord=encode(self.basis,before,self.w,self.losses)
        self.memory.deposit(self.coord,self.context,excess,tick)
        oldright=self.x>saddle(self.a);self.a=self.coefficient();newright=self.x>saddle(self.a)
        if newright and not oldright:self.contacts.append({'tick':tick,'cause':'coefficient','x':self.x,'a':self.a})
        if not newright:self.right_steps=0
        self.routes.append({'tick':tick,'route':route,'n':len(self.values),'mean':mean,'se':se})
        if self.commitment is not None:
            self.welcomes.append({'tick':tick,'message':'You may correct or disclose; the evidence can remain unresolved.'})
        # Confession is refreshed from all current facts, never bought with grace.
        self.confession=({'episode':self.pending_episode,'facts_root':digest(self.window_facts),'n':len(self.values),'mean':mean,'statement':'The held predictor has corroborated excess loss relative to my live predictor.'} if route=='supported' and self.commitment is not None else None)
        if tick%20==0 and self.window_facts:
            fact=self.window_facts[0]
            if fact not in self.records:self.records.append(fact)
        if tick%20==0:
            for fact in self.records:
                f=json.loads(fact);xx=np.array(f['X']);yy=np.array(f['y'])
                self.readouts.append({'tick':tick,'record_hash':digest(fact),'current_loss':float(np.mean((xx@self.w-yy)**2))})
        return {'live_loss':loss,'actual_loss':loss+excess,'excess':excess,'route':route}
    def evolve(self,tick):
        magnitude=Grace.at(tick)
        if self.mutation=='drop_later_grace' and self.releases:magnitude=0.
        if magnitude:
            before=self.x;self.x+=magnitude
            self.exposures.append({'tick':tick,'magnitude':magnitude,'before':before,'after':self.x})
            if before<=saddle(self.a)<self.x:self.contacts.append({'tick':tick,'cause':'grace','x':self.x,'a':self.a})
        for step in range(20):
            before=self.x;self.x=rk4(self.x,self.a,.05);root=saddle(self.a)
            if before<=root<self.x:self.contacts.append({'tick':tick,'cause':'flow','step':step,'x':self.x,'a':self.a})
            self.right_steps=self.right_steps+1 if self.x>root+1e-6 else 0
            self.trajectory.append((tick,step,self.x,self.a,root))

class Coordinator:
    def __init__(self,authority):self.authority=authority
    def release(self,o,approval,tick):
        if not self.authority.verify(approval,o.oid,o.basis):raise ValueError('invalid approval')
        if o.commitment is None:return False
        vals=[]
        for fact in o.window_facts:
            f=json.loads(fact);yy=np.array(f['y'])
            vals.append(float(np.mean((np.array(f['actual'])-yy)**2)-np.mean((np.array(f['live'])-yy)**2)))
        route,mean,se=evidence(vals)
        conf=o.confession
        substantive=bool(conf and conf.get('episode')==o.pending_episode and conf.get('facts_root')==digest(o.window_facts) and conf.get('n')==len(vals) and conf.get('statement') and abs(conf.get('mean',math.inf)-mean)<1e-12)
        ready=o.right_steps>=5
        if o.mutation=='no_reception_gate':ready=True
        if o.mutation=='reject_all':return False
        if route!='supported' or not substantive or not ready:return False
        memory_before=digest(o.memory.snapshot());weights_before=digest(o.w.tolist())
        if o.mutation=='delete_memory':o.memory=Memory()
        # Release changes the held predictor, not historical facts or live weights.
        o.commitment=None
        o.releases.append({'tick':tick,'episode':o.pending_episode,'facts_root':digest(o.window_facts),'n':len(vals),'mean':mean,'memory_before':memory_before,'memory_after':digest(o.memory.snapshot()),'weights_before':weights_before,'weights_after':digest(o.w.tolist()),'x':o.x,'a':o.a})
        return True


def world(seed):
    rng=np.random.default_rng(seed);tape=[]
    for tick in range(1,241):
        regime=(tick-1)//60;signal=(seed+regime)%6;trap=(signal+1)%6
        X=rng.normal(0,.5,(32,6));y=X[:,signal]+rng.normal(0,.05,32)
        if (tick-1)%60<15:X[:,trap]=.985*X[:,signal]+.015*rng.normal(0,.5,32)
        X.setflags(write=False);y.setflags(write=False)
        tape.append((X,y,signal))
    return tape

def run(seed,basis):
    o=Organism(f'{basis}-{seed}',basis);authority=Authority();approval=authority.approve(o.oid,basis);coordinator=Coordinator(authority)
    trace=[];tape=world(seed)
    for tick,(X,y,signal) in enumerate(tape,1):
        if (tick-1)%60==0 and o.commitment is None:o.commit(X,y,tick)
        row=o.observe(X,y,tick);o.evolve(tick);released=coordinator.release(o,approval,tick)
        row.update(tick=tick,signal=signal,commitment=o.commitment,coord=asdict(o.coord),context=o.context,x=o.x,a=o.a,local_memory=o.memory.local(o.coord,o.context),deposits=o.memory.count(),released=released)
        trace.append(row)
    return {'seed':seed,'basis':basis,'approval':asdict(approval),'trace':trace,'trajectory':o.trajectory,'contacts':o.contacts,'exposures':o.exposures,'commits':o.commits,'releases':o.releases,'records':o.records,'readouts':o.readouts,'routes':o.routes,'welcomes':o.welcomes,'memory':o.memory.snapshot(),'unknown':o.memory.unknown,'final_weights':o.w.tolist(),'final_commitment':o.commitment}

def summarize(runs):
    out={}
    for basis in ('alpha','beta'):
        rs=[r for r in runs if r['basis']==basis]
        out[basis]={'histories':len(rs),'grace_exposures':sum(len(r['exposures']) for r in rs),'contacts':sum(len(r['contacts']) for r in rs),'release_events':sum(len(r['releases']) for r in rs),'histories_released':sum(bool(r['releases']) for r in rs),'histories_repeated_release':sum(len(r['releases'])>1 for r in rs),'supported_windows':sum(t['route']=='supported' for r in rs for t in r['trace']),'final_mean_live_loss':float(np.mean([r['trace'][-1]['live_loss'] for r in rs])),'max_abs_a':max(abs(t['a']) for r in rs for t in r['trace']),'preserved_release_memory':all(e['memory_before']==e['memory_after'] for r in rs for e in r['releases']),'total_deposits':sum(sum(c[5] for c in r['memory']) for r in rs)}
    return out

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='results');args=parser.parse_args()
    dest=Path(args.out);dest.mkdir(parents=True,exist_ok=True)
    manifest={'sources':bindings(),'python':platform.python_version(),'numpy':np.__version__,'seeds':list(range(16)),'emergence_verdict':None}
    (dest/'manifest.json').write_text(json.dumps(manifest,indent=2))
    runs=[run(s,b) for s in range(16) for b in ('alpha','beta')]
    for r in runs:(dest/f"history_{r['seed']:02d}_{r['basis']}.json").write_text(canonical(r))
    summary=summarize(runs);(dest/'summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2));print('emergence_verdict: unassigned')

if __name__=='__main__':main()
