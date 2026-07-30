# AI Project Build Guide — Cognizant Ace Frontier Engineer Application

Three projects, each buildable in 1–2 days, designed to map directly onto the
Ace Team JD (RAG pipelines, multi-agent systems, AI code validation/quality
gates). Build in this order: **Code Review Assistant → RAG Assistant →
Multi-Agent System** (easiest/fastest to hardest).

Once each is done, update the corresponding entry in `resume.tex` with real
numbers (dataset size, latency, accuracy, etc.) instead of the bracketed
placeholder text.

---

## Project 1: AI Code Review & Validation Assistant

**Maps to JD:** "Validate AI-generated code for quality and correctness",
"AI Quality Metrics", "Integrate AI validation, testing, and quality gates
into CI/CD pipelines."

**Estimated time:** ~1 day
**Stack:** Python, Claude or OpenAI API (no agent framework needed), optional
`flake8`/`pylint`, optional GitHub API

### Architecture

```
 Code diff (.patch / .py file / GitHub PR)
        │
        ▼
 ┌───────────────────┐
 │  Static analysis   │  (flake8 / pylint — cheap, deterministic checks)
 └─────────┬─────────┘
           │  issues (list)
           ▼
 ┌───────────────────┐
 │   LLM Reviewer      │  Claude/OpenAI API call with a structured-output
 │   (prompt + diff)   │  prompt: "review this diff, return JSON"
 └─────────┬─────────┘
           │  JSON: [{issue, severity, line, suggested_fix}]
           ▼
 ┌───────────────────┐
 │  Quality Gate       │  combine static + LLM results → pass/fail decision
 │  (rule: no HIGH      │  based on severity threshold
 │  severity issues)   │
 └─────────┬─────────┘
           │
           ▼
   Report (CLI output / JSON file / simple FastAPI response)
```

### Step-by-step

1. **Get sample input.** Use a few of your own commits (e.g. Formula Manipal
   telemetry code, or the music recommendation project) as test diffs.
   `git diff HEAD~1` is enough to get a real diff to test on.
2. **Static analysis pass.** Run `flake8` or `pylint` on the changed file(s),
   capture output as a list of `(line, message)` issues. This is your
   deterministic baseline — cheap and fast, and it's good practice to combine
   rule-based + LLM-based checks (this is literally what "AI Quality" means
   in production systems).
3. **Design the LLM prompt for structured output.** Ask for JSON directly,
   e.g.:
   ```
   You are a code reviewer. Given this diff, return ONLY valid JSON:
   {
     "issues": [
       {"line": <int>, "severity": "low|medium|high",
        "category": "bug|style|correctness|security",
        "description": "...", "suggested_fix": "..."}
     ],
     "overall_quality": "pass|fail"
   }
   Diff:
   <diff text>
   ```
   Use the Claude API (`messages.create`) or OpenAI's function-calling /
   structured-output mode to guarantee valid JSON back.
4. **Parse and merge results.** Combine static-analysis issues and LLM
   issues into one list; de-duplicate obvious overlaps.
5. **Quality gate logic.** Define a simple rule: fail the check if any
   `severity: high` issue is found, or if the LLM sets `overall_quality:
   fail`. This is your "quality gate" — the same concept as CI/CD gating,
   just implemented at prototype scale.
6. **Wrap it in something runnable.** Simplest: a CLI script
   (`python review.py path/to/diff`). Slightly more polished: a small
   FastAPI endpoint that accepts a diff and returns the JSON report.
7. **(Optional, if you have time) Hook into GitHub.** Use the GitHub API to
   pull a real PR diff via its URL instead of a local file — this makes the
   demo much more concrete for an interview ("it reviews real PRs").
8. **Test on 3–5 diffs** (some clean, some with an intentionally introduced
   bug) so you can show it catching real issues in a demo.

### What to note for your resume/interview
- How many diffs you tested it on, and how many real/injected issues it
  caught vs. missed.
