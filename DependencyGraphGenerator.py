from OP import OP
from Node import Node
# Create an empty map, M
# walk the block, top to bottom
#     at each operation o:
#         create a node for o
#         if o defines VRi :
#             set M(VRi ) to o
#         for each VRj used in o,
#             add an edge from o to the node in M(VRj)
#         if o is a load, store, or output operation,
#             add serial & conflict edges to other memory ops

"""
For reference, for an operation OP:
    -Index 0: Line number
    -Index 1: Opcode
    -Indices 2, 6, and 10: SRs 1, 2, and 3 (or constants for loadI and output)
    -Indices 3, 7, and 11: VRs 1, 2, and 3
    -Indices 4, 8, 12: PRs 1, 2, and 3
    -Indices 5, 9, 13: NUs 1, 2, and 3
"""
def generate_dependency_graph(head: OP):
    codesToLexemes = ["load", "loadI", "store", "add", "sub", "mult", "lshift", "rshift", "output", "nop"]
    operand_def_indices = {
        "load": [2], "loadI": [2], "store": [], "add": [2], "sub": [2], "mult": [2], "lshift": [2], "rshift": [2],
        "output": [], "nop": []
    }
    operand_use_indices = {
        "load": [0], "loadI": [], "store": [0, 2], "add": [0, 1], "sub": [0, 1], "mult": [0, 1], "lshift": [0, 1], "rshift": [0, 1],
        "output": [0], "nop": []
    }

    # Maps virtual registers to the operation that defines them
    M = {}
    # Keeps track of important previous operations for conflict and serialization edges
    mostRecentStore = None
    mostRecentOutput = None
    previousLoadsAndOutputs = []

    # Start of the DOT file
    dot_lines = ["digraph G {", "node [shape=box];"]  # Set the shape of nodes

    nodes = []
    current_OP = head
    while current_OP:
        node = Node(current_OP)
        lexeme = codesToLexemes[current_OP.getData()[1]]

        # If the OP defines a VR then add that to M to keep track of for any future OPs that need to use it (dependency)
        for operand_index in operand_def_indices[lexeme]:
            vr = current_OP.getData()[4 * operand_index + 3]
            M[vr] = node

        # If the OP uses any VRs make sure to add an edge to track those dependencies
        for operand_index in operand_use_indices[lexeme]:
            vr = current_OP.getData()[4 * operand_index + 3]
            if vr in M:
                node.setNewChild(M[vr], "Data", f'r{vr}')
                M[vr].setNewParent(node)

        # OP is a load, store, or output: serialization and conflict edges
        if lexeme in ["load", "output"]:
            if mostRecentStore and mostRecentStore not in node.getChildren():
                node.setNewChild(mostRecentStore, "Conflict")
                mostRecentStore.setNewParent(node)
        if lexeme == "output":
            if mostRecentOutput and mostRecentOutput not in node.getChildren():
                node.setNewChild(mostRecentOutput, "Serial")
                mostRecentOutput.setNewParent(node)
        if lexeme == "store":
            if mostRecentStore and mostRecentStore not in node.getChildren():
                node.setNewChild(mostRecentStore, "Serial")
                mostRecentStore.setNewParent(node)
            for loadOrOutput in previousLoadsAndOutputs:
                if loadOrOutput not in node.getChildren():
                    node.setNewChild(loadOrOutput, "Serial")
                    loadOrOutput.setNewParent(node)

        # Update any of the important operation records
        if lexeme == "store":
            mostRecentStore = node
        if lexeme == "output":
            mostRecentOutput = node
        if lexeme in ["load", "output"]:
            previousLoadsAndOutputs.append(node)

        nodes.append(node)
        # Move on to the next operation
        current_OP = current_OP.getNext()


    # Add nodes and edges to dot_lines
    # for node in nodes:
    #     op_label = node.getOPLabel()
    #     dot_lines.append(f'{op_label} [label={op_label}];')
    #     for child in node.getChildren():
    #         child_label = child.getOPLabel()
    #         edge_info = node.getEdge(child)
    #         edge_type = edge_info["edgeType"]
    #         edge_dependency = edge_info["edgeDependency"]
    #         # Format the edge label based on the edge type and dependency
    #         edge_label = edge_type
    #         if edge_type == "Data":
    #             edge_label += f', {edge_dependency}'
    #         dot_lines.append(f'{op_label} -> {child_label} [label="{edge_label}"];')

    # # End of the DOT file
    # dot_lines.append("}")

    # # Write the DOT lines to a file
    # with open('graph.dot', 'w') as file:
    #     file.writelines(line + "\n" for line in dot_lines)
    
    # Find roots
    roots = [node for node in nodes if len(node.getParents()) == 0]
    # Find leaves
    leaves = [node for node in nodes if len(node.getChildren()) == 0]
    
    return nodes, roots, leaves

