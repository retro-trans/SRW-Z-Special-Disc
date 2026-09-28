"""English menu text with native button/link tokens retained byte-for-byte."""
import re
from library_text import encode

TOKENS=re.compile(r'(<-?\d+>|\[\d+\]|%[-+0#]*\d*(?:\.\d+)?[sdifuxXc])')

def menu_encode(value):
    return b''.join(p.encode('ascii') if TOKENS.fullmatch(p) else encode(p) for p in TOKENS.split(value))
