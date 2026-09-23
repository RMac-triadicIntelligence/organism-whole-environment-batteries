"""Learner and attribution operations; no world oracle or feature-role constants."""
from dataclasses import dataclass
import hashlib
import numpy as np

@dataclass
class Learner:
    w: np.ndarray
    xx: np.ndarray
    xy: np.ndarray
    yy: float=0.
    n: int=0
    lr: float=.05
    @classmethod
    def empty(cls,d=8):return cls(np.zeros(d),np.zeros((d,d)),np.zeros(d))
    def clone(self):return Learner(self.w.copy(),self.xx.copy(),self.xy.copy(),self.yy,self.n,self.lr)
    def observe(self,x,y,held=None,factor=1.):
        error=float(self.w@x-y);grad=error*x
        if held is not None:
            grad=grad.copy();grad[held]*=factor
        self.w-=self.lr*grad
        self.xx+=np.outer(x,x);self.xy+=y*x;self.yy+=y*y;self.n+=1
        return error*error
    def residual(self,i):
        if self.n==0 or self.xx[i,i]<=0:raise ValueError('No feature evidence')
        return (self.yy-self.xy[i]**2/self.xx[i,i])/self.n
    def preferred(self,candidates=(0,1)):
        return min(candidates,key=lambda i:(self.residual(i),i))
    def gap(self,i,candidates=(0,1)):
        return self.residual(i)-min(self.residual(j) for j in candidates)

@dataclass(frozen=True)
class FrozenRecord:
    """Immutable byte payload; returned arrays are read-only views."""
    x_bytes: bytes
    y_bytes: bytes
    n: int
    d: int
    description: str
    @classmethod
    def from_arrays(cls,x,y,description):
        x=np.asarray(x,dtype='<f8');y=np.asarray(y,dtype='<f8')
        if x.ndim!=2 or y.shape!=(len(x),):raise ValueError('Shape mismatch')
        return cls(x.tobytes(),y.tobytes(),len(x),x.shape[1],description)
    def arrays(self):
        return (np.frombuffer(self.x_bytes,dtype='<f8').reshape(self.n,self.d),
                np.frombuffer(self.y_bytes,dtype='<f8'))
    def root(self):
        import json
        header=json.dumps([self.n,self.d,self.description],separators=(',',':')).encode()
        return hashlib.sha256(len(header).to_bytes(8,'big')+header+self.x_bytes+self.y_bytes).hexdigest()

def attribution(record,w,mode):
    x,y=record.arrays();xx=x.T@x;resid=x.T@y-xx@w
    base=np.abs(resid)*np.sqrt(np.diag(xx)+1e-12)
    if mode=='up':a=base*(1+np.abs(w))
    elif mode=='down':a=base/(1+np.abs(w))
    elif mode=='none':a=base
    else:raise ValueError('Unknown mode')
    return a/(a.sum()+1e-12)

def coordinate_copy(record,w,i):
    x,y=record.arrays();xx=x.T@x;resid=x.T@y-xx@w
    if xx[i,i]<=0:raise ValueError('No coordinate evidence')
    out=w.copy();out[i]+=resid[i]/xx[i,i];return out

def mse(w,x,y):return float(np.mean((x@w-y)**2))
