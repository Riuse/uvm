import struct
import sys
import json

def parse_instruction(line):
    parts = line.split()
    if parts[0] == "LOAD_CONST":
        opcode = 0b1011
        constant = int(parts[1])
        address = int(parts[2])
        if constant >= (1 << 21) or address >= (1 << 6):
            raise ValueError("Constant or address out of range")
        instruction = (address << 25) | (constant << 4) | opcode
        return opcode, constant, address, instruction, 4
    elif parts[0] == "READ_MEM":
        opcode = 0b0000
        address_b = int(parts[1])
        address_c = int(parts[2])
        if address_b >= (1 << 6) or address_c >= (1 << 6):
            raise ValueError("Address out of range")
        instruction = (address_c << 26) | (address_b << 20) | (opcode << 4)
        return opcode, address_b, address_c, instruction, 2
    elif parts[0] == "WRITE_MEM":
        opcode = 0b1111
        offset_d = int(parts[3])
        address_c = int(parts[2])
        address_b = int(parts[1])
        if offset_d >= (1 << 12) or address_c >= (1 << 6) or address_b >= (1 << 6):
            raise ValueError("Offset or address out of range")
        instruction = (offset_d << 16) | (address_c << 10) | (address_b << 4) | opcode
        return opcode, address_b, address_c, offset_d, instruction, 4
    elif parts[0] == "SHIFT_RIGHT":
        opcode = 0b1101
        address_d = int(parts[3])
        address_c = int(parts[2])
        address_b = int(parts[1])
        if address_d >= (1 << 6) or address_c >= (1 << 6) or address_b >= (1 << 6):
            raise ValueError("Address out of range")
        instruction = (address_d << 16) | (address_c << 10) | (address_b << 4) | opcode
        return opcode, address_b, address_c, address_d, instruction, 3
    else:
        raise ValueError(f"Unknown instruction: {parts[0]}")

def assemble(input_file, output_file, log_file):
    log_entries = []
    with open(input_file, 'r') as infile, open(output_file, 'wb') as outfile:
        for line in infile:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if "WRITE_MEM" in line:
                opcode, address_b, address_c, offset_d, instruction, byte_length = parse_instruction(line)
                instruction_bytes = struct.pack('>I', instruction)
                reversed_bytes = instruction_bytes[::-1]
                outfile.write(reversed_bytes)
                log_entries.append({
                    "A": 15,
                    "B": address_b,
                    "C": address_c,
                    "D": offset_d,
                    "bytes": [f"0x{byte:02X}" for byte in reversed_bytes]
                })
            elif "SHIFT_RIGHT" in line:
                opcode, address_b, address_c, address_d, instruction, byte_length = parse_instruction(line)
                instruction_bytes = struct.pack('>I', instruction)
                reversed_bytes = instruction_bytes[::-1]
                outfile.write(reversed_bytes)
                log_entries.append({
                    "A": 13,
                    "B": address_d,
                    "C": address_c,
                    "D": address_b,
                    "bytes": [f"0x{byte:02X}" for byte in reversed_bytes[:3]]
                })
            else:
                opcode, operand1, operand2, instruction, byte_length = parse_instruction(line)
                if byte_length == 4:
                    instruction_bytes = struct.pack('>I', instruction)
                    reversed_bytes = instruction_bytes[::-1]
                    outfile.write(reversed_bytes)
                    log_entries.append({
                        "A": opcode,
                        "B": operand1,
                        "C": operand2,
                        "bytes": [f"0x{byte:02X}" for byte in reversed_bytes]
                    })
                elif byte_length == 2:
                    instruction_bytes = struct.pack('>H', instruction >> 16)
                    reversed_bytes = instruction_bytes[::-1]
                    outfile.write(reversed_bytes)
                    log_entries.append({
                        "A": opcode,
                        "B": operand1,
                        "C": operand2,
                        "bytes": [f"0x{byte:02X}" for byte in reversed_bytes]
                    })
    with open(log_file, 'w') as logfile:
        json.dump(log_entries, logfile, indent=4)

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    log_file = sys.argv[3]
    assemble(input_file, output_file, log_file)
