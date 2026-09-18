# Output Files

This file covers filename derivation, collisions, and the freshness check that
maps URLs to unique target files.

## Derive the filename

For each valid URL:

1. Remove the `http://` or `https://` prefix.
2. Remove trailing slashes.
3. Replace `/`, `?`, `&`, `=`, `#`, and `:` with `-`.
4. Replace characters unsafe in a filename with `-`.
5. Collapse repeated hyphens.
6. Append `-<digest>.md`, where `<digest>` is the first eight hex characters of
   the normalized URL's SHA-256 digest.

So `https://docs.example.com/api/auth` becomes
`docs.example.com-api-auth-a1b2c3d4.md`. The digest is always added, so a URL
keeps the same filename whether it is scraped alone or beside a colliding URL.

## Check freshness

Read each target file's modification time and size.

| Platform | Modification-time command |
| -------- | ------------------------- |
| macOS    | `stat -f %m <file>`       |
| Linux    | `stat -c %Y <file>`       |

A file is fresh when its age is below `CACHE_TTL_HOURS` and its size is above
zero. Record a fresh file as `CACHED` with its size and drop it from the queue.
Queue missing, empty, expired, and unreadable files. When `CACHE_TTL_HOURS` is
`0`, queue every URL.

Done when every valid URL maps to one unique path inside the output folder and
is either `CACHED` or queued exactly once.
