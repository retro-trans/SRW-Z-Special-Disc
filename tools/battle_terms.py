"""Source-scoped caption spelling corrections, after editorial changes."""
import json
import re
from functools import lru_cache
from sp_disc import ROOT
from glossary_terms import canonicalize as shared

PATH = ROOT/'work/glossary/battle-spelling.json'


@lru_cache(None)
def rules():
    return json.loads(PATH.read_text(encoding='utf-8'))['rules']


def canonicalize(value, native, *, literal_breaks=True):
    value = shared(value)
    if literal_breaks: value = value.replace('\\n', '\n')
    # A line break is presentation whitespace and may split a proper name.
    marker = '\\n'
    native = native.replace(marker, '').replace('\n', '').replace('\r', '')
    for rule in rules():
        if not any(term in native for term in rule['native']): continue
        if rule.get('native_pattern') and not re.search(rule['native_pattern'], native): continue
        for old in rule['variants']:
            protected = [match.span() for phrase in rule.get('protected_english', [])
                         for match in re.finditer(r'\s+'.join(map(re.escape, phrase.split())), value, re.I)]
            pattern = r'(?<![A-Za-z])' + r'(?:\s|\\n)+'.join(re.escape(s) for s in old.split()) + r'(?![A-Za-z])'
            matches = list(re.finditer(pattern, value))
            for match in reversed(matches):
                if any(lo < match.end() and match.start() < hi for lo, hi in protected): continue
                value = value[:match.start()] + rule['english'] + value[match.end():]
    return value.replace('\n', '\\n') if literal_breaks else value
