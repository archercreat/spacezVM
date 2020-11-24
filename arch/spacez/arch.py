from miasm.core.cpu import *
from miasm.core.utils import Disasm_Exception
from miasm.expression.expression import ExprId, ExprInt, ExprLoc, \
    ExprMem, ExprOp, is_expr
from miasm.core.asm_ast import AstId, AstMem

from miasm.arch.spacez.regs import *
import miasm.arch.spacez.regs as spacez_regs_module

class instruction_spacez(instruction):
  """Generic Spacez instruction
  Notes:
      - this object is used to build internal miasm instructions based
        on mnemonics
      - it must be implemented !
  """

  # Default delay slot
  # Note:
  #   - mandatory for the miasm Machine
  delayslot = 0

  def __init__(self, name, mode, args, additional_info=None):
    self.name = name
    self.mode = mode
    self.args = args
    self.additional_info = additional_info
    self.offset = None
    self.l = None
    self.b = None


  @staticmethod
  def arg2str(expr, pos=None, loc_db=None):
      """Convert mnemonics arguments into readable strings according to the
      Spacez architecture and their internal types
      Notes:
          - it must be implemented ! However, a simple 'return str(expr)'
            could do the trick.
          - it is used to mimic objdump output
      Args:
          expr: argument as a miasm expression
          pos: position index in the arguments list
      """

      if isinstance(expr, ExprId) or isinstance(expr, ExprInt):
          return str(expr)

      elif isinstance(expr, ExprLoc):
          if loc_db is not None:
              return loc_db.pretty_str(expr.loc_key)
          else:
              return str(expr)
      # Raise an exception if the expression type was not processed
      message = "instruction_spacez.arg2str(): don't know what \
                  to do with a '%s' instance." % type(expr)
      raise Disasm_Exception(message)

  def __str__(self):
    """Return the mnemonic as a string.
    Note:
        - it is not mandatory as the instruction class already implement
          it. It used to get rid of the padding between the opcode and the
          arguments.
        - most of this code is copied from miasm/core/cpu.py
    """

    o = "%s" % self.name

    # if self.name in [
    #   "MOV", "ADD", "SUB", 
    #   "MUL", "DIV", "MOD", 
    #   "AND", "OR", "XOR"]:

    #   if self.args[0].is_int():
    #     o += " %s"  % self.arg2str(self.args[0])
    #     o += ", %s" % hex(int(self.args[1])) 
    #   else:
    #     o += " %s"  % self.arg2str(self.args[0])
    #     o += ", %s" % self.arg2str(self.args[1])

    # elif self.name in ['JNE', 'JE', 'JGE', 'JL']:
    #   o += " %s"  % hex(int(self.args[2]))
    #   o += ", %s" % self.arg2str(self.args[0])
    #   o += ", %s" % self.arg2str(self.args[1])
      
    # else:
    args = []
    if self.args:
        o += " "
    for i, arg in enumerate(self.args):
        if not is_expr(arg):
            raise ValueError('zarb arg type')
        x = self.arg2str(arg, pos=i)
        args.append(x)
    o += self.gen_args(args)
    return o

  def breakflow(self):
    """Instructions that stop a basic block."""
    if self.name in ["VMEXIT", "JE", "JNE", "JGE", "JL", "JMP"]:
      return True
    return False

  def splitflow(self):
    """Instructions that splits a basic block, i.e. the CPU can go somewhere else."""
    if self.name in ["JE", "JNE", "JGE", "JL"]:
      return True
    return False

  def dstflow(self):
    """Instructions that explicitly provide the destination."""
    if self.name in ["JMP", "JE", "JNE", "JGE", "JL"]:
      return True
    return False

  def dstflow2label(self, loc_db):
    """Set the label for the current destination.
        Note: it is used at disassembly"""
    if self.name == 'JMP':
      loc_arg = 0
    elif self.name in ["JE", "JNE", "JGE", "JL"]:
      loc_arg = 2
    else:
      return
    expr = self.args[loc_arg]
    if not expr.is_int():
      return
    addr = int(expr) & int(expr.mask)

    loc_key = loc_db.get_or_create_offset_location(addr)
    self.args[loc_arg] = ExprLoc(loc_key, expr.size)

  def getdstflow(self, loc_db):
    """Get the argument that points to the instruction destination."""
    if self.name == "JMP":
      return [self.args[0]]
    elif self.name in ["JE", "JNE", "JGE", "JL"]:
      return [self.args[2]]
    raise RuntimeError

  def is_subcall(self):
    """Instructions used to call sub functions.
      Spacez Does not have calls.
    """
    return False

