"""Consolidate complete suspend meanings; no runtime patch or layout approval."""
import argparse
import json
from sp_disc import ROOT, sha, require
from suspend_format import native_records, EXE_SHA, TEXT_START, TEXT_END, SCRIPT_START, SCRIPT_END, OUTPUT as CANDIDATES
from battle_terms import canonicalize, PATH as SPELLING
from glossary_terms import PATH as SHARED
from library_text import japanese

BASE = ROOT/'work/translation/en'
OUT = BASE/'suspend_reviewed.json'
SLICES = ((0,80),(80,160),(160,240),(240,296))
TERMS = ROOT/'work/glossary/suspend-terms.json'


def prepare():
    exe, native, scenes = native_records()
    candidate_blob = CANDIDATES.read_bytes()
    candidate = json.loads(candidate_blob)
    expected = dict(source_executable_sha256=EXE_SHA,
        source_text_region_sha256=sha(exe[TEXT_START:TEXT_END]),
        source_script_region_sha256=sha(exe[SCRIPT_START:SCRIPT_END]),
        candidate_input_sha256=sha(candidate_blob))
    require(candidate['source_executable_sha256'] == EXE_SHA
        and candidate['text_region_sha256'] == expected['source_text_region_sha256']
        and candidate['script_region_sha256'] == expected['source_script_region_sha256'], 'Suspend candidate source')
    inputs = {CANDIDATES.name: sha(candidate_blob)}
    entries, changes, notes, coverage = [], [], [], []
    for lo, hi in SLICES:
        stem = f'suspend_{lo:03}_{hi-1:03}'
        paths = [BASE/(stem+suffix+'.json') for suffix in ('','_review')]
        blobs = [p.read_bytes() for p in paths]
        draft, review = map(json.loads, blobs)
        inputs.update({p.name:sha(b) for p,b in zip(paths,blobs)})
        require(review['author_file_sha256'] == sha(blobs[0]), 'Stale suspend author review')
        ids = list(range(lo,hi))
        for obj in (draft, review):
            require(all(obj[k] == v for k,v in expected.items()), 'Suspend source/input bindings')
            require(obj['reviewed_ids'] == ids and obj['rows_in_slice'] == hi-lo, 'Suspend meaning coverage')
        require([r['id'] for r in draft['entries']] == ids, 'Suspend author inventory')
        corrections = {r['id']:r for r in review['corrections']}
        require(len(corrections) == len(review['corrections']) and set(corrections) <= set(ids), 'Suspend correction inventory')
        for row in draft['entries']:
            i = row['id']; source = native[i]
            require(row['source_sha256'] == source['source_sha256'], 'Suspend native row binding')
            require(row.get('source_offset', row.get('offset')) == source['offset'], 'Suspend native coordinate')
            if 'occurrences' in row:
                require(row['occurrences'] == source['occurrences'], 'Suspend occurrence binding')
            value = row['text']
            if i in corrections:
                edit = corrections[i]
                require(edit['source_sha256'] == source['source_sha256'] and edit['before'] == value, 'Suspend review preimage')
                value = edit['text']
            before = value
            value = canonicalize(value, source['text'], literal_breaks=False)
            if before != value:
                changes.append(dict(id=i,before=before,after=value,source_sha256=source['source_sha256']))
            speaker, sep, body = value.partition('\n')
            require(speaker and sep and body.startswith('\u300c') and body.endswith('\u300d'), 'Suspend speaker/quote structure')
            # Native body line breaks are presentation wrapping; the author may
            # draft a complete paragraph before measured English layout. The
            # speaker/body delimiter and quote pair remain structural.
            require('\\n' not in value, 'Suspend literal escaped line break')
            require(not japanese(speaker+body[1:-1]) and '\x00' not in value, 'Non-English suspend draft')
            require(all(ord(c)>=32 or c=='\n' for c in value), 'Unexpected suspend control character')
            entries.append(dict(id=i,offset=source['offset'],address=source['address'],
                source_sha256=source['source_sha256'],occurrences=source['occurrences'],
                speaker=speaker,text=value,meaning_reviewed=True,layout_approved=False,
                notes=row.get('notes',[])))
        notes += [dict(input=paths[1].name,note=n) for n in review.get('uncertainties',[])]
        coverage.append(dict(input=paths[1].name,assigned_records=hi-lo,
            distinct_native_rows_examined=review['distinct_native_rows_examined'],
            native_occurrences_examined=review['native_occurrences_examined'],
            assigned_native_occurrences=review['assigned_native_occurrences']))
    require(len(entries)==296 and sum(len(r['occurrences']) for r in entries)==379, 'Suspend consolidated inventory')
    return dict(schema_version=1,status='Meaning reviewed; full English drafts only. Encoding, relocation and runtime layout remain pending.',
        **expected,review_inputs=inputs,glossary_inputs={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (SHARED,SPELLING,TERMS)},
        reviewed_records=296,reviewed_occurrences=379,scene_count=len(scenes),
        scenes=scenes,entries=entries,name_changes=changes,review_coverage=coverage,review_notes=notes,
        runtime='Pending by user choice; not installed in v0.2.9')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    cfg=prepare()
    print(json.dumps({k:cfg[k] for k in ('status','reviewed_records','reviewed_occurrences','scene_count','name_changes','review_coverage')},indent=2))
    print(json.dumps([cfg['entries'][i] for i in (0,158,239,284,295)],ensure_ascii=True,indent=2))
    if args.write: OUT.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else: print('DRY RUN: no files written')


if __name__=='__main__': main()
