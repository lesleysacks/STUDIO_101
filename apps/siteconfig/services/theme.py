"""Map validated theme tokens onto the CSS variables the stylesheets already use."""

from __future__ import annotations

from .security import FONT_STACKS, assert_css_fragment


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    raw = value.lstrip("#")
    return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)


def build_theme_css(theme: dict) -> str:
    colors = theme["colors"]
    layout = theme["layout"]
    typography = theme["typography"]
    red, green, blue = _hex_to_rgb(colors["primary"])
    heading = FONT_STACKS[typography["heading_font"]]
    body = FONT_STACKS[typography["body_font"]]
    declarations = {
        "--primary": colors["primary"],
        "--primary-light": colors["primary_light"],
        "--primary-glow": f"rgba({red}, {green}, {blue}, 0.4)",
        "--bg-dark": colors["background"],
        "--bg-primary": colors["background"],
        "--bg-card": colors["surface"],
        "--bg-surface": colors["surface"],
        "--bg-surface-elevated": colors["surface"],
        "--text-white": colors["text"],
        "--text-primary": colors["text"],
        "--text-muted": colors["muted"],
        "--text-secondary": colors["muted"],
        "--text-gray": colors["subtle"],
        "--accent-burgundy": colors["primary"],
        "--accent-rose": colors["primary_light"],
        "--accent-gold": colors["accent"],
        "--border-burgundy": f"rgba({red}, {green}, {blue}, 0.5)",
        "--accent-burgundy-glow": f"rgba({red}, {green}, {blue}, 0.4)",
        "--font-heading": heading,
        "--font-body": body,
        "--radius-sm": layout["card_radius"],
        "--radius-md": layout["radius_md"],
        "--radius-lg": layout["radius_lg"],
        "--site-content-width": layout["content_width"],
        "--section-spacing": layout["section_spacing"],
    }
    for name, value in declarations.items():
        assert_css_fragment(value, file="theme.json", path=f"$.css.{name}")
    variables = "".join(f"{name}: {value};" for name, value in declarations.items())
    return (
        f":root{{{variables}}}"
        ".container{max-width:var(--site-content-width);}"
        "section{padding:var(--section-spacing) 0;}"
    )
