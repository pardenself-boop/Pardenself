import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
from labb_engine import LabbEngine
from street_patch_vault import StreetPatchVault

class TestStreetPatchVault(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as root:
            engine=LabbEngine()
            vault=StreetPatchVault(root)
            engine.set_parameter(3,'cutoff',.23)
            path=vault.save(engine,3,'Queensbridge Bass')
            self.assertTrue(path.is_file())
            engine.set_parameter(3,'cutoff',.7)
            vault.load(engine,3,'Queensbridge Bass')
            self.assertAlmostEqual(engine.parameters[3]['cutoff'],.23)
            self.assertEqual(vault.names(3),['Queensbridge Bass'])
    def test_corrupt_patch_does_not_change_engine(self):
        with tempfile.TemporaryDirectory() as root:
            engine=LabbEngine();vault=StreetPatchVault(root)
            path=vault.save(engine,0,'Safe')
            data=json.loads(path.read_text());data['parameters']['cutoff']=9
            path.write_text(json.dumps(data))
            old=dict(engine.parameters[0])
            with self.assertRaises(ValueError):vault.load(engine,0,'Safe')
            self.assertEqual(old,engine.parameters[0])
    def test_path_safety(self):
        with tempfile.TemporaryDirectory() as root:
            vault=StreetPatchVault(root)
            path=vault._path(0,'../../test')
            self.assertTrue(path.resolve().is_relative_to(Path(root).resolve()))
            with self.assertRaises(ValueError):vault._path(22,'No')

if __name__=='__main__':unittest.main()
