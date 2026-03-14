import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from nicegui import events, ui

try:
    from api_client import APIClientError, DataSanitizerAPIClient
except ImportError:
    from client.api_client import APIClientError, DataSanitizerAPIClient


APP_TITLE = "Data Sanitizer"
HISTORY_CACHE: List[Dict[str, Any]] = []

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

:root {
  --bg-1: #fff4df;
  --bg-2: #f4fbf1;
  --ink: #0f172a;
  --muted: #475569;
  --panel: rgba(255, 255, 255, 0.82);
  --line: rgba(15, 23, 42, 0.12);
  --accent: #0f766e;
  --accent-2: #b45309;
}

body {
  font-family: 'Space Grotesk', sans-serif;
  color: var(--ink);
  background:
    radial-gradient(1300px 700px at -10% -10%, #ffeec2 0%, transparent 60%),
    radial-gradient(900px 700px at 110% 0%, #dcfce7 0%, transparent 60%),
    linear-gradient(140deg, var(--bg-1) 0%, var(--bg-2) 100%);
}

.mono {
  font-family: 'IBM Plex Mono', monospace;
}

.shell {
  max-width: 1120px;
  margin: 0 auto;
  padding: 16px;
}

.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 18px;
  backdrop-filter: blur(8px);
}

.fade-up {
  animation: rise 480ms ease-out both;
}

@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.risk-low {
  color: #166534;
  background: #dcfce7;
}

.risk-medium {
  color: #92400e;
  background: #fef3c7;
}

.risk-high {
  color: #991b1b;
  background: #fee2e2;
}

@media (max-width: 768px) {
  .shell {
    padding: 10px;
  }
}
</style>
"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _risk_level(result: Dict[str, Any]) -> str:
    report = result.get("report", {})
    risk = report.get("risk_level", "unknown") if isinstance(report, dict) else "unknown"
    return str(risk).lower()


def _risk_class(risk: str) -> str:
    if risk not in {"low", "medium", "high"}:
        return "risk-medium"
    return f"risk-{risk}"


def _format_counts(report: Dict[str, Any]) -> List[str]:
    by_type = report.get("findings_by_type", {}) if isinstance(report, dict) else {}
    if not isinstance(by_type, dict) or not by_type:
        return ["No categorized findings available."]
    return [f"{name}: {count}" for name, count in by_type.items()]


def _get_history() -> List[Dict[str, Any]]:
    return HISTORY_CACHE


def _save_history(result: Dict[str, Any], source_file: str, api_base_url: str) -> None:
    history = _get_history()
    history.insert(
        0,
        {
            "saved_at": _now_iso(),
            "source_file": source_file,
            "api_base_url": api_base_url,
            "result": result,
        },
    )
    if len(history) > 12:
        del history[12:]


def _top_nav(active: str) -> None:
    with ui.row().classes("w-full items-center justify-between shell"):
        with ui.row().classes("items-center gap-2"):
            ui.icon("verified_user").classes("text-2xl text-teal-700")
            ui.label(APP_TITLE).classes("text-2xl font-bold")
        with ui.row().classes("gap-2"):
            ui.button("Analyze", on_click=lambda: ui.navigate.to("/"), color="teal-8").props(
                "unelevated"
            ).set_enabled(active != "home")
            ui.button("Results", on_click=lambda: ui.navigate.to("/results"), color="amber-8").props(
                "unelevated"
            ).set_enabled(active != "results")


@ui.page("/")
def home_page() -> None:
    ui.add_head_html(THEME_CSS)
    _top_nav("home")

    state: Dict[str, str] = {"uploaded_text": "", "file_name": "uploaded.txt"}

    @ui.refreshable
    def quick_snapshot() -> None:
        history = _get_history()
        if not history:
            with ui.column().classes("panel p-4 w-full fade-up"):
                ui.label("No processed files yet.").classes("text-base text-slate-700")
                ui.label("Run your first analysis to see risk summary and findings here.").classes(
                    "text-sm text-slate-500"
                )
            return

        latest = history[0]
        result = latest.get("result", {})
        report = result.get("report", {}) if isinstance(result.get("report"), dict) else {}
        risk = _risk_level(result)
        total = report.get("total_findings", len(result.get("detections", [])))

        with ui.column().classes("panel p-4 w-full fade-up").style("animation-delay: 120ms"):
            with ui.row().classes("items-center justify-between w-full"):
                ui.label("Latest Scan").classes("text-lg font-semibold")
                ui.badge(risk.upper(), color="transparent").classes(f"px-3 py-1 {_risk_class(risk)}")
            ui.label(f"File: {latest.get('source_file', 'unknown')} | Findings: {total}").classes(
                "text-sm text-slate-700"
            )
            for line in _format_counts(report):
                ui.label(line).classes("text-sm text-slate-600 mono")

    async def process_content() -> None:
        content = input_text.value.strip() if input_text.value else ""
        if not content and state["uploaded_text"]:
            content = state["uploaded_text"]

        if not content:
            ui.notify("Upload a text file or paste content before processing.", color="warning")
            return

        process_button.disable()
        process_button.props("loading")

        client = DataSanitizerAPIClient(base_url=api_base_url.value)
        try:
            result = await client.process_text(content, file_name=state["file_name"])
        except APIClientError as exc:
            ui.notify(str(exc), color="negative", multi_line=True)
        else:
            _save_history(result, state["file_name"], api_base_url.value)
            quick_snapshot.refresh()
            ui.notify("Sanitization complete. Open Results for full report.", color="positive")
        finally:
            process_button.enable()
            process_button.props(remove="loading")

    def clear_form() -> None:
        state["uploaded_text"] = ""
        state["file_name"] = "uploaded.txt"
        file_chip.set_text("No file uploaded")
        input_text.value = ""
        ui.notify("Input cleared.", color="primary")

    async def handle_upload(event: events.UploadEventArguments) -> None:
        text = ""
        name = "uploaded.txt"

        if hasattr(event, "file") and event.file is not None:
            uploaded_file = event.file
            name = getattr(uploaded_file, "name", None) or name
            try:
                text = await uploaded_file.text("utf-8")
            except UnicodeDecodeError:
                ui.notify("Only UTF-8 text files are supported right now.", color="negative")
                return
        elif hasattr(event, "content"):
            # Legacy NiceGUI fallback.
            data = event.content.read()
            name = getattr(event, "name", None) or name
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                ui.notify("Only UTF-8 text files are supported right now.", color="negative")
                return
        else:
            ui.notify("Upload event format is not supported by this NiceGUI version.", color="negative")
            return

        state["uploaded_text"] = text
        state["file_name"] = name
        input_text.value = text
        file_chip.set_text(f"Loaded: {state['file_name']} ({len(text)} chars)")
        ui.notify("File uploaded and loaded into editor.", color="positive")

    with ui.column().classes("shell gap-4"):
        with ui.column().classes("panel p-5 gap-3 fade-up"):
            ui.label("Sanitize Document").classes("text-3xl font-bold")
            ui.label(
                "Upload a text file or paste content, then send it to your API Gateway/Lambda backend for PII detection and masking."
            ).classes("text-base text-slate-700")

            with ui.row().classes("w-full gap-3 items-end"):
                api_base_url = (
                    ui.input(
                        "Backend API Base URL",
                        value=os.getenv("SANITIZER_API_BASE_URL", "http://localhost:3000"),
                    )
                    .props("outlined")
                    .classes("w-full")
                )

            with ui.row().classes("w-full gap-3 items-center"):
                ui.upload(
                    label="Upload UTF-8 .txt",
                    auto_upload=True,
                    on_upload=handle_upload,
                ).props('accept=".txt,text/plain"')
                file_chip = ui.badge("No file uploaded", color="grey-3").classes("text-slate-700")

            input_text = (
                ui.textarea("Document Text")
                .props("outlined autogrow")
                .classes("w-full")
                .style("min-height: 250px;")
            )

            with ui.row().classes("gap-2"):
                process_button = ui.button("Analyze and Sanitize", on_click=process_content, color="teal-8").props(
                    "unelevated"
                )
                ui.button("Clear", on_click=clear_form, color="grey-7").props("flat")
                ui.button("Open Results", on_click=lambda: ui.navigate.to("/results"), color="amber-8").props(
                    "outline"
                )

        quick_snapshot()


@ui.page("/results")
def results_page() -> None:
    ui.add_head_html(THEME_CSS)
    _top_nav("results")

    history = _get_history()
    selected = {"index": 0}

    @ui.refreshable
    def render_details() -> None:
        entries = _get_history()
        if not entries:
            with ui.column().classes("panel p-5 w-full fade-up"):
                ui.label("No results available yet.").classes("text-lg font-semibold")
                ui.label("Process a file on the Analyze page first.").classes("text-sm text-slate-600")
            return

        idx = selected["index"]
        if idx >= len(entries):
            idx = 0

        chosen = entries[idx]
        result = chosen.get("result", {})
        detections = result.get("detections", []) if isinstance(result.get("detections"), list) else []
        report = result.get("report", {}) if isinstance(result.get("report"), dict) else {}
        sanitized_text = result.get("sanitized_text", "")
        risk = _risk_level(result)

        with ui.column().classes("panel p-5 gap-3 fade-up"):
            with ui.row().classes("w-full items-center justify-between"):
                ui.label("Scan Details").classes("text-2xl font-bold")
                ui.badge(risk.upper(), color="transparent").classes(f"px-3 py-1 {_risk_class(risk)}")

            ui.label(f"Saved at: {chosen.get('saved_at', 'unknown')}  |  Source: {chosen.get('source_file', 'unknown')}").classes(
                "text-sm text-slate-700 mono"
            )

            with ui.row().classes("gap-2"):
                ui.badge(f"Total findings: {report.get('total_findings', len(detections))}", color="teal-2")
                ui.badge(f"Request ID: {result.get('request_id', 'unknown')}", color="amber-2")

            if detections:
                rows = []
                for i, item in enumerate(detections, start=1):
                    rows.append(
                        {
                            "id": i,
                            "type": item.get("type", "unknown"),
                            "start": item.get("start", "-"),
                            "end": item.get("end", "-"),
                        }
                    )
                ui.table(
                    columns=[
                        {"name": "id", "label": "#", "field": "id", "align": "left"},
                        {"name": "type", "label": "Type", "field": "type", "align": "left"},
                        {"name": "start", "label": "Start", "field": "start", "align": "left"},
                        {"name": "end", "label": "End", "field": "end", "align": "left"},
                    ],
                    rows=rows,
                    row_key="id",
                    pagination=10,
                ).classes("w-full")
            else:
                ui.label("No explicit detection coordinates were returned by the backend.").classes("text-sm text-slate-600")

            with ui.expansion("Findings by type", value=True).classes("w-full"):
                for line in _format_counts(report):
                    ui.label(line).classes("text-sm text-slate-700 mono")

            ui.label("Sanitized Output").classes("text-lg font-semibold")
            ui.textarea(value=sanitized_text).props("readonly outlined autogrow").classes("w-full").style(
                "min-height: 220px;"
            )

            ui.label("Raw Report JSON").classes("text-lg font-semibold")
            ui.code(json.dumps(report, indent=2), language="json").classes("w-full")

    with ui.column().classes("shell gap-4"):
        with ui.column().classes("panel p-5 gap-3 fade-up"):
            ui.label("Result History").classes("text-2xl font-bold")
            if history:
                options = {
                    i: (
                        f"{entry.get('saved_at', 'unknown')} | "
                        f"{entry.get('source_file', 'unknown')} | "
                        f"{_risk_level(entry.get('result', {})).upper()}"
                    )
                    for i, entry in enumerate(history)
                }

                def on_change(value: Any) -> None:
                    selected["index"] = int(value)
                    render_details.refresh()

                ui.select(options=options, value=0, on_change=lambda e: on_change(e.value)).props("outlined").classes(
                    "w-full"
                )
            else:
                ui.label("No scans have been stored in this browser session yet.").classes("text-sm text-slate-600")

        render_details()


ui.run(
    title=APP_TITLE,
    reload=False,
    port=int(os.getenv("PORT", "8080")),
    storage_secret=os.getenv("NICEGUI_STORAGE_SECRET", "data-sanitizer-dev-secret"),
)