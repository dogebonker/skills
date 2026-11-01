# OBEY AI Systems Rules for LLM Components

## When to use

Use for any system or service where an LLM generates, classifies, extracts, retrieves, routes, judges, or takes actions through tools, and for the decision of whether an LLM belongs in the design at all.

## Primary bias to correct

Do not design LLM components as if model output were correct, well-formed, safe, cheap, fast, and deterministic, or as if more autonomy, more agents, more retrieval, or more training were the default path to quality.

## Decision rules

### Whether to use an LLM

- Use deterministic code or a rules engine when the task has clear rules, structured inputs, and no need for judgment. Reserve LLMs for complex judgment, rule sets too intricate to maintain, and heavy reliance on unstructured data. [S2]
- Start with the simplest design that meets the target: one LLM call with retrieval and in-context examples. Add steps, agents, or autonomy only when an eval shows the simpler design falls short. [S1]
- Set the required accuracy from the cost of each outcome (correct answer, wrong answer, escalation) and derive a break-even accuracy. Put a human in the decision when a single failure is expensive. [S4]
- Build on the provider API directly first. Adopt a framework only after reading the code beneath it, since hidden prompts and responses make failures hard to debug. [S1]

### Workflow or agent

- Use a fixed workflow with predefined code paths when the steps are known in advance. Use an agent only for open-ended problems where the step count cannot be predicted and the model's decisions can be trusted. [S1]
- Pick the workflow shape from the task structure: chain for fixed sequential subtasks with programmatic gates between steps, router when distinct input categories need different handling and classification is reliable, parallel sectioning for independent subtasks, parallel voting when several attempts raise confidence. [S1]
- Use orchestrator-workers only when subtasks cannot be known until runtime. Use evaluator-optimizer only when evaluation criteria are clear and iteration measurably improves output. [S1]
- Maximize one agent with tools before splitting into several. Split only for complex conditional logic or tool overload, then choose a manager that calls agents as tools or decentralized handoffs between peers. [S2]
- Give every agent loop explicit exit conditions: a final structured output, an error, or a maximum number of turns. Have the agent read ground truth from the environment (tool results, code execution) at each step. [S1] [S2]
- Design tools as a model-facing interface: clear names, documented parameters, examples, edge cases, and arguments shaped so mistakes are hard to make, such as requiring absolute paths. [S1]

### Knowledge: long context, RAG, fine-tuning

- Put the whole corpus in the prompt with prompt caching when it is under about 200,000 tokens. Build retrieval only above that size. [S3]
- Use RAG or context injection when the model lacks knowledge, needs current data, or needs proprietary data. Use fine-tuning for consistent format, style, or task behavior, never to add knowledge. [S4]
- Exhaust prompt design against an eval set before fine-tuning. When fine-tuning, start with about 50 examples that match production inputs, including any retrieved context. [S4]
- Retrieve with hybrid search: lexical BM25 for exact identifiers plus embeddings for meaning, merged with rank fusion. [S3]
- Chunk to a few hundred tokens at most, prepend a short document-level context to each chunk before indexing, retrieve wide (about 150 candidates), rerank, and pass about 20 chunks. Tune each value against retrieval evals. [S3]
- Enforce document permissions inside the vector store, accept knowledge only from trusted sources, tag data by access level, and keep immutable logs of retrieval. [S17]
- Return citations that point into source documents so claims are auditable. Check in code that each answer field carries at least one citation. [S11]
- Allow the model to answer "I don't know", restrict answers to provided documents, and validate critical claims outside the model before high-stakes use. [S10]

### Model, latency, and cost

- Prototype with the most capable model on every step to set a quality baseline, then swap smaller models step by step while evals hold the target. [S2]
- Route simple or common inputs to smaller, faster models and hard inputs to more capable ones. [S1] [S2]
- Measure baseline latency and time to first token per step. Meet latency budgets with model choice, shorter prompts and outputs, a hard max_tokens, and streaming. [S7]
- Order every prompt as stable prefix first (tools, system, reference material) and per-request content last, so the prefix is cacheable. A change to tool definitions invalidates the whole cache. [S5]
- Use prompt caching for repeated prefixes, with the default 5-minute lifetime for interactive traffic and the 1-hour lifetime for batch jobs with shared context. [S5] [S6]
- Send work that tolerates up to 24 hours of delay (evals, backfills, bulk extraction) through a batch API at half price. [S6]
- Cap cost per request and per user with input size limits, rate limits, quotas, limits on queued and total actions, and per-step timeouts. [S18]

### Evals as a component

- Write specific, measurable success criteria and an eval set before building. Mirror the real task distribution and include edge cases such as missing, overlong, harmful, and ambiguous inputs. [S8]
- Start with 20 to 50 tasks drawn from real failures and grow the set from bug reports, support queues, and production traces. [S9]
- Grade with code wherever an exact answer exists, with an LLM judge where nuance is needed, and with humans to validate. Prefer more automated cases over fewer hand-graded ones. [S8] [S9]
- Calibrate every LLM judge against human expert labels before trusting it. Give it a detailed rubric, an "Unknown" option, one dimension per judge, and a different model from the one under test. [S8] [S9]
- Keep a regression suite that runs near 100% and gate every prompt, model, retrieval, and tool change on it. Run several trials per task because outputs are non-deterministic. [S9]
- Read transcripts from eval runs to confirm graders measure what matters. Pair automated evals with production monitoring and periodic human review. [S9]

