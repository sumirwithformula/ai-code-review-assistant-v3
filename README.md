
## Demo

Try it yourself!

1. Clone the repo
2. Create a `.env` file with your Gemini API key
3. Run: `python review.py tests/sample_patches/clean1.patch` (Clean)
4. Run: `python review.py tests/sample_patches/bug_sqlconcat.patch` (Flagged)


## Current Status & Limitations

**Currently, this tool only supports Python** via `flake8` for static analysis.

The **LLM review** works for **any language** (JavaScript, Go, Rust, etc.), but static analysis is Python‑only for now.

I will be on adding more languages and LLM providers!

---

## Roadmap

### Phase 1: Multi-Language Static Analysis (Coming Soon)
- JavaScript/TypeScript → ESLint
- Go → golangci-lint
- Rust → Clippy
- Java → Checkstyle
- Ruby → RuboCop
- C/C++ → Clang-Tidy

The architecture is already modular so I will just drop in a new linter!

### Phase 2: Multi-LLM Support (Coming Soon)
- **Anthropic Claude** – for deeper reasoning
- **OpenAI GPT-4** – for complex code reviews
- **Groq** – for ultra-fast, low-cost reviews
- **Local models** (Ollama) – for offline/private use

I intend to make switching between providers as simple as changing a single environment variable.

### Phase 3: CI/CD Integration (Coming not so soon to be very honest)
- GitHub Action integration
- GitLab CI support
- Jenkins pipeline integration
- Automatic PR commenting

---

## Contributing

Want to add support for your favorite language or LLM? 
- Fork the repo
- Add your linter to `reviewer/static.py`
- Submit a PR! (I will learn how to review a PR)

I am especially looking for help with Phase 3
---

