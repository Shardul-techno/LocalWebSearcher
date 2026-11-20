# CODEX_NEXT_STEPS.md — From milestone 9: first Android APK, shared pipeline

This continues `CODEX_INSTRUCTIONS.md` (milestones M0 to M8 are assumed done). The principles, dependency rule, data model and config rules in that file still apply unless this file changes them.

**Source of truth for the final product:** `My_Idea.md` in the repo root. This file is the plan for getting there. If they conflict, `My_Idea.md` wins; note the conflict in `STATUS.md`.

---

## 0. Before you start

1. Read `STATUS.md` and `My_Idea.md`. If `My_Idea.md` has no section called "Model working", it is the old version: STOP and tell the owner to commit the new one.
2. Run the tests and `python -m lre doctor`. Check M0–M8 acceptance criteria. If something marked done is broken, fix it first in one separate commit.
3. Work in **stages** (below). At the end of each stage: update `STATUS.md`, commit, print the report from section 9, then **STOP and wait**. Do not begin the next stage until the owner says so.
4. Working style is unchanged: files under ~250 lines, one responsibility per module, an ADR in `docs/decisions/` for every non-obvious decision, no feature creep, everything tunable in config, no hidden globals.
5. Commands for the owner are **PowerShell 5.1** syntax (no `&&`).

## 1. Completed work — Stage 1 (M6, M7, M8)

The Windows implementation work below is already present in the repository. Do not recreate it. Only fix regressions found by the mandatory checks, and finish the outstanding Checkpoint 1 measurements/manual verification.

### M6 — Minimal Tk UI — implemented

- `src/lre/ui/tk_app.py` provides the question field, mode and project selectors, Run/Cancel, progress display, results, history and clickable source/quote links.
- Research runs on a worker thread and communicates with the UI through `queue.Queue`.
- The App menu provides storage-location and model-manager entries.
- Missing-model state is surfaced in the UI.
- Enter submits the prompt. **Shift+Enter for multiline input is not implemented yet** and remains an outstanding requirement from `My_Idea.md`.

### M7 — Reproducible setup, data paths, model manager, bundled LLM runtime — implemented

- `scripts/setup.ps1`, runtime and development lock files, and the documented PowerShell setup path are present.
- `src/lre/settings/paths.py` resolves development, portable and per-user runtime paths.
- `config/model_catalog.toml` and `src/lre/llm/model_manager.py` provide model catalog/install/remove/active-model handling, resumable downloads, SHA-256 checking and progress/cancellation hooks.
- `src/lre/llm/managed_server.py` manages a loopback llama.cpp server lifecycle.
- `scripts/fetch_llama_server.ps1` and `third_party/llama_server.lock.toml` pin and verify the Windows server runtime.
- `lre selftest` is implemented for offline packaged checks.
- A unified user-selected storage root is implemented, with separated `data/`, `cache/`, `models/`, `logs/`, `temp/` and `assets/` folders, a first-run picker, a later storage-location menu item, migration/verification and retention of the original files.
- Legacy split data/models/logs layouts are imported during first storage selection.

### M8 — Packaging and CI — implemented

- PyInstaller one-folder packaging is configured in `packaging/lre.spec`.
- The per-user Inno Setup installer is configured in `packaging/lre.iss`.
- `scripts/build_windows.ps1` builds the Windows package, runs frozen selftest, creates the portable zip and checksums.
- `.github/workflows/ci.yml` contains cross-platform tests, fresh setup and Windows package/install/selftest/uninstall jobs.
- `.github/workflows/release.yml` publishes release assets on version tags.
- `docs/testing-clean-install.md`, `LICENSE` and `THIRD_PARTY_NOTICES.md` are present.
- The installer is unsigned; the SmartScreen warning is documented.

### Additional completed work from the follow-up request

- Shared network handling exists in `src/lre/fetch/network.py`: bounded retries with backoff/jitter, retryable HTTP status handling, Retry-After handling and redacted JSONL diagnostics.
- The shared handler is used by page fetching and Wikipedia search; URL validation and isolated search-provider errors are also logged.
- Network tests exist in `tests/test_network.py`.
- Enter-to-submit is wired in the Tk prompt and covered by a UI test.
- User-selected unified storage and safe-copy migration support are implemented in `src/lre/app/preferences.py` and `src/lre/app/service.py`.

