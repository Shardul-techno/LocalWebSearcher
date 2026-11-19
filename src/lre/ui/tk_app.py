"""Small Tk interface. It depends only on the application facade and core events."""
import queue
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from lre.app.service import ResearchService
from lre.core.events import Event


class ResearchWindow:
    def __init__(self, root: tk.Tk, service: ResearchService | None = None):
        self.root = root
        self.service = service or ResearchService()
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.cancel = threading.Event()
        self.worker: threading.Thread | None = None
        self.question = tk.StringVar()
        self.mode = tk.StringVar(value="search")
        self.project = tk.StringVar(value="inbox")
        self.progress = tk.StringVar(value="Ready")
        self._build()
        self.reload_projects()
        self.reload_history()
        ready, message = self.service.model_ready()
        if not ready:
            self.progress.set(f"No local model ready: {message}. Use Models… to see next steps.")
        self.root.after(100, self.poll)

    def _build(self) -> None:
        self.root.title("Local Research")
        self.root.minsize(820, 540)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)
        menu = tk.Menu(self.root)
        app_menu = tk.Menu(menu, tearoff=False)
        app_menu.add_command(label="Data folder…", command=self.choose_data_folder)
        app_menu.add_command(label="Models…", command=self.models_dialog)
        menu.add_cascade(label="App", menu=app_menu)
        self.root.config(menu=menu)
        controls = ttk.Frame(self.root, padding=10)
        controls.grid(row=0, column=0, columnspan=2, sticky="ew")
        controls.columnconfigure(0, weight=1)
        ttk.Entry(controls, textvariable=self.question).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Combobox(controls, textvariable=self.mode, values=("simple", "search", "deep"), state="readonly", width=9).grid(row=0, column=1, padx=(0, 8))
        self.projects = ttk.Combobox(controls, textvariable=self.project, state="normal", width=16)
        self.projects.grid(row=0, column=2, padx=(0, 8))
        self.projects.bind("<<ComboboxSelected>>", lambda _event: self.reload_history())
        self.run_button = ttk.Button(controls, text="Run", command=self.run)
        self.run_button.grid(row=0, column=3, padx=(0, 4))
        self.cancel_button = ttk.Button(controls, text="Cancel", command=self.stop, state="disabled")
        self.cancel_button.grid(row=0, column=4)
        left = ttk.Frame(self.root, padding=(10, 0, 5, 10))
        left.grid(row=1, column=0, sticky="nsew")
        ttk.Label(left, text="Past runs").pack(anchor="w")
        self.history = tk.Listbox(left, width=30)
        self.history.pack(fill="both", expand=True)
        self.history.bind("<<ListboxSelect>>", self.show_selected)
        right = ttk.Frame(self.root, padding=(5, 0, 10, 10))
        right.grid(row=1, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)
        ttk.Label(right, textvariable=self.progress).grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.output = tk.Text(right, wrap="word", state="disabled")
        self.output.grid(row=1, column=0, sticky="nsew")

    def reload_projects(self) -> None:
        names = self.service.projects()
        if self.project.get() not in names:
            names.insert(0, self.project.get())
        self.projects["values"] = names

    def reload_history(self) -> None:
        self.history.delete(0, tk.END)
        self.runs = self.service.history(self.project.get())
        for run in self.runs:
            self.history.insert(tk.END, f"{run.created_at[:16]}  {run.question[:36]}")

    def run(self) -> None:
        question = self.question.get().strip()
        if not question:
            self.progress.set("Enter a question first.")
            return
        ready, message = self.service.model_ready()
        if not ready:
            self.progress.set(f"No local model ready: {message}")
            return
        self.cancel.clear()
        self.run_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.progress.set("Starting research…")
        self.worker = threading.Thread(target=self._ask, args=(question,), daemon=True)
        self.worker.start()

    def _ask(self, question: str) -> None:
        try:
            _, rendered = self.service.ask(question, self.project.get(), self.mode.get(), cancel=self.cancel, on_event=lambda event: self.events.put(("event", event)))
            self.events.put(("result", rendered))
        except Exception as exc:
            self.events.put(("error", str(exc)))

    def stop(self) -> None:
        self.cancel.set()
        self.progress.set("Cancelling after the current operation…")

    def poll(self) -> None:
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "event":
                    event = value
                    assert isinstance(event, Event)
                    self.progress.set(event.message)
                elif kind == "result":
                    self.show_result(value)
                    self.progress.set("Saved")
                    self.reload_projects()
                    self.reload_history()
                    self.finish()
                else:
                    self.progress.set(f"Could not run research: {value}")
                    self.finish()
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def finish(self) -> None:
        self.run_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")

    def show_result(self, rendered: object) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, "SOURCES\n")
        for index, source in enumerate(rendered.sources, 1):
            self.output.insert(tk.END, f"  {index}. {source.title} - {source.domain} - {source.url}\n")
        self.output.insert(tk.END, "\nQUOTES\n")
        for quote in rendered.quotes:
            self.output.insert(tk.END, f'  [{quote.pid}] "{quote.text}"\n      {quote.title} - ')
            start = self.output.index(tk.INSERT)
            self.output.insert(tk.END, quote.url)
            end = self.output.index(tk.INSERT)
            tag = f"quote-{quote.pid}"
            self.output.tag_add(tag, start, end)
            self.output.tag_config(tag, foreground="#1769aa", underline=True)
            self.output.tag_bind(tag, "<Button-1>", lambda _event, url=quote.url: webbrowser.open(url))
            self.output.insert(tk.END, "\n")
        self.output.insert(tk.END, f"\nSUMMARY\n  {rendered.summary}\n")
        self.output.configure(state="disabled")

    def show_selected(self, _event: object) -> None:
        selection = self.history.curselection()
        if selection:
            _, rendered = self.service.show(self.runs[selection[0]].run_id, self.project.get())
            self.show_result(rendered)

    def choose_data_folder(self) -> None:
        selected = filedialog.askdirectory(parent=self.root, title="Choose Local Research data folder")
        if selected:
            self.service.set_data_directory(Path(selected))
            messagebox.showinfo("Data folder", "Saved. Restart Local Research to use the new folder.")

    def models_dialog(self) -> None:
        messagebox.showinfo("Models", "Model manager arrives in M7.")


def main() -> None:
    root = tk.Tk()
    ResearchWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
