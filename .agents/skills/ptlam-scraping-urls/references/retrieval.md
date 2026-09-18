# Retrieval

This file covers bounded retrieval, completeness, safe replacement, and the JSON
result for each queued URL.

## Run the queue

Process independent URLs without exceeding `MAX_PARALLEL_TASKS`. Use bounded
concurrency or run them one by one. A host with subagents may give each task one
resolved URL and target path, start at most one batch, and wait for it before
the next.

For each URL:

1. Prefer an available page-to-Markdown scraper that returns the page body.
2. Otherwise use the host's URL-fetch tool and ask for the full page in Markdown
   with headings, paragraphs, code, lists, tables, and document order.
3. Classify access blocks, login pages, empty bodies, and error pages as
   `FAILED`.
4. Classify summaries, cut-off bodies, or other incomplete results as `PARTIAL`;
   never present them as complete captures.
5. Write an `OK` result to a temporary sibling file, confirm it is not empty,
   then replace the target atomically. Keep any older target when retrieval or
   the check fails.

## Return one JSON object per URL

Do not use a delimiter-based record that URL or error text could confuse.

```json
{
  "status": "OK",
  "url": "https://example.com",
  "file": "example-a1b2c3d4.md",
  "size_bytes": 1234,
  "detail": ""
}
```

`status` is `OK`, `PARTIAL`, or `FAILED`. A `PARTIAL` or `FAILED` object uses
`null` for `file` and `size_bytes` and gives a short `detail`. Continue after
either outcome.

Done when every queued URL has exactly one result and every `OK` target exists
at the reported non-zero size.
