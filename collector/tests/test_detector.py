import unittest
from collector.events.detector import ProductionEventDetector
class DetectorTests(unittest.TestCase):
 def test_one_event_per_cycle(self):
  d=ProductionEventDetector('Output',True,0,'Result');self.assertIsNone(d.update({'Output':False}));self.assertIsNotNone(d.update({'Output':True,'Result':True}));self.assertIsNone(d.update({'Output':True}));self.assertIsNone(d.update({'Output':False}));self.assertIsNotNone(d.update({'Output':True,'Result':False}))
 def test_active_low(self):
  d=ProductionEventDetector('Output',False,0);self.assertIsNone(d.update({'Output':True}));self.assertIsNotNone(d.update({'Output':False}))
