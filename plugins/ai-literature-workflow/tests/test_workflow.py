from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"


def run_script(name: str, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / name), *args],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != expected:
        raise AssertionError(
            f"{name} returned {result.returncode}, expected {expected}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class WorkflowIntegrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "research"
        run_script(
            "init_research_project.py",
            "--root",
            str(self.project),
            "--project-id",
            "test-project",
            "--title",
            "Efficient inference for language models",
            "--profile",
            "review",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def log(self, decision_type: str, rationale: str) -> None:
        run_script(
            "log_decision.py",
            "--project",
            str(self.project),
            "--type",
            decision_type,
            "--choice",
            "approve",
            "--rationale",
            rationale,
        )

    def validate(self, gate: str) -> None:
        run_script(
            "validate_gate.py",
            "--project",
            str(self.project),
            "--gate",
            gate,
            "--write",
        )

    def test_initial_project_blocks_at_g0(self) -> None:
        result = run_script(
            "validate_gate.py",
            "--project",
            str(self.project),
            "--next",
            expected=1,
        )
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["failed_gate"], "G0")

    def test_init_rejects_filesystem_root(self) -> None:
        filesystem_root = str(Path(self.project.anchor))
        run_script(
            "init_research_project.py",
            "--root",
            filesystem_root,
            expected=1,
        )

    def test_dedupe_refuses_existing_output_by_default(self) -> None:
        raw = self.project / "search" / "raw_results.csv"
        run_script(
            "normalize_and_dedupe.py",
            "--input",
            str(raw),
            "--output",
            str(self.project / "search" / "deduped.csv"),
            expected=1,
        )

    def test_duplicate_doi_is_removed(self) -> None:
        raw = self.project / "search" / "raw_results.csv"
        fields = [
            "paper_id", "title", "authors", "year", "venue", "doi", "arxiv_id", "url", "abstract", "source", "retrieved_at", "status", "citation_count",
        ]
        rows = [
            {"paper_id": "p1", "title": "Paper One", "year": "2025", "doi": "https://doi.org/10.1000/ABC", "source": "OpenAlex", "retrieved_at": "2026-11-13"},
            {"paper_id": "p2", "title": "Paper One extended title", "year": "2025", "doi": "10.1000/abc", "source": "Crossref", "retrieved_at": "2026-11-13", "abstract": "longer abstract"},
        ]
        write_csv(raw, fields, rows)
        run_script("normalize_and_dedupe.py", "--input", str(raw), "--output", str(self.project / "search" / "deduped.csv"), "--overwrite")
        with (self.project / "search" / "deduped.csv").open(encoding="utf-8", newline="") as handle:
            deduped = list(csv.DictReader(handle))
        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0]["doi"], "10.1000/abc")
        self.assertIn("OpenAlex", deduped[0]["source"])
        self.assertIn("Crossref", deduped[0]["source"])

    def test_full_gate_sequence_and_package(self) -> None:
        (self.project / "planning" / "question_card.md").write_text("""# Research Question Card

## Research question
How do inference-efficiency methods trade accuracy for latency?

## Why it matters
The result informs model deployment under limited compute.

## Scope
Transformer inference on language-model benchmarks.

## Out of scope
Training from scratch and hardware fabrication.

## Time range
2022 through 2026.

## Success criteria
Evidence from multiple method families with comparable evaluations.

## Output form
A thesis-related-work section.
""", encoding="utf-8")
        self.log("scope_approval", "The question and thesis relation match my research plan.")
        self.validate("G0")
        (self.project / "search" / "search_protocol.md").write_text("""# Search Protocol

## Sources
arXiv, OpenAlex, Crossref, Semantic Scholar, and OpenReview.

## Queries
quantization, distillation, sparse attention, speculative decoding.

## Date range
2022 through 2026.

## Inclusion criteria
Peer-reviewed or influential preprint work with inference experiments.

## Exclusion criteria
Training-only optimization and papers without language-model evaluation.

## Screening process
Title and abstract screening followed by full-text verification.
""", encoding="utf-8")
        self.log("search_protocol_approval", "The sources and criteria cover my research question.")
        self.validate("G1")
        paper_id = "doi_10_1000_demo"
        raw_fields = ["paper_id", "title", "authors", "year", "venue", "doi", "arxiv_id", "url", "abstract", "source", "retrieved_at", "status", "citation_count"]
        write_csv(self.project / "search" / "raw_results.csv", raw_fields, [{"paper_id": paper_id, "title": "Efficient Inference Study", "year": "2025", "venue": "DemoConf", "doi": "10.1000/demo", "url": "https://example.org/demo", "source": "OpenAlex", "retrieved_at": "2026-11-13", "status": "peer-reviewed"}])
        write_csv(self.project / "search" / "screening.csv", ["paper_id", "title", "decision", "reason", "screener", "screened_at"], [{"paper_id": paper_id, "title": "Efficient Inference Study", "decision": "include", "reason": "Directly evaluates inference efficiency.", "screener": "human", "screened_at": "2026-11-13"}])
        corpus_row = {"paper_id": paper_id, "title": "Efficient Inference Study", "year": "2025", "venue": "DemoConf", "doi": "10.1000/demo", "arxiv_id": "", "bib_key": "smith2025efficient", "status": "peer-reviewed", "note_path": f"corpus/notes/{paper_id}.json"}
        write_csv(self.project / "corpus" / "index.csv", list(corpus_row), [corpus_row])
        self.log("corpus_freeze", "The included paper directly matches the approved scope.")
        self.validate("G2")
        card = {"paper_id": paper_id, "title": "Efficient Inference Study", "year": 2025, "venue": "DemoConf", "status": "peer-reviewed", "problem": "Reduce inference latency.", "method": "Structured sparse attention.", "datasets": ["DemoBench"], "baselines": ["Dense Transformer"], "metrics": ["latency", "accuracy"], "main_results": ["Lower latency at comparable accuracy."], "limitations": ["Single benchmark."], "claims_supported": ["C1"], "quality": "medium", "provenance": {"source": "OpenAlex", "url": "https://example.org/demo", "retrieved_at": "2026-11-13"}}
        write_json(self.project / "corpus" / "notes" / f"{paper_id}.json", card)
        write_csv(self.project / "analysis" / "evidence_matrix.csv", ["paper_id", "bib_key", "problem", "method", "datasets", "baselines", "metrics", "main_results", "limitations", "quality", "claims_supported"], [{"paper_id": paper_id, "bib_key": "smith2025efficient", "problem": card["problem"], "method": card["method"], "datasets": "DemoBench", "baselines": "Dense Transformer", "metrics": "latency; accuracy", "main_results": card["main_results"][0], "limitations": card["limitations"][0], "quality": "medium", "claims_supported": "C1"}])
        self.validate("G3")
        write_json(self.project / "analysis" / "quality_report.json", {"status": "PASS", "papers": {paper_id: {"quality": "medium", "supported_claims": ["C1"], "unsupported_or_conditional_claims": [], "risks": ["Single benchmark"], "rationale": "The result is relevant but not broadly validated."}}})
        self.log("quality_scope_approval", "I accept a benchmark-specific claim scope.")
        self.validate("G4")
        (self.project / "analysis" / "gap_map.md").write_text("# Research Gap Map\n\n## Gap 1\nCross-benchmark robustness is under-tested.\n", encoding="utf-8")
        (self.project / "synthesis" / "review_outline.md").write_text("# Review Outline\n\n## Efficient inference\nDiscuss sparse attention [@smith2025efficient].\n", encoding="utf-8")
        self.log("synthesis_approval", "The outline reflects the approved evidence and claim scope.")
        self.validate("G5")
        (self.project / "writing" / "related_work.md").write_text("# Related Work\n\nSparse attention reduces latency in the reviewed benchmark [@smith2025efficient].\n", encoding="utf-8")
        self.validate("G6")
        (self.project / "references" / "references.bib").write_text("""@inproceedings{smith2025efficient,
  title = {Efficient Inference Study},
  author = {Smith, Alex},
  year = {2025},
  booktitle = {DemoConf},
  doi = {10.1000/demo}
}
""", encoding="utf-8")
        run_script("audit_citations.py", "--project", str(self.project), "--write")
        self.validate("G7")
        write_json(self.project / "audit" / "consistency.json", {"status": "PASS"})
        write_json(self.project / "audit" / "final_audit.json", {"status": "PASS"})
        self.log("submission_approval", "I approve the final claim scope for this package.")
        self.validate("G8")
        manifest = json.loads((self.project / "planning" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["last_passed_gate"], "G8")
        self.assertTrue(manifest["allowed"]["final_export"])
        package = self.project / "research-package.zip"
        run_script("build_research_package.py", "--project", str(self.project), "--output", str(package))
        self.assertTrue(package.exists())


if __name__ == "__main__":
    unittest.main()
