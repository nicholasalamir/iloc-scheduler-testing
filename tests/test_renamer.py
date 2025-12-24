import pytest
from io import StringIO
from Scanner import Scanner
import Parser
import Renamer


class TestRenamerBasicRenaming:
    # Test basic register renaming functionality

    def test_rename_simple_loadI(self, scanner):
        # Simple loadI should assign VR to target register
        iloc_code = "loadI 100 => r1\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        Renamer.renaming(tail, num_ops, max_sr)

        # Check VR assigned to target (index 11)
        assert head.getData()[11] is not None
        assert head.getData()[11] >= 0  # Valid VR assigned

    def test_rename_load_with_use_and_def(self, scanner):
        # Load has both use (source) and def (target)
        iloc_code = "load r1 => r2\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        Renamer.renaming(tail, num_ops, max_sr)

        # Both operands should have VRs assigned
        assert head.getData()[3] >= 0  # VR for r1 (use)
        assert head.getData()[11] >= 0  # VR for r2 (def)

    def test_rename_add_three_operands(self, scanner):
        # Add has two uses and one def
        iloc_code = "add r1, r2 => r3\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        Renamer.renaming(tail, num_ops, max_sr)

        # All three operands should have VRs
        assert head.getData()[3] >= 0  # VR for r1
        assert head.getData()[7] >= 0  # VR for r2
        assert head.getData()[11] >= 0  # VR for r3

    def test_rename_store_two_uses(self, scanner):
        # Store has two uses, no def
        iloc_code = "store r1 => r2\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        Renamer.renaming(tail, num_ops, max_sr)

        # Both uses should have VRs
        assert head.getData()[3] >= 0  # VR for r1
        assert head.getData()[11] >= 0  # VR for r2


class TestRenamerMultipleInstructions:
    # Test renaming across multiple instructions

    def test_rename_data_dependency(self, scanner):
        # r1 defined then used - should get same VR
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r2\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        Renamer.renaming(tail, num_ops, max_sr)

        # First instruction defines r1
        vr_r1_def = head.getData()[11]
        # Second instruction uses r1 twice
        vr_r1_use1 = head.getNext().getData()[3]
        vr_r1_use2 = head.getNext().getData()[7]

        # All should be same VR
        assert vr_r1_def == vr_r1_use1
        assert vr_r1_def == vr_r1_use2

    def test_rename_independent_registers(self, scanner):
        # Independent registers should get different VRs
        iloc_code = "loadI 5 => r1\nloadI 10 => r2\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        Renamer.renaming(tail, num_ops, max_sr)

        vr_r1 = head.getData()[11]
        vr_r2 = head.getNext().getData()[11]

        # Should be different VRs
        assert vr_r1 != vr_r2

    def test_rename_register_reuse(self, scanner):
        # Same register used in different contexts gets different VRs
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r1\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        Renamer.renaming(tail, num_ops, max_sr)

        # First r1 (def)
        vr_r1_first = head.getData()[11]
        # Second r1 (def after use)
        vr_r1_second = head.getNext().getData()[11]

        # Should be different VRs (different live ranges)
        assert vr_r1_first != vr_r1_second


class TestRenamerNextUse:
    # Test next use (NU) tracking

    def test_next_use_simple(self, scanner):
        # r1 defined then used - NU should be set
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r2\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        Renamer.renaming(tail, num_ops, max_sr)

        # First instruction defines r1, NU should point to next instruction
        nu_r1 = head.getData()[13]  # NU for r1
        assert nu_r1 == 1  # Next use is at index 1

    def test_next_use_no_future_use(self, scanner):
        # r1 defined but never used - NU should be infinity
        iloc_code = "loadI 5 => r1\nloadI 10 => r2\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        Renamer.renaming(tail, num_ops, max_sr)

        # r1 never used after definition
        nu_r1 = head.getData()[13]
        assert nu_r1 == float('inf')


class TestRenamerEdgeCases:
    # Test edge cases and special instructions

    def test_rename_nop(self, scanner):
        # Nop has no operands to rename
        iloc_code = "nop\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        # Should not crash
        Renamer.renaming(tail, num_ops, max_sr)
        assert True

    def test_rename_output(self, scanner):
        # Output has constant, no register renaming
        iloc_code = "output 100\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        # Should not crash
        Renamer.renaming(tail, num_ops, max_sr)
        assert True

    def test_rename_mult_operation(self, scanner):
        # Test multiplication (3-address instruction)
        iloc_code = "mult r1, r2 => r3\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        Renamer.renaming(tail, num_ops, max_sr)

        # All three operands should have VRs
        assert head.getData()[3] >= 0
        assert head.getData()[7] >= 0
        assert head.getData()[11] >= 0

    def test_rename_lshift_rshift(self, scanner):
        # Test shift operations
        iloc_code = "lshift r1, r2 => r3\nrshift r4, r5 => r6\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        Renamer.renaming(tail, num_ops, max_sr)

        # All operands should have VRs
        assert head.getData()[3] >= 0  # lshift operands
        assert head.getNext().getData()[3] >= 0  # rshift operands


class TestRenamerPreservesStructure:
    # Test that renaming preserves IR structure

    def test_renaming_preserves_linked_list(self, scanner):
        # Renaming should not break linked list structure
        iloc_code = "loadI 1 => r1\nloadI 2 => r2\nloadI 3 => r3\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        Renamer.renaming(tail, num_ops, max_sr)

        # Verify linked list still intact
        assert head.getNext() is not None
        assert head.getNext().getNext() is not None
        assert head.getNext().getNext().getNext() is None

    def test_renaming_preserves_opcodes(self, scanner):
        # Renaming should not change opcodes
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r2\n"
        file = StringIO(iloc_code)
        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        opcode1_before = head.getData()[1]
        opcode2_before = head.getNext().getData()[1]

        Renamer.renaming(tail, num_ops, max_sr)

        # Opcodes should remain unchanged
        assert head.getData()[1] == opcode1_before
        assert head.getNext().getData()[1] == opcode2_before
