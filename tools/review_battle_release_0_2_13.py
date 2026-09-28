"""Merge reviewed 480-719 captions while preserving the frozen v0.2.12 baseline."""
import argparse
import copy
import json

from sp_disc import ROOT, sha, require
from battle_format import unique_sources
from battle_terms import canonicalize, PATH as SPELLING
from battle_placeholder import verify as verify_placeholder
from review_battle_batch_00480_00719 import prepare as fresh_candidates, BASELINE, BASE_SHA, OUT as CANDIDATES

OUT = ROOT / 'work/translation/en/battle_release_0.2.13.json'
CANDIDATES_SHA = '4b0b1a3be867f0a42b272b27c2e131c89b9b750e94d0ce0c4eec702c31868ed3'


def prepare():
    original = BASELINE.read_bytes()
    require(sha(original) == BASE_SHA, 'Frozen v0.2.12 release changed')
    raw = CANDIDATES.read_bytes()
    require(sha(raw) == CANDIDATES_SHA, 'Frozen reviewed candidate changed')
    saved = json.loads(raw)
    fresh = fresh_candidates()
    # The source-bound spelling file may gain new rules after the meaning pass.
    # Every freshly derived word, source binding and layout must remain identical.
    compare = copy.deepcopy(fresh)
    compare['spelling_sha256'] = saved['spelling_sha256']
    require(compare == saved, 'Candidate meaning/layout changed under current dependencies')
    require(fresh['translated_captions'] == 215 and fresh['translated_records'] == 427
            and fresh['deferred_ids'] == [600] and len(fresh['retained_base_ids']) == 24,
            'New caption coverage changed')
    result = json.loads(original)
    native = unique_sources()
    for row in result['entries']:
        if row['text'] is not None:
            require(canonicalize(row['text'], native[row['id']]['text']) == row['text'],
                    'Unexpected baseline spelling amendment requires separate review')
    old_ids = {r['id'] for r in result['entries']}
    require(not old_ids.intersection(r['id'] for r in fresh['entries']), 'Duplicate new caption')
    result.setdefault('review_history', []).append(dict(
        release='0.2.12', review_inputs=result['review_inputs'],
        baseline_release=result.get('baseline_release'),
        baseline_name_amendments=result.get('baseline_name_amendments', [])))
    result['review_inputs'] = dict(fresh['review_inputs'], **{CANDIDATES.name: CANDIDATES_SHA})
    result['baseline_release'] = dict(file=BASELINE.name, sha256=BASE_SHA)
    result['baseline_name_amendments'] = []
    result['entries'].extend(fresh['entries'])
    result['review_notes'].extend(fresh['review_notes'])
    result['name_changes'].extend(fresh['name_changes'])
    result['runtime_dispositions'] = [verify_placeholder()]
    result.update(spelling_sha256=sha(SPELLING.read_bytes()),
                  candidate_terms_sha256=fresh['candidate_terms_sha256'],
                  candidate_coverage=fresh['slices'], reviewed_captions=len(result['entries']),
                  translated_captions=sum(r['layout_approved'] for r in result['entries']),
                  translated_records=sum(len(r['occurrences']) for r in result['entries'] if r['layout_approved']),
                  deferred_ids=[r['id'] for r in result['entries'] if not r['layout_approved']],
                  reviewed_candidate_sha256=CANDIDATES_SHA,
                  current_candidate_spelling_sha256=fresh['spelling_sha256'],
                  reviewed_candidate_spelling_sha256=saved['spelling_sha256'])
    require(result['reviewed_captions'] == 1681 and result['translated_captions'] == 1678
            and result['translated_records'] == 4323 and result['deferred_ids'] == [323, 444, 600],
            'Merged release inventory')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = prepare()
    print(json.dumps({k: result[k] for k in ('reviewed_captions', 'translated_captions', 'translated_records', 'deferred_ids')}, indent=2))
    print(json.dumps([{k: row[k] for k in ('id', 'text', 'lines', 'line_widths')}
                      for row in result['entries'] if row['id'] in (484, 568, 576, 600, 604, 637, 668, 675, 718)], indent=2))
    if args.write:
        require(not OUT.exists(), 'Refusing to overwrite a versioned release')
        OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    else:
        print('DRY RUN: no files written')


if __name__ == '__main__':
    main()
