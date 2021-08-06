class CPU:
    def __init__(self, memory_size:int = 2048):
        self.memory = bytearray(memory_size)
        
        self.instructions = {
            'add', 
            'addi', 
            'lw', 
            'sw', 
            'beq',
            'noop'
        }
        self.registers = {
            'pc': 0x0000,
            'ra': 0x0000,
            'rb': 0x0000,
            'rc': 0x0000,
            'rd': 0x0000
        }

    def add(self, regA, regB, regC):
        if (regA in self.registers
        and regB in self.registers
        and regC in self.registers):
            self.registers[regC] = self.registers[regA] + self.registers[regB]
            return
        # Error, unexpected argument

    def addi(self, regA, const, regB):
        if (regA in self.registers
        and regB in self.registers):
            self.registers[regB] = self.registers[regA] + int(const)
            return
        # Error, unexpected argument
    



'''
add ra rb ra
lw ra rb 
'''

# Separar linha por linha
