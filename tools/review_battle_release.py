"""Combine independently reviewed caption slices, then spelling and layout."""
import argparse
import json
from sp_disc import ROOT, sha, require
from battle_format import BIN_SHA, SEG_SHA, unique_sources
from battle_terms import canonicalize, PATH as SPELLING
from battle_text import layout, width, flatten, LINE_LIMIT, ROWS
from glossary_terms import PATH as GLOSSARY
from library_text import japanese
from review_battle_new import prepare as new_review

BASE = ROOT/'work/translation/en'
OUT = BASE/'battle_release_0.2.11.json'
SLICES = ((0, 80), (80, 160), (160, 240), (240, 320), (320, 400), (400, 480), (480, 560), (560, 640), (640, 720), (720, 800), (800, 877))


def previous_release():
    native = unique_sources(); fresh = new_review(); entries = []; changes = []; notes = []
    inputs = dict(fresh['review_inputs'])
    inputs['battle_new_sources.json'] = fresh['source_manifest_sha256']
    rows = [dict(r, review_set='new') for r in fresh['entries']]
    queue_path = BASE/'battle_reuse_review_sources.json'; queue_bytes = queue_path.read_bytes()
    queue = json.loads(queue_bytes); digest = sha(queue_bytes); inputs[queue_path.name] = digest
    for lo, hi in SLICES:
        suffix = f'{lo:03d}_{hi-1:03d}.json'
        author_name = 'battle_reuse_'+suffix; review_name = 'battle_reuse_review_'+suffix
        a = (BASE/author_name).read_bytes(); b = (BASE/review_name).read_bytes()
        author = json.loads(a); review = json.loads(b)
        inputs[author_name] = sha(a); inputs[review_name] = sha(b)
        for doc in (author, review):
            require(doc['source_manifest_sha256'] == digest and doc['source_bin_sha256'] == BIN_SHA, 'Stale reuse review')
            require(doc['reviewed_ids'] == list(range(lo, hi)), 'Incomplete reuse slice')
        require(review['author_file_sha256'] == sha(a), 'Stale reuse author review')
        require([r['id'] for r in author['entries']] == list(range(lo, hi)), 'Reuse author inventory')
        fixes = {r['id']: r for r in review['corrections']}
        require(len(fixes) == len(review['corrections']) and set(fixes) <= set(range(lo, hi)), 'Invalid reuse correction inventory')
        notes.extend(review['uncertainties'])
        for row in author['entries']:
            i = row['id']; bound = queue['entries'][i]; source = native[bound['source_id']]
            require(row['source_id'] == source['id'] and row['source_sha256'] == source['source_sha256'], 'Reuse source binding')
            fixed = fixes.get(i, row)
            require(fixed['source_id'] == source['id'] and fixed['source_sha256'] == source['source_sha256'], 'Correction source binding')
            value = fixed['text']
            require(value.count('\\n') == source['text'].count('\\n'), 'Meaning edit changed source line breaks')
            rows.append(dict(id=i, review_set='reuse', source_id=source['id'], source_sha256=source['source_sha256'],
                text=value, meaning_reviewed=True, occurrences=source['occurrences']))
    extra_path = BASE/'battle_layout_review.json'; extra_raw = extra_path.read_bytes()
    extra = json.loads(extra_raw); inputs[extra_path.name] = sha(extra_raw)
    require(extra['source_bin_sha256'] == BIN_SHA, 'Stale caption layout review')
    supplements = {r['id']: r for r in extra['entries']}
    require(len(supplements) == len(extra['entries']), 'Duplicate caption layout review')
    seen = set()
    for row in rows:
        source = native[row['source_id']]; before = row['text']
        if source['id'] in supplements:
            edit = supplements[source['id']]
            require(edit['source_sha256'] == source['source_sha256'] and edit['before'] == before
                    and edit['meaning_reviewed'], 'Stale caption follow-up review')
            before = edit['text']
        value = canonicalize(before, source['text'])
        require(source['id'] not in seen, 'Duplicate release caption'); seen.add(source['id'])
        require(value and not japanese(value) and all(ord(c) >= 32 for c in value), 'Invalid English caption')
        if before != value: changes.append(dict(review_set=row['review_set'], id=row['id'], before=before, after=value))
        lines = layout(value); approved = lines is not None
        if approved: require(flatten(value) == ' '.join(lines)[1:-1], 'Caption layout changed words')
        entries.append(dict(id=source['id'], review_set=row['review_set'], review_id=row['id'],
            source_sha256=source['source_sha256'], occurrences=source['occurrences'], text=value,
            meaning_reviewed=True, layout_approved=approved, lines=lines, line_widths=list(map(width, lines)) if lines else [],
            deferred_reason=None if approved else 'Full meaning exceeds two rows at 460 font units; retain native caption'))
    require(len(entries) == 1000 and sum(len(r['occurrences']) for r in entries) == 2312, 'Release review coverage')
    require(set(supplements) <= seen, 'Unused caption follow-up review')
    # Three independently reviewed variants of the pictured pre-title attack.
    # Keep the original release inventory intact; never approve the donor queue.
    attack_path = BASE/'battle_screenshot_mazinger_review.json'; attack_raw = attack_path.read_bytes()
    attack = json.loads(attack_raw); inputs[attack_path.name] = sha(attack_raw)
    manifest_path = BASE/'battle_reuse.json'; manifest_raw = manifest_path.read_bytes()
    require(attack['source_bin_sha256'] == BIN_SHA and attack['source_seg_sha256'] == SEG_SHA
            and attack['source_manifest_sha256'] == sha(manifest_raw), 'Stale demo caption review')
    require(attack['reviewed_target_ids'] == [17440,20018,22375]
            and [r['source_id'] for r in attack['entries']] == attack['reviewed_target_ids'], 'Demo caption review inventory')
    require(sha(json.dumps(attack['author_proposals'],sort_keys=True,separators=(',',':')).encode())
            == attack['author_proposals_sha256'], 'Demo caption proposal identity')
    proposals = {r['source_id']:r['text'] for r in attack['author_proposals']}
    inputs[manifest_path.name] = sha(manifest_raw)
    for row in attack['entries']:
        source = native[row['source_id']]
        require(row['source_sha256'] == source['source_sha256'] and row['occurrences'] == source['occurrences']
                and row['before'] == proposals[source['id']] and row['decision'] == 'approved unchanged'
                and row['text'] == row['before'], 'Demo caption source/meaning binding')
        require(source['id'] not in seen, 'Duplicate demo caption'); seen.add(source['id'])
        value = canonicalize(row['text'],source['text']); lines = layout(value)
        require(lines == row['lines'] and list(map(width,lines)) == row['line_widths']
                and flatten(value) == ' '.join(lines)[1:-1], 'Demo caption reviewed layout drift')
        entries.append(dict(id=source['id'], review_set='attract-demo', review_id=source['id'],
            source_sha256=source['source_sha256'],occurrences=source['occurrences'],text=value,
            meaning_reviewed=True,layout_approved=True,lines=lines,line_widths=list(map(width,lines)),deferred_reason=None))
    require(len(entries) == 1003 and sum(len(r['occurrences']) for r in entries) == 2315, 'Demo release coverage')
    notes.extend(attack['uncertainties'])
    return dict(schema_version=1, source_bin_sha256=BIN_SHA, source_seg_sha256=SEG_SHA,
        review_inputs=inputs, glossary_sha256=sha(GLOSSARY.read_bytes()), spelling_sha256=sha(SPELLING.read_bytes()),
        terms_sha256=fresh['terms_sha256'], entries=entries, name_changes=changes,
        reviewed_captions=len(entries), translated_captions=sum(r['layout_approved'] for r in entries),
        translated_records=sum(len(r['occurrences']) for r in entries if r['layout_approved']),
        deferred_ids=[r['id'] for r in entries if not r['layout_approved']],
        line_limit=LINE_LIMIT, row_limit=ROWS, review_notes=fresh['review_notes']+notes,
        runtime='Static layout only; emulator acceptance pending by user choice')


