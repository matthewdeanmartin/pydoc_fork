"""Tkinter GUI for pydoc_fork — three-panel layout.

Left panel: command buttons
Center panel: form inputs and output log
Right panel: help/instructions
"""

import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from functools import partial
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

# ---------------------------------------------------------------------------
# Help text per command
# ---------------------------------------------------------------------------

HELP_GENERATE = """\
Generate HTML Documentation
============================
Creates static HTML docs for one or more Python
modules or packages.

Packages / Modules
  Space-separated list of importable names or
  file paths. Use "." to document everything in
  the current directory.
  Examples:
    my_package
    sys os pathlib
    . (current directory)
    path/to/module.py

Output Folder
  Directory where .html files will be written.
  Created automatically if it does not exist.

Theme
  classic - blue/purple vintage pydoc colours
  light   - modern light theme
  dark    - VS Code-style dark theme

Project Name
  Heading shown on the generated index page.

Document Internals
  Include private members (names starting with
  an underscore or not listed in __all__).

Prefer docs.python.org
  Link stdlib modules to python.org instead of
  generating local copies.

No Index
  Skip creating index.html.

Verbose
  Print detailed debug logging to the output
  panel below.
"""

HELP_OPEN = """\
Open Documentation in Browser
==============================
Opens the index.html file from the last (or
selected) output folder in your default web
browser.

If no output folder is set, you will be prompted
to choose one.
"""

HELP_ABOUT = """\
About pydoc_fork
================
pydoc_fork is a fork of CPython's pydoc module
optimised for generating static HTML documentation
in CI/CD pipelines.

Features
  • Static HTML output — no web server needed
  • Three built-in colour themes
  • Jinja2 templates (customisable)
  • Markdown and RST docstring support
  • Optional auto-discovery of related modules
  • Config via pyproject.toml [tool.pydoc_fork]

Command line
  pydoc_fork <package>... --output <folder>

Source / issues
  https://github.com/matthewdeanmartin/pydoc_fork
"""

COMMANDS = [
    ("Generate Docs", "generate"),
    ("Open in Browser", "open_browser"),
    ("About", "about"),
]


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------


