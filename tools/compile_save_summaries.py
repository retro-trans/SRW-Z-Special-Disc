"""Relocate reviewed save/load recaps without changing HSFC or save records."""
import argparse
import json
import struct
from sp_disc import ROOT, Disc, SOURCE, EXE, decode, sha, require
from library_text import text, japanese
from menu_encoding import menu_encode
from glossary_terms import canonicalize, PATH as GLOSSARY_PATH
from reuse_compdata import POOL_BASE
from save_summary_text import wrap, LINE_LIMIT, ROWS

MEMBER='DATA/HSFC.BIN'
SOURCE_SHA='695ccf4e07f6269baa95019d74caa8764a4f12d5a2231144f0f78a2e0c3a851e'
GETTER=0x43cb60
FILE_BASE=0xff680
PREIMAGE=bytes.fromhex('2c00828c3c2c05003f2c05004019050021206500801804002318640040180300211043000800e00320004224')
STRIDES=((0x43cc54,0x24640042,1),(0x43cc78,0x24640084,2))
COUNT=66
CELL_BYTES=256
from review_save_summary_followup import OUT as INPUT, prepare as reviewed_input


def getter_code(table):
    require(table%4==0 and 0<table<0x7fff0000,'Recap table address')
    # Keep the native 16-bit index contract. Invalid values select the empty
    # entry. Both control transfers have explicit delay slots. No stack or
    # callee-saved registers are used; the load in jr's slot returns the record.
    words=[0x30a5ffff,0x2ca30043,0x14600002,0,0x00002821,
           0x00051880,0x3c020000|((table+0x8000)>>16),
           0x24420000|(table&65535),0x00431021,0x03e00008,0x8c420000]
    return struct.pack('<11I',*words)


def build(exe,pool):
    native=Disc(SOURCE).read(EXE);archive=Disc(SOURCE).read(MEMBER)
    raw,_=decode(archive)
    require(sha(raw)==SOURCE_SHA and len(raw)==13312,'Save recap source identity')
    require(not any(raw[0x20:0xe6]),'Save recap empty record')
    cfg=json.loads(INPUT.read_text(encoding='utf-8'))
    require(cfg['source_sha256']==SOURCE_SHA and cfg['reviewed_ids']==list(range(COUNT)),'Save recap review incomplete')
    require(cfg['glossary_sha256']==sha(GLOSSARY_PATH.read_bytes()),'Refresh save recap glossary pass')
    require(cfg==reviewed_input(),'Refresh versioned save recap follow-up')
    for name,digest in cfg['review_inputs'].items():
        require(sha((ROOT/'work/translation/en'/name).read_bytes())==digest,'Stale save recap review '+name)
    require([r['id']for r in cfg['entries']]==list(range(COUNT)),'Save recap inventory')
    out=bytearray(exe);pool=bytearray(pool);pool.extend(bytes((-len(pool))%4))
    table_offset=len(pool);table=POOL_BASE+table_offset;pool.extend(bytes((COUNT+1)*4))
    empty=POOL_BASE+len(pool);pool.extend(bytes(ROWS*CELL_BYTES))
    struct.pack_into('<I',pool,table_offset,empty)
    entries=[];unique={};patches=[];deferred=[]
    for row in cfg['entries']:
        i=row['id'];at=0xe6+i*198;source=raw[at:at+198];digest=sha(source)
        require((row['offset'],row['source_sha256'])==(at,digest),'Save recap source binding '+str(i))
        value=canonicalize(row['text'])
        require(value==row['text'] and not japanese(value),'Save recap glossary gate')
        lines,widths=wrap(value,strict=False);require(lines==row['lines'] and widths==row['line_widths'],'Save recap layout drift')
        require(len(lines)>0,'Missing save recap text')
        record=bytearray()
        approved=row['layout_approved']
        if approved:
            require(row['meaning_reviewed'],'Save recap editorial gate')
            require(len(lines)<=ROWS,'Save recap row overflow')
            cells=[menu_encode(line)for line in lines+['']*(ROWS-len(lines))]
            require([text(cell)for cell in cells]==lines+['']*(ROWS-len(lines)),'Save recap encoding readback')
        else:
            # A failed layout keeps the exact native strings in widened cells.
            # The getter/stride contract is shared by all indices; a native
            # 66-byte record cannot be returned after switching to 256 strides.
            require(i in cfg['deferred_ids'] and row['deferred_reason'],'Untracked recap deferral')
            cells=[]
            for j in range(ROWS):
                cell=source[j*66:(j+1)*66];nul=cell.find(b'\0')
                require(nul>=0 and not any(cell[nul:]),'Native recap cell ownership')
                cells.append(cell[:nul])
            deferred.append(i)
        for encoded in cells:
            require(len(encoded)<CELL_BYTES,'Save recap relocated cell too small')
            record.extend(encoded+bytes(CELL_BYTES-len(encoded)))
        if digest in unique:
            address,previous=unique[digest]
            require(previous==record,'Duplicate native recaps have divergent English')
        else:
            address=POOL_BASE+len(pool);pool.extend(record);unique[digest]=(address,record)
        struct.pack_into('<I',pool,table_offset+4*(i+1),address)
        item=dict(id=i,runtime_index=i+1,offset=at,source_sha256=digest,
            relocated_address=address,translated=approved)
        if approved:item.update(text=value,lines=lines,line_widths=widths)
        else:item['deferred_reason']=row['deferred_reason']
        entries.append(item)
    require(len(unique)==52,'Save recap unique inventory')
    require(deferred==cfg['deferred_ids'] and COUNT-len(deferred)==cfg['translated_records'],'Save recap coverage drift')
    def patch(va,before,after):
        at=va-FILE_BASE
        require(native[at:at+len(before)]==before and out[at:at+len(before)]==before,'Save recap hook preimage '+hex(va))
        require(len(before)==len(after),'Save recap code patch length')
        out[at:at+len(after)]=after
        patches.append(dict(address=va,offset=at,source_hex=before.hex(),payload_hex=after.hex()))
    patch(GETTER,PREIMAGE,getter_code(table))
    for va,before,multiplier in STRIDES:
        patch(va,struct.pack('<I',before),struct.pack('<I',0x24640000|CELL_BYTES*multiplier))
    protected=bytearray(out)
    for p in patches:
        at=p['offset'];data=bytes.fromhex(p['source_hex']);protected[at:at+len(data)]=data
    require(protected==exe,'Unexpected save recap executable mutation')
    return bytes(out),bytes(pool),dict(entries=entries,records=COUNT,unique_records=len(unique),
        translated_records=COUNT-len(deferred),deferred_ids=deferred,
        source_sha256=SOURCE_SHA,source_member_sha256=sha(archive),pointer_table=table,
        empty_record=empty,cell_bytes=CELL_BYTES,record_bytes=ROWS*CELL_BYTES,
        line_limit_font_units=LINE_LIMIT,row_limit=ROWS,patches=patches,
        hsfc_archive_unchanged=True,save_record_format_unchanged=True,runtime='pending by user choice')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    _,_,report=build(Disc(SOURCE).read(EXE),b'')
    print(json.dumps({k:v for k,v in report.items()if k not in ('entries','patches')},indent=2))
    print(json.dumps([r for r in report['entries']if r['id']in (0,38,65)],indent=2))
    if args.write:
        # Addresses depend on the assembled pool prefix; retain only bindings.
        for row in report['entries']:row.pop('relocated_address')
        for key in ('pointer_table','empty_record','patches'):report.pop(key)
        (ROOT/'work/translation/en/save_summaries_bound.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')


if __name__=='__main__':main()
