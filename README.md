# UnicodeSourceReview


New implementation author: **dhtfish98**. Current project version: **1.0.3**.

Offline evidence for reviewing physical Unicode direction controls and two selected invisible Hangul characters in a local UTF-8 source file. It reports locations and control-scope diagnostics without executing, importing, editing, or printing the source. Ordinary Chinese, Japanese, combining marks and emoji are supported as text.

```sh
python -m pip install .
unicode-source-review path/to/source.txt
```

Output is ASCII-escaped JSON. Exit 0 means no selected physical characters were observed in a complete review; 1 means reviewer attention is required; 2 means input or analysis is incomplete. Invalid or missing command arguments return fixed ASCII JSON OPEN and exit 2
without echoing paths, argument values or control characters on either output
stream. `--help` prints ordinary help and `--version` prints the tool version.
None of these establish whether a program is malicious, exploitable or safe.

Locations use zero-based UTF-8 byte offsets and one-based lines and codepoint columns, including an initial BOM. Columns are neither editor UTF-16 positions nor grapheme/display widths. CRLF is one line break; CR, LF, U+2028 and U+2029 also advance a line. A literal ASCII backslash-u escape is not a physical Unicode control.

The selected repertoire is U+061C, U+200E–U+200F, U+202A–U+202E, U+2066–U+2069, U+3164 and U+FFA0. Valid uses can still require contextual review. This is not a complete Unicode confusables scanner, language parser or Unicode bidirectional rendering engine. The scope diagnostic tracks explicit embedding/isolate delimiters and never simulates rendered execution.

The input reader requires POSIX descriptors and rejects symbolic links in every path component and non-regular files. Paths containing a parent (`..`) component are refused before normalization, so a link followed by `..` cannot silently select different bytes. Defaults bound input to 8 MiB, analysis to 2,097,152 codepoints, output to 4,096 records and open control scopes to 128. Limits return OPEN, retaining already observed evidence. File metadata changes during reading are rejected; the report identifies the bytes read by SHA-256, without claiming an adversarial writer cannot evade metadata observations.

See ORIGIN.md for attribution, DEFENSIVE_SCOPE.md for capability boundaries and VALIDATION.md for measured checks.

Local-file capability boundary: required OS flags must be exact positive integers. Descriptor walking also requires declared `os.open` directory-relative support. Missing, null, zero, boolean or otherwise invalid required capabilities return a controlled OPEN result before file access. Native Windows local-file reading is outside this POSIX profile.
