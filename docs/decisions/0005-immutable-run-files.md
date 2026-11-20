# 0005: Persist completed runs as immutable JSON

- Each run is serialized to a temporary file in its project folder.
- The destination is claimed with `O_CREAT|O_EXCL`, then the temp file is `os.replace`d into place. Plain rename alone is not enough: POSIX rename silently overwrites, which would mutate an immutable run.
- Project subfolders remain normal folders for easy manual organization and sync.
- Extracted page text stays in a separate rebuildable cache.
- Rendering rechecks cached page hashes and exact passage offsets before showing quotes.
