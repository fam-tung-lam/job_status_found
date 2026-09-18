# Python Modules and Imports

Python import, publication, and file-placement mechanics.

## Publish one intentional API

Use the repository's package layout. When a new packaged project has none, put
importable code under `src/<package>/` and mirror its capability structure under
`tests/`.

Python spells an internal module or name with a leading underscore. Publish a
supported name deliberately through the package entry point and `__all__` when
the repository uses it. Never expose an implementation just so a test can import
it.

A public re-export is a compatibility promise. Keep it, deprecate it through the
project's mechanism, or treat its removal as a breaking change. Keep
`__init__.py` about package composition; importing the package must not start
services, read remote state, or do expensive work.

When splitting an implementation module, preserve supported import paths with
explicit re-exports. Keep `_` helpers out of those facades and `__all__`; moving
code does not make its implementation part of the package contract.

## Keep imports directional

- Let the formatter or import sorter own grouping and order.
- Match the package's choice of absolute or explicit relative imports. Do not
  mix styles inside one changed module without a boundary reason.
- A consumer outside the package imports its published surface. Internal code
  may import the owning module directly when re-exporting through `__init__.py`
  would load unrelated code eagerly or create a cycle.
- Put annotation-only imports behind `TYPE_CHECKING` when runtime evaluation is
  unnecessary and the annotation policy allows it.
- Avoid wildcard imports. Name every dependency the module uses.

Keep imports at module scope by default. A local import needs a verified runtime
reason, such as an optional dependency or a cycle you cannot yet remove. When
moving the import only hides the cycle, fix the direction instead.

## Keep files owned

Name a module after its one responsibility. Use the project's existing package
and test names; do not add `helpers.py`, `utils.py`, or a new folder as a
speculative home.

Put a new test beside the existing tests for its unit. With no pattern, mirror
the source path and name the file `test_<module>.py`. Split one unit across
several test files only by stable behavior, never by bug or change ID.

Finish when every import follows the declared direction, the package exports
only supported names, and each new file has one concrete owner.
