# 0005: Persist completed runs as immutable JSON

- Each run is serialized to a temporary file in its project folder.
- The completed file is atomically renamed into place and never overwritten.
- Project subfolders remain normal folders for easy manual organization and sync.
- Extracted page text stays in a separate rebuildable cache.
- Rendering rechecks cached page hashes and exact passage offsets before showing quotes.
