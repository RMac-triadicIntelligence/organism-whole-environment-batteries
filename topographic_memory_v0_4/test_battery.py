"""Integrity fixtures are not experimental histories."""
import json, unittest
from dataclasses import replace
import numpy as np
import battery as b

def fixture(mutation=None,ready=True):
    o=b.Organism('fixture','alpha',mutation);a=b.Authority();p=a.approve(o.oid,o.basis)
    o.commitment=(0,1.);o.pending_episode=1
    for t in range(3):
        o.window_facts.append(b.canonical({'tick':t,'X':[[0]*6]*4,'y':[0.]*4,'live':[0.]*4,'actual':[.4]*4}))
        o.memory.deposit(o.coord,o.context,.16,t)
    o.confession={'episode':1,'facts_root':b.digest(o.window_facts),'n':3,'mean':.16,'statement':'Corroborated performance evidence'}
    o.a=o.coefficient()
    if ready:o.x=-.1;o.evolve(8)
    return o,a,p

def positive(mutation=None):
    o,a,p=fixture(mutation);return b.Coordinator(a).release(o,p,8) is True

def reception_guard(mutation=None):
    o,a,p=fixture(mutation,False);return b.Coordinator(a).release(o,p,1) is False

def retention(mutation=None):
    o,a,p=fixture(mutation);before=b.digest(o.memory.snapshot())
    return b.Coordinator(a).release(o,p,8) is True and b.digest(o.memory.snapshot())==before

def broadcast_continues(mutation=None):
    o,a,p=fixture(mutation);released=b.Coordinator(a).release(o,p,8);o.evolve(16)
    return released is True and [e['tick'] for e in o.exposures]==[8,16]

def memory_path(mutation=None):
    o=b.Organism('memory','alpha',mutation);o.memory.deposit(o.coord,o.context,.2,0)
    p=b.Organism('other','alpha',mutation);p.memory.deposit(p.coord,p.context,-.2,0)
    return abs(b.rk4(-.7,o.coefficient(),.05)-b.rk4(-.7,p.coefficient(),.05))>.001

class Integrity(unittest.TestCase):
    def test_positive_release(self):self.assertIs(positive(),True)
    def test_reception_required(self):self.assertIs(reception_guard(),True)
    def test_memory_retained(self):self.assertIs(retention(),True)
    def test_grace_continues(self):self.assertIs(broadcast_continues(),True)
    def test_memory_changes_flow(self):self.assertIs(memory_path(),True)
    def test_counts_continue(self):
        m=b.Memory();c=b.Coord(0,0,0,0)
        for t in range(20):m.deposit(c,'settled',.1,t)
        self.assertEqual(m.count(),20);self.assertAlmostEqual(m.local(c,'settled'),.1)
    def test_categorical_distance(self):
        a=b.Coord(0,0,0,0)
        self.assertEqual(b.Memory.distance(a,b.Coord(0,0,0,1),'s','s'),b.Memory.distance(a,b.Coord(0,0,0,5),'s','s'))
        z=np.zeros(6);u=z.copy();u[0]=1;v=z.copy();v[4]=1
        self.assertNotEqual(b.encode('alpha',z,u,[1]).p,b.encode('alpha',z,v,[1]).p)
    def test_bad_signature(self):
        o,a,p=fixture()
        with self.assertRaisesRegex(ValueError,'invalid approval'):b.Coordinator(a).release(o,replace(p,signature='bad'),8)
    def test_wrong_recipient(self):
        o,a,p=fixture();o.oid='other'
        with self.assertRaisesRegex(ValueError,'invalid approval'):b.Coordinator(a).release(o,p,8)
    def test_source_binding(self):
        o,a,p=fixture();data=json.loads(p.payload);data['sources']['battery.py']='changed'
        self.assertFalse(a.verify(replace(p,payload=b.canonical(data)),o.oid,o.basis))
    def test_self_authorization(self):
        with self.assertRaisesRegex(ValueError,'self authorization'):b.Authority().approve('authority','alpha')
    def test_blank_and_forged_confession(self):
        for change in ({'statement':''},{'facts_root':'forged'},{'mean':99}):
            o,a,p=fixture();o.confession.update(change)
            self.assertIs(b.Coordinator(a).release(o,p,8),False)
    def test_bad_evidence(self):
        o,a,p=fixture();o.window_facts=[b.canonical({'X':[[0]*6],'y':[0],'live':[1],'actual':[0]})]*3
        o.confession['facts_root']=b.digest(o.window_facts);o.confession['mean']=-1
        self.assertIs(b.Coordinator(a).release(o,p,8),False)
        self.assertEqual(b.evidence([-1]*3)[0],'corrected')
    def test_same_tape(self):
        for (x,y,s),(xx,yy,ss) in zip(b.world(3),b.world(3)):
            np.testing.assert_array_equal(x,xx);np.testing.assert_array_equal(y,yy);self.assertFalse(x.flags.writeable)
    def test_facts_weights_preserved(self):
        o,a,p=fixture();facts=tuple(o.window_facts);weights=o.w.copy()
        self.assertTrue(b.Coordinator(a).release(o,p,8));self.assertEqual(tuple(o.window_facts),facts);np.testing.assert_array_equal(o.w,weights)
    def test_second_cycle(self):
        o,a,p=fixture();c=b.Coordinator(a);self.assertTrue(c.release(o,p,8))
        o.commitment=(1,1.);o.pending_episode=2;o.confession['episode']=2
        self.assertTrue(c.release(o,p,9));self.assertEqual(len(o.releases),2)
    def test_rk4_convergence(self):
        def end(dt):
            x=-.2
            for _ in range(round(2/dt)):x=b.rk4(x,.2,dt)
            return x
        self.assertLess(abs(end(.05)-end(.025)),1e-6)
    def test_broadcast_without_commitment(self):
        o=b.Organism('free','beta')
        for t in range(1,25):o.evolve(t)
        self.assertEqual([e['tick'] for e in o.exposures],[8,16,24])

def mutant_report():
    out=[]
    for name,case in [('reject_all',positive),('no_reception_gate',reception_guard),('delete_memory',retention),('drop_later_grace',broadcast_continues),('ignore_memory',memory_path)]:
        try:
            base=case();mutant=case(name)
            out.append({'mutant':name,'baseline':base,'mutant_result':mutant,'verdict':'DETECTED' if base is True and mutant is False else 'FAIL'})
        except Exception as e:out.append({'mutant':name,'verdict':'HARNESS_ERROR','exception':repr(e)})
    return out

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Integrity))
    report=mutant_report();print(json.dumps(report,indent=2))
    raise SystemExit(0 if result.wasSuccessful() and all(r['verdict']=='DETECTED' for r in report) else 1)
