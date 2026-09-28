"""Check v0.2.13 Library edits against every frozen v0.2.12 field before saving."""
import argparse
import json
import zipfile
from sp_disc import ROOT, sha, require
from complete_library import run, wrap_pixels
from battle_terms import canonicalize
from library_text import records, fields, text
from review_narration import prepare as narration
from reviewed_library_corrections import PATH as REVIEW


def prepare():
    with zipfile.ZipFile(ROOT/'work/output/SRW Z Special Disc English v0.2.12.inputs.zip') as frozen:
        raw = frozen.read('work/translation/en/library_complete.json')
        previous_narration = json.loads(frozen.read('work/translation/en/narration_reviewed.json'))
    review = json.loads(REVIEW.read_text(encoding='utf-8'))
    require(sha(raw) == review['input_sha256'], 'Frozen Library preimage')
    previous = json.loads(raw)
    fresh, overrides = run()
    before = {r['id']: r for r in previous['entries']}
    after = {r['id']: r for r in fresh['entries']}
    require(set(before) == set(after) and len(after) == 4995, 'Library inventory')
    expected = {k: v['text'] for k, v in before.items()}
    for row in review['prose_corrections'] + review['inflected_spelling_approvals']:
        require(expected[row['id']] == row['before'], 'Full-field review preimage')
        expected[row['id']] = row['text']
    blobs = {k: records((ROOT/f'work/cache/library/native/DATA/MTVZKN{k}.BIN').read_bytes())
             for k in ('RT', 'PT', 'KW')}
    changed = []
    for ident, old in before.items():
        native_fields = dict(fields(blobs[old['set']][old['record']])[1])
        native = text(native_fields[old['tag']])
        if old['tag'] in ('DSCR', 'DSC2'):
            native += '\n' + text(native_fields[{'RT': 'RBTN', 'PT': 'CHFN', 'KW': 'WORD'}[old['set']]])
        value = canonicalize(expected[ident], native, literal_breaks=False)
        if old['tag'] in ('DSCR', 'DSC2'):
            value = wrap_pixels(value, old['set'])
        require(value == after[ident]['text'], 'Unapproved Library words/layout: ' + ident)
        if value != old['text']:
            changed.append(dict(id=ident, source_sha256=old['source_sha256'], before=old['text'], text=value))
    require(len(changed) == 16, 'Library change scope')
    narrated = narration()
    old_spelling = previous_narration.pop('spelling_sha256')
    compare = dict(narrated)
    compare.pop('spelling_sha256')
    require(compare == previous_narration, 'Unexpected narration amendment')
    cases = [('Meteor', 'Meteor~ミーティア~', 'Meteor'),
             ('Meteor', 'ミーティア', 'METEOR'), ('Meteorite', 'ミーティア', 'Meteorite'),
             ('Over Freezed', 'オーバーフリーズ', 'Over Freezed'),
             ('Over Freeze Blt', 'オーバーフリーズバレット', 'Overfreeze Blt'),
             ('Gauli Hughes', 'ヒューズ・ガウリ', 'Hughes Gauli'),
             ('Gauli Hughes', 'ガウリ', 'Gauli Hughes')]
    for value, native, wanted in cases:
        require(canonicalize(value, native) == wanted, 'Scoped spelling regression')
    report = dict(version='0.2.13', library_fields_checked=4995, library_changes=changed,
                  narration_text_and_layout_unchanged=True, old_spelling_sha256=old_spelling,
                  spelling_sha256=narrated['spelling_sha256'], spelling_cases_passed=len(cases))
    return fresh, overrides, narrated, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    fresh, overrides, narrated, report = prepare()
    print(json.dumps(report, indent=2))
    if args.write:
        outputs = {'work/translation/en/library_complete.json': fresh,
                   'work/analysis/library-review.json': overrides,
                   'work/translation/en/narration_reviewed.json': narrated,
                   'work/analysis/build-0.2.13-name-pass.json': report}
        for path, value in outputs.items():
            (ROOT/path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    else:
        print('DRY RUN: no data written')


if __name__ == '__main__':
    main()