- Whether you combined static + LLM checks (this shows you understand why
  pure LLM judgment isn't enough for production quality gates).
- Any latency/cost numbers if you tracked them (e.g. "~2s per review call").

---

## Project 2: RAG-Based Knowledge Assistant

**Maps to JD:** "Design and build RAG pipelines, vector stores, and
knowledge bases", "Design context engineering, retrieval, and grounding
strategies to improve AI accuracy and reliability."

**Estimated time:** ~1 day
**Stack:** Python, LangChain, Chroma or FAISS (vector store), a sentence
embedding model (OpenAI/Claude embeddings, or `sentence-transformers` if you
want a free local option), Claude/OpenAI API for generation, Streamlit for
the UI

### Architecture

```
 Source documents (PDFs, .md notes, reports)
        │
        ▼
 ┌───────────────────┐
 │   Chunking          │  split into ~300-500 token chunks with overlap
 └─────────┬─────────┘
           ▼
 ┌───────────────────┐
 │   Embedding         │  embed each chunk (OpenAI/Claude embeddings API,
 │                     │  or sentence-transformers locally)
 └─────────┬─────────┘
           ▼
 ┌───────────────────┐
 │  Vector Store        │  Chroma or FAISS — stores chunk vectors + metadata
 │  (Chroma/FAISS)      │  (source file, page number)
 └─────────┬─────────┘
           │  (at query time)
           ▼
 User question ──► embed query ──► similarity search ──► top-k chunks
           │
           ▼
 ┌───────────────────┐
 │  Prompt assembly    │  "Answer using ONLY this context: <chunks>.
 │                     │   Question: <question>. Cite sources."
 └─────────┬─────────┘
           ▼
 ┌───────────────────┐
 │  LLM generation      │  Claude/OpenAI API call
 └─────────┬─────────┘
           ▼
   Answer + cited source chunks ──► displayed in Streamlit chat UI
```

### Step-by-step

1. **Pick your document set.** Use something real and personal — your
   Formula Manipal reports, class notes, or the water quality/Bayesian
   network project reports. This makes the demo authentic and easy to talk
   about.
2. **Chunk the documents.** Use LangChain's
   `RecursiveCharacterTextSplitter` (~300–500 tokens per chunk, ~50 token
   overlap). Keep track of source filename per chunk for later citation.
3. **Embed and store.** Use LangChain's `Chroma.from_documents()` (or FAISS
   equivalent) with an embedding model. Chroma is simplest to set up locally
   (no server needed for a prototype).
4. **Build the retriever.** `vectorstore.as_retriever(search_kwargs={"k":
   4})` — retrieves the top-4 most relevant chunks per query.
5. **Prompt template.** Use LangChain's `RetrievalQA` chain or build the
   prompt manually: inject retrieved chunks as context, instruct the model
   to answer only from that context and to say "I don't know" if the answer
   isn't there (this avoids hallucination — worth mentioning in an
   interview).
6. **Add citations.** Return which source chunk(s) were used alongside the
   answer — this is what "grounding" means in the JD's language.
7. **Build the UI.** A simple Streamlit app: text input for the question,
   display the answer + expandable "sources" section showing the retrieved
   chunks.
8. **Test edge cases.** Ask a question the documents don't cover, confirm it
   says it doesn't know rather than making something up. Ask something
   ambiguous, see how retrieval handles it.

