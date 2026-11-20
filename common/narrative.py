"""Narration without voice-over: chapter tag (top-left) + reading-paced captions (bottom).

Every scene of an episode inherits from `Narrated`, so captions always sit in the same place,
use the same size, and stay on screen long enough to be read.
"""
import re
from manim import (Scene, MovingCameraScene, Tex, VGroup, FadeIn, FadeOut, FadeTransform,
                   UP, DOWN, LEFT, UL, config)
from common.style import FG, MUTED

CAPTION_Y = -3.35
CAPTION_SIZE = 34
CAPTION_WIDTH = 13.0
WORDS_PER_SECOND = 3.2       # comfortable reading speed for a technical audience


def reading_time(text):
    maths = re.findall(r"\$[^$]*\$", text)
    words = len(re.sub(r"\$[^$]*\$", " ", text).split()) + 2 * len(maths)
    return max(1.6, 0.8 + words / WORDS_PER_SECOND)


class NarrationMixin:
    caption = None
    chapter_tag = None

    def _make_caption(self, text, size):
        cap = Tex(text, font_size=size, color=FG)
        if cap.width > CAPTION_WIDTH:
            cap.scale_to_fit_width(CAPTION_WIDTH)
        return cap.move_to([0, CAPTION_Y, 0])

    def say(self, text, wait=None, size=CAPTION_SIZE, run_time=0.8, extra=0.0, anims=()):
        """Show (or replace) the caption, play optional animations meanwhile, then wait to read."""
        new = self._make_caption(text, size)
        intro = FadeIn(new, shift=0.1 * UP) if self.caption is None else FadeTransform(self.caption, new)
        self.play(intro, *anims, run_time=run_time)
        self.caption = new
        t = reading_time(text) + extra if wait is None else wait
        if t > 0:
            self.wait(t)

    def unsay(self, run_time=0.5):
        if self.caption is not None:
            self.play(FadeOut(self.caption), run_time=run_time)
            self.caption = None

    def chapter(self, label, animate=True):
        tag = Tex(label, font_size=26, color=MUTED).to_corner(UL, buff=0.35)
        if self.chapter_tag is None:
            if animate:
                self.play(FadeIn(tag), run_time=0.6)
            else:
                self.add(tag)
        else:
            self.play(FadeTransform(self.chapter_tag, tag), run_time=0.6)
        self.chapter_tag = tag


class Narrated(NarrationMixin, Scene):
    pass


class NarratedCamera(NarrationMixin, MovingCameraScene):
    pass
