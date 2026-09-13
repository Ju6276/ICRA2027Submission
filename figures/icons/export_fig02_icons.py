#!/usr/bin/env python3
"""Export the five input glyphs currently used in Fig. 2(b).

Geometry, colors and stroke widths match the existing figure functions.
Outputs are editable SVGs and 512-pixel PNGs with transparent backgrounds.
"""
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parent))
from figure_palette import draw_input_icon, FORCE_EDGE


def force_history(ax):
    # Matches draw_fig02_architecture.force_history(31, cy-13, 32, 26),
    # shifted onto this isolated icon canvas; no numerical data are implied.
    x, y, w, h = 4, 7, 32, 26
    ax.plot([x, x, x+w], [y+2, y+h, y+h], color='#555555', lw=.8,
            solid_capstyle='round', solid_joinstyle='round', zorder=3)
    t = np.linspace(0, 1, 120)
    yy = y+h*(.68-.25*np.sin(2*np.pi*t)*np.exp(-.9*t)-.15*t)
    ax.plot(x+5+(w-10)*t, yy, color=FORCE_EDGE, lw=1.7,
            solid_capstyle='round', solid_joinstyle='round', zorder=3)


def main():
    glyphs = [('pooled_context', 'context'), ('force_history', None),
              ('proprioception', 'proprioception'), ('reference', 'reference'),
              ('timing', 'timing')]
    plt.rcParams['svg.fonttype'] = 'none'
    for name, kind in glyphs:
        # Fig. 2 uses 100 drawing units per inch. Preserve its stroke-to-size ratio.
        fig = plt.figure(figsize=(.4, .4), facecolor='none')
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set(xlim=(0, 40), ylim=(40, 0))
        ax.axis('off')
        if kind:
            draw_input_icon(ax, kind, 20, 20, 32, -32)
        else:
            force_history(ax)
        base = OUT / f'fig02_{name}'
        fig.savefig(base.with_suffix('.svg'), transparent=True,
                    metadata={'Date': None, 'Description': f'Fig. 2 input icon: {name}'})
        fig.savefig(base.with_suffix('.png'), dpi=1280, transparent=True)
        plt.close(fig)
        print(base.name)


if __name__ == '__main__':
    main()
