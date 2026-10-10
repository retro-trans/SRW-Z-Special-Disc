"""Translate the Battle Viewer options/BGM help table without moving strings."""
import json, struct
from sp_disc import ROOT, decode, banlz, require, sha
from reuse_compdata import BBASE
from library_text import text, japanese
from menu_encoding import menu_encode, TOKENS
from save_summary_text import width

MEMBER='DATA/COMPDATA.BN'
SPEC=ROOT/'work/translation/en/public/battle_viewer_help.json'

def build(disc):
    cfg=json.loads(SPEC.read_text(encoding='utf-8'))
    packed=disc.read(MEMBER);raw=decode(packed)[0]
    require(sha(packed)==cfg['source_packed_sha256'] and sha(raw)==cfg['source_decoded_sha256'], 'Battle Viewer base drift')
    out=bytearray(raw);spans=[]
    require(len(cfg['entries'])==12,'Battle Viewer table coverage')
    for r in cfg['entries']:
        at,cap,ptr,value=r['offset'],r['capacity'],r['pointer'],r['text']
        before=raw[at:at+cap];old=text(before.split(b'\0')[0])
        require(sha(before)==r['source_sha256'],'Help field preimage')
        require(struct.unpack_from('<I',raw,ptr)[0]==BBASE+at,'Help pointer binding')
        require(TOKENS.findall(old)==TOKENS.findall(value),'Button/control token drift')
        encoded=menu_encode(value)
        require(len(encoded)==r['encoded_bytes'] and len(encoded)<cap,'Help field overflow')
        measured=width(value.replace('<-1>',''))+(24 if '<-1>' in value else 0)
        require(measured==r['width'] and measured<=cfg['max_width'] and '\n' not in value,'Help bar overflow')
        require(not any(a<at+cap and at<b for a,b in spans),'Overlapping help fields')
        out[at:at+cap]=encoded+bytes(cap-len(encoded));spans.append((at,at+cap))
        require(text(out[at:at+cap].split(b'\0')[0])==value and not japanese(value),'Help readback')
    restored=bytearray(out)
    for lo,hi in spans:restored[lo:hi]=raw[lo:hi]
    require(restored==raw,'Changes outside Battle Viewer help fields')
    new=banlz.compress_record(bytes(out),flags=banlz.parse_header(packed)[1])
    require(decode(new)[0]==out,'Strict COMPDATA compression readback')
    return {MEMBER:new},dict(entries=cfg['entries'],decoded_sha256=sha(out),
        maximum_width=max(r['width'] for r in cfg['entries']),max_lines=1,
        control_tokens_preserved=True,pointers_and_other_decoded_bytes_identical=True,emulator='pending')
