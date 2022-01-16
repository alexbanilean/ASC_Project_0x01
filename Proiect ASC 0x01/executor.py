name_lists = ["rv32ui-v-addi.mc", "rv32ui-v-beq.mc", "rv32ui-v-lw.mc", "rv32ui-v-srl.mc", "rv32ui-v-sw.mc", "rv32ui-v-xor.mc", "rv32um-v-rem.mc"]
d = {}
registers = [0 for i in range(32)]
PC = 0
next_file_flag = 0

def twos_comp(val, bits):
    if val < 0:
        val = (1 << bits) + val
    else:
        if (val & (1 << (bits - 1))) != 0:
            val = val - (1 << bits)
    return val

def r_unsigned_shift(base, exp):
    if exp == 0:
        return base

    base = twos_comp(base, 32)

    sgn = 1
    if base < 0:
        #sgn = -1
        byte = bin(base)[3:-exp].zfill(32)
    else:
        byte = bin(base)[2:-exp].zfill(32)
    return int(byte,2)

def sign_extend(bytes):
    if bytes[0] == '0':
        return "00000000000000000000" + bytes
    else:
        return "11111111111111111111" + bytes

def check_hex_string(x):
    hexdigits = "0123456798abcdefABCDEF"
    for i in x:
        if i not in hexdigits:
            return 0
    return 1


def decode_R_format(x):
    global PC

    func7 = x[0:7]
    rs2 = int(x[7:12], 2)
    rs1 = int(x[12:17], 2)
    func3 = x[17: 20]
    rd = int(x[20:25], 2)

    if rd == 0:
        PC += 4
        return

    if func3 == "000" and func7 == "0000000":
        # add
        registers[rd] = registers[rs1] + registers[rs2]
    elif func3 == "000" and func7 == "0100000":
        # sub
        registers[rd] = registers[rs1] - registers[rs2]
    elif func3 == "001" and func7 == "0000000":
        # sll
        while registers[rs2] < 0:
            registers[rs2] += 32
        registers[rd] = registers[rs1] << registers[rs2]
    elif func3 == "010" and func7 == "0000000":
        # slt
        registers[rd] = (registers[rs1] < registers[rs2])
    elif func3 == "011" and func7 == "0000000":
        # sltu
        registers[rd] = (registers[rs1] < registers[rs2])
    elif func3 == "100" and func7 == "0000000":
        # xor
        registers[rd] = registers[rs1] ^ registers[rs2]
    elif func3 == "101" and func7 == "0000000":
        # srl
        while registers[rs2] < 0:
            registers[rs2] += 32
        registers[rd] = r_unsigned_shift(registers[rs1], registers[rs2])
    elif func3 == "101" and func7 == "0000000":
        # sra - in python there is only sra
        while registers[rs2] < 0:
            registers[rs2] += 32
        registers[rd] = registers[rs1] >> registers[rs2]
    elif func3 == "110" and func7 == "0000000":
        # or
        registers[rd] = registers[rs1] | registers[rs2]
    elif func3 == "110" and func7 == "0000001":
        # rem
        if registers[rs2] == 0:
            registers[rd] = registers[rs1]
        else:
            minus = 1
            if registers[rs2] < 0:
                registers[rs2] = -registers[rs2]
            if registers[rs1] < 0:
                registers[rs1] = -registers[rs1]
                minus = -1
            registers[rd] = (registers[rs1] % registers[rs2]) * minus
    elif func3 == "111" and func7 == "0000000":
        # and
        registers[rd] = registers[rs1] & registers[rs2]

    PC += 4


def decode_I_format(bytes):
    global PC

    if bytes[27] == "1":
        imm = int(bytes[:12], 2)
        imm = twos_comp(imm, 12)

        rs1 = int(bytes[12:17], 2)
        func3 = bytes[17:20]
        rd = int(bytes[20:25], 2)
        if rd == 0:
            PC += 4
            return

        if func3 == "000":
            # addi
            registers[rd] = registers[rs1] + imm

            maxim = (1 << 31) - 1
            minim = -1 << 31
            if registers[rd] > maxim:
                registers[rd] -= (1 << 32)
            if registers[rd] < minim:
                registers[rd] += (1 << 32)

        elif func3 == "001":
            # slli, slliw
            shamt = int(bytes[7:12], 2)
            registers[rd] = registers[rs1] << shamt
        elif func3 == "010":
            # slti
            registers[rd] = registers[rs1] < imm
        elif func3 == "011":
            # sltiu
            registers[rd] = registers[rs1] < imm
        elif func3 == "100":
            # xori
            registers[rd] = registers[rs1] ^ imm
        elif func3 == "101":
            shamt = int(bytes[7:12], 2)
            if bytes[1] == "0":
                # srli, srliw
                registers[rd] = 2 << (32 - shamt + 1) - (registers[rs1] >> shamt)
            else:
                # srai, sraiw
                registers[rd] = registers[rs1] >> shamt
        elif func3 == "110":
            # ori
            registers[rd] = registers[rs1] | imm
        elif func3 == "111":
            # andi
            registers[rd] = registers[rs1] & imm
    else:

        offset = int(bytes[:12], 2)
        offset = twos_comp(offset, 12)
        rs1 = int(bytes[12:17], 2)
        width = bytes[17:20]
        rd = int(bytes[20:25], 2)

        if rd == 0:
            PC += 4
            return

        if width == "010":
            # lw
            adresa = registers[rs1] + offset
            registers[rd] = int(d[adresa], 2)

            if adresa + 2 in d:
                registers[rd] <<= 16
                registers[rd] += int(d[adresa + 2], 2)

            registers[rd] = twos_comp(registers[rd], 32)
        else:
            # other instructions
            return
    PC += 4

