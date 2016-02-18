# vim: set encoding=utf-8
import os
import re
from unittest import TestCase

from click.testing import CliRunner
from mock import Mock, patch

from regparser.index import xml_sync
from regparser.history import annual
from tests.http_mixin import HttpMixin


class HistoryAnnualVolumeTests(HttpMixin, TestCase):
    def test_init(self):
        uri = re.compile(r'.*gpo.gov.*1010.*12.*4.*xml')
        self.expect_xml_http(uri=uri)
        volume = annual.Volume(1010, 12, 4)
        self.assertEqual(True, volume.exists)

        self.expect_xml_http(status=404, uri=uri)
        volume = annual.Volume(1010, 12, 4)
        self.assertEqual(False, volume.exists)

    def test_should_contain1(self):
        self.expect_xml_http("""
        <CFRDOC>
            <AMDDATE>Jan 1, 2001</AMDDATE>
            <PARTS>Part 111 to 222</PARTS>
        </CFRDOC>""")

        volume = annual.Volume(2001, 12, 2)
        self.assertFalse(volume.should_contain(1))
        self.assertFalse(volume.should_contain(100))
        self.assertFalse(volume.should_contain(300))
        self.assertFalse(volume.should_contain(250))
        self.assertTrue(volume.should_contain(111))
        self.assertTrue(volume.should_contain(211))
        self.assertTrue(volume.should_contain(222))

        self.expect_xml_http("""
        <CFRDOC>
            <AMDDATE>Jan 1, 2001</AMDDATE>
            <PARTS>Parts 587 to End</PARTS>
        </CFRDOC>""")

        volume = annual.Volume(2001, 12, 2)
        self.assertFalse(volume.should_contain(111))
        self.assertFalse(volume.should_contain(586))
        self.assertTrue(volume.should_contain(587))
        self.assertTrue(volume.should_contain(600))
        self.assertTrue(volume.should_contain(999999))

    def test_should_contain2(self):
        pt111 = """
        <PART>
            <EAR>Pt. 111</EAR>
            <HD SOURCE="HED">PART 111-Something</HD>
            <FIELD>111 Content</FIELD>
        </PART>"""
        pt112 = """
        <PART>
            <EAR>Pt. 112</EAR>
            <HD SOURCE="HED">PART 112-Something</HD>
            <FIELD>112 Content</FIELD>
        </PART>"""

        self.expect_xml_http(pt111, uri=re.compile(r".*part111\.xml"))
        self.expect_xml_http(pt112, uri=re.compile(r".*part112\.xml"))
        self.expect_xml_http(status=404, uri=re.compile(r".*part113\.xml"))
        self.expect_xml_http("""
        <CFRDOC>
            <AMDDATE>Jan 1, 2001</AMDDATE>
            <PARTS>Part 111 to 222</PARTS>
            %s
            %s
        </CFRDOC>""" % (pt111, pt112), uri=re.compile(r".*bulkdata.*"))

        volume = annual.Volume(2001, 12, 2)

        xml = volume.find_part_xml(111)
        self.assertEqual(len(xml.xpath('./EAR')), 1)
        self.assertEqual(xml.xpath('./EAR')[0].text, 'Pt. 111')
        self.assertEqual(len(xml.xpath('./FIELD')), 1)
        self.assertEqual(xml.xpath('./FIELD')[0].text, '111 Content')

        xml = volume.find_part_xml(112)
        self.assertEqual(len(xml.xpath('./EAR')), 1)
        self.assertEqual(xml.xpath('./EAR')[0].text, 'Pt. 112')
        self.assertEqual(len(xml.xpath('./FIELD')), 1)
        self.assertEqual(xml.xpath('./FIELD')[0].text, '112 Content')

        self.assertEqual(volume.find_part_xml(113), None)

    def test_should_contain_with_single_part(self):
        self.expect_xml_http("""
        <CFRDOC>
            <AMDDATE>Jan 1, 2001</AMDDATE>
            <PARTS>Part 641 (§§ 641.1 to 641.599)</PARTS>
        </CFRDOC>""")

        volume = annual.Volume(2001, 12, 2)
        self.assertFalse(volume.should_contain(640))
        self.assertTrue(volume.should_contain(641))
        self.assertFalse(volume.should_contain(642))

    def test_should_contain__empty_volume(self):
        """If the first volume does not contain a PARTS tag, we should assume
        that it covers all of the regs in this title"""
        self.expect_xml_http("""
        <CFRDOC>
            <SOMETHINGELSE>Here</SOMETHINGELSE>
        </CFRDOC>
        """, uri=re.compile(r".*bulkdata.*"))

        volume = annual.Volume(2001, 12, 1)
        self.assertTrue(volume.should_contain(1))
        self.assertTrue(volume.should_contain(10))
        self.assertTrue(volume.should_contain(100))
        self.assertTrue(volume.should_contain(1000))

    def test_find_part_local(self):
        """Verify that a local copy of the annual edition content is
        checked"""
        with CliRunner().isolated_filesystem():
            path = os.path.join(xml_sync.GIT_DIR, 'annual')
            os.makedirs(path)
            path = os.path.join(path, 'CFR-2020-title11-vol12-part13.xml')
            with open(path, 'w') as f:
                f.write('<ROOT><CHILD>content</CHILD></ROOT>')

            xml = annual.Volume(2020, 11, 12).find_part_xml(13)
            self.assertEqual(xml.xpath('./CHILD')[0].text,
                             'content')


