from typing import List, Dict, Any

def quality_gate(static_issues: List[tuple[int, str]], llm_result: Dict[str, Any]) -> bool:
    """
    Determine if the code passes the quality gate.
    Fails if any high severity LLM issue or overall_quality is 'fail'.
    Static issues alone do not cause a fail (but you could add thresholds).
    """
    if llm_result.get("overall_quality") == "fail":
        return False
    for issue in llm_result.get("issues", []):
        if issue.get("severity") == "high":
            return False
    return True