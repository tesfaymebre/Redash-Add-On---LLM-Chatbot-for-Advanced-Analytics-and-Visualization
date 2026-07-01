# Task 1: LLM Revolution — Research & Project Planning Report

> **Branch:** `task/01-llm-research`  
> **Project:** Redash Add-On — LLM Chatbot for Advanced Analytics and Visualization

---

## 1. Executive Summary

Large Language Models (LLMs) have shifted data analytics from "write SQL first, explore second" to "ask in natural language, let the system generate and validate SQL." They do **not** replace analysts — they automate syntax, schema lookup, and routine queries so humans focus on framing questions, validating results, and driving decisions.

For our Redash chatbot, the research converges on a clear architecture: a **thin React add-on** calling a **Quart backend** that orchestrates **LangChain SQL agents** with **schema + sample-value context**, **execute-and-retry loops**, **read-only database access**, and optional **LlamaIndex retrieval** over YouTube metadata docs. Visualization generation can leverage tools like **LIDA**, while multi-step insight extraction follows patterns from **InsightPilot** (understand → summarize → compare → explain). **Flowise** offers a no-code sandbox to prototype these flows before hard-coding them.

---

## 2. LLM Tool Landscape (Conceptual Foundations)

### 2.1 OpenAI Tools

| Tool | What it is | Relevance to our project |
|------|------------|--------------------------|
| **Chat Completions** | Send messages (system + user + assistant), get text back | Core NL→SQL and insight generation |
| **Assistants / Threads / Runs** | Stateful agents with tool use and conversation memory | Multi-turn dashboard Q&A with context |
| **Function Calling** | Model returns structured JSON to invoke your code | Execute SQL, fetch schema, create Redash viz |
| **Advanced Data Analysis / Code Interpreter** | Sandboxed Python for data analysis | EDA on query results, chart recommendations |
| **Actions (Plugins)** | Connect model to external APIs | Redash API: create queries, dashboards |

**Key takeaway for our project:**  
Use **Chat Completions + Function Calling** as the primary primitives in Tasks 3–4 (proven, simple, testable). Reserve **Assistants API** for persistent multi-turn dashboard chat if we need built-in thread memory. Use **Code Interpreter patterns** only for ad-hoc EDA on query result DataFrames — not as the main SQL path. **GPT Actions** map directly to calling our Quart backend or Redash REST API from a ChatGPT-style interface.

---

### 2.2 LangChain Components

| Component | Role | Our use case |
|-----------|------|--------------|
| **Tools** | Wrappers around functions (run SQL, list tables) | Agent can "act" on the database |
| **Agents** | LLM decides which tool to call next | Route: summarize viz vs generate SQL vs build dashboard |
| **Memory** | Persist conversation / schema context | Follow-up questions ("now filter by mobile only") |
| **Retrievers** | Fetch relevant docs/chunks via similarity search | Inject table definitions & sample rows into prompts |
| **Adapters** | Connect to models, vector stores, APIs | Swap OpenAI for another provider if needed |

**Key takeaway:**  
LangChain is our **orchestration layer** — it wires the LLM to SQL tools, handles ReAct-style reasoning loops, and passes database error messages back for self-correction. Use **SQLDatabaseToolkit + create_sql_agent** for NL→SQL, with custom tools for Redash-specific actions (create visualization, publish dashboard).

---

### 2.3 LlamaIndex Components

| Component | Role | Our use case |
|-----------|------|--------------|
| **Data connectors** | Ingest CSV, SQL, APIs into indexable documents | Index YouTube schema docs + column descriptions |
| **Query functions** | Structured retrieval over indexed data | "What columns exist in subscription_status?" |
| **Indexing** | Build vector or keyword indexes | Semantic search over metadata & past queries |

**Key takeaway:**  
Use **LlamaIndex for retrieval (RAG)**, not for agent orchestration. When a user asks about "mobile viewership by geography," LlamaIndex retrieves the relevant table/column descriptions from indexed schema docs rather than stuffing all 15+ YouTube tables into every prompt. LangChain agents call LlamaIndex retrievers as a tool.

---

### 2.4 Vector Databases

