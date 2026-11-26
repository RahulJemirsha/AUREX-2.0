# AUREX 2.0 — Second Submission Brief

AUREX 2.0 is a free-first software research prototype that converts a local Git repository into a structured, evidence-labelled research report. It inventories source files and symbols, records Git provenance, discovers likely test files, and produces deterministic coding-task research candidates with acceptance criteria and adversarial test ideas.

The second iteration strengthens the first prototype by adding a reusable Python package, a command-line interface, repository provenance fields, a structured JSON report, deterministic candidate identifiers, and automated unit tests. The architecture is designed to accept the compulsory Click, Zod, and JsonCpp repositories through the same repository-analysis interface.

The current release deliberately labels generated items as low-confidence, proposal-only candidates. It does not claim that missing functionality has been proven, that feature patches have been generated, or that upstream test suites have been executed. The next stages are richer parsers, dependency/call graphs, opt-in test execution, sandboxing, mutation testing, and an AI-assisted research dashboard.
