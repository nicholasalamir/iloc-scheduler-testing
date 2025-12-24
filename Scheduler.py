from Node import Node
from OP import OP
import heapq
import logging

# Configure logging (disabled by default, enable via logging.basicConfig)
logger = logging.getLogger(__name__)


def schedule(nodes, roots, leaves, debug=False):
    # print([leaf.formatOP() for leaf in leaves])
    '''
    nodes, roots, and leaves are sorted in descending order of priority.
    '''
    # Instrumentation: Track statistics
    total_instructions = len(nodes)
    instructions_scheduled = 0
    logger.info(f"Starting scheduling for {total_instructions} instructions")

    # print("INSTRUCTIONS TO SCHEDULE", len(nodes))
    cycle = 1
    ready = leaves[:]  # Create a heap with negative priorities
    for node in ready:
        node.ready = True
    heapq.heapify(ready)  # Transform list into a heap, in-place
    active = set()

    # Assertion: All leaves should be ready initially
    assert all(node.ready for node in leaves), "All leaf nodes must be ready at start"

    while ready or active:
        # print("READY SET: ", [node.formatOP() for node in ready])
        # print("READY SET: ", [node.formatOP() for node in ready])
        # print("ACTIVE SET: ", [active_op[0].formatOP() for active_op in active])
        instruction = "[ "
        operations = ["nop", "nop"]

        # Flags to indicate if a functional unit has been scheduled
        scheduled_on_f0 = False
        scheduled_on_f1 = False
        output_scheduled = False

        # Hold onto ops that are priority but can't be scheduled (like necessary functional unit taken)
        nodes_to_reready = set()
        # Pick an operation for each of the functional units
        while ready:
            if scheduled_on_f0 and scheduled_on_f1:
                # Both functional units have been scheduled, can exit the loop
                break
            # print("READY BEFORE SCHEDULING: ", [node.formatOP() for node in ready])
            # Pop the node with the highest priority
            node = heapq.heappop(ready)
            scheduled = False

            op_code = node.OP.getData()[1]
            formatted_op = node.formatOP()

            # Check constraints for functional units and schedule operations
            if op_code in [0, 2] and not scheduled_on_f0:  # load and store only on f0
                operations[0] = formatted_op
                scheduled_on_f0 = True
                active.add((node, cycle + 5))
                scheduled = True
                instructions_scheduled += 1
                logger.debug(f"Cycle {cycle}: Scheduled {formatted_op} on f0")
            elif op_code == 5 and not scheduled_on_f1:  # mult only on f1
                operations[1] = formatted_op
                scheduled_on_f1 = True
                active.add((node, cycle + 3))
                scheduled = True
            elif op_code == 8 and not output_scheduled:  # only one output per cycle
                if not scheduled_on_f1:
                    operations[1] = formatted_op
                    scheduled_on_f1 = True
                    output_scheduled = True
                    active.add((node, cycle + 1))
                    scheduled = True
                elif not scheduled_on_f0:   
                    operations[0] = formatted_op
                    scheduled_on_f0 = True
                    output_scheduled = True
                    active.add((node, cycle + 1))
                    scheduled = True
                output_scheduled = True
            elif op_code in [1, 3, 4, 6, 7]:  # other operations on any functional unit
                if not scheduled_on_f1:
                    operations[1] = formatted_op
                    scheduled_on_f1 = True
                    active.add((node, cycle + 1))
                    scheduled = True
                elif not scheduled_on_f0:
                    operations[0] = formatted_op
                    scheduled_on_f0 = True
                    active.add((node, cycle + 1))
                    scheduled = True
            # We are ignoring nops (op_code == 9)

            if not scheduled:
                nodes_to_reready.add(node)
        
        # Re-ready nodes that were pulled out but not scheduled
        for node in nodes_to_reready:
            heapq.heappush(ready, node)

        # Remove operations from Active that retire
        to_remove_from_active = set()
        for active_op in active:
            node, finish_cycle = active_op[0], active_op[1]
            if finish_cycle <= cycle + 1:
                to_remove_from_active.add(active_op)
                node.finished = True
        for active_op in to_remove_from_active:
            node, finish_cycle = active_op[0], active_op[1]
            for dependent in node.getParents():
                can_add_to_ready = True
                # Check if dependent is ready (all dependencies fulfilled)
                for depender in dependent.getChildren():
                    if not depender.finished:
                        can_add_to_ready = False
                        break
                if can_add_to_ready and not dependent.ready:
                    dependent.ready = True
                    heapq.heappush(ready, dependent)
        active = active.difference(to_remove_from_active)
        # print("ACTIVE AFTER RETIRING: ", [node[0].formatOP() for node in active])

        # Check for early releases 
        # print("ACTIVE SET EARLY RELEASE: ", [active_op[0].formatOP() for active_op in active])
        # print("READY SET EARLY RELEASE" , [node.formatOP() for node in ready])
        for active_op in active:
            node = active_op[0]
            op_code = node.OP.getData()[1]
            # codesToLexemes = ["load", "loadI", "store", "add", "sub", "mult", "lshift", "rshift", "output", "nop"]
            # Multi-cycle operation
            # if op_code in [0, 2, 5] and not node.ready
            if op_code in [0, 2]:
                # print("ACTIVE OP: ", node.formatOP())
                for dependent in node.getParents():
                    if not dependent.ready and dependent.getEdge(node)["edgeType"] == "Serial":
                        # print("DEPENDENT UNDER CONSIDERATION: ", dependent.formatOP())
                        can_add_to_ready = True
                        # Check if all data and serial constraints are satisfied
                        for child in dependent.getChildren():
                            if child != node:
                                if not child.finished:
                                    can_add_to_ready = False
                                    break
                        if can_add_to_ready:
                            # print("ADDING DEPENDENT", dependent.formatOP())
                            dependent.ready = True
                            # print("ADDING THIS OP TO READY SET DUE TO EARLY RELEASE: ", dependent.formatOP())
                            heapq.heappush(ready, dependent)


                


        # Add the scheduled operations to the instruction
        instruction += " ; ".join(operations) + " ]"
        print(instruction)

        # Increment the cycle counter
        cycle += 1

    # Instrumentation: Log final statistics
    final_cycle = cycle - 1
    logger.info(f"Scheduling complete: {total_instructions} instructions in {final_cycle} cycles")

    # Assertion: All nodes should be finished
    assert all(node.finished for node in nodes), "All nodes must be finished after scheduling"

    # print("INSTRUCTIONS SCHEDULED: ", len([node for node in nodes if node.finished]))

    # Return cycle count for testing purposes
    return final_cycle
