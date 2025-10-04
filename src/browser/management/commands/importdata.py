"""Defines the command for importing data into the database."""
from browser.models.entry import Entry
from django.core.management.base import BaseCommand
from pathlib import Path
import xml.etree.ElementTree as XML
from typing import Tuple


class Command(BaseCommand):
    """Implements the command for importing data into the database."""

    help = "Import the data into the database."
    requires_migrations_checks = True

    def add_arguments(self, parser):
        """Add command-line arguments.

        Parameters
        ----------
        parser: argparse.Parser, required
            The command-line arguments parser.
        """
        parser.add_argument(
            '--input-directory',
            help="The path of the directory containing dictionary entries.",
            required=True)

    def handle(self, *args, **options):
        """Import the data into the database."""
        input_dir = Path(options['input_directory'])

        for entry_file in input_dir.glob("*.xml"):
            entry = self.__read_contents(entry_file)
            if self.__update_entry(entry):
                style = self.style.SUCCESS
                message = f'Entry {entry_file.stem} updated.'
            else:
                style = self.style.NOTICE
                message = f'Entry {entry_file.stem} did not chage.'
            self.stdout.write(message, style)

        self.stdout.write("Finished importing data.")

    def __update_entry(self, entry: Entry):
        """Update the specified entry if changed.

        Parameters
        ----------
        entry: Entry, required
            The entry to update.

        Returns
        -------
        entry_updated: bool
            True if the entry was updated; False if no update required.
        """
        if not Entry.objects.filter(id=entry.id).exists():
            entry.save()
            return True

        db_entry = Entry.objects.get(id=entry.id)
        if db_entry.is_equal_to(entry):
            return False

        db_entry.copy_values_from(entry)
        db_entry.save()
        return True

    def __read_contents(self, entry_file: Path) -> Entry:
        """Read the contents of the entry file.

        Parameters
        ----------
        entry_file: Path, required
            The path of the entry file.

        Returns
        -------
        entry: Entry
            The entry read from the file.
        """
        parser = EntryXmlParser()
        return parser.parse(entry_file)


class EntryXmlParser:
    """Parse the contents of an XML into an Entry."""

    def parse(self, xml_file: Path) -> Entry | None:
        """Parse the contents of the provided file into an Entry.

        Parameters
        ----------
        xml_file: Path, required
            The XML file containing the Entry.

        Returns
        -------
        entry: Entry
            The entry or None.
        """
        tree = XML.parse(xml_file)
        root = tree.getroot()
        id = self.__parse_id(root)
        title_word, title_word_md5 = self.__parse_title_word(root, 'titleWord')
        twn, twn_md5 = self.__parse_title_word(root, 'titleWordNormalized')
        text_html, text_md5 = self.__parse_body(root)
        return Entry(id=id,
                     title_word=title_word,
                     title_word_md5=title_word_md5,
                     title_word_normalized=twn,
                     title_word_normalized_md5=twn_md5,
                     text_html=text_html,
                     text_md5=text_md5)

    def __parse_body(self, xml_root: XML.ElementTree) -> Tuple[str, str]:
        """Parse the body of the entry.

        Parameters
        ----------
        xml_root: ElementTree, required
            The root of the XML tree.

        Returns
        -------
        (html, md5): tuple of (str, str)
            A tuple containing the HTML markup of the entry, and the MD5 sum.
        """
        converter = DictMarkdownToHtmlConverter()
        for elem in xml_root.iter('body'):
            md5 = elem.get('md5hash')
            paragraphs = elem.iter('paragraph')
            html = '\n'.join([converter.convert(p.text) for p in paragraphs])
            return (f'<article>\n{html}\n</article>', md5)

        return ('', '')

    def __parse_title_word(self,
                           xml_root: XML.ElementTree,
                           tag_name: str,
                           md5: str = 'md5hash') -> Tuple[str, str]:
        """Parse the title word specified by tag name.

        Parameters
        ----------
        xml_root: ElementTree, required
            The root element that represents the entry.
        tag_name: str, required
            The name of the tag containing the title word.
        md5: str, optional
            The name of the attribute containing the MD5 hash.
            Default value si 'md5hash'.

        Returns
        -------
        (title_word, md5hash): tuple of (str, str)
            The title word and its MD5 hash.
        """
        for elem in xml_root.iter(tag_name):
            return (elem.text, elem.get(md5))
        return ('', '')

    def __parse_id(self, xml_root: XML.ElementTree) -> int:
        """Parse the id of the entry.

        Parameters
        ----------
        xml_root: ElementTree, required
            The root element that represents the entry.

        Returns
        -------
        id: int
            The id of the entry.
        """
        val = xml_root.get('id')
        return int(val)