def prepare():
    from review_battle_candidates import prepare as candidate_review, OUTPUT as CANDIDATES, BASELINE
    result = previous_release()
    baseline = json.loads(BASELINE.read_text(encoding='utf-8'))
    require(result['entries'] == baseline['entries'], 'Earlier release entries drifted before explicit amendments')
    candidates = candidate_review()
    require(json.loads(CANDIDATES.read_text(encoding='utf-8')) == candidates, 'Refresh independently reviewed candidates')
    require(not candidates['deferred_ids'], 'Resolve candidate meaning/layout before this release')
    prior = {r['id']:r for r in result['entries']}
    require(not(set(prior) & {r['id'] for r in candidates['entries']}), 'Candidate duplicates earlier release')
    result['review_inputs'].update(candidates['review_inputs'])
    result['review_inputs'][CANDIDATES.name] = sha(CANDIDATES.read_bytes())
    result['entries'].extend(candidates['entries'])
    result['review_notes'].extend(candidates['review_notes'])
    result['name_changes'].extend(candidates['name_changes'])
    # A separately reported meaning defect in an already released caption.
    # The candidate author retains its baseline text; this gate makes the
    # reviewed amendment explicit instead of silently replacing that baseline.
    review_path = BASE/'battle_candidate_review_00160_00239.json'
    review = json.loads(review_path.read_text(encoding='utf-8'))
    fixes = review['baseline_amendment_proposals']
    require(len(fixes) == 1 and fixes[0]['id'] == 169, 'Unexpected baseline amendment inventory')
    fix = fixes[0]; row = prior[169]; source = unique_sources()[169]
    require(fix['source_sha256'] == source['source_sha256'] and fix['before'] == row['text']
            and fix['context']['native_occurrences'] == source['occurrences']
            and fix['proposed'] == 'You ZAFT weaklings! Get lost!' and fix['reason'], 'Stale baseline meaning amendment')
    value = canonicalize(fix['proposed'],source['text']); lines = layout(value)
    require(lines is not None and flatten(value) == ' '.join(lines)[1:-1], 'Baseline amendment layout')
    row.update(text=value,lines=lines,line_widths=list(map(width,lines)))
    result['baseline_amendments'] = [dict(id=169,before=fix['before'],after=value,reason=fix['reason'],
        review_file=review_path.name,review_sha256=sha(review_path.read_bytes()))]
    require(len(result['entries']) == 1232 and len({r['id'] for r in result['entries']}) == 1232,
            'Consecutive candidate release inventory')
    result.update(reviewed_captions=len(result['entries']),
        translated_captions=sum(r['layout_approved'] for r in result['entries']),
        translated_records=sum(len(r['occurrences']) for r in result['entries'] if r['layout_approved']),
        deferred_ids=[r['id'] for r in result['entries'] if not r['layout_approved']],
        candidate_coverage=candidates['slices'])
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--write', action='store_true'); args = p.parse_args()
    result = prepare()
    print(json.dumps({k: result[k] for k in ('reviewed_captions', 'translated_captions', 'translated_records', 'deferred_ids', 'baseline_amendments')}, indent=2))
    print(json.dumps({'new_name_changes':[r for r in result['name_changes'] if 'review_set' not in r],
        'samples':[{k:r[k] for k in ('id','text','lines','line_widths')} for r in result['entries']
                   if r['id'] in (169,182,207,216) or not r['layout_approved']]},indent=2))
    if args.write: OUT.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    else: print('DRY RUN: no files written')


if __name__ == '__main__': main()
