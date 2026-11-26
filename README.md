# AUREX 2.0 — Second Submission Prototype

**Autonomous Software Research & Evolution Engine**  
A free-first research prototype that inventories source code, records repository provenance, and creates evidence-labelled coding-task candidates.

## What's implemented
- Python AST inventory for functions, async functions, and classes.
- Lightweight lexical inventory for TypeScript/JavaScript and C/C++ declarations.
- Repository metadata capture when the input is a Git checkout: commit, branch, dirty state.
- Test-file discovery and extension statistics.
- Deterministic task-candidate IDs and JSON research reports.
- Explicit status/validation fields to distinguish proposals from verified work.
- Unit tests for core analysis behavior.

## What is not implemented
This release does **not** claim autonomous multi-agent reasoning, semantic dependency graphs, feature-patch generation, sandbox execution, mutation testing, or upstream test-suite validation. Those are roadmap items, not current capabilities.

## Run locally
Requires Python 3.10+; no third-party packages are required.

```bash
python -m unittest discover -s tests -v
python -m aurex.cli /path/to/local/repository --output aurex-report.json --limit 10
```

For the compulsory repositories, clone them first:
```bash
git clone --depth 1 https://github.com/pallets/click.git
git clone --depth 1 https://github.com/colinhacks/zod.git
git clone --depth 1 https://github.com/open-source-parsers/jsoncpp.git
```
Then run the CLI separately on each local folder.

## Report semantics
`task_type=research_candidate`, `confidence=low`, and `status=proposal_only` are intentional. A candidate is not proof of a missing feature or a verified bug. Review the source and run the upstream project's own tests before treating a proposal as an engineering task.

## Architecture
1. Repository intake and provenance
2. Static source inventory
3. Test-file inventory
4. Evidence-labelled task proposal generation
5. JSON report for review and future dashboard integration

## Free-first roadmap
- v2.1: richer language parsers and import/call graph.
- v2.2: test runner adapters with explicit opt-in and timeouts.
- v2.3: isolated execution and resource limits.
- v3.0: semantic retrieval, agent orchestration, mutation testing, and dashboard.

## License
MIT
