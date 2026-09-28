"""Consolidate the unreleased 480-719 meaning reviews; never alter v0.2.12."""
import argparse
import json
import re

from sp_disc import ROOT, sha, require
from battle_format import BIN_SHA, SEG_SHA, unique_sources
from battle_terms import canonicalize, PATH as SPELLING
from battle_text import layout, width, flatten, LINE_LIMIT, ROWS
from glossary_terms import PATH as GLOSSARY
from library_text import CHARS, japanese

BASE = ROOT / 'work/translation/en'
BASELINE = BASE / 'battle_release_0.2.12.json'
BASE_SHA = 'e20ad0dd4d0a3f5b3f167b10336f3bbe2927ddc782150732edc7aef7c7a8efde'
MANIFEST = BASE / 'battle_reuse.json'
MANIFEST_SHA = '091423d6dbc663aac2f0c4caff74c451b293a7af768c04ae7d4955ed04d91ba3'
TERMS = ROOT / 'work/glossary/battle-candidate-00480-00719-terms.json'
SUPPLEMENT = BASE / 'battle_candidate_layout_00480_00719.json'
OUT = BASE / 'battle_candidates_00480_00719_reviewed.json'
SLICES = ((480, 560), (560, 640), (640, 720))


def read(path):
    raw = path.read_bytes()
    return json.loads(raw), sha(raw)


def batch_names(value, native):
    """Only the researched ability/equipment spellings, after meaning review."""
    value = canonicalize(value, native)
    native = native.replace('\\n', '').replace('\n', '')
    if 'オーバーフリーズ' in native:
        value = re.sub(r'(?<![A-Za-z])Over(?:\s|\\n)+Freeze(?![A-Za-z])', 'Overfreeze', value)
    if 'ミーティア' in native:
        value = re.sub(r'(?<![A-Za-z])Meteor(?![A-Za-z])', 'METEOR', value)
    return value


