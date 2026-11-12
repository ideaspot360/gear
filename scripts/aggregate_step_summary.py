#!/usr/bin/env python3
"""
H-GEAR STUDIO CI/CD Quality Gate Dynamic Step Summary Aggregator
Parses runtime JSON test artifacts from Job 1, Job 2, and Job 3.
Renders 100% truthful, 6-decimal precision raw metric tables to $GITHUB_STEP_SUMMARY.
Zero Tolerance for Hardcoding or Flattery Bias.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

EXPECTED_JOBS = [
    {
        "id": "backend-invariant-harness",
        "name": "Job 1",
        "file_names": ["job1_results.json", "reports/job1_results.json", "job1-results/job1_results.json"]
    },
    {
        "id": "diagram-quality-linter",
        "name": "Job 2",
        "file_names": ["diagram_results.json", "reports/diagram_results.json", "diagram-results/diagram_results.json"]
    },
    {
        "id": "blog-quality-multilingual-linter",
        "name": "Job 3",
        "file_names": ["blog_results.json", "reports/blog_results.json", "blog-results/blog_results.json"]
    }
]

def find_artifact_file(base_dir: Path, candidate_names: List[str]) -> Path | None:
    for name in candidate_names:
        p = base_dir / name
        if p.is_file():
            return p
        # Check recursive pattern
        matches = list(base_dir.glob(f"**/{Path(name).name}"))
        if matches:
            return matches[0]
    return None

def format_raw_value(val: Any, unit: str = "") -> str:
    if isinstance(val, float):
        if abs(val) < 1e-5 and val != 0:
            formatted = f"{val:.8f}".rstrip('0').rstrip('.')
            if len(formatted.split('.')[-1]) < 6:
                formatted = f"{val:.6f}"
        else:
            formatted = f"{val:.6f}"
        return f"{formatted} {unit}".strip()
    return f"{val} {unit}".strip()

def aggregate_summary(artifacts_dir: Path, output_summary_path: Path | None, output_verdict_path: Path) -> bool:
    all_passed = True
    total_metrics_count = 0
    passed_metrics_count = 0
    failed_metrics_count = 0
    
    summary_lines = []
    summary_lines.append("### 🛡️ H-GEAR STUDIO Quality Gate Audit Report (Zero-Tolerance)")
    summary_lines.append("")
    summary_lines.append("| Gate | Item | Standard | Raw Data (Runtime Output) | Status |")
    summary_lines.append("|---|---|---|---|:---:|")

    for job_info in EXPECTED_JOBS:
        job_label = job_info["name"]
        artifact_path = find_artifact_file(artifacts_dir, job_info["file_names"])
        
        if artifact_path is None:
            all_passed = False
            summary_lines.append(
                f"| **{job_label}** | Job Execution & Artifact | Artifact Generated | `MISSING / CRASHED` | 🔴 **FAIL** |"
            )
            continue
            
        try:
            with open(artifact_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            all_passed = False
            summary_lines.append(
                f"| **{job_label}** | JSON Artifact Parsing | Valid JSON | `Corrupted: {str(e)}` | 🔴 **FAIL** |"
            )
            continue

        metrics = data.get("metrics", [])
        if not metrics:
            all_passed = False
            summary_lines.append(
                f"| **{job_label}** | Metrics Content | >= 1 Metric | `Empty Metrics List` | 🔴 **FAIL** |"
            )
            continue

        for m in metrics:
            total_metrics_count += 1
            item = m.get("item", "Unknown Item")
            standard = m.get("standard", "N/A")
            raw_val = m.get("raw_value", "N/A")
            unit = m.get("unit", "")
            raw_str = format_raw_value(raw_val, unit)
            status = m.get("status", "FAIL").upper()
            
            if status == "PASS":
                passed_metrics_count += 1
                badge = "🟢 `PASS`"
            else:
                failed_metrics_count += 1
                all_passed = False
                badge = "🔴 `FAIL`"
                
            summary_lines.append(f"| **{job_label}** | {item} | {standard} | {raw_str} | {badge} |")

    summary_lines.append("")
    if all_passed and total_metrics_count > 0:
        summary_lines.append(
            f"**Final Gate Decision**: 🟢 **ALL CHECKS PASSED ({passed_metrics_count}/{total_metrics_count}) — APPROVED FOR PRODUCTION DEPLOYMENT**"
        )
    else:
        all_passed = False
        summary_lines.append(
            f"**Final Gate Decision**: 🔴 **ZERO-TOLERANCE GATE FAILED ({failed_metrics_count} failed or missing) — DEPLOYMENT BLOCKED**"
        )
    summary_lines.append("")

    markdown_report = "\n".join(summary_lines)
    
    # 1. Output to $GITHUB_STEP_SUMMARY
    github_step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if github_step_summary:
        with open(github_step_summary, "a", encoding="utf-8") as f:
            f.write(markdown_report + "\n")
    elif output_summary_path:
        output_summary_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_summary_path, "w", encoding="utf-8") as f:
            f.write(markdown_report + "\n")
            
    # 2. Output verdict JSON for subsequent CI steps
    verdict_data = {
        "all_passed": all_passed,
        "total_metrics": total_metrics_count,
        "passed_count": passed_metrics_count,
        "failed_count": failed_metrics_count
    }
    output_verdict_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_verdict_path, "w", encoding="utf-8") as f:
        json.dump(verdict_data, f, indent=2)
        
    print(markdown_report)
    return all_passed

def main():
    parser = argparse.ArgumentParser(description="Aggregate CI/CD QA test results into Step Summary.")
    parser.add_argument("--artifacts-dir", type=Path, default=Path("reports/artifacts"), help="Directory containing downloaded test artifacts")
    parser.add_argument("--output-summary", type=Path, default=None, help="Optional output markdown file path")
    parser.add_argument("--output-verdict", type=Path, default=Path("reports/artifacts/aggregated_gate_verdict.json"), help="Output JSON verdict file path")
    
    args = parser.parse_args()
    success = aggregate_summary(args.artifacts_dir, args.output_summary, args.output_verdict)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
