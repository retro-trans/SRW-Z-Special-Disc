"""Read installed squad UI changes and restore only verified spans for older audits."""
import json,struct
import numpy as np
from sp_disc import ROOT,Disc,EXE,VT1,decode,sha,file_sha,require
from library_text import text,CHARS
from port_menu_runtime import NEW_FILE
from inspect_english_runtime import CAVE

PREVIOUS=ROOT/'work/output/SRW Z Special Disc English v0.2.23.iso'
COMP='DATA/COMPDATA.BN';ART='KURODATA/KVMDATA.BIN';PAGE=0x20900

class PriorComparison:
    def __init__(self,disc,overrides):self.disc=disc;self.overrides=overrides
    def read(self,name):return self.overrides.get(name) if name in self.overrides else self.disc.read(name)

def pixels(blob):
    v=np.frombuffer(blob[PAGE+64:PAGE+32832],np.uint8);p=np.empty(65536,np.uint8)
    p[0::2]=v&15;p[1::2]=v>>4
    return p.reshape(256,256)

def audit(disc,exe,report):
    binding=ROOT/'work/ui/squad-followup/native-inventory.json'
    draft=ROOT/'work/translation/en/squad_followup_draft.json';review=ROOT/'work/translation/en/squad_followup_review.json'
    for name,path in [('bindings_sha256',binding),('draft_sha256',draft),('review_sha256',review)]:
        require(file_sha(path)==report[name],'Squad report binding drift')
    inv=json.loads(binding.read_text(encoding='utf8'));d=json.loads(draft.read_text(encoding='utf8'));r=json.loads(review.read_text(encoding='utf8'))
    require(d['bindings_sha256']==file_sha(binding) and r['draft_sha256']==file_sha(draft),'Squad meaning review binding')
    require(r['verdict']=='pass' and r['entries_examined']==r['entries_in_slice']==16 and r['entries']==d['entries'],'Squad meaning review coverage')
    require(d['entries']==[dict(id=x['id'],source=x['source'],text=x['text'])for x in inv['entries']],'Squad approved wording')
    old=Disc(PREVIOUS);oe=old.read(EXE);oc=decode(old.read(COMP))[0];ok=old.read(ART)
    co=decode(disc.read(COMP))[0];kvm=disc.read(ART)
    require({n:sha(old.read(n))for n in (EXE,COMP,ART)}==inv['prior_sha256'],'Squad baseline identity')
    require(len(exe)==len(oe) and len(co)==len(oc) and len(kvm)==len(ok),'Squad payload size changed')
    require(report['fields']==[x for x in inv['entries']if x['kind']!='art'] and report['tiles']==[x for x in inv['entries']if x['kind']=='art'],'Squad report coverage')
    re=bytearray(exe);rc=bytearray(co);p=pixels(kvm);op=pixels(ok);mask=np.zeros((256,256),bool)
    widths=exe[NEW_FILE+0x78b960-CAVE:NEW_FILE+0x78b960-CAVE+69]
    measured={}
    for row in inv['entries']:
        if row['kind']=='art':
            x,y,z,b=row['box'];require(sha(p[y:b,x:z].tobytes())==row['after_sha256'],'Squad artwork readback')
            require(sha(op[y:b,x:z].tobytes())==row['before_sha256'],'Squad source tile drift');mask[y:b,x:z]=True;continue
        at=row['offset'];cap=row['capacity'];owner=co if row['kind']=='comp'else exe
        prior=oc if row['kind']=='comp'else oe;restored=rc if row['kind']=='comp'else re
        require(prior[at:at+cap].hex()==row['before_hex'] and owner[at:at+cap].hex()==row['after_hex'],'Squad bounded field readback')
        require(text(owner[at:at+cap].split(b'\0')[0])==row['text'],'Squad English decoding')
        if row['pointer'] is not None:
            require(co[row['pointer']:row['pointer']+4]==oc[row['pointer']:row['pointer']+4],'Squad selector changed')
        measured[row['id']]=sum(13 if c==' 'else widths[CHARS.index(ord(c))]+1 if ord(c)in CHARS else 24 for c in row['text'])
        require(measured[row['id']]==row['width'],'Squad installed font widths')
        restored[at:at+cap]=prior[at:at+cap]
    require(re==oe and rc==oc,'Squad changed unapproved executable/menu bytes')
    require(np.array_equal(p[~mask],op[~mask]),'Squad unrelated pixels changed')
    rk=bytearray(kvm);rk[PAGE+64:PAGE+32832]=ok[PAGE+64:PAGE+32832]
    require(rk==ok,'Squad palette/header/other atlas changed')
    for ident in ('comp/97150','comp/97180','comp/971e0','comp/97210','pool/97000','pool/97080'):
        require(measured[ident]<=430,'Squad line exceeds panel')
    gaps=[182-measured['comp/971b0'],156-measured['pool/97248']]
    require(min(gaps)>=8,'Squad colored overlay overlaps')
    receipt=json.loads(PREVIOUS.with_suffix('.json').read_text())
    for name in set(receipt['members'])|{VT1}:
        if name not in (EXE,COMP,ART):require(disc.read(name)==old.read(name),'Unrelated squad archive changed: '+name)
    result=dict(text_fields_read_back=14,image_tiles_read_back=2,overlay_gaps=gaps,
        other_executable_and_menu_bytes_identical=True,palettes_and_other_pixels_identical=True,
        all_other_archives_identical_to='0.2.23',story_dialogue_unchanged=True,runtime='pending by user choice')
    return result,PriorComparison(disc,{EXE:oe,COMP:old.read(COMP),ART:ok})
