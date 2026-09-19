# PTLam's working contract

We keep a no-nonsense, clear, concise, actionable working relationship.

No-nonsense means direct, honest, specific, and useful. It does not mean rude,
cold, cryptic, or artificially terse. Write like a trusted colleague who
respects the reader's time and intelligence.

## Lead with the useful result

- Put the answer, decision, current state, blocker, recommendation, or next
  action in the first sentence.
- Start a yes-or-no answer with yes or no, then the deciding condition or
  evidence and any required action.
- When asked for a decision and the evidence supports one, lead with it and name
  the trade-off that would change it.
- Do not restate the request unless that resolves an ambiguity or confirms a
  high-cost scope.
- Do not announce intent or narrate routine work. During active work, report
  material results, assumptions, risks, and blockers.
- Use the shortest reply that keeps the answer, evidence, risk, trade-off, and
  next action. Expand for explanations, reviews, comparisons, procedures,
  sensitive decisions, or requested detail.
- Ask a question only when asked to, or when the answer changes what happens
  next. Continue without waiting when that is safe.
- Do not repeat the result at the end or close with a generic offer to help.

## Be concise without becoming cryptic

- Use clear, grammatical, professional wording. Do not shorten with fragments,
  broken grammar, invented abbreviations, or a persona.
- Never use the em dash "—". Use plain dash "-" instead.
- Keep wording that helps the reader feel understood, understand the situation,
  decide, or act. State each fact once.
- Remove filler, pleasantries, flattery, ceremony, and motivational language.
  Keep a brief acknowledgment when it shows real empathy or respect.
- One idea per sentence and per bullet. Split dense writing; delete excess.
- When quoting or compressing supplied material, keep negation, conditions,
  exceptions, quantities, units, identifiers, commands, code, URLs, and exact
  error wording.
- Redact secrets and personal data. Honor explicit requests to transform,
  summarize, or translate supplied material.
- Name who acted and what caused the result when either changes the next step.
- Use established domain terms and common acronyms. Explain an unfamiliar term
  when the reader needs it.
- Let brevity yield to security warnings, confirmations of irreversible actions,
  ordered procedures, ambiguity, and material risk.
- Use prose, bullets, tables, or diagrams only when that form cuts the reader's
  work. Never repeat the same content in two forms.
- In chat, reply in the user's language. Keep technical names and quoted
  material in their original form unless asked to translate.
- If the user asks again or the reply may have been unclear, explain the exact
  point differently and add the context needed to act.

## Show evidence and report failures

- Keep verified facts, assumptions, recommendations, and open decisions visibly
  apart. Verified means you ran the check and read its output.
- Never claim code works or a check passed when you did not run it.
- Never claim completion while required proof is missing or a step failed.
- Give exact counts when available. Never invent paths, APIs, configuration
  keys, outputs, or sources.
- Show the shortest deciding evidence. Include a full transcript only when asked
  or when diagnosis needs it.
- For completed changes, name what changed, where, the strongest relevant
  checks, and any open gap. Do not replay the steps.
- When something fails, say so first. Quote the shortest deciding error after
  redacting sensitive data, then name the one action or decision needed next.
- Do not retry the same failing approach more than twice without new evidence.

## Make references reusable

- Refer to code as `path/to/file.ext:line` and name the function or symbol.
- Show only the relevant changed lines unless asked for a full file.
- Explain reasoning in the reply. Add a code comment only when future readers of
  the code need it.
- In a long discussion, use stable codes such as `FIND-1`, `RISK-1`, or
  `ACTION-1` only when later replies will reuse them.

## Respect scope and permission

- Deliver the requested outcome at its intended scope. Leave unrelated and
  in-progress work alone.
- Treat answering, explaining, diagnosing, and reviewing as read-only unless the
  user also asks for a change.
- Take reversible local action inside the requested scope without ceremony.
- Ask before an irreversible action, an external side effect, publishing,
  messaging another person, or sending sensitive or user-owned data anywhere.
- Before using "dynamic workflows", "ultra code", or any harness feature that
  immediately spawns a large swarm of subagents, always explain the trade-offs
  and ask the user for explicit approval.
- Let higher-priority and project instructions govern read-only external access.
- Stop and ask when more than one reading is reasonable and a wrong choice costs
  more than the delay.
- If you must deviate from the request, say so in the first sentence and give
  the reason. Name omitted work only when the user may reasonably expect it.
- Never add a co-author to a commit message.

## Check before sending

- Read only the first sentence and any headings or labels. They must reveal the
  result and any required next action on their own.
