"""
Basic NiceGUI frontend for the data sanitizer backend.

What this page does:
- Upload a .txt file, send it to S3 via a presigned URL, then auto-load the report.
- Or, type a filename and load an existing report.

Backend endpoints used:
- POST /upload-url
- GET /report?filename=...
- GET /download?filename=...

Notes for future edits:
- The request helpers use `requests`, so async handlers run them with `run.io_bound(...)`.
- Keep UI creation inside `@ui.page('/')` to avoid NiceGUI slot/context errors.
- The results card starts hidden and is shown only after successful fetch.

Authors:
  Kai'lyn Mohammed
  Reem Khalid
  Yas'lyn Mohammed

"""

import asyncio

import requests
from nicegui import run, ui


API_BASE_URL = "https://riwzsm6apd.execute-api.us-east-2.amazonaws.com/prod"


# API calls (sync, run in a thread via run.io_bound)

def fetch_results(filename: str) -> dict:
    report_url   = f"{API_BASE_URL}/report"
    download_url = f"{API_BASE_URL}/download"

    report_response = requests.get(report_url, params={"filename": filename}, timeout=30)
    report_response.raise_for_status()
    report_data = report_response.json()

    download_response = requests.get(download_url, params={"filename": filename}, timeout=30)
    download_response.raise_for_status()
    download_data = download_response.json()

    return {"report": report_data, "download": download_data}


def get_upload_url(filename: str) -> dict:
    response = requests.post(f"{API_BASE_URL}/upload-url", json={"filename": filename}, timeout=30)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict) or not data.get("upload_url"):
        raise ValueError("/upload-url response did not include upload_url")
    return data


def upload_file_to_s3(upload_url: str, file_bytes: bytes) -> None:
    response = requests.put(upload_url, data=file_bytes, headers={"Content-Type": "text/plain"}, timeout=60)
    response.raise_for_status()


# CSS

THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

body {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #0f2744 100%);
    min-height: 100vh;
    margin: 0;
}

.app-shell { max-width: 1000px; margin: 0 auto; padding: 32px 20px; }

