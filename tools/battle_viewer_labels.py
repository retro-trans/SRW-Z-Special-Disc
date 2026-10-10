"""Translate the remaining Battle Viewer sprite labels and HIT abbreviations."""
import json,struct
import numpy as np
from PIL import Image,ImageDraw
from sp_disc import ROOT,EXE,require,sha,file_sha
from episode_titles import unpack,pack
from deployment_ui import FONT,render
from menu_encoding import menu_encode
from library_text import text

ART='KURODATA/KVMDATA.BIN'
SPEC=ROOT/'work/translation/en/public/battle_viewer_labels.json'

def build(disc):
    cfg=json.loads(SPEC.read_text(encoding='utf-8'));raw=disc.read(ART);exe=disc.read(EXE)
    sprites=disc.read(cfg['sprite_member']);page=cfg['page'];start=page+64;end=start+32768
    require(sha(raw)==cfg['art_sha256'] and sha(exe)==cfg['exe_sha256'],'Battle Viewer base drift')
    require(sha(sprites)==cfg['sprite_sha256'] and file_sha(FONT)==cfg['font_sha256'],'Sprite/font identity')
    require(raw[page:page+8]==b'TIM2\x04\0\x01\0' and struct.unpack_from('<HH',raw,page+36)==(256,256),'Word atlas geometry')
    before=unpack(raw[start:end],256,256);after=before.copy();mask=np.zeros(before.shape,bool)
    for r in cfg['icons']:
        x,y,right,bottom=r['box'];rect=np.s_[y:bottom,x:right]
        require(sha(before[rect].tobytes())==r['source_sha256'],'Sprite pixel preimage')
        require(all(sprites[p:p+4]==bytes(r['box']) for p in r['sprite_refs']),'Sprite sampling bounds')
        require(not mask[rect].any(),'Overlapping sprite edits')
        tile,layout=render(r['text'],r['box']);require(layout==r['layout'],'English sprite layout drift')
        after[rect]=tile;mask[rect]=True
    require(np.array_equal(before[~mask],after[~mask]),'Protected atlas pixels changed')
    art=raw[:start]+pack(after)+raw[end:]
    require(np.array_equal(unpack(art[start:end],256,256),after),'Atlas pixel readback')
    out=bytearray(exe);fields=[]
    for r in cfg['fields']:
        at,cap=r['offset'],r['capacity'];old=exe[at:at+cap];encoded=menu_encode(r['text'])
        require(sha(old)==r['source_sha256'] and len(encoded)<cap,'HIT field binding/capacity')
        out[at:at+cap]=encoded+bytes(cap-len(encoded))
        require(text(out[at:at+cap].split(b'\0')[0])==r['text'],'HIT text readback');fields.append(r)
    restored=bytearray(out)
    for r in fields:
        at,cap=r['offset'],r['capacity'];restored[at:at+cap]=exe[at:at+cap]
    require(restored==exe,'Executable change outside HIT label strings')
    dest=ROOT/'work/ui/battle-viewer-labels';dest.mkdir(parents=True,exist_ok=True)
    canvas=Image.new('RGB',(384,220),'#18191d');d=ImageDraw.Draw(canvas)
    for k,r in enumerate(cfg['icons']):
        x,y,right,bottom=r['box'];tile=Image.fromarray(after[y:bottom,x:right]*17).resize(((right-x)*3,(bottom-y)*3),Image.Resampling.NEAREST)
        d.text((8,8+k*65),r['meaning'],fill='white');tile.thumbnail((260,52));canvas.paste(tile,(110,4+k*65))
    d.text((8,200),'HIT: B (Barrier)  P (Pierce)  D (Defend)',fill='#f6ce46')
    canvas.save(dest/'preview-0.3.20.png')
    (dest/'layout.json').write_text(json.dumps(cfg,indent=2)+'\n',encoding='utf-8')
    return {ART:art,EXE:bytes(out)},dict(icons=cfg['icons'],fields=fields,texture_span=[start,end],
        protected_texels_palettes_and_headers_identical=True,sprite_geometry_unchanged=True,
        executable_code_and_other_strings_identical=True,emulator='pending')