class PydocForkGui(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("pydoc_fork")
        self.geometry("1000x640")
        self.minsize(800, 500)
        self._active_command = "generate"

        # Declare all instance attributes up front (populated by _build_* methods)
        self._cmd_buttons: dict[str, tk.Button] = {}
        self._center_frame: tk.Frame
        self._panel_title: tk.Label
        self._form_container: tk.Frame
        self._log: scrolledtext.ScrolledText
        self._run_btn: tk.Button
        self._clear_btn: tk.Button
        self._help_text: scrolledtext.ScrolledText

        # Form fields (generate)
        self._pkg_var = tk.StringVar(value=".")
        self._out_var = tk.StringVar(value="docs")
        self._theme_var = tk.StringVar(value="classic")
        self._proj_var = tk.StringVar(value="Python Project")
        self._internals_var = tk.BooleanVar(value=False)
        self._prefer_org_var = tk.BooleanVar(value=False)
        self._no_index_var = tk.BooleanVar(value=False)
        self._verbose_var = tk.BooleanVar(value=False)

        # Form fields (open browser)
        self._browser_out_var = tk.StringVar(value="docs")

        self._build_ui()
        self._select_command("generate")

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_ui(self):
        self.columnconfigure(0, weight=0, minsize=160)
        self.columnconfigure(1, weight=3)
        self.columnconfigure(2, weight=2, minsize=240)
        self.rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_center_panel()
        self._build_right_panel()

    def _build_left_panel(self):
        frame = tk.Frame(self, bg="#2c3e50", width=160)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_propagate(False)

        tk.Label(
            frame,
            text="pydoc_fork",
            bg="#2c3e50",
            fg="#ecf0f1",
            font=("Segoe UI", 13, "bold"),
            pady=16,
        ).pack(fill="x")

        ttk.Separator(frame, orient="horizontal").pack(fill="x", padx=8, pady=4)

        for label, key in COMMANDS:
            btn = tk.Button(
                frame,
                text=label,
                bg="#34495e",
                fg="#ecf0f1",
                activebackground="#1abc9c",
                activeforeground="#ffffff",
                relief="flat",
                anchor="w",
                padx=12,
                pady=8,
                font=("Segoe UI", 10),
                command=partial(self._select_command, key),
            )
            btn.pack(fill="x", padx=4, pady=2)
            self._cmd_buttons[key] = btn

    def _build_center_panel(self):
        self._center_frame = tk.Frame(self, bg="#f5f5f5")
        self._center_frame.grid(row=0, column=1, sticky="nsew")
        self._center_frame.columnconfigure(0, weight=1)

        self._panel_title = tk.Label(
            self._center_frame,
            text="",
            bg="#34495e",
            fg="#ffffff",
            font=("Segoe UI", 12, "bold"),
            anchor="w",
            padx=12,
            pady=8,
        )
        self._panel_title.grid(row=0, column=0, sticky="ew")

        form_container = tk.Frame(self._center_frame, bg="#f5f5f5")
        form_container.grid(row=1, column=0, sticky="ew", padx=12, pady=8)
        form_container.columnconfigure(1, weight=1)
        self._form_container = form_container

        tk.Label(
            self._center_frame,
            text="Output",
            bg="#f5f5f5",
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).grid(row=2, column=0, sticky="ew", padx=12)

        self._log = scrolledtext.ScrolledText(
            self._center_frame,
            height=10,
            state="disabled",
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            wrap="word",
        )
        self._log.grid(row=3, column=0, sticky="nsew", padx=12, pady=(0, 8))
        self._center_frame.rowconfigure(3, weight=1)

        btn_frame = tk.Frame(self._center_frame, bg="#f5f5f5")
        btn_frame.grid(row=4, column=0, sticky="ew", padx=12, pady=(0, 10))

        self._run_btn = tk.Button(
            btn_frame,
            text="Run",
            bg="#1abc9c",
            fg="#ffffff",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=6,
            command=self._run_command,
        )
        self._run_btn.pack(side="left", padx=(0, 8))

        self._clear_btn = tk.Button(
            btn_frame,
            text="Clear Output",
            bg="#95a5a6",
            fg="#ffffff",
            relief="flat",
            font=("Segoe UI", 10),
            padx=12,
            pady=6,
            command=self._clear_log,
        )
        self._clear_btn.pack(side="left")

    def _build_right_panel(self):
        frame = tk.Frame(self, bg="#ecf0f1")
        frame.grid(row=0, column=2, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        tk.Label(
            frame,
            text="Help & Instructions",
            bg="#34495e",
            fg="#ffffff",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
            padx=12,
            pady=8,
        ).grid(row=0, column=0, sticky="ew")

        self._help_text = scrolledtext.ScrolledText(
            frame,
            wrap="word",
            font=("Segoe UI", 9),
            bg="#ecf0f1",
            relief="flat",
            state="disabled",
            padx=10,
            pady=10,
        )
        self._help_text.grid(row=1, column=0, sticky="nsew")

    # ------------------------------------------------------------------
    # Command selection
    # ------------------------------------------------------------------

    def _select_command(self, key: str):
        self._active_command = key
        for k, btn in self._cmd_buttons.items():
            btn.config(bg="#1abc9c" if k == key else "#34495e")

        for widget in self._form_container.winfo_children():
            widget.destroy()

        builders = {
            "generate": self._build_generate_form,
            "open_browser": self._build_open_browser_form,
            "about": self._build_about_form,
        }
        help_texts = {
            "generate": HELP_GENERATE,
            "open_browser": HELP_OPEN,
            "about": HELP_ABOUT,
        }
        titles = {
            "generate": "Generate HTML Documentation",
            "open_browser": "Open Documentation in Browser",
            "about": "About pydoc_fork",
        }
        self._panel_title.config(text=titles.get(key, ""))
        builders[key]()
        self._set_help(help_texts.get(key, ""))
        self._run_btn.config(state="normal" if key != "about" else "disabled")

    # ------------------------------------------------------------------
    # Form builders
    # ------------------------------------------------------------------

    def _add_labeled_entry(self, label: str, variable: tk.Variable, row: int) -> tk.Entry:
        """Add a label + Entry row to the form container."""
        tk.Label(
            self._form_container,
            text=label,
            bg="#f5f5f5",
            anchor="w",
            font=("Segoe UI", 9),
        ).grid(row=row, column=0, sticky="w", pady=4, padx=(0, 8))
        entry = tk.Entry(self._form_container, textvariable=variable, font=("Segoe UI", 9))
        entry.grid(row=row, column=1, sticky="ew", pady=4)
        return entry

    def _add_folder_row(self, label: str, variable: tk.StringVar, row: int, browse_cmd):
        """Add a label + entry + browse-button row."""
        tk.Label(
            self._form_container,
            text=label,
            bg="#f5f5f5",
            anchor="w",
            font=("Segoe UI", 9),
        ).grid(row=row, column=0, sticky="w", pady=4, padx=(0, 8))
        out_frame = tk.Frame(self._form_container, bg="#f5f5f5")
        out_frame.grid(row=row, column=1, sticky="ew", pady=4)
        out_frame.columnconfigure(0, weight=1)
        tk.Entry(out_frame, textvariable=variable, font=("Segoe UI", 9)).grid(row=0, column=0, sticky="ew")
        tk.Button(
            out_frame,
            text="Browse…",
            relief="flat",
            bg="#bdc3c7",
            command=browse_cmd,
            font=("Segoe UI", 9),
            padx=6,
        ).grid(row=0, column=1, padx=(4, 0))

    def _build_generate_form(self):
        fc = self._form_container
        fc.columnconfigure(1, weight=1)

        self._add_labeled_entry("Packages / Modules:", self._pkg_var, 0)
        self._add_folder_row("Output Folder:", self._out_var, 1, self._browse_output)

        # Theme radio buttons
        tk.Label(fc, text="Theme:", bg="#f5f5f5", anchor="w", font=("Segoe UI", 9)).grid(
            row=2, column=0, sticky="w", pady=4, padx=(0, 8)
        )
        theme_frame = tk.Frame(fc, bg="#f5f5f5")
        theme_frame.grid(row=2, column=1, sticky="w", pady=4)
        for theme in ("classic", "light", "dark"):
            tk.Radiobutton(
                theme_frame,
                text=theme,
                variable=self._theme_var,
                value=theme,
                bg="#f5f5f5",
                font=("Segoe UI", 9),
            ).pack(side="left", padx=(0, 12))

        self._add_labeled_entry("Project Name:", self._proj_var, 3)

        checks = [
            ("Document Internals", self._internals_var),
            ("Prefer docs.python.org", self._prefer_org_var),
            ("No Index", self._no_index_var),
            ("Verbose", self._verbose_var),
        ]
        check_frame = tk.Frame(fc, bg="#f5f5f5")
        check_frame.grid(row=4, column=0, columnspan=2, sticky="w", pady=6)
        for i, (text, var) in enumerate(checks):
            tk.Checkbutton(
                check_frame,
                text=text,
                variable=var,
                bg="#f5f5f5",
                font=("Segoe UI", 9),
            ).grid(row=0, column=i, sticky="w", padx=(0, 16))

    def _build_open_browser_form(self):
        fc = self._form_container
        fc.columnconfigure(1, weight=1)
        self._add_folder_row("Output Folder:", self._browser_out_var, 0, self._browse_browser_folder)

    def _build_about_form(self):
        fc = self._form_container
        fc.columnconfigure(0, weight=1)

        tk.Label(
            fc,
            text="pydoc_fork",
            bg="#f5f5f5",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(8, 0))

        tk.Label(
            fc,
            text="Fork of CPython's pydoc — static HTML docs for CI",
            bg="#f5f5f5",
            font=("Segoe UI", 10),
            fg="#555555",
        ).grid(row=1, column=0, sticky="w")

        link = tk.Label(
            fc,
            text="https://github.com/matthewdeanmartin/pydoc_fork",
            bg="#f5f5f5",
            font=("Segoe UI", 9),
            fg="#3498db",
            cursor="hand2",
        )
        link.grid(row=2, column=0, sticky="w", pady=(4, 0))
        link.bind("<Button-1>", lambda _e: webbrowser.open("https://github.com/matthewdeanmartin/pydoc_fork"))

    # ------------------------------------------------------------------
    # Browse helpers
    # ------------------------------------------------------------------

    def _browse_output(self):
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self._out_var.set(folder)

    def _browse_browser_folder(self):
        folder = filedialog.askdirectory(title="Select docs folder")
        if folder:
            self._browser_out_var.set(folder)

    # ------------------------------------------------------------------
    # Run dispatcher
    # ------------------------------------------------------------------

    def _run_command(self):
        dispatch = {
            "generate": self._run_generate,
            "open_browser": self._run_open_browser,
        }
        action = dispatch.get(self._active_command)
        if action:
            action()

    def _run_generate(self):
        packages = self._pkg_var.get().strip()
        output = self._out_var.get().strip()

        if not packages:
            messagebox.showerror("Missing input", "Please enter at least one package or module name.")
            return
        if not output:
            messagebox.showerror("Missing input", "Please specify an output folder.")
            return

        cmd = [sys.executable, "-m", "pydoc_fork"]
        cmd.extend(packages.split())
        cmd += ["--output", output]
        cmd += ["--theme", self._theme_var.get()]
        cmd += ["--project_name", self._proj_var.get() or "Python Project"]

        if self._internals_var.get():
            cmd.append("--document_internals")
        if self._prefer_org_var.get():
            cmd.append("--prefer_docs_python_org")
        if self._no_index_var.get():
            cmd.append("--no_index")
        if self._verbose_var.get():
            cmd.append("--verbose")

        self._log_line("$ " + " ".join(cmd) + "\n")
        self._run_btn.config(state="disabled", text="Running…")
        threading.Thread(target=self._exec_subprocess, args=(cmd, output), daemon=True).start()

    def _exec_subprocess(self, cmd: list[str], output_folder: str):
        try:
            with subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            ) as process:
                assert process.stdout is not None
                for line in process.stdout:
                    self._log_line(line)
                process.wait()
                if process.returncode == 0:
                    self._log_line("\nDone. Output written to: " + output_folder + "\n")
                    self.after(0, lambda: self._offer_open_browser(output_folder))
                else:
                    self._log_line("\nProcess exited with code " + str(process.returncode) + "\n")
        except Exception as exc:
            self._log_line("\nError: " + str(exc) + "\n")
        finally:
            self.after(0, lambda: self._run_btn.config(state="normal", text="Run"))

    def _offer_open_browser(self, output_folder: str):
        index_path = Path(output_folder).resolve() / "index.html"
        if index_path.exists() and messagebox.askyesno(
            "Open docs?", "Documentation generated.\nOpen index.html in your browser?"
        ):
            webbrowser.open(index_path.as_uri())

    def _run_open_browser(self):
        folder = self._browser_out_var.get().strip()
        if not folder:
            messagebox.showerror("Missing input", "Please specify the docs folder.")
            return
        index_path = Path(folder).resolve() / "index.html"
        if not index_path.exists():
            self._log_line("No index.html found in: " + str(index_path.parent) + "\n")
            messagebox.showerror("File not found", "No index.html found in:\n" + str(index_path.parent))
            return
        webbrowser.open(index_path.as_uri())
        self._log_line("Opened: " + str(index_path) + "\n")

    # ------------------------------------------------------------------
    # Log helpers
    # ------------------------------------------------------------------

    def _log_line(self, text: str):
        def _append():
            self._log.config(state="normal")
            self._log.insert("end", text)
            self._log.see("end")
            self._log.config(state="disabled")

        self.after(0, _append)

    def _clear_log(self):
        self._log.config(state="normal")
        self._log.delete("1.0", "end")
        self._log.config(state="disabled")

    # ------------------------------------------------------------------
    # Help panel
    # ------------------------------------------------------------------

    def _set_help(self, text: str):
        self._help_text.config(state="normal")
        self._help_text.delete("1.0", "end")
        self._help_text.insert("1.0", text)
        self._help_text.config(state="disabled")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    """Launch the pydoc_fork GUI."""
    app = PydocForkGui()
    app.mainloop()


if __name__ == "__main__":
    main()
