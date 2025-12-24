from OP import OP

def renaming(IR: OP, num_ops, max_sr):
    """
    IR: The tail of the intermediate representation (structured as a doubly-linked list).
    num_ops: Number of operations.
    max_sr: The greatest value of a register in the ILOC block.

    For reference, for an operation in the IR OP:
        -Index 0: Line number
        -Index 1: Opcode
        -Indices 2, 6, and 10: SRs 1, 2, and 3 (or constants for loadI and output)
        -Indices 3, 7, and 11: VRs 1, 2, and 3
        -Indices 4, 8, 12: PRs 1, 2, and 3
        -Indices 5, 9, 13: NUs 1, 2, and 3
    """
    VRName = 0
    SRToVR = {}
    LU = {}

    # Initialization
    for i in range(0, max_sr + 1):
        SRToVR[i] = -1
        LU[i] = float("inf")

    index = num_ops - 1

    # Traverse the block bottom-to-top
    OP = IR
    # Map opcode to the indices in the IR that store definitions and uses
    codesToLexemes = ["load", "loadI", "store", "add", "sub", "mult", "lshift", "rshift", "output", "nop"]
    operand_def_indices = {"load": [2], "loadI": [2], "store": [], "add": [2], "sub": [2], "mult": [2], "lshift": [2], "rshift": [2], 
                           "output": [], "nop": []}
    operand_use_indices = {"load": [0], "loadI": [], "store": [0, 2], "add": [0, 1], "sub": [0, 1], "mult": [0, 1], "lshift": [0, 1], "rshift": [0, 1], 
                           "output": [], "nop": []}
    currLive = 0
    maxLive = 0
    maxVR = 0
    while OP != None:
        # Go through each operand of OP that OP defines
        lexeme = codesToLexemes[OP.getData()[1]]
        for operand_index in operand_def_indices[lexeme]:
            # Get the operand source register by calculating offset
            sr = OP.getData()[4 * operand_index + 2]
            # Unused DEF
            if SRToVR[sr] == -1:
                SRToVR[sr] = VRName
                # Increment VRName and currLive
                VRName += 1
                maxVR = VRName
                currLive += 1
            # Already used below this line; record in IR
            # VR
            OP.getData()[4 * operand_index + 3] = SRToVR[sr]
            # NU
            OP.getData()[4 * operand_index + 5] = LU[sr]
            # Kill the operand
            SRToVR[sr] = -1
            LU[sr] = float("inf")
            currLive -= 1
        for operand_index in operand_use_indices[lexeme]:
            # Get the operand source register by calculating offset
            sr = OP.getData()[4 * operand_index + 2]
            # Last USE
            if SRToVR[sr] == -1:
                SRToVR[sr] = VRName
                # Increment VRName
                VRName += 1
                maxVR = VRName - 1
                currLive += 1
            # VR
            OP.getData()[4 * operand_index + 3] = SRToVR[sr]
            # NU
            OP.getData()[4 * operand_index + 5] = LU[sr]
            # Set LU
            LU[sr] = index
        # print("OP ", index, "in renamer: ", OP.getData())

        # Check maxLive
        maxLive = max(maxLive, currLive)
        # Move up a line
        index -= 1
        OP = OP.getPrev()

    # return maxVR, maxLive


