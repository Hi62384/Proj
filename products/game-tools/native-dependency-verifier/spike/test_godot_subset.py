import unittest
import godot_subset


class DescriptorSubsetTests(unittest.TestCase):
    def test_multiline_comments_and_quoted_punctuation(self):
        text = '[libraries]\nwindows = "a;\\\"b" ; comment\n[dependencies]\nwindows = {\n "a;}": "", ; comment\n "b": "x",\n}\n'
        result = godot_subset.parse_sections(text)
        self.assertEqual(result['libraries'][0][1], 'a;"b')
        self.assertEqual(result['dependencies'][0][1], {'a;}': '', 'b': 'x'})

    def test_invalid_inputs_fail_closed(self):
        cases = ['[dependencies]\nwindows = {"a": "", "a": ""}',
                 '[libraries]\na = "x"\na = "y"',
                 '[libraries]\na = "x"\n[libraries]\nb = "y"',
                 '[dependencies]\na = {"x": "y"',
                 '[libraries]\na = "unterminated',
                 '[dependencies]\na = ' + '{"x":' * 33 + '0' + '}' * 33,
                 'x' * (1024 * 1024 + 1)]
        for case in cases:
            with self.subTest(case=case[:50]), self.assertRaises(ValueError):
                godot_subset.parse_sections(case)


if __name__ == '__main__':
    unittest.main(verbosity=2)
