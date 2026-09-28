"""Bind reviewed location meanings to all native title images; dry-run first."""
import argparse
import json
from sp_disc import ROOT, sha, file_sha, require
from world_map_titles import native, FONT, TARGET, REVIEW, BINDINGS, render


def prepare():
    review=json.loads(REVIEW.read_text(encoding='utf-8'))
    draft=ROOT/review['draft_path']
    require(file_sha(draft)==review['draft_sha256'], 'Location review draft drift')
    require(review['entries_examined']==review['entries_in_scope']==13 and
            review['source_transcription_mismatches']==0, 'Location meaning coverage')
    spellings=json.loads((ROOT/'work/glossary/battle-spelling.json').read_text(encoding='utf-8'))
    # This scoped spelling pass follows the independent meaning corrections.
    require('Domepolis' in json.dumps(spellings), 'Missing locked Domepolis spelling')
    archive,offsets,table,rows=native()
    bindings=dict(schema_version=1,member='MAP/MAPMODEL.BIN',archive_sha256=sha(archive),
                  table_offset=0x3542F0,table_sha256=sha(table),width=512,height=32,
                  storage='linear low nibble first; vertically flipped',
                  entries=[{k:v for k,v in r.items() if k!='raw'} for r in rows])
    binding_bytes=(json.dumps(bindings,indent=2)+'\n').encode('utf-8')
    entries=[];changes=[]
    for row,approved in zip(rows,review['entries']):
        require(row['chunk']==approved['chunk'], 'Location review order')
        value=approved['text'].replace('Dome Polis','Domepolis')
        if value!=approved['text']:
            changes.append(dict(chunk=row['chunk'],before=approved['text'],after=value))
        pixels,layout=render(value)
        entries.append(dict(chunk=row['chunk'],text=value,source_raw_sha256=row['source_raw_sha256'],
                            frozen_raw_sha256=sha(pixels),layout=layout))
    target=dict(schema_version=1,status='reviewed',review_sha256=file_sha(REVIEW),
                bindings_sha256=sha(binding_bytes),font_sha256=file_sha(FONT),
                naming_changes_after_meaning_review=changes,
                do_not_touch=['Domepolis','Katez','Gallia','Ameria','Bellforest','Tresor Institute',
                              'Saint-Germain Castle','Newark Base','McConnell Base'],entries=entries)
    return binding_bytes,target


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true')
    args=parser.parse_args();bindings,target=prepare()
    print(json.dumps(target,indent=2),flush=True)
    if args.write:
        BINDINGS.write_bytes(bindings)
        TARGET.write_text(json.dumps(target,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')


if __name__=='__main__':main()
