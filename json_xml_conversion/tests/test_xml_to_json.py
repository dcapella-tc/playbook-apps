import unittest

from helpers.xml_to_json import xml_to_json


class TestXmlToJson(unittest.TestCase):
    def test_leaf(self):
        self.assertEqual(xml_to_json('<a>1</a>'), {'a': '1'})

    def test_nesting(self):
        self.assertEqual(xml_to_json('<a><b>1</b></a>'), {'a': {'b': '1'}})

    def test_repeated_tags(self):
        self.assertEqual(xml_to_json('<a><b>1</b><b>2</b></a>'), {'a': {'b': ['1', '2']}})

    def test_whitespace_handling(self):
        self.assertEqual(xml_to_json('<a>  x  </a>'), {'a': 'x'})

    def test_empty_text_leaf(self):
        self.assertEqual(xml_to_json('<a></a>'), {'a': ''})

    def test_invalid_xml_raises(self):
        with self.assertRaises(ValueError):
            xml_to_json('<a>')

    def test_empty_input_raises(self):
        with self.assertRaises(ValueError):
            xml_to_json('   ')


if __name__ == '__main__':
    unittest.main()
