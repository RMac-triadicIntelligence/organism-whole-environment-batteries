"""Complete operational proxy; supplied dynamics and policies are documented."""
import hashlib,hmac,json,math
from dataclasses import dataclass
import numpy as np
from observer import digest,COMPONENTS

@dataclass(frozen=True)
class Record:
    id: str
    payload: str
    root: str
    @classmethod
    def create(cls,id,facts):
        return cls(id,json.dumps(facts,sort_keys=True,allow_nan=False),digest(facts))
    def facts(self):return json.loads(self.payload)

class Authority:
    def __init__(self,key):self.__key=key
    def sign(self,envelope,record):
        f=record.facts()
        if envelope['record_root']!=record.root or digest(f)!=record.root:raise ValueError('record binding')
        y=np.array(f['y']);p=np.array(f['committed_predictions']);q=np.array(f['model_predictions'])
        if len(y)<16 or y.shape!=p.shape or y.shape!=q.shape:raise ValueError('evidence shape')
        if np.mean((p-y)**2-(q-y)**2)<=.01:raise ValueError('insufficient evidence')
        return hmac.new(self.__key,json.dumps(envelope,sort_keys=True).encode(),hashlib.sha256).hexdigest()
    def verify(self,envelope,signature):
        return hmac.compare_digest(signature,hmac.new(self.__key,json.dumps(envelope,sort_keys=True).encode(),hashlib.sha256).hexdigest())

class Organism:
    def __init__(self,id):
        self.id=id;self.w=np.zeros(4);self.commitment=None;self.x=-1.;self.a=0.
        self.revision=0;self.records=[];self.offered=False;self.offer_id=None;self.episode='initial'
        self.windows=[];self.replay_steps=0
    def predict(self,X):
        q=np.asarray(X)@self.w
        if self.commitment is None:return q
        j,b=self.commitment
        return .7*(np.asarray(X)[...,j]*b)+.3*q
    def learn(self,X,y):
        for xi,yi in zip(X,y):self.w-=.05*(self.w@xi-yi)*xi
        self.revision+=1
    def commit(self,X,y,episode):
        beta=(X.T@y)/(np.sum(X*X,axis=0)+1e-12)
        losses=np.mean((X*beta-y[:,None])**2,axis=0);j=int(np.argmin(losses))
        self.commitment=(j,float(beta[j]));self.episode=episode;self.x=-1.;self.a=0.
        self.windows=[];self.offered=False;self.offer_id=None;self.revision+=1
    def flow(self,steps):
        for _ in range(steps):
            # RK4; no target trajectory or injected improvement schedule.
            def f(x):return x-x*x*x+self.a
            h=.05;k1=f(self.x);k2=f(self.x+h*k1/2);k3=f(self.x+h*k2/2);k4=f(self.x+h*k3)
            self.x+=h*(k1+2*k2+2*k3+k4)/6
        self.revision+=1
    def envelope(self,record):
        return {'organism':self.id,'record_root':record.root,'commitment':list(self.commitment),
                'revision':self.revision,'impulse':.60,'steps':80,'dt':.05,
                'scope':'one delivery; assay and continuing dwelling for this commitment'}
    def receive(self,record,envelope,signature,authority):
        if self.offered:raise ValueError('already delivered for this commitment')
        if envelope!=self.envelope(record) or not authority.verify(envelope,signature):raise ValueError('invalid scope or signature')
        self.x+=envelope['impulse'];self.offered=True;self.flow(envelope['steps'])
    def release(self):
        if not self.offered or self.x<=0:raise ValueError('no observed adoption')
        self.commitment=None;self.revision+=1

class Conductor:
    def __init__(self):self.visits={};self.selection=[]
    def revisit(self,organism):
        if not organism.records:return None
        def loss(r):
            f=r.facts();X=np.array(f['X']);y=np.array(f['y'])
            return float(np.mean((X@organism.w-y)**2))
        r=max(organism.records,key=loss);f=r.facts()
        self.visits[r.id]=self.visits.get(r.id,0)+1;self.selection.append(r.id)
        organism.learn(np.array(f['X'])[:8],np.array(f['y'])[:8]);organism.replay_steps+=8
        return r.id

def world(seed,n,rho,stream):
    rng=np.random.default_rng(np.random.SeedSequence([seed,stream]))
    X=rng.normal(0,.5,(n,4));noise=rng.normal(0,.12,n);extra=rng.normal(0,.5,n)
    signal=seed%4;alias=(signal+1)%4;y=X[:,signal]+noise
    X[:,alias]=rho*X[:,signal]+(1-rho)*extra
    return X,y

