# Configuration

This file covers the workspace root, the configuration file, the three keys, and
how a prompt override wins.

## Fix the workspace root first

Use the workspace root the run started in. Do not swap it for a nested
repository found later or for a folder the run moves into. When the host shows
several roots and the intended one is unclear, ask which root owns the run.

## The configuration file

```text
<workspace-root>/.ptlam-agent-plugin/ptlam-scraping-urls/CONFIG.yml
```

On the first run, create the parent folder and copy
[the default configuration](../assets/CONFIG.yml) there. On later runs, keep
manual edits and read the file every time before resolving values.

## The three keys

| Key                  | Meaning                                      | Valid value                              |
| -------------------- | -------------------------------------------- | ---------------------------------------- |
| `OUTPUT_DIRECTORY`   | Default folder for scraped Markdown files    | Non-empty path inside the workspace root |
| `MAX_PARALLEL_TASKS` | Most scrape jobs running at once             | Positive integer                         |
| `CACHE_TTL_HOURS`    | Age below which an existing output is reused | Non-negative number; `0` disables reuse  |

## Resolve each key

Resolve every key on its own. Use the prompt's value when the user gives one;
otherwise use the file's value. The prompt may override any key with an
assignment, a YAML block, or a clear plain-language instruction. This prompt
overrides all three:

```text
OUTPUT_DIRECTORY=docs/archive MAX_PARALLEL_TASKS=3 CACHE_TTL_HOURS=24
https://docs.example.com/start
https://docs.example.com/api
```

A prompt override applies to the current run only. Change `CONFIG.yml` itself
only when the user explicitly asks to save new defaults.

Normalize the effective output path before creating it. Reject `..`, symlink, or
absolute-path escapes from the workspace unless the user explicitly names that
outside destination for this run. Never save an outside path as the default.
When outside output is allowed, report that boundary before writing.

Report an invalid effective value and stop before creating the output folder.
Never quietly replace a hand-edited configuration.
