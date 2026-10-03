import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from unicode_source_review import Limits, read_regular_file, review_bytes
from unicode_source_review.cli import main
from unicode_source_review.input import InputError
import unicode_source_review


class SourceEvidenceTests(unittest.TestCase):
    def test_ordinary_languages_and_emoji(self):
        data = "变量 = '日本語 😀 é'\n".encode()
        report = review_bytes(data)
        self.assertTrue(report["complete"])
        self.assertEqual(report["status"], "NO_SELECTED_CHARACTERS")
        self.assertEqual(report["input_sha256"], hashlib.sha256(data).hexdigest())

    def test_all_selected_characters(self):
        # Harmless character records, with no executable code or attack sample.
        for number in [0x061C, 0x200E, 0x200F, *range(0x202A, 0x202F), *range(0x2066, 0x206A), 0x3164, 0xFFA0]:
            with self.subTest(number=number):
                report = review_bytes(chr(number).encode())
                self.assertEqual(report["status"], "REVIEW")
                self.assertEqual(report["findings"][0]["codepoint"], f"U+{number:04X}")

    def test_offsets_not_visual_columns(self):
        text = "中😀é" + chr(0x200E)
        record = review_bytes(text.encode())["findings"][0]
        self.assertEqual(record["byte_offset"], 10)
        self.assertEqual(record["column_codepoints"], 5)

    def test_newline_families(self):
        for newline in ["\n", "\r", "\r\n", "\u2028", "\u2029"]:
            with self.subTest(newline=ascii(newline)):
                record = review_bytes(("a" + newline + chr(0x200F)).encode())["findings"][0]
                self.assertEqual((record["line"], record["column_codepoints"]), (2, 1))

    def test_empty_and_bom(self):
        self.assertTrue(review_bytes(b"")["complete"])
        row = review_bytes(b"\xef\xbb\xbf" + chr(0x3164).encode())["findings"][0]
        self.assertEqual((row["byte_offset"], row["column_codepoints"]), (3, 2))

    def test_literal_escape_is_not_physical_control(self):
        self.assertEqual(review_bytes(br"\u202E \u3164")["findings"], [])

    def test_balanced_embedding_and_isolate(self):
        for numbers in [(0x202A, 0x202C), (0x2066, 0x2069), (0x2066, 0x202A, 0x2069)]:
            report = review_bytes("".join(map(chr, numbers)).encode())
            self.assertEqual(len(report["findings"]), len(numbers))
            self.assertTrue(report["complete"])

    def test_pdf_cannot_cross_isolate_boundary(self):
        report = review_bytes("".join(map(chr, [0x202A, 0x2066, 0x202C, 0x2069, 0x202C])).encode())
        codes = [r["code"] for r in report["findings"]]
        self.assertIn("unmatched_embedding_close", codes)
        self.assertFalse(any(code.startswith("unclosed") for code in codes))

    def test_unclosed_and_unmatched(self):
        for number, code in [(0x202A, "unclosed_embedding"), (0x2066, "unclosed_isolate"),
                             (0x202C, "unmatched_embedding_close"), (0x2069, "unmatched_isolate_close")]:
            self.assertIn(code, [r["code"] for r in review_bytes(chr(number).encode())["findings"]])

    def test_invalid_utf8_is_open_and_does_not_echo_data(self):
        report = review_bytes(b"private_text\xff")
        self.assertFalse(report["complete"])
        self.assertEqual(report["errors"], [{"code": "invalid_utf8", "byte_offset": 12}])
        self.assertNotIn("private_text", json.dumps(report))

    def test_limits_do_not_return_clean(self):
        cases = [(b"abc", Limits(input_bytes=2), "input_byte_limit"),
                 (b"abc", Limits(codepoints=2), "codepoint_limit"),
                 ((chr(0x200E) * 2).encode(), Limits(findings=1), "finding_limit"),
                 ((chr(0x202A) * 2).encode(), Limits(controls_depth=1), "control_depth_limit")]
        for data, limits, expected in cases:
            report = review_bytes(data, limits)
            self.assertFalse(report["complete"])
            self.assertEqual(report["status"], "OPEN")
            self.assertEqual(report["errors"][-1]["code"], expected)

    def test_budget_validation(self):
        for value in [True, 0, -1, 2.0, 2**40]:
            with self.assertRaises(ValueError):
                Limits(findings=value)

    def test_metadata_never_echoes_source(self):
        report = review_bytes(("private_token_value " + chr(0x200E)).encode())
        self.assertNotIn("private_token_value", json.dumps(report))

    def test_wrong_api_types(self):
        for data in ["text", bytearray(b"x"), None]:
            with self.assertRaises(TypeError):
                review_bytes(data)
        for limits in [False, 0, {}, "limits"]:
            with self.assertRaises(TypeError):
                review_bytes(b"text", limits)


