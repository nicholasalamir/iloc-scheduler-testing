import pytest
from io import StringIO
from Scanner import Scanner
import Parser


class TestParserBasicInstructions:
    # Test parsing basic ILOC instructions into IR

    def test_parse_loadI(self, scanner):
        # Parse loadI instruction
        iloc_code = "loadI 100 => r5\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        assert head is not None  # Parser should create head node
        assert head.getData()[1] == 1  # Opcode 1 (loadI)
        assert head.getData()[2] == 100  # Constant value
        assert head.getData()[10] == 5  # Target register r5
        assert num_ops == 1
        assert max_sr == 5

    def test_parse_load(self, scanner):
        # Parse load instruction
        iloc_code = "load r1 => r2\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        assert head is not None
        assert head.getData()[1] == 0  # Opcode 0 (load)
        assert head.getData()[2] == 1  # Source register r1
        assert head.getData()[10] == 2  # Target register r2
        assert num_ops == 1
        assert max_sr == 2

    def test_parse_store(self, scanner):
        # Parse store instruction
        iloc_code = "store r3 => r4\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        assert head is not None
        assert head.getData()[1] == 2  # Opcode 2 (store)
        assert head.getData()[2] == 3  # Source register r3
        assert head.getData()[10] == 4  # Target register r4

    def test_parse_add(self, scanner):
        # Parse add instruction
        iloc_code = "add r1, r2 => r3\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        assert head is not None
        assert head.getData()[1] == 3  # Opcode 3 (add)
        assert head.getData()[2] == 1  # First operand r1
        assert head.getData()[6] == 2  # Second operand r2
        assert head.getData()[10] == 3  # Target r3

    def test_parse_mult(self, scanner):
        # Parse mult instruction
        iloc_code = "mult r7, r8 => r9\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        assert head is not None
        assert head.getData()[1] == 5  # Opcode 5 (mult)
        assert head.getData()[2] == 7  # First operand r7
        assert head.getData()[6] == 8  # Second operand r8
        assert head.getData()[10] == 9  # Target r9

    def test_parse_output(self, scanner):
        # Parse output instruction
        iloc_code = "output 42\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        assert head is not None
        assert head.getData()[1] == 8  # Opcode 8 (output)
        assert head.getData()[2] == 42  # Constant value

    def test_parse_nop(self, scanner):
        # Parse nop instruction
        iloc_code = "nop\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        assert head is not None
        assert head.getData()[1] == 9  # Opcode 9 (nop)


class TestParserLinkedList:
    # Test Parser's linked list construction

    def test_multiple_instructions_linked(self, scanner):
        # Multiple instructions should be properly linked
        iloc_code = "loadI 5 => r1\nloadI 10 => r2\nadd r1, r2 => r3\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        assert head is not None
        assert head.getNext() is not None  # Head links to second
        assert head.getNext().getNext() is not None  # Second links to third
        assert head.getNext().getNext().getNext() is None  # Third is last
        assert num_ops == 3

    def test_head_and_tail_correct(self, scanner):
        # Head and tail pointers should be correct
        iloc_code = "loadI 1 => r1\nloadI 2 => r2\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        assert head is not None
        assert tail is not None
        assert head != tail  # Different for 2 ops
        assert head.getNext() == tail  # Head points to tail
        assert tail.getPrev() == head  # Tail points back to head


class TestParserTracking:
    # Test Parser's tracking of max_sr and num_ops

    def test_max_sr_tracking(self, scanner):
        # Parser should track maximum source register
        iloc_code = "add r1, r2 => r10\nadd r5, r20 => r3\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        assert max_sr == 20  # Highest register number

    def test_num_ops_tracking(self, scanner):
        # Parser should correctly count operations
        iloc_code = "loadI 1 => r1\nloadI 2 => r2\nloadI 3 => r3\nloadI 4 => r4\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        assert num_ops == 4


class TestParserComments:
    # Test Parser's handling of comments and empty lines

    def test_comment_lines_ignored(self, scanner):
        # Comment lines should not create operations
        iloc_code = "// This is a comment\nloadI 5 => r1\n// Another comment\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        assert num_ops == 1  # Comments not counted
        assert head.getData()[1] == 1  # Only parse the loadI


