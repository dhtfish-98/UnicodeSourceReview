import argparse
import json

from .analysis import Limits, review_bytes
from .input import InputError, read_regular_file
from . import __version__


class PrivateArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse's ordinary diagnostics can quote private paths and controls.
        raise ValueError("invalid command arguments")


def main(argv=None):
    parser = PrivateArgumentParser(prog="unicode-source-review", description="Review selected physical Unicode source characters without executing the input")
    parser.add_argument("file", help="one ordinary UTF-8 source file; no directories or URLs")
    parser.add_argument("--version", action="version", version=__version__)
    try:
        args = parser.parse_args(argv)
    except ValueError:
        print(json.dumps({"schema_version": 1, "status": "OPEN", "complete": False,
                          "findings": [], "errors": [{"code": "invalid_arguments", "message": "invalid command arguments"}]},
                         ensure_ascii=True, sort_keys=True))
        return 2
    try:
        limits = Limits()
        result = review_bytes(read_regular_file(args.file, limits.input_bytes), limits)
    except (InputError, ValueError) as error:
        result = {"schema_version": 1, "status": "OPEN", "complete": False,
                  "findings": [], "errors": [{"code": "input_error", "message": str(error)}]}
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 2 if not result["complete"] else 1 if result["findings"] else 0
