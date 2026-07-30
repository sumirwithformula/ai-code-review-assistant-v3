# Project 2: RAG-Based Knowledge Assistant

**Build this second.** ~1 day. Builds on Project 1's "structured LLM output"
pattern, adds retrieval + grounding on top.

**Maps to JD:** Design and build RAG pipelines, vector stores, and knowledge
bases · Design context engineering, retrieval, and grounding strategies to
improve AI accuracy and reliability.

**Stack:** Python, LangChain, Chroma or FAISS, an embedding model
(OpenAI/Claude embeddings, or `sentence-transformers` for a free local
option), Claude/OpenAI API for generation, Streamlit for the UI.

---

## Architecture

```
 Source documents (PDFs, .md notes, reports)
        │
        ▼
 ┌────────────────────┐
 │   Chunking          │  ~300–500 token chunks, ~50 token overlap
 └─────────┬──────────┘
           ▼
 ┌────────────────────┐
 │   Embedding         │  embed each chunk
 └─────────┬──────────┘
           ▼
 ┌────────────────────┐
 │  Vector Store       │  Chroma/FAISS — vectors + metadata (source, page)
 └─────────┬──────────┘
           │ (at query time)
           ▼
 User question → embed query → similarity search → top-k chunks
           │
           ▼
 ┌────────────────────┐
 │  Prompt assembly    │  "Answer using ONLY this context. Cite sources."
 └─────────┬──────────┘
           ▼
 ┌────────────────────┐
 │  LLM generation     │
 └─────────┬──────────┘
           ▼
   Answer + cited source chunks → Streamlit chat UI
```

---

## Step-by-step

### 1. Pick your document set
Use something real and personal — reports, class notes, or project write-ups
you already have. Authentic data = an easier interview conversation than a
generic Wikipedia dump.

### 2. Chunk the documents
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
chunks = splitter.split_documents(docs)  # docs loaded via a LangChain loader
```
Keep the source filename (and page number, if PDF) attached to each chunk's
metadata — you need this later for citations.

### 3. Embed and store
```python
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # free, local
vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")
```
Chroma is the simplest to set up locally — no server needed for a prototype.

### 4. Build the retriever
```python
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
```

### 5. Prompt template — answer only from context
```python
RAG_PROMPT = """Answer the question using ONLY the context below. If the
answer isn't in the context, say "I don't know based on the provided
documents" — do not make anything up.

Context:
{context}

Question: {question}
"""

def answer(question: str):
    docs = retriever.invoke(question)
    context = "\n\n".join(f"[{d.metadata['source']}]: {d.page_content}" for d in docs)
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": RAG_PROMPT.format(context=context, question=question)}],
    )
    return resp.content[0].text, docs
```
The "say I don't know" instruction is your hallucination-avoidance strategy
— call it out explicitly, it's directly what "grounding" and "reliability"
mean in the JD.

### 6. Add citations
Return the `docs` (with `.metadata['source']`) alongside the answer so the
UI can show which chunks were actually used.

### 7. Build the UI
```python
import streamlit as st

st.title("Knowledge Assistant")
q = st.text_input("Ask a question")
if q:
    ans, sources = answer(q)
    st.write(ans)
    with st.expander("Sources"):
        for d in sources:
            st.write(f"**{d.metadata['source']}**: {d.page_content[:200]}...")
```

### 8. Test edge cases
- Ask something the documents don't cover → confirm it says "I don't know"
  rather than fabricating an answer.
- Ask something ambiguous → check which chunks retrieval pulls back and
  whether the answer is reasonable given them.

---

## Testing checklist
- [ ] 8–10 questions with known answers in the docs → check correctness +
      correct source cited
- [ ] 2–3 out-of-scope questions → confirm "I don't know" response, no
      hallucination
- [ ] 1 ambiguous question → inspect retrieved chunks, sanity-check the
      answer
- [ ] Record chunk count, doc count, and retrieval `k` used

## What to capture for your resume/interview
- Number of documents/pages indexed, total chunk count.
- Retrieval evaluation, even informal: "tested 10 questions, 8/10 answered
  correctly with the right source cited."
- Your hallucination-avoidance approach ("answer only from context, say I
  don't know otherwise") — this is a strong, specific talking point.

### Resume bullet template
> Built a RAG-based knowledge assistant (LangChain + Chroma) over [N]
> documents / [M] chunks, with grounded generation and source citation via
> the Claude API; evaluated on [X] test questions with [Y]/[X] correctly
> answered and sourced, using an explicit "answer only from context"
> strategy to reduce hallucination.
