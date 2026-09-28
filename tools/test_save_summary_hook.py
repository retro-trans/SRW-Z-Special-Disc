"""Execute the recap getter's MIPS instructions, including branch delay slots."""
import struct
import unittest
from compile_save_summaries import getter_code, GETTER


def execute(code,table,index):
    words=struct.unpack('<11I',code)
    regs=[0]+[0x50000000+r*0x100 for r in range(1,32)]
    regs[5]=index;initial=regs[:];regs[31]=0x1000
    pc=GETTER;pending=None;reads=[];steps=0
    while pc!=0x1000:
        if not GETTER<=pc<GETTER+len(code) or pc%4:raise AssertionError('Invalid code target')
        word=words[(pc-GETTER)//4];op=word>>26;rs=(word>>21)&31;rt=(word>>16)&31;rd=(word>>11)&31
        imm=word&65535;signed=imm-65536 if imm&32768 else imm
        next_pc=pending if pending is not None else pc+4;pending=None
        if op==12:regs[rt]=regs[rs]&imm
        elif op==11:regs[rt]=int(regs[rs]<(signed&0xffffffff))
        elif op==5:pending=pc+4+signed*4 if regs[rs]!=regs[rt] else pc+8
        elif op==15:regs[rt]=imm<<16
        elif op==9:regs[rt]=(regs[rs]+signed)&0xffffffff
        elif op==35:
            address=(regs[rs]+signed)&0xffffffff;reads.append(address)
            if address%4 or not table<=address<table+67*4:raise AssertionError('Out-of-bounds pointer read')
            regs[rt]=0x900000+(address-table)//4*768
        elif op==0:
            fn=word&63
            if fn==0:regs[rd]=(regs[rt]<<((word>>6)&31))&0xffffffff
            elif fn==33:regs[rd]=(regs[rs]+regs[rt])&0xffffffff
            elif fn==8:pending=regs[rs]
            else:raise AssertionError('Unexpected special instruction')
        else:raise AssertionError('Unexpected instruction or memory write')
        regs[0]=0;pc=next_pc;steps+=1
        if steps>11:raise AssertionError('Getter did not return')
    return regs,initial,reads


class RecapGetterTest(unittest.TestCase):
    def test_every_16bit_index_and_signed_address_carry(self):
        for table in (0x827f20,0x82ff80):
            code=getter_code(table)
            for index in range(65536):
                regs,initial,reads=execute(code,table,index)
                expected=index if index<67 else 0
                self.assertEqual(regs[2],0x900000+expected*768,(table,index))
                self.assertEqual(reads,[table+expected*4])
                # The native getter is leaf code: stack, gp, s0-s7 and fp must
                # survive. We also ensure a0 remains intact in this replacement.
                for r in (4,*range(16,24),28,29,30):self.assertEqual(regs[r],initial[r])
                self.assertEqual(regs[31],0x1000)

    def test_low_halfword_matches_native_index_contract(self):
        table=0x82ff80;code=getter_code(table)
        for high in (0,0xffff,0x1234):
            for low in (0,1,66,67,0x7fff,0x8000,0xffff):
                regs,_,_=execute(code,table,high<<16|low)
                self.assertEqual(regs[2],0x900000+(low if low<67 else 0)*768)


if __name__=='__main__':unittest.main()
