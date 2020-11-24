from miasm.ir.analysis import ira
from miasm.arch.spacez.sem import ir_spacez
from miasm.expression.expression import *

class ir_a_spacez_base(ir_spacez, ira):

  def __init__(self, loc_db):
    ir_spacez.__init__(self, loc_db)
    self.ret_reg = self.arch.regs.R0

  def call_effects(self, addr, *args):
    call_assignblk = [
            ExprAssign(self.ret_reg, ExprOp('call_func', addr, *args)),
    ]
    return call_assignblk

class ir_a_spacez(ir_a_spacez_base):

  def __init__(self, loc_db):
      ir_a_spacez_base.__init__(self, loc_db)

  def get_out_regs(self, _):
      return set([self.ret_reg, self.sp])