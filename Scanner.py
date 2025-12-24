class Scanner:
    def scan_constant(self, start, line):
        idx = start
        num = 0
        try:
            if not ("0" <= line[idx] <= "9"):
                return (None, None)
            else:
                while idx < len(line) and "0" <= line[idx] <= "9":
                    num = num * 10 + int(line[idx])
                    idx += 1
            return (num, idx)
        except IndexError:
            return (None, None)
    
    # Return both lexeme and category as integers
    def next_token(self, start_idx, line, stream, line_num):
        idx = int(start_idx)
        try:
            # Skip whitespace
            while line[idx] == " " or line[idx] == "\t":
                idx += 1
            
            # End of line (go to the next line)
            if line[idx] == "\n":
                if stream:
                    print(str(line_num) + ": < NEWLINE, \"\\n\" >")
                return 9, None, None
            
            
            # A comment is ignored and will terminate with EOL
            if line[idx] == "/":
                if line[idx + 1] == "/":
                    if stream:
                        print(str(line_num) + ": < NEWLINE, \"\\n\" >")
                    return 9, None, None
                
            
            if line[idx] == "s":
                # ARITHOP (must be sub)
                if line[idx + 1] == "u":
                    if line[idx + 2] == "b":
                        if stream:
                            print(str(line_num) + ": < ARITHOP, \"sub\" >")
                        return 0, idx + 3, 4
                    else:
                        return None, None, None
                # MEMOP (must be store)
                elif line[idx + 1] == "t":
                    if line[idx + 2] == "o":
                        if line[idx + 3] == "r":
                            if line[idx + 4] == "e":
                                if stream:
                                    print(str(line_num)+ ": < MEMOP, \"store\" >")
                                return 1, idx + 5, 2
                            else:
                                return None, None, None
                        else:
                            return None, None, None
                    else:
                        return None, None, None
                else:
                    return None, None, None
            elif line[idx] == "l":
                if line[idx + 1] == "o":
                    if line[idx + 2] == "a":
                        if line[idx + 3] == "d":
                            # LOADI
                            if line[idx + 4] == "I":
                                if stream:
                                    print(str(line_num) + ": < LOADI, \"loadI\" >")
                                return 2, idx + 5, 1
                            
                            # MEMOP (load)
                            else:
                                if stream:
                                    print(str(line_num) + ": < MEMOP, \"load\" >")
                                return 1, idx + 4, 0
                            
                        else:
                            return None, None, None
                    else:
                        return None, None, None
                # ARITHOP (lshift)
                elif line[idx + 1] == "s":
                    if line[idx + 2] == "h":
                        if line[idx + 3] == "i":
                            if line[idx + 4] == "f":
                                if line[idx + 5] == "t":
                                    if stream:
                                        print(str(line_num) + ": < ARITHOP, \"lshift\" >")
                                    return 0, idx + 6, 6
                                else:
                                    return None, None, None
                            else:
                                return None, None, None
                        else:
                            return None, None, None
                    else:
                        return None, None, None
                else:
                    return None, None, None
            # ARITHOP (rshift)
            elif line[idx] == "r":
                if line[idx + 1] == "s":
                    if line[idx + 2] == "h":
                        if line[idx + 3] == "i":
                            if line[idx + 4] == "f":
                                if line[idx + 5] == "t":
                                    if stream:
                                        print(str(line_num) + ": < ARITHOP, \"rshift\" >")
                                    return 0, idx + 6, 7
                                else:
                                    return None, None, None
                            else:
                                return None, None, None
                        else:
                            return None, None, None
                    else:
                        return None, None, None
                # REGISTER
                else:
                    res = self.scan_constant(idx + 1, line)
                    if res[0] == None:
                        return None, None, None
                    else:
                        if stream:
                            print(str(line_num) + ": < REG, \"r"+ str(res[0]) + "\" >")
                        return 5, res, None
            # ARITHOP (mult)
            elif line[idx] == "m":
                if line[idx + 1] == "u":
                    if line[idx + 2] == "l":
                        if line[idx + 3] == "t":
                            if stream:
                                print(str(line_num) + ": < ARITHOP, \"mult\" >")
                            return 0, idx + 4, 5
                        else:
                            return None, None, None
                    else:
                        return None, None, None
                else:
                    return None, None, None
            # ARITHOP (add)
            elif line[idx] == "a":
                if line[idx + 1] == "d":
                    if line[idx + 2] == "d":
                        if stream:
                            print(str(line_num) + ": < ARITHOP, \"add\" >")
                        return 0, idx + 3, 3
                    else:
                        return None, None, None
                else:
                    return None, None, None
            # INTO
            elif line[idx] == "=":
                if line[idx + 1] == ">":
                    if stream:
                        print(str(line_num) + ": < INTO, \"=>\" >")
                    return 7, idx + 2, None
            # COMMA
            elif line[idx] == ",":
                return 6, idx + 1, None
            # NOP
            elif line[idx] == "n":
                if line[idx + 1] == "o":
                    if line[idx + 2] == "p":
                        if stream:
                            print(str(line_num) + ": < NOP, \"nop\" >")
                        return 4, idx + 3, 9
                    else:
                        return None, None, None
                else:
                    return None, None, None
            # OUTPUT
            elif line[idx] == "o":
                if line[idx + 1] == "u":
                    if line[idx + 2] == "t":
                        if line[idx + 3] == "p":
                            if line[idx + 4] == "u":
                                if line[idx + 5] == "t":
                                    if stream:
                                        print(str(line_num) + ": < OUTPUT, \"output\" >")
                                    return 3, idx + 6, 8
                                else:
                                    return None, None, None
                            else:
                                return None, None, None
                        else:
                            return None, None, None
                    else:
                        return None, None, None
                else:
                    return None, None, None
            # CONSTANT
            elif "0" <= line[idx] <= "9":
                res = self.scan_constant(idx, line)
                if res != (None, None):
                    if stream:
                        print(str(line_num) + ": < CONSTANT, \"", res[0], "\" >")
                return 10, res, res[0]
            # Implicit catch-all for error state
            else:
                return None, None, None
        # Out of characters in line; cannot scan over lines, must be in error state
        except IndexError:
            if stream:
                print(str(line_num) + ": < NEWLINE, \"\\n\" >")
            return 10, None, None