| Concept | Explanation | Our use case |
|---------|-------------|--------------|
| **Embeddings** | Dense vectors representing meaning of text | Embed table/column descriptions, dashboard titles |
| **Semantic search** | Find nearest neighbors in vector space | Retrieve relevant schema snippets for NL→SQL |

**Candidate stores:** **pgvector** (same Postgres as analytics — simplest ops), Chroma (local/dev prototyping), Pinecone (managed scale).

**Key takeaway:**  
Index **business descriptions** of YouTube tables (e.g., "Device type — breakdown of views by Mobile, Desktop, TV") plus **sample distinct values** for filter columns. Retrieve top-k chunks per question to keep prompts small and accurate.

---

## 3. Literature & Resource Summaries

### 3.1 SQL Generation Using LLMs

**Source:** [Can LLMs Replace Data Analysts? Getting Answers Using SQL](https://towardsdatascience.com/can-llms-replace-data-analysts-getting-answers-using-sql-8cf7da132259/) (Mariya Mansurova, TDS, Dec 2023)

**Summary:**  
This two-part series builds an "LLM-powered analyst" that answers business questions by querying SQL databases via **LLM agents**. Part 2 focuses on the **ReAct pattern** (Reasoning + Acting): the model plans, calls tools, observes results, and iterates — mirroring how human analysts work.

The author implements a ClickHouse-backed agent with four tools:
1. **List of tables** — embedded in the system prompt (static context)
2. **`get_table_columns`** — returns column names and types for a table
3. **`get_table_column_distr`** — returns top-N distinct values for filter columns
4. **`execute_sql`** — runs the generated query and returns results (including DB errors)

The agent is built first **from scratch** using OpenAI Function Calling, then refactored to LangChain's `AgentExecutor`. A key demo shows self-correction: the model generates SQL using a wrong column name (`active` instead of `is_active`), receives the database error, calls `get_table_columns`, fixes the query, and returns the correct count.

The article compares agent types (OpenAI Functions, ReAct, Plan-and-Execute) and emphasizes that LLMs **augment** analysts — they handle SQL syntax and schema navigation while humans provide business framing and validate outputs.

**Techniques mentioned:**
- [x] Schema injection in prompt (table list + descriptions in system message)
- [x] Few-shot examples (via tool observation loops rather than static examples)
- [x] Self-correction / re-prompt on SQL error (pass DB traceback to model)

**Limitations:**
- Agents can loop indefinitely — need iteration limits (author uses max 10)
- No guarantee against DML (`DELETE`, `DROP`) — must enforce read-only DB permissions
- Column name hallucination on first attempt is common; schema lookup adds latency
- Static table list in prompt doesn't scale to hundreds of tables

**Application to our chatbot:**  
Mirror this exact tool pattern in our Quart backend for YouTube data:
- System prompt lists our tables (`device_type`, `geography`, `viewership_by_date`, etc.)
- Tools: `get_columns`, `get_distinct_values`, `execute_sql` (read-only Postgres user)
- LangChain `AgentExecutor` with max iterations and error-feedback loop
- For our 15 dimension folders in `Data/`, pre-compute column metadata during ETL (Task 2)

---

### 3.2 OpenAI Cookbook — SQL Backtranslation

**Source:** [Backtranslation_of_SQL_queries.py](https://github.com/openai/openai-cookbook/blob/main/examples/Backtranslation_of_SQL_queries.py) *(referenced in challenge brief; file may have been moved/renamed)*

**Related cookbook:** [How to evaluate LLMs for SQL generation](https://github.com/openai/openai-cookbook/blob/main/examples/evaluation/How_to_evaluate_LLMs_for_SQL_generation.ipynb)

**Summary:**  
The challenge references a **backtranslation** example for SQL. While the exact file path returns 404 in the current cookbook repo, the concept and related evaluation notebooks are well-established in OpenAI's documentation.

**Backtranslation** (applied to SQL) is a round-trip validation technique:

```
Natural Language Question
        ↓
    SQL Query (generated)
        ↓
Natural Language Description (back-translate SQL → English)
        ↓
Compare: does the description match the original question?
```

If the back-translated description diverges semantically from the user's question, the SQL likely misinterprets intent — even if it executes without error.

The related **SQL evaluation cookbook** demonstrates a complementary two-layer validation:
1. **Syntactic validation** — execute CREATE + SELECT against SQLite; catch syntax errors
2. **Semantic validation (G-Eval style)** — use a second LLM call to score whether the generated SQL actually answers the original question

The cookbook generates structured JSON output: `{ "create": "CREATE TABLE ...", "select": "SELECT ..." }` and runs automated test functions (`test_create`, `test_select`, `test_llm_sql`).

**What is backtranslation?**  
SQL → natural language → SQL again (or NL → SQL → NL). Used to detect **semantic drift** — when syntactically valid SQL returns wrong or empty results because the model misunderstood column semantics, join logic, or filter values.

**Application to our chatbot:**  
Implement as an optional **quality gate** before returning SQL to Redash:
1. Generate SQL from user question
2. Ask LLM: "Describe in plain English what this SQL query returns"
3. Compare description to original question (cosine similarity or LLM-as-judge)
4. If mismatch → regenerate with clarification prompt
Also adopt the cookbook's **execute-and-validate** pattern in our CI test suite for golden questions (e.g., "total views by device type").

---

### 3.3 Flowise AI (Quick Experimentation)

**Source:** [https://flowiseai.com/](https://flowiseai.com/) | [SQL Agent Tutorial](https://docs.flowiseai.com/tutorials/sql-agent)

**Summary:**  
Flowise is an **open-source, visual, no-code platform** built on LangChain. Users drag-and-drop nodes (LLM, prompt template, custom functions, condition agents) to build AI workflows without writing backend code. It supports OpenAI, Anthropic, and local models, and can be self-hosted or embedded via API/SDK.

The **SQL Agent tutorial** implements a production-grade NL→SQL pipeline:
1. **Get DB Schema** — retrieve table/column metadata
2. **Generate SQL Query** — LLM with JSON structured output (`sql_query` field only)
3. **Check SQL Query** — Condition Agent validates syntax (no `DELETE`/`DROP`, valid keywords)
4. **Run SQL Query** — Custom JavaScript function executes against the database
5. **Check Results** — if error, loop back to step 2 with error message (self-correction)
6. **Generate NL Response** — LLM summarizes results for the user

Key design choices: **structured JSON output** prevents the model from wrapping SQL in markdown; **Condition Agents** act as guardrails; **flow state** passes `sqlQuery` between nodes.

**Application to our chatbot:**  
Use Flowise as a **rapid prototype** in Task 4 before implementing in Quart:
- Connect to our Postgres `youtube_analytics` database
- Test prompt templates and self-correction loops visually
- Export the working flow logic into Python/LangChain for production
- Flowise is **not** our production deployment — it's a design sandbox

---

### 3.4 InsightPilot Paper

**Source:** [An LLM-Empowered Automated Data Exploration System (arXiv 2304.00477)](https://arxiv.org/pdf/2304.00477v2) — Microsoft Research, EMNLP 2023 Demo

**Summary:**  
InsightPilot addresses a limitation of pure text-to-SQL: users often ask **fuzzy, high-level questions** ("show me interesting trends in viewership") that cannot be answered by a single SQL query. The system combines an **LLM planner** with a deterministic **insight engine** to produce multi-step exploration sequences ending in natural-language reports with charts.

**Architecture (3 components):**
1. **User interface** — natural language input; displays text + charts
2. **LLM planner** — selects insights and analysis actions based on context
3. **Insight engine** — executes actions via QuickInsight, MetaInsight, XInsight tools

**Four analysis actions:**
| Action | Purpose | Example |
|--------|---------|---------|
| **Understand** | Enumerate high-level patterns in data | "School A has Rank#1 average score" |
| **Summarize** | Check if a pattern holds across dimensions | "Most schools show rising scores, except School C" |
| **Compare** | Contrast insight across neighbors | "Schools A and B rising; School C flat" |
| **Explain** | Causal explanation for outliers | "2020 outlier caused by Exam Form=Take-home" |

The LLM selects actions iteratively until it chooses termination (`⊥`) or hits token limits, then synthesizes top-K insights into a coherent report.

**Key problems solved:**
- **Hallucination** — insight engine returns verified facts, not LLM guesses
- **Context window overflow** — engine abstracts millions of cells into compact insight tuples
- **User intent** — LLM interprets fuzzy questions and steers exploration

User studies showed InsightPilot outperformed OpenAI Code Interpreter on completeness, relevance, and understandability.

**Key ideas to borrow:**
- [x] Automated insight extraction (deterministic stats + LLM narration)
- [x] Multi-step exploration loop (not one-shot SQL)
- [x] Human-in-the-loop validation (review before publishing to dashboard)

**Application to our chatbot:**  
Map InsightPilot actions to our chatbot **modes**:
- **Dashboard context chat** → Summarize + Explain (describe what a Redash viz shows)
- **Open exploration** → Understand + Compare (trend across device types, geographies)
- **NL query** → text-to-SQL (complementary, not replacement)

Our backend can expose `/chat/insight` that runs SQL, computes basic stats (trend, outlier, top-N), and asks the LLM to **narrate verified numbers** — never invent them.

---

### 3.5 LangChain — LLMs and SQL

**Source:** [LangChain Blog: LLMs and SQL](https://www.langchain.com/blog/llms-and-sql) (Francisco Ingham & Jon Luo, March 2023)

**Summary:**  
LangChain provides **SQL chains** (single-shot: question → SQL → result → answer) and **SQL agents** (multi-step: list tables → inspect schema → write SQL → fix errors → answer). The blog covers practical production lessons:

**1. Limit query output size**  
LLM-generated queries can return millions of rows, blowing the context window. Instruct the model to use `LIMIT`, select minimal columns, and aggregate where possible.

**2. Self-correction on SQL errors**  
When a query fails, pass the **original SQL + error traceback** back to the LLM — exactly what a human DBA would do. LangChain agents do this automatically in the ReAct loop.

**3. Security**  
Always use **read-only database credentials**. Scope permissions to specific tables. Consider table allow-lists. LLMs can be prompt-injected to run destructive SQL.

**Patterns mentioned:**
- [x] **SQLDatabaseChain** — single-pass: generates SQL, runs it, summarizes results
- [x] **Agent with SQL toolkit** — `create_sql_agent` + `SQLDatabaseToolkit` (list tables, schema, query, checker)
- [x] **Schema retrieval** — agent calls `sql_db_schema` tool before writing SQL

**SQLChain vs SQLAgent trade-off** (from community benchmarks):
- **SQLChain** — faster, fewer tokens, but fails on multi-step questions
- **SQLAgent** — answers more questions, self-corrects, but higher latency and occasional hallucination when no data matches

**Application to our chatbot:**  
Use **SQLAgent** as default (YouTube questions often need schema lookup + filter value discovery). Use **SQLDatabaseChain** for simple metric lookups ("total views yesterday"). Implement LangChain's **human-in-the-loop middleware** to pause before executing SQL in production — show generated query in Redash UI for user approval.

---

### 3.6 LLM Tools Arena (Awesome List)

**Source:** [underlines/awesome-ml — llm-tools.md](https://github.com/underlines/awesome-ml/blob/master/llm-tools.md)

**Summary:**  
This curated list catalogs LLM frameworks, agents, and domain-specific tools. For our BI/SQL/visualization project, the most relevant entries:

| Tool | Category | Why it matters |
|------|----------|----------------|
| **LIDA** (Microsoft) | Viz generation | LLM-powered chart code generation from data summaries; grammar-agnostic (matplotlib, altair, plotly) |
| **LangChain** | Orchestration | SQL agents, tools, memory — our primary backend framework |
| **LlamaIndex** | RAG / indexing | Schema doc retrieval, query engines over metadata |
| **Flowise** | No-code prototyping | Visual SQL agent builder for rapid iteration |
| **OpenAI Code Interpreter** | Data analysis | Sandboxed Python EDA — benchmark compared unfavorably to InsightPilot for exploration |
| **DB-GPT / SQLCoder** | Text-to-SQL models | Specialized models fine-tuned on SQL; alternative to GPT-4 for cost/latency |
| **Vanna.ai** | NL→SQL + training | Train on DDL + example queries; RAG over past questions |

**LIDA pipeline** (most relevant for Task 5):
1. **Summarizer** — compact NL summary of dataset
2. **Goal Explorer** — enumerate visualization goals
3. **VisGenerator** — generate, execute, filter viz code
4. **Infographer** — stylized infographics (experimental)

**Application to our chatbot:**  
- **Task 4:** LangChain SQL agent (primary)
- **Task 5:** LIDA or custom LLM viz-spec generator → Redash visualization JSON
- **Schema RAG:** LlamaIndex over our YouTube table documentation
- **Evaluation:** Golden question set inspired by Spider / BIRD benchmarks mentioned in the awesome list

---

### 3.7 LlamaIndex — Context-Aware LLM Apps

**Source:** [LeewayHertz — LlamaIndex overview](https://www.leewayhertz.com/llamaindex/)

**Summary:**  
LlamaIndex (formerly GPT Index) is a **data framework for connecting custom data to LLMs**. Where LangChain focuses on **orchestration** (chains, agents, tools), LlamaIndex focuses on **ingestion, indexing, and retrieval** — the "context" in RAG applications.

**Core pipeline:**
```
Data Sources → Connectors → Documents → Nodes → Index → Query Engine → LLM Response
```

**Key components:**
- **LlamaHub** — 100+ data connectors (Postgres, PDF, Notion, APIs, CSV)
- **Indices** — vector (semantic), tree (hierarchical summary), keyword (exact match)
- **Query engines** — retrieve relevant nodes, synthesize answer
- **Chat engines** — multi-turn RAG with memory
- **Agents / Workflows** — newer multi-step RAG + tool use (overlaps with LangChain)

**LangChain vs LlamaIndex:**
| | LangChain | LlamaIndex |
|---|-----------|------------|
| Strength | Agent orchestration, tool calling | Data ingestion, indexing, retrieval |
| Best for | "Do this sequence of actions" | "Find relevant context, then answer" |
| Integration | Can call LlamaIndex retrievers as LangChain tools | Exposes retrievers/query engines as callable modules |

**Application to our chatbot:**  
Build a **schema knowledge base** in Task 2:
1. For each YouTube table, create a markdown doc: table purpose, columns, sample values, example questions
2. Index with LlamaIndex `VectorStoreIndex` (pgvector backend)
3. On each chat request, retrieve top-5 relevant schema chunks
4. Inject into LangChain agent system prompt alongside live `information_schema` query

Also index **Redash query history** and **dashboard descriptions** so the chatbot can answer "what does this dashboard show?" without re-querying raw data.

---

## 4. Project Planning (Bridge to Task 2+)

### 4.1 Proposed Architecture (High Level)

```
User (Redash UI)
    → React chat add-on (query editor + dashboard pop-up)
    → Quart backend
        ├── /chat          — general Q&A, routes to appropriate handler
        ├── /sql           — NL → SQL → execute → summarize
        ├── /insight       — multi-step exploration (InsightPilot-style)
        ├── /viz           — generate visualization spec (LIDA-inspired)
        └── /dashboard     — assemble viz collection into Redash dashboard
    → LangChain agent layer
        ├── SQLDatabaseToolkit (list tables, schema, query)
        ├── Custom tools (Redash API, distinct values)
        └── LlamaIndex retriever (schema docs)
    → PostgreSQL (youtube_analytics) + pgvector (schema embeddings)
    → OpenAI API (gpt-4o-mini for routing, gpt-4o for SQL generation)
    → Redash API (publish queries, visualizations, dashboards)
```

### 4.2 Technology Choices

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend framework | **Quart** | Async I/O for concurrent OpenAI + DB + Redash calls; challenge requirement |
| LLM orchestration | **LangChain** (agents + tools) | Mature SQL agent support, self-correction loops, human-in-the-loop |
| Context retrieval | **LlamaIndex + pgvector** | Semantic search over schema docs; same Postgres instance |
| Database | **PostgreSQL** | YouTube CSVs load cleanly; `information_schema` for live schema; Redash native support |
| Vector store | **pgvector** | No extra infrastructure; co-located with analytics DB |
| LLM provider | **OpenAI** (gpt-4o / gpt-4o-mini) | Best text-to-SQL accuracy; function calling; challenge requirement |
| Viz generation | **LIDA** or custom viz-spec | Grammar-agnostic; generates matplotlib/altair code → Redash chart types |
| Prototyping | **Flowise** | Visual NL→SQL flow design before Quart implementation |
| Frontend | **Redash React add-on** | Thin client; all intelligence in backend |

### 4.3 Risk Register

| Risk | Mitigation |
|------|------------|
| Hallucinated SQL | Schema injection + LlamaIndex retrieval + execute-and-retry + read-only DB user |
| Wrong but valid SQL (silent errors) | Backtranslation check; row-count sanity checks; sample result preview in UI |
| API cost / latency | gpt-4o-mini for intent routing; cache schema metadata; limit agent iterations to 5 |
| Redash fork complexity | Thin add-on calling external backend; no LLM logic inside Redash handlers |
| Schema drift | Regenerate schema docs on ETL reload; CI test against golden questions |
| Prompt injection | Table allow-list; block DDL/DML keywords; parameterized tool inputs |

### 4.4 Task Roadmap (Weeks 3–4)

| Task | Deliverable | Depends on |
|------|-------------|------------|
| Task 1 | This report | — |
| Task 2 | DB schema + ETL scripts + EDA notebook | `Data/` CSVs |
| Task 3 | Redash add-on UI + Quart `/chat` and `/sql` endpoints | Task 2 |
| Task 4 | LangChain SQL agent + LlamaIndex schema RAG | Task 1, 3 |
| Task 5 | Auto viz generation + dashboard assembly | Task 4 |
| Task 6 | Blog / final report | All |

---

## 5. Conclusion

The LLM revolution in data analytics is not about replacing SQL or analysts — it is about **lowering the syntax barrier** while keeping humans in the loop for question framing and result validation. The research points to a layered architecture: **retrieval** (LlamaIndex) for schema context, **orchestration** (LangChain agents) for tool use and self-correction, **deterministic engines** (InsightPilot-style stats) for verified insights, and **visualization tools** (LIDA) for chart generation.

For our Redash chatbot, the critical design decisions are: (1) separate backend from Redash UI, (2) read-only SQL with execute-and-retry, (3) rich schema context beyond raw `information_schema`, and (4) multiple chat modes (summarize viz, generate SQL, explore insights, build dashboard) rather than a single generic prompt. Task 2 — loading YouTube data and designing the schema — is the immediate next step, because every LLM technique above depends on well-modeled, documented tables.

---

## References

1. Mansurova, M. (2023). *Can LLMs Replace Data Analysts? Getting Answers Using SQL.* Towards Data Science. https://towardsdatascience.com/can-llms-replace-data-analysts-getting-answers-using-sql-8cf7da132259/
2. OpenAI. *Backtranslation of SQL queries* (cookbook example). https://github.com/openai/openai-cookbook/blob/main/examples/Backtranslation_of_SQL_queries.py
3. OpenAI. *How to evaluate LLMs for SQL generation* (cookbook). https://github.com/openai/openai-cookbook/blob/main/examples/evaluation/How_to_evaluate_LLMs_for_SQL_generation.ipynb
4. FlowiseAI. (2024). *SQL Agent Tutorial.* https://docs.flowiseai.com/tutorials/sql-agent
5. Ding, R., Han, S., Zhang, D. (2023). *InsightPilot: An LLM-Empowered Automated Data Exploration System.* EMNLP 2023 Demo. https://arxiv.org/pdf/2304.00477v2
6. Ingham, F. & Luo, J. (2023). *LLMs and SQL.* LangChain Blog. https://www.langchain.com/blog/llms-and-sql
7. underlines. *LLM Tools — awesome-ml.* https://github.com/underlines/awesome-ml/blob/master/llm-tools.md
8. LeewayHertz. *LlamaIndex: An overview.* https://www.leewayhertz.com/llamaindex/
9. Dibia, V. (2023). *LIDA: Automated Visualizations with LLMs.* Microsoft Research. https://microsoft.github.io/lida/