### Checkpoint 1 — still outstanding; do not claim complete until measured

The implementation milestone is complete, but the checkpoint report still needs real measurements and a clean-machine check:

- Installer size.
- Installed size.
- Cold start time.
- Time for one `search`-mode question on the owner's laptop with the bundled model.
- Manual install on a truly clean Windows machine/account using `docs/testing-clean-install.md`.
- Record exactly what was and was not verified in `STATUS.md`.

The latest `STATUS.md` records the known limitations and unverified items. Do not invent measurements or claim a clean-machine test that has not happened.

---

## 2. What the updated `My_Idea.md` changes

| New or changed item | Handled in |
|---|---|
| Installable by non-technical people (.exe) | Stage 1 — implemented; Checkpoint 1 verification remains |
| Models interchangeable, installable inside the app | Stage 1 — implemented for Windows; A1 for Android |
| Android app ASAP, Kotlin/Java allowed | Stage 2, 3 |
| Model outputs a range "passage 1, sentence 3 to 4" (sentence = start to full stop) | Stage 4; data groundwork in Stage 3 |
| Model "outputs tools like web searching" in an agentic loop | Stage 4 |
| Most-visited websites, like/dislike tuning, profiles/skills, memory, RAG, summary/prompt-bar position | Parking lot (section 7): keep hooks only |
| Unified user-selected storage root, reliable network diagnostics/recovery, output truncation detection and Enter/Shift+Enter behaviour | Windows groundwork partly implemented in Stage 1; remaining gaps must be tracked in `STATUS.md` and addressed without duplicating existing code |

## 3. New standing rules

- **R1 Installability.** Nothing in docs or scripts may assume something that is not in a fresh clone or listed as a prerequisite with a download link. Three audiences, three paths: end users (installer or APK, no commands), developers (one setup script), contributors (CI). The `pip install -e .[dev]` style instruction is **removed everywhere**; dev tools come from `requirements-dev.lock.txt`.
- **R2 Verified commands.** Every command shown in the README is executed in CI from a fresh checkout. If a command cannot be tested, do not document it as working.
- **R3 IDs, not text.** The model outputs IDs (passages now, sentence ranges and result IDs later). It never types URLs or quotes.
- **R4 Two apps, one contract.** The Python app is the reference implementation; the Kotlin Android app must match it, proven by shared test vectors in `contract/` (Stage 3).
- **R5 Privacy.** No telemetry, analytics or crash reporters. Permitted outbound traffic: the search provider, page fetches, model downloads **only on user action**, and localhost LLM calls. Android: `allowBackup=false`, no Google services, no cleartext HTTP.
- **R6 Verify, do not guess.** Download URLs, SHA-256 hashes, release asset names, library versions and command-line flags must be checked against official sources. If you cannot verify one, fail safe (refuse, or ask the user to confirm) and list it in `STATUS.md` under "Unverified".

---

# STAGE 2 — First Android APK and the README (A1, M9)

## A1 — Android skeleton that proves the model runs on the phone

**Decision (already made; do not relitigate): a native Kotlin app (Jetpack Compose) with llama.cpp through JNI. No Python on Android.** Reasons: lightest footprint, no Python runtime and no native wheel risk (`lxml`/`trafilatura`), full control of the Android lifecycle, and the owner allows Kotlin. The cost is that the pipeline logic is ported; Stage 3 controls that with shared test vectors. If the JNI or native build blocks you, STOP and report options; do not switch approach silently.

**Targets.** `compileSdk` and `targetSdk` 35 (Android 15), `minSdk` 28 unless a dependency forces higher (verify), Kotlin, Gradle Kotlin DSL with a version catalog, JDK 17, `arm64-v8a` only (x86_64 behind an opt-in flag for the emulator). Use a recent NDK so native libraries are 16 KB page-size aligned (needed for newer Android devices; verify the flag). Enable edge-to-edge (mandatory behaviour at target 35).

