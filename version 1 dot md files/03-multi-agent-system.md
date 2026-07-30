# Project 3: Multi-Agent Task Automation System

**Build this last.** ~1–2 days, most involved of the three. Reuses the
structured-output pattern from Project 1 and the "grounding via retrieved
context" pattern from Project 2, now across multiple coordinated LLM calls.

**Maps to JD:** Build and orchestrate multi-agent AI systems · Design
AI-native solutions, agentic workflows, and enterprise-scale AI
architectures · Establish governance, escalation, and human-AI collaboration
patterns.

**Stack:** Python, LangGraph, Claude/OpenAI API, one tool for at least one
agent to call (web search — e.g. Tavily — or a local document lookup).

---

## Architecture

```
                     ┌─────────────────────────┐
                     │        Planner Agent       │
                     │  breaks user task into      │
                     │  ordered sub-tasks           │
                     └────────────┬────────────┘
                                  │ sub-task list (shared state)
                                  ▼
                     ┌─────────────────────────┐
                     │      Retriever Agent        │
                     │  calls a tool per sub-task    │
                     └────────────┬────────────┘
                                  │ gathered info (shared state)
                                  ▼
                     ┌─────────────────────────┐
                     │       Writer Agent           │
                     │  synthesizes into final       │
                     │  answer/report                │
                     └────────────┬────────────┘
                                  │
                     ┌────────────┴────────────┐
                     │   Conditional routing:      │
                     │   if self-check fails,        │
                     │   loop back to Retriever       │
                     └─────────────────────────┘
                                  │
                                  ▼
                           Final output to user
```

This is a LangGraph **StateGraph**: each agent is a node, a shared state
object carries the task/gathered info/draft between nodes, and conditional
edges define the loop-back logic.

---

## Step-by-step

### 1. Pick a concrete, demoable task type
E.g. "given a topic, research it and write a 200-word summary with sources."
Simple enough to finish in the time budget, complex enough to genuinely need
3 agents.

### 2. Define the shared state schema
```python
from typing import TypedDict, List

class AgentState(TypedDict):
    task: str
    subtasks: List[str]
    gathered_info: List[str]
    draft: str
    is_approved: bool
```

### 3. Build the Planner node
```python
def planner(state: AgentState) -> AgentState:
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content":
            f'Break this task into 2-4 concrete research sub-questions. '
            f'Return ONLY a JSON list of strings.\nTask: {state["task"]}'}],
    )
    state["subtasks"] = json.loads(resp.content[0].text)
    return state
```

### 4. Build the Retriever node
```python
def retriever(state: AgentState) -> AgentState:
    info = state.get("gathered_info", [])
    for sub in state["subtasks"]:
        result = web_search_tool(sub)   # e.g. Tavily API call
        info.append(f"{sub}: {result}")
    state["gathered_info"] = info
    return state
```

### 5. Build the Writer node
```python
def writer(state: AgentState) -> AgentState:
    context = "\n".join(state["gathered_info"])
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content":
            f'Write a 200-word summary with sources, using only this info:\n{context}\n\n'
            f'Then on a new line write ONLY "APPROVED" if the info was sufficient, '
            f'or "INSUFFICIENT" if more research is needed.'}],
    )
    text = resp.content[0].text
    state["draft"] = text
    state["is_approved"] = "APPROVED" in text.upper()
    return state
```

### 6. Wire the graph
```python
from langgraph.graph import StateGraph, END

graph = StateGraph(AgentState)
graph.add_node("planner", planner)
graph.add_node("retriever", retriever)
graph.add_node("writer", writer)

graph.set_entry_point("planner")
graph.add_edge("planner", "retriever")
graph.add_edge("retriever", "writer")

def check_approval(state: AgentState) -> str:
    return "approved" if state["is_approved"] else "not_approved"

graph.add_conditional_edges("writer", check_approval, {
    "approved": END,
    "not_approved": "retriever",
})

app = graph.compile()
```

### 7. Add basic logging
```python
def planner(state: AgentState) -> AgentState:
    print(f"[planner] input task: {state['task']}")
    ...
    print(f"[planner] output subtasks: {state['subtasks']}")
    return state
```
Do this for every node. This "observability" angle is explicitly called out
in the JD ("observability, drift monitoring, guardrails") — cheap to add,
strong to mention.

### 8. Test on 2–3 different task topics
Pick at least one topic where the first research pass is likely to be thin,
so you can show the loop-back (`writer → retriever`) actually firing. This
is the single most impressive thing to demo — it proves you understand
agentic control flow, not just a linear chain of calls.

---

## Testing checklist
- [ ] 1 topic where the first pass succeeds cleanly (no loop-back)
- [ ] 1 topic engineered to trigger loop-back at least once — log and save
      this run's transcript for the interview
- [ ] Add a max-loop guard (e.g. cap at 2 loop-backs) so a stuck run can't
      infinite-loop and burn API credits
- [ ] Count total LLM calls and rough wall-clock time per run

## What to capture for your resume/interview
- The state schema and why you chose those fields — shows deliberate design,
  not just "I called LangGraph."
- A concrete transcript of the conditional loop-back triggering — this is
  your strongest talking point.
- LLM calls per run and rough latency (e.g. "~4 LLM calls, ~15s per run on
  the happy path, up to 2 loop-backs allowed").

### Resume bullet template
> Designed and built a multi-agent research-and-writing system (LangGraph
> StateGraph) with Planner, Retriever, and Writer agents coordinating over
> shared state, including conditional loop-back routing on a self-check
> flag; tested across [N] task topics, with loop-back logic verified to
> trigger correctly at least [X] time(s); averaged [Y] LLM calls and ~[Z]s
> per run.

---

## Cross-project tips (apply to all three)
- **Keep API costs low while building:** use Haiku/mini-tier models during
  development, switch to a stronger model only for the final demo run.
- **Version control everything** in a public/shareable GitHub repo — clean
  commit history is itself a small signal given how Git/CI-CD heavy the JD
  is.
- **Write a short README per project** (problem, architecture diagram, how
  to run it, one example interaction). This doubles as your source when you
  go back and fill in the resume bullet placeholders with real numbers.
