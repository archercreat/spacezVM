from miasm.core.utils import decode_hex, encode_hex
from spacez.arch import mn_spacez

def test():
  unit_tests  = [('CLS', '00')]
  unit_tests += [('STRD R0', '0100')]
  unit_tests += [('STRB R0', '0200')]
  unit_tests += [('STRW R0', '0300')]
  unit_tests += [('LDRD R0', '0400')]
  unit_tests += [('LDRB R0', '0500')]
  unit_tests += [('LDRW R0', '0600')]
  unit_tests += [('MOV 0x68, R0', '076800')]
  unit_tests += [('MOV R1, R0',   '080100')]
  unit_tests += [('ADD R2, R3',   '090203')]
  unit_tests += [('SUB R0, R2',   '0A0002')]
  unit_tests += [('MUL R0, R2',   '0B0002')]
  unit_tests += [('DIV R0, R2',   '0C0002')]
  unit_tests += [('MOD R0, R2',   '0D0002')]
  unit_tests += [('AND R0, R2',   '0E0002')]
  unit_tests += [('OR R0, R2',    '0F0002')]
  unit_tests += [('XOR R0, R2',   '100002')]
  unit_tests += [('JMP 0x69',     '1169')]
  unit_tests += [('JE R0, R1, 0x32', '1200000132')]
  unit_tests += [('JNE R0, R1, 0x32', '1201000132')]
  unit_tests += [('JGE R0, R1, 0x32', '1202000132')]
  unit_tests += [('JL R0, R1, 0x32', '1203000132')]
  unit_tests += [('READ_INPUT 0x20', '1320')]
  unit_tests += [('PRN', '14')]
  unit_tests += [('VMEXIT', '15')]

  for mn_str, mn_hex in unit_tests:
    # print("-" * 49)  # Tests separation
    mn_bin = decode_hex(mn_hex)
    mn = mn_spacez.dis(mn_bin)
    print("dis: %s -> %s" % (mn_hex.ljust(10), str(mn).ljust(20)))
    assert(str(mn) == mn_str)  # disassemble assertion
    




if __name__ == "__main__":
    test()