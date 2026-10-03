# Defensive scope

Input: one explicitly selected local UTF-8 source file. Output: bounded metadata about selected physical characters and delimiter scopes. The tool does not emit source snippets, credentials or control characters verbatim.

There is no network interface, URL input, target discovery, code loader, browser, plugin execution, source rewriting, injection generator, concealment or safeguards bypass. Tests consist of ordinary text and harmless Unicode character records.

Incomplete input, malformed encoding or exhausted budgets remain OPEN. An absence of selected characters is not a security finding about the whole program. This supporting defensive project alone does not prove eligibility under the [Anthropic CVP rules](https://support.claude.com/en/articles/14604842-real-time-cyber-safeguards-on-claude-opus-and-sonnet).
