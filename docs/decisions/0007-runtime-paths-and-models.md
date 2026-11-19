# 0007: Resolve runtime data and models outside a packaged application

- Development keeps data, models and overrides in the project directory.
- A frozen installation uses the user profile; portable.flag opts into sibling folders.
- Catalog models download only after an explicit install action.
- Missing catalog hashes require confirmation of the computed hash before activation.
- llama-server is loopback-only and is stopped explicitly and at process exit.
