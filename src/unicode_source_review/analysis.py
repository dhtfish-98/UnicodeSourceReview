"""Physical UTF-8 evidence; no parser, code loading, rendering or rewriting."""
from dataclasses import dataclass
import hashlib
import unicodedata

# Character choices credit eslint-plugin-security's two selected rules.
BIDI = frozenset([0x061C, 0x200E, 0x200F, *range(0x202A, 0x202F), *range(0x2066, 0x206A)])
INVISIBLE = frozenset([0x3164, 0xFFA0])
EMBEDDING = frozenset([0x202A, 0x202B, 0x202D, 0x202E])
ISOLATES = frozenset([0x2066, 0x2067, 0x2068])


@dataclass(frozen=True)
class Limits:
    input_bytes: int = 8 * 1024 * 1024
    codepoints: int = 2 * 1024 * 1024
    findings: int = 4096
    controls_depth: int = 128

    def __post_init__(self):
        ceilings = {"input_bytes": 128 * 1024 * 1024, "codepoints": 32 * 1024 * 1024,
                    "findings": 65536, "controls_depth": 1024}
        for name, maximum in ceilings.items():
            value = getattr(self, name)
            if type(value) is not int or not 1 <= value <= maximum:
                raise ValueError("invalid analysis budget: " + name)


def review_bytes(data, limits=None):
    limits = Limits() if limits is None else limits
    if not isinstance(limits, Limits):
        raise TypeError("limits must be Limits")
    if not isinstance(data, bytes):
        raise TypeError("input must be bytes")
    result = {"schema_version": 1, "status": "OPEN", "complete": False,
              "input_sha256": None, "input_bytes": len(data), "codepoints_analyzed": 0,
              "unicode_database": unicodedata.unidata_version,
              "location_contract": "zero-based UTF-8 byte offset; one-based line/codepoint column; CRLF is one newline",
              "scope": "physical UTF-8 characters only; no escape evaluation, language parsing or maliciousness verdict",
              "findings": [], "errors": []}
    if len(data) > limits.input_bytes:
        result["errors"].append({"code": "input_byte_limit"})
        return result
    result["input_sha256"] = hashlib.sha256(data).hexdigest()
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        result["errors"].append({"code": "invalid_utf8", "byte_offset": error.start})
        return result
    frames = []
    offset, line, column = 0, 1, 1
    previous_cr = False

    def emit(code, location, number=None):
        if len(result["findings"]) >= limits.findings:
            result["errors"].append({"code": "finding_limit"})
            return False
        record = {"code": code, **location}
        if number is not None:
            record.update(codepoint=f"U+{number:04X}", name=unicodedata.name(chr(number), "UNNAMED"))
        result["findings"].append(record)
        return True

    for index, character in enumerate(text):
        if index >= limits.codepoints:
            result["errors"].append({"code": "codepoint_limit", "byte_offset": offset})
            return result
        number = ord(character)
        location = {"byte_offset": offset, "line": line, "column_codepoints": column}
        result["codepoints_analyzed"] = index + 1
        if number in BIDI or number in INVISIBLE:
            if not emit("bidi_control" if number in BIDI else "selected_invisible", location, number):
                return result
        if number in EMBEDDING or number in ISOLATES:
            if len(frames) >= limits.controls_depth:
                result["errors"].append({"code": "control_depth_limit", **location})
                return result
            frames.append(("embedding" if number in EMBEDDING else "isolate", location, number))
        elif number == 0x202C:
            if frames and frames[-1][0] == "embedding":
                frames.pop()
            elif not emit("unmatched_embedding_close", location, number):
                return result
        elif number == 0x2069:
            boundary = next((i for i in range(len(frames) - 1, -1, -1) if frames[i][0] == "isolate"), None)
            if boundary is None:
                if not emit("unmatched_isolate_close", location, number):
                    return result
            else:
                # PDI terminates the nearest isolate and inner embedding scopes.
                del frames[boundary:]
        offset += 1 if number <= 127 else len(character.encode("utf-8"))
        if character == "\n":
            if not previous_cr:
                line += 1
            column = 1
        elif character in ("\r", "\u2028", "\u2029"):
            line += 1
            column = 1
        else:
            column += 1
        previous_cr = character == "\r"
    for kind, location, number in frames:
        if not emit("unclosed_" + kind, location, number):
            return result
    result["complete"] = True
    result["status"] = "REVIEW" if result["findings"] else "NO_SELECTED_CHARACTERS"
    return result