class TestParserErrors:
    # Test Parser's error handling

    def test_invalid_syntax_reported(self, scanner, capsys):
        # Parser should report errors for invalid syntax
        iloc_code = "add r1 r2 => r3\n"  # Missing comma
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        captured = capsys.readouterr()
        assert "ERROR" in captured.err  # Error reported to stderr
        assert "1" in captured.err  # Line number included

    def test_unknown_operation_reported(self, scanner, capsys):
        # Parser should report errors for unknown operations
        iloc_code = "foo r1 => r2\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        captured = capsys.readouterr()
        assert "ERROR" in captured.err


class TestParserEmptyFile:
    # Test Parser's handling of empty files

    def test_empty_file(self, scanner):
        # Empty files should be handled gracefully
        iloc_code = ""
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

        assert head is None  # Empty file results in None head
        assert tail is None
        assert num_ops == 0


class TestParserIntegration:
    # Test Parser with test data files

    def test_parse_data_dependency_file(self, scanner, test_data_dir):
        # Parse the data_dependency.iloc test file
        with open(f"{test_data_dir}/data_dependency.iloc", "r") as file:
            head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)

            assert num_ops == 4  # data_dependency.iloc has 4 operations
            assert head is not None
            assert max_sr >= 1


class TestParserIRToString:
    # Test Parser's IR_toString function (lines 26-59)

    def test_IR_toString_loadI(self, scanner, capsys):
        # IR_toString with loadI instruction
        iloc_code = "loadI 100 => r5\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Parser.IR_toString(head)

        captured = capsys.readouterr()
        assert "loadI" in captured.out

    def test_IR_toString_load(self, scanner, capsys):
        # IR_toString with load instruction
        iloc_code = "load r1 => r2\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Parser.IR_toString(head)

        captured = capsys.readouterr()
        assert "load" in captured.out

    def test_IR_toString_store(self, scanner, capsys):
        # IR_toString with store instruction
        iloc_code = "store r3 => r4\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Parser.IR_toString(head)

        captured = capsys.readouterr()
        assert "store" in captured.out

    def test_IR_toString_add(self, scanner, capsys):
        # IR_toString with add instruction
        iloc_code = "add r1, r2 => r3\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Parser.IR_toString(head)

        captured = capsys.readouterr()
        assert "add" in captured.out

    def test_IR_toString_sub(self, scanner, capsys):
        # IR_toString with sub instruction
        iloc_code = "sub r1, r2 => r3\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Parser.IR_toString(head)

        captured = capsys.readouterr()
        assert "sub" in captured.out

    def test_IR_toString_mult(self, scanner, capsys):
        # IR_toString with mult instruction
        iloc_code = "mult r1, r2 => r3\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Parser.IR_toString(head)

        captured = capsys.readouterr()
        assert "mult" in captured.out

    def test_IR_toString_lshift(self, scanner, capsys):
        # IR_toString with lshift instruction
        iloc_code = "lshift r1, r2 => r3\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Parser.IR_toString(head)

        captured = capsys.readouterr()
        assert "lshift" in captured.out

    def test_IR_toString_rshift(self, scanner, capsys):
        # IR_toString with rshift instruction
        iloc_code = "rshift r1, r2 => r3\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Parser.IR_toString(head)

        captured = capsys.readouterr()
        assert "rshift" in captured.out

    def test_IR_toString_output(self, scanner, capsys):
        # IR_toString with output instruction
        iloc_code = "output 42\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Parser.IR_toString(head)

        captured = capsys.readouterr()
        assert "output" in captured.out

    def test_IR_toString_nop(self, scanner, capsys):
        # IR_toString with nop instruction
        iloc_code = "nop\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Parser.IR_toString(head)

        captured = capsys.readouterr()
        assert "nop" in captured.out

    def test_IR_toString_multiple_instructions(self, scanner, capsys):
        # IR_toString with multiple instructions
        iloc_code = "loadI 5 => r1\nadd r1, r1 => r2\noutput 100\n"
        file = StringIO(iloc_code)

        head, tail, num_ops, max_sr = Parser.parseILOC(file, False, False, False, scanner)
        Parser.IR_toString(head)

        captured = capsys.readouterr()
        # Should print all three instructions
        assert "loadI" in captured.out
        assert "add" in captured.out
        assert "output" in captured.out