### Untrusted input and actions

- Treat retrieved documents, web pages, files, and tool results as data that may carry injected instructions. Mark and separate external content from instructions, and constrain model behavior to the task. [S14]
- Expose only the tools a feature needs, each with the narrowest function. Prefer granular tools over open-ended ones such as shell access or arbitrary URL fetch. [S16]
- Run tools under the end user's identity with the narrowest scope, and enforce authorization in the downstream system, not in the model. [S16]
- Rate each tool by read or write access, reversibility, permissions, and financial impact. Require human approval for high-risk and irreversible actions. [S2] [S14] [S16]
- Layer guardrails: rules-based checks (length limits, blocklists, regex), classifiers for relevance and safety, PII filtering on output, and moderation. One guardrail alone is unlikely to suffice. [S2]
- Test with adversarial inputs and prompt injection attempts before launch, and test agents in a sandbox. [S1] [S14]

### Output boundary

- Treat model output as untrusted user input: validate it before it reaches backends, encode it for its destination, use parameterized queries, and apply a strict content security policy. [S15]
- Define output formats and validate them. Use schema-constrained structured outputs or strict tool use for machine-read output. [S12] [S14]
- Handle refusal and max_tokens stop reasons explicitly, and check in code any constraint the schema cannot enforce, such as numeric ranges and string lengths. [S12]
- Keep authorization, policy, and rule checks in deterministic code. [S2] [S16]

### Failure handling

- Retry transient errors (connection errors, rate limits, 5xx, overload) with exponential backoff that honors retry-after, and bound the retry count. Treat spend-cap errors as non-retryable. [S13]
- Stream or batch long generations instead of holding long idle connections. [S13]
- Set timeouts and throttling on expensive steps, and degrade to partial function under load rather than failing completely. [S18]
- Define a fallback for each low-confidence or failed step: ask the user for more information, return to intent detection, or hand off to a human. [S4]
- Escalate to a human when an agent exceeds its retry or action limit. [S2]

### Observability

- Trace each run end to end with a span per model call, tool call, handoff, and guardrail check, and store inputs and outputs under an explicit sensitive-data policy. [S19]
- Log provider request IDs with each span so failures can be matched to provider records. [S13]
- Monitor production for drift and new failure modes, and feed failing traces back into the eval set. [S9]

## Trigger rules

- When proposing an agent or a multi-agent design, name the simpler workflow it replaces and the eval result that justifies the extra autonomy. [S1] [S2]
- When adding retrieval, state corpus size, the long-context alternative, the hybrid search and reranking plan, permission enforcement, and the retrieval eval. [S3] [S17]
- When proposing fine-tuning, show the failure is behavior or format, not missing knowledge, and that prompt design was exhausted against evals. [S4]
- When adding a tool, state its risk rating, scope, the identity it runs under, and whether it needs human approval. [S2] [S16]
- When changing a model, prompt, retrieval setting, or tool, rerun the regression suite before release. [S9]
- When model output feeds code, a database, a browser, or another system, define the schema, validation, and encoding at that boundary. [S12] [S15]
- When a step is on a user-facing path, state its latency budget, cost cap, timeout, retry policy, and fallback. [S7] [S13] [S18]

## Final checklist

- An LLM is used only where judgment or unstructured data requires it, and deterministic code owns the rest.
- The design is the simplest workflow that meets the target, with agents justified by evals.
- Knowledge strategy (long context, RAG, fine-tuning) matches the failure type and corpus size.
- Retrieval is hybrid, reranked, permission-aware, cited, and evaluated.
- Model per step, latency budget, cost cap, caching layout, and batch use are explicit.
- Success criteria, an eval set, calibrated judges, and a regression gate exist before build.
- External content is treated as data, tools are least-privilege, and irreversible actions need approval.
- Model output is schema-validated and encoded at every boundary.
- Every step has a timeout, bounded retries, and a fallback or human handoff.
- Every run is traced with inputs, outputs, and request IDs, and failures flow back into evals.

## Sources

- [S1] https://www.anthropic.com/engineering/building-effective-agents
- [S2] https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf
- [S3] https://www.anthropic.com/news/contextual-retrieval
- [S4] https://developers.openai.com/api/docs/guides/optimizing-llm-accuracy
- [S5] https://platform.claude.com/docs/en/docs/build-with-claude/prompt-caching
- [S6] https://platform.claude.com/docs/en/docs/build-with-claude/batch-processing
- [S7] https://platform.claude.com/docs/en/docs/test-and-evaluate/strengthen-guardrails/reduce-latency
- [S8] https://platform.claude.com/docs/en/docs/test-and-evaluate/develop-tests
- [S9] https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- [S10] https://platform.claude.com/docs/en/docs/test-and-evaluate/strengthen-guardrails/reduce-hallucinations
- [S11] https://platform.claude.com/docs/en/docs/build-with-claude/citations
- [S12] https://platform.claude.com/docs/en/docs/build-with-claude/structured-outputs
- [S13] https://platform.claude.com/docs/en/api/errors
- [S14] https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- [S15] https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/
- [S16] https://genai.owasp.org/llmrisk/llm062025-excessive-agency/
- [S17] https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/
- [S18] https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/
- [S19] https://openai.github.io/openai-agents-python/tracing/
