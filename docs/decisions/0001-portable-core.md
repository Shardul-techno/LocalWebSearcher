# 0001: Keep the core portable

- Core models contain only standard-library types.
- Platform and network details belong behind adapters.
- This keeps a future Android runtime from inheriting desktop dependencies.
- Current delivery targets Windows 11 and Python 3.11.
- Android UI and inference packaging are deferred.