# def generate_dependency_graph(head: OP):
#     # Map opcode to the indices in the IR that store definitions and uses
#     codesToLexemes = ["load", "loadI", "store", "add",
#                       "sub", "mult", "lshift", "rshift", "output", "nop"]
#     operand_def_indices = {"load": [2], "loadI": [2], "store": [], "add": [2], "sub": [2], "mult": [2], "lshift": [2], "rshift": [2],
#                            "output": [], "nop": []}
#     operand_use_indices = {"load": [0], "loadI": [], "store": [0, 2], "add": [0, 1], "sub": [0, 1], "mult": [0, 1], "lshift": [0, 1], "rshift": [0, 1],
#                            "output": [], "nop": []}
#     OP = head

#     # Go through each operation in the ILOC block, top-to-bottom
#     # Maps virtual registers to the operation that defines them
#     M = {}

#     # Keeps track of important previous operations for conflict and serialization edges
#     mostRecentStore = None
#     mostRecentOutput = None
#     previousLoadsAndOutputs = []

#     while OP:
#         # Create a node for OP (node stores the line number)
#         node = Node(OP)

#         # If the OP defines a VR then add that to M to keep track of for any future OPs that need to use it (dependency)
#         lexeme = codesToLexemes[OP.getData()[1]]
#         for operand_index in operand_def_indices[lexeme]:
#             vr = OP.getData()[4 * operand_index + 3]
#             M[vr]: dict[int, OP] = node
        
#         # If the OP uses any VRs make sure to add an edge to track those dependencies
#         for operand_index in operand_use_indices[lexeme]:
#             vr = OP.getData()[4 * operand_index + 3]
#             node.setNewChild(M[vr])
#             M[vr].setNewParent(node)
        
#         # OP is a load, store, or output: serialization and conflict edges
#         if lexeme == "load" or lexeme == "output":
#             # Needs a conflict edge to the most recent store
#             node.setNewChild(mostRecentStore)
#             if mostRecentStore:
#                 mostRecentStore.setNewParent(node)
#         if lexeme == "output":
#             # Needs a serialization edge to the most recent output
#             node.setNewChild(mostRecentOutput)
#             if mostRecentOutput:
#                 mostRecentOutput.setNewParent(node)
#         if lexeme == "store":
#             # Needs a sereialization edge to the most recent store
#             node.setNewChild(mostRecentStore)
#             if mostRecentStore:
#                 mostRecentStore.setNewParent(node)
#             # Needs serializatione edges to all previous loads and outputs
#             for loadOrOutput in previousLoadsAndOutputs:
#                 node.setNewChild(loadOrOutput)
#                 loadOrOutput.setNewParent(node)
            
#         # Update any of the important operation records
#         if lexeme == "store":
#             mostRecentStore = node
#         if lexeme == "output":
#             mostRecentOutput = node
#         if lexeme == "load" or lexeme == "output":
#             previousLoadsAndOutputs.append(node)
        
#         # Move on to the next operation
#         OP = OP.getNext()


