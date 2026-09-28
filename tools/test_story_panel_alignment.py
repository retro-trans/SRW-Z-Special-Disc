"""Execute the small alignment helpers in a bounded integer instruction model."""
import struct
import unittest
from align_story_panels import *


class Machine:
    def __init__(self, payload):
        self.mem = {POOL_BASE+i:b for i,b in enumerate(payload)}
        self.r = [0]*32
        self.r[29] = 0x3000000
        self.r[31] = 0xDEADBEEF
        self.calls = []

    def get(self, at, size, signed=False):
        return int.from_bytes(bytes(self.mem.get(at+i,0) for i in range(size)), 'little', signed=signed)

    def put(self, at, value, size):
        for i,b in enumerate((value % (1 << (size*8))).to_bytes(size,'little')):
            self.mem[at+i] = b

    def string(self, at):
        result = bytearray()
        for i in range(256):
            b = self.get(at+i,1)
            if not b: return bytes(result)
            result.append(b)
        raise AssertionError('Unterminated model string')

    def run(self, pc):
        pending = None
        for _ in range(20000):
            if pc == 0xDEADBEEF: return
            if pc == APPEND:
                self.calls.append((pc, self.r[5], self.string(self.r[5]), self.r[6:9].copy()))
                n = self.get(self.r[4]+0x252A,2)
                if 1 <= n <= 16:
                    row = self.r[4]+(n-1)*594
                    count = self.get(row+10,2)
                    if 1 <= count < 8:
                        self.put(row+10,count+1,2)
                        segment = row+12+count*74
                        for i,b in enumerate(self.string(self.r[5])+b'\0'): self.put(segment+i,b,1)
                        self.put(segment+0x42,-75,2)  # native measured append position
                        self.put(segment+0x44,18+(n-1)*12,2)
                        for i,v in enumerate(self.r[6:9]): self.put(segment+0x46+i,v,1)
                pc = self.r[31]; pending = None; continue
            if pc == MEASURE:
                self.calls.append((pc,self.r[4],self.r[5]))
                self.r[2] = 777  # recognizable native fallback result
                pc = self.r[31]; pending = None; continue
            w = self.get(pc,4); op=w>>26; rs=w>>21&31;rt=w>>16&31;rd=w>>11&31
            imm=w&65535; simm=imm if imm<32768 else imm-65536
            nxt=pc+4; jump=None
            if op==0:
                fn=w&63
                if fn==0: self.r[rd]=self.r[rt] << (w>>6&31)
                elif fn in (0x21,0x2D):self.r[rd]=self.r[rs]+self.r[rt]
                elif fn==8:jump=self.r[rs]
                else:raise AssertionError(hex(w))
            elif op in (2,3):
                if op==3:self.r[31]=pc+8
                jump=(w&0x3FFFFFF)<<2
            elif op in (4,5):
                yes=self.r[rs]==self.r[rt]
                if yes == (op==4):jump=pc+4+simm*4
            elif op==9:self.r[rt]=self.r[rs]+simm
            elif op==11:self.r[rt]=int((self.r[rs]&0xFFFFFFFFFFFFFFFF)<(simm&0xFFFFFFFFFFFFFFFF))
            elif op==13:self.r[rt]=self.r[rs]|imm
            elif op==15:self.r[rt]=imm<<16
            elif op in (33,36,30,55):
                size={33:2,36:1,30:16,55:8}[op]
                self.r[rt]=self.get(self.r[rs]+simm,size,signed=op==33)
            elif op in (41,31,63):
                self.put(self.r[rs]+simm,self.r[rt],{41:2,31:16,63:8}[op])
            else:raise AssertionError(hex(w))
            self.r[0]=0
            if pending is not None:nxt=pending
            pending=jump;pc=nxt
        raise AssertionError('Model step bound')


class AlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        native=(ROOT/'work/cache/english-runtime/special.elf').read_bytes()
        _,cls.payload,cls.report=build(native,b'')
        cls.entries={x['kind']:x['address'] for x in cls.report['helpers']}

    def test_center_matches_and_fallback(self):
        for value,mode,expected in [(q,0,-(actual_width(q)//2)) for q in QUESTIONS]+[
                ('Play this episode? Extra',0,777),('Play this episode?',1,777),('',0,777)]:
            with self.subTest(value=value,mode=mode):
                m=Machine(self.payload);at=0x2000000
                for i,b in enumerate(menu_encode(value)+b'\0'):m.put(at+i,b,1)
                m.r[4]=at;m.r[5]=mode;m.run(self.entries['center'])
                self.assertEqual(m.r[2],expected)
                self.assertEqual(m.r[4],at)

    def test_confirmation_and_other_modes(self):
        for mode in (0,1,2,3,4):
            for n in (1,7,16):
                for pointer,value in ((0x4C3990,b'CLEAR!'),(0x4C39B8,b'---')):
                    with self.subTest(mode=mode,row=n,pointer=pointer):
                        m=Machine(self.payload);obj=0x2000000;row=obj+(n-1)*594
                        m.r[4]=obj;m.r[5]=pointer;m.r[6:9]=[23,0,4];m.r[20]=mode
                        old_s0=0x11112222333344445555666677778888;m.r[16]=old_s0
                        m.put(obj+0x252A,n,2);m.put(row+10,1,2)
                        for i,b in enumerate(b'  native\0'):m.put(pointer+i,b,1)
                        m.run(self.entries['status'])
                        self.assertEqual(m.get(row+10,2),2)
                        self.assertEqual(m.get(row+0x98,2,True),STATUS_X if mode==0 else -75)
                        self.assertEqual(m.get(row+0x9A,2),18+(n-1)*12)
                        self.assertEqual([m.get(row+0x9C+i,1) for i in range(3)],[23,0,4])
                        self.assertEqual(m.calls[0][2],value if mode==0 else b'  native')
                        self.assertEqual(m.r[16],old_s0)
                        self.assertEqual(m.r[29],0x3000000)

    def test_no_new_segment_does_not_reposition(self):
        for count in (0,2,7,8):
            m=Machine(self.payload);obj=0x2000000;m.r[4]=obj;m.r[5]=0x4C39B8
            m.put(obj+0x252A,1,2);m.put(obj+10,count,2);m.put(obj+0x98,55,2)
            m.run(self.entries['status'])
            self.assertEqual(m.get(obj+0x98,2),55)

    def test_patch_guards(self):
        native=bytearray((ROOT/'work/cache/english-runtime/special.elf').read_bytes())
        for va in MARGINS+STATUS_CALLS+CENTER_CALLS:
            changed=native.copy();changed[va-BASE]^=1
            with self.subTest(va=va),self.assertRaises(ValueError):build(changed,b'')


if __name__ == '__main__':unittest.main()
