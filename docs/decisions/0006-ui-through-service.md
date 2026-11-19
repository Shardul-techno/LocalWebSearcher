# 0006: Keep the Tk interface behind the service facade

- Tk imports only the application facade and core progress events.
- Research executes in one daemon worker thread per request.
- A queue moves events and completed render results back to the UI thread.
- Quote URLs are supplied by verified rendering, then opened by the default browser.
- Future platform UIs can use the same service-shaped operations.