class spacez_additional_info(object):
  """Additional Spacez instructions information
  """

  def __init__(self):
    self.except_on_instr = False

class mn_spacez(cls_mn):
  # Define variables that stores information used to disassemble & assemble
  # Notes: - these variables are mandatory
  #        - they could be moved to the cls_mn class

  num = 0  # holds the number of mnemonics

  all_mn = list()  # list of mnenomnics, converted to metamn objects

  all_mn_mode = defaultdict(list) # mneomnics, converted to metamn objects
                                  # Note:
                                  #   - the key is the mode # GV: what is it ?
                                  #   - the data is a list of
                                  #     mnemonics

  all_mn_name = defaultdict(list)    # mnenomnics strings
                                     # Note:
                                     #   - the key is the mnemonic string
                                     #   - the data is the corresponding
                                     #     metamn object

  all_mn_inst = defaultdict(list)    # mnemonics objects
                                     # Note:
                                     #   - the key is the mnemonic Python class
                                     #   - the data is an instantiated
                                     #     object
  bintree = dict()  # Variable storing internal values used to guess a
                      # mnemonic during disassembly

  # Defines the instruction set that will be used
  instruction = instruction_spacez

  # Python module that stores registers information
  regs = spacez_regs_module

  max_instruction_len = 5
  # Default delay slot
  # Note:
  #   - mandatory for the miasm Machine
  delayslot = 0

  # Architecture name
  name = "spacez"

  # PC name depending on architecture attributes (here, l or b)
  # pc = PC

  def additional_info(self):
    """Define instruction side effects # GV: not fully understood yet
    When used, it must return an object that implements specific
    variables, such as except_on_instr.
    Notes:
        - it must be implemented !
        - it could be moved to the cls_mn class
    """

    return spacez_additional_info()

  @classmethod
  def gen_modes(cls, subcls, name, bases, dct, fields):
    """Ease populating internal variables used to disassemble & assemble, such
    as self.all_mn_mode, self.all_mn_name and self.all_mn_inst
    Notes:
        - it must be implemented !
        - it could be moved to the cls_mn class. All miasm architectures
          use the same code
    Args:
        cls: ?
        sublcs:
        name: mnemonic name
        bases: ?
        dct: ?
        fields: ?
    Returns:
        a list of ?
    """

    dct["mode"] = None
    return [(subcls, name, bases, dct, fields)]

  @classmethod
  def getmn(cls, name):
    """Get the mnemonic name
    Notes:
        - it must be implemented !
        - it could be moved to the cls_mn class. Most miasm architectures
          use the same code
    Args:
        cls:  the mnemonic class
        name: the mnemonic string
    """

    return name.upper()

  @classmethod
  def getpc(cls, attrib=None):
    """"Return the ExprId that represents the Program Counter.
    Notes:
        - mandatory for the symbolic execution
        - PC is defined in regs.py
    Args:
        attrib: architecture dependent attributes (here, l or b)
    """

    return PC

  @classmethod
  def getsp(cls, attrib=None):
    """"Return the ExprId that represents the Stack Pointer.
    Notes:
        - mandatory for the symbolic execution
        - SP is defined in regs.py
    Args:
        attrib: architecture dependent attributes (here, l or b)
    """

    return SP

  @classmethod
  def getqp(cls, attrib=None):
    """"Return the ExprId that represents the Queue Pointer.
    Notes:
        - mandatory for the symbolic execution
        - QP is defined in regs.py
    Args:
        attrib: architecture dependent attributes (here, l or b)
    """

    return QP

  @classmethod
  def getbits(cls, bitstream, attrib, start, n):
    """Return an integer of n bits at the 'start' offset
        Note: code from miasm/arch/mips32/arch.py
    """

    # Return zero if zero bits are requested
    if not n:
      return 0
    o = 0  # the returned value
    while n:
      # Get a byte, the offset is adjusted according to the endianness
      offset = start // 8  # the offset in bytes
      # n_offset = cls.endian_offset(attrib, offset)  # the adjusted offset
      c = cls.getbytes(bitstream, offset, 1)
      if not c:
          raise IOError

      # Extract the bits value
      c = ord(c)
      r = 8 - start % 8
      c &= (1 << r) - 1
      l = min(r, n)
      c >>= (r - l)
      o <<= l
      o |= c
      n -= l
      start += l

    return o

  @classmethod
  def endian_offset(cls, attrib, offset):
    if attrib == "b":
      return offset
    else:
      raise NotImplementedError("bad attrib")

  def value(self, mode):
    v = super(mn_spacez, self).value(mode)
    if mode == 'b':
      return [x for x in v]
    else:
      raise NotImplementedError("bad attrib")

