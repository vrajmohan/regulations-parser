from stevedore import extension
from stevedore.exception import NoMatches

OUTPUT_DIR = ''
API_BASE = ''
META = {}

#   All current, US CFR titles
CFR_TITLES = [
    None,
    "General Provisions",
    "Grants and Agreements",
    "The President",
    "Accounts",
    "Administrative Personnel",
    "Domestic Security",
    "Agriculture",
    "Aliens and Nationality",
    "Animals and Animal Products",
    "Energy",
    "Federal Elections",
    "Banks and Banking",
    "Business Credit and Assistance",
    "Aeronautics and Space",
    "Commerce and Foreign Trade",
    "Commercial Practices",
    "Commodity and Securities Exchanges",
    "Conservation of Power and Water Resources",
    "Customs Duties",
    "Employees' Benefits",
    "Food and Drugs",
    "Foreign Relations",
    "Highways",
    "Housing and Urban Development",
    "Indians",
    "Internal Revenue",
    "Alcohol, Tobacco Products and Firearms",
    "Judicial Administration",
    "Labor",
    "Mineral Resources",
    "Money and Finance: Treasury",
    "National Defense",
    "Navigation and Navigable Waters",
    "Education",
    "Panama Canal [Reserved]",
    "Parks, Forests, and Public Property",
    "Patents, Trademarks, and Copyrights",
    "Pensions, Bonuses, and Veterans' Relief",
    "Postal Service",
    "Protection of Environment",
    "Public Contracts and Property Management",
    "Public Health",
    "Public Lands: Interior",
    "Emergency Management and Assistance",
    "Public Welfare",
    "Shipping",
    "Telecommunication",
    "Federal Acquisition Regulations System",
    "Transportation",
    "Wildlife and Fisheries",
]

DEFAULT_IMAGE_URL = (
    'https://s3.amazonaws.com/images.federalregister.gov/' +
    '%s/original.gif')

# list of strings: phrases which shouldn't be broken by definition links
IGNORE_DEFINITIONS_IN = {'ALL': []}

# List of strings: phrases which should be included as definition links
INCLUDE_DEFINITIONS_IN = {'ALL': []}

# list of modules implementing the __contains__ and __getitem__ methods
OVERRIDES_SOURCES = [
    'regcontent.overrides'
]

# list of iterable[(xpath, replacement-xml)] modules, which will be loaded
# in regparser.content.Macros
MACROS_SOURCES = [
    'regcontent.macros'
]

# list of modules implementing the __contains__ and __getitem__ methods
# The key is the notice that needs to be modified; it should point to a dict
# which will get merged with the notice['changes'] dict
REGPATCHES_SOURCES = [
    'regcontent.regpatches'
]

# In some cases, it is beneficial to tweak the XML the Federal Register
# provides. This setting specifies file paths to look through for local
# versions of their XML. See also XML_REPO below, which is effectively tacked
# on to the end of this list
LOCAL_XML_PATHS = []


# Sometimes appendices provide examples or model forms that include
# labels that we would otherwise recognize as structural to the appendix
# text itself. This specifies those labels to ignore by regulation
# number, appendix, and label.
APPENDIX_IGNORE_SUBHEADER_LABEL = {}

# The `pipeline` command pulls in the latest edits to FR notices. This URL
# defines where it should find those edits
XML_REPO = 'https://github.com/eregs/fr-notices.git'

# A dictionary of agency-specific external citations
# @todo - move ATF citations to an extension
CUSTOM_CITATIONS = {
    "ATF I 5300.1": "https://atf-eregs.apps.cloud.gov/static/atf_eregs/5300_1.pdf",
    "ATF I 5300.2": "https://www.atf.gov/file/58806/download"}

PREPROCESSORS = [
    "regparser.tree.xml_parser.preprocessors.MoveLastAMDPar",
    "regparser.tree.xml_parser.preprocessors.SupplementAMDPar",
    "regparser.tree.xml_parser.preprocessors.ParenthesesCleanup",
    "regparser.tree.xml_parser.preprocessors.MoveAdjoiningChars",
    "regparser.tree.xml_parser.preprocessors.ApprovalsFP",
    "regparser.tree.xml_parser.preprocessors.ExtractTags",
    "regparser.tree.xml_parser.preprocessors.Footnotes",
    "regparser.tree.xml_parser.preprocessors.AtfI50032",
    "regparser.tree.xml_parser.preprocessors.AtfI50031",
]

try:
    stevedore_mgr = extension.ExtensionManager(
        namespace="eregs_ns.parser.preprocessors", invoke_on_load=False)
    stevedore_mgr.map(lambda ext: PREPROCESSORS.append(ext.entry_point_target))
except NoMatches:
    pass

try:
    from local_settings import *
except ImportError:
    pass
