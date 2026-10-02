# Source and contribution

Technical reference: [eslint-community/eslint-plugin-security](https://github.com/eslint-community/eslint-plugin-security/tree/d1ba1cd7365925dd01606a22e4d9bcdcf7f1d8fd), fixed commit `d1ba1cd7365925dd01606a22e4d9bcdcf7f1d8fd`, Apache-2.0.

The selected references are rules/detect-bidi-characters.js and rules/detect-invisible-characters.js, their character repertoire, LICENSE and package.json. Original rule credits include Luciano Mammino (spelled Luciamo in the source header), Simone Sanfratello, Liran Tal and electrohyun. The upstream copyright and license are retained in LICENSE and NOTICE.

This new Python implementation was assisted by Codex at the repository owner's instruction. It independently implements bounded descriptor input, physical UTF-8 scanning, byte/codepoint locations, explicit control-scope diagnostics and incomplete-analysis reports. It neither imports ESLint nor repackages its implementations. It is a complete implementation of this selected project scope, not a complete rewrite or replacement of the upstream multi-rule plugin.

The upstream algorithms and history remain their authors' work. Applicant contributions, identity, organization and any real safeguards impact must be substantiated separately; no CVE, upstream discovery or CVP approval is claimed.
