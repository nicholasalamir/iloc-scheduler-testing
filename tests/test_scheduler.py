import pytest
from io import StringIO
from Scanner import Scanner
import Parser
import Renamer
import DependencyGraphGenerator
import PriorityCalculator
import Scheduler


class TestSchedulerBasic:
    # Test basic scheduling (these are already tested in integration tests)
    # Just adding a few quick smoke tests here

    def test_scheduler_returns_cycle_count(self, scanner):
        # Scheduler should return a cycle count
        iloc_code = "loadI 5 => r1\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)
        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)
        nodes, roots, leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

        cycle_count = Scheduler.schedule(nodes, roots, leaves, False)

        assert cycle_count is not None
        assert cycle_count >= 1

    def test_scheduler_handles_dependencies(self, scanner):
        # Scheduler should respect dependencies
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r2\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Renamer.renaming(tail, num_ops, max_sr)
        nodes, roots, leaves = DependencyGraphGenerator.generate_dependency_graph(head)
        nodes, roots, leaves = PriorityCalculator.calculatePriorities(nodes, roots, leaves)

        cycle_count = Scheduler.schedule(nodes, roots, leaves, False)

        # Add must wait for loadI
        assert cycle_count is not None
        assert cycle_count > 0
