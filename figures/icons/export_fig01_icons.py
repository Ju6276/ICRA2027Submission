#!/usr/bin/env python3
"""Extract Fig. 1's original vector icons without redrawing or editing the figure.

Requires PyMuPDF (fitz) for SVG rendering. Element selections refer to the
verified source revision below; re-check them if the figure is regenerated.
The four existing Twemoji SVGs are copied directly, retaining their attribution.
"""
from copy import deepcopy
import hashlib
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

import fitz

OUT = Path(__file__).resolve().parent
SOURCE = OUT / 'sources' / 'fig01_original.svg'
SOURCE_SHA256 = 'd6b3a92e9a41f1594504822986032135e2269be4ec4ccf32aad9352b0787a3cb'
SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')


def groups(patches=(), lines=()):
    return {f'patch_{i}' for i in patches} | {f'line2d_{i}' for i in lines}


SELECTIONS = {
    'proprioception': groups(patches=[39, 43, 53, 54, 55, 65, 66]),
    'force_history': groups(lines=[22, 23]),
    'frozen': groups(lines=range(4, 22)),
    'force_target': groups(patches=[40, 41, 44, 45, 46, 56, 57, 58, 59, 60, 67, 68]),
    'delay_target': groups(patches=[42], lines=[24, 25, 26, 51, 52]),
    'correction_distillation': groups(patches=[73, 75], lines=range(61, 68)),
    'robot_arm': groups(patches=[38, 61, 62, 63, 69, 70, 71],
                        lines=[48, 49, 50, 53, 54, 58, 59, 60]),
}


def svg_bytes(root):
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def extract(root, identifiers, name):
    out = ET.Element(f'{{{SVG}}}svg', dict(root.attrib))
    ET.SubElement(out, f'{{{SVG}}}title').text = f'Fig. 1: {name.replace("_", " ")}'
    ET.SubElement(out, f'{{{SVG}}}desc').text = (
        'Original vector elements extracted from fig01_method_overview.svg. '
        'No surrounding card, label or data-flow connection is included.')
    definitions = ET.SubElement(out, f'{{{SVG}}}defs')
    seen_ids = set()
    # Marker definitions and the original figure clipping rectangle remain valid
    # in the unchanged source coordinate system.
    for original_defs in root.iter(f'{{{SVG}}}defs'):
        for item in original_defs:
            identifier = item.get('id')
            if identifier and identifier in seen_ids:
                continue
            definitions.append(deepcopy(item))
            if identifier:
                seen_ids.add(identifier)
    found = set()
    for item in root.iter():
        if item.get('id') not in identifiers:
            continue
        found.add(item.get('id'))
        copied = deepcopy(item)
        for parent in copied.iter():
            for child in list(parent):
                if child.tag == f'{{{SVG}}}defs':
                    parent.remove(child)
        out.append(copied)
    if found != identifiers:
        raise ValueError(f'Missing SVG elements for {name}: {identifiers-found}')
    # Determine actual painted bounds, including stroke caps, markers and glow.
    with fitz.open(stream=svg_bytes(out), filetype='svg') as doc:
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(4, 4), alpha=True)
        from PIL import Image
        painted = Image.frombytes('RGBA', (pix.width, pix.height), pix.samples).getbbox()
        if painted is None:
            raise ValueError(f'Empty icon: {name}')
        vx, vy, vw, vh = map(float, root.get('viewBox').split())
        x0, x1 = (vx + painted[i] * vw / pix.width for i in (0, 2))
        y0, y1 = (vy + painted[i] * vh / pix.height for i in (1, 3))
    side = max(x1-x0, y1-y0) * 1.16
    cx, cy = (x0+x1)/2, (y0+y1)/2
    out.set('viewBox', f'{cx-side/2:.6f} {cy-side/2:.6f} {side:.6f} {side:.6f}')
    out.set('width', '512')
    out.set('height', '512')
    return out


def rasterize(svg_path):
    with fitz.open(svg_path) as doc:
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(512/page.rect.width, 512/page.rect.height), alpha=True)
        assert (pix.width, pix.height) == (512, 512)
        pix.save(svg_path.with_suffix('.png'))


def main():
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise RuntimeError('Fig. 1 changed. Verify SVG element selections before exporting.')
    root = ET.parse(SOURCE).getroot()
    for name, identifiers in SELECTIONS.items():
        target = OUT / f'fig01_{name}.svg'
        target.write_bytes(svg_bytes(extract(root, identifiers, name)))
        rasterize(target)
        print(target.stem)
    for name in ('camera', 'instruction', 'teacher', 'student'):
        target = OUT / f'fig01_{name}.svg'
        shutil.copyfile(OUT / f'{name}.svg', target)
        rasterize(target)
        print(target.stem)


if __name__ == '__main__':
    main()
