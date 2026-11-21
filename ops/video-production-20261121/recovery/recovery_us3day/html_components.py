"""Render the original number, kinetic, and panel snippets in Chrome.

The snippet files are not rewritten. A host page supplies the shot variables,
runs the snippet script, and seeks the timeline that ships with that snippet.
number-pop-in and panel-reveal keep their motion in a timeline comment; the
host executes that comment with the same GSAP build. It does not draw ASS.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import socket
import subprocess
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .project import ROOT

CAPTURE = Path(__file__).with_name("capture_html_frames.mjs")
STAGE_W = 1080
STAGE_H = 1128
WELL_H = 280


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _library(project: dict) -> Path:
    roots = project.get("library_roots") or {}
    raw = roots.get("hf_components") or "inputs/components"
    path = Path(raw)
    if not path.is_absolute():
        cwd = Path.cwd() / path
        if cwd.exists():
            return cwd
        rooted = ROOT / path
        if rooted.exists():
            return rooted
    return path


def _snippet(library: Path, name: str) -> Path:
    return library / "hf_components" / name / f"{name}.html"


def _split_snippet(html: str) -> tuple[str, str, str]:
    """Return markup, style, and script from a pasted snippet. The text is unchanged."""
    style = ""
    script = ""
    if "<style>" in html and "</style>" in html:
        style = html.split("<style>", 1)[1].split("</style>", 1)[0]
    if "<script>" in html and "</script>" in html:
        script = html.split("<script>", 1)[1].split("</script>", 1)[0]
    markup = html
    if "<style>" in markup:
        markup = markup.split("<style>", 1)[0]
    markup = markup.strip()
    return markup, style, script


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return


def _serve(directory: Path) -> tuple[ThreadingHTTPServer, int]:
    handler = lambda *args, **kwargs: _QuietHandler(*args, directory=str(directory), **kwargs)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, server.server_address[1]


def _capture(url: str, out_dir: Path, frames: int, timeline: str) -> str:
    port = _free_port()
    proc = subprocess.run(
        [
            "node",
            str(CAPTURE),
            url,
            str(out_dir),
            str(frames),
            "30",
            timeline,
            str(port),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=180,
    )
    if proc.returncode != 0 or not (out_dir / "f0000.png").is_file():
        raise RuntimeError((proc.stderr or proc.stdout).decode("utf-8", "replace")[-1200:])
    version_file = out_dir / "chrome-version.txt"
    return version_file.read_text(encoding="utf-8").strip() if version_file.is_file() else ""


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _font_face(family: str, href: str, weight: str) -> str:
    return (
        "@font-face { font-family: '%s'; src: url('%s'); font-weight: %s; font-style: normal; font-display: block; }"
        % (family, href, weight)
    )


def _host_css(anchor: str) -> str:
    if anchor == "center":
        slot = "#slot { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; }"
    else:
        slot = (
            "#slot, #stage { position:absolute; left:0; width:%dpx; height:%dpx; bottom:0; }"
            % (STAGE_W, WELL_H)
        )
        slot += "#slot { display:flex; align-items:center; justify-content:center; }"
    return """
html, body { margin:0; width:%(w)dpx; height:%(h)dpx; overflow:hidden; background:transparent; }
%(slot)s
.hf-transition-number-pop-in, .hf-transition-number-pop-in span, .hf-transition-number-pop-in small,
.hf-transition-panel-reveal, .hf-transition-panel-reveal header {
  font-family: Inter, "Noto Sans CJK SC", sans-serif;
}
.hf-transition-panel-reveal header { font-size: 28px; line-height: 1.35; }
#root { --font-display: Geist, "Noto Sans CJK SC", sans-serif; }
""" % {"w": STAGE_W, "h": STAGE_H, "slot": slot}


def _page(body: str, fonts: str) -> str:
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<style>%s%s</style></head><body>%s</body></html>" % (fonts, "", body)
    )


def _number_page(snippet: str, variables: dict, fonts: str, anchor: str) -> str:
    markup, style, script = _split_snippet(snippet)
    payload = json.dumps(
        {
            "value": str(variables.get("value") if variables.get("value") is not None else ""),
            "unit": str(variables.get("unit") if variables.get("unit") is not None else ""),
            "lift": variables.get("lift") or "standard",
            "tone": variables.get("tone") or "paper",
        },
        ensure_ascii=False,
    )
    # The fromTo below is the timeline comment in number-pop-in.html, not a new motion.
    timeline = """
<script src="gsap-3.14.2.min.js"></script>
<script>
var tl = gsap.timeline({ paused: true });
tl.fromTo('.hf-transition-number-pop-in span, .hf-transition-number-pop-in small',
  { opacity: 0, '--hf-number-y': '24px', '--hf-number-scale': 0.82, '--hf-number-blur': '8px' },
  { opacity: 1, '--hf-number-y': '0px', '--hf-number-scale': 1, '--hf-number-blur': '0px', duration: 0.34, stagger: 0.055, ease: 'back.out(1.8)' },
  0);
