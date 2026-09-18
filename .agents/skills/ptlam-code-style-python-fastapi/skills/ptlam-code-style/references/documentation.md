# Documentation and Comments

What belongs in a doc comment, and what an explanatory comment is for. The
specialization owns the doc-comment syntax and the tool that renders it.

## Document every public symbol

A doc comment on a public symbol says what the caller gets, not how the code
works. Document the caller semantics the name and signature do not express:

- what it does, in the domain's words;
- parameter meaning, units, valid ranges, and what invalid input does;
- what it returns, and what an empty or absent result means;
- expected rejections and other failures the caller must handle; and
- any constraint the signature cannot express: ordering, lifetime, threading, or
  the cost of calling it.

Do not restate an obvious parameter name or type just to fill a tag. Cover every
caller obligation once, using the stack's documentation syntax.

Add a short example only when the signature alone leaves the usage unclear. Skip
the doc comment on an internal symbol whose name and signature already say
everything. Write one the moment they do not.

## Explain why, not what

The code says what it does. A comment earns its place by saying why: the
constraint, the bug, the ordering requirement, or the rejected alternative that
is invisible from the code. A comment that restates the line below it goes stale
quietly. Delete it.

## Mark a deliberate deviation

Anything that breaks the local pattern says so where it lives. Name the rule it
departs from and what forced the departure, in a comment beside the code that
surprises the reader. Otherwise the next reader copies it or "fixes" it back.

## Do not link out of the codebase

No links to issues, pull requests, design docs, or specifications inside a
comment. They rot faster than the code, and a reader who cannot open the link is
left with nothing. Put the reasoning in the comment and the link in the pull
request.

## Mark what will go stale

When a comment records a version, a vendor behavior, an external contract, or a
deadline, say when it was true and how a reader can tell it no longer is.

## Keep comments true

A comment is part of the change. When you change the behavior it describes,
update it in the same edit or delete it. Do not leave commented-out code;
version control already remembers it.

## Finish

Finish when every public symbol you touched documents its contract, every
remaining comment explains a reason the code cannot, and nothing you changed
left a stale description behind.
