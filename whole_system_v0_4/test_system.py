import copy,json,unittest
from pathlib import Path
import numpy as np
from system import Organism,Conductor,Record,Authority,run_history
from observer import digest,inspect

class SystemTests(unittest.TestCase):
    def setup_offer(self,x=-.1):
        o=Organism('test');o.commitment=(0,1.);o.x=x;o.a=.1
        facts={'X':np.ones((16,4)).tolist(),'y':[0.]*16,
               'committed_predictions':[1.]*16,'model_predictions':[0.]*16}
        r=Record.create('r',facts);o.records.append(r);a=Authority(b'external-test-key')
        e=o.envelope(r);s=a.sign(e,r);return o,r,a,e,s
    def test_positive_release_path_without_erasure(self):
        o,r,a,e,s=self.setup_offer();o.w[:]=[.1,.2,.3,.4];w=o.w.copy();root=r.root
        o.receive(r,e,s,a);self.assertGreater(o.x,0);o.release()
        np.testing.assert_array_equal(o.w,w);self.assertEqual(o.records[0].root,root)
        X=np.ones((4,4));np.testing.assert_array_equal(o.predict(X),X@w)
    def test_nonreception_is_possible(self):
        o,r,a,e,s=self.setup_offer(-1.);o.a=0.;o.receive(r,e,s,a)
        self.assertLess(o.x,0);self.assertIsNotNone(o.commitment)
    def test_single_delivery(self):
        o,r,a,e,s=self.setup_offer();o.receive(r,e,s,a)
        with self.assertRaises(ValueError):o.receive(r,e,s,a)
    def test_offering_binding(self):
        o,r,a,e,s=self.setup_offer();bad=copy.deepcopy(e);bad['impulse']=9.
        with self.assertRaises(ValueError):o.receive(r,bad,s,a)
    def test_revision_binding(self):
        o,r,a,e,s=self.setup_offer();o.learn(np.ones((1,4)),np.ones(1))
        with self.assertRaises(ValueError):o.receive(r,e,s,a)
    def test_other_authority_rejected(self):
        o,r,a,e,s=self.setup_offer()
        with self.assertRaises(ValueError):o.receive(r,e,s,Authority(b'other'))
    def test_evidence_recomputed(self):
        o,r,a,e,s=self.setup_offer();f=r.facts();f['committed_predictions']=[0.]*16
        r2=Record.create('r2',f)
        with self.assertRaises(ValueError):a.sign(o.envelope(r2),r2)
    def test_record_payload_not_mutated_by_read(self):
        o,r,a,e,s=self.setup_offer();f=r.facts();f['y'][0]=123
        self.assertEqual(digest(r.facts()),r.root)
    def test_replay_changes_learner(self):
        o,r,a,e,s=self.setup_offer();o.w[:]=1.;before=o.w.copy();c=Conductor()
        self.assertEqual(c.revisit(o),'r');self.assertFalse(np.array_equal(before,o.w))
        self.assertEqual(o.replay_steps,8);self.assertEqual(c.visits['r'],1)
    def test_saved_histories_integrity_and_finiteness(self):
        p=Path(__file__).parent/'results/histories.json';histories=json.loads(p.read_text())
        self.assertEqual(len(histories),12)
        for h in histories:
            self.assertEqual(inspect(h)['integrity_issues'],[])
            self.assertTrue(inspect(h)['environment_documented'])
            for e in h['events']:
                if 'x' in e:self.assertTrue(np.isfinite(e['x']))
    def test_saved_disclosures_match_experience(self):
        histories=json.loads((Path(__file__).parent/'results/histories.json').read_text())
        for h in histories:
            experiences=[e for e in h['events'] if e['kind']=='experience']
            for r in h['records']:
                f=r['facts'];e=next(e for e in experiences if e['block']==f['block'] and e['window']==f['window'])
                for key in ['X','y','committed_predictions','model_predictions','actual_predictions']:
                    self.assertEqual(f[key],e[key])
    def test_seeded_full_run_reproduces(self):
        saved=json.loads((Path(__file__).parent/'results/histories.json').read_text())
        for seed in [0,7]:
            history,arrays,summary=run_history(seed)
            self.assertEqual(history,saved[seed])
            self.assertEqual(summary['seed'],seed)

if __name__=='__main__':unittest.main()
