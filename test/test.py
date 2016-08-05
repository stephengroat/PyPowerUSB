import unittest
import pwrusb

class TestContrustorDestructor(unittest.TestCase):

  def test_constructor(self):
    self.assertTrue(pwrusb.PyPwrUSB() is pwrusb.PyPwrUSB)

if __name__ == '__main__':
  unittest.main()
