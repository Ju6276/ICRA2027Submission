"""Shared semantic palette for Figures 1--3 and a vector snowflake."""
import math
INK = '#202A30'
EDGE = '#647781'
NEUTRAL = '#EEF1F3'
BACKGROUND = '#F7F8F9'
REFERENCE = '#D8E8EE'
REFERENCE_EDGE = '#668C9C'
# Palette C: apricot force, rose delay, and their equal RGB mix for the
# student's joint correction. Light fills and darker strokes keep small
# modules and labels legible at the paper's printed size.
FORCE_ACCENT = '#DF9E64'
FORCE = '#F9ECE0'
FORCE_EDGE = '#B27E50'
DELAY_ACCENT = '#C87598'
DELAY = '#F4E3EA'
DELAY_EDGE = '#A05E7A'
JOINT_CORRECTION = '#D48A7E'
JOINT_CORRECTION_EDGE = '#AA6E65'
COMMAND = '#E7EEDC'


def snowflake_segments(cx, cy, radius, yscale=1):
    for i in range(6):
        angle = math.pi * i / 3
        ux, uy = math.cos(angle), math.sin(angle)
        yield [(cx,cy),(cx+radius*ux,cy+radius*uy*yscale)]
        for side in [-1,1]:
            yield [(cx+.58*radius*ux,cy+.58*radius*uy*yscale),
                   (cx+radius*(.8*ux-side*.19*uy),
                    cy+radius*(.8*uy+side*.19*ux)*yscale)]