**Modules** (mirror the Python dependency rule):
```
android/
  settings.gradle.kts  build.gradle.kts  gradle/libs.versions.toml  gradlew  gradlew.bat
  core/            pure Kotlin/JVM: models, interfaces (LlmBackend, SearchProvider, TextExtractor, RunStore). No android.* imports
  adapters/        JVM only: OkHttp, Jsoup, search providers, extractor (filled in A3)
  llm-llamacpp/    Android library: CMake build of llama.cpp (pinned tag, git submodule) + thin JNI
  app/             Compose UI and manual wiring (no Hilt)
```
`llm-llamacpp` loads a GGUF, creates a context, applies the model's own chat template through the llama.cpp API, streams tokens, supports cancellation, and implements `LlmBackend` from `:core`. Start from the upstream llama.cpp Android example at the pinned tag, check that it builds, then simplify. Threads and context size come from config; the phone has 6 GB RAM and a Dimensity 6020, so default to models of about 1B parameters or less and a 2048 context.

**A1 scope (small on purpose).** Model screen (catalog from the shared `config/model_catalog.toml`, download with progress, resume and SHA-256 check into app-private storage) plus a "Test the model" box (single turn, streamed output, showing load time and tokens per second). That is all. The goal is an early, downloadable APK that answers the biggest risk: does the model run well on the real phone?

**Manifest and privacy.** `INTERNET` permission only; `android:allowBackup="false"` with `dataExtractionRules` excluding everything; cleartext traffic disabled; no Firebase, analytics or Google services.

**CI** `.github/workflows/android.yml` on Ubuntu: JDK 17, Android SDK and NDK, `./gradlew :core:test :app:assembleRelease`. If the secrets `ANDROID_KEYSTORE_B64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD` exist, sign the release APK; otherwise produce a debug-signed APK named `...-debug.apk`. Upload as an artifact; on tags `v*` attach to the Release with its SHA-256. Write `docs/release-setup.md` for the owner: how to create the keystore once with `keytool`, how to store it as secrets, and a warning that losing the key means the app can never be updated in place. Write `android/README.md` (build with Android Studio is optional; CI is the primary route; sideloading steps).

## M9 — README and docs (evaluator-quality, not long)

Rewrite the root `README.md` (aim for 200 to 280 lines; push detail to `docs/`). Every statement must be true of the repo at that moment; generate the project tree from `git ls-files`, never from memory. No badges for workflows that do not exist; no screenshots unless real files exist.

Required sections, in order:
1. Title, one-sentence pitch, and the USP (exact verbatim quotes with links, checked by code).
2. **Quick start for users**: Windows (download Setup.exe from Releases, SmartScreen note, first run downloads a model, ask a question); Android (download APK, allow installs from the browser, first run downloads a model). No commands needed.
3. Features: a table of **implemented / in progress / planned**, honest.
4. How it works: a short pipeline diagram (question, queries, search, fetch, extract, passages, rank, model picks IDs, code copies quotes, verify, summary) and the one-paragraph explanation of why the model never writes quotes.
5. Privacy: a table of what stays on the device and the only things that leave (search queries, page fetches, user-initiated model downloads).
6. Requirements and tested hardware.
7. Usage: Tk app, CLI examples, switching models.
8. Configuration: where the files live, key settings.
9. **Project structure**: a tree with a one-line purpose per folder, plus the dependency rule in three lines.
10. Development: prerequisites with links (Git, Python 3.11; Android Studio optional), clone, the one setup command, run, test, build installer, build APK (CI route first).
11. Testing and the shared contract.
12. Limitations and known issues (tiny-model quality, unsigned installer, early Android).
13. Roadmap (link to `My_Idea.md`), License, third-party notices.

Also add: `LICENSE` (MIT as a placeholder; list "owner must confirm" in `STATUS.md`), `THIRD_PARTY_NOTICES.md` (llama.cpp, trafilatura, httpx, PyInstaller, Inno Setup, model licenses from the catalog; verify each licence), and `docs/ARCHITECTURE.md` (the one-page module map). Add `tests/test_readme_paths.py` that checks every backticked repo path in the README exists.

