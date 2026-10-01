"""Source-bound translation of the reported Hyakki Soldier caption."""
import json
from sp_disc import ROOT
from demo_battle_captions import build as build_captions, BIN, SEG

INVENTORY=ROOT/'work/translation/en/hyakki_caption.json'

def build(data,seg):
    inventory=json.loads(INVENTORY.read_text(encoding='utf-8'))
    entries=[(e['id'],e['source_sha256'],e['text'],e['speaker']) for e in inventory['entries']]
    result=build_captions(data,seg,caption_entries=entries,
        base_bin_sha=inventory['base_bin_sha256'],base_seg_sha=inventory['base_seg_sha256'])
    from sp_disc import require
    require(result[2]["translated_occurrences"]==6 and len(result[2]["entries"])==1,"Expected six caption occurrences")
    return result
