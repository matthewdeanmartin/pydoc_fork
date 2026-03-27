# Agent Mandates

- **Dependency Management:** Use `uv` and `uv run` for all commands and operations. Avoid using the system Python or `pip` directly.
- **Testing and Linting:** Prefer using the `Makefile` for all testing and linting. LLMs should prioritize the `-llm` targets (e.g., `make pytest-llm`, `make check-llm`) to minimize token usage and output noise.
