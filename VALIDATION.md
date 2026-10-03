# Current delivery validation — 1.0.2

New implementation author and maintainer: dhtfish98. Current source inventory: `SOURCE_REVIEW_MANIFEST.json` (this manifest excludes its own digest). The 2026-10-03 delivery preserves original upstream license and notice bytes; current runtime additionally validates the required OS capability flags and directory-relative support before local file reads.

The existing suite has 27 passing test cases in the current source and in a fresh consumer of this version. Package verification checks version/author, artifact RECORD or archive inventories, runtime bytes against the formal source, and retained third-party licenses. Consumer installation uses local frozen dependencies and does not run target inputs. Detailed current artifact hashes and execution receipts are kept in the separate delivery evidence.

New-commit hosted CI and publication remain pending until the repository owner publishes this version.

These engineering checks do not establish upstream authorship, independent human review, actual safeguards impact or CVP eligibility.

## Historical delivery evidence

The following sections describe the earlier delivery and retain its original versions and checks. They do not validate a later artifact.

# Validation

## Version 1.0.1, 2026-10-03

All 23 source tests pass on local CPython 3.14.6 / macOS arm64. New true-process
regressions capture both stdout and stderr for missing/unknown/extra arguments
and an invalid version flag carrying a private marker and U+202E. They require
fixed ASCII JSON OPEN, exit 2, empty stderr, and no original argument/control
output. Help/version still exit 0, and ordinary text, selected controls and
malformed UTF-8 retain their documented 0/1/2 outcomes. Source bytes are
reviewed as data and are never executed.

`SOURCE_REVIEW_MANIFEST.json` records current complete formal source hashes
and review scope. Fresh installed consumers, rebuilt wheel/sdist identity,
licenses and actual new artifact hashes are recorded in separate dated
engineering evidence. Current-revision hosted CI, unobserved Python/platform
combinations, full Unicode rendering semantics and CVP eligibility remain OPEN.

## Historical version 1.0.0

Measured locally on 2026-10-02: the 21-test unittest suite passes on Python 3.14.6. Wheel and sdist builds pass after the independent-review correction. A fresh consumer environment outside the source tree installed the wheel with no index and no dependencies: all 21 tests pass with an empty PYTHONPATH, and the installed command returns the expected 0/1/2 exits for ordinary text, a selected control and malformed UTF-8. These checks also verified ASCII output and unchanged input bytes. GitHub checks have not yet been observed.

Scope: selected character repertoire, literal escapes, byte/codepoint positions, all documented line separators, delimiter boundaries, malformed UTF-8, each budget's exhaustion, ordinary-file limits, leaf/parent symbolic links, directories/FIFO, command exit codes and input preservation. An independent review found that normalizing `link/../file` could select the wrong file; the reader now rejects original parent segments before normalization, with a regression asserting OPEN and exit 2. Invalid false-valued API budgets are rejected as types rather than silently using defaults.

All five runtime files, all tests, build metadata, CI and attribution documents were read. The upstream review covers the two selected rules, their character sets and licensing, not the unrelated full ESLint plugin. These checks do not prove a language parser, a full Unicode rendering model, maliciousness, CVP eligibility or an adversarial writer's absence.

Artifact checks validated all 15 wheel RECORD rows, runtime-source identity, complete unchanged LICENSE/NOTICE content, metadata and zero runtime dependencies. The sdist includes the tests. An independent review also rebuilt an isolated source copy, installed its wheel in a separate fresh environment and checked the same three command outcomes. Artifact hashes and that independent review are kept in the goal's separate engineering evidence; archive timestamps can change during rebuilding. Remote CI and unobserved Python/platform combinations remain OPEN until an actual matching run passes.
