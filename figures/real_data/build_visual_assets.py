#!/usr/bin/env python3
"""Extract selected native video frames and plot timestamped wrench exports.

Requires numpy, matplotlib, Pillow and av. Run after export_signals.py.
Single-frame PNGs are uncropped and contain no labels or overlays.
"""

import argparse
import copy
import csv
import json
from pathlib import Path

import av
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
COLORS = ("#3374B4", "#D66B36", "#3A9275")
PLATFORMS = {
    "franka": {
        "title": "Franka",
        "frames": [250, 400, 550, 700],
        "cameras": [
            ("observation_image", "External", "videos/observation_image/episode_000000.mp4"),
            ("observation_wrist_image", "Wrist", "videos/observation_wrist_image/episode_000000.mp4"),
        ],
    },
    "bimanual": {
        "title": "Bimanual",
        "frames": [200, 275, 350, 425],
        "cameras": [
            ("faceImg", "Front", "faceImg.mp4"),
            ("leftImg", "Left wrist", "leftImg.mp4"),
            ("rightImg", "Right wrist", "rightImg.mp4"),
        ],
    },
}


def font(size, bold=False):
    path = Path("/System/Library/Fonts/Supplemental") / ("Arial Bold.ttf" if bold else "Arial.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def save_frames(source, output, config):
    records = []
    for camera, label, relative in config["cameras"]:
        destination = output / "images" / camera
        destination.mkdir(parents=True, exist_ok=True)
        wanted = {frame: f"t{i + 1:02d}" for i, frame in enumerate(config["frames"])}
        with av.open(str(source / relative)) as video:
            rate = float(video.streams.video[0].average_rate)
            for index, frame in enumerate(video.decode(video=0)):
                if index in wanted:
                    name = wanted[index]
                    target = destination / f"{name}.png"
                    picture = frame.to_image().convert("RGB")
                    picture.save(target, optimize=True)
                    records.append({"camera": camera, "view_label": label, "id": name,
                                    "frame_index": index, "width": picture.width, "height": picture.height,
                                    "video_time_s": float(frame.time) if frame.time is not None else index / rate,
                                    "file": str(target.relative_to(output)), "source_video": relative})
                if index >= max(wanted):
                    break
        if len(list(destination.glob("t*.png"))) != 4:
            raise RuntimeError(f"Expected four images for {camera}")
    (output / "images_manifest.json").write_text(json.dumps(records, indent=2) + "\n")
    return records


def fit_image(canvas, path, rectangle):
    x, y, width, height = rectangle
    picture = Image.open(path).convert("RGB")
    picture.thumbnail((width, height), Image.Resampling.LANCZOS)
    canvas.paste(picture, (x + (width - picture.width) // 2, y + (height - picture.height) // 2))


def multiview(output, config, timing):
    cell_w, cell_h, gutter, margin, label_h = 520, 390, 16, 24, 52
    rows = len(config["cameras"])
    top_h = 108
    width = margin * 2 + cell_w * 4 + gutter * 3
    height = top_h + rows * (cell_h + label_h + gutter) + margin
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, 20), config["title"] + " | Four selected timesteps", font=font(34, True), fill="#223344")
    for column, point in enumerate(timing):
        draw.text((margin + column * (cell_w + gutter), 68),
                  f"{point['id']}   {point['time_s']:.3f} s   (frame {point['frame_index']})",
                  font=font(24), fill="#526070")
    for row, (camera, label, _) in enumerate(config["cameras"]):
        y = top_h + row * (cell_h + label_h + gutter)
        draw.text((margin, y), label, font=font(26, True), fill="#223344")
        for column, point in enumerate(timing):
            x = margin + column * (cell_w + gutter)
            fit_image(sheet, output / "images" / camera / f"{point['id']}.png",
                      (x, y + label_h, cell_w, cell_h))
    sheet.save(output / "multiview_grid.png", optimize=True)
    # One camera strip per timestep; originals above retain their native sizes.
    for point in timing:
        strip = Image.new("RGB", (rows * cell_w + (rows - 1) * gutter, cell_h), "white")
        for row, (camera, _, _) in enumerate(config["cameras"]):
            fit_image(strip, output / "images" / camera / f"{point['id']}.png",
                      (row * (cell_w + gutter), 0, cell_w, cell_h))
        strip.save(output / f"multiview_{point['id']}.png", optimize=True)


def load_csv(path):
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    groups = {}
    for row in rows:
        groups.setdefault(row["arm"], []).append(row)
    return {arm: {key: np.array([float(row[key]) for row in values])
                  for key in ("time_s", "fx", "fy", "fz", "tx", "ty", "tz")
                  + (("time_offset_ms",) if "time_offset_ms" in values[0] else ())}
            for arm, values in groups.items()}


def style_axes(ax):
    ax.spines[["top", "right"]].set_visible(False)
    for name in ("left", "bottom"):
        ax.spines[name].set_color("#86919A")
        ax.spines[name].set_linewidth(.7)
    ax.grid(axis="y", color="#E5E8EB", linewidth=.6)
    ax.tick_params(colors="#45515C", width=.7, length=3)
    ax.margins(x=.01, y=.15)


def save_plot(fig, output, name):
    fig.savefig(output / (name + ".png"), dpi=240, facecolor="white")
    fig.savefig(output / (name + ".svg"), facecolor="white")
    plt.close(fig)


def wrench_plot(output, config, groups, timing, name, history=False, bi_si_units=False):
    arms = sorted(groups)
    labels = {"arm": "Franka | base frame", "franka": "Franka | base frame", "left": "Left arm | world frame", "right": "Right arm | world frame"}
    units_known = config["title"] == "Franka" or bi_si_units
    fig, axes = plt.subplots(2, len(arms), squeeze=False, sharex=True,
                             figsize=(7.6 if len(arms) == 1 else 11.2, 4.9), layout="constrained")
    for column, arm in enumerate(arms):
        values = groups[arm]
        x = values["time_offset_ms"] if history else values["time_s"]
        for row, (prefix, quantity, unit) in enumerate((("f", "Force", "N"), ("t", "Torque", "N·m"))):
            ax = axes[row, column]
            for component, color in zip("xyz", COLORS):
                ax.plot(x, values[prefix + component], color=color,
                        linewidth=1.45 if history else .95,
                        marker="o" if history else None, markersize=3 if history else 0,
                        label=("$F_" if prefix == "f" else r"$\tau_") + component + "$", zorder=3)
            ax.set_ylabel(f"{quantity} ({unit})" if units_known else f"{quantity} (source units)")
            style_axes(ax)
            ax.legend(loc="upper left", ncol=3, frameon=False, fontsize=9, handlelength=1.7,
                      columnspacing=1.4, bbox_to_anchor=(0, 1.13))
            if not history:
                for point in timing:
                    ax.axvline(point["time_s"], color="#929BA4", linewidth=.75, linestyle="--", zorder=1)
                    if row == 0:
                        ax.text(point["time_s"], .98, point["id"], transform=ax.get_xaxis_transform(),
                                ha="center", va="top", fontsize=8, color="#5D6975",
                                bbox={"facecolor":"white", "edgecolor":"none", "pad":1})
            if row == 1:
                ax.set_xlabel("Time relative to selected observation (ms)" if history else "Episode time (s)")
                if history:
                    ax.set_xticks([-100, -75, -50, -25, 0])
        title = labels.get(arm, arm.replace("_", " ").title())
        axes[0, column].set_title(title, loc="left", pad=31, fontweight="bold", fontsize=11)
    fig.suptitle(("100 ms wrench history" if history else "External wrench estimate") + " | 100 Hz resampled", fontsize=13)
    save_plot(fig, output / "plots", name)


def norm_plot(output, groups, timing, units_known):
    fig, axes = plt.subplots(len(groups), 1, squeeze=False, sharex=True,
                             figsize=(7.6, 2.6 if len(groups) == 1 else 4.7), layout="constrained")
    for row, (arm, values) in enumerate(sorted(groups.items())):
        ax = axes[row, 0]
        magnitude = np.sqrt(sum(values["f" + axis] ** 2 for axis in "xyz"))
        ax.plot(values["time_s"], magnitude, color="#3374B4", linewidth=1.1)
        ax.set_ylabel(r"$\|F\|_2$" + (" (N)" if units_known else " (source units)"))
        ax.set_title(arm.replace("_", " ").title(), loc="left", fontsize=11)
        style_axes(ax)
        ax.set_ylim(bottom=0)
        for point in timing:
            ax.axvline(point["time_s"], color="#929BA4", linewidth=.8, linestyle="--")
            ax.text(point["time_s"], .94, point["id"], transform=ax.get_xaxis_transform(),
                    ha="center", va="top", fontsize=8, color="#5D6975")
    axes[-1, 0].set_xlabel("Episode time (s)")
    fig.suptitle("Force magnitude | 100 Hz resampled", fontsize=12)
    save_plot(fig, output / "plots", "force_magnitude_100hz")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_root", type=Path, help="Downloaded source data directory")
    parser.add_argument("--platform", choices=PLATFORMS, help="Build only this platform")
    parser.add_argument("--source-subdir", help="Source directory relative to source_root; requires --platform")
    parser.add_argument("--output-subdir", help="Asset directory under real_data; requires --platform")
    parser.add_argument("--frames", nargs=4, type=int, help="Four selected video indices; requires --platform")
    parser.add_argument("--bimanual-si-units", action="store_true", help="Use only after source units are confirmed")
    parser.add_argument("--plots-only", action="store_true", help="Regenerate plots without changing extracted images or multiview sheets")
    args = parser.parse_args()
    if (args.source_subdir or args.output_subdir or args.frames) and not args.platform:
        parser.error("Source/output/frame overrides require --platform")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none",
                         "axes.titlesize": 11, "savefig.pad_inches": .05})
    selected = {args.platform: PLATFORMS[args.platform]} if args.platform else PLATFORMS
    for platform, base_config in selected.items():
        config = copy.deepcopy(base_config)
        if args.frames:
            config["frames"] = args.frames
        output = ROOT / (args.output_subdir or platform)
        output.mkdir(parents=True, exist_ok=True)
        (output / "plots").mkdir(exist_ok=True)
        records = [] if args.plots_only else save_frames(args.source_root / (args.source_subdir or platform), output, config)
        timing = json.loads((output / "timesteps.json").read_text())
        assert [point["frame_index"] for point in timing] == config["frames"]
        if not args.plots_only:
            multiview(output, config, timing)
        groups = load_csv(output / "data" / "wrench_100hz.csv")
        wrench_plot(output, config, groups, timing, "wrench_100hz", bi_si_units=args.bimanual_si_units)
        norm_plot(output, groups, timing, platform == "franka" or args.bimanual_si_units)
        for point in timing:
            histories = load_csv(output / "data" / f"history_{point['id']}_100ms.csv")
            wrench_plot(output, config, histories, timing, f"history_{point['id']}_100ms",
                        history=True, bi_si_units=args.bimanual_si_units)
        print(json.dumps({"platform": platform, "single_frames": len(records), "output": str(output)}))


if __name__ == "__main__":
    main()
