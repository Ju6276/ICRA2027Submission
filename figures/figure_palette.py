"""Shared semantic palette for Figures 1--3 and a vector snowflake."""
import math
INK = '#202A30'
EDGE = '#647781'
NEUTRAL = '#EEF1F3'
BACKGROUND = '#F7F8F9'
# Shared data colors match Fig. 2's targets, heads, and reference chunks.
# Peach denotes the shared student module / joint correction; it is a
# semantic color, not an RGB mixture of the separately supervised outputs.
REFERENCE = '#9DC3E6'
REFERENCE_EDGE = '#38688B'
FORCE = '#FFE699'
FORCE_EDGE = '#806722'
FORCE_ACCENT = FORCE_EDGE
DELAY = '#D7D0E7'
DELAY_EDGE = '#695781'
DELAY_ACCENT = DELAY_EDGE
STUDENT_FILL = '#F8CBAD'
STUDENT_ACCENT = '#E7AE88'
JOINT_CORRECTION = STUDENT_ACCENT
JOINT_CORRECTION_EDGE = '#9A6444'
COMMAND = '#85A771'
COMMAND_EDGE = '#4E8A45'


def snowflake_segments(cx, cy, radius, yscale=1):
    for i in range(6):
        angle = math.pi * i / 3
        ux, uy = math.cos(angle), math.sin(angle)
        yield [(cx,cy),(cx+radius*ux,cy+radius*uy*yscale)]
        for side in [-1,1]:
            yield [(cx+.58*radius*ux,cy+.58*radius*uy*yscale),
                   (cx+radius*(.8*ux-side*.19*uy),
                    cy+radius*(.8*uy+side*.19*ux)*yscale)]
