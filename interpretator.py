import struct
import sys
import json

class UVMInterpreter:
    def __init__(self, memory_size=1024):
        self.memory = [0] * memory_size
    
    def load_binary(self, binary_file):
        with open(binary_file, 'rb') as f:
            self.binary_data = f.read()
    
    def execute(self):
        pc = 0
        while pc < len(self.binary_data):
            opcode = self.binary_data[pc] & 0xF
            if opcode == 0b1011:  # LOAD_CONST
                instruction = struct.unpack('>I', self.binary_data[pc:pc+4])[0]
                instruction = int.from_bytes(instruction.to_bytes(4, byteorder='big'), byteorder='little')
                constant = (instruction >> 4) & 0x1FFFFF
                address = (instruction >> 25) & 0x3F
                self.memory[address] = constant
                pc += 4
            elif opcode == 0b0000:  # READ_MEM
                instruction = struct.unpack('>H', self.binary_data[pc:pc+2])[0]
                instruction = int.from_bytes(instruction.to_bytes(2, byteorder='big'), byteorder='little')
                address_b = (instruction >> 20) & 0x3F
                address_c = (instruction >> 26) & 0x3F
                self.memory[address_c] = self.memory[address_b]
                pc += 2
            elif opcode == 0b1111:  # WRITE_MEM
                instruction = struct.unpack('>I', self.binary_data[pc:pc+4])[0]
                instruction = int.from_bytes(instruction.to_bytes(4, byteorder='big'), byteorder='little')
                offset_d = (instruction >> 16) & 0xFFF
                address_c = (instruction >> 10) & 0x3F
                address_b = (instruction >> 4) & 0x3F
                self.memory[address_b + offset_d] = self.memory[address_c]
                pc += 4
            elif opcode == 0b1101:  # SHIFT_RIGHT
                instruction = struct.unpack('>I', self.binary_data[pc:pc+4])[0]
                instruction = int.from_bytes(instruction.to_bytes(4, byteorder='big'), byteorder='little')
                address_d = (instruction >> 16) & 0x3F
                address_c = (instruction >> 10) & 0x3F
                address_b = (instruction >> 4) & 0x3F
                result_address = self.memory[address_c]
                value_b = self.memory[address_b]
                num_bits = self.memory[address_d]
                shifted_value = (value_b >> num_bits) | (value_b << (16 - num_bits) & 0xFFFF)
                self.memory[result_address] = shifted_value
                pc += 4
            else:
                raise ValueError(f"Unknown opcode: {opcode}")
    
    def save_memory_range(self, output_file, start_address, end_address):
        memory_range = {f"Memory[{address}]": self.memory[address] for address in range(start_address, end_address + 1)}
        with open(output_file, 'w') as f:
            json.dump(memory_range, f, indent=4)

if __name__ == "__main__":
    binary_file = sys.argv[1]
    output_file = sys.argv[2]
    start_address = int(sys.argv[3])
    end_address = int(sys.argv[4])

    interpreter = UVMInterpreter()
    interpreter.load_binary(binary_file)
    interpreter.execute()
    interpreter.save_memory_range(output_file, start_address, end_address)
