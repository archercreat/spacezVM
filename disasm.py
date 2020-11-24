from miasm.analysis.machine import Machine
from miasm.core.locationdb import LocationDB
from miasm.analysis.simplifier import *
from miasm.ir.symbexec import *
from miasm.arch.spacez.regs import regs_init

from miasm.analysis.cst_propag import *

def save_ircfg(ircfg, name: str) -> None:
  import subprocess
  open(name, 'w').write(ircfg.dot())
  subprocess.call(["dot", "-Tpng", name, "-o", "test.png"])
  subprocess.call(["rm", name])

fdesc = open("bytecode", 'rb')
loc_db = LocationDB()

raw = fdesc.read()
# The Container will provide a *bin_stream*, bytes source for the disasm engine
# It will prodive a view from a PE or an ELF.
# cont = Container.from_stream(fdesc, loc_db)

# The Machine, instantiated with the detected architecture, will provide tools
# (disassembler, etc.) to work with this architecture
machine = Machine("spacez")
# code.interact(local=locals())

# Instantiate a disassembler engine, using the previous bin_stream and its
# associated location DB. The assembly listing will use the binary symbols
mdis = machine.dis_engine(raw, loc_db=loc_db)

# Run a recursive traversal disassembling from the entry point
# (do not follow sub functions by default)
addr = 0
asmcfg = mdis.dis_multiblock(addr)

ira = machine.ira(loc_db)

ircfg = ira.new_ircfg_from_asmcfg(asmcfg)
state = regs_init
# propagate_cst_expr(ira, ircfg, 0, state)
# simp  = IRCFGSimplifierCommon(ira)
loc = loc_db.get_offset_location(addr)
# simp.simplify(ircfg, loc)

simp = IRCFGSimplifierSSA(ira)
simp.simplify(ircfg, loc)
# Display each basic blocks
# for block in asmcfg.blocks:
    # print(block)

# Output control flow graph in a dot file
# save_ircfg(asmcfg, "test.dot")
save_ircfg(ircfg, "test2.dot")