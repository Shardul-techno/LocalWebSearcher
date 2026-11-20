# Third-party notices

This is an initial inventory of the components explicitly called out by the project plan. It is not yet a complete license report for every transitive Python dependency or every file in a packaged runtime. Recheck the exact versions and notices before publishing a release.

## Runtime and extraction libraries

| Component | Pinned/current use | Upstream license information |
|---|---|---|
| [llama.cpp](https://github.com/ggml-org/llama.cpp) | Windows CPU server runtime; exact archive is recorded in `third_party/llama_server.lock.toml` | MIT. The upstream repository contains the MIT license. Preserve the license files shipped inside the runtime archive. |
| [Trafilatura](https://github.com/adbar/trafilatura) | `trafilatura==2.3.1` | Apache License 2.0. Upstream states versions before 1.8.0 were GPLv3+; the pinned version is newer than that boundary. |
| [HTTPX](https://github.com/encode/httpx) | `httpx==0.28.1` | BSD 3-Clause. Preserve the copyright and license notice as required by that license. |

## Build and packaging tools

| Component | Pinned/current use | Upstream license information |
|---|---|---|
| [PyInstaller](https://github.com/pyinstaller/pyinstaller) | `pyinstaller==6.22.3` on Windows development/build environments | GPL-2.0-or-later with the PyInstaller Bootloader Exception; selected files use Apache-2.0. Follow the upstream `COPYING.txt` and license documentation for the exact file-level terms. |
| [Inno Setup](https://jrsoftware.org/isinfo.php) | Installed by the Windows CI job using Chocolatey; the workflow does not currently pin an exact Inno Setup version | The upstream site asks commercial users to purchase a commercial license. CI may build without installing a license key, but that does not settle the owner's obligations for commercial use. Review the exact `LICENSE.TXT` shipped with the installed version and obtain a commercial license if applicable. |

## Model weights

| Catalog entry | Upstream model | Declared license |
|---|---|---|
| `qwen35-0.8b-q4` | [Qwen/Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B) and [ggml-org/Qwen3.5-0.8B-GGUF](https://huggingface.co/ggml-org/Qwen3.5-0.8B-GGUF) | Apache-2.0 is declared by both the official Qwen model card and the GGUF repository metadata. |
| `qwen35-2b-q4` | [Qwen/Qwen3.5-2B](https://huggingface.co/Qwen/Qwen3.5-2B) and [ente-ai/Qwen3.5-2B-GGUF](https://huggingface.co/ente-ai/Qwen3.5-2B-GGUF) | Apache-2.0 is declared by the official Qwen model card and the GGUF repository metadata. |

Model files are downloaded from the URLs in `config/model_catalog.toml` only after the user chooses Install. The model catalog currently has empty SHA-256 fields, so the application computes the downloaded file's hash and requires user confirmation before selecting an unverified model. A model's license does not establish that its download URL, hash, or conversion provenance has been independently verified.

## Remaining license work

- Generate a complete inventory from the exact contents of `requirements.lock.txt` and `requirements-dev.lock.txt`, including transitive dependencies and platform-specific packages.
- Record the exact Inno Setup version installed in CI and archive/review its corresponding `LICENSE.TXT`.
- Verify the exact llama.cpp release archive and preserve all notices included in it.
- Confirm that the repository's MIT `LICENSE` is the owner's intended license before public release.
- Recheck model-card and conversion-repository license metadata when catalog URLs or model versions change.

This document is informational and is not legal advice.
