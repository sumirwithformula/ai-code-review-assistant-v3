from typing import List, Tuple, Dict, Any

def merge_issues(static_issues: List[Tuple[int, str]], llm_issues: List[Dict]) -> List[Dict]:
    """
    Combine static and LLM issues. Deduplicate based on line number and message similarity.
    For simplicity, we dedupe if same line and similar message (case-insensitive substring).
    """
    # Convert static issues to dict form
    static_dicts = []
    for line, msg in static_issues:
        static_dicts.append({
            "line": line,
            "severity": "low",   # flake8 doesn't give severity, we treat as low
            "category": "style",
            "description": msg,
            "suggested_fix": "",
            "source": "static"
        })
    
    # Add llm issues with source flag
    for issue in llm_issues:
        issue["source"] = "llm"
    
    combined = static_dicts + llm_issues
    
    # Deduplicate by line + message substring (simple approach)
    deduped = []
    seen = set()
    for issue in combined:
        key = (issue["line"], issue["description"][:30].lower())  # first 30 chars as fingerprint
        if key not in seen:
            seen.add(key)
            deduped.append(issue)
    return deduped