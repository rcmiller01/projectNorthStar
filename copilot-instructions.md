# Copilot Custom Instructions for projectNorthStar
# Golden Rules — Project Operating Guide (All Repos)

> Purpose: a generic, non‑secret operating manual for every codebase we build. No domain specifics; safe to publish. Use this to keep behavior consistent across VS Code, local agents, and chat assistants.

---

## 1) Modes of Operation

### Planner Mode (default before significant work)

* Trigger when a task is new, ambiguous, cross‑cutting, or risky.
* Assistant **must ask 4–6 clarifying questions** focused on inputs, outputs, constraints, risks, and definitions of done.
* Produce a **plan** with:

  * Objectives & acceptance criteria
  * Deliverables & file touch‑list
  * Budget (time/token/memory/IO) & stop conditions
  * Tooling/models to use; fallbacks/escalation
  * Test/verification approach
* **Announce when the plan is complete**, summarize intended actions, and **state the next action**.

### Execute Mode

* Work strictly against the plan. Keep changes scoped to the declared files.
* Small, atomic commits; pass linters/tests locally before PR.
* On budget breach or repeated verifier failure, **escalate per plan**, or return to Planner Mode.

### Reflect Mode (post‑work)

* Add a short **Post‑Code Reflection** to the PR or change log:

  * What changed and why
  * What surprised us
  * Risks introduced / tech debt created
  * Next sensible improvement

---

## 2) Repository Structure (choose the subset you need)

```
/ (root)
  README.md                # Quickstart; how to run/tests; support matrix
  GOLDEN_RULES.md          # This file (keep synced across repos)
  /src                     # Application/library code (see subfolders)
    /core                  # Orchestration, routing, shared kernels
    /experts               # Task-specific modules (e.g., sql_agent, code_fixer)
    /retrieval             # Graph + vector retrieval code; chunkers/parsers
    /verify                # Verifiers, validators, test harness runners
    /memory                # HRM/task cache/pattern libraries (no secrets)
    /ui                    # CLI/web or editor integrations (optional)
  /configs                 # *.yaml/json/toml; environment-agnostic
  /prompts                 # Prompt templates & grammars; non-secret
  /tests                   # Unit/integration/e2e; goldens live here
  /scripts                 # Dev/ops scripts (lint, build, release, data prep)
  /docs                    # Architecture notes, ADRs, design diagrams
  /examples                # Minimal runnable demos & sample inputs/outputs
  /infra                   # IaC, Dockerfiles, compose, k8s manifests
  /assets                  # Static assets (logos, small fixtures)
  /data                    # Small, non-sensitive sample data only
```

**Root vs. subfolders**

* **Root** holds repo meta (README, this guide, licensing, high-level configs).
* **/src** contains all executable logic; avoid free‑floating modules at root.
* **/configs** are environment‑agnostic; put secrets in your platform’s secret store, not the repo.

---

## 3) File, Function, and Module Limits

* **Files**: soft limit **≤ 400 lines**, hard **≤ 800**. Split into modules when exceeded.
* **Functions/methods**: soft **≤ 30 lines**, hard **≤ 60**. Aim for **cyclomatic complexity ≤ 10**; extract helpers when above.
* **Public APIs**: favor small, pure functions; avoid hidden mutable globals; document inputs/outputs with types.
* **Docs**: first‑line summary ≤ 72 chars; include examples for non‑obvious behavior.

---

## 4) Budgets & Efficiency (enforced)

* Track and respect budgets per task:

  * **time\_s** (wall time), **tokens** (LLM), **memory\_mb**, **io\_mb**, **cost\_usd** (if applicable)
* Store defaults in `configs/budget.yaml`; override in task plans.
* On approaching 90% of any budget, assistants must **pause, summarize progress, propose options** (stop, optimize, or escalate).

**Example `configs/budget.yaml`**

```yaml
defaults:
  time_s: 180
  tokens: 16000
  memory_mb: 4096
  io_mb: 256
  cost_usd: 0.25
policy:
  warn_at: 0.9
  hard_stop: true
```

---

## 5) Retrieval & Context (generic)

* Prefer **graph/structural retrieval** (relations, schemas, call graphs) first; blend **vector + keyword** when recall is thin.
* Cite sources/paths in outputs (file paths, table/column names, node IDs).
* Keep context packs **small and relevant**; avoid dumping entire files or schemas when a snippet suffices.

---

## 6) Verification & Testing

* Every change must have **verification**:

  * Unit tests for new logic; regression tests for fixed bugs
  * Schema/contract checks for data and APIs
  * Deterministic outputs for goldens where feasible
* CI gates: lint → type‑check → unit → integration (fast) → optional e2e (slow)
* Artifacts to attach in PRs: diffs, test logs, verification summary, any generated assets.

---

## 7) Commits, Branching, and PRs

* **Conventional Commits**: `type(scope): summary` (e.g., `feat(sql): add safe top-k join`)
* Branch model: `feature/<slug>`, `fix/<slug>`, `chore/<slug>`
* PR checklist:

  * [ ] Plan included or linked
  * [ ] Tests updated/passing; coverage not down materially
  * [ ] Budget respected; metrics attached
  * [ ] Post‑Code Reflection added (see template)

---

## 8) Post‑Code Reflection (template)

```
### Reflection
- Why: <problem + constraints>
- What changed: <modules/files>
- Verification: <tests/checks run>
- Risks/Tradeoffs: <perf, debt, portability>
- Next action: <bite‑sized follow‑up>
```

---

## 9) Planner Mode — Protocol (for VS Code & chat assistants)

1. Detect need → ask **4–6 clarifying questions** (inputs, outputs, constraints, risks, DoD).
2. Draft plan with: goals, acceptance criteria, file touch‑list, budgets, tools/models, verification, risks & rollbacks.
3. **Announce plan complete** → summarize actions → **state the next action** and await confirmation (unless pre‑authorized).
4. During execution: surface blockers early; propose alternatives within budget; switch back to Planner Mode on scope creep.

---

## 10) Don’ts

* Don’t commit secrets, tokens,