def addop(name, fields, args=None, alias=False):
  """
  Dynamically create the "name" object
  Notes:
      - it could be moved to a generic function such as:
        addop(name, fields, cls_mn, args=None, alias=False).
      - most architectures use the same code
  Args:
      name:   the mnemonic name
      fields: used to fill the object.__dict__'fields' attribute # GV: not understood yet
      args:   used to fill the object.__dict__'fields' attribute # GV: not understood yet
      alias:  used to fill the object.__dict__'fields' attribute # GV: not understood yet
  """

  namespace = {"fields": fields, "alias": alias}

  if args is not None:
      namespace["args"] = args

  # Dynamically create the "name" object
  type(name, (mn_spacez,), namespace)

class spacez_arg(m_arg):
  def asm_ast_to_expr(self, arg, loc_db):
    """Convert AST to expressions
        Note: - code inspired by miasm/arch/mips32/arch.py"""

    if isinstance(arg, AstId):
      if isinstance(arg.name, ExprId):
        return arg.name
      if isinstance(arg.name, str) and arg.name in gpr_names:
        return None  # GV: why?
      loc_key = loc_db.get_or_create_name_location(arg.name.encode())
      return ExprLoc(loc_key, 32)

    elif isinstance(arg, AstMem):
      addr = self.asm_ast_to_expr(arg.ptr, loc_db)
      if addr is None:
        return None
      return ExprMem(addr, 32)

    elif isinstance(arg, AstInt):
      return ExprInt(arg.value, 32)

    elif isinstance(arg, AstOp):
      args = [self.asm_ast_to_expr(tmp, loc_db) for tmp in arg.args]
      if None in args:
          return None
      return ExprOp(arg.op, *args)

    # Raise an exception if the argument was not processed
    message = "mep_arg.asm_ast_to_expr(): don't know what \
                to do with a '%s' instance." % type(arg)
    raise Exception(message)

class spacez_reg(reg_noarg, spacez_arg):
  """Generic Spacez register
  Note:
      - the register size will be set using bs()
  """
  reg_info = gpr_infos  # the list of Spacez registers defined in regs.py
  parser = reg_info.parser  # GV: not understood yet

class spacez_imm(imm_noarg, spacez_arg):
  """Generic Spacez immediate
  Note:
      - the immediate size will be set using bs()
  """
  parser = base_expr

reg   = bs(l=8,  cls=(spacez_reg, ))
imm8  = bs(l=8,  cls=(spacez_imm, spacez_arg))

# mnemonics
addop("CLS", [bs("00000000")])
addop("STRD", [bs("00000001"), reg])
addop("STRB", [bs("00000010"), reg])
addop("STRW", [bs("00000011"), reg])
addop("LDRD", [bs("00000100"), reg])
addop("LDRB", [bs("00000101"), reg])
addop("LDRW", [bs("00000110"), reg])
addop("MOV", [bs("00000111"), imm8, reg])
addop("MOV", [bs("00001000"), reg, reg])
addop("ADD", [bs("00001001"), reg, reg])
addop("SUB", [bs("00001010"), reg, reg])
addop("MUL", [bs("00001011"), reg, reg])
addop("DIV", [bs("00001100"), reg, reg])
addop("MOD", [bs("00001101"), reg, reg])
addop("AND", [bs("00001110"), reg, reg])
addop("OR",  [bs("00001111"), reg, reg])
addop("XOR", [bs("00010000"), reg, reg])
addop("JMP", [bs("00010001"), imm8])
addop("JE",  [bs("00010010"), bs("00000000"), reg, reg, imm8])
addop("JNE", [bs("00010010"), bs("00000001"), reg, reg, imm8])
addop("JGE", [bs("00010010"), bs("00000010"), reg, reg, imm8])
addop("JL",  [bs("00010010"), bs("00000011"), reg, reg, imm8])
addop("VMEXIT", [bs("00010101")])
addop("PRN", [bs("00010100")])
addop("READ_INPUT", [bs("00010011"), imm8])