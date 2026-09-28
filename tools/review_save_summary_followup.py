"""Merge the independently reviewed recap follow-up into a versioned input."""
import argparse
import copy
import json
from sp_disc import ROOT, sha, require, Disc, SOURCE
from glossary_terms import canonicalize
from save_summary_text import wrap, ROWS
from review_save_summaries import prepare as base_prepare

BASE = ROOT/'work/translation/en'
FILES = ('save_summaries_reviewed.json', 'save_summaries_followup.json',
         'save_summaries_followup_review.json')
OUT = BASE/'save_summaries_release_0.2.9.json'


def prepare():
    blobs = [(BASE/name).read_bytes() for name in FILES]
    hashes = dict(zip(FILES, map(sha, blobs)))
    base, draft, review = map(json.loads, blobs)
    require(base == base_prepare(), 'Refresh original recap review')
    require(review['reviewed_followup_sha256'] == hashes[FILES[1]], 'Stale recap follow-up review')
    for obj in (draft, review):
        require(obj['reviewed_input_sha256'] == hashes[FILES[0]], 'Stale recap base')
        require(obj['source_sha256'] == base['source_sha256'], 'Recap source mismatch')
        require(obj['reviewed_ids'] == list(range(66)), 'Incomplete recap follow-up context')
        require(obj['target_ids'] == base['deferred_ids'], 'Recap follow-up target mismatch')
        require(obj['input_hashes'] == dict(base['review_inputs'], **{FILES[0]: hashes[FILES[0]]}),
                'Recap follow-up input bindings')
        for name, digest in obj['input_hashes'].items():
            require(sha((BASE/name).read_bytes()) == digest, 'Stale recap input '+name)
    require(draft['source_member_sha256'] == review['source_member_sha256'] == sha(Disc(SOURCE).read('DATA/HSFC.BIN')), 'Recap archive binding')
    approved = review['approved_ids_after_corrections']
    require(approved == draft['proposed_ids'], 'Recap approval inventory mismatch')
    require(review['unresolved_ids'] == draft['unresolved_ids'] == [27], 'Recap unresolved inventory')
    require([r['id'] for r in draft['entries']] == draft['target_ids'], 'Recap raw proposal inventory')
    proposals = {r['id']: r for r in draft['entries']}
    require(list(proposals) == draft['target_ids'], 'Recap proposal inventory')
    edits = {r['id']: r for r in review['corrections']}
    require(len(edits) == len(review['corrections']) and set(edits) <= set(approved), 'Recap correction inventory')
    result = copy.deepcopy(base)
    result['review_inputs'].update(hashes)
    for row in result['entries']:
        i = row['id']
        if i not in proposals:
            continue
        proposal = proposals[i]
        require(proposal['source_sha256'] == row['source_sha256'], 'Recap proposal source')
        require(proposal['before'] == row['text'], 'Recap proposal preimage')
        if i not in approved:
            require(proposal['after'] == row['text'], 'Unapproved recap changed')
            continue
        value = proposal['after']
        if i in edits:
            edit = edits[i]
            require(edit['before'] == value and edit['source_sha256'] == row['source_sha256'], 'Recap review preimage')
            value = edit['text']
        value = ' '.join(canonicalize(value).split())
        lines, widths = wrap(value, strict=False)
        require(len(lines) <= ROWS, 'Reviewed recap does not fit')
        row.update(text=value, lines=lines, line_widths=widths, meaning_reviewed=True,
                   layout_approved=True, review_reason=edits[i]['reason'] if i in edits else 'Passed independent follow-up native-source review')
        row.pop('deferred_reason', None)
    result['deferred_ids'] = [r['id'] for r in result['entries'] if not r['layout_approved']]
    result['translated_records'] = 66-len(result['deferred_ids'])
    require(result['translated_records'] == 65 and result['deferred_ids'] == [27], 'Recap follow-up coverage')
    result['review_notes'] += review['uncertainties']
    result['followup_approved_ids'] = approved
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    result = prepare()
    print(json.dumps(dict(translated_records=result['translated_records'], deferred_ids=result['deferred_ids'],
        samples=[{k:r[k] for k in ('id','text','lines','line_widths')} for r in result['entries']
                 if r['id'] in result['followup_approved_ids']]), indent=2))
    if args.write:
        OUT.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    else:
        print('DRY RUN: no files written')


if __name__ == '__main__': main()