**STOP, report (Checkpoint 2).** Include the APK link, load time and tokens per second on the phone if the owner reports them, and the CI status.

---

# STAGE 3 — Shared contract and the full pipeline on Android (M10, A2, A3)

## M10 — Contract (Python reference)
- **Sentences in the data model now** (even though selection stays ID-based until Stage 4): `Passage.sentences: list[(start, end)]` in the same page-text coordinates. A sentence runs from its first non-space character to and including its terminating punctuation. Split at `. `, `!`, `?` (plus any closing quote or bracket) followed by whitespace and a capital letter, digit or opening quote, or at a newline. Do not split after abbreviations from a config list (`Dr.`, `e.g.`, `i.e.`, `vs.`, `etc.`, `Fig.`, `No.`), initials, decimals or URLs. Passages are built from **whole sentences**; a sentence never spans two passages.
- **Offsets are Unicode code points.** Python does this natively; Kotlin strings are UTF-16, so the Kotlin port must convert. Add tests with emoji, CJK and combining characters.
- Add `Passage.text_sha256` (hash of the passage text) so a synced run can be checked at rest even when the page cache is absent. Bump run files to `schema_version = 2`; the reader still accepts 1.
- **Tokenizer spec for BM25** written down explicitly (maximal runs of Unicode letters and digits, lowercased with a locale-independent rule, stop-word list from config). Ties broken by passage order. Scores compared with a tolerance, rankings compared exactly.
- Create `contract/`: `README.md` (what is normative), `run.schema.json`, `samples/` (a real run file), and `vectors/*.json` generated by `scripts/gen_vectors.py` **from the Python reference**: splitting and sentences, tokenizer and BM25 ranking, text-fragment links, tolerant parsers, prompt rendering (given passages and a template, the exact output string), result rendering. A Python test fails if regenerating the vectors changes them.
- The shared files are single copies at the repo root (`prompts/`, `config/default.toml`, `config/model_catalog.toml`); the Android Gradle build copies them into assets. No duplicates in the repo.

## A2 — Kotlin pipeline port (`:core`)
Port splitter and sentences, tokenizer and BM25, verify (SHA-256), text-fragment builder, tolerant parsers, prompt rendering, output rendering, run-file models (`kotlinx.serialization`; record the dependency in an ADR), and the agent loop skeleton over the interfaces. **All `contract/vectors` must pass on the JVM in CI**; the Kotlin reader must load the Python sample run file, and a Kotlin-written run file must validate against `run.schema.json`. Add an architecture test (no `android.*` and no third-party imports in `:core` beyond the serialization library).

## A3 — Android end to end
- `:adapters`: `WikipediaProvider`; `DuckDuckGoProvider` (there is no Kotlin counterpart of the Python `ddgs` package, so implement carefully against what works today, rate-limit, fail gracefully and document the fragility); `JsoupExtractor` (strip scripts, navigation and footers, prefer `article` or `main`, join paragraphs with `\n`, deterministic); the same fetch safety rules as Python (http/https only, no private IPs, size and time caps, optional robots.txt); page cache. Extraction output need not match Python's, because offsets only have to be consistent within a run.
- Minimal Compose UI: question box, mode (simple/search/deep), Run/Cancel, progress, results as **Sources, tappable Quotes (open in the default browser with `ACTION_VIEW`), Summary**, and a history list.
- Storage: the same run-file format. Default location is app-private storage. Add "Choose sync folder" using the Storage Access Framework (`OpenDocumentTree`, persistable permission) so Syncthing-Fork can sync the same folder structure the desktop uses (projects are subfolders). Run files are written once and never edited.
- Inference and network calls run off the main thread, with working cancellation.

**STOP, report (Checkpoint 3).** Include: the APK link, on-device time for one `search`-mode question, and any contract mismatches found between Python and Kotlin.

---

## 7. Parking lot (do NOT implement; avoid blocking)

