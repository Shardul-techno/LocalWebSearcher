# This file highlights what the final project is going to be and what the priorities are; it does not highlight the intermediate steps and milestones.

## Requirements
1. The architecture needs to be modular. I should be able to easily take out a piece and use it elsewhere
2. There should be enough compatibility with at least Windows 11 and Android 15 that I will not need too large an update to fit a higher version for core functionality
3. There will be two models, one on my phone and one on my laptop
4. Both models must run locally on my laptop and phone on their specifications
	1. Laptop:
		HP Pavilion
		Processor: 12th Gen Intel(R) Core(TM) i5-1235U (1.30 GHz)
		Installed RAM: 16.0 GB (15.7 GB usable)
		Graphics card: Intel(R) Iris(R) Xe Graphics (128 MB)
		Storage: 361 GB of 477 GB used
		System type: 64-bit operating system, x64-based processor
		Pen and touch: No pen or touch input is available for this display
	2. Phone:
		Processor: Dimensity 6020 Octa-core
		Battery: 5000mAh (TYP)
		RAM: 6GB initial + 6GB expandable
		Performance booster: Trinity engine
		OS: Android 15
5. Privacy:
	1. The goal is to have a model that does not send data to the internet; 100% local privacy for prompts, messages, settings, history and usage data.
	2. Messages, settings, history and usage data must remain on the user's device unless the user explicitly chooses to sync them.
	3. Network privacy, where browser cookies, caches and history are concerned, can be tolerated.
	4. No restrictions on what I can do with it.
	5. No mandatory cloud AI service.
	6. Offline-capable interface and local history, with internet required only for online research.
7. I don't want to keep my laptop on as a server. I want both my phone and laptop to be independent but coordinating.
8. UI:
	1. I want a proper separate window and app as a UI.
	2. I want a clean, minimalistic, less cognitively triggering UI.
9. Very lightweight:
	1. I don't want an OpenWebUI-based UI due to the Docker bloat.
	2. I want to remove the need to run Docker in the background.
	3. Reuse existing architecture whenever possible.
	4. The running and storage cost in terms of hardware should be minimal; check device specifications above to confirm.
10. Chat will be synced on login, whenever Wi-Fi is available. I have experience with Syncthing and a Syncthing Android fork.
11. No unnecessarily complex infrastructure.
12. **User-selected storage location:**
	1. On first setup, the app must ask the user where to store the locally installed/downloaded models.
	2. Use the selected location as the root for the app's local data as well, including model files, databases, chat/history, memory, downloaded assets, temporary files and caches.
	3. Keep data in clearly separated subfolders (for example, models/, data/, cache/, logs/ and temp/) so individual components can be moved, backed up, cleared or reused independently.
	4. Let the user change the storage location later through Settings. Provide a safe migration process that copies/verifies data before switching paths and does not silently delete the original.
	5. Handle platform-specific storage permissions, unavailable drives, removable storage and insufficient space gracefully. Never silently fall back to filling the system drive; explain the fallback and ask for confirmation.
	6. Store only essential configuration/bootstrap information outside the selected root when the operating system requires it.
13. **Reliable networking and failure recovery:**
	1. Network and HTTPS failures must be logged with enough diagnostic detail to identify the actual cause, rather than recording only a generic "HTTPS error".
	2. Every failed operation should record the operation/stage, sanitized URL or host, timestamp, exception/error type, error message, HTTP status (if a response exists), OS/network error code (if available), timeout settings and retry count.
	3. Logs must not contain API keys, authentication headers, cookies, passwords or other secrets. Sensitive URL query parameters should be redacted.
	4. Implement bounded retries with exponential backoff and jitter for transient failures such as connection resets, temporary DNS failures, timeouts, HTTP 429 and retryable 5xx responses. Respect Retry-After when provided.
	5. Do not repeatedly retry permanent failures such as certificate validation errors, invalid URLs, unsupported protocols, most 4xx responses or blocked hosts. Surface a useful error and allow the user to retry manually.
	6. Add configurable connect/read timeouts, response-size limits, redirect limits, cancellation and an overall request deadline.
	7. If one source or search provider fails, isolate the failure and continue with other sources where possible. Preserve successful results and mark missing/failed sources clearly.
	8. Validate TLS certificates by default. Do not disable certificate verification as a workaround for HTTPS errors.
	9. Provide a diagnostic view/export so the user can inspect failures and report them without exposing private data.
	10. Add tests for common network failures and recovery behaviour, including DNS resolution errors, connection refused/reset, connect/read timeout, TLS certificate errors, invalid URLs, redirect loops, HTTP 401/403/404/408/429/5xx, empty or malformed responses, offline mode and interrupted downloads.
