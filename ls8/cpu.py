"""CPU functionality."""

import sys
import os

# file access will store our path
# we first get our current working directory
# then we walk down every path from our directory.
# if we encounter the file from our sys.argv, then we will create that path and store it in file_access to use later
file_access = ''
path = os.getcwd()
for root, dirs, names in os.walk(path):
    if sys.argv[1] in names:
        file_access = os.path.join(root, sys.argv[1])

LDI = 0b10000010 #LDI
PRN = 0b01000111 #PRN
ADD = 0b10100000 #ADD
MUL = 0b10100010 #MUL
HLT = 0b00000001 #HLT
PUSH = 0b01000101 #PUSH
POP = 0b01000110 #POP
CALL = 0b01010000 #CALL
RET = 0b00010001 #RET
CMP = 0b10100111 #CMP
JMP  = 0b01010100 #JMP
JEQ  = 0b01010101 #JEQ
JNE  = 0b01010110 #JNE

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        #self.ram is our memory, holds ints from 0-255
        self.ram = [0] * 256
        #self.reg is going to store our registers
        self.reg = [0] * 8
        self.branch_table = {}
        self.branch_table[LDI] = self.handle_ldi
        self.branch_table[PRN] = self.handle_prn
        self.branch_table[ADD] = self.handle_add
        self.branch_table[MUL] = self.handle_mul
        self.branch_table[CMP] = self.handle_cmp
        self.branch_table[HLT] = self.handle_hlt
        self.branch_table[PUSH] = self.handle_push
        self.branch_table[POP] = self.handle_pop
        self.branch_table[CALL] = self.handle_call
        self.branch_table[RET] = self.handle_ret
        self.branch_table[JMP] = self.handle_jmp
        self.branch_table[JEQ] = self.handle_jeq
        self.branch_table[JNE] = self.handle_jne

        # Internal regs
        self.pc = 0 # Program Counter: where current instruction is located
        self.ir = 0 # Instruction Register: copy of the current instruction
        self.mar = 0 # Memory Address Register: address to read/write to
        self.mdr = 0 # Memory Data Register: the value being read/wrote
        self.fl = 0 # Flag Register: holds the current flags status
        self.op_a = 0 # Operand A
        self.op_b = 0 # Operand B
        self.running = True

        self.reg[7] = 0xF4 # Stack Pointer: points to the top of our stack, or F4 if empty

    ###NECESSARY PROGRAM FUNCTIONS###
    def ram_read(self, ind):
        # set our mar as the location receiving, 
        # and the mdr as the value in memory at that location. 
        # then return the value
        self.mar = ind
        self.mdr = self.ram[ind]
        return self.mdr

    def ram_write(self, ind, mdr):
        self.mar = ind
        self.mdr = mdr
        self.ram[ind] = mdr
        return

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print("usage: comp.py progname")
            sys.exit(1)

        try:
            with open(file_access) as f:
                for line in f:
                    line = line.strip()
        
                    if line == '' or line[0] == "#":
                        continue
        
                    try:
                        str_value = line.split("#")[0]
                        instruction = int(str_value, 2)
        
                    except ValueError:
                        print(f"Invalid number: {str_value}")
                        sys.exit(1)
        
                    self.ram[address] = instruction
                    address += 1
        
        except FileNotFoundError:
            print(f"File not found: {sys.argv[1]}")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op  == "CMP":
            #`FL` bits: `00000LGE`
            # we'll do comparisons against each condition. LGE stands for less, greater, equal. bit is changed accordingly to equal true or false
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            else:
                self.fl = 0b00000001
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
    ###END OF PROGRAM FUNCTIONS###


    ###BRANCH TABLE FUNCTIONS###
    def handle_ldi(self):
        self.reg[self.op_a] = self.op_b

    def handle_prn(self):
        print(f'Register at {self.op_a} contains {self.reg[self.op_a]}')

    def handle_add(self):
        self.alu('ADD', self.op_a, self.op_b)

    def handle_mul(self):
        self.alu('MUL', self.op_a, self.op_b)

    def handle_cmp(self):
        self.alu('CMP', self.op_a, self.op_b)

    def handle_hlt(self):
        self.running = False

    def handle_push(self):
        self.reg[7] -= 1

        val = self.reg[self.op_a]
        self.ram[self.reg[7]] = val 

    def handle_pop(self):
        # access the value in our memory located at our stack pointer
        # then set the value in our register at self.op_a and increment stack counter
        val = self.ram[self.reg[7]]
        self.reg[self.op_a] = val

        self.reg[7] += 1

    def handle_call(self):
        #NOTE: sets pc, will trigger if conditional for pc        
        ret_addr = self.pc + 2
        
        # Decrement the stack pointer
        self.reg[7] -= 1
    
        # Copy the value onto the stack
        top_of_stack_addr = self.reg[7]
        self.ram[top_of_stack_addr] = ret_addr

        sub_addr = self.reg[self.op_a]

        self.pc = sub_addr

    def handle_ret(self):
        #NOTE: sets pc, will trigger if conditional for pc
        ret_addr = self.ram[self.reg[7]]

        self.reg[7] += 1
        self.pc = ret_addr

    def handle_jmp(self):
        # self.op_a will equal target register; access register and set address value stored in there to our pc
        #NOTE: sets pc, will trigger if conditional for pc
        self.pc = self.reg[self.op_a]
    
    def handle_jeq(self):
        # if LGE is set to E = 1, call jump handler to jump to self.op_a
        if self.fl == 0b00000001:
            self.handle_jmp()
        else:
            self.pc += 2
    
    def handle_jne(self):
        # if LGE is not set to E = 1, call jump handler to jump to self.op_a
        if self.fl != 0b00000001:
            self.handle_jmp()
        else:
            self.pc += 2


    ###END BRANCH TABLE FUNCTIONS###

    def run(self):
        """Run the CPU."""

        while self.running:
            # read the address stored at pc, store it in ir.
            # we also create opers a and b in case we need them for LDI            
            self.ir = self.ram[self.pc]
            self.op_a = self.ram_read(self.pc + 1)
            self.op_b = self.ram_read(self.pc + 2)

            # Once we have our instruction, we'll access the location on our branch table at that instruction if it exists, passing in our operand a and b.
            # This will send them to our handle functions
            if self.ir in self.branch_table:
                self.branch_table[self.ir]()
            else:
                print("Unrecognized operation. Terminating process.")
                self.running = False

            #afterwards, we want to increment our counter by 1 + the number of operands that were necessary for our operation (determined by the first 2 places of our binary number)
            if self.ir & 0b00010000 != 0:
                continue
            else: 
                self.pc += (self.ir >> 6) + 1

cpu = CPU()
cpu.load()