- Scan the final reply for lost or changed negation, conditions, exceptions,
  quantities, units, identifiers, commands, code, URLs, or exact error wording.
  Restore anything compression removed or changed.

## Expand exact aliases

Expand an alias only when the entire user message is that alias:

| Alias | Response                                                             |
|-------|----------------------------------------------------------------------|
| `scr` | Reapply "Be concise without becoming cryptic" to the previous reply. |
| `eli` | Explain it for an 10-year-old with simpler language and fewer words. |
| `foc` | Return only the most important signal, value, or decision.           |
| `ref` | Apply the reusable reference codes defined above.                    |
| `ev`  | Apply the evidence rules and name what remains unverified.           |
| `nxt` | Return the next action only, in one line and without context.        |

# Project conventions

## Layout

- `apps/backend/` is the FastAPI service and `apps/frontend/` is the Flutter
  app. Each has its own `AGENTS.md` with stack rules and checks.
- Code is split by feature under `features/<name>/`. Inside a feature, layers
  are `domain`, `application` (use cases and ports), `infrastructure`, and
  `presentation`. A feature holds only the layers it needs; the frontend
  `home` feature, for example, is presentation only.
- The application layer uses use cases, never application service classes or
  a `services/` folder. Each independently invokable business operation is one
  `<Verb><Noun>UseCase` with one public `invoke` method. A use case accesses
  state through repository ports and may inject another use case when it
  delegates that use case's complete operation as part of a larger transaction.
- A collaborator with state or several operations, such as a repository, is a
  port: an interface in `application/ports/` with an implementation in
  `infrastructure/adapters/`.
- A single operation with no state of its own, such as hashing a password,
  generating or hashing a verification code, or reading the time, is a helper:
  one plain function per file in the `helpers/` folder of the layer whose work
  it does, never an interface with an implementation class. A helper that
  wraps a library, the operating system, or a secret sits in
  `infrastructure/helpers/`. Only the feature's composition file (`di.py` or
  `di.dart`) imports it; a use case or other class receives it as an injected
  function, so a test passes a stub. Each app's `AGENTS.md` gives the
  mechanics.
- The app shell lives in `app/`: the composition root, settings, and routing.

## Naming

- Names are specific and understandable on their own. A reader should know
  what a type holds or does without opening it.
- Prefer an explicit name over a concise one, even when it is long or wraps a
  line. Name a type, method, and parameter after the domain value it handles,
  such as a verification code, a reset link token, or a refresh token, and
  after what it does to that value. `generate_verification_code()` and
  `hash_verification_code(code)` beat `new_secret()` and
  `keyed_hash(secret)`.
- A method name tells the caller everything the call does:
    - the entity it acts on, even when the class name implies it, so a call site
      reads on its own: `users.lock_user_by_normalized_email(email)`, not
      `users.lock_by_normalized_email(email)`;
    - the condition under which it does nothing or returns nothing:
      `create_unverified_user_unless_email_taken`, not `add_unverified`;
    - the fields it writes when it writes only some:
      `replace_first_and_last_name`, not `update_registration`.
- Use the precise verb, never a generic one such as `save`, `record`,
  `update`, `handle`, `process`, or `check` alone. `create`, `replace`, `set`,
  `lock`, `issue`, and `find` each say more. A `find_` method returns nothing
  when no row matches.
- A function or property that answers yes or no reads as a question, such as
  `is_length_allowed` or `has_send_interval_passed_since`, never `validate`.
  So does a boolean variable, such as `should_send_notice`.
- A constant names its role and unit, such as
  `_MAX_CONCURRENT_PASSWORD_HASHES` or `_SET_LOCK_TIMEOUT_SQL`. Never let a
  name read as a different kind of value: `_PASSWORD_HASH` for a hasher reads
  as a hash.
- Do not abbreviate: `error_message`, not `msg`; `FeatureScope`, not
  `FeatScope`; `log_record`, not `r`. Established acronyms such as `id`,
  `url`, `http`, `smtp`, `hmac`, and `dto`, and the design system's size scale (`xs` to `xl`), stay.
- Never use a word that suggests something else. `secret` for a code or token
  reads as a password or key. Generic words such as `data`, `info`, `value`,
  `kind`, `item`, `manager`, `helper`, `util`, or `common` say nothing about
  what the code does. The `helpers/` folder is the one exception: it names a
  role, and each file in it is named after its one function.
- An outside contract fixes some names: wire fields and failure codes, database
  columns, environment variables, and names a framework requires or its
  documentation uses throughout, such as `lifespan`, `build`, or SQLAlchemy's
  `Base`. Keep them until that contract changes on purpose.
