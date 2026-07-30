# Project 1: AI Code Review & Validation Assistant

**Build this first.** ~1 day. Lowest complexity, highest resume-relevance for
"AI Quality Gates" / "validate AI-generated code" JD language.

**Maps to JD:** Validate AI-generated code for quality and correctness · AI
Quality Metrics · Integrate AI validation, testing, and quality gates into
CI/CD pipelines.

**Stack:** Python, Claude or OpenAI API, `flake8`/`pylint` (optional but
recommended), optional GitHub API for pulling real PR diffs.

---

## Architecture

```
 Code diff (.patch / .py file / GitHub PR)
        │
        ▼
 ┌────────────────────┐
 │  Static analysis    │  flake8 / pylint — cheap, deterministic checks
 └─────────┬──────────┘
           │ issues (list)
           ▼
 ┌────────────────────┐
 │   LLM Reviewer      │  Claude/OpenAI call, structured-output prompt
 └─────────┬──────────┘
           │ JSON: [{issue, severity, line, suggested_fix}]
           ▼
 ┌────────────────────┐
 │   Quality Gate      │  combine static + LLM → pass/fail decision
 └─────────┬──────────┘
           ▼
   Report (CLI / JSON file / FastAPI response)
```

---

## Step-by-step

### 1. Get sample input
Use a few of your own commits as test diffs — real, personal data makes the
demo credible in an interview.
```bash
git diff HEAD~1 > sample.patch
```

### 2. Static analysis pass (deterministic baseline)
```bash
flake8 path/to/file.py --format='%(row)d:%(col)d %(code)s %(text)s'
```
Parse this into a list of `(line, message)` tuples. This is the
"rule-based" half of "combine rule-based + LLM-based checks" — call this
out explicitly in your interview, it's exactly what "AI Quality" means in
production.

### 3. Design the LLM prompt for structured output
```python
PROMPT = """You are a senior code reviewer. Given this diff, return ONLY
valid JSON, no prose, no markdown fences:

{
  "issues": [
    {"line": <int>, "severity": "low|medium|high",
     "category": "bug|style|correctness|security",
     "description": "...", "suggested_fix": "..."}
  ],
  "overall_quality": "pass|fail"
}

Diff:
{diff_text}
"""
```
```python
import anthropic, json

client = anthropic.Anthropic()

def review_diff(diff_text: str) -> dict:
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",  # cheap/fast for dev
        max_tokens=1000,
        messages=[{"role": "user", "content": PROMPT.format(diff_text=diff_text)}],
    )
    raw = resp.content[0].text.strip()
    return json.loads(raw)
```
Tip: if JSON parsing ever fails, add `"Respond with nothing but the JSON
object."` as a hard constraint and strip any leading/trailing backticks
before `json.loads`.

### 4. Parse and merge results
Combine static-analysis issues + LLM issues into one list. De-dupe obvious
overlaps (e.g. same line number, similar message text — a simple string
similarity check is enough, no need for anything fancy).

### 5. Quality gate logic
```python
def quality_gate(static_issues, llm_result) -> bool:
    if any(i["severity"] == "high" for i in llm_result["issues"]):
        return False
    if llm_result["overall_quality"] == "fail":
        return False
    return True
```
This rule — "fail on any HIGH severity issue" — *is* your quality gate. Same
concept as a CI/CD gate, just running at prototype scale.

### 6. Wrap it in something runnable
Simplest: CLI script.
```python
# review.py
import sys
if __name__ == "__main__":
    diff_path = sys.argv[1]
    diff_text = open(diff_path).read()
    static_issues = run_flake8(diff_path)
    llm_result = review_diff(diff_text)
    passed = quality_gate(static_issues, llm_result)
    print(json.dumps({"passed": passed, "static": static_issues, "llm": llm_result}, indent=2))
```
Slightly more polished: a FastAPI endpoint that accepts a diff and returns
the JSON report — nice if you want a live demo in the interview instead of a
terminal screenshot.

### 7. (Optional, time permitting) Hook into GitHub
Pull a real PR diff via the GitHub API instead of a local file:
```python
import requests
def fetch_pr_diff(owner, repo, pr_number, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {"Accept": "application/vnd.github.v3.diff", "Authorization": f"token {token}"}
    return requests.get(url, headers=headers).text
```
This turns "it reviews diffs" into "it reviews real PRs" — a much stronger
interview demo.

### 8. Test on 3–5 diffs
Include some clean diffs and some with an **intentionally introduced bug**
(off-by-one, missing null check, SQL string concat, etc.) so you can show it
catching real issues live.

---

## Testing checklist
- [ ] 2 clean diffs → both pass the gate
- [ ] 2–3 diffs with an injected bug each → gate fails, correct line flagged
- [ ] 1 diff with a subtle issue (e.g. off-by-one) → check if LLM catches
      what flake8 misses (this is your "why LLM + static both matter" story)
- [ ] Record latency per review call (`time.perf_counter()` around the API
      call is enough)

## What to capture for your resume/interview
- Number of diffs tested, and hit rate on injected bugs (e.g. "caught 7/8
  intentionally injected bugs across 5 test diffs").
- Explicit note that you combined static + LLM checks — shows you understand
  *why* pure LLM judgment isn't sufficient for production quality gates.
- Latency/cost per review call (e.g. "~2s per review call on Haiku, ~$0.001
  per diff").

### Resume bullet template
> Built an AI-assisted code review tool combining static analysis (flake8)
> with an LLM-based structured-output reviewer (Claude API) to implement an
> automated quality gate; tested on [N] diffs, catching [X/Y] intentionally
> injected defects with ~[Z]s latency per review.
