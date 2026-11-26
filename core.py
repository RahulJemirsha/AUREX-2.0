from __future__ import annotations
import ast, hashlib, json, re, subprocess
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

IGNORE_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "build", "dist"}
EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".cpp", ".cc", ".c", ".h", ".hpp"}

def run_git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr.strip() or "git command failed")
    return p.stdout.strip()

def repo_metadata(repo: Path) -> dict:
    is_repo = (repo / ".git").exists()
    return {
        "path": str(repo.resolve()),
        "is_git_repository": is_repo,
        "commit": run_git(repo, "rev-parse", "HEAD") if is_repo else None,
        "branch": run_git(repo, "branch", "--show-current") if is_repo else None,
        "dirty": bool(run_git(repo, "status", "--porcelain")) if is_repo else None,
    }

def source_files(repo: Path):
    for p in repo.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in EXTENSIONS:
            continue
        if any(part in IGNORE_DIRS for part in p.parts):
            continue
        try:
            if p.stat().st_size <= 1_000_000:
                yield p
        except OSError:
            continue

def python_symbols(path: Path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, UnicodeError, OSError):
        return []
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.append({"name": node.name, "kind": type(node).__name__, "line": node.lineno})
    return out

def lexical_symbols(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    patterns = [
        (r"\b(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)", "function"),
        (r"\b(?:export\s+)?class\s+([A-Za-z_$][\w$]*)", "class"),
        (r"\b(?:class|struct)\s+([A-Za-z_]\w*)", "class_or_struct"),
        (r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>", "arrow_function"),
    ]
    out = []
    for pattern, kind in patterns:
        for m in re.finditer(pattern, text):
            out.append({"name": m.group(1), "kind": kind, "line": text.count("\n", 0, m.start()) + 1})
    return out

def analyze_repository(repo_path: str) -> dict:
    repo = Path(repo_path).expanduser().resolve()
    if not repo.is_dir():
        raise FileNotFoundError(f"Repository directory does not exist: {repo}")
    files = list(source_files(repo))
    symbols, tests = [], []
    extension_counts = Counter()
    for path in files:
        rel = path.relative_to(repo).as_posix()
        extension_counts[path.suffix.lower()] += 1
        if "test" in path.name.lower() or "spec" in path.name.lower() or "tests" in rel.lower():
            tests.append(rel)
        found = python_symbols(path) if path.suffix.lower() == ".py" else lexical_symbols(path)
        for item in found:
            symbols.append({"file": rel, **item})
    return {
        "repository": repo.name,
        "metadata": repo_metadata(repo),
        "source_file_count": len(files),
        "test_file_count": len(tests),
        "extensions": dict(sorted(extension_counts.items())),
        "test_files": sorted(tests)[:200],
        "symbols": symbols[:2000],
    }

def propose_tasks(analysis: dict, limit: int = 10) -> list:
    tests = analysis["test_files"]
    tasks = []
    for sym in analysis["symbols"]:
        name, file = sym["name"], sym["file"]
        if name.startswith("_") or len(name) < 3:
            continue
        # Evidence is structural only; this does not claim a missing feature.
        related = [t for t in tests if Path(t).stem.lower().find(name.lower()) >= 0]
        evidence = "No direct test-file name match found by the prototype's lexical heuristic."
        if related:
            evidence = "Possible test-file name match: " + ", ".join(related[:3])
        seed = f'{analysis["repository"]}:{file}:{name}:{sym["line"]}'
        task_id = hashlib.sha256(seed.encode()).hexdigest()[:10]
        tasks.append({
            "task_id": task_id,
            "title": f"Investigate behavior and test coverage for {name}",
            "target": {"file": file, "symbol": name, "kind": sym["kind"], "line": sym["line"]},
            "evidence": evidence,
            "task_type": "research_candidate",
            "confidence": "low",
            "status": "proposal_only",
            "acceptance_criteria": [
                "Document the current observable behavior of the target symbol.",
                "Add focused tests for normal, boundary, and invalid-input cases.",
                "Run the repository's relevant test suite and report the exact command and result."
            ],
            "adversarial_test_ideas": [
                "Empty and minimal input",
                "Boundary-sized and unusually large input",
                "Malformed or unexpected input",
                "Repeated calls and state-leakage checks"
            ],
            "limitations": "Candidate is generated from static symbol inventory and filename heuristics; human review is required."
        })
    tasks.sort(key=lambda x: (x["target"]["file"], x["target"]["line"], x["task_id"]))
    return tasks[:limit]

def create_report(repo_path: str, limit: int = 10) -> dict:
    analysis = analyze_repository(repo_path)
    tasks = propose_tasks(analysis, limit)
    return {
        "product": "AUREX",
        "version": "2.0.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": "static source inventory + deterministic, evidence-labelled task candidates",
        "repository": analysis["repository"],
        "repository_metadata": analysis["metadata"],
        "summary": {
            "source_files": analysis["source_file_count"],
            "test_files": analysis["test_file_count"],
            "symbols_indexed": len(analysis["symbols"]),
            "task_candidates": len(tasks)
        },
        "analysis": analysis,
        "task_candidates": tasks,
        "validation": {
            "upstream_tests_executed": False,
            "feature_patches_generated": False,
            "sandboxed_execution": False,
            "note": "AUREX 2.0 prototype does not claim upstream correctness or automatic feature implementation."
        }
    }

def save_report(report: dict, output: str):
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path