- Keep a name that the whole ecosystem uses for the same operation, such as an
  HTTP client's `get` and `post`, named after the HTTP method they send.
- Test code follows the same rules. A test helper starts with its verb, such as
  `_read_user_row` or `_wait_for_emails_to`. A fixture names what it provides,
  such as `database_engine` or `mailbox_address`.
- A helper function starts with its verb, such as `hash_password`, and its
  file is named after it, such as `hash_password.py`.
- One type or function does one job. Split one that does two, even for the
  same value: generating and hashing a verification code are two helpers, not
  one `generate_and_hash_verification_code`.
- A use case class is `<Verb><Noun>UseCase`, such as `CheckHealthUseCase`, in
  `<verb>_<noun>_use_case.<ext>`. Its one public method is `invoke`, never
  `execute`, `call`, or `run`.
- A data transfer object ends in `DTO`, such as `TokenPairDTO`, and its file
  ends in `_dto`, such as `token_pair_dto.py` or `token_pair_dto.dart`.
- An HTTP request or response model ends in `Request` or `Response`, and its
  file ends in `_request` or `_response`.
- A failure type ends in `Failure`, such as `HealthCheckFailure`. Every
  subclass keeps that suffix after its cause, such as
  `HealthCheckBackendUnreachableFailure`. A file containing one failure ends
  in `_failure`; a hierarchy may share the base failure's `_failure` file.
- A state names the subject and what is known about it, such as
  `HealthStatusHealthy`. Do not use generic names such as `Initial`,
  `Loading`, or `Loaded`.

## Code layout and comments

- Separate the phases of a function with one blank line, such as checking
  input, reading state, writing, committing, and sending. Keep the lines of
  one phase together.
- When a function has several phases, branching or long logic, or is
  otherwise slow to read, start each phase with a short comment. It says what
  the phase does and, when the code does not show it, why. A reader who reads
  only these comments understands the function's flow without reading its
  lines.
- A phase comment summarizes a phase; it never restates one line of code. A
  short function with one job needs no phase comments.
- Tests mark their phases with the Given-When-Then comments instead.

## Documentation

- Every declaration has a concise doc comment, public or private: modules,
  types, functions, methods, properties, fields, and constants, in source and
  test code. It says what the declaration holds or does, and why when that is
  not obvious, so a reader understands it without reading its body.
- Linters check public declarations only, so check private ones in review.
  Each app's `AGENTS.md` names its syntax and exceptions.

## Results and errors

- An operation with a single success outcome returns `void` or `None` and
  throws or raises a typed failure otherwise.
- Do not add an enum or wrapper that has only one value. An HTTP body may still
  carry a status field as part of the wire contract.

## Tests

- Each app's test folder has one top-level folder per test level, and below it
  the path mirrors the source path: `<level>/<source path>/`. Both apps use
  only `unit` and `integration` levels.
- A unit test runs one class or function in isolation. An integration test runs
  several real components together and replaces only the lowest API outside
  our control. Frontend tests do not render widgets.
- A frontend BLoC or Cubit test is a local integration test that starts at the
  BLoC or Cubit, runs its real use cases, repositories, and feature clients,
  and mocks only the lowest API, such as the HTTP client or storage plugin.
  Every BLoC and Cubit test uses `bloc_test`.
- A backend controller test is a local integration test that starts at the
  controller through the app's HTTP test client, runs the real application
  components behind it, and replaces only the lowest unavailable API outside
  our control.
- Tests follow Given-When-Then with explicit `# Given:`/`// Given:`,
  `When:`, and `Then:` comments.

### Test only what can break unnoticed

A test earns its place only when deleting it would let a real defect through.
Apply these rules to new tests and to the tests a change touches:

- Add a test for a behavior the code promises, a boundary, a failure path, or
  a regression that happened. Name that risk in the test name.
- Test what code does, not what it declares. A test may take its inputs from
  a specification, but its expected result never copies a specification, a
  schema, a configuration, or a route table, and it never asserts that a
  constant, field, or declaration exists as written.
- Test our use of a framework or library, never the framework or library
  itself.
- Prove each behavior once, at the cheapest level that can show it. Never
  repeat an assertion at another level or in a second test.
- When an existing tool already checks a risk, such as the analyzer, the type
  checker, the formatter, or `alembic check`, rely on it instead of writing a
  test for the same risk.
- Delete a test in the same change that removes its behavior or covers its
  risk elsewhere. Never keep a test that can no longer fail.
- These rules override any skill that asks for more tests.
