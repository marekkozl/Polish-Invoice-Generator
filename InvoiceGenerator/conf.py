import os
import locale
import gettext

PROJECT_ROOT = os.path.dirname(os.path.abspath(os.path.join(__file__)))
APP_NAME = "InvoiceGenerator"

LANGUAGE = 'en'

LOCALE_DIR = os.path.join(PROJECT_ROOT, 'locale')

DEFAULT_LANGUAGES = os.environ.get('LANG', '').split(':')
DEFAULT_LANGUAGES += ['en_US', 'pl_PL']

languages = []
lc, encoding = locale.getdefaultlocale()
if lc:
    languages = [lc]

languages += DEFAULT_LANGUAGES
mo_location = LOCALE_DIR

gettext.install(True, localedir=None, unicode=1)
gettext.find(APP_NAME, mo_location)
gettext.textdomain(APP_NAME)
gettext.bind_textdomain_codeset(APP_NAME, "UTF-8")
try:
    t = gettext.translation(APP_NAME, mo_location, languages=languages, fallback=True)
    _ = lambda message: t.gettext(message).decode('utf8')
except IOError:
    _ = lambda x: x
    print "Fix this!"
except ImportError:
    _ = lambda x: x

FONT_PATH = '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf'
FONT_BOLD_PATH = '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans-Bold.ttf'
