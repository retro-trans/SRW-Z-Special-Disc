"""Load source-bound, independently reviewed Library corrections for v0.2.13."""
import json
from sp_disc import ROOT, sha, require

PATH = ROOT / 'work/translation/en/library_review_0.2.13.json'
REVIEW_SHA = 'eb99963f1df35f01ff1c84ce651d3037edfd4500bee67ea2341059712822ad5a'
PHRASES = {
    'PT/280/DSC2': ('of its arms,', "of the Jinba's arms,"),
    'RT/239/DSCR': ('steal the very lives of the ceiling of Yapan.',
                    'steal the very lives of the people of the ceiling of Yapan.'),
    'RT/239/DSC2': ('space, attempted to steal the lives of the leaders\nof Yapan. However, she was stopped by Adette\'s\n',
                    "space, attempted to steal the lives of the people\nof Yapan's Ceiling. However, she was stopped by Adette's\n"),
}


def corrections():
    raw = PATH.read_bytes()
    require(sha(raw) == REVIEW_SHA, 'Library meaning review changed')
    review = json.loads(raw)
    prose = review['prose_corrections']
    inflected = review['inflected_spelling_approvals']
    require({r['id'] for r in prose} == set(PHRASES) and len(prose) == 3,
            'Library prose review inventory')
    require(len(inflected) == 6 and len({r['id'] for r in inflected}) == 6,
            'Library inflection review inventory')
    output = []
    for row in prose + inflected:
        require(row['meaning_reviewed'] is True, 'Library correction not reviewed')
        for key in ('before', 'text'):
            require(sha(row[key].encode('utf-8')) == row[key + '_sha256'],
                    'Library review text hash')
        old, new = (PHRASES[row['id']] if row in prose else
                    (row['replace_from'], row['replace_to']))
        require(row['before'].count(old) == 1 and row['before'].replace(old, new) == row['text'],
                'Library correction changes unapproved words')
        output.append(dict(ids=[row['id']], old=old.strip(), new=new.strip(),
                           source_sha256=row['source_sha256'], reason=row['reason']))
    return output
