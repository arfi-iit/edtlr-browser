from django.test import TestCase
from browser.management.commands.importdata import EntryXmlParser
from browser.management.commands.importdata import DictMarkdownToHtmlConverter
from tempfile import NamedTemporaryFile
from pathlib import Path


class EntryXmlParserTestCase(TestCase):
    """Defines test cases for the EntryXmlParser class."""

    def setUp(self):
        """Set up the test case."""
        with NamedTemporaryFile("wt",
                                encoding='utf-8',
                                delete=False,
                                delete_on_close=False) as tmp_file:
            tmp_file.write("""<?xml version='1.0' encoding='UTF-8'?>
<entry id="3917" xmlns:edtlr="https://edtlr.iit.academiaromana-is.ro">
  <titleWord md5hash="56ef7f1ea1078edecf215a3521343127">ECLISIARHÍE</titleWord>
  <titleWordNormalized md5hash="0da5e09d295d842d3878a995f0b0228a">ECLISIARHIE</titleWordNormalized>
  <body md5hash="9721086245e27c0ce40701a887440209">
    <paragraph>**ECLISIARHÍE**  s. f.  v. **ecleziarhie**.</paragraph>
  </body>
</entry>
""")
            tmp_file.close()
            self.xml_file = Path(tmp_file.name)

    def test_parse(self):
        """Test that the parser works."""
        parser = EntryXmlParser()
        entry = parser.parse(self.xml_file)
        self.assertEqual(entry.id, 3917)
        self.assertEqual(entry.title_word, "ECLISIARHÍE")
        self.assertEqual(entry.title_word_md5,
                         "56ef7f1ea1078edecf215a3521343127")
        self.assertEqual(entry.title_word_normalized, "ECLISIARHIE")
        self.assertEqual(entry.title_word_normalized_md5,
                         "0da5e09d295d842d3878a995f0b0228a")
        self.assertEqual(entry.text_md5, "9721086245e27c0ce40701a887440209")


class DictMarkdownToHtmlConverterTestCase(TestCase):
    """Defines test cases for the dictmarkdown to HTML converter."""

    TEST_DATA = [
        ('ECLISIARHÍE  s. f.  v. ecleziarhie.',
         'ECLISIARHÍE  s. f.  v. ecleziarhie.'),
        ('**ECLISIARHÍE**  s. f.  v. **ecleziarhie**.',
         '<strong>ECLISIARHÍE</strong>  s. f.  v. <strong>ecleziarhie</strong>.'
         ),
        ('**ECLISIARHÍE^1^**  s. f.  v. **ecleziarhie_i_**.',
         '<strong>ECLISIARHÍE<superscript>1</superscript></strong>  s. f.  v. <strong>ecleziarhie<subscript>i</subscript></strong>.'
         ),
        ('*ECLISIARHÍE*  s. f.  v. **ecleziarhie**.',
         '<em>ECLISIARHÍE</em>  s. f.  v. <strong>ecleziarhie</strong>.')
    ]

    def setUp(self):
        """Set up the tests."""
        self.converter = DictMarkdownToHtmlConverter()

    def test_conversion(self):
        """Test that the conversion works."""
        for input_str, expected in self.TEST_DATA:
            self.assertEqual(self.converter.convert(input_str), expected)
