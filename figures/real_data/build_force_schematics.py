#!/usr/bin/env python3
"""Compact F/T input illustrations from the saved 100 Hz data.

Force and torque each use one max-absolute display scale across their three
axes. This preserves the time-series shape and within-group proportions;
these drawings have no quantitative axis. No smoothing or synthetic data.
"""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

ROOT = Path(__file__).resolve().parent
COLORS = ('#377AB5', '#D89135', '#639378')
CHANNELS = ('fx', 'fy', 'fz', 'tx', 'ty', 'tz')

def read_data(path):
    groups = {}
    with path.open(newline='') as stream:
        for row in csv.DictReader(stream):
            groups.setdefault(row['arm'], []).append(row)
    return {arm: {key: np.asarray([float(row[key]) for row in rows])
                  for key in ('time_s',) + CHANNELS}
            for arm, rows in groups.items()}


def draw_axis(ax, values, scale_source, compact=False, show_axes=False):
    x = values['time_s']
    display_x = (x-x[0]) / (x[-1]-x[0])
    scales = {}
    for prefix, style in [('f', '-'), ('t', (0, (3, 2)))]:
        channels = np.array([values[prefix+axis] for axis in 'xyz'])
        maximum = float(np.max(np.abs([scale_source[prefix+axis] for axis in 'xyz'])))
        scale = maximum if maximum > 0 else 1.0
        scales['force' if prefix == 'f' else 'torque'] = scale
        for data, color in zip(channels, COLORS):
            ax.plot(display_x, data/scale, color=color, linewidth=.8 if compact else 1.0,
                    linestyle=style, solid_capstyle='round', dash_capstyle='round')
    ax.set_xlim(-.025, 1.025)
    ax.set_ylim(-1.16, 1.16)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
    if show_axes:
        ax.set_xlim(-.065, 1.06)
        axis_style = dict(arrowstyle='-|>', color='#66717C', lw=.65,
                          mutation_scale=8, shrinkA=0, shrinkB=0)
        # The horizontal axis also marks the common physical zero of F and T.
        ax.annotate('', xy=(1.035, 0), xytext=(0, 0),
                    arrowprops=axis_style, zorder=0)
        ax.annotate('', xy=(0, 1.12), xytext=(0, -1.10),
                    arrowprops=axis_style, zorder=0)
        ax.annotate('0', xy=(0, 0), xytext=(-5, -4),
                    textcoords='offset points', ha='right', va='top',
                    fontsize=7, color='#485460')
        ax.text(1.045, -.09, '$t$', ha='left', va='top',
                fontsize=8, color='#485460')
    raw_selection = (scale_source['time_s'] >= x[0]) & (scale_source['time_s'] <= x[-1])
    return {'force_scale_N': scales['force'], 'torque_scale_Nm': scales['torque'],
            'source_time_range_s': [float(x[0]), float(x[-1])], 'samples': len(x),
            'segment_peak_force_norm_N': float(np.linalg.norm([scale_source['f'+a][raw_selection] for a in 'xyz'], axis=0).max()),
            'segment_peak_torque_norm_Nm': float(np.linalg.norm([scale_source['t'+a][raw_selection] for a in 'xyz'], axis=0).max())}


def render(folder, groups, scale_sources, filename, show_axes=False):
    fig, axes = plt.subplots(len(groups), 1, squeeze=False,
                             figsize=(3.8, 1.9), facecolor='none')
    fig.subplots_adjust(left=.025, right=.975, bottom=.035, top=.81, hspace=.24)
    fig.legend(handles=[Line2D([], [], color='#485460', lw=1.2, label='F'),
                        Line2D([], [], color='#485460', lw=1.2, linestyle=(0, (3, 2)), label='T')],
               frameon=False, ncol=2, loc='upper right', bbox_to_anchor=(.99, .99),
               borderaxespad=0, handlelength=1.6, handletextpad=.4, columnspacing=1, fontsize=9)
    scales = {}
    for ax, (arm, values) in zip(axes[:, 0], groups.items()):
        scales[arm] = draw_axis(ax, values, scale_sources[arm], compact=len(groups)>1,
                                show_axes=show_axes)
        if len(groups) > 1:
            ax.text(0, 1.0, arm.capitalize(), transform=ax.transAxes,
                    fontsize=7, color='#485460', va='bottom')
    for extension in ('png', 'svg'):
        kwargs = {'metadata': {'Date': None}} if extension == 'svg' else {}
        fig.savefig(folder / f'{filename}.{extension}', dpi=320, transparent=True, **kwargs)
    plt.close(fig)
    return scales


def main():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype': 'none'})
    for platform in ('franka_object_flipping', 'bimanual'):
        base = ROOT / platform
        groups = read_data(base / 'data/wrench_100hz.csv')
        scale_sources = groups
        if platform == 'bimanual':
            # Author requested a lower-magnitude interval for the input sketch.
            # Use the same recorded interval for both arms and retain the full
            # episode display scales, so this interval is not magnified again.
            groups = {arm: {key: value[(values['time_s'] >= 1.6) & (values['time_s'] <= 2.6)]
                            for key, value in values.items()}
                      for arm, values in groups.items()}
        folder = base / 'plots'
        report = {'source': 'data/wrench_100hz.csv',
                  'role': 'Qualitative input illustration',
                  'display_transform': 'Force and torque separately divided by their full-episode group maximum absolute value across the three axes; no mean subtraction, smoothing, or extra magnification of the selected interval.',
                  'line_styles': {'force': 'solid', 'torque': 'dashed'},
                  'axis_colors': dict(zip('xyz', COLORS)), 'outputs': {}}
        report['coordinate_frame'] = 'world' if platform == 'bimanual' else 'Franka base O'
        if platform == 'bimanual':
            report['interval_selection'] = {'range_s': [1.6, 2.6],
                                            'reason': 'Author requested a low-magnitude input example; selected one continuous early-episode interval for both arms.',
                                            'scope': 'Input illustration only; not a full-episode performance summary.'}
        report['layout'] = {'width_inches': 3.8, 'height_inches': 1.9,
                            'arrangement': 'vertically stacked arms' if len(groups)>1 else 'single arm'}
        name = 'force_torque_schematic'
        show_axes = platform == 'franka_object_flipping'
        report['layout']['axes'] = 'Arrowed axes with zero origin and time label; no other numeric ticks' if show_axes else 'Hidden'
        report['outputs'][name] = render(folder, groups, scale_sources, name,
                                         show_axes=show_axes)
        (folder / 'force_torque_schematic_metadata.json').write_text(
            json.dumps(report, indent=2) + '\n')
        print(f'{platform}: ' + ', '.join(report['outputs']))


if __name__ == '__main__':
    main()
