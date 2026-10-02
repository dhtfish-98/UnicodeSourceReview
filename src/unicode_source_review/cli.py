import argparse
import json

from .analysis import Limits, review_bytes
from .input import InputError, read_regular_file


def main(argv=None):
    parser = argparse.ArgumentParser(description="Review selected physical Unicode source characters without executing the input")
    parser.add_argument("file", help="one ordinary UTF-8 source file; no directories or URLs")
    args = parser.parse_args(argv)
    try:
        limits = Limits()
        result = review_bytes(read_regular_file(args.file, limits.input_bytes), limits)
    except (InputError, ValueError) as error:
        result = {"schema_version": 1, "status": "OPEN", "complete": False,
                  "findings": [], "errors": [{"code": "input_error", "message": str(error)}]}
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 2 if not result["complete"] else 1 if result["findings"] else 0
