# @todo - right now this is a copy-paste from parse_rule_changes. SxS and
# rule changes will develop different data structures, however, so these files
# will diverge soon
from unittest import TestCase

from click.testing import CliRunner
from lxml import etree
from mock import patch

from regparser.commands.fetch_sxs import fetch_sxs
from regparser.index import dependency, entry
from regparser.notice.xml import NoticeXML
from tests.xml_builder import XMLBuilderMixin


class CommandsFetchSxSTests(XMLBuilderMixin, TestCase):
    def setUp(self):
        super(CommandsFetchSxSTests, self).setUp()
        self.cli = CliRunner()
        with self.tree.builder("ROOT") as root:
            root.PRTPAGE(P="1234")
            root.CFR('12 CFR 1000')
        self.notice_xml = NoticeXML(self.tree.render_xml())

    def test_missing_notice(self):
        """If the necessary notice XML is not present, we should expect a
        dependency error"""
        with self.cli.isolated_filesystem():
            result = self.cli.invoke(fetch_sxs, ['1111'])
            self.assertTrue(isinstance(result.exception, dependency.Missing))

    @patch('regparser.commands.fetch_sxs.build_notice')
    @patch('regparser.commands.fetch_sxs.meta_data')
    def test_writes(self, meta_data, build_notice):
        """If the notice XML is present, we write the parsed version to disk,
        even if that version's already present"""
        with self.cli.isolated_filesystem():
            entry.Notice('1111').write(self.notice_xml)
            self.cli.invoke(fetch_sxs, ['1111'])
            meta_data.return_value = {'example': 1}
            self.assertTrue(build_notice.called)
            args, kwargs = build_notice.call_args
            self.assertTrue(args[2], {'example': 1})
            self.assertTrue(
                isinstance(kwargs['xml_to_process'], etree._Element))

            build_notice.reset_mock()
            entry.Entry('rule_changes', '1111').write('content')
            self.cli.invoke(fetch_sxs, ['1111'])
            self.assertTrue(build_notice.called)
