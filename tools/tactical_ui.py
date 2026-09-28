"""Repair byte-addressed movement strings and small tactical UI translations."""
import argparse,json,struct
from sp_disc import ROOT,Disc,SOURCE,EXE,sha,file_sha,require
from library_text import text
from prepare_tactical_ui import BINDINGS,DRAFT,PREVIOUS,inventory

REVIEW=ROOT/'work/translation/en/tactical_ui_review.json'

def prepare():
    inv=json.loads(BINDINGS.read_text(encoding='utf8'))
    draft=json.loads(DRAFT.read_text(encoding='utf8'));review=json.loads(REVIEW.read_text(encoding='utf8'))
    require(inv==inventory()[0],'Tactical source inventory drift')
    require(draft['bindings_sha256']==file_sha(BINDINGS) and review['draft_sha256']==file_sha(DRAFT)
            and review['bindings_sha256']==file_sha(BINDINGS),'Tactical review input drift')
    require(review['entries_examined']==review['entries_in_slice']==13,'Incomplete tactical meaning review')
    require([r['id'] for r in review['entries']]==[r['id'] for r in draft['entries']], 'Tactical review coverage')
    for r,s in zip(review['entries'],draft['entries']):
        require(r['verdict']=='pass' and r['text']==s['text'] and r['encoded_hex']==s['encoded_hex'],
                'Unapproved tactical text/encoding')
    return inv,draft['entries']

def compile_component(exe,inv,entries):
    require(len(entries)==13 and [r['id'] for r in entries]==[r['id'] for r in inv['entries']],
            'Tactical field inventory')
    out=bytearray(exe);spans=[];native=Disc(SOURCE).read(EXE)
    for guard in inv['formatter_guards']:
        lo=guard['offset'];hi=lo+guard['size']
        require(sha(exe[lo:hi])==guard['sha256'],'Movement formatter instruction drift')
    for src,row in zip(inv['entries'],entries):
        at=src['offset'];size=src['capacity'];value=bytes.fromhex(row['encoded_hex'])
        require(native[at:at+size].hex()==src['native_hex'],'Native tactical field identity')
        require(exe[at:at+size].hex()==src['prior_hex'],'Tactical field conflicts with earlier component')
        require(b'\0' not in value and len(value)<size and text(value)==row['text'],'Tactical encoding/bounds')
        payload=value+bytes(size-len(value));out[at:at+size]=payload
        spans.append(dict(id=row['id'],offset=at,size=size,before_hex=src['prior_hex'],after_hex=payload.hex(),
                          text=row['text'],role=src['role']))
    # These templates are byte-addressed by the unchanged native formatter.
    template=bytes(out[0x3bfdf0:0x3bfe08]).split(b'\0')[0]
    require(template[:8]==bytes.fromhex('816d81408140815e') and len(template)==16,'Movement prefix geometry')
    require(len(out[0x3bfe10:0x3bfe18].split(b'\0')[0])==6,'Terrain placeholder geometry')
    for off in (0x39d518,0x39d520,0x39d528):
        require(out[off]==0x85 and out[off+2]==0,'Terrain cell must be one two-byte private glyph')
    for row in inv['coordinates']:
        at=row['offset'];old=row['before_word'];new=row['after_word']
        require(struct.unpack_from('<I',exe,at)[0]==old and old>>16==new>>16,'Tactical coordinate opcode drift')
        struct.pack_into('<I',out,at,new)
        spans.append(dict(id=f"coordinate/{row['va']:x}",offset=at,size=4,
                          before_hex=struct.pack('<I',old).hex(),after_hex=struct.pack('<I',new).hex(),note=row['note']))
    restored=bytearray(out)
    for r in spans:restored[r['offset']:r['offset']+r['size']]=bytes.fromhex(r['before_hex'])
    require(restored==exe,'Tactical edit escaped approved spans')
    return bytes(out),dict(fields=13,squad_suffixes=5,terrain_markers=3,movement_fields=4,stat_labels=1,
                          coordinate_words=len(inv['coordinates']),spans=spans,
                          formatter_instructions_unchanged=True,other_exe_bytes_unchanged=True)

def build(exe):
    inv,entries=prepare();out,report=compile_component(exe,inv,entries)
    return out,dict(report,bindings_sha256=file_sha(BINDINGS),draft_sha256=file_sha(DRAFT),review_sha256=file_sha(REVIEW))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.parse_args()
    out,report=build(Disc(PREVIOUS).read(EXE))
    print(json.dumps(report,indent=2));print('DRY RUN: no executable written')

if __name__=='__main__':main()
