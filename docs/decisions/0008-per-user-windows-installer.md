# 0008: Per-user Windows installer, no admin

- The Inno Setup script uses `PrivilegesRequired=lowest` and installs to `%LOCALAPPDATA%\Programs\LocalResearch`.
- End users should not need an administrator account for a privacy-local desktop research tool.
- Start Menu and optional desktop shortcuts are created for the current user only.
- Uninstall leaves chats, settings and models alone unless the user ticks the optional delete-userdata task.
