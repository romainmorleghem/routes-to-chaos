"""Shared visual identity for the *Routes to Chaos* series."""
from manim import config, TexTemplate, ManimColor

# Palette — dark background, one warm accent for "the map", one cool for "the identity line".
BG = ManimColor("#0E1116")
FG = ManimColor("#E6E6E6")
MUTED = ManimColor("#7A8291")
MAP = ManimColor("#F2A541")      # the map f(x)
DIAG = ManimColor("#5DA9E9")     # y = x, fixed points
ORBIT = ManimColor("#E85D75")    # cobweb / trajectories
STABLE = ManimColor("#6CCB8B")
ACCENT = ManimColor("#C792EA")   # constants (delta, alpha)

# Bifurcation-diagram colormap stops (density -> colour), dark to bright.
DENSITY_STOPS = ["#0E1116", "#2B2D6E", "#7A3E9D", "#E85D75", "#F2A541", "#FFF4D6"]

TEX = TexTemplate()
TEX.add_to_preamble(r"\usepackage{amsmath,amssymb}")


def setup():
    config.background_color = BG
    config.tex_template = TEX
