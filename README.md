# CPU Hipotética

Assembler e Emulador de uma CPU Hipotética, baseada na arquitetura MIPS, 
estudada na matéria de Fundamentos de Arquiteturas de Computadores, Ciência da Computação, UFF


A CPU tem 10 registradores, 2 especiais e 8 auxiliares
PC - Program Counter
IR - Intruction Register
Reg0
Reg1
Reg2
Reg3
Reg4
Reg5
Reg6
Reg7

## Instruction Set

| OPCODE    |      Types        | Detalhes                              |
| ------    | --------------    | --------                              |
| **ADD**   | regA regB destReg | soma o valor de regA e regB em regC   |
| **ADDI**  | regA regB const   | soma o valor de regA com const e guarda em regB |
| **LW**    | regA regB desloc  | carrega no regB o endereço de regA + desloc |
| **SW**    | regA regB desloc  | guarda o valor de regB no endereço de regA + desloc |
| **BEQ**   | regA regB desloc  | Compara regA e regB, se iguais, descola |
| **HALT**  |                   | para execução do programa             |
| **NOOP**  |                   | sem operação                          |

## Bytes

### ADD
| OPCODE    | BIAS      | OP_BIN | REG_A | REG_B | BIAS               | REG_C |
| --------- | --------  | ------ | ----  | ----  | ----               | ----  |
| **ADD**   | 0000 000  | 000    | 000   | 000   | 0000 0000 0000 0   | 000   |
### ADDI
| OPCODE    | BIAS      | OP_BIN | REGA | REGB | INTEGER              |
| --------- | --------  | ------ | ---- | ---- | -------------------- |
| **ADDI**  | 0000 000  | 001    | 000  | 000  | 0000 0000 0000 000   |

### LW - Load Word
| OPCODE    | BIAS      | OP_BIN | REGA | REGB | MEMORY ADDRESS        |
| --------- | --------- | ------ | ---- | ---- | --------------------- |
| **LW**    | 0000 000  | 010    | 000  | 000  | 0000 0000 0000 0000   |

### SW - Store Word
| OPCODE    | BIAS      | OP_BIN | REGA | REGB | MEMORY ADDRESS        |
| --------- | --------- | ------ | ---- | ---- | --------------------- |
| **SW**    | 0000 000  | 011    | 000  | 000  | 0000 0000 0000 0000   |

### BEQ - Branch on Equal
| OPCODE    | BIAS      | OP_BIN | REGA | REGB | MEMORY ADDRESS        |
| --------- | --------- | ------ | ---- | ---- | --------------------- |
| **BEQ**   | 0000 000  | 100    | 000  | 000  | 0000 0000 0000 0000   |

### HALT
| OPCODE    | BIAS      | OP_BIN |  BIAS                       |
| --------- | --------- | ------ | -----------------------     |
| **HALT**  | 0000 000  | 110    | 0000 0000 0000 0000 0000 00 |

### NOOP - No Operation
| OPCODE    | BIAS      | OP_BIN |  BIAS                        |
| --------- | --------- | ------ | -----------------------      |
| **NOOP**  | 0000 000  | 111    | 0000 0000 0000 0000 0000 00  |