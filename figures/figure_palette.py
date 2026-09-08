"""Shared semantic palette and vector snowflake for Figures 1 and 2."""
import math
INK = '#202A30'
EDGE = '#647781'
NEUTRAL = '#EEF1F3'
BACKGROUND = '#F7F8F9'
REFERENCE = '#D8E8EE'
REFERENCE_EDGE = '#668C9C'
FORCE = '#F8DEC2'
FORCE_EDGE = '#B6793D'
DELAY = '#E7DDF0'
DELAY_EDGE = '#8D70A7'
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
