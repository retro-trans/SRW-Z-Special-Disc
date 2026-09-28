"""Bind the 110 main-game chart summaries by complete native source strings."""
import argparse
import json
import struct
from collections import defaultdict
from library_text import *
from compile_chart import SOURCE_SHA,BASE,wrap


def prepare():
    native=decode(Disc(SOURCE).read('DATA/STAGE.BIN'))[0]
    original=decode((ORIGINAL/'DATA_STAGE.BIN').read_bytes())[0]
    donor=decode(Disc(DONOR,True).read('DATA/STAGE.BIN'))[0]
    require(sha(native)==SOURCE_SHA,'Special Disc chart identity')
    require(sha(original)=='cadf3047a803c862a5210434179372bab15c08073afbc74401628db8704cba82','Main chart identity')
    require(sha(donor)=='8cdcd8355a1ff4cb89cbbf5f33f92b79dd6325e8f3a9832bb6b738d812574178','English donor chart identity')
    # The donor relocates some English paragraphs. Follow the corresponding
    # pointer-table field, never read English at the Japanese text offset.
    answers=defaultdict(dict);main_base=0x7566f0
    for site in range(0x10dd4,0x10f8c,4):
        old=struct.unpack_from('<I',original,site)[0]-main_base
        new=struct.unpack_from('<I',donor,site)[0]-main_base
        require(0<=old<len(original) and 0<=new<len(donor),'Main donor pointer bounds')
        raw=original[old:original.index(0,old)+1]
        value=' '.join(text(donor[new:donor.index(0,new)]).split())
        require(value and not japanese(value),'Untranslated donor synopsis')
        answers[raw].setdefault(value,[]).append(dict(pointer_site=site,native_offset=old,english_offset=new))
    entries=[]
    for i in range(110):
        site=0x14864+i*4;at=struct.unpack_from('<I',native,site)[0]-BASE
        require(0x7eb0<=at<0x14860,'Main chart source pointer')
        end=native.index(0,at)+1;raw=native[at:end];options=answers[raw]
        refs=[p for p in range(0x3650,len(native)-3,4)if at<=struct.unpack_from('<I',native,p)[0]-BASE<end]
        require([p for p in refs if p>=0x4a60]==[site],'Main chart source has unknown text-region references')
        require(options,'Missing native match '+str(i))
        value,origins=next(iter(options.items()))
        require(value and not japanese(value),'Untranslated donor chart '+str(i))
        # Retain prose in the target; line wrapping is applied after meaning
        # review and glossary corrections by the final compiler.
        value=' '.join(value.split());formatted,widths=wrap(value)
        entries.append(dict(id=i,offset=at,capacity=len(raw),pointer_site=site,
            source_sha256=sha(raw),donor_bindings=origins,text=value,
            alternate_exact_source_translations=[v for v in options if v!=value],
            untyped_word_matches_preserved=[p for p in refs if p!=site],
            initial_line_count=len(widths)))
    return dict(source_sha256=SOURCE_SHA,original_sha256=sha(original),donor_sha256=sha(donor),
        entries=entries,editorial_status='exact-source donor candidates; apply review overrides before build')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    result=prepare()
    print(json.dumps(dict(entries=len(result['entries']),max_lines=max(r['initial_line_count']for r in result['entries']),
        samples=[result['entries'][i]for i in (0,54,109)]),indent=2))
    if args.write:(ROOT/'work/translation/en/chart_main.json').write_text(json.dumps(result,indent=2)+'\n')
    else:print('DRY RUN: no files written')


if __name__=='__main__':main()
