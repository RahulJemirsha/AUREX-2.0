import tempfile, unittest
from pathlib import Path
from aurex.core import analyze_repository, propose_tasks, create_report

class AurexV2Tests(unittest.TestCase):
    def test_python_symbol_inventory(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sample.py").write_text("class Engine:\n    def evolve(self):\n        return True\n")
            (root / "test_engine.py").write_text("def test_evolve(): pass\n")
            a = analyze_repository(str(root))
            names = {s["name"] for s in a["symbols"]}
            self.assertIn("Engine", names)
            self.assertIn("evolve", names)
            self.assertEqual(a["test_file_count"], 1)

    def test_deterministic_task_ids(self):
        analysis = {"repository":"demo", "test_files":[], "symbols":[
            {"name":"calculate","file":"app.py","kind":"FunctionDef","line":2}
        ]}
        first = propose_tasks(analysis)
        second = propose_tasks(analysis)
        self.assertEqual(first[0]["task_id"], second[0]["task_id"])
        self.assertEqual(first[0]["status"], "proposal_only")

    def test_report_marks_unrun_tests(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "module.py").write_text("def hello(): return 'hi'\n")
            report = create_report(str(root))
            self.assertFalse(report["validation"]["upstream_tests_executed"])

if __name__ == "__main__":
    unittest.main()
