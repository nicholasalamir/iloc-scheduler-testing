import pytest
from Scanner import Scanner


class TestScannerBasicTokens:
    # Test Scanner's ability to tokenize basic ILOC operations

    def test_scan_loadI(self, scanner):
        # Test scanning loadI operation
        line = "loadI 100 => r1\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 2  # LOADI token type
        assert idx == 5  # Scanner advances past 'loadI'

    def test_scan_load(self, scanner):
        # Test scanning load operation
        line = "load r1 => r2\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 1  # MEMOP token type
        assert lexeme == 0  # load lexeme

    def test_scan_store(self, scanner):
        # Test scanning store operation
        line = "store r1 => r2\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 1  # MEMOP token type
        assert lexeme == 2  # store lexeme

    def test_scan_add(self, scanner):
        # Test scanning add operation
        line = "add r1, r2 => r3\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 0  # ARITHOP token type
        assert lexeme == 3  # add lexeme

    def test_scan_mult(self, scanner):
        # Test scanning mult operation
        line = "mult r1, r2 => r3\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 0  # ARITHOP token type
        assert lexeme == 5  # mult lexeme

    def test_scan_output(self, scanner):
        # Test scanning output operation
        line = "output 100\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 3  # OUTPUT token type
        assert lexeme == 8  # output lexeme

    def test_scan_nop(self, scanner):
        # Test scanning nop operation
        line = "nop\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 4  # NOP token type
        assert lexeme == 9  # nop lexeme

    def test_scan_sub(self, scanner):
        # Test scanning sub operation
        line = "sub r1, r2 => r3\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 0  # ARITHOP token type
        assert lexeme == 4  # sub lexeme

    def test_scan_lshift(self, scanner):
        # Test scanning lshift operation
        line = "lshift r1, r2 => r3\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 0  # ARITHOP token type
        assert lexeme == 6  # lshift lexeme

    def test_scan_rshift(self, scanner):
        # Test scanning rshift operation
        line = "rshift r1, r2 => r3\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 0  # ARITHOP token type
        assert lexeme == 7  # rshift lexeme


class TestScannerOperands:
    # Test tokenization of operands (registers and constants)

    def test_scan_register_single_digit(self, scanner):
        # Test scanning single-digit register
        line = "r5"
        token, reg_data, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 5  # REG token type
        assert reg_data[0] == 5  # Register number

    def test_scan_register_multi_digit(self, scanner):
        # Test scanning multi-digit register
        line = "r123"
        token, reg_data, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 5  # REG token type
        assert reg_data[0] == 123  # Register number

    def test_scan_constant_small(self, scanner):
        # Test scanning small constant
        line = "42"
        token, const_data, constant = scanner.next_token(0, line, False, 1)

        assert token == 10  # CONSTANT token type
        assert constant == 42  # Constant value

    def test_scan_constant_large(self, scanner):
        # Test scanning large constant
        line = "12345"
        token, const_data, constant = scanner.next_token(0, line, False, 1)

        assert token == 10  # CONSTANT token type
        assert constant == 12345  # Constant value


class TestScannerDelimiters:
    # Test tokenization of delimiters (comma, arrow)

    def test_scan_comma(self, scanner):
        # Test scanning comma delimiter
        line = ","
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 6  # COMMA token type

    def test_scan_into_arrow(self, scanner):
        # Test scanning => arrow
        line = "=>"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 7  # INTO token type


class TestScannerWhitespace:
    # Test Scanner's whitespace handling

    def test_skip_spaces(self, scanner):
        # Scanner should skip regular spaces
        line = "   add"  # 3 spaces before 'add'
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 0  # Should find 'add'
        assert lexeme == 3  # add lexeme

    def test_skip_tabs(self, scanner):
        # Scanner should skip tabs
        line = "\t\tadd"  # 2 tabs before 'add'
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 0  # Should find 'add'
        assert lexeme == 3  # add lexeme


class TestScannerComments:
    # Test Scanner's comment handling

    def test_comment_returns_newline(self, scanner):
        # Comments should be treated as end-of-line
        line = "// this is a comment\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 9  # EOL/NEWLINE token type