class DictMarkdownToHtmlConverter:
    """Converts DictMarkdown to HTML."""

    def convert(self, text: str) -> str:
        """Convert the dict markdown string to HTML.

        Parameters
        ----------
        text: str, required
            The text to convert.

        Returns
        -------
        html: str
            The text converted to HTML.
        """
        text = self.__handle_bold(text)
        html = ''
        open_marks = []
        collection = iter(text)
        c = next(collection, None)
        while c:
            match c:
                case DictMarkdown.SUPERSCRIPT:
                    html = self.__append_tag(html, DictMarkdown.SUPERSCRIPT,
                                             open_marks,
                                             DictMarkdownHtmlTags.SUPERSCRIPT)
                case DictMarkdown.SUBSCRIPT:
                    html = self.__append_tag(html, DictMarkdown.SUBSCRIPT,
                                             open_marks,
                                             DictMarkdownHtmlTags.SUBSCRIPT)
                case DictMarkdown.SPACED:
                    html = self.__append_tag(html, DictMarkdown.SPACED,
                                             open_marks,
                                             DictMarkdownHtmlTags.SPACED)
                case DictMarkdown.ITALIC:
                    html = self.__append_tag(html, DictMarkdown.ITALIC,
                                             open_marks,
                                             DictMarkdownHtmlTags.ITALIC)
                case DictMarkdown.REF:
                    html = self.__append_tag(html, DictMarkdown.REF,
                                             open_marks,
                                             DictMarkdownHtmlTags.REF)
                case _:
                    html += c
            c = next(collection, None)
        return html

    def __append_tag(self, text: str, mark: str, open_marks: list[str],
                     tag_name: str) -> str:
        """Append the open/closing tag according to mark to the provided text.

        Parameters
        ----------
        text: str, required
            The text to append the tag to.
        mark: str, required
            The dict-markdown mark for which to apend the tag.
        open_marks: list of str, required
            The stack of open marks.
        tag_name: str, required
            The name of the tag to append.

        Returns
        -------
        updated_text: str,
            The text with the proper tag added to it.
        """
        last = open_marks.pop() if len(open_marks) > 0 else None
        if last == mark:
            return text + f'</{tag_name}>'

        if last is not None:
            open_marks.append(last)
        open_marks.append(mark)
        return text + f'<{tag_name}>'

    def __handle_bold(self, dict_markdown: str) -> str:
        """Handle the bold marks in the text.

        Parameters
        ----------
        text: str, required
            The text in dict-markdown format.

        Returns
        -------
        partial_html: str
            The text with the bold marks replaced with proper HTML tag.
        """
        pos = self.__find_bold_marks(dict_markdown)

        is_closing = True
        for idx in reversed(pos):
            tag_name = DictMarkdownHtmlTags.BOLD
            tag = f'</{tag_name}>' if is_closing else f'<{tag_name}>'
            if idx + 2 > len(dict_markdown):
                dict_markdown = f'{dict_markdown[:idx]}{tag}'
            else:
                left, right = dict_markdown[:idx], dict_markdown[idx + 2:]
                dict_markdown = f'{left}{tag}{right}'
            is_closing = not is_closing
        return dict_markdown

    def __find_bold_marks(self, text: str) -> list[int]:
        """Find the bold marks '**' in text, and return positions.

        Parameters
        ----------
        text: str, required
            The text in dict-markdown format.

        Returns
        -------
        pos: list of int
            The positions of bold marks in text.
        """
        pos = []
        idx = text.find(DictMarkdown.BOLD, 0)
        while idx != -1:
            pos.append(idx)
            idx = text.find(DictMarkdown.BOLD, idx + 1)
        return pos


class DictMarkdownHtmlTags:
    """The HTML tags used for dict-markdown."""

    BOLD = 'strong'
    ITALIC = 'em'
    SUBSCRIPT = 'subscript'
    SUPERSCRIPT = 'superscript'
    SPACED = 'code'
    REF = 'cite'


class DictMarkdown:
    """The markup symbols for dict-markdown."""

    BOLD = '**'
    ITALIC = '*'
    SUBSCRIPT = '_'
    SUPERSCRIPT = '^'
    SPACED = '$'
    REF = '@'