### What to note for your resume/interview
- Number of documents/pages indexed, chunk count.
- How you evaluated retrieval quality (even informally — "tested 10
  questions, 8 were answered correctly with the right source cited").
- Any hallucination-avoidance strategy you used (this is a big talking
  point — "grounding" and "reliability" are explicitly in the JD).

---

## Project 3: Multi-Agent Task Automation System

**Maps to JD:** "Build and orchestrate multi-agent AI systems", "Design
AI-native solutions, agentic workflows, and enterprise-scale AI
architectures", "Establish governance, escalation, and human-AI
collaboration patterns."

**Estimated time:** ~1–2 days (most involved of the three)
**Stack:** Python, LangGraph, Claude/OpenAI API, a simple tool (e.g. a web
search function or a local document lookup) for at least one agent to call

### Architecture

```
                     ┌─────────────────────────┐
                     │        Planner Agent       │
                     │  breaks user task into      │
                     │  ordered sub-tasks           │
                     └────────────┬────────────┘
                                  │  sub-task list (shared state)
                                  ▼
                     ┌─────────────────────────┐
                     │      Retriever Agent        │
                     │  calls a tool (web search /  │
                     │  doc lookup) per sub-task     │
                     └────────────┬────────────┘
                                  │  gathered info (shared state)
                                  ▼
                     ┌─────────────────────────┐
                     │       Writer Agent           │
                     │  synthesizes gathered info    │
                     │  into a final answer/report   │
                     └────────────┬────────────┘
                                  │
                     ┌────────────┴────────────┐
                     │   Conditional routing:      │
                     │   if Writer's output fails    │
                     │   a self-check, loop back      │
                     │   to Retriever for more info    │
                     └─────────────────────────┘
                                  │
                                  ▼
                           Final output to user
```

This is a LangGraph **StateGraph**: each agent is a node, the shared state
object carries the task, gathered info, and draft output between nodes, and
edges (including conditional edges) define the flow.

### Step-by-step

1. **Pick a concrete task type.** Something demoable end-to-end, e.g. "given
   a topic, research it and write a 200-word summary with sources" — simple
   enough to finish in the time budget, complex enough to need 3 agents.
2. **Define the shared state schema.** A `TypedDict` with fields like
   `task`, `subtasks`, `gathered_info`, `draft`, `is_approved`.
3. **Build the Planner node.** An LLM call that takes the user's task and
   returns a short list of sub-tasks/questions to research (structured JSON
   output again, same pattern as Project 1).
4. **Build the Retriever node.** For each sub-task, call a tool — simplest
   option is a web search API (e.g. Tavily, or even a basic
   `requests`-based search wrapper) — and append results to
   `gathered_info` in the state.
5. **Build the Writer node.** An LLM call that takes `gathered_info` and
   produces the final draft, plus a simple self-check flag
   (`is_approved: true/false`) based on whether it has enough information.
6. **Wire the graph.** In LangGraph:
   `graph.add_node("planner", ...)`, `add_node("retriever", ...)`,
   `add_node("writer", ...)`, then `add_edge` for the linear path and
   `add_conditional_edges("writer", check_approval, {"approved": END,
   "not_approved": "retriever"})` for the loop-back case.
7. **Add basic logging.** Print/log each node's input and output as the
   graph runs — this "observability" angle is explicitly called out in the
   JD ("observability, drift monitoring, guardrails").
8. **Test on 2–3 different task topics** to confirm the loop-back logic
   actually triggers at least once (pick a topic where the first pass is
   likely to be insufficient, to show the conditional routing working).

### What to note for your resume/interview
- The state schema and why you chose those fields.
- A concrete example of the conditional loop-back triggering (this is the
  most "impressive" part to talk about — it shows you understand agentic
  control flow, not just chaining calls).
- Any cost/latency awareness (how many LLM calls per run, roughly how long
  it took).

---

## General tips that apply across all three

- **Keep API costs low while building:** use cheaper/faster models
  (e.g. Claude Haiku or GPT-4o-mini) during development, and only switch to
  a stronger model for the final demo run if needed.
- **Version control everything** in a public (or shareable private) GitHub
  repo — the JD environment leans heavily on Git/CI-CD, so having clean
  commit history itself is a small signal.
- **Write a short README per project** (problem, architecture diagram, how
  to run it, one example interaction) — this is what you'll actually show
  in an interview, and it doubles as your source for updating the resume
  bullet afterward.
