# Python Typing

Type mechanics for Python code. The project's minimum Python version and its
configured checker decide which syntax and features are available.

## Type changed production code

Annotate every parameter and return of a callable you add or substantially
change. Add attribute and local annotations when inference does not make the
contract clear. Keep an existing public signature unless the change owns its
compatibility impact.

- Prefer precise domain types over `Any`. Use `object` and narrow it when the
  input is really unknown.
- For inputs, accept useful abstractions such as `Iterable`, `Sequence`,
  `Mapping`, or a small `Protocol`; return the concrete type the caller gets.
  Validation and serialization models may need concrete containers.
- Use builtin generics and `X | None` only when every supported interpreter
  accepts them; otherwise follow the project's compatibility syntax.
- Use `TypedDict` for a fixed dictionary shape, and a dataclass or model when
  behavior, validation, or identity gives the value a stronger owner.
- Make a new API keyword-only when positional order is easy to confuse. Do not
  retrofit keyword-only arguments onto a public API without a compatibility
  plan.

Never use a mutable object as a function default. Use `None` as a sentinel, or a
factory the data-model mechanism owns.

## Put identity, unit, and time in the type

- Give a distinct identifier its own type with `NewType`, such as
  `UserId = NewType("UserId", str)`, so an order identifier cannot be passed
  where a user identifier belongs.
- Use `decimal.Decimal` for money and any exact quantity. Binary floats round in
  ways an accounting report eventually surfaces.
- Use a timezone-aware `datetime` for an instant, `datetime.now(UTC)` to read
  the clock, and `date` only for a calendar day with no instant. Reject a naive
  `datetime` at the boundary that accepts it.
- Freeze a value object with `@dataclass(frozen=True, slots=True)`, and use an
  `enum.StrEnum` or `enum.Enum` for a closed vocabulary instead of loose
  strings.

## Keep static and runtime guarantees apart

Type hints do not validate untrusted input. Validate at the boundary that owns
the data and raise a useful exception. Never rely on `assert` for correctness,
caller validation, or a promised failure, because optimized Python removes it.
Reserve it for a debug-only check whose removal is harmless.

Use casts and ignores only after narrowing cannot express a fact the checker
misses. Keep a suppression on the smallest expression, include the exact error
code when supported, and say why the checker cannot prove it.

For a package that promises type information downstream, include and publish the
`py.typed` marker. Test the built artifact rather than assuming the source tree
reaches consumers.

Finish when the configured checker reports no new failure in changed code and
the annotations describe values the runtime really returns.
