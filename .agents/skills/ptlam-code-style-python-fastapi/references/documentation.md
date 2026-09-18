# Python Docstrings

Python docstring syntax and tool mechanics.

## Document every public name

Give every public module, package, class, function, method, and property a
Google-style docstring. That includes every `__init__.py`: give it at least a
one-line docstring that says what the package owns (Ruff rule D104). Names that
start with an underscore and everything under `tests/` are exempt.

Document each Pydantic model field with an attribute docstring, the string
literal on the line after the field, and set
`model_config = ConfigDict(use_attribute_docstrings=True)` so the docstring
becomes the field's schema description. An explicit `Field(description=...)`
overrides that docstring, so do not set both.

Ruff enforces the docstring requirement, and
[dev-toolchain.md](dev-toolchain.md) owns its configuration. No Ruff rule checks
Pydantic field docstrings, so review them.

A repository that already enforces NumPy, Sphinx, or another section style keeps
it until migrating is in scope. Do not mix section styles in one project.

## Write the docstring

Use a PEP 257-compatible triple-double-quoted docstring: one summary sentence, a
blank line, then the required detail. Put it as the first statement of the
documented module, package, class, or callable. Let type annotations carry types
instead of repeating them in prose.

Use Google sections only when they apply, and put `Args:` before `Returns:` or
`Yields:`, and both before `Raises:`. Describe only parameters the signature
has, values it returns or yields, and exceptions it raises on purpose. Start a
`@property` docstring with the value it describes, not a verb such as "Returns".
Treat a doctest as executable only when the repository collects it.

Finish when every public name has a Google-style docstring, `ruff check` passes
the `D` and `DOC` rules, every Pydantic field has an attribute docstring, and,
when the repository generates API documentation, the rendered contract matches
the implementation and tests.
