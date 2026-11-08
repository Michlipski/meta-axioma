"""Tier 1 Presentation Micro-Auditor & Ergonomics Invariant Sentry (`[L1-G4B-015]`).

Enforces:
- HERM-UI-001: DOM Query Bijectivity (JavaScript DOM queries mapped bijectively to HTML id attributes).
- HERM-UI-002: Responsive Viewport & Anti-Fixed-Pixel Canvas Layout.
- HERM-UI-003: Statechart-to-DOM Bisimulation (Formal state machine events mapped to UI triggers).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid

from .domain_models import (
    AuditSeverity,
    DOMBijectivityViolation,
    ResponsiveCanvasViolation,
    StatechartDOMBisimulationViolation,
)


@dataclass(frozen=True)
class DOMQueryWitness:
    """Witness record for a single DOM query found in client scripts."""
    query_type: str
    target_selector: str
    source_file: str
    line_number: int
    is_bijective: bool
    is_dynamically_created: bool = False
    is_whitelisted: bool = False
    remediation_note: str = ""


@dataclass(frozen=True)
class CanvasResponsivenessWitness:
    """Witness record for a visual canvas / SVG element layout inspection."""
    tag: str
    element_id: str
    declared_width: Optional[str]
    declared_height: Optional[str]
    has_viewbox: bool
    is_responsive_in_css: bool
    css_rules_detected: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class StatechartBisimulationWitness:
    """Witness record proving bisimulation between StatechartIR and DOM triggers."""
    event_name: str
    event_category: str
    matching_dom_trigger: Optional[str]
    trigger_type: Optional[str]
    is_bisimilar: bool


@dataclass
class PresentationAuditReport:
    """Formal verification report produced by Tier 1 Presentation Micro-Auditor."""
    report_id: str
    app_id: str
    is_certified: bool
    herm_ui_001_bijectivity_pass: bool
    herm_ui_002_responsiveness_pass: bool
    herm_ui_003_bisimulation_pass: bool
    total_static_ids_in_html: int
    total_queries_in_js: int
    unmapped_dom_queries: List[str] = field(default_factory=list)
    canvas_violations: List[str] = field(default_factory=list)
    bisimulation_violations: List[str] = field(default_factory=list)
    dom_witnesses: List[DOMQueryWitness] = field(default_factory=list)
    canvas_witnesses: List[CanvasResponsivenessWitness] = field(default_factory=list)
    bisimulation_witnesses: List[StatechartBisimulationWitness] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "app_id": self.app_id,
            "is_certified": self.is_certified,
            "herm_ui_001_bijectivity_pass": self.herm_ui_001_bijectivity_pass,
            "herm_ui_002_responsiveness_pass": self.herm_ui_002_responsiveness_pass,
            "herm_ui_003_bisimulation_pass": self.herm_ui_003_bisimulation_pass,
            "total_static_ids_in_html": self.total_static_ids_in_html,
            "total_queries_in_js": self.total_queries_in_js,
            "unmapped_dom_queries": self.unmapped_dom_queries,
            "canvas_violations": self.canvas_violations,
            "bisimulation_violations": self.bisimulation_violations,
        }


class _HTMLStaticDOMParser(HTMLParser):
    """Pure standard-library parser extracting declared static DOM topology and assets."""

    def __init__(self) -> None:
        super().__init__()
        self.declared_ids: Set[str] = set()
        self.declared_classes: Set[str] = set()
        self.declared_data_actions: Set[str] = set()
        self.declared_data_events: Set[str] = set()
        self.has_viewport_meta: bool = False
        self.viewport_content: str = ""
        self.script_sources: List[str] = []
        self.stylesheet_hrefs: List[str] = []
        self.canvas_nodes: List[Dict[str, str]] = []
        self.svg_nodes: List[Dict[str, str]] = []
        self.button_ids: Set[str] = set()

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        attr_dict: Dict[str, str] = {k.lower(): v or "" for k, v in attrs}

        element_id = attr_dict.get("id")
        if element_id:
            self.declared_ids.add(element_id)
            if tag == "button" or "btn" in element_id:
                self.button_ids.add(element_id)

        element_class = attr_dict.get("class")
        if element_class:
            for cls in element_class.split():
                self.declared_classes.add(cls)

        if "data-action" in attr_dict:
            self.declared_data_actions.add(attr_dict["data-action"])

        if "data-event" in attr_dict:
            self.declared_data_events.add(attr_dict["data-event"])

        if tag == "meta" and attr_dict.get("name") == "viewport":
            self.has_viewport_meta = True
            self.viewport_content = attr_dict.get("content", "")

        if tag == "script" and "src" in attr_dict:
            self.script_sources.append(attr_dict["src"])

        if tag == "link" and attr_dict.get("rel") == "stylesheet" and "href" in attr_dict:
            self.stylesheet_hrefs.append(attr_dict["href"])

        if tag == "canvas":
            self.canvas_nodes.append(attr_dict)

        if tag == "svg":
            self.svg_nodes.append(attr_dict)


class PresentationMicroAuditor:
    """Tier 1 Static Syntactic Micro-Auditor enforcing [L1-G4B-015]."""

    # Regular expressions for JavaScript DOM queries
    REGEX_GET_ELEMENT_BY_ID = re.compile(
        r'(?:document\s*\.\s*getElementById|\$\s*)\(\s*["\']([^"\'`\$\n]+)["\']\s*\)'
    )
    REGEX_QUERY_SELECTOR_ID = re.compile(
        r'(?:\.\s*querySelector(?:All)?)\(\s*["\']#([a-zA-Z0-9_\-]+)["\']\s*\)'
    )
    REGEX_DYNAMIC_SET_ATTRIBUTE_ID = re.compile(
        r'\.setAttribute\(\s*["\']id["\']\s*,\s*["\']([^"\'`\$\n]+)["\']\s*\)'
    )
    REGEX_DYNAMIC_ID_ASSIGNMENT = re.compile(
        r'\.id\s*=\s*["\']([^"\'`\$\n]+)["\']'
    )
    REGEX_DYNAMIC_TEMPLATE_ID = re.compile(
        r'id=["\']([a-zA-Z0-9_\-]+)\$\{'
    )

    # Standard whitelisted dynamic prefix patterns
    DEFAULT_DYNAMIC_PREFIXES = (
        "node-", "edge-", "card-", "tab-", "btn-", "ghost-", "val-",
        "bar-", "insp-", "chip-", "layer", "cell-", "status-", "item-", "metric-"
    )

    # Autonomous transitions that do not require human interactive DOM triggers
    DEFAULT_AUTONOMOUS_EVENTS = {
        "BOOT", "INITIALIZED_OK", "SOLVER_SAT", "SOLVER_UNSAT", "TOKEN_MOVED",
        "SHADOWS_PROJECTED", "COLLISIONS_EVALUATED", "TICK", "TIMER_EXPIRED",
        "SYNC_COMPLETE", "STREAM_CLOSED", "PEER_CONNECTED", "METRIC_UPDATED"
    }

    def __init__(
        self,
        dynamic_prefixes: Optional[Tuple[str, ...]] = None,
        autonomous_events: Optional[Set[str]] = None,
    ) -> None:
        self.dynamic_prefixes = dynamic_prefixes or self.DEFAULT_DYNAMIC_PREFIXES
        self.autonomous_events = autonomous_events or self.DEFAULT_AUTONOMOUS_EVENTS

    def parse_html(self, html_content: str) -> _HTMLStaticDOMParser:
        """Parses HTML document into static DOM model."""
        parser = _HTMLStaticDOMParser()
        parser.feed(html_content)
        return parser

    def extract_js_dom_queries(self, js_content: str) -> Tuple[Set[str], Set[str]]:
        """Extracts queried DOM IDs and dynamically registered IDs from JavaScript."""
        queried_ids: Set[str] = set()
        dynamically_created_ids: Set[str] = set()

        for match in self.REGEX_GET_ELEMENT_BY_ID.finditer(js_content):
            queried_ids.add(match.group(1))

        for match in self.REGEX_QUERY_SELECTOR_ID.finditer(js_content):
            queried_ids.add(match.group(1))

        for match in self.REGEX_DYNAMIC_SET_ATTRIBUTE_ID.finditer(js_content):
            dynamically_created_ids.add(match.group(1))

        for match in self.REGEX_DYNAMIC_ID_ASSIGNMENT.finditer(js_content):
            dynamically_created_ids.add(match.group(1))

        for match in self.REGEX_DYNAMIC_TEMPLATE_ID.finditer(js_content):
            dynamically_created_ids.add(match.group(1))

        return queried_ids, dynamically_created_ids

    def audit_dom_bijectivity(
        self,
        declared_ids: Set[str],
        queried_ids: Set[str],
        dynamically_created_ids: Set[str],
    ) -> Tuple[bool, List[str], List[DOMQueryWitness]]:
        """Enforces HERM-UI-001 (DOM Query Bijectivity)."""
        unmapped: List[str] = []
        witnesses: List[DOMQueryWitness] = []

        for q_id in sorted(queried_ids):
            # Check 1: Declared in static HTML
            if q_id in declared_ids:
                witnesses.append(
                    DOMQueryWitness(
                        query_type="static_id",
                        target_selector=q_id,
                        source_file="app.js",
                        line_number=0,
                        is_bijective=True,
                    )
                )
                continue

            # Check 2: Dynamically created in JavaScript
            if q_id in dynamically_created_ids:
                witnesses.append(
                    DOMQueryWitness(
                        query_type="dynamic_created",
                        target_selector=q_id,
                        source_file="app.js",
                        line_number=0,
                        is_bijective=True,
                        is_dynamically_created=True,
                    )
                )
                continue

            # Check 3: Matches a recognized dynamic prefix
            if any(q_id.startswith(pfx) for pfx in self.dynamic_prefixes):
                witnesses.append(
                    DOMQueryWitness(
                        query_type="whitelisted_prefix",
                        target_selector=q_id,
                        source_file="app.js",
                        line_number=0,
                        is_bijective=True,
                        is_whitelisted=True,
                    )
                )
                continue

            # Unmapped ID violation
            unmapped.append(q_id)
            witnesses.append(
                DOMQueryWitness(
                    query_type="unmapped_query",
                    target_selector=q_id,
                    source_file="app.js",
                    line_number=0,
                    is_bijective=False,
                    remediation_note=f"Element ID '{q_id}' queried in JS but absent from HTML.",
                )
            )

        is_pass = (len(unmapped) == 0)
        return is_pass, unmapped, witnesses

    def audit_responsive_canvas_viewport(
        self,
        has_viewport_meta: bool,
        canvas_nodes: List[Dict[str, str]],
        svg_nodes: List[Dict[str, str]],
        css_content: str,
    ) -> Tuple[bool, List[str], List[CanvasResponsivenessWitness]]:
        """Enforces HERM-UI-002 (Responsive Viewport & Anti-Fixed-Pixel Canvas)."""
        violations: List[str] = []
        witnesses: List[CanvasResponsivenessWitness] = []

        if not has_viewport_meta:
            violations.append("Missing <meta name='viewport' content='width=device-width, initial-scale=1.0'> in HTML.")

        # Check responsive CSS indicators
        css_cleaned = re.sub(r"/\*.*?\*/", "", css_content, flags=re.DOTALL)
        css_lower = css_cleaned.lower()
        has_css_vars = ":root" in css_cleaned or "--" in css_cleaned
        has_fluid_layout = (
            "display: flex" in css_lower
            or "display:flex" in css_lower
            or "display: grid" in css_lower
            or "display:grid" in css_lower
        )
        has_responsive_canvas_css = (
            "max-width: 100%" in css_lower
            or "max-width:100%" in css_lower
            or "width: 100%" in css_lower
            or "width:100%" in css_lower
            or "aspect-ratio" in css_lower
            or "flex: 1" in css_lower
            or "flex:1" in css_lower
        )

        detected_css_rules = []
        if has_css_vars:
            detected_css_rules.append("css_variables")
        if has_fluid_layout:
            detected_css_rules.append("fluid_flex_or_grid")
        if has_responsive_canvas_css:
            detected_css_rules.append("responsive_canvas_rules")

        if not (has_css_vars or has_fluid_layout or has_responsive_canvas_css):
            violations.append("Stylesheet lacks modern responsive declarations (CSS variables, flexbox, or grid).")

        # Inspect <canvas> elements
        for node in canvas_nodes:
            cid = node.get("id", "canvas")
            width_attr = node.get("width")
            height_attr = node.get("height")

            # Inline fixed dimensions without responsive CSS
            is_fixed_pixel = False
            if width_attr and height_attr:
                try:
                    w_val = int(width_attr)
                    h_val = int(height_attr)
                    if w_val >= 200 and h_val >= 150:
                        is_fixed_pixel = True
                except ValueError:
                    pass

            is_responsive = has_responsive_canvas_css or (f"#{cid}" in css_lower and ("width:" in css_lower or "max-width:" in css_lower))

            if is_fixed_pixel and not is_responsive:
                violations.append(
                    f"<canvas id='{cid}'> has fixed dimensions ({width_attr}x{height_attr}) without responsive CSS."
                )

            witnesses.append(
                CanvasResponsivenessWitness(
                    tag="canvas",
                    element_id=cid,
                    declared_width=width_attr,
                    declared_height=height_attr,
                    has_viewbox="viewbox" in node,
                    is_responsive_in_css=is_responsive,
                    css_rules_detected=detected_css_rules,
                )
            )

        # Inspect large workspace <svg> elements (ignoring small icons <= 48px)
        for node in svg_nodes:
            sid = node.get("id", "svg")
            w_str = node.get("width")
            h_str = node.get("height")
            has_viewbox = "viewbox" in node

            is_large = False
            if w_str and h_str:
                try:
                    w = int(w_str)
                    h = int(h_str)
                    if w > 48 and h > 48:
                        is_large = True
                except ValueError:
                    pass

            if is_large and not has_viewbox and not has_responsive_canvas_css:
                violations.append(
                    f"<svg id='{sid}'> has fixed dimensions ({w_str}x{h_str}) without viewBox or responsive CSS."
                )

            witnesses.append(
                CanvasResponsivenessWitness(
                    tag="svg",
                    element_id=sid,
                    declared_width=w_str,
                    declared_height=h_str,
                    has_viewbox=has_viewbox,
                    is_responsive_in_css=has_responsive_canvas_css,
                    css_rules_detected=detected_css_rules,
                )
            )

        is_pass = (len(violations) == 0)
        return is_pass, violations, witnesses

    def audit_statechart_dom_bisimulation(
        self,
        statechart_events: List[str],
        declared_actions: Set[str],
        declared_events: Set[str],
        declared_ids: Set[str],
        js_content: str,
    ) -> Tuple[bool, List[str], List[StatechartBisimulationWitness]]:
        """Enforces HERM-UI-003 (Statechart-to-DOM Bisimulation)."""
        violations: List[str] = []
        witnesses: List[StatechartBisimulationWitness] = []

        js_lower = js_content.lower()

        for event in statechart_events:
            event_upper = event.upper()

            # Filter out autonomous system-internal transitions
            if event_upper in self.autonomous_events:
                witnesses.append(
                    StatechartBisimulationWitness(
                        event_name=event,
                        event_category="AUTONOMOUS_REACTIVE",
                        matching_dom_trigger=None,
                        trigger_type="autonomous_internal",
                        is_bisimilar=True,
                    )
                )
                continue

            event_norm = event.lower().replace("_", "-")
            event_raw = event.lower()

            # Check 1: data-action or data-event attribute
            matched_trigger = None
            trigger_type = None

            if event in declared_actions or event_raw in declared_actions:
                matched_trigger = f"data-action='{event}'"
                trigger_type = "data-action"
            elif event in declared_events or event_raw in declared_events:
                matched_trigger = f"data-event='{event}'"
                trigger_type = "data-event"
            elif any(event_norm in d_id.lower() or event_raw in d_id.lower() for d_id in declared_ids):
                # Matching button or element ID (e.g. btn-undo for EV_UNDO)
                matching_id = next(d_id for d_id in declared_ids if event_norm in d_id.lower() or event_raw in d_id.lower())
                matched_trigger = f"id='{matching_id}'"
                trigger_type = "id_match"
            elif event.lower() in js_lower or event_raw in js_lower:
                # Direct JS dispatch or handler binding
                matched_trigger = f"js_dispatch('{event}')"
                trigger_type = "js_dispatch"

            if matched_trigger:
                witnesses.append(
                    StatechartBisimulationWitness(
                        event_name=event,
                        event_category="HUMAN_INTERACTIVE",
                        matching_dom_trigger=matched_trigger,
                        trigger_type=trigger_type,
                        is_bisimilar=True,
                    )
                )
            else:
                violations.append(
                    f"Interactive Statechart event '{event}' has no corresponding DOM trigger (data-action, button ID, or JS dispatch)."
                )
                witnesses.append(
                    StatechartBisimulationWitness(
                        event_name=event,
                        event_category="HUMAN_INTERACTIVE",
                        matching_dom_trigger=None,
                        trigger_type=None,
                        is_bisimilar=False,
                    )
                )

        is_pass = (len(violations) == 0)
        return is_pass, violations, witnesses

    def audit_static_bundle(
        self,
        html_content: str,
        js_content: str,
        css_content: str,
        statechart_events: Optional[List[str]] = None,
        app_id: str = "app",
        allow_raise: bool = True,
    ) -> PresentationAuditReport:
        """Audits an entire static web bundle against HERM-UI-001..003."""
        report_id = f"rpt_ui_{uuid.uuid4().hex[:12]}"

        # 1. Parse HTML
        parsed_html = self.parse_html(html_content)

        # 2. Extract JS DOM queries
        queried_ids, dynamically_created_ids = self.extract_js_dom_queries(js_content)

        # 3. Rule 1: DOM Bijectivity
        bio_pass, unmapped, dom_witnesses = self.audit_dom_bijectivity(
            declared_ids=parsed_html.declared_ids,
            queried_ids=queried_ids,
            dynamically_created_ids=dynamically_created_ids,
        )

        # 4. Rule 2: Responsive Viewport & Canvas
        resp_pass, canvas_viols, canvas_witnesses = self.audit_responsive_canvas_viewport(
            has_viewport_meta=parsed_html.has_viewport_meta,
            canvas_nodes=parsed_html.canvas_nodes,
            svg_nodes=parsed_html.svg_nodes,
            css_content=css_content,
        )

        # 5. Rule 3: Statechart-DOM Bisimulation
        bisim_pass = True
        bisim_viols: List[str] = []
        bisim_witnesses: List[StatechartBisimulationWitness] = []
        if statechart_events:
            bisim_pass, bisim_viols, bisim_witnesses = self.audit_statechart_dom_bisimulation(
                statechart_events=statechart_events,
                declared_actions=parsed_html.declared_data_actions,
                declared_events=parsed_html.declared_data_events,
                declared_ids=parsed_html.declared_ids,
                js_content=js_content,
            )

        is_certified = bio_pass and resp_pass and bisim_pass

        report = PresentationAuditReport(
            report_id=report_id,
            app_id=app_id,
            is_certified=is_certified,
            herm_ui_001_bijectivity_pass=bio_pass,
            herm_ui_002_responsiveness_pass=resp_pass,
            herm_ui_003_bisimulation_pass=bisim_pass,
            total_static_ids_in_html=len(parsed_html.declared_ids),
            total_queries_in_js=len(queried_ids),
            unmapped_dom_queries=unmapped,
            canvas_violations=canvas_viols,
            bisimulation_violations=bisim_viols,
            dom_witnesses=dom_witnesses,
            canvas_witnesses=canvas_witnesses,
            bisimulation_witnesses=bisim_witnesses,
        )

        if allow_raise and not is_certified:
            if not bio_pass:
                raise DOMBijectivityViolation(
                    f"HERM-UI-001 Violation: Unmapped DOM IDs queried in JS: {', '.join(unmapped)}"
                )
            if not resp_pass:
                raise ResponsiveCanvasViolation(
                    f"HERM-UI-002 Violation: Responsive canvas/viewport failure: {'; '.join(canvas_viols)}"
                )
            if not bisim_pass:
                raise StatechartDOMBisimulationViolation(
                    f"HERM-UI-003 Violation: Statechart-to-DOM bisimulation drift: {'; '.join(bisim_viols)}"
                )

        return report

    def audit_app_directory(
        self,
        app_dir: str | Path,
        statechart_events: Optional[List[str]] = None,
        allow_raise: bool = True,
    ) -> PresentationAuditReport:
        """Inspects an application directory (e.g. apps/<app_name>) and audits its static presentation assets."""
        path = Path(app_dir).resolve()
        static_dir = path / "static" if (path / "static").exists() else path

        # Find HTML file
        html_file = static_dir / "index.html"
        if not html_file.exists():
            html_file = path / "index.html"

        # Find JS file
        js_files = list(static_dir.glob("*.js"))
        if not js_files:
            js_files = list(path.glob("*.js"))

        # Find CSS file
        css_files = list(static_dir.glob("*.css"))
        if not css_files:
            css_files = list(path.glob("*.css"))

        html_content = html_file.read_text(encoding="utf-8") if html_file.exists() else ""
        js_content = "\n".join(f.read_text(encoding="utf-8") for f in js_files) if js_files else ""
        css_content = "\n".join(f.read_text(encoding="utf-8") for f in css_files) if css_files else ""

        return self.audit_static_bundle(
            html_content=html_content,
            js_content=js_content,
            css_content=css_content,
            statechart_events=statechart_events,
            app_id=path.name,
            allow_raise=allow_raise,
        )
