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
        self.labels = {} # 'LABEL' : ( ADDRESS: int, lookingFor: boolean )

    def LoadProgram(self, path: str):
        try:
            with open(path, 'r') as file:
                self.program = file.read()
        except FileNotFoundError:
            print("Error, file not found")
        return

    def CheckError(self, opcodes, instruction):
        pass

    def EvalLine(self, address, labelResolve):
        line = self.lines[address]
        opcodes = line.split()
        mask = 0
        op = Assembler.instructions[opcodes[0]]
        regA = Assembler.registers[opcodes[1]]
        regB = Assembler.registers[opcodes[2]]
        deloc = labelResolve - address - 1
        mask += deloc
        mask += regB << 16
        mask += regA << 19
        mask += op << 22
        self.compiledProgram.insert(
            address, 
            mask.to_bytes(4, byteorder='big')
        )

    def EvaluateLine(self, i, opcodes, label = 0):

        mask = 0
        op = Assembler.instructions[opcodes[i]]
        mask += op << 22

        if op != 'noop' and op != 'halt':
            regA = Assembler.registers[opcodes[i + 1]]
            regB = Assembler.registers[opcodes[i + 2]]
            mask += regA << 19
            mask += regB << 16
        if op == 'add':
            
            regC = Assembler.registers[opcodes[i + 3]]
            mask += regC

        elif op == 'addi' or op=='lw' or op=='sw':
            nib16 = int(opcodes[i + 3])
            nC = nib16.to_bytes(2, byteorder='big',signed=True)
            mask += int.from_bytes(nC, 'big')
        
        elif op == 'beq':
            label = opcodes[i + 3]
            if not label in self.labels:
                self.labels[label] = (counter, True)
                continue
            address = self.labels[label][0]

        self.compiledProgram.append(mask.to_bytes(4, byteorder='big'))

    def CleanProgram(self, program:str):
        lines = program.split("\n")
        for l in lines:
            op = l.split()
            if len(op) == 0:
                lines.remove(l)
        self.lines = lines

    def Assemble(self, program: str):
        
        counter = -1
        self.CleanProgram(program)
        
        for line in self.lines:

            opcodes = line.split()
            counter += 1
            i = 0

            # Se a primeira palavra da linha não for um OP Code
            # Será compreendido como um Label
            if not opcodes[i] in Assembler.instructions:
                if (opcodes[i] in self.labels):
                    address = self.labels[opcodes[i]][0]
                    self.EvalLine(address, counter)
                else:
                    self.labels[opcodes[i]] = (counter, False)
                i += 1

            if (opcodes[i] == 'add'):
                mask = 0
                op = Assembler.instructions[opcodes[i]]
                regA = Assembler.registers[opcodes[i + 1]]
                regB = Assembler.registers[opcodes[i + 2]]
                regC = Assembler.registers[opcodes[i + 3]]
                
                mask += regC
                mask += regB << 16
                mask += regA << 19
                mask += op << 22
                self.compiledProgram.append(mask.to_bytes(4, byteorder='big'))

            elif opcodes[i] == 'addi':
                mask = 0
                op = Assembler.instructions[opcodes[i]]
                regA = Assembler.registers[opcodes[i + 1]]
                regB = Assembler.registers[opcodes[i + 2]]
                regC = int(opcodes[i + 3])
                nC = regC.to_bytes(2, byteorder='big',signed=True)
                mask += int.from_bytes(nC, 'big')
                mask += regB << 16
                mask += regA << 19
                mask += op << 22
                self.compiledProgram.append(mask.to_bytes(4, byteorder='big'))

            elif (opcodes[i] == 'lw' or opcodes[i] == 'sw'):
                mask = 0
                op = Assembler.instructions[opcodes[i]]
                regA = Assembler.registers[opcodes[i + 1]]
                regB = Assembler.registers[opcodes[i + 2]]
                mem = int(opcodes[i + 3])
                nC = mem.to_bytes(2, byteorder='big',signed=True)
                mask += int.from_bytes(nC, 'big')
                mask += regB << 16
                mask += regA << 19
                mask += op << 22
                self.compiledProgram.append(mask.to_bytes(4, byteorder='big'))

            elif opcodes[i] == 'beq':
                mask = 0
                op   = Assembler.instructions[opcodes[i]]
                regA = Assembler.registers[opcodes[i + 1]]
                regB = Assembler.registers[opcodes[i + 2]]
                label = opcodes[i + 3]
                if not label in self.labels:
                    self.labels[label] = (counter, True)
                    continue
                address = self.labels[label][0]

                mask += address - counter - 1
                mask += regB << 16
                mask += regA << 19
                mask += op << 22
                self.compiledProgram.append(mask.to_bytes(4, byteorder='big'))

            elif opcodes[i] == 'noop' or opcodes[i] == 'halt':
                mask = 0
                mask += Assembler.instructions[opcodes[i]] << 22
                self.compiledProgram.append(mask.to_bytes(4, byteorder='big'))
        
        return self.compiledProgram

    def Disassemble(self, program):
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
        beq reg3 reg1 ELSE - 0000 000 100 011 001 0000 0000 0000 0010
        add reg3 reg1 reg4 - 0000 000 000 011 001 0000 0000 0000 0 100

        beq reg1 reg1 EXIT - 0000 000 100 001 001 0000 0000 0000 0001
ELSE    add reg3 reg2 reg4 - 0000 000 000 011 010 0000 0000 0000 0 100
EXIT    halt               - 0000 000 110 000 000 0000 0000 0000 0000
"""
# by = asm.Assemble(program)

binaryFile = open("out.bin", "rb")
binary = binaryFile.read()
code = asm.Disassemble(binary)

print(code)