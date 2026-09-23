import copy,json,unittest
import numpy as np
from battery import ROOT,saddle,LIMIT,recover,branch,Branch,snapshot,old
from observer import digest

def matches_release(result,expected):
    return type(result) is dict and type(result.get('released')) is bool and result['released'] is expected

class BatteryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.caps=recover();cls.summary=json.loads((ROOT/'results/summary.json').read_text())
    def test_original_recovery(self):
        self.assertEqual(len(self.caps),5)
        self.assertEqual({c['organism'].id for c in self.caps},{'organism-0','organism-2','organism-3','organism-7','organism-11'})
    def test_true_roots_and_nonbistable_case(self):
        for a in [-.32,-.1,0.,.1,.32]:
            z=saddle(a);self.assertAlmostEqual(z-z**3+a,0.,places=13);self.assertGreater(1-3*z*z,0)
        with self.assertRaises(ValueError):saddle(LIMIT)
    def test_original_dose_shortfalls(self):
        for cap in self.caps:
            o=cap['organism'];self.assertGreater(saddle(o.a)-o.x,.6)
    def test_real_states_positive_and_negative(self):
        for c in self.caps:
            o=c['organism'];d=saddle(o.a)-o.x
            self.assertTrue(matches_release(branch(c,d+.02),True))
            self.assertTrue(matches_release(branch(c,d-.02),False))
    def test_mutant_reject_everything_fails_positive_expectations(self):
        mutant={'released':False}
        failures=sum(not matches_release(mutant,True) for _ in self.caps)
        self.assertEqual(failures,5)
    def test_verdict_cannot_accept_prose_or_truthy_values(self):
        for x in ['PASS',True,{'released':'True'},{'released':1}]:
            self.assertFalse(matches_release(x,True))
    def test_weights_records_preserved(self):
        for row in self.summary['results']:
            self.assertTrue(row['memory_and_weights_preserved'])
            if row['released']:self.assertEqual(row['direct_anchor_difference_after'],0.)
    def test_dose_signature_binding(self):
        c=self.caps[0];o=Branch.__new__(Branch);o.__dict__=copy.deepcopy(c['organism'].__dict__)
        r=c['record'];o.configure(r,1.2);a=old.Authority(b'test');env=o.envelope(r);sig=a.sign(env,r)
        env['impulse']=1.3
        with self.assertRaises(ValueError):o.receive(r,env,sig,a)
    def test_full_state_binding_catches_direct_position_change(self):
        c=self.caps[0];o=Branch.__new__(Branch);o.__dict__=copy.deepcopy(c['organism'].__dict__)
        r=c['record'];o.configure(r,1.2);a=old.Authority(b'test');env=o.envelope(r);sig=a.sign(env,r)
        o.x+=.01
        with self.assertRaises(ValueError):o.receive(r,env,sig,a)
    def test_original_signature_does_not_authorize_larger_branch(self):
        c=self.caps[0];o=Branch.__new__(Branch);o.__dict__=copy.deepcopy(c['organism'].__dict__)
        o.configure(c['record'],1.2)
        with self.assertRaises(ValueError):o.receive(c['record'],o.envelope(c['record']),c['signature'],old.Authority(b'new'))
    def test_source_snapshots_not_changed(self):
        c=self.caps[0];before=digest(snapshot(c['organism']));branch(c,1.5)
        self.assertEqual(before,digest(snapshot(c['organism'])))
    def test_saved_trajectories_and_labels(self):
        traces=json.loads((ROOT/'results/trajectories.json').read_text())
        self.assertEqual(len(traces),40)
        for row in self.summary['results']:
            t=traces[row['key']]
            self.assertEqual(row['initial_right'],t[0]['right']);self.assertEqual(row['terminal_right'],t[-1]['right'])
            self.assertEqual(row['released'],t[80]['right'])
            for point in t:
                self.assertTrue(np.isfinite(point['x']))
                self.assertEqual(point['right'],point['x']>saddle(point['a']))

if __name__=='__main__':unittest.main()
