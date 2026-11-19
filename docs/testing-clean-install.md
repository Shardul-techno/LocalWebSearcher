# Clean-install test

Perform this test in a Windows Sandbox, VM, or separate Windows account.

1. Download `LocalResearch-Setup-<version>.exe` and `SHA256SUMS.txt`; verify the installer hash.
2. Install with default options and launch Local Research from the Start menu.
3. Confirm the empty-state message says no model is installed, then use **Models** to download one intentionally.
4. In a Command Prompt, run `"C:\Program Files\Local Research\lre.exe" selftest` and expect `[ok]`.
5. Create a test chat, uninstall, and leave the “delete local chats…” option unchecked. Reinstall and confirm the chat remains.
6. Uninstall again with that option checked; confirm `%APPDATA%\LocalResearch` and `%LOCALAPPDATA%\LocalResearch` are removed.
