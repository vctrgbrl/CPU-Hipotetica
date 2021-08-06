import sys

memory = bytearray(4 * 2**16)
breaks = {0x0000}
program: bytes
halt = False
instructions = {
    'add'   : 0x00,
    'addi'  : 0x01, 
    'lw'    : 0x02, 
    'sw'    : 0x03, 
    'beq'   : 0x04,
    'halt'  : 0x06,
    'noop'  : 0x07
}

registers = [0,0,0,0,0,0,0,0]
pc = 0
ir = 0

def read_mem(address, signed=False):
    global memory, registers
    return int.from_bytes(memory[address*4:address*4 +4], byteorder='big', signed=signed)

def write_mem(address: int, value:int, signed=False):
    global memory, registers
    vb = value.to_bytes(4, 'big', signed=True)
    memory[address] = vb[0]
    memory[address + 1] = vb[1]
    memory[address + 2] = vb[2]
    memory[address + 3] = vb[3]
    return

def clock():
    global memory, registers, instructions, halt, pc, ir
    # Le instrução do endereço pc e coloca em ir
    ir = read_mem(pc)
    oper  = 0b00000001110000000000000000000000 & ir
    A =     0b00000000001110000000000000000000 & ir
    B =     0b00000000000001110000000000000000 & ir
    nib16 = 0b00000000000000001111111111111111 & ir
    last3 = 0b00000000000000000000000000000111 & ir

    oper >>= 22
    A >>= 19
    B >>= 16
    nib16 = int.from_bytes( nib16.to_bytes(2,'big'), byteorder='big', signed=True)

    if oper == instructions['add']:
        # res = (registers[B] + registers[A]).to_bytes(4, byteorder='big')
        # registers[last3] = int.from_bytes(res, byteorder='big',signed=True)
        registers[last3] = registers[B] + registers[A]
    elif oper == instructions['addi']:
        registers[B] = registers[A] + nib16

    elif oper == instructions['lw']:
        pointer = registers[A] + nib16
        registers[B] = read_mem(pointer)

    elif oper == instructions['sw']:
        pointer = registers[A] + nib16

    elif oper == instructions['beq']:
        if registers[A] == registers[B]:
            pc += nib16

    elif oper == instructions['halt']:
        halt = True
        return
    
    elif oper == instructions['noop']:
        return
    
    pc += 1

def load_program(program):
    i = 0
    global memory
    for byte in program:
        memory[i] = byte
        i+=1

def print_mem(address, r=4):
    global memory
    for i in range(r):
        print(f"{address + i:04x}", end="  ")
        for j in range(4):
            print(f"{memory[ (address+i) * 4 + j]:02x}", end=" ")
        print("")

def set_reg(reg, value):
    global pc
    maps = {
        'reg0' : 0x00,
        'reg1' : 0x01,
        'reg2': 0x02,
        'reg3': 0x03,
        'reg4': 0x04,
        'reg5': 0x05,
        'reg6': 0x06,
        'reg7': 0x07,
    }
    if reg == 'pc':
        pc = value
    else:
        registers[maps[reg]] = value

def print_status():
    global registers, ir, pc
    disRegisters = ['reg0','reg1','reg2','reg3','reg4','reg5','reg6','reg7']
    i = 0
    print("- registers -")
    print('pc',f'{pc:08x}')
    print('ir',f'{ir:08x}')
    for reg in registers:
        print(disRegisters[i], f'{reg:08x}')
        i+=1

def run():
    global halt, memory, registers, breaks, pc
    while not halt:
        clock()
        if pc in breaks:
            break

# 1000  00 00 00 00
# 0000  00 00 00 00
# 0000  00 00 00 00
# 0000  00 00 00 00

# >> help
# >> dis
# >> clear
# >> step
# >> run
# >> set
# >> print memory
# >> print *pc
# >> print *reg2
# >> status check

program = open(sys.argv[1],'rb').read()
load_program(program)

while not halt:
    input()
    clock()
    print_mem(0,6)
    print_status()