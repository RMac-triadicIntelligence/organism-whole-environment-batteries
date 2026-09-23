import ast,csv,json,unittest
from pathlib import Path
from dataclasses import FrozenInstanceError
import numpy as np
from core import Learner,FrozenRecord,attribution,coordinate_copy
from run import block,datahash,bootstrap
ROOT=Path(__file__).parent

class Integrity(unittest.TestCase):
    def test_fixed_draws_across_correlation(self):
        x0,y0=block(3,1,64,0);x1,y1=block(3,1,64,.95)
        np.testing.assert_array_equal(y0,y1)
        # For seed 3, signal=1 and only feature 0 is transformed.
        np.testing.assert_array_equal(x0[:,1:],x1[:,1:])
    def test_gradient_locality(self):
        a=Learner.empty();b=a.clone();x=np.arange(1,9,dtype=float)/10
        a.observe(x,1,held=3,factor=1);b.observe(x,1,held=3,factor=.05)
        keep=[i for i in range(8) if i!=3]
        np.testing.assert_array_equal(a.w[keep],b.w[keep]);self.assertAlmostEqual(b.w[3],.05*a.w[3])
    def test_evidence_preference_not_weight_ranking(self):
        a=Learner.empty();a.n=10;a.yy=10;a.xx=np.eye(8)*10;a.xy=np.array([9,1,0,0,0,0,0,0.])
        a.w[1]=100
        self.assertEqual(a.preferred(),0);self.assertGreater(a.gap(1),0)
    def test_no_evidence_rejected(self):
        with self.assertRaises(ValueError):Learner.empty().preferred()
    def test_record_immutability_and_hash_coverage(self):
        x,y=block(0,2,16,.95);r=FrozenRecord.from_arrays(x,y,'event');root=r.root()
        with self.assertRaises(FrozenInstanceError):r.description='rewrite'
        with self.assertRaises(ValueError):r.arrays()[0][0,0]=99
        y2=y.copy();y2[0]+=.1
        self.assertNotEqual(root,FrozenRecord.from_arrays(x,y2,'event').root())
        self.assertNotEqual(root,FrozenRecord.from_arrays(x,y,'other').root())
    def test_attribution_variants_have_declared_direction(self):
        r=FrozenRecord.from_arrays(np.eye(2),np.array([3.,1.]),'example');w=np.array([2.,0.])
        self.assertEqual(int(np.argmax(attribution(r,w,'up'))),0)
        self.assertEqual(int(np.argmax(attribution(r,w,'down'))),1)
    def test_unexposed_variants_equal(self):
        x,y=block(2,3,32,.95);r=FrozenRecord.from_arrays(x,y,'event');w=np.zeros(8)
        np.testing.assert_array_equal(attribution(r,w,'up'),attribution(r,w,'none'))
        np.testing.assert_array_equal(attribution(r,w,'down'),attribution(r,w,'none'))
    def test_diagnostic_copy_does_not_change_reader_or_record(self):
        x,y=block(1,2,16,.8);r=FrozenRecord.from_arrays(x,y,'event');w=np.arange(8)/10
        before=w.copy();root=r.root()
        attribution(r,w,'up');coordinate_copy(r,w,2)
        np.testing.assert_array_equal(w,before);self.assertEqual(root,r.root())
    def test_no_world_oracle_in_learner(self):
        tree=ast.parse((ROOT/'core.py').read_text())
        names={n.id for n in ast.walk(tree) if isinstance(n,ast.Name)}
        self.assertFalse(names & {'TRUE_RULE','TRAP_RULE','signal','World'})
    def test_saved_pairing_and_unconstrained_identity(self):
        rows=list(csv.DictReader((ROOT/'results/h2_trials.csv').read_text().splitlines()))
        arrays=np.load(ROOT/'results/inputs_and_trajectories.npz')
        for seed in range(24):
            for ci,rho in enumerate([0.,.8,.95]):
                sub=[r for r in rows if int(r['seed'])==seed and float(r['rho'])==rho]
                self.assertEqual(len(sub),6)
                self.assertEqual(len({r['input_hash'] for r in sub}),1)
                self.assertEqual(len({r['initial_hash'] for r in sub}),1)
                prefix=f'h2_{seed}_{ci}'
                self.assertEqual(sub[0]['input_hash'],datahash(arrays[prefix+'_x'],arrays[prefix+'_y']))
                free=[r for r in sub if float(r['factor'])==1.]
                np.testing.assert_array_equal(arrays[free[0]['array_prefix']+'_loss'],arrays[free[1]['array_prefix']+'_loss'])
                for r in sub:
                    a=Learner.empty();a.w=arrays[r['array_prefix']+'_initial_w'].copy()
                    losses=np.array([a.observe(x,y,int(r['held_feature']),float(r['factor'])) for x,y in zip(arrays[prefix+'_x'],arrays[prefix+'_y'])])
                    np.testing.assert_array_equal(losses,arrays[r['array_prefix']+'_loss'])
    def test_record_shared_across_all_reader_conditions(self):
        rows=list(csv.DictReader((ROOT/'results/h1_trials.csv').read_text().splitlines()))
        for seed in range(24):
            sub=[r for r in rows if int(r['seed'])==seed]
            self.assertEqual(len(sub),12);self.assertEqual(len({r['record_root'] for r in sub}),1)
    def test_paired_bootstrap_and_saved_summary(self):
        rows=list(csv.DictReader((ROOT/'results/paired_contrasts.csv').read_text().splitlines()))
        summary=json.loads((ROOT/'results/summary.json').read_text())
        vals=[np.mean([float(r['contrast']) for r in rows if r['hypothesis']=='H2' and int(r['seed'])==s and r['condition'].startswith('0.05:')]) for s in range(24)]
        self.assertEqual(bootstrap(vals),summary['H2']['0.05']['disagreement_minus_agreement'])
        self.assertEqual(bootstrap([0]*24)['ci95_percentile'],[0,0])
if __name__=='__main__':unittest.main()