def decode_S_format(x):

    global PC

    imm2 = x[0:7]
    rs2 = int(x[7:12], 2)
    rs1 = int(x[12:17], 2)
    func3 = x[17: 20]
    imm1 = x[20:25]

    imm = imm2 + imm1
    imm = int(imm, 2)
    imm = twos_comp(imm, 12)

    location = registers[rs1] + imm

    if func3 == "000":
        # sb
        d[location] = registers[rs2][0:8] + d[location][8:]
    elif func3 == "001":
        # sh
        d[location] = registers[rs2][0:16] + d[location][16:]
    elif func3 == "010":
        # sw
        if registers[rs2] < 0:
            # sgn = -1
            d[location] = bin((1 << 32) + registers[rs2])[2:].zfill(32)
        else:
            d[location] = bin(registers[rs2])[2:].zfill(32)

    PC += 4


def decode_SB_format(x):

    global PC

    imm2 = x[0:7]
    rs2 = int(x[7:12], 2)
    rs1 = int(x[12:17], 2)
    func3 = x[17: 20]
    imm1 = x[20:25]

    imm = int(imm2[0] + imm1[4] + imm2[1:] + imm1[0:4] + "0", 2)
    imm = twos_comp(imm, 13)

    if func3 == "000":
        # beq
        if registers[rs1] == registers[rs2]:
            PC += imm
        else:
            PC += 4
    elif func3 == "001":
        # bne
        if registers[rs1] != registers[rs2]:
            PC += imm
        else:
            PC += 4
    elif func3 == "100":
        # blt
        if registers[rs1] < registers[rs2]:
            PC += imm
        else:
            PC += 4
    elif func3 == "101":
        # bge
        if registers[rs1] >= registers[rs2]:
            PC += imm
        else:
            PC += 4
    elif func3 == "110":
        # bltu
        if registers[rs1] < registers[rs2]:
            PC += imm
        else:
            PC += 4
    elif func3 == "111":
        # bgeu
        if registers[rs1] >= registers[rs2]:
            PC += imm
        else:
            PC += 4
    else:
        PC += 4

def decode_U_format(bytes):

    global PC

    if bytes[26] == '1':
        # lui

        imm = int(bytes[:20], 2)
        imm = imm << 12
        imm = twos_comp(imm, 32)
        rd = int(bytes[20:25], 2)

        if rd != 0:
            registers[rd] = imm

        PC += 4

    else:
        # auipc

        imm = int(bytes[:20], 2)
        imm = twos_comp(imm, 20)
        imm = imm << 12
        rd = int(bytes[20:25], 2)

        if rd != 0:
            registers[rd] = PC + imm

        PC += 4


def decode_UJ_format(bytes):

    global PC

    offset = int(bytes[0] + bytes[12:20] + bytes[11] + bytes[1:11] + "0", 2)
    offset = twos_comp(offset, 20)
    rd = int(bytes[20:25], 2)

    if rd != 0:
        registers[rd] = PC + 4

    PC += offset

def decode_ecall():

    global next_file_flag

    # check a0 == 1 -> completed successfully
    if registers[10] == 1:
        print("Pass")
    else:
        print(f"Fail: Test_{registers[10] // 2}")

    next_file_flag = 1
    return

def cycle(x):

    global PC

    bin_instr = x

    type_opcode = bin_instr[25:32]

    if type_opcode == "0110011":
        # R format
        decode_R_format(bin_instr)
    elif type_opcode == "0100011":
        # S format
        decode_S_format(bin_instr)
    elif type_opcode == "1100011":
        # SB format
        decode_SB_format(bin_instr)
    elif type_opcode == "0010011" or type_opcode == "0000011":
        # I format
        decode_I_format(bin_instr)
    elif type_opcode == "0110111":
        # U format -> lui
        decode_U_format(bin_instr)
    elif type_opcode == "0010111":
        # U format -> auipc
        decode_U_format(bin_instr)
    elif type_opcode == "1110011":
        # ecall
        decode_ecall()
    else:
        print("Not supported operation!")
        PC = -1

for file in name_lists:

    d = {}
    registers = [0 for i in range(32)]
    PC = 0
    next_file_flag = 0

    with open(file, "r") as f:
        for line in f:

            splt = [x for x in line.strip().split()]
            address = splt[0]
            address = address[:8]
            instr = splt[1]

            if check_hex_string(address) and check_hex_string(instr):
                d[int(address, 16) - int("80000000", 16)] = bin(int(instr, 16))[2:].zfill(32)

        # start with <userstart>, registers are already clean
        PC = 10720

        print(f"{file} output: ", end=' ')

        while PC in d:
            if next_file_flag == 1:
                next_file_flag = 0
                break
            cycle(d[PC])
