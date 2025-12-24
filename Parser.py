from OP import OP
from Scanner import Scanner
import sys
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Add dict for lexemes
categories = ["ARITHOP", "MEMOP", "LOADI", "OUTPUT", "NOP", "REG", "COMMA", "INTO", "EOF", "EOL", "CONSTANT"]
'''
0 - ARITHOP
1 - MEMOP
2 - LOADI
3 - OUTPUT
4 - NOP
5 - REG
6 - COMMA
7 - INTO
8 - EOF
9 - EOL
10 - CONSTANT
'''

def IR_toString(head):
    codesToLexemes = ["load", "loadI", "store", "add", "sub", "mult", "lshift", "rshift", "output", "nop"]
    curr = head
    while curr != None:
        opcode = curr.getData()[1]
        # Two operands
        if opcode  == 0:
            print(codesToLexemes[opcode] + "\t[SR " + str(curr.getData()[2]) + "], [ ], [SR " + str(curr.getData()[10]) + "]")
        elif opcode  == 1:
            print(codesToLexemes[opcode] + "\t[SR " + str(curr.getData()[2]) + "], [ ], [SR " + str(curr.getData()[10]) + "]")
        elif opcode  == 2:
            print(codesToLexemes[opcode] + "\t[SR " + str(curr.getData()[2]) + "], [ ], [SR " + str(curr.getData()[10]) + "]")
        # Three operands
        elif opcode == 3:
            print(codesToLexemes[opcode] + "\t[SR " + str(curr.getData()[2]) + "], [SR " + str(curr.getData()[6]) +
                   "], [SR " + str(curr.getData()[10]) + "]")
        elif opcode == 4:
            print(codesToLexemes[opcode] + "\t[SR " + str(curr.getData()[2]) + "], [SR " + str(curr.getData()[6]) +
                   "], [SR " + str(curr.getData()[10]) + "]")
        elif opcode == 5:
            print(codesToLexemes[opcode] + "\t[SR " + str(curr.getData()[2]) + "], [SR " + str(curr.getData()[6]) +
                   "], [SR " + str(curr.getData()[10]) + "]")
        elif opcode == 6:
            print(codesToLexemes[opcode] + "\t[SR " + str(curr.getData()[2]) + "], [SR " + str(curr.getData()[6]) +
                   "], [SR " + str(curr.getData()[10]) + "]")
        elif opcode == 7:
            print(codesToLexemes[opcode] + "\t[SR " + str(curr.getData()[2]) + "], [SR " + str(curr.getData()[6]) +
                   "], [SR " + str(curr.getData()[10]) + "]")
        # One operand
        elif opcode == 8:
            print(codesToLexemes[opcode] + "\t[SR " + str(curr.getData()[2]) + "], [ ], [ ]")
        # No operands
        elif opcode == 9:
            print(codesToLexemes[opcode] + "\t[ ], [ ], [ ]")
        curr = curr.getNext()


def add_node(head, tail, node):
    # Insert at the end of the list if list exists
    if tail != None:
        tail.next = node
        node.prev = tail
    else:
        head = node
    # Update the tail
    tail = node
    return node, head


def finish_arithop(start, line, stream, line_num, scanner: Scanner):
    # When parsing constants or registers, we will get the data back as (constant value, new index in string)

    # Register 1
    token, reg_data, lexeme = scanner.next_token(start, line, stream, line_num)
    if token != 5:
        return None
    else:
        r1 = reg_data[0]

    # Comma
    token, idx, lexeme = scanner.next_token(reg_data[1], line, stream, line_num)
    if token != 6:
        return None

    # Register 2
    token, reg_data, lexeme = scanner.next_token(idx, line, stream, line_num)
    if token != 5:
        return None
    else:
        r2 = reg_data[0]

    # INTO
    token, idx, lexeme = scanner.next_token(reg_data[1], line, stream, line_num)
    if token != 7:
        return None
    # Register 3
    token, reg_data, lexeme = scanner.next_token(idx, line, stream, line_num)
    if token != 5:
        return None
    else:
        r3 = reg_data[0]
    # EOL
    token, idx, lexeme = scanner.next_token(reg_data[1], line, stream, line_num)
    if token != 9:
        return None
    else:
        record = OP()
        record.getData()[0] = line_num
        record.getData()[2] = r1
        record.getData()[6] = r2
        record.getData()[10] = r3
        return record
    