- **Profiles / skills / personalities:** files in `skills/` bundled into a profile that injects text through `agent/prompts.py` (the only place prompts are assembled).
- **Like/dislike tuning:** store feedback as separate tiny files `feedback/<run_id>_<uuid8>.json`, never by editing run files (keeps Syncthing safe). Later use: adjust ranking or prompts.
- **Most-visited websites:** derive from run files (sources are already stored); an optional local cache that is not synced.
- **Memory (optional) and RAG over files and history:** a new document source that yields `SourceDoc` and `Passage` objects, with whitelist and blacklist roots in config (Android: SAF grants).
- **Settings UI:** depth and focus sliders map onto existing config keys; summary and prompt-bar position, themes, wallpaper, window and prompt-bar size are UI-only settings.
- **MCP servers, embedding ranker, encryption at rest (wrap `RunStore`), sync conflict handling, code signing, app-store distribution.**

## 8. Repo layout additions

```
.github/workflows/  ci.yml  release.yml  android.yml
packaging/          lre.spec  lre.iss
third_party/        llama_server.lock.toml
bin/                (gitignored) llama-server.exe
contract/           README.md  run.schema.json  samples/  vectors/  eval/(Stage 4)
config/             model_catalog.toml (new)
docs/               ARCHITECTURE.md  release-setup.md  testing-clean-install.md  decisions/
android/            (section A1)
src/lre/llm/        model_manager.py  managed_server.py
src/lre/settings/   paths.py (or core/paths.py)
scripts/            setup.ps1 (rewritten)  fetch_llama_server.ps1  build_windows.ps1  gen_vectors.py
LICENSE  THIRD_PARTY_NOTICES.md  requirements-dev.lock.txt
```

## 9. Stage report template (print at each STOP)

```
STAGE <n> REPORT
Done:            <milestones completed, with commit hashes>
Verified by CI:  <jobs that passed, with links if available>
Measured:        <sizes, timings, tokens/s>
Not verified:    <anything untested, especially clean-machine and on-phone behaviour>
Unverified facts (R6): <URLs/hashes/flags/versions you could not confirm>
Decisions made:  <ADR numbers>
Problems:        <what failed or is fragile>
Suggested next:  <up to 5 tasks>
```

## 10. Definition of done for Stages 1 to 3

- A person with no Python can install from `Setup.exe`, let the app download a model, and get Sources, verified Quotes and a Summary.
- A person with an Android 15 phone can install the APK, download a model, and do the same.
- The README's commands all run in CI from a fresh checkout; `tests/test_readme_paths.py` passes.
- Python and Kotlin pass the same `contract/vectors`; run files written by either app load in the other.
- Every displayed quote passes verification on both platforms; no module breaks the dependency rule; `STATUS.md` is current.

---

# STAGE 4 — Advanced selection (M11). Do NOT start until the owner says so

1. **Sentence-range selection (both platforms).** Passages are shown to the model with numbered sentences: `[3] (1) First sentence. (2) Second sentence. ...`. The model answers `PICK: 3:2-3, 7:1-1`, meaning passage 3 sentences 2 to 3, passage 7 sentence 1. Code validates (passage exists, `1 <= first <= last <= n`, at most `max_sentences_per_quote` from config), merges overlaps, and builds each quote as `page_text[sentences[first].start : sentences[last].end]` from the stored record, then verifies it. Invalid picks fall back to the whole passage. Keep `selection.mode = "passage" | "span"` in config so the two can be compared. Update vectors, prompts and tests on both sides. Add a small offline eval set `contract/eval/` (10 to 20 questions with fixture pages) and record in `STATUS.md` a comparison table for the tiny model: valid-format rate, verified-quote rate, answer-contained rate.
2. **Tool-call protocol.** The agent's `DECIDE` step outputs exactly one line from a closed set: `SEARCH: <query>`, `OPEN: <result ids>`, or `FINISH`. Search results are shown as `[R1] title - domain`, and the model opens pages **by ID**, never by typing URLs. Tools are small classes in `agent/tools.py` (name, description, argument parser, executor) so adding `search_history` or `read_file` later means adding a class. Budgets come from config. If the output cannot be parsed twice, fall back to the deterministic M4 loop. Mirror in Kotlin.

**STOP, report (Checkpoint 4).**