@unittest.skipUnless(os.name == "posix", "descriptor no-follow input is POSIX-only")
class InputAndCommandTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.file = self.root / "input.txt"

    def tearDown(self):
        self.temp.cleanup()

    def test_read_limit_and_input_preservation(self):
        self.file.write_bytes(b"abc")
        before = hashlib.sha256(self.file.read_bytes()).digest()
        self.assertEqual(read_regular_file(self.file, 3), b"abc")
        self.assertEqual(hashlib.sha256(self.file.read_bytes()).digest(), before)
        with self.assertRaises(InputError):
            read_regular_file(self.file, 2)

    def test_empty_file(self):
        self.file.write_bytes(b"")
        self.assertEqual(read_regular_file(self.file, 1), b"")

    def test_symlink_leaf_and_parent(self):
        self.file.write_bytes(b"x")
        leaf = self.root / "leaf"
        leaf.symlink_to(self.file)
        parent = self.root / "parent"
        parent.symlink_to(self.root, target_is_directory=True)
        for path in [leaf, parent / self.file.name]:
            with self.assertRaises(InputError):
                read_regular_file(path, 8)

    def test_directory_fifo_missing(self):
        fifo = self.root / "pipe"
        os.mkfifo(fifo)
        for path in [self.root, fifo, self.root / "missing"]:
            with self.assertRaises(InputError):
                read_regular_file(path, 8)

    def test_parent_segments_cannot_erase_symlink_checks(self):
        self.file.write_bytes(b"plain")
        other = self.root / "other"
        (other / "deep").mkdir(parents=True)
        (other / "input.txt").write_bytes(chr(0x200E).encode())
        (self.root / "link").symlink_to(other / "deep", target_is_directory=True)
        for path in [str(self.root / "link") + "/../input.txt",
                     str(other / "deep") + "/../../input.txt"]:
            with self.assertRaises(InputError):
                read_regular_file(path, 64)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main([path])
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(output.getvalue())["status"], "OPEN")

    def test_cli_exit_codes_and_ascii_output(self):
        for data, expected in [(b"plain", 0), (chr(0x200E).encode(), 1), (b"\xff", 2)]:
            self.file.write_bytes(data)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main([str(self.file)])
            self.assertEqual(code, expected)
            self.assertTrue(output.getvalue().isascii())
            self.assertIn("status", json.loads(output.getvalue()))

    def test_cli_missing_does_not_print_path(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main([str(self.root / "private_path_missing")])
        self.assertEqual(code, 2)
        self.assertNotIn("private_path_missing", output.getvalue())

    def command(self, args):
        environment = dict(os.environ, PYTHONPATH=str(Path(unicode_source_review.__file__).parent.parent))
        return subprocess.run([sys.executable, "-m", "unicode_source_review", *args],
                              cwd=self.root, env=environment, capture_output=True, check=False)

    def test_process_invalid_arguments_are_private_ascii_open(self):
        private = "PRIVATE_ARGUMENT_" + chr(0x202E)
        for args in ([], ["--" + private], [private, "--" + private], [private, private], [private, "--version=" + private]):
            with self.subTest(argument_count=len(args)):
                completed = self.command(args)
                self.assertEqual(completed.returncode, 2)
                self.assertEqual(completed.stderr, b"")
                self.assertTrue(completed.stdout.isascii())
                self.assertNotIn(private.encode(), completed.stdout)
                self.assertNotIn(b"PRIVATE_ARGUMENT_", completed.stdout)
                report = json.loads(completed.stdout)
                self.assertEqual(report["status"], "OPEN")
                self.assertFalse(report["complete"])
                self.assertEqual(report["errors"][0]["code"], "invalid_arguments")

    def test_process_help_version_and_normal_exits(self):
        for argument in ("--help", "--version"):
            completed = self.command([argument])
            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stderr, b"")
            self.assertTrue(completed.stdout.isascii())
        self.assertEqual(self.command(["--version"]).stdout.strip(), b"1.0.2")
        for data, expected in ((b"plain", 0), (chr(0x200E).encode(), 1), (b"\xff", 2)):
            self.file.write_bytes(data)
            completed = self.command([str(self.file)])
            self.assertEqual(completed.returncode, expected)
            self.assertEqual(completed.stderr, b"")
            self.assertTrue(completed.stdout.isascii())


if __name__ == "__main__":
    unittest.main()
