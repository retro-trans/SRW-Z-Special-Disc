"""Relocate indexed caption strings after a block, retaining its native bytes.

This low-level component does not approve translation or install an ISO. A
caller must also provide the larger display buffer, reviewed layout, updated
SEG table, file-table relocation, and playback verification.
"""
import struct
from sp_disc import require
from battle_format import native_layout,indexed


def relocate(raw,replacements):
    parsed=native_layout(raw);rows=parsed['rows'];count=len(rows)
    require(all(type(i)is int and 0<=i<count for i in replacements),'Unknown caption record')
    if not replacements:return raw
    out=bytearray(raw);seen={}
    # The first appended field must be a C-string boundary even if an opaque
    # native tail happens to end in a nonzero byte.
    if out[-1]:out.append(0)
    for i,value in sorted(replacements.items()):
        require(isinstance(value,bytes) and value and b'\0'not in value,'Invalid relocated caption bytes')
        if value not in seen:
            seen[value]=len(out);out.extend(value+b'\0')
        offset=seen[value]-parsed['pool'];require(0<=offset<2**32,'Caption offset overflow')
        struct.pack_into('<I',out,parsed['index']+8*i+4,offset)
    out.extend(bytes((-len(out))%16))
    actual=indexed(out,parsed['index'],count)
    restored=bytearray(out[:len(raw)])
    for i in replacements:
        at=parsed['index']+8*i+4;restored[at:at+4]=raw[at:at+4]
    require(restored==raw,'Relocation changed bytes outside selected index offsets')
    for old,new in zip(rows,actual):
        require(old['metadata']==new['metadata'],'Voice metadata changed')
        require(new['raw']==replacements.get(old['record'],old['raw']),'Relocated caption readback')
        if old['record']in replacements:require(new['start']>=len(raw),'English overwrote native storage')
    return bytes(out)