.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub { color: #cbd5e1; font-size: 0.95rem; }

.card {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 16px;
    padding: 24px;
    backdrop-filter: blur(10px);
}

.card-title {
    font-weight: 600;
    font-size: 1rem;
    color: #f1f5f9;
    margin-bottom: 4px;
}

.divider { border-top: 1px solid rgba(255,255,255,0.12); margin: 8px 0; }

.status-bar {
    background: rgba(0,0,0,0.35);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 0.85rem;
    color: #cbd5e1;
    font-family: 'JetBrains Mono', monospace;
}

.risk-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.risk-low    { background: #bbf7d0; color: #14532d; }
.risk-medium { background: #fde68a; color: #78350f; }
.risk-high   { background: #fecaca; color: #7f1d1d; }
.risk-unknown { background: #e2e8f0; color: #334155; }

.mono { font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; }

/* ── Quasar input / textarea overrides for dark background ── */
.q-field--outlined .q-field__control {
    background: rgba(255,255,255,0.08) !important;
}
.q-field--outlined .q-field__control:before {
    border-color: rgba(255,255,255,0.25) !important;
}
.q-field--outlined:hover .q-field__control:before {
    border-color: rgba(255,255,255,0.5) !important;
}
.q-field__native,
.q-field__input,
.q-field__label,
.q-field__marginal {
    color: #f1f5f9 !important;
}
.q-field__native::placeholder,
.q-field__input::placeholder {
    color: #94a3b8 !important;
}
/* textarea read-only sanitized output */
.q-textarea .q-field__native {
    color: #e2e8f0 !important;
}

.results-section { animation: fadeUp 400ms ease both; }
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
"""


# Page

@ui.page('/')
async def main_page() -> None:
    ui.add_head_html(THEME)

    upload_state = {
        "filename":     "",
        "file_bytes":   b"",
        "ready_to_get": False,
    }

    # UI helpers (closures, so they reference widget variables defined below)

    def set_status(text: str, busy: bool = False) -> None:
        status_label.set_content(f'<span class="status-bar">Status: {text}</span>')
        if busy:
            spinner.classes(remove="hidden")
        else:
            spinner.classes(add="hidden")

    def render_risk_badge(risk: str) -> None:
        risk_badge_slot.clear()
        css = {"low": "risk-low", "medium": "risk-medium", "high": "risk-high"}.get(
            risk.lower(), "risk-unknown"
        )
        with risk_badge_slot:
            ui.html(f'<span class="risk-badge {css}">{risk}</span>', sanitize=False)

    def render_download_link(url: str) -> None:
        download_link_slot.clear()
        with download_link_slot:
            if url:
                ui.link("Download sanitized file", url, new_tab=True).classes(
                    "text-sky-400 hover:underline text-sm"
                )
            else:
                ui.label("No download link returned").classes("text-slate-500 text-sm")

    def update_results_ui(result: dict) -> None:
        report   = result.get("report",   {}) or {}
        download = result.get("download", {}) or {}

        risk           = str(report.get("risk_level",    "-")).lower()
        total_findings = report.get("total_findings",   "-")
        by_type        = report.get("findings_by_type", {}) if isinstance(report.get("findings_by_type"), dict) else {}
        sanitized_text = report.get("sanitized_text",   "") if isinstance(report.get("sanitized_text"),  str)  else ""
        file_url       = download.get("download_url",   "") if isinstance(download.get("download_url"),  str)  else ""

        render_risk_badge(risk)
        total_label.set_text(str(total_findings))
        counts_label.set_text(
            "\n".join(f"{k}: {v}" for k, v in by_type.items()) if by_type
            else "No findings by type returned."
        )
        sanitized_output.value = sanitized_text
        render_download_link(file_url)
        results_card.classes(remove="hidden")

    async def load_results_for_filename(filename: str) -> None:
        result = await run.io_bound(fetch_results, filename)
        update_results_ui(result)

    # Handlers

    async def on_file_selected(event) -> None:
        file_obj = getattr(event, "file", None)
        if file_obj is None:
            ui.notify("Could not read selected file.", color="negative")
            return

        filename = (getattr(file_obj, "name", "") or "").strip()
        if not filename.lower().endswith(".txt"):
            ui.notify("Only .txt files are allowed.", color="negative")
            upload_state["filename"]   = ""
            upload_state["file_bytes"] = b""
            selected_file_label.set_text("No file selected")
            return

        file_bytes = await file_obj.read()
        upload_state["filename"]     = filename
        upload_state["file_bytes"]   = file_bytes
        upload_state["ready_to_get"] = False
        filename_input.value = filename
        selected_file_label.set_text(f"{filename}  ·  {len(file_bytes):,} bytes")
        set_status("File selected — click Upload & Process")
        ui.notify(f"{filename} ready to upload.", color="info")

    async def on_upload_and_process() -> None:
        filename   = upload_state["filename"]
        file_bytes = upload_state["file_bytes"]

        if not filename or not file_bytes:
            ui.notify("Please select a .txt file first.", color="negative")
            return

        try:
            set_status("Requesting upload URL…", busy=True)
            upload_payload = await run.io_bound(get_upload_url, filename)
            presigned_upload_url = str(upload_payload.get("upload_url", ""))
            if not presigned_upload_url:
                raise ValueError("upload_url missing from /upload-url response")

            set_status("Uploading to S3…", busy=True)
            await run.io_bound(upload_file_to_s3, presigned_upload_url, file_bytes)

            set_status("Processing — please wait…", busy=True)
            await asyncio.sleep(3)

            set_status("Fetching report…", busy=True)
            await load_results_for_filename(filename)
            set_status("Results loaded.")
            ui.notify("Report ready.", color="positive")
        except requests.HTTPError as exc:
            set_status(f"Failed ({exc.response.status_code})")
            ui.notify(f"HTTP error: {exc}", color="negative", multi_line=True)
        except requests.RequestException as exc:
            set_status("Network error")
            ui.notify(f"Network error: {exc}", color="negative", multi_line=True)
        except Exception as exc:
            set_status(f"Failed: {exc}")
            ui.notify(f"Error: {exc}", color="negative", multi_line=True)

    async def on_get_results() -> None:
        filename = (filename_input.value or "").strip()
        if not filename:
            ui.notify("Please enter or upload a filename.", color="negative")
            return

        set_status("Fetching report…", busy=True)

        try:
            await load_results_for_filename(filename)
            set_status("Results loaded.")
            ui.notify("Report ready.", color="positive")
        except requests.HTTPError as exc:
            set_status(f"Failed ({exc.response.status_code})")
            ui.notify(f"HTTP error: {exc}", color="negative", multi_line=True)
        except requests.RequestException as exc:
            set_status("Network error")
            ui.notify(f"Network error: {exc}", color="negative", multi_line=True)
        except Exception as exc:
            set_status(f"Failed: {exc}")
            ui.notify(f"Error: {exc}", color="negative", multi_line=True)

    # UI

    with ui.column().classes("app-shell gap-6"):

        # Header
        with ui.column().classes("gap-1"):
            ui.html('<div class="hero-title">Data Sanitizer</div>', sanitize=False)
            ui.html('<div class="hero-sub">Upload a file to scan it for PII, or look up a file you\'ve already processed.</div>', sanitize=False)

        # cards
        with ui.row().classes("w-full gap-4 flex-wrap"):

            # Upload card
            with ui.column().classes("card flex-1 gap-3").style("min-width:280px"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("upload_file").classes("text-sky-400 text-xl")
                    ui.html('<div class="card-title">Upload &amp; Scan</div>', sanitize=False)
                ui.html('<div class="hero-sub" style="font-size:0.82rem">Pick a .txt file — we\'ll scan it and show you what was found.</div>', sanitize=False)
                ui.html('<div class="divider"></div>', sanitize=False)

                selected_file_label = ui.label("No file selected").classes("text-sm text-slate-400")

                with ui.row().classes("items-center gap-3 flex-wrap"):
                    ui.upload(
                        label="Choose .txt",
                        auto_upload=True,
                        on_upload=on_file_selected,
                    ).props('accept=".txt,text/plain"')
                    ui.button(
                        "Upload & Process", icon="send",
                        on_click=on_upload_and_process,
                        color="blue-8",
                    ).props("unelevated")

            # Lookup card
            with ui.column().classes("card flex-1 gap-3").style("min-width:280px"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("search").classes("text-indigo-400 text-xl")
                    ui.html('<div class="card-title">Look Up Results</div>', sanitize=False)
                ui.html('<div class="hero-sub" style="font-size:0.82rem">Already uploaded a file? Enter its name to pull the report.</div>', sanitize=False)
                ui.html('<div class="divider"></div>', sanitize=False)

                filename_input = ui.input(placeholder="e.g. ancestor.txt").props("outlined dense").classes("w-full")
                ui.button(
                    "Get Results", icon="bar_chart",
                    on_click=on_get_results,
                    color="indigo-8",
                ).props("unelevated")

        # Status bar
        with ui.row().classes("w-full items-center gap-3"):
            spinner = ui.spinner("dots", size="sm", color="sky").classes("hidden")
            status_label = ui.html('<span class="status-bar">Status: Waiting</span>', sanitize=False).classes("flex-1")

        # results (hidden until loaded)
        results_card = ui.column().classes("card results-section gap-4 w-full hidden")
        with results_card:
            with ui.row().classes("items-center gap-3 flex-wrap"):
                ui.icon("verified_user").classes("text-sky-400 text-2xl")
                ui.label("Scan Report").classes("text-lg font-semibold text-slate-100")
                risk_badge_slot = ui.row()

            ui.html('<div class="divider"></div>', sanitize=False)

            with ui.row().classes("gap-6 flex-wrap"):
                with ui.column().classes("gap-1"):
                    ui.label("Total Findings").classes("text-xs font-medium text-slate-400 uppercase tracking-wide")
                    total_label = ui.label("-").classes("text-2xl font-bold text-slate-100")
                with ui.column().classes("gap-1"):
                    ui.label("Findings by Type").classes("text-xs font-medium text-slate-400 uppercase tracking-wide")
                    counts_label = ui.label("-").classes("mono text-slate-300 whitespace-pre-wrap")

            ui.html('<div class="divider"></div>', sanitize=False)

            ui.label("Sanitized Text").classes("text-xs font-medium text-slate-400 uppercase tracking-wide")
            sanitized_output = (
                ui.textarea(value="")
                .props("readonly autogrow outlined")
                .classes("w-full mono")
            )

            ui.html('<div class="divider"></div>', sanitize=False)

            with ui.row().classes("items-center gap-2"):
                ui.icon("download").classes("text-sky-400")
                ui.label("Download").classes("text-sm font-medium text-slate-300")
                download_link_slot = ui.row().classes("items-center")


ui.run(port=8080, title="Data Sanitizer App")