window.__timelines = { "number-pop-in": tl };
window.__hfReady = true;
</script>
"""
    body = (
        "<script>window.__hyperframes={getVariables:function(){return %s;}};</script>"
        "<div id='slot'>%s</div><style>%s%s</style><script>%s</script>%s"
        % (payload, markup, style, _host_css(anchor), script, timeline)
    )
    return _page(body, fonts)


def _panel_page(snippet: str, variables: dict, fonts: str, anchor: str) -> str:
    markup, style, script = _split_snippet(snippet)
    payload = json.dumps(
        {
            "title": str(variables.get("title") or ""),
            "width": variables.get("width") or "wide",
            "tone": variables.get("tone") or "ink",
            "reveal": variables.get("reveal") or "fade",
        },
        ensure_ascii=False,
    )
    # Demo body lines stay in the snippet markup. The host removes them after the
    # real script sets the title, so "Duration 420ms" is not burned into the film.
    timeline = """
<script src="gsap-3.14.2.min.js"></script>
<script>
document.querySelectorAll(".hf-transition-panel-reveal p").forEach(function (node) { node.remove(); });
var tl = gsap.timeline({ paused: true });
tl.fromTo('.hf-transition-panel-reveal',
  { '--hf-panel-open': 0 },
  { '--hf-panel-open': 1, duration: 0.44, ease: 'power3.inOut' },
  0);