class HistoryAnnualTests(TestCase):
    def test_annual_edition_for(self):
        for title in range(1, 17):
            notice = {'effective_on': '2000-01-01'}
            self.assertEqual(annual.annual_edition_for(title, notice), 2000)

            notice = {'effective_on': '2000-01-02'}
            self.assertEqual(annual.annual_edition_for(title, notice), 2001)
        for title in range(17, 28):
            notice = {'effective_on': '2000-01-01'}
            self.assertEqual(annual.annual_edition_for(title, notice), 2000)

            notice = {'effective_on': '2000-04-01'}
            self.assertEqual(annual.annual_edition_for(title, notice), 2000)

            notice = {'effective_on': '2000-04-02'}
            self.assertEqual(annual.annual_edition_for(title, notice), 2001)
        for title in range(28, 42):
            notice = {'effective_on': '2000-01-01'}
            self.assertEqual(annual.annual_edition_for(title, notice), 2000)

            notice = {'effective_on': '2000-07-01'}
            self.assertEqual(annual.annual_edition_for(title, notice), 2000)

            notice = {'effective_on': '2000-07-02'}
            self.assertEqual(annual.annual_edition_for(title, notice), 2001)
        for title in range(42, 100):
            notice = {'effective_on': '2000-01-01'}
            self.assertEqual(annual.annual_edition_for(title, notice), 2000)

            notice = {'effective_on': '2000-10-01'}
            self.assertEqual(annual.annual_edition_for(title, notice), 2000)

            notice = {'effective_on': '2000-10-02'}
            self.assertEqual(annual.annual_edition_for(title, notice), 2001)

    @patch('regparser.history.annual.Volume')
    def test_find_volume(self, Volume):
        v1 = Mock()
        v1.exists = True
        v1.should_contain.return_value = False

        v2 = Mock()
        v2.exists = True
        v2.should_contain.return_value = True

        v3 = Mock()
        v3.exists = False

        def side_effect(year, title, vol_num):
            if vol_num > 3:
                return v2
            return v1
        Volume.side_effect = side_effect

        self.assertEqual(annual.find_volume(2000, 11, 3), v2)

        def side_effect(year, title, vol_num):
            if vol_num > 3:
                return v3
            return v1
        Volume.side_effect = side_effect
        self.assertEqual(annual.find_volume(2000, 11, 3), None)
