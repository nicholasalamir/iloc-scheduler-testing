from OP import OP

class Node:
    def __init__(self, OP):
        self.OP = OP
        self.children = set()
        self.parents = set()
        # Maps children ID to edgeType ("Data", "Serial", "Conflict") and potentially VR dependency ("" for serial and conflict)
        self.edges = {}
        self.latency = 0
        self.priority = 0
        self.finished = False
        self.ready = False

    def setNewChild(self, node, edgeType, edgeDependency = ""):
        self.children.add(node)
        self.edges[node.getOPNum()] = {"edgeType": edgeType, "edgeDependency": edgeDependency}
    def getEdge(self, node):
        return self.edges[node.getOPNum()]
    def getEdgeLatency(self, node):
        # codesToLexemes = ["load", "loadI", "store", "add", "sub", "mult", "lshift", "rshift", "output", "nop"]
        edge = self.getEdge(node)
        opcode_idx = self.OP.getData()[1]
        if edge["edgeType"] == "Serial":
            return 1
        elif opcode_idx == 0 or opcode_idx == 2:
            return 5
        elif opcode_idx == 5:
            return 3
        else:
            return 1

    def getChildren(self):
        return self.children
    def setNewParent(self, node):
        self.parents.add(node)
    def getParents(self):
        return self.parents
    
    def getOPNum(self):
        return self.OP.getData()[0]

    def formatOP(self):
        return format_ILOC_operation(self.OP)
    def getOPLabel(self):
        # Assuming the operation label is a unique string representation of the operation
        formatted_op = self.formatOP().replace('"', '\\"')
        return f'"{formatted_op}"'
    def __lt__(self, other):
        return self.priority > other.priority

def format_ILOC_operation(op: OP) -> str:
    codesToLexemes = ["load", "loadI", "store", "add", "sub", "mult", "lshift", "rshift", "output", "nop"]
    opcode_idx = op.getData()[1]
    op_data = op.getData()
    formatted_str = ""

    if opcode_idx == 0:
        formatted_str = f"load r{op_data[3]} => r{op_data[11]}"
    elif opcode_idx == 1:
        formatted_str = f"loadI {op_data[2]} => r{op_data[11]}"
    elif opcode_idx == 2:
        formatted_str = f"store r{op_data[3]} => r{op_data[11]}"
    elif opcode_idx == 3:
        formatted_str = f"add r{op_data[3]}, r{op_data[7]} => r{op_data[11]}"
    elif opcode_idx == 4:
        formatted_str = f"sub r{op_data[3]}, r{op_data[7]} => r{op_data[11]}"
    elif opcode_idx == 5:
        formatted_str = f"mult r{op_data[3]}, r{op_data[7]} => r{op_data[11]}"
    elif opcode_idx == 6:
        formatted_str = f"lshift r{op_data[3]}, r{op_data[7]} => r{op_data[11]}"
    elif opcode_idx == 7:
        formatted_str = f"rshift r{op_data[3]}, r{op_data[7]} => r{op_data[11]}"
    elif opcode_idx == 8:
        formatted_str = f"output {op_data[2]}"
    elif opcode_idx == 9:
        formatted_str = "nop"

    return formatted_str
