"""Read back the setup/Bazaar patch before supplying older audits a prior view."""
import json,struct
import numpy as np
from sp_disc import ROOT,Disc,SOURCE,EXE,VT1,decode,sha,file_sha,require
from library_text import text

PREVIOUS=ROOT/'work/output/SRW Z Special Disc English v0.2.22.iso'
KVM='KURODATA/KVMDATA.BIN';STAGE='DATA/STAGE.BIN'
PAGES={5:0x28b40,6:0x30d80,10:0x52080}

class PriorComparison:
    def __init__(self,disc,overrides):self.disc=disc;self.overrides=overrides
    def read(self,name):return self.overrides[name] if name in self.overrides else self.disc.read(name)

def pixel_data(b,p):
    v=np.frombuffer(b[p+64:p+32832],np.uint8)
    out=np.empty(65536,np.uint8);out[0::2]=v&15;out[1::2]=v>>4
    return out.reshape(256,256)

def review(component,report,binding):
    folder=ROOT/'work/translation/en';draft=folder/f'{component}_draft.json';check=folder/f'{component}_review.json'
    for key,path in [('bindings_sha256',binding),('draft_sha256',draft),('review_sha256',check)]:
        require(file_sha(path)==report[key],component+' receipt binding')
    d=json.loads(draft.read_text(encoding='utf8'));r=json.loads(check.read_text(encoding='utf8'))
    require(d['bindings_sha256']==file_sha(binding) and r['draft_sha256']==file_sha(draft) and r['verdict']=='pass',component+' meaning review drift')
    return json.loads(binding.read_text(encoding='utf8')),d,r

def audit(disc,exe,report,slogan):
    binding=ROOT/'work/ui/setup-art/native-inventory.json';inv,draft,checked=review('setup_art',report,binding)
    require(checked['entries_examined']==checked['entries_in_slice']==len(inv['entries'])==26 and checked['entries']==draft['entries'],'Setup review coverage')
    prior=Disc(PREVIOUS);oldexe=prior.read(EXE);old=prior.read(KVM);now=disc.read(KVM)
    require(sha(oldexe)==inv['prior_exe_sha256'] and sha(old)==inv['prior_sha256'],'Setup prior identity')
    require(len(now)==len(old) and sha(now)==report['after_sha256'] and sha(old)==report['before_sha256'],'Setup payload identity')
    restored=bytearray(now);mask={p:np.zeros((256,256),bool)for p in PAGES}
    require([r['id']for r in report['tiles']]==[r['id']for r in inv['entries']],'Setup tile inventory')
    for src,row in zip(inv['entries'],report['tiles']):
        require(all(row[k]==v for k,v in src.items()),'Setup tile metadata')
        page=src['page'];x,y,r,b=src['box'];p=PAGES[page];a=pixel_data(now,p)
        require(sha(a[y:b,x:r].tobytes())==row['pixel_sha256'],'Setup final pixel readback')
        if 'english_pixel_sha256'in src:require(row['pixel_sha256']==src['english_pixel_sha256'],'Setup frozen art binding')
        mask[page][y:b,x:r]=True
    for page,p in PAGES.items():
        a=pixel_data(now,p);b=pixel_data(old,p)
        require(np.array_equal(a[~mask[page]],b[~mask[page]]),'Other word pixels changed')
        restored[p+64:p+32832]=old[p+64:p+32832]
    require(restored==old,'Setup changed other textures, headers or palettes')
    expected={}
    for r in inv['entries']:
        if not r['id'].startswith('marquee/'):continue
        x,y,z,b=r['box'];at=0x3a0440+r['record']*14
        expected[at]=struct.pack('<4B3h',x,y,z,b,(z-x)*2//3,16,-1)
    for record in (5,7,8,9):
        at=0x3a0440+record*14;x,y,r,b=struct.unpack_from('<4B',oldexe,at)
        expected[at+4]=struct.pack('<3h',(r-x)*2//3,16,-1)
    for r in inv['code']:
        at=r['va']-0xff680;require(struct.unpack_from('<I',oldexe,at)[0]==r['before'],'Banner native instruction')
        expected[at]=struct.pack('<I',r['after'])
    require(len(expected)==23 and {r['offset'] for r in report['exe_spans']}==set(expected),'Setup allowed executable spans')
    restored_exe=bytearray(exe)
    for at,value in expected.items():
        require(exe[at:at+len(value)]==value,'Banner coordinates/instructions readback')
        restored_exe[at:at+len(value)]=oldexe[at:at+len(value)]
    require(restored_exe==oldexe,'Other executable data/code changed')
    sb,sd,sr=review('bazaar_slogan',slogan,ROOT/'work/ui/setup-art/bazaar-slogan-inventory.json')
    require(sr['entries_examined']==sr['entries_in_slice']==1 and sr['text']==slogan['text']==sd['text']==sb['text'],'Slogan review coverage')
    prior_stage=prior.read(STAGE);stage=disc.read(STAGE);restored_stage=bytearray(stage)
    require(sha(prior_stage)==sb['prior_sha256'] and len(stage)==len(prior_stage),'Slogan prior identity')
    require([(r['chunk'],r['offset'])for r in sb['entries']]==[(44,0x1d44),(49,0x2b24),(50,0x1d84)],'Slogan slot identity')
    for r in sb['entries']:
        lo,hi,p=r['start'],r['end'],r['offset'];before=decode(prior_stage[lo:hi])[0];after,used=decode(stage[lo:hi]);restored=bytearray(after)
        require(len(after)==len(before) and not any(stage[lo+used:hi]),'Slogan compression bounds')
        require(before[p:p+128].hex()==r['source_hex'] and text(after[p:p+128].split(b'\0')[0])==sr['text'],'Slogan source/English readback')
        require(not any(after[p+len(sr['text'])+1:p+128]),'Slogan fixed-field padding')
        restored[p:p+128]=before[p:p+128]
        require(restored==before,'Slogan altered dialogue or gameplay')
        restored_stage[lo:hi]=prior_stage[lo:hi]
    require(restored_stage==prior_stage,'Slogan changed other stage records')
    receipt=json.loads(PREVIOUS.with_suffix('.json').read_text())
    for name in set(receipt['members'])|{VT1}:
        if name not in (EXE,KVM,STAGE):require(disc.read(name)==prior.read(name),'Unrelated setup archive changed: '+name)
    from stage_ui_guard import check
    story=check(stage,True,True)
    result=dict(tiles_read_back=26,marquee_sprite_records=12,marquee_code_words=11,bazaar_slogan_fields=3,
        palettes_and_other_pixels_identical=True,all_other_archives_identical_to='0.2.22',story=story,
        runtime='pending by user choice',earlier_audits_use_verified_prior_view=True)
    return result,PriorComparison(disc,{EXE:oldexe,KVM:old,STAGE:prior_stage})
