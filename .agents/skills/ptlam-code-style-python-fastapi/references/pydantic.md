# Pydantic v2

Pydantic v2 validation and serialization mechanics for a Python project that
already uses Pydantic.

Check the installed major version and the project's shared base models before
editing. If the project uses Pydantic v1 or a compatibility layer, follow that
repository instead of mixing APIs from this reference.

Use a Pydantic model when data crosses an untrusted validation, serialization,
or schema boundary. Prefer a dataclass or ordinary typed object for trusted
internal state that needs none of those behaviors.

## Declare the contract

- Put simple bounds, patterns, aliases, descriptions, and factories in `Field`.
- Use `default_factory` for every mutable or computed default.
- Keep defaults intrinsically valid. Set `validate_default` on the field or
  model when constraints or validators must also run on defaults.
- Choose coercive or strict validation at the owning boundary and test the
  accepted conversions; do not enable strict mode everywhere by reflex.
- Set shared behavior with `ConfigDict`; choose the extra-field policy and alias
  behavior deliberately instead of inheriting them by accident.
- Use `field_validator` for one field and `model_validator` for a cross-field
  invariant. A validator is deterministic, performs no I/O, and returns the
  value or instance its mode requires.
- Use `PrivateAttr(default_factory=...)` for non-serialized mutable state.
- Put post-validation setup in `model_post_init` instead of overriding
  `BaseModel.__init__`.
- Prefer concrete `list`, `tuple`, and `dict` field types when the accepted
  shape is known. Use an abstract collection only when the schema promises it.

Use v2 operations: `model_validate`, `model_dump`, `model_dump_json`, and
`model_json_schema`. Enable `from_attributes` only on a model that intentionally
reads object attributes. Never use `model_construct` with untrusted data.

Keep Python field names in the project's Python convention. Centralize wire
aliases and serialization defaults at the owning external boundary so every
caller cannot choose a different payload shape.

The [Pydantic model](https://docs.pydantic.dev/latest/concepts/models/) and
[validator](https://docs.pydantic.dev/latest/concepts/validators/) links
identify the canonical APIs; they are not required reading. When the locked
major differs or an operation is unavailable, inspect the installed package and
prove the version-specific behavior with a focused local test.

Finish when input outside the chosen coercion policy fails, defaults and valid
input produce the declared types, and round-trip tests cover every alias or
custom serializer.
