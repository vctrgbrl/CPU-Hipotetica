import sys
import os

memory = bytearray(4 * 2**16)
breaks = {0x0000}
program: bytes
halt = False
init = False
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

def set_reg(args: list):
    global pc
    reg = args[0]
    value = int(args[1])
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

def print_status(args: list):
    global registers, ir, pc
    disRegisters = ['reg0','reg1','reg2','reg3','reg4','reg5','reg6','reg7']
    i = 0
    print("- registers -")
    print('pc',f'{pc:08x}')
    print('ir',f'{ir:08x}')
    for reg in registers:
        print(disRegisters[i], f'{reg:08x}')
        i+=1

def run(args: list):
    global halt, memory, registers, breaks, pc
    while not halt:
        clock()
        if pc in breaks:
            breaks.remove(pc)
            print_mem(pc)
            print_status([])
            break

def help(args: list):
    print(
    """
    >> help - display de commandos
    >> load - carrega um arquivo binario na memoria no endereço 0000
    >> dis - faz o disassemble do programa próximo ao registrador pc
    >> step - executa um ciclo
    >> run - executa até achar um break
    >> break [endereço] - marca um local da memória
    >> set [registrador|endereço] [valor] - força um valor no registrador/memoria
    >> print memory [endereço] - mostra a memoria no determinado endereço  
    >> status - mostra status dos registradores

    OBS: endereços devem ser setados como inteiros

    """)

def clear(args: list):
    os.system("clear")

def exit(args: list):
    global halt
    halt = True
    return

def interface_print(args: list):
    if(args[0] == "memory"):
        print_mem(int(args[1]))
        return

def open_program(args: list):
    global program, init
    try:
        prog = open(args[0],'rb')
        program = prog.read()
        print("carreagado com sucesso")
        load_program(program)
        init = True
    except FileNotFoundError:
        print(f"programa {args[0]} não encontrado")

def break_at(args: list):
    global breaks
    address = int(args[0])
    breaks.add(address)

def step(args: list):
    clock()

def command(cmd: list):
    interfaces_commands = {
        'help': help,
        'clear': clear,
        'set': set_reg,
        'status': print_status,
        'print': interface_print,
        'exit': exit,
        'load': open_program,
        'run': run,
        'step': step,
        'break': break_at
    }
    if not cmd[0] in interfaces_commands:
        print(f"comando inexperado: {cmd[0]}")
        return
    args = cmd[1:]
    interfaces_commands[cmd[0]](args)

if len(sys.argv) == 2:
    open_program(sys.argv)

while not halt:
    print(">>", end=" ")
    cmd = input()
    if cmd == "":
        continue
    command(cmd.split())