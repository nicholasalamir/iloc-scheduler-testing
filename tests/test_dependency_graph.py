import pytest
from io import StringIO
from Scanner import Scanner
import Parser
import Renamer
import DependencyGraphGenerator


class TestDependencyGraphBasic:
    # Test basic dependency graph creation

    def test_single_instruction_is_root_and_leaf(self, scanner):
        # Single instruction should be both root and leaf
        iloc_code = "loadI 5 => r1\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)

        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        assert len(nodes) == 1
        assert len(roots) == 1  # No dependencies, so it's a root
        assert len(leaves) == 1  # No dependents, so it's a leaf
        assert roots[0] == leaves[0]

    def test_two_independent_instructions(self, scanner):
        # Two independent loadI operations
        iloc_code = "loadI 5 => r1\nloadI 10 => r2\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)

        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        assert len(nodes) == 2
        assert len(roots) == 2  # Both are roots (independent)
        assert len(leaves) == 2  # Both are leaves (no dependents)


class TestDependencyGraphDataDependencies:
    # Test data dependency edge creation

    def test_simple_data_dependency(self, scanner):
        # r1 defined then used - creates data dependency
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r2\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)

        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        assert len(nodes) == 2
        assert len(roots) == 1  # Only loadI is root
        assert len(leaves) == 1  # Only add is leaf

        # Add should have loadI as child (dependency)
        add_node = nodes[1]
        assert len(add_node.getChildren()) > 0

    def test_chain_of_dependencies(self, scanner):
        # Three instructions with chain of dependencies
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r2\nadd r2, r2 => r3\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)

        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        assert len(nodes) == 3
        assert len(roots) == 1  # Only first loadI is root
        assert len(leaves) == 1  # Only last add is leaf

    def test_multiple_uses_of_same_register(self, scanner):
        # r1 used by multiple instructions
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r2\nadd r1, r2 => r3\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)

        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        assert len(nodes) == 3
        assert len(roots) == 1  # loadI is only root
        # Both adds depend on loadI


class TestDependencyGraphMemoryOperations:
    # Test serial and conflict edges for memory operations

    def test_store_serial_dependency(self, scanner):
        # Two stores should have serial edge
        iloc_code = "store r1 => r2\nstore r3 => r4\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)

        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        # Second store should depend on first store
        second_store = nodes[1]
        assert len(second_store.getChildren()) > 0  # Has serial edge

    def test_load_store_conflict(self, scanner):
        # Load after store should have conflict edge
        iloc_code = "store r1 => r2\nload r3 => r4\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)

        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        # Load should have conflict edge to store
        load_node = nodes[1]
        assert len(load_node.getChildren()) > 0

    def test_output_serial_dependency(self, scanner):
        # Two outputs should have serial edge
        iloc_code = "output 100\noutput 200\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)

        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        # Second output should depend on first
        second_output = nodes[1]
        assert len(second_output.getChildren()) > 0

    def test_store_after_load(self, scanner):
        # Store after load should have serial edge
        iloc_code = "load r1 => r2\nstore r3 => r4\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)

        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        # Store should have serial edge to load
        store_node = nodes[1]
        assert len(store_node.getChildren()) > 0


class TestDependencyGraphRootsAndLeaves:
    # Test correct identification of roots and leaves

    def test_roots_have_no_parents(self, scanner):
        # All roots should have no parents
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r2\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)

        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        for root in roots:
            assert len(root.getParents()) == 0

    def test_leaves_have_no_children(self, scanner):
        # All leaves should have no children
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r2\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)

        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        for leaf in leaves:
            assert len(leaf.getChildren()) == 0

    def test_parallel_operations_multiple_roots(self, scanner):
        # Independent operations should all be roots
        iloc_code = "loadI 1 => r1\nloadI 2 => r2\nloadI 3 => r3\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)

        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        # All three should be roots (independent)
        assert len(roots) == 3


class TestDependencyGraphComplexPatterns:
    # Test complex dependency patterns

    def test_diamond_dependency(self, scanner):
        # Diamond pattern: one defines, two use, one combines
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r2\nadd r1, r1 => r3\nadd r2, r3 => r4\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)

        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        assert len(nodes) == 4
        assert len(roots) == 1  # Only loadI
        assert len(leaves) == 1  # Only final add

    def test_mixed_data_and_serial_dependencies(self, scanner):
        # Mix of data and serial dependencies
        iloc_code = "loadI 5 => r1\nstore r1 => r2\nload r2 => r3\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)

        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        # Load should have both data and conflict dependencies
        load_node = nodes[2]
        assert len(load_node.getChildren()) > 0


class TestDependencyGraphEdgeCases:
    # Test edge cases

    def test_nop_instruction(self, scanner):
        # Nop has no dependencies
        iloc_code = "nop\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)

        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        assert len(nodes) == 1
        assert len(roots) == 1
        assert len(leaves) == 1

    def test_all_arithmetic_operations(self, scanner):
        # Test all arithmetic operation types - just verify they all work
        iloc_code = "loadI 1 => r1\nloadI 2 => r2\nadd r1, r2 => r3\nsub r1, r2 => r4\nmult r1, r2 => r5\nlshift r1, r2 => r6\nrshift r1, r2 => r7\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)

        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        # All 7 instructions should create nodes
        assert len(nodes) == 7
        # Should have at least 1 root and 1 leaf
        assert len(roots) >= 1
        assert len(leaves) >= 1
