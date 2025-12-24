# #!/usr/bin/python -u

import argparse
import sys
import Parser
from Scanner import Scanner
import Renamer
# from Allocator import Allocator
import print_ILOC_block
import DependencyGraphGenerator
import PriorityCalculator
import Scheduler

def main():
    # Store and check for filename
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="a valid Linux pathname relative to the current working directory which contains the input file")
    args = parser.parse_args()

    if not args.name:
        print("ERROR: Input file not provided", file=sys.stderr)
        return
    else:
        try:
            file = open(args.name, "r", encoding="utf-8")
        except Exception:
            print("ERROR: could not open the provided file.", file=sys.stderr)
            return
        
        # Instantiate the scanner and pass it around for use
        scanner = Scanner()
        # Begin parsing the file and build the IR
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        # Rename the ILOC block and print to stdout
        # max_vr, maxLive = Renamer.renaming(tail, num_ops, max_sr)
        Renamer.renaming(tail, num_ops, max_sr)

        # Print the renamed block to stdout
        # print_ILOC_block.print_ILOC_block(head)

        # LAB 3 NEW CODE! ////////////////////////////////////////////////////////////////////
        
        # Generate the dependence graph
        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        # Calculate priorities
        prioritized_nodes, prioritized_roots, prioritized_leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)
        # for node in prioritized_nodes:
        #     print(node.formatOP() + " Latency: " + str(node.latency) + " Priority: " + str(node.priority))

        # Schedule the code
        Scheduler.schedule(prioritized_nodes, prioritized_roots, prioritized_leaves)

        file.close()

if __name__ == "__main__":
    main()
