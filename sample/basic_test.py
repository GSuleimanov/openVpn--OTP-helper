import unittest
import main


class TestArguments(unittest.TestCase):

    def test_one_arg(self):
        arguments = ['first']
        with self.assertRaises(ValueError):
            main.checkArgs(arguments)

    def test_two_args(self):
        arguments = ['first', 'second']
        with self.assertRaises(ValueError):
            main.checkArgs(arguments)

    def test_three_args_incorrect_profile(self):
        arguments = ['first', 'second', 'third']
        with self.assertRaises(ValueError):
            main.checkArgs(arguments)

    def test_three_args_correct_profile(self):
        arguments = ['example', 'example', 'on']
        args = main.checkArgs(arguments)
        self.assertTrue(len(args), 2)


if __name__ == '__main__':
    unittest.main()