def finish_memop(start, line, stream, line_num, scanner: Scanner):
    token, reg_data, lexeme = scanner.next_token(start, line, stream, line_num)
    if token != 5:
        return None
    else:
        r1 = reg_data[0]
    
    # INTO
    token, idx, lexeme = scanner.next_token(reg_data[1], line, stream, line_num)
    if token != 7:
        return None

    # Register 2
    token, reg_data, lexeme = scanner.next_token(idx, line, stream, line_num)
    if token != 5:
        return None
    else:
        r2 = reg_data[0]

    # EOL
    token, idx, lexeme = scanner.next_token(reg_data[1], line, stream, line_num)
    if token == 9:
        record = OP()
        record.getData()[0] = line_num
        record.getData()[2] = r1
        record.getData()[10] = r2
        return record
    else:
        return None



def finish_loadI(start, line, stream, line_num, scanner: Scanner):
    # CONSTANT
    token, const_data, constant = scanner.next_token(start, line, stream, line_num)
    if token != 10:
        return None

    # INTO
    token, idx, lexeme = scanner.next_token(const_data[1], line, stream, line_num)
    if token != 7:
        return None
    
    # Register 2
    token, reg_data, lexeme = scanner.next_token(idx, line, stream, line_num)
    if token != 5:
        return None
    else:
        r2 = reg_data[0]
    
    # EOL
    token, idx, lexeme = scanner.next_token(reg_data[1], line, stream, line_num)
    if token != 9:
        return None
    else:
        temp = OP()
        temp.getData()[0] = line_num
        temp.getData()[1] = 1
        temp.getData()[2] = constant
        temp.getData()[10] = r2
        return temp


def finish_output(start, line, stream, line_num, scanner: Scanner):
    # CONSTANT
    token, const_data, constant = scanner.next_token(start, line, stream, line_num)
    if token != 10:
        return None
    
    # EOL
    token, idx, lexeme = scanner.next_token(const_data[1], line, stream, line_num)
    if token != 9:
        return None
    else:
        temp = OP()
        temp.getData()[0] = line_num
        temp.getData()[2] = constant
        return temp


def finish_nop(start, line, stream, line_num, scanner: Scanner):
    token, idx, lexeme = scanner.next_token(start, line, stream, line_num)
    if token != 9:
        return None
    else:
        temp = OP()
        temp.getData()[0] = line_num
        return temp


def parseILOC(file, parse, stream, read, scanner: Scanner):
    error = False
    head = None
    tail = head
    line_num = 0
    num_ops = 0
    max_sr = 0
    while True:
        line = file.readline()
        line_num += 1
        if not line:
            break
        

        token, idx, lexeme = scanner.next_token(0, line, stream, line_num)
        if token == None:
            error_msg = f"ERROR {line_num}: line invalid"
            print(error_msg, file=sys.stderr)
            logger.error(error_msg)
            error = True
        else:
            # Record the new operation
            num_ops += 1

            if token == 0:
                node = finish_arithop(idx, line, stream, line_num, scanner)
                if not node:
                    print("ERROR ", line_num, ": line invalid", file=sys.stderr)
                    error = True
                    continue
                
                # Update the max SR number
                max_sr = max(max_sr, max(node.getData()[2], node.getData()[6], node.getData()[10]))
            elif token == 1:
                node = finish_memop(idx, line, stream, line_num, scanner)
                if not node:
                    print("ERROR ", line_num, ": line invalid", file=sys.stderr)
                    error = True
                    continue

                # Update the max SR number
                max_sr = max(max_sr, max(node.getData()[2], node.getData()[10]))
            elif token == 2:
                node = finish_loadI(idx, line, stream, line_num, scanner)
                if not node:
                    print("ERROR ", line_num, ": line invalid", file=sys.stderr)
                    error = True
                    continue
                # Update the max SR number
                max_sr = max(max_sr, node.getData()[10])
            elif token == 3:
                node = finish_output(idx, line, stream, line_num, scanner)
                if not node:
                    print("ERROR ", line_num, ": line invalid", file=sys.stderr)
                    error = True
                    continue
            elif token == 4:
                node = finish_nop(idx, line, stream, line_num, scanner)
                if not node:
                    print("ERROR ", line_num, ": line invalid", file=sys.stderr)
                    error = True
                    continue
            elif token == 9:
                # Comment: Not an operation
                num_ops -= 1

                continue
            else:
                print("ERROR ", line_num, ": line invalid", file=sys.stderr)
                error = True
                continue

            tail, head = add_node(head, tail, node)
            tail.getData()[1] = lexeme
    if parse:
        print("FAILURE") if error else print("SUCCESS")
    elif read:
        IR_toString(head)
    elif stream:
        print(str(line_num) + ": < ENDFILE, \"\" >")

    return head, tail, num_ops, max_sr