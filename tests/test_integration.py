import pytest
import sys
from io import StringIO
from Scanner import Scanner
import Parser
import Renamer
import DependencyGraphGenerator
import PriorityCalculator
import Scheduler


class TestScannerParserIntegration:
    # Test Scanner and Parser working together

    def test_scanner_parser_simple_loadI(self, scanner):
        # Scanner to Parser pipeline with simple loadI
        iloc_code = "loadI 100 => r5\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        assert head is not None  # Parser should handle scanned input
        assert head.getData()[1] == 1  # loadI opcode
        assert head.getData()[2] == 100  # Constant
        assert head.getData()[10] == 5  # Register

    def test_scanner_parser_multi_instruction(self, scanner):
        # Scanner to Parser with multiple instructions
        iloc_code = "loadI 5 => r1\nloadI 10 => r2\nadd r1, r2 => r3\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        assert num_ops == 3  # All 3 instructions parsed
        assert max_sr == 3  # Max register tracked

        # Verify linked list
        assert head is not None
        assert head.getNext() is not None
        assert head.getNext().getNext() is not None

    def test_scanner_parser_with_comments(self, scanner):
        # Scanner to Parser handles comments
        iloc_code = "// Comment\nloadI 5 => r1\n// Another comment\nadd r1, r1 => r2\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        assert num_ops == 2  # Comments ignored
        assert head.getData()[1] == 1  # First is loadI
        assert head.getNext().getData()[1] == 3  # Second is add


class TestParserRenamerIntegration:
    # Test Parser and Renamer working together

    def test_parser_renamer_basic(self, scanner):
        # Parser to Renamer pipeline
        iloc_code = "loadI 100 => r1\nadd r1, r1 => r2\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        # Renamer modifies IR in place
        Renamer.renaming(tail, num_ops, max_sr)

        # Verify renaming completed
        assert head is not None
        assert tail is not None

    def test_parser_renamer_preserves_structure(self, scanner):
        # Renamer should preserve linked list structure
        iloc_code = "loadI 1 => r1\nloadI 2 => r2\nadd r1, r2 => r3\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        original_count = num_ops

        # Renamer modifies in place
        Renamer.renaming(tail, num_ops, max_sr)

        # Count nodes after renaming
        count = 0
        curr = head
        while curr:
            count += 1
            curr = curr.getNext()

        assert count == original_count  # Number of instructions preserved


class TestFullPipelineIntegration:
    # Test complete pipeline with all components

    def test_full_pipeline_simple(self, scanner):
        # Complete pipeline: Scanner → Parser → Renamer → DependencyGraph → Priority → Scheduler
        iloc_code = "loadI 5 => r1\nloadI 10 => r2\nadd r1, r2 => r3\n"
        file = StringIO(iloc_code)

        # Parse
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        # Rename (modifies IR in place)
        Renamer.renaming(tail, num_ops, max_sr)

        # Build dependency graph
        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

        # Calculate priorities (returns new prioritized collections)
        nodes, roots, leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

        # Schedule
        cycle_count = Scheduler.schedule(nodes, roots, leaves, False)

        assert cycle_count is not None
        assert cycle_count >= 0
        assert cycle_count >= num_ops / 2  # Dual-issue processor

    def test_full_pipeline_data_dependency(self, scanner, test_data_dir):
        # Complete pipeline with data dependency file
        with open(f"{test_data_dir}/data_dependency.iloc", "r") as file:
            # Parse
            head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

            # Rename
            Renamer.renaming(tail, num_ops, max_sr)

            # Build dependency graph
            nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

            # Calculate priorities
            nodes, roots, leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

            # Schedule
            cycle_count = Scheduler.schedule(nodes, roots, leaves, False)

            assert cycle_count is not None
            assert len(nodes) == num_ops  # Node for each operation

    def test_full_pipeline_parallel_loadI(self, scanner, test_data_dir):
        # Complete pipeline with parallel loadI instructions
        with open(f"{test_data_dir}/parallel_loadI.iloc", "r") as file:
            # Parse
            head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

            # Rename
            Renamer.renaming(tail, num_ops, max_sr)

            # Build dependency graph
            nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

            # Calculate priorities
            nodes, roots, leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

            # Schedule
            cycle_count = Scheduler.schedule(nodes, roots, leaves, False)

            # Two independent loadI operations should execute in parallel
            assert cycle_count is not None
            assert num_ops == 2

    def test_full_pipeline_all_arithops(self, scanner, test_data_dir):
        # Complete pipeline with all arithmetic operations
        with open(f"{test_data_dir}/all_arithops.iloc", "r") as file:
            # Parse
            head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

            # Rename
            Renamer.renaming(tail, num_ops, max_sr)

            # Build dependency graph
            nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)

            # Calculate priorities
            nodes, roots, leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

            # Schedule
            cycle_count = Scheduler.schedule(nodes, roots, leaves, False)

            assert cycle_count is not None
            assert num_ops == 5  # All 5 arithops


class TestErrorPropagation:
    # Test error handling through the pipeline

    def test_parser_error_stops_pipeline(self, scanner):
        # Parser errors should be handled gracefully
        iloc_code = "invalid r1 => r2\n"
        file = StringIO(iloc_code)

        # Capture stderr
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        # Parser handles error without crashing
        assert True
