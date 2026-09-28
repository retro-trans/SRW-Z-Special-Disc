"""Validate the actual mission prompt, then expose verified prior comparison bytes."""
import json,struct
from sp_disc import ROOT,Disc,EXE,VT1,decode,sha,file_sha,require
from library_text import CHARS,text
from inspect_english_runtime import CAVE
from port_menu_runtime import NEW_FILE

PREVIOUS=ROOT/'work/output/SRW Z Special Disc English v0.2.21.iso'
MEMBER='DATA/COMPDATA.BN'


class PriorComparison:
    """Only the two independently validated prompt changes are reversed.

    Older component audits compare entire archives/executables to historical
    builds. They receive this view only after final-disc prompt verification.
    All unrelated members are read directly from the new disc.
    """
    def __init__(self,disc,exe,comp):
        self.disc=disc;self.exe=exe;self.comp=comp

    def read(self,name):
        if name==EXE:return self.exe
        if name==MEMBER:return self.comp
        return self.disc.read(name)


def check(exe,comp,previous_exe,previous_comp):
    raw=decode(comp)[0];old=decode(previous_comp)[0]
    require(len(raw)==len(old)==652800,'Mission prompt overlay size changed')
    expected=b'Attempt this mission?'+bytes(11)
    require(raw[0x98270:0x98290]==expected,'Mission prompt text readback')
    require(struct.unpack_from('<I',raw,0x6a2c8)[0]==0x7fd1f0,'Mission prompt selector mismatch')
    require(text(raw[0x98270:0x98290].split(b'\0')[0])=='Attempt this mission?','Prompt encoding')
    restored=bytearray(raw);restored[0x98270:0x98290]=old[0x98270:0x98290]
    require(restored==old,'Other menu data changed with mission prompt')
    # Read final installed font widths rather than trusting the compiler report.
    start=NEW_FILE+0x78b960-CAVE;widths=exe[start:start+69]
    value='Attempt this mission?'
    width=sum(13 if c==' ' else widths[CHARS.index(ord(c))]+1 for c in value)
    require(width==210,'Mission prompt font measurement changed')
    at=0x437038-0xff680;word=struct.unpack_from('<I',exe,at)[0]
    require(word>>16==0x2402,'Mission prompt position instruction')
    relative=struct.unpack('<h',struct.pack('<H',word&65535))[0]
    require(relative==-84-width//2==-189,'Mission prompt centering')
    restored_exe=bytearray(exe)
    require(struct.unpack_from('<I',previous_exe,at)[0]==0x2442ffac,'Mission prompt prior coordinate')
    restored_exe[at:at+4]=previous_exe[at:at+4]
    require(restored_exe==previous_exe,'Other executable bytes changed with mission prompt')
    # Preserve both loads, measurement/draw calls, Yes/No setup, and delay slots.
    require(exe[0x43701c-0xff680:at]==previous_exe[0x43701c-0xff680:at] and
            exe[at+4:0x43707c-0xff680]==previous_exe[at+4:0x43707c-0xff680], 'Prompt caller behavior')
    return dict(questions_read_back=1,shared_by_challenge_briefings=18,text=value,
        width=width,absolute_x=320+relative,center_x=236,question_y=111,
        only_decoded_menu_slot_changed=[0x98270,0x98290],only_exe_word_changed=at,
        pointer_measurement_draw_and_choice_logic_unchanged=True,
        runtime='pending by user choice'),bytes(restored_exe)


def audit(disc,exe,report):
    folder=ROOT/'work/translation/en';binding=ROOT/'work/ui/mission-prompt/native-inventory.json'
    inv=json.loads(binding.read_text(encoding='utf8'))
    review=json.loads((folder/'mission_prompt_review.json').read_text(encoding='utf8'))
    for key,path in [('bindings_sha256',binding),('draft_sha256',folder/'mission_prompt_draft.json'),
                     ('review_sha256',folder/'mission_prompt_review.json')]:
        require(file_sha(path)==report[key],'Mission prompt receipt binding')
    require(review['verdict']=='pass' and review['entries_examined']==review['entries_in_slice']==1 and
            review['text']==report['text']=='Attempt this mission?' and
            review['draft_sha256']==report['draft_sha256'],'Mission prompt meaning review')
    previous=Disc(PREVIOUS);oldexe=previous.read(EXE);oldcomp=previous.read(MEMBER)
    require(sha(oldexe)==inv['prior_exe_sha256'] and sha(oldcomp)==inv['prior_member_sha256'],'Prompt baseline identity')
    comp=disc.read(MEMBER);result,restored=check(exe,comp,oldexe,oldcomp)
    require(sha(decode(comp)[0])==report['decoded_after_sha256'] and
            sha(decode(oldcomp)[0])==report['decoded_before_sha256'],'Prompt decoded receipt hashes')
    receipt=json.loads(PREVIOUS.with_suffix('.json').read_text())
    for name in receipt['members']:
        if name not in (EXE,MEMBER):require(disc.read(name)==previous.read(name),'Unrelated prompt archive edit: '+name)
    require(disc.read(VT1)==previous.read(VT1),'Prompt changed briefing textures')
    result.update(all_other_archives_identical_to='0.2.21',earlier_checks_use_verified_prior_comparison_view=True)
    return result,PriorComparison(disc,restored,oldcomp)
