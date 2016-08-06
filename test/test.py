import unittest
import pwrusb

class TestContrustorDestructor(unittest.TestCase):

  def test_constructor(self):
    handle = pwrusb.PyPwrUSB()
    self.assertTrue(handle is pwrusb.PyPwrUSB)
  
  def test_destructor(self):
    handle = pwrusb.PyPwrUSB()
    del handle
    self.assertTrue(handle is None)

if __name__ == '__main__':
  unittest.main()
