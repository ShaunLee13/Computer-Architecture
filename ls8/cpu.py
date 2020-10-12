"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        #self.ram is our memory, holds ints from 0-255
        self.ram = [0] * 256
        #self.reg is going to store our registers
        self.reg = [0] * 8

        # Internal regs
        self.pc = 0 # Program Counter: where current instruction is located
        self.ir = 0 # Instruction Register: copy of the current instruction
        self.mar = 0 # Memory Address Register: address to read/write to
        self.mdr = 0 # Memory Data Register: the value being read/wrote
        self.fl = 0 # Flag Register: holds the current flags status

        self.reg[7] = 0xF4 # Stack Pointer: points to the top of our stack, or F4 if empty

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

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
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

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            # read the address stored at pc, store it in ir.
            # we also create opers a and b in case we need them for LDI
            self.ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # Now we execute our instructions
            if self.ir == 0b10000010: #LDI function
                # we'll access the register at operand a, and insert operand b there
                self.reg[operand_a] = operand_b

                # then increment our counter by 3 places
                self.pc += 3

            elif self.ir == 0b01000111: #PRN function
                # we need to access register at operand a and print that to our terminal
                print(f'Register at {operand_a} contains {self.reg[operand_a]}')

                #after that, we increment our counter by 2 places
                self.pc += 2

            elif self.ir == 0b00000001: #HLT function
                # we just need to terminate the process
                running = False

            #and if none of the other functions apply, we've encountered an error, so print a response and exit.
            else:
                print("Error: Instruction not recognized. Terminating Process.")
                running = False


cpu = CPU()
cpu.load()
