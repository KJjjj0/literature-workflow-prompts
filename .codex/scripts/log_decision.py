from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from common import safe_project_root, text_has_placeholder


ALLOWED_TYPES = {
    "scope_approval",
    "search_protocol_approval",
    "corpus_freeze",
    "quality_scope_approval",
    "synthesis_approval",
    "submission_approval",
    "scope_change",
    "claim_scope_change",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Append a human research decision.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--type", required=True, choices=sorted(ALLOWED_TYPES))
    parser.add_argument("--choice", default="approve")
    parser.add_argument("--rationale", default="")
    parser.add_argument("--evidence", action="append", default=[])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    supplied_rationale = args.rationale.strip()
    approval_choice = args.choice.casefold() in {"approve", "accept", "accepted", "ok"}
    requires_reason = args.type in {"scope_change", "claim_scope_change"} or not approval_choice
    if requires_reason and not supplied_rationale:
        raise SystemExit("This decision requires a short user-supplied rationale.")
    if supplied_rationale and text_has_placeholder(supplied_rationale):
        raise SystemExit("Rationale contains an unresolved placeholder.")
    project = safe_project_root(args.project)
    ledger = project / "planning" / "decisions.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    rationale = supplied_rationale or (
        f"User explicitly approved {args.type} for the displayed artifact; "
        "no additional rationale was supplied."
    )
    record = {
        "decision_id": f"{args.type}-{now}-{uuid4().hex[:8]}",
        "decision_type": args.type,
        "status": "DECIDED",
        "decided_by": "human",
        "choice": args.choice,
        "rationale": rationale,
        "rationale_source": "user_supplied" if supplied_rationale else "standardized_approval",
        "approval_basis": "explicit_user_approval",
        "evidence_refs": args.evidence,
        "decided_at": now,
    }
    with ledger.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps({"status": "PASS", "decision": record}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