def prepare():
    sources = unique_sources()
    base, digest = read(BASELINE)
    require(digest == BASE_SHA, 'Frozen v0.2.12 baseline changed')
    require(sha(MANIFEST.read_bytes()) == MANIFEST_SHA, 'Candidate source manifest changed')
    require(base['source_bin_sha256'] == BIN_SHA and base['source_seg_sha256'] == SEG_SHA,
            'Baseline native archive binding')
    prior = {r['id']: r for r in base['entries']}
    require(len(prior) == len(base['entries']) == 1465 and base['translated_captions'] == 1463
            and base['translated_records'] == 3896 and base['deferred_ids'] == [323, 444],
            'Baseline inventory or deferred dispositions changed')
    for i, row in prior.items():
        require(row['source_sha256'] == sources[i]['source_sha256']
                and row['occurrences'] == sources[i]['occurrences'], 'Baseline native identity')
        if i in (323, 444):
            require(row['text'] is None and not row['meaning_reviewed'] and not row['layout_approved']
                    and row['lines'] is None and row['deferred_reason'], 'Baseline deferral changed')
        else:
            require(row['meaning_reviewed'] and row['layout_approved']
                    and row['lines'] == layout(row['text'])
                    and row['line_widths'] == list(map(width, row['lines'])), 'Baseline approval/layout')
    bindings = dict(source_bin_sha256=BIN_SHA, source_seg_sha256=SEG_SHA,
                    source_manifest_sha256=MANIFEST_SHA, base_release_sha256=BASE_SHA)
    inputs = {BASELINE.name: BASE_SHA, MANIFEST.name: MANIFEST_SHA,
              str(TERMS.relative_to(ROOT)): sha(TERMS.read_bytes())}
    pending = []
    retained = []
    notes = []
    coverage = []
    for lo, hi in SLICES:
        suffix = f'{lo:05d}_{hi-1:05d}.json'
        ap = BASE / ('battle_candidate_' + suffix)
        rp = BASE / ('battle_candidate_review_' + suffix)
        author, ah = read(ap)
        review, rh = read(rp)
        inputs.update({ap.name: ah, rp.name: rh})
        ids = list(range(lo, hi))
        occurrences = sum(len(sources[i]['occurrences']) for i in ids)
        for doc in (author, review):
            require(all(doc.get(k) == v for k, v in bindings.items()), 'Stale batch source binding ' + suffix)
            require(doc['reviewed_ids'] == ids and doc['rows_in_slice'] == 80, 'Incomplete batch review ' + suffix)
            require(doc['rows_examined'] >= 80 and doc['occurrences_examined'] >= occurrences,
                    'Insufficient reported source examination ' + suffix)
        require(review['author_file_sha256'] == ah, 'Stale independent author binding ' + suffix)
        require(not review.get('baseline_amendment_proposals', []), 'Unhandled baseline meaning amendment')
        require([r['id'] for r in author['entries']] == ids, 'Author inventory ' + suffix)
        fixes = {r['id']: r for r in review['corrections']}
        unresolved = set(review['unresolved_ids'])
        require(len(fixes) == len(review['corrections']) and set(fixes) <= set(ids), 'Invalid correction IDs')
        require(len(unresolved) == len(review['unresolved_ids']) and unresolved <= set(ids), 'Invalid unresolved IDs')
        for row in author['entries']:
            i = row['id']
            source = sources[i]
            require(row['source_sha256'] == source['source_sha256'], 'Author native identity ' + str(i))
            require(row['retained_from_base'] == (i in prior), 'Author baseline classification ' + str(i))
            value = row['text']
            if i in fixes:
                fix = fixes[i]
                require(fix['source_sha256'] == source['source_sha256'] and fix['before'] == value
                        and fix['reason'], 'Stale correction ' + str(i))
                value = fix['text']
            if i in prior:
                require(value == row['text'] == prior[i]['text'] and i not in unresolved,
                        'Baseline text needs separate reviewed amendment ' + str(i))
                retained.append(i)
                continue
            require((value is None) == (i in unresolved), 'Unexplained or contradictory deferral ' + str(i))
            if value is not None:
                require(isinstance(value, str) and value.strip() and not japanese(value)
                        and all(ord(c) >= 32 for c in value), 'Invalid English ' + str(i))
                require(value.count('\\n') == source['text'].count('\\n'), 'Native draft break count ' + str(i))
            pending.append(dict(id=i, source_sha256=source['source_sha256'],
                                occurrences=source['occurrences'], text=value))
        notes.extend(dict(slice=[lo, hi], stage=stage, note=n)
                     for stage, doc in (('author', author), ('review', review)) for n in doc['uncertainties'])
        coverage.append(dict(start=lo, end=hi, rows=80, native_occurrences=occurrences,
                             author_rows_examined=author['rows_examined'], reviewer_rows_examined=review['rows_examined']))
    supplement, sh = read(SUPPLEMENT)
    require(all(supplement.get(k) == v for k, v in bindings.items()), 'Stale compact-review sources')
    require(supplement['author_file'] == 'battle_candidate_00560_00639.json'
            and supplement['review_file'] == 'battle_candidate_review_00560_00639.json'
            and supplement['author_file_sha256'] == inputs[supplement['author_file']]
            and supplement['review_file_sha256'] == inputs[supplement['review_file']], 'Stale compact-review inputs')
    require(supplement['reviewed_ids'] == [604] and [r['id'] for r in supplement['entries']] == [604],
            'Compact-review inventory')
    edit = supplement['entries'][0]
    target = next(r for r in pending if r['id'] == 604)
    require(edit['source_sha256'] == target['source_sha256'] and edit['before'] == target['text']
            and edit['meaning_reviewed'] is True and edit['reason']
            and supplement['context']['native_occurrences'] == target['occurrences'], 'Compact-review source/preimage')
    require(edit['text'] == "That violates Article 9 of the Citizens' Charter,\\nalso called the Exodus Law!",
            'Unexpected compact wording needs another review')
    target['text'] = edit['text']
    inputs[SUPPLEMENT.name] = sh
    name_changes = []
    for row in pending:
        value = row['text']
        if value is None:
            lines = None
        else:
            changed = batch_names(value, sources[row['id']]['text'])
            if changed != value:
                name_changes.append(dict(id=row['id'], before=value, after=changed))
            value = row['text'] = changed
            lines = layout(value)
            if lines is not None:
                require(flatten(value) == ' '.join(lines)[1:-1], 'Layout changed words')
                require(not (set(''.join(lines)) - set(map(chr, CHARS)) - {' ', '~'}), 'Unsupported caption glyph')
        row.update(review_set='candidate', review_id=row['id'], meaning_reviewed=value is not None,
                   layout_approved=lines is not None, lines=lines, line_widths=list(map(width, lines)) if lines else [],
                   deferred_reason=None if lines else ('Unresolved birth-name spelling; preserve native text' if row['id'] == 600
                       else 'Full meaning exceeds two rows; preserve native text'))
    expected = set(range(480, 720)) - set(prior)
    require({r['id'] for r in pending} == expected and len(pending) == len(expected), 'Consolidated inventory')
    require(len(retained) == 24, 'Retained baseline inventory')
    return dict(schema_version=1, **bindings, review_inputs=inputs, entries=pending, retained_base_ids=retained,
                preserved_baseline_deferred_ids=[323, 444], slices=coverage, review_notes=notes,
                meaning_reviewed=sum(r['meaning_reviewed'] for r in pending),
                translated_captions=sum(r['layout_approved'] for r in pending),
                translated_records=sum(len(r['occurrences']) for r in pending if r['layout_approved']),
                deferred_ids=[r['id'] for r in pending if not r['layout_approved']], name_changes=name_changes,
                layout_amendments=[edit], glossary_sha256=sha(GLOSSARY.read_bytes()), spelling_sha256=sha(SPELLING.read_bytes()),
                candidate_terms_sha256=sha(TERMS.read_bytes()), line_limit=LINE_LIMIT, row_limit=ROWS,
                status='Unreleased reviewed candidates; no ISO changes', runtime='pending by user choice')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = prepare()
    print(json.dumps({k: result[k] for k in ('translated_captions', 'translated_records', 'deferred_ids', 'name_changes', 'slices')}, indent=2))
    print(json.dumps([r for r in result['entries'] if r['id'] in (484, 489, 498, 552, 568, 577, 600, 604, 637, 668, 675, 718)], indent=2))
    if args.write:
        OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    else:
        print('DRY RUN: no files written')


if __name__ == '__main__':
    main()
