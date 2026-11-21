"""Render every sequence of episode 2 in order and concatenate them into one video.

    python render.py            # 480p preview  -> media/ep02_preview_480p15.mp4
    python render.py -q k       # 4K final      -> media/ep02_2160p60.mp4
    python render.py --only s03 # re-render one sequence, then re-assemble

Each scene starts on the exact frame where the previous one ends (shared layouts in
scenes/_stages.py), so plain concatenation gives a continuous video.
"""
import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parent / "media"
SEQUENCE = [
    ("s00_cold_open", "ColdOpen"),
    ("s01_squaring", "Squaring"),
    ("s02_orbits", "Orbits"),
    ("s03_cardioid", "Cardioid"),
    ("s04_bulbs", "Bulbs"),
    ("s05_real_axis", "RealAxis"),
    ("s06_julia", "Julia"),
    ("s07_teaser", "Teaser"),
]
QUALITY = {"l": "480p15", "m": "720p30", "h": "1080p60", "p": "1440p60", "k": "2160p60"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-q", default="l", choices=QUALITY)
    ap.add_argument("--only", nargs="*", default=None, help="file prefixes to re-render, e.g. s03 s04")
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    folder = QUALITY[a.q]
    parts = []
    for f, scene in SEQUENCE:
        out = MEDIA / "videos" / f / folder / f"{scene}.mp4"
        todo = not a.no_render and (a.only is None or any(f.startswith(o) for o in a.only))
        if todo or not out.exists():
            print(f"--> {f}.{scene} [{folder}]", flush=True)
            subprocess.run(["manim", f"-q{a.q}", "--media_dir", str(MEDIA), str(HERE / "scenes" / f"{f}.py"),
                            scene], check=True, cwd=HERE / "scenes")
        parts.append(out)
    lst = MEDIA / f"ep02_{folder}.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    final = MEDIA / f"ep02_{folder}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", str(final)], check=True)
    print(f"Episode assembled: {final}")


if __name__ == "__main__":
    sys.exit(main())
