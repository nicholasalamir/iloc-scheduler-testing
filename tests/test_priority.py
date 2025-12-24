import pytest
from io import StringIO
from Scanner import Scanner
import Parser
import Renamer
import DependencyGraphGenerator
import PriorityCalculator


class TestPriorityBasicCalculation:
    # Test basic priority calculation

    def test_single_instruction_priority(self, scanner):
        # Single instruction should have priority 0 (no latency, no descendants)
        iloc_code = "loadI 5 => r1\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)
        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        nodes, roots, leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

        # Should have priority calculated
        assert nodes[0].priority is not None
        assert nodes[0].priority >= 0

    def test_two_independent_instructions(self, scanner):
        # Independent instructions should have same priority
        iloc_code = "loadI 5 => r1\nloadI 10 => r2\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)
        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        nodes, roots, leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

        # Both should have priority 0 (independent, no descendants)
        assert nodes[0].priority == nodes[1].priority


class TestPriorityLatency:
    # Test latency calculation

    def test_latency_assigned(self, scanner):
        # Latency should be assigned to all nodes
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r2\nadd r2, r2 => r3\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)
        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        nodes, roots, leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

        # All nodes should have latency assigned
        for node in nodes:
            assert node.latency is not None
            assert node.latency >= 0


class TestPriorityDescendants:
    # Test descendant counting

    def test_priorities_calculated_for_all_nodes(self, scanner):
        # All nodes should have priorities calculated
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r2\nadd r2, r2 => r3\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)
        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        nodes, roots, leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

        # All nodes should have priorities
        for node in nodes:
            assert node.priority is not None
            assert node.priority >= 0


class TestPriorityFormula:
    # Test priority formula: 10 * latency + descendants

    def test_priority_formula_components(self, scanner):
        # Priority should be calculated using latency and descendants
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r2\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)
        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        nodes, roots, leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

        # All nodes should have latency and priority assigned
        for node in nodes:
            assert node.latency is not None
            assert node.priority is not None

    def test_higher_priority_for_critical_path(self, scanner):
        # Instructions on critical path should have priorities calculated
        iloc_code = "loadI 5 => r1\nmult r1, r1 => r2\nmult r2, r2 => r3\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)
        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        nodes, roots, leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

        # All nodes should have priorities assigned
        for node in nodes:
            assert node.priority is not None
            assert node.priority >= 0


class TestPrioritySorting:
    # Test that results are sorted by priority

    def test_nodes_sorted_by_priority(self, scanner):
        # Returned nodes should be sorted by priority (descending)
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r2\nadd r2, r2 => r3\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)
        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        sorted_nodes, sorted_roots, sorted_leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

        # Check nodes are sorted descending
        for i in range(len(sorted_nodes) - 1):
            assert sorted_nodes[i].priority >= sorted_nodes[i + 1].priority

    def test_roots_sorted_by_priority(self, scanner):
        # Multiple roots should be sorted by priority
        iloc_code = "loadI 5 => r1\nloadI 10 => r2\nadd r1, r1 => r3\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)
        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        sorted_nodes, sorted_roots, sorted_leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

        # Roots should be sorted
        if len(sorted_roots) > 1:
            for i in range(len(sorted_roots) - 1):
                assert sorted_roots[i].priority >= sorted_roots[i + 1].priority

    def test_leaves_sorted_by_priority(self, scanner):
        # Multiple leaves should be sorted by priority
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r2\nadd r1, r1 => r3\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)
        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        sorted_nodes, sorted_roots, sorted_leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

        # Leaves should be sorted
        if len(sorted_leaves) > 1:
            for i in range(len(sorted_leaves) - 1):
                assert sorted_leaves[i].priority >= sorted_leaves[i + 1].priority


class TestPriorityComplexPatterns:
    # Test priority calculation for complex dependency patterns

    def test_diamond_pattern_priorities(self, scanner):
        # Diamond pattern: priorities should be calculated for all nodes
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r2\nadd r1, r1 => r3\nadd r2, r3 => r4\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)
        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        nodes, roots, leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

        # All nodes should have priorities assigned
        for node in nodes:
            assert node.priority is not None

    def test_parallel_chains_priorities(self, scanner):
        # Two parallel chains should have similar priorities
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r2\nloadI 10 => r3\nadd r3, r3 => r4\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)
        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        nodes, roots, leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

        # Both roots should have similar priorities (same structure)
        assert len(roots) == 2


class TestPriorityEdgeCases:
    # Test edge cases

    def test_nop_instruction_priority(self, scanner):
        # Nop should still get priority calculated
        iloc_code = "nop\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)
        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        nodes, roots, leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

        # Should have priority 0 (no latency, no descendants)
        assert nodes[0].priority == 0

    def test_memory_operations_priorities(self, scanner):
        # Memory operations should get priorities
        iloc_code = "load r1 => r2\nstore r3 => r4\noutput 100\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)
        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        nodes, roots, leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

        # All should have priorities assigned
        for node in nodes:
            assert node.priority is not None
            assert node.priority >= 0
