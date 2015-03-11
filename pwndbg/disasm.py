import gdb
import collections
import pwndbg.color

Instruction = collections.namedtuple('Instruction', ['address', 'length', 'asm'])

def get(address, instructions=1):
    address = int(address)
    raw = gdb.selected_frame().architecture().disassemble(address, address+0xffffffff, instructions)
    retval = []
    for insn in raw:
        retval.append(Instruction(insn['addr'],insn['length'], insn['asm']))
    return retval

def near(address, instructions=1):
    # Find out how far back we can go without having a page fault
    distance = instructions * 8
    for start in range(address-distance, address):
        if pwndbg.memory.peek(start):
            break

    # Disassemble more than we expect to need, move forward until we have
    # enough instructions and we start on the correct spot
    insns = []
    while start < address:
        insns = get(start, instructions)
        last = insns[-1]

        if last.address + last.length == address:
            break

        start += 1

    return insns[-instructions:] + get(address, instructions + 1)



branches = set([
# Unconditional x86 branches
'call', 'callq',
'jmp',
'ret',
# Conditional x86 branches
'ja',  'jna',
'jae', 'jnae',
'jb',  'jnb',
'jbe', 'jnbe',
'jc',  'jnc',
'je',  'jne',
'jg',  'jng',
'jge', 'jnge',
'jl',  'jnl',
'jle', 'jnle',
'jo',  'jno',
'jp',  'jnp',
'jpe', 'jpo',
'js',  'jns',
'jz', 'jnz',
# ARM branches
'b', 'bl', 'bx', 'blx', 'bxj', 'b.w',
'beq', 'beq.w', 'bne', 'bmi', 'bpl', 'blt',
'ble', 'bgt', 'bge', 'bxne',
# MIPS branches
'j', 'jal', 'jr'
# PowerPC has too many, don't care
# http://llvm.org/klaus/llvm/raw/e48e8c7a6069374daee4c9be1e17b8ed31527f5e/test/MC/PowerPC/ppc64-encoding-ext.s
# SPARC
'ba', 'bne', 'be', 'bg', 'ble', 'bge', 'bl', 'bgu', 'bleu',
'jmpl'
])

def color(ins):
    asm = ins.asm
    if asm.split()[0] in branches:
        asm = pwndbg.color.yellow(asm)
        asm += '\n'
    return asm