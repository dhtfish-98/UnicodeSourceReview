# Source and contribution

Technical reference: [eslint-community/eslint-plugin-security](https://github.com/eslint-community/eslint-plugin-security/tree/d1ba1cd7365925dd01606a22e4d9bcdcf7f1d8fd), fixed commit `d1ba1cd7365925dd01606a22e4d9bcdcf7f1d8fd`, Apache-2.0.

The selected references are rules/detect-bidi-characters.js and rules/detect-invisible-characters.js, their character repertoire, LICENSE and package.json. Original rule credits include Luciano Mammino (spelled Luciamo in the source header), Simone Sanfratello, Liran Tal and electrohyun. The upstream copyright and license are retained in LICENSE and NOTICE.

This new Python implementation was authored by dhtfish98 at the repository owner's instruction. It independently implements bounded descriptor input, physical UTF-8 scanning, byte/codepoint locations, explicit control-scope diagnostics and incomplete-analysis reports. It neither imports ESLint nor repackages its implementations. It is a complete implementation of this selected project scope, not a complete rewrite or replacement of the upstream multi-rule plugin.

The upstream algorithms and history remain their authors' work. Applicant contributions, identity, organization and any real safeguards impact must be substantiated separately; no CVE, upstream discovery or CVP approval is claimed.

New implementation author: dhtfish98. This attribution applies to the new project implementation; original sources, licenses and third-party notices retain their authors. Automated checks do not establish independent human review or CVP eligibility.

## Current distribution and reference boundary

New Python scanner is distributed. The selected character repertoire is explicitly reference-derived; original copyright and license remain while its specific applicability is OPEN. No ESLint runtime is bundled. New implementation author and maintainer: dhtfish98. Source identities and bounded research facts above remain provenance, not an assertion that those authors wrote or endorsed the new runtime.
