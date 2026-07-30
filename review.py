import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Tuple, Dict, Any

# Load environment variables from .env file (if present)
load_dotenv()
# Import our modular components
from reviewer.static import run_flake8
from reviewer.llm import review_diff
from reviewer.merge import merge_issues
from reviewer.gate import quality_gate

def main():
    # Check command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python review.py <path_to_diff_or_py_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Read the entire diff/file content
    try:
        diff_text = Path(file_path).read_text(encoding='utf-8')
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Static analysis – only works if the input is a .py file (not a patch)
    if file_path.endswith('.py'):
        print("Running static analysis (flake8)...")
        static_issues = run_flake8(file_path)
        print(f"Static analysis found {len(static_issues)} issues.")
    else:
        print("Skipping static analysis (input is not a .py file).")
        static_issues = []

    # LLM review – measure latency
    print("Sending diff to Gemini for review...")
    start_time = time.perf_counter()
    llm_result = review_diff(diff_text)
    elapsed = time.perf_counter() - start_time
    print(f"LLM review completed in {elapsed:.2f} seconds.")

    # Merge static and LLM issues (de‑duplicate)
    merged = merge_issues(static_issues, llm_result.get("issues", []))

    # Apply the quality gate
    passed = quality_gate(static_issues, llm_result)

    # Build final report
    report = {
        "passed": passed,
        "static_issues_count": len(static_issues),
        "llm_issues_count": len(llm_result.get("issues", [])),
        "merged_issues": merged,
        "llm_overall_quality": llm_result.get("overall_quality"),
        "latency_sec": elapsed,
    }

    # Print the report as pretty JSON
    print(json.dumps(report, indent=2))

    # Exit with appropriate code (0 = success, 1 = gate failed)
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()