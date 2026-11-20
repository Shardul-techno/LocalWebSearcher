# Clean-install test

Perform this test in a Windows Sandbox, VM, or separate Windows account.

1. Download `LocalResearch-Setup-<version>.exe` and `SHA256SUMS.txt`; verify the installer hash.
2. Install with default options (no admin prompt; installs under `%LOCALAPPDATA%\Programs\LocalResearch`) and launch Local Research from the Start menu.
3. Confirm the empty-state message says no model is installed, then use **Models** to download one intentionally.
4. In a Command Prompt, run `"%LOCALAPPDATA%\Programs\LocalResearch\lre.exe" selftest` and expect `[ok]`.
5. Create a test chat, uninstall, and leave the “delete local chats…” option unchecked. Reinstall and confirm the chat remains.
6. Uninstall again with that option checked; confirm `%APPDATA%\LocalResearch` and `%LOCALAPPDATA%\LocalResearch` are removed (the install folder under `Programs\LocalResearch` is removed by the uninstaller itself).
7. Windows SmartScreen will warn because the installer is unsigned: choose **More info**, then **Run anyway**. Compare the published SHA-256 before trusting the binary.
