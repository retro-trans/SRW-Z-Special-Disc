"""Execute generated buffer adapters, including MIPS branch delay slots."""
import struct
import unittest
from battle_buffer import helper_code, ORIGINAL_BUFFERS


def execute(code, argument, pointer, target):
    words = struct.unpack('<%dI' % (len(code)//4), code)
    base = 0x830000; pc = base; pending = None
    regs = [0] + [0x50000000 + i*0x100 for i in range(1, 32)]
    regs[argument] = pointer; regs[6] = 96; initial = regs[:]
    for step in range(30):
        if pc == target: return regs, initial
        if not base <= pc < base+len(code) or pc % 4: raise AssertionError('Escaped helper')
        word = words[(pc-base)//4]; op = word >> 26
        rs = word >> 21 & 31; rt = word >> 16 & 31; imm = word & 65535
        next_pc = pending if pending is not None else pc+4; pending = None
        if word == 0: pass
        elif op == 15: regs[rt] = imm << 16
        elif op == 13: regs[rt] = regs[rs] | imm
        elif op == 4:
            signed = imm-65536 if imm & 32768 else imm
            pending = pc+4+4*signed if regs[rs] == regs[rt] else pc+8
        elif op == 2: pending = (pc+4 & 0xf0000000) | (word & 0x3ffffff) << 2
        else: raise AssertionError('Unexpected instruction or memory access')
        regs[0] = 0; pc = next_pc
    raise AssertionError('Helper did not tail call')


class BattleBufferTest(unittest.TestCase):
    def test_both_objects_and_unknown_addresses_preserve_call_contract(self):
        for buffers in ((0x838000, 0x8380a0), (0x83fff0, 0x840090)):
            for argument, target, capacity in ((4, 0x2f1760, None), (5, 0x2fd9a0, None), (4, 0x1a23d8, 160)):
                code = helper_code(argument, buffers, target, capacity)
                for pointer in (*ORIGINAL_BUFFERS, 0, 0x6899c7, 0x6899c9, 0x68ab19, 0x900000):
                    regs, before = execute(code, argument, pointer, target)
                    known = pointer in ORIGINAL_BUFFERS
                    self.assertEqual(regs[argument], buffers[ORIGINAL_BUFFERS.index(pointer)] if known else pointer)
                    self.assertEqual(regs[6], capacity if known and capacity is not None else before[6])
                    for reg in range(32):
                        if reg not in (argument, 25, 6): self.assertEqual(regs[reg], before[reg])

    def test_large_capacity_has_no_16bit_truncation(self):
        code = helper_code(4, (0x900000, 0xa00000), 0x1a23d8, 0x18000)
        regs, _ = execute(code, 4, ORIGINAL_BUFFERS[1], 0x1a23d8)
        self.assertEqual(regs[6], 0x18000)


if __name__ == '__main__': unittest.main()
