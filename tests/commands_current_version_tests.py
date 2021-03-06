from datetime import date
import json
from random import randint
from unittest import TestCase

from click.testing import CliRunner
from mock import patch

from regparser.commands import current_version
from regparser.index import entry


class CommandsCurrentVersionTests(TestCase):
    def setUp(self):
        self.title = randint(1, 999)
        self.part = randint(1, 999)
        self.year = randint(2000, 2020)
        self.version_id = '{}-annual-{}'.format(self.year, self.part)

    def test_process_creation(self):
        """If no tree is present, we should build one"""
        to_patch = 'regparser.commands.current_version.xml_parser'
        with CliRunner().isolated_filesystem(), patch(to_patch) as xml_parser:
            entry.Entry('annual', self.title, self.part, self.year).write(
                '<ROOT />')

            xml_parser.reg_text.build_tree.return_value = {'my': 'tree'}
            current_version.process_if_needed(self.title, self.part, self.year)
            tree = entry.Entry('tree', self.title, self.part,
                               self.version_id).read()
            self.assertEqual(json.loads(tree), {'my': 'tree'})
            notice = entry.SxS(self.version_id).read()
            self.assertEqual(notice['document_number'], self.version_id)
            self.assertEqual(notice['cfr_parts'], [self.part])

    def test_process_no_need_to_create(self):
        """If everything is up to date, we don't need to build new versions"""
        with CliRunner().isolated_filesystem():
            annual = entry.Entry('annual', self.title, self.part, self.year)
            tree = entry.Entry('tree', self.title, self.part, self.version_id)
            annual.write('ANNUAL')
            tree.write('TREE')

            current_version.process_if_needed(self.title, self.part, self.year)

            # didn't change
            self.assertEqual(annual.read(), 'ANNUAL')
            self.assertEqual(tree.read(), 'TREE')

    def test_create_version(self):
        """Creates a version associated with the part and year"""
        with CliRunner().isolated_filesystem():
            current_version.create_version_entry_if_needed(
                self.title, self.part, self.year)
            version = entry.Version(
                self.title, self.part, self.version_id).read()
            self.assertEqual(version.effective, date.today())
            self.assertEqual(version.published, date.today())