14. **Accurate and complete model output:**
	1. A generated answer or code block must not be silently cut off. The app must detect and clearly report incomplete or truncated output.
	2. Accuracy must not depend only on increasing model size or changing model parameters. The system should also manage context limits, output-token limits, stop sequences, prompt construction, tool results, streaming, parsing and UI rendering.
	3. Configure an appropriate maximum output-token budget for each task and model. Detect when the model stops because it reached a token/context limit or another stop condition.
	4. Preserve the model's finish/stop reason and usage metadata when the inference backend provides them. Distinguish a normal completion from a length-limit stop, interruption, timeout or backend error.
	5. For code-generation tasks, check that code fences, brackets, braces and other structural delimiters are complete where practical. Do not treat a syntactically incomplete response as a successful final answer.
	6. If output is incomplete, offer a controlled continuation or regeneration path. Continuations must preserve the preceding output and avoid duplicating or silently overwriting content.
	7. Keep the raw model response separate from parsed/rendered output so parser or UI truncation can be distinguished from model-side truncation.
	8. Add tests for long outputs, maximum-token stops, interrupted streams, malformed structured output, parser failures and UI rendering limits.
15. **Prompt input behaviour:**
	1. Pressing Enter in the prompt input must submit/run the prompt.
	2. Shift+Enter must insert a newline without submitting.
	3. Keep the Send button available as an alternative, and prevent accidental duplicate submissions while a request is already being sent.

## Idea:
- Summary:
	1. It will be a simple, small, lightweight, free, agentic model.
	2. I want a web search system that takes the strengths of Google search and agentic search and combines the advantages.
	3. The most important part of the project is to ensure that the information is as reliable as it can get. The main USP is that the application always displays the exact wording from relevant passages, with a link to the source website at the bottom that opens in the user's default browser.

- Before prompt:
	1. User can define how many web searches they want to do (Deep, search or simple search).
	2. Whether the user wants deep searches (for technical topics) or broad searches (brainstorming).
	3. User can select a profile.
	4. They can decide what initial instructions to give. The app will have several different skills; a personality is a collection of specific skills (one personality for Art, one for Programming, one for being a Good Friend...).

- Model working:
  1. The model must be interchangeable with another model as pleased. More models should be possible to install within this app itself.
  2. The model will work under an agentic loop.
  3. Model understands the search and outputs tools like web searching.
  4. After a model has found the websites, the text will be extracted and then given to the model.
  5. The model then outputs a range of values (passage 1, sentence 3 to 4). Sentence meaning start to full stop.

- Response Format:
  1. A short list of literal words/sentences taken from the text, and the link to the page it took it from will be accessible by clicking on it.
  2. The quotation should not be AI-generated, but should be exact words from the excerpts.
  3. It will have a short AI summary at the end which gives the final conclusion.

- Application:
	1. Will store history, memory (optional by user).
	2. Projects with Subfolder architecture.
	3. An interactive interface, with proper feedback, instead of a big wall of text everywhere.
	4. The model should save the history of the most commonly searched websites.
	5. There should be a liking and disliking system, where the user can tune the model's future responses.
	6. Manual syncing of history on both devices.
	7. Automatic feature to sync chat history.
	8. Will have settings mentioned below.
	9. RAG for searching personal files and for searching through my history and memory.

## Settings:
1. Set a slider for depth.
2. Set a slider for focus.
3. Select a profile.
4. Set constraints.
5. Select MCP server, if any.
6. Permission limits:
	1. Which personal files are whitelisted.
	2. Which are blacklisted.
	3. Other limits, depending on devices.
7. Select favourite websites and search engines.
8. How the response should be:
	1. Length-wise.
	2. Interactivity-wise.
	3. Graphic-wise.
	4. Other small changes.
9. UI:
	1. Theme changes.
	2. Colour preferences.
	3. Wallpaper.
	4. Size of window.
	5. Size of prompt bar.
	6. Option to change the position of the AI summary and the prompt bar.

## Priority:
1. Lightweight in terms of hardware.
2. Needs to run moderately fast.
3. Needs to have very good accuracy in terms of response.
