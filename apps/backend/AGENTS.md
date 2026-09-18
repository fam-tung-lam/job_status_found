# Backend agent notes

## Docstrings

- Style: Google (`Args:`, `Returns:`, `Yields:`, `Raises:`, `Attributes:`,
  `Example:`). Do not mix NumPy or Sphinx field styles.
- Every public module, package, class, function, method, and property has a
  docstring. `_private` names and `tests/` are exempt.
- Do not repeat types; annotations carry them.
- Property docstrings describe the value ("Whether...", "The..."), never start
  with a verb such as "Returns".
- Document class attributes and Pydantic fields with an attribute docstring on
  the line after the declaration. Pydantic models set
  `use_attribute_docstrings=True` so the text also reaches the JSON schema.
- Enforced by Ruff `D` (convention `google`) plus preview rules `D420`, `D421`,
  and `DOC*`, selected by exact code in `pyproject.toml`.
- Docstrings are read in code and IDE hovers only; there is no generated
  documentation site.

## Checks

```shell
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest --cov
```

