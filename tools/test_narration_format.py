"""Exercise expanded narration lengths, command preservation and corrupt inputs."""
import struct
from narration_format import native_records, parse, replace_text
from sp_disc import require, banlz, decode


def main():
    records=native_records()[-1];expanded=0;rejected=0
    for _,raw,before in records:
        for size in (1,15,16,17,511,1024,2049):
            value=b'A'*size+b'\n'+b'B'*size
            changed=replace_text(raw,value)
            require(parse(changed)['text']==value,'Expanded narration roundtrip')
            require(decode(banlz.compress_record(changed))[0]==changed,'Expanded narration compression')
            require(replace_text(changed,before['text'])==raw,'Expanded narration restoration')
            expanded+=1
        cases=[]
        for offset in (12,16,56,64,before['rawt_offset']+4):
            bad=bytearray(raw);struct.pack_into('<I',bad,offset,0x7fffffff);cases.append(bad)
        cases.extend((raw[:-1],raw+bytes(16)))
        for bad in cases:
            try:parse(bad)
            except ValueError:rejected+=1
            else:raise ValueError('Corrupt narration accepted')
    print('PASS: 10 native identities,',expanded,'expanded compression/restoration cases,',rejected,'corrupt records rejected; no files written')


if __name__=='__main__':main()
