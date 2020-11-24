from miasm.core.asmblock import disasmEngine
from miasm.arch.spacez.arch import mn_spacez


class dis_spacez(disasmEngine):
  """MeP miasm disassembly engine - Big Endian
      Notes:
          - its is mandatory to call the miasm Machine
  """
  def __init__(self, bs=None, **kwargs):
    super(dis_spacez, self).__init__(mn_spacez, None, bs, **kwargs)