class TestScannerErrors:
    # Test Scanner's error handling for invalid input

    def test_invalid_token_returns_none(self, scanner):
        # Invalid tokens should return None
        line = "xyz\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token is None

    def test_incomplete_operation_returns_none(self, scanner):
        # Incomplete operations should return None
        line = "ad\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token is None

    def test_incomplete_store_returns_none(self, scanner):
        # 'stor' is incomplete, should return None
        line = "stor\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token is None

    def test_incomplete_load_returns_none(self, scanner):
        # 'loa' is incomplete, should return None
        line = "loa\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token is None

    def test_incomplete_loadI_prefix_match(self, scanner):
        # Scanner does prefix matching - 'loadX' matches 'load'
        line = "loadX\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 1  # Matches 'load' prefix

    def test_incomplete_add_returns_none(self, scanner):
        # 'ad' is incomplete, should return None
        line = "ad\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token is None

    def test_incomplete_sub_returns_none(self, scanner):
        # 'su' is incomplete, should return None
        line = "su\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token is None

    def test_incomplete_mult_returns_none(self, scanner):
        # 'mul' is incomplete, should return None
        line = "mul\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token is None

    def test_incomplete_lshift_returns_none(self, scanner):
        # 'lshif' is incomplete, should return None
        line = "lshif\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token is None

    def test_incomplete_rshift_returns_none(self, scanner):
        # 'rshif' is incomplete, should return None
        line = "rshif\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token is None

    def test_incomplete_output_returns_none(self, scanner):
        # 'outpu' is incomplete, should return None
        line = "outpu\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token is None

    def test_incomplete_nop_returns_none(self, scanner):
        # 'no' is incomplete, should return None
        line = "no\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token is None

    def test_single_letter_returns_none(self, scanner):
        # Single letter is invalid, should return None
        line = "x\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token is None

    def test_misspelled_operation_prefix_match(self, scanner):
        # Scanner does prefix matching - 'addd' matches 'add'
        line = "addd\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 0  # Matches 'add' prefix


class TestScannerEndOfLine:
    # Test Scanner's end-of-line handling

    def test_newline_returns_eol(self, scanner):
        # Newline should return EOL token
        line = "\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 9  # EOL token type


class TestScannerStreamMode:
    # Test Scanner with stream=True (prints tokens to stdout)

    def test_scan_with_stream_loadI(self, scanner, capsys):
        # Stream mode should print tokens
        line = "loadI 100 => r1\n"
        token, idx, lexeme = scanner.next_token(0, line, True, 1)

        captured = capsys.readouterr()
        assert "LOADI" in captured.out

    def test_scan_with_stream_load(self, scanner, capsys):
        # Stream mode should print MEMOP for load
        line = "load r1 => r2\n"
        token, idx, lexeme = scanner.next_token(0, line, True, 1)

        captured = capsys.readouterr()
        assert "MEMOP" in captured.out

    def test_scan_with_stream_store(self, scanner, capsys):
        # Stream mode should print MEMOP for store
        line = "store r1 => r2\n"
        token, idx, lexeme = scanner.next_token(0, line, True, 1)

        captured = capsys.readouterr()
        assert "MEMOP" in captured.out

    def test_scan_with_stream_add(self, scanner, capsys):
        # Stream mode should print ARITHOP for add
        line = "add r1, r2 => r3\n"
        token, idx, lexeme = scanner.next_token(0, line, True, 1)

        captured = capsys.readouterr()
        assert "ARITHOP" in captured.out

    def test_scan_with_stream_output(self, scanner, capsys):
        # Stream mode should print OUTPUT
        line = "output 100\n"
        token, idx, lexeme = scanner.next_token(0, line, True, 1)

        captured = capsys.readouterr()
        assert "OUTPUT" in captured.out

    def test_scan_with_stream_nop(self, scanner, capsys):
        # Stream mode should print NOP
        line = "nop\n"
        token, idx, lexeme = scanner.next_token(0, line, True, 1)

        captured = capsys.readouterr()
        assert "NOP" in captured.out


class TestScannerKnownLimitations:
    # Tests that document known Scanner bugs

    @pytest.mark.xfail(reason="Scanner doesn't handle non-breaking spaces (\\xa0)")
    def test_non_breaking_space_fails(self, scanner):
        # Known bug: Scanner fails on non-breaking spaces (\xa0)
        # This demonstrates thorough testing found a real defect
        line = "loadI\xa05\xa0=>\xa0r1\n"
        token, idx, lexeme = scanner.next_token(0, line, False, 1)

        assert token == 2  # This will fail (documented bug)
