class Assembler:

    MAX_VALUE = 2**15 - 1
    MIN_VALUE = - 2**15

    instructions = {
        'add'   : 0x00,
        'addi'  : 0x01, 
        'lw'    : 0x02, 
        'sw'    : 0x03, 
        'beq'   : 0x04,
        'halt'  : 0x06,
        'noop'  : 0x07,
    }

    registers = {
        'pc'  : 0x00,
        'reg1': 0x01,
        'reg2': 0x02,
        'reg3': 0x03,
        'reg4': 0x04,
        'reg5': 0x05,
        'reg6': 0x06,
        'reg7': 0x07,
    }

    disRegisters = ['pc','reg1','reg2','reg3','reg4','reg5','reg6','reg7']
    disInstuctions = ['add','addi','lw','sw','beq','err','halt','noop']

    def __init__(self):
        self.program = ""
        self.lines = []
        self.compiledProgram = []
        self.definedLabels = {} # 'LABEL' : ADDRESS: int
        self.lookingforLabels = {} # 'LABEL': [ADRESSES]
        self.exception = False

    def LoadProgram(self, path: str):
        try:
            with open(path, 'r') as file:
                self.program = file.read()
        except FileNotFoundError:
            print("Error, file not found")
        return

    def SaveProgram(self, name: str):
        if self.exception:
            return
        if self.compiledProgram == "":
            return
        with open(name, 'wb') as file:
            for l in self.compiledProgram:
                file.write(l)

    def ThrowError(self, code, line, extra):
        # Redefinição de Label
        self.exception = True
        if code == 100:
            print(f"Redefinição de Label '{extra}'")
        elif code == 101:
            print(f"Label não definida '{extra}'")
        elif code == 400:
            print(f"Registrador '{extra}' não existente")
        elif code == 500:
            print(f"Instrução inexperada '{extra}'")
        print(f"linha: {line}")

    def CleanProgram(self, program:str):
        lines = program.split("\n")
        for l in lines:
            op = l.split()
            if len(op) == 0:
                lines.remove(l)
        self.lines = lines

    def Assemble(self, program: str):
        self.exception = False
        counter = -1
        self.CleanProgram(program)
        
        for line in self.lines:

            opcodes = line.split()
            counter += 1
            i = 0

            # Se a primeira palavra da linha não for um OP Code
            # Será compreendido como um Label
            if not opcodes[i] in Assembler.instructions:
                if (opcodes[i] in self.definedLabels):
                    self.ThrowError(100, counter, opcodes[i])
                    break
                elif (opcodes[i] in self.lookingforLabels):
                    addresses = self.lookingforLabels[opcodes[i]]
                    for a in addresses:
                        instruct = int.from_bytes(self.compiledProgram[a], byteorder='big')
                        instruct += counter - a - 1
                        self.compiledProgram[a] = instruct.to_bytes(4, byteorder='big')
                    del self.lookingforLabels[opcodes[i]]
                        
                self.definedLabels[opcodes[i]] = counter
                i += 1

            mask = 0
            op = Assembler.instructions[opcodes[i]]
            mask += op << 22

            if opcodes[i] != 'noop' and opcodes[i] != 'halt':
                try:
                    regA = Assembler.registers[opcodes[i + 1]]
                    regB = Assembler.registers[opcodes[i + 2]]
                except Exception:
                    self.ThrowError(400, counter, opcodes[i+1])
                    break
                mask += regA << 19
                mask += regB << 16
            if opcodes[i] == 'add':
                regC = Assembler.registers[opcodes[i + 3]]
                mask += regC
            elif opcodes[i] == 'addi' or opcodes[i] =='lw' or opcodes[i]=='sw':
                nib16 = int(opcodes[i + 3])
                nC = nib16.to_bytes(2, byteorder='big',signed=True)
                mask += int.from_bytes(nC, 'big')
            elif opcodes[i] == 'beq':
                label = opcodes[i + 3]
                if label in self.definedLabels:
                    address = self.definedLabels[label]
                    mask += address - counter - 1
                else:
                    if not label in self.lookingforLabels:
                        self.lookingforLabels[label] = []
                    self.lookingforLabels[label].append(counter)
            elif  opcodes[i] != 'noop' and opcodes[i] != 'halt':
                self.ThrowError(500, counter, opcodes[i])
            self.compiledProgram.append(mask.to_bytes(4, byteorder='big'))

        if len(self.lookingforLabels) > 0:
            for label, addresses in self.lookingforLabels.items():
                for a in addresses:
                    self.ThrowError(101, a, label)

        if self.exception:
            return []
        return self.compiledProgram

    def Disassemble(self, program: bytes):
        length = len(program)
        i = 0
        lines = []
        while i < length:
            code = int.from_bytes( program[i:i+4], byteorder='big', signed=False)
            i+=4
            oper  = 0b00000001110000000000000000000000 & code
            parmB = 0b00000000001110000000000000000000 & code
            parmC = 0b00000000000001110000000000000000 & code
            nib16 = 0b00000000000000001111111111111111 & code
            last3 = 0b00000000000000000000000000000111 & code

            oper >>= 22
            parmB >>= 19
            parmC >>= 16

            if oper == 0:
                line = 'add'+' '+Assembler.disRegisters[parmB]+' '+ Assembler.disRegisters[parmC]+' '+Assembler.disRegisters[last3]
            elif 6 <= oper <= 7:
                line = Assembler.disInstuctions[oper]
            else:
                line = Assembler.disInstuctions[oper] + ' ' + Assembler.disRegisters[parmB] +' ' + Assembler.disRegisters[parmC]+ ' ' + str(nib16)

            lines.append(line)
        return lines

asm = Assembler()
program = """
        beq reg3 reg1 ELSE
        add reg3 reg1 reg4

        beq reg1 reg1 EXIT
ELSE    add reg3 reg2 reg4
EXIT    halt"""
by = asm.Assemble(program)
# asm.SaveProgram("out.bin")
print(by)

# binFile = open("out.bin", "rb")
# binary = binFile.read()
# disassembled = asm.Disassemble(binary)
# print(disassembled)