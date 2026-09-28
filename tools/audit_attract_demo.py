"""Independent final-disc preservation and name readback for the attract demo."""
import struct
import numpy as np
from sp_disc import SOURCE, Disc, require, sha, tim2, decode
from library_text import text


def audit(disc, report):
    native=Disc(SOURCE);old=native.read('BTL/OP.BIN');data=disc.read('BTL/OP.BIN')
    require(len(data)==len(old)==798496 and sha(old)==report['source_sha256']
            and sha(data)==report['output_sha256'],'Demo archive identity')
    require(disc.read('BTL/OP.SEG')==native.read('BTL/OP.SEG'),'Demo segment table changed')
    names=report['names'];titles=report['titles'];restored=bytearray(data)
    require(len(names)==61 and len({r['id'] for r in names})==61,'Demo name report inventory')
    comp=decode(disc.read('DATA/COMPDATA.BN'))[0];old_comp=decode(native.read('DATA/COMPDATA.BN'))[0]
    # Independently enumerate typed crew records from the two-level native
    # directory. Names occupy twenty bytes, not the thirty-two-byte stride.
    expected={};seg=struct.unpack('<7I',native.read('BTL/OP.SEG'))
    for bank in range(3):
        h,base,end=seg[bank*2:bank*2+3];count=old[base]
        ptrs=struct.unpack_from('<%dI'%(count+2),old,h+4)
        for scene in range(count):
            start=base+ptrs[scene+1];unit=start+16
            for side in range(2):
                crew=struct.unpack_from('<I',old,unit+20)[0]
                for slot in range(crew):
                    record=unit+32+slot*32;pilot=struct.unpack_from('<I',old,record)[0]
                    expected[f'{bank}/{scene}/{side}/{slot}']=(record+12,pilot)
                unit+=144+crew*32
            require(unit+old[start+2]*16==base+ptrs[scene+2],'Native demo parse boundary')
    require(set(expected)=={r['id'] for r in names},'Demo name coverage')
    for row in names:
        at,pilot=expected[row['id']]
        require((at,pilot,20)==(row['offset'],row['pilot_id'],row['capacity']),'Demo name field coordinates')
        source=old[at:at+20];cell=data[at:at+20];raw=cell.split(b'\0')[0]
        require(sha(source)==row['source_cell_sha256'] and not any(cell[len(raw):]),'Demo name terminator/padding')
        p=0x2b50+pilot*178+2
        require(source.split(b'\0')[0]==old_comp[p:p+21].split(b'\0')[0],'Demo pilot native identity')
        require(text(raw)==row['text']==text(comp[p:p+21].split(b'\0')[0]),'Demo name differs from regular English display')
        restored[at:at+20]=source
    require(len(titles)==20 and {(r['bank'],r['scene']) for r in titles}==
            {(b,s) for b,n in enumerate((7,6,7)) for s in range(n)},'Demo title coverage')
    for b,at in enumerate((64,266288,532160)):
        original=old[at:at+263232];updated=data[at:at+263232];a=tim2(original);z=tim2(updated)
        lo=a['start'];hi=lo+a['image_size'];count=(7,6,7)[b]
        require(updated[:lo]==original[:lo] and updated[hi:]==original[hi:],'Demo TIM2 header/palette changed')
        require(np.array_equal(a['indices'][count*40:],z['indices'][count*40:]),'Unused demo pixels changed')
        for row in (r for r in titles if r['bank']==b):
            y=row['scene']*40;patch=z['indices'][y:y+40]
            require(sha(patch.tobytes())==row['indices_sha256'] and np.any(patch),'Demo title pixels differ from inspected atlas')
            yy,xx=np.nonzero(patch)
            require(row['ink_bounds']==[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'Demo title ink bounds')
            require(xx.min()>0 and xx.max()<511 and yy.min()>0 and yy.max()<39,'Demo title touches cell edge')
        restored[at+lo:at+hi]=original[lo:hi]
    require(restored==old,'Demo numeric fields, crew IDs, commands or opaque bytes changed')
    return dict(names_read_back=61,titles_read_back=20,scenes=20,names_match_regular_battle_display=True,
        all_bytes_outside_names_and_title_pixels_identical=True,unused_title_pixels_identical=True,
        segment_table_and_palettes_identical=True,title_cells_within_bounds=True,runtime='pending by user choice')
