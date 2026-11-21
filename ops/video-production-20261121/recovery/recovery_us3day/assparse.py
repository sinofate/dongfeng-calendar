"""Parse the master ASS. Comment rows are kept and never treated as cues."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AssStyle:
    name: str
    fontname: str
    fontsize: int
    primary: str
    secondary: str
    outline_color: str
    back: str
    bold: int
    outline: int
    shadow: int
    alignment: int
    margin_l: int
    margin_r: int
    margin_v: int

    def as_extracted(self) -> dict:
        return {
            "layer": "extracted",
            "source": "final_v1.ass Style D",
            "name": self.name,
            "fontname": self.fontname,
            "fontsize": self.fontsize,
            "primary": self.primary,
            "outline_color": self.outline_color,
            "bold": self.bold,
            "outline": self.outline,
            "shadow": self.shadow,
            "alignment": self.alignment,
            "margin_l": self.margin_l,
            "margin_r": self.margin_r,
            "margin_v": self.margin_v,
        }


@dataclass(frozen=True)
class AssEvent:
    kind: str
    start: float
    end: float
    style: str
    text: str

    @property
    def is_dialogue(self) -> bool:
        return self.kind == "dialogue"


@dataclass(frozen=True)
class AssFile:
    play_res_x: int
    play_res_y: int
    style: AssStyle
    events: tuple[AssEvent, ...]

    @property
    def dialogues(self) -> tuple[AssEvent, ...]:
        return tuple(event for event in self.events if event.kind == "dialogue")

    @property
    def comments(self) -> tuple[AssEvent, ...]:
        return tuple(event for event in self.events if event.kind == "comment")


def ass_color_to_hex(value: str) -> str:
    """ASS &HAABBGGRR to #RRGGBB. Alpha is ignored."""
    digits = value.strip().lstrip("&").lstrip("H").lstrip("h")
    if len(digits) != 8:
        raise ValueError(f"unexpected ASS colour {value}")
    blue = digits[2:4]
    green = digits[4:6]
    red = digits[6:8]
    return f"#{red}{green}{blue}".upper()


def parse_ass_time(value: str) -> float:
    hours, minutes, seconds = value.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def format_ass_time(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0
    centiseconds = int(round(seconds * 100))
    hours, centiseconds = divmod(centiseconds, 360000)
    minutes, centiseconds = divmod(centiseconds, 6000)
    whole, centiseconds = divmod(centiseconds, 100)
    return f"{hours}:{minutes:02d}:{whole:02d}.{centiseconds:02d}"


def parse_ass(path: str | Path) -> AssFile:
    play_x = play_y = None
    style: AssStyle | None = None
    events: list[AssEvent] = []
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("PlayResX:"):
            play_x = int(line.split(":", 1)[1].strip())
        elif line.startswith("PlayResY:"):
            play_y = int(line.split(":", 1)[1].strip())
        elif line.startswith("Style:"):
            fields = [part.strip() for part in line.split(":", 1)[1].split(",")]
            style = AssStyle(
                name=fields[0],
                fontname=fields[1],
                fontsize=int(float(fields[2])),
                primary=ass_color_to_hex(fields[3]),
                secondary=ass_color_to_hex(fields[4]),
                outline_color=ass_color_to_hex(fields[5]),
                back=ass_color_to_hex(fields[6]),
                bold=int(fields[7]),
                outline=int(float(fields[16])),
                shadow=int(float(fields[17])),
                alignment=int(fields[18]),
                margin_l=int(fields[19]),
                margin_r=int(fields[20]),
                margin_v=int(fields[21]),
            )
        elif line.startswith("Dialogue:") or line.startswith("Comment:"):
            kind = "dialogue" if line.startswith("Dialogue:") else "comment"
            body = line.split(":", 1)[1].lstrip()
            fields = body.split(",", 9)
            if len(fields) != 10:
                raise ValueError(f"ASS event does not have 10 fields: {line}")
            events.append(
                AssEvent(
                    kind=kind,
                    start=parse_ass_time(fields[1]),
                    end=parse_ass_time(fields[2]),
                    style=fields[3],
                    text=fields[9],
                )
            )
    if play_x is None or play_y is None or style is None:
        raise ValueError(f"ASS missing PlayRes or Style: {path}")
    return AssFile(play_x, play_y, style, tuple(events))


def events_overlapping(events: tuple[AssEvent, ...], t0: float, t1: float, *, kind: str = "dialogue") -> list[AssEvent]:
    """Half-open overlap on the media clock. A cue ending at t0 belongs to the previous span."""
    selected = []
    for event in events:
        if event.kind != kind:
            continue
        if event.end <= t0 or event.start >= t1:
            continue
        selected.append(event)
    return selected
