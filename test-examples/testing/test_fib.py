import unittest
import fib

class TestFibFunctions(unittest.TestCase):
    def test_fib(self):
        self.assertEqual(fib.fib(5), 5)

        with self.assertRaises(TypeError):
            fib.fib('a')

    def test_fib_seq(self):
        self.assertEqual(fib.fib_seq(1, 5), [1, 1, 2, 3, 5])

    @unittest.skip('Demo skip')
    def test_nothing(self):
        self.fail("Should not happen")

    @unittest.expectedFailure
    def test_fail(self):
        self.assertEqual(1, 0)

    #@unittest.skipIf()
    #@unittest.skipUnless()


if __name__ == '__main__':
    unittest.main()

    #suite = unittest.TestLoader().loadTestsFromTestCase(TestFibFunctions)
    #unittest.TextTestRunner().run(suite)