window.__timelines = { "panel-reveal": tl };
window.__hfReady = true;
</script>
"""
    body = (
        "<script>window.__hyperframes={getVariables:function(){return %s;}};</script>"
        "<div id='slot'>%s</div><style>%s%s</style><script>%s</script>%s"
        % (payload, markup, style, _host_css(anchor), script, timeline)
    )
    return _page(body, fonts)


def _kinetic_page(snippet_path: Path, variables: dict, fonts: str) -> tuple[str, list[str]]:
    raw = snippet_path.read_text(encoding="utf-8")
    template = raw.split("<template>", 1)[1].split("</template>", 1)[0]
    notes = [
        "original kinetic-center-build.html bytes are unchanged",
        "host drops the Google Fonts stylesheet link and points the two script src values at local GSAP 3.14.2 and the fetched CustomEase 3.14.2",
        "host sets #root --color from the declared color variable; the snippet CSS already reads var(--color) and the inline script does not assign it",
        "host measureFont adds Noto Sans CJK SC because the snippet measures with a latin stack and the supplied Geist/Inter files have no CJK",
    ]
    template = template.replace(
        '<link\n        rel="stylesheet"\n        href="https://fonts.googleapis.com/css2?family=Geist:wght@500;600;700;800&amp;display=block"\n      />',
        "",
    )
    template = template.replace(
        'src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"',
        'src="gsap-3.14.2.min.js"',
    )
    template = template.replace(
        'src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/CustomEase.min.js"',
        'src="CustomEase-3.14.2.min.js"',
    )
    template = template.replace(
        "var measureFont = '-apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, sans-serif';",
        'var measureFont = \'"Noto Sans CJK SC", Geist, sans-serif\';',
    )
    color = str(variables.get("color") or "#FFFFFF")
    payload = json.dumps(
        {
            "text": str(variables.get("text") or ""),
            "font_size": variables.get("font_size") or 72,
            "entry_offset": variables.get("entry_offset") or 48,
            "color": color,
            "font_weight": str(variables.get("font_weight") or "700"),
        },
        ensure_ascii=False,
    )
    body = (
        "<script>window.__hyperframes={getVariables:function(){return %s;}};</script>"
        "<div id='stage' style='--color:%s'>%s</div>"
        "<style>%s #root{--color:%s}</style>"
        "<script>window.__hfReady=!!(window.__timelines&&window.__timelines['kinetic-center-build']);</script>"
        % (payload, color, template, _host_css("well"), color)
    )
    return _page(body, fonts), notes


def _fonts_css() -> str:
    return "\n".join(
        [
            _font_face("Inter", "Inter-latin-700-normal.woff2", "700"),
            _font_face("Inter", "Inter-latin-400-normal.woff2", "400"),
            _font_face("Geist", "Geist-Bold.ttf", "700"),
            _font_face("Geist", "Geist-SemiBold.ttf", "600"),
            _font_face("Geist", "Geist-Regular.ttf", "500"),
            _font_face("Noto Sans CJK SC", "NotoSansCJK-Bold.ttc", "700"),
        ]
    )


def _link_assets(directory: Path, library: Path) -> None:
    vendor = library / "vendor"
    mapping = {
        "gsap-3.14.2.min.js": vendor / "gsap" / "gsap-3.14.2.min.js",
        "CustomEase-3.14.2.min.js": vendor / "gsap" / "CustomEase-3.14.2.min.js",
        "Inter-latin-700-normal.woff2": vendor / "fonts" / "Inter-latin-700-normal.woff2",
        "Inter-latin-400-normal.woff2": vendor / "fonts" / "Inter-latin-400-normal.woff2",
        "Geist-Bold.ttf": vendor / "fonts" / "Geist-Bold.ttf",
        "Geist-SemiBold.ttf": vendor / "fonts" / "Geist-SemiBold.ttf",
        "Geist-Regular.ttf": vendor / "fonts" / "Geist-Regular.ttf",
        "NotoSansCJK-Bold.ttc": Path("/workspace/ops/video-production-20261121/recovery/inputs/fonts/NotoSansCJK-Bold.ttc"),
    }
    for name, source in mapping.items():
        target = directory / name
        if target.exists():
            target.unlink()
        target.symlink_to(source)


def render_html_component(project: dict, shot: dict, out_mov: Path, anchor: str = "well") -> dict:
    component = shot.get("component") or {}
    name = str(component.get("id") or "").split(":")[-1]
    library = _library(project)
    snippet_path = _snippet(library, name)
    if not snippet_path.is_file():
        raise FileNotFoundError(snippet_path)
    variables = component.get("variables") or {}
    duration = float(shot["t1"]) - float(shot["t0"])
    capture_seconds = {"number-pop-in": 1.0, "panel-reveal": 1.0, "kinetic-center-build": 2.0}[name]
    frames = max(2, int(round(capture_seconds * 30)))
    work = out_mov.parent / f"{shot['id']}_{name}_html"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    _link_assets(work, library)
    fonts = _fonts_css()
    adaptations = [
        "transparent host, placed inside the 1080x1128 stage, not in the title or subtitle bands",
        "Noto Sans CJK SC is only the CJK fallback after Inter/Geist; film titles and subtitles stay on the ASS Noto styles",
        "demo.html was not opened and its default copy is not the shot text",
    ]
    snippet = snippet_path.read_text(encoding="utf-8")
    if name == "number-pop-in":
        page = _number_page(snippet, variables, fonts, anchor)
        adaptations.append("timeline is the fromTo comment inside number-pop-in.html, run with gsap 3.14.2")
    elif name == "panel-reveal":
        page = _panel_page(snippet, variables, fonts, anchor)
        adaptations.append("timeline is the fromTo comment inside panel-reveal.html, run with gsap 3.14.2")
        adaptations.append("host removes the snippet's default body lines Duration 420ms and Easing power3.out after the real script sets the title")
    elif name == "kinetic-center-build":
        page, extra = _kinetic_page(snippet_path, variables, fonts)
        adaptations.extend(extra)
    else:
        raise RuntimeError(name)
    (work / "host.html").write_text(page, encoding="utf-8")
    server, port = _serve(work)
    try:
        browser = _capture(f"http://127.0.0.1:{port}/host.html", work, frames, name)
    finally:
        server.shutdown()
    hold = max(0.0, duration - capture_seconds)
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-framerate", "30",
            "-i", str(work / "f%04d.png"),
            "-vf", f"tpad=stop_mode=clone:stop_duration={hold:.3f},format=rgba",
            "-c:v", "qtrle",
            "-t", f"{duration:.3f}",
            str(out_mov),
        ],
        check=True,
    )
    landed = work / f"f{frames - 1:04d}.png"
    evidence_png = out_mov.with_suffix(".landed.png")
    shutil.copyfile(landed, evidence_png)
    for frame in work.glob("f*.png"):
        if frame.name != landed.name:
            frame.unlink()
    return {
        "id": component.get("id"),
        "status": "html_snippet_rendered",
        "not_ass_redraw": True,
        "source_html": str(snippet_path),
        "source_sha256": _sha256(snippet_path),
        "variables": variables,
        "renderer": "google-chrome headless CDP screenshot",
        "browser": browser,
        "capture_frames": frames,
        "capture_seconds": capture_seconds,
        "hold_seconds": round(hold, 3),
        "anchor": anchor,
        "landed_png": str(evidence_png),
        "landed_sha256": _sha256(evidence_png),
        "host_adaptations": adaptations,
        "gsap_sha256": _sha256(library / "vendor" / "gsap" / "gsap-3.14.2.min.js"),
        "customease_sha256": _sha256(library / "vendor" / "gsap" / "CustomEase-3.14.2.min.js") if name == "kinetic-center-build" else "",
        "customease_note": "fetched from https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/CustomEase.min.js; not in the asset library; not handwritten" if name == "kinetic-center-build" else "",
    }