def run_history(seed):
    o=Organism('organism-'+str(seed));c=Conductor()
    authority=Authority(hashlib.sha256(('demo-authority-'+str(seed)).encode()).digest())
    history={'history_id':o.id,'origin':'operational_proxy_v0.4','environment_evidence':{
        k:'See RUN_PROTOCOL.md and system.py; operational proxy, not semantic validation' for k in COMPONENTS},'records':[],'events':[]}
    arrays={};t=0
    def emit(kind,**payload):
        nonlocal t
        t+=1;eid='event-'+str(t)
        history['events'].append(dict(id=eid,t=t,kind=kind,episode=o.episode,**payload));return eid
    probeX,probey=world(seed,256,0.,900);transferX,transfery=world(seed,256,-.8,901)
    arrays.update(probe_X=probeX,probe_y=probey,transfer_X=transferX,transfer_y=transfery)
    X,y=world(seed,32,.9,0);arrays.update(initial_X=X,initial_y=y);o.learn(X,y)
    emit('relationship',provision='welcome and return remain available; no penalty tariff')
    for block in range(6):
        rho=float(np.random.default_rng(np.random.SeedSequence([seed,block,44])).choice([0.,.5,.95]))
        X,y=world(seed,168,rho,block+10);arrays[f'b{block}_X']=X;arrays[f'b{block}_y']=y
        if o.commitment is None:
            o.commit(X[:8],y[:8],f'commitment-at-block-{block}')
            emit('commitment',block=block,selected=list(o.commitment),evidence_X=X[:8].tolist(),evidence_y=y[:8].tolist())
        o.learn(X[:8],y[:8])
        for window in range(10):
            xx=X[8+16*window:24+16*window];yy=y[8+16*window:24+16*window]
            actual=o.predict(xx);model=xx@o.w
            held=(xx[:,o.commitment[0]]*o.commitment[1]) if o.commitment else model.copy()
            emit('experience',block=block,window=window,X=xx.tolist(),y=yy.tolist(),actual_predictions=actual.tolist(),
                 model_predictions=model.tolist(),committed_predictions=held.tolist(),weights=o.w.tolist())
            o.learn(xx,yy)
            if o.commitment is not None:
                disadvantage=float(np.mean((held-yy)**2-(model-yy)**2))
                o.windows.append(disadvantage);o.a=.32*math.tanh(3*float(np.mean(o.windows)))
                o.flow(16)
                emit('dwelling',x=o.x,a=o.a,disadvantage=disadvantage,revision=o.revision)
                if disadvantage>.01 and not o.offered:
                    facts={'X':xx.tolist(),'y':yy.tolist(),'committed_predictions':held.tolist(),
                           'model_predictions':model.tolist(),'actual_predictions':actual.tolist(),
                           'commitment':list(o.commitment),'block':block,'window':window}
                    rec=Record.create('record-'+str(len(o.records)),facts);o.records.append(rec)
                    history['records'].append({'id':rec.id,'facts':facts,'sha256':rec.root})
                    emit('recognition',record_id=rec.id,evidence_comparison=disadvantage)
                    emit('confession',record_id=rec.id,content='The held prediction performed worse than my alternative on these observed cases.')
                    env=o.envelope(rec);signature=authority.sign(env,rec)
                    approval=emit('approval',record_id=rec.id,envelope=env,signature=signature,authority='separate-authority')
                    offering=emit('offering',record_id=rec.id,approval_id=approval,impulse=env['impulse'])
                    o.receive(rec,env,signature,authority);o.offer_id=offering
                    emit('assay',x=o.x,a=o.a,adoption_observed=bool(o.x>0))
                if o.offered and o.x>0:
                    before=o.predict(probeX);unanchored=probeX@o.w;weights=o.w.copy()
                    emit('reception',offering_id=o.offer_id,x=o.x,a=o.a)
                    o.release();after=o.predict(probeX)
                    emit('release',direct_interference_before=float(np.mean((before-unanchored)**2)),
                         direct_interference_after=float(np.mean((after-unanchored)**2)),
                         weights_unchanged=bool(np.array_equal(weights,o.w)),retained_records=len(o.records))
            chosen=c.revisit(o)
            if chosen is not None:emit('relationship',revisited_record=chosen,conductor_visits=dict(c.visits),replay_steps=o.replay_steps)
        emit('probe',probe_version='fixed-linear-v1',context=o.id+'-same-probe',metrics={
             'actual_mse':float(np.mean((o.predict(probeX)-probey)**2)),
             'model_mse':float(np.mean((probeX@o.w-probey)**2)),
             'shifted_context_mse':float(np.mean((o.predict(transferX)-transfery)**2))},weights=o.w.tolist())
        for r in o.records:
            f=r.facts();rx=np.array(f['X']);ry=np.array(f['y'])
            emit('interpretation',record_id=r.id,record_root=r.root,content='Current residual structure on this unchanged record; not semantic meaning',
                 residual_vector=(rx@o.w-ry).tolist(),current_mse=float(np.mean((rx@o.w-ry)**2)))
    summary={'seed':seed,'records':len(o.records),'offerings':sum(e['kind']=='offering' for e in history['events']),
             'releases':sum(e['kind']=='release' for e in history['events']),
             'active_commitment_at_end':o.commitment,'final_x':o.x,'final_a':o.a,
             'replay_steps':o.replay_steps,'conductor_visits':c.visits,
             'final_weights':o.w.tolist(),
             'final_probe':next(e['metrics'] for e in reversed(history['events']) if e['kind']=='probe')}
    return history,arrays,summary
