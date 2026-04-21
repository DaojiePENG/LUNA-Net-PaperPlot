"""
Compose LUNA-Net main architecture figure (Fig. 3-0):
  (a) LUNA-Net overview          -- left column, full height
  (b) LLEM architecture          -- right column, top
  (c) RSNE architecture          -- right column, middle
  (d) IAF  architecture          -- right column, bottom

SVG source dimensions (used to set height_ratios):
  Fig.3-1: 531 x 436 px  (w:h = 1.218)
  Fig.3-2: 821 x 232 px  (w:h = 3.540)
  Fig.3-3: 820 x 228 px  (w:h = 3.596)
  Fig.3-4: 914 x 271 px  (w:h = 3.372)

Backend: Agg (no xelatex required).  Set USE_PGF=True on a machine with
xelatex on PATH to get LaTeX-typeset labels.
"""

import os

USE_PGF = False   # set True on a machine with xelatex in PATH

import matplotlib
if USE_PGF:
    matplotlib.use('pgf')
else:
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import rcParams
import numpy as np
import fitz  # PyMuPDF  (pip install pymupdf)

_base_params = {
    'font.family': 'serif',
    'font.serif':  ['Times New Roman', 'DejaVu Serif'],
    'font.size': 12,
    'figure.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
}
if USE_PGF:
    _base_params.update({
        'pgf.texsystem': 'xelatex',
        'pgf.rcfonts': False,
        'pgf.preamble': (
            r'\usepackage{xcolor}'
            r'\usepackage{fontspec}'
            r'\setmainfont{Times New Roman}'
        ),
    })
rcParams.update(_base_params)

BASE   = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(BASE)


def pdf_to_array(path, dpi=300):
    """Render the first page of a PDF to an RGB numpy array via PyMuPDF."""
    doc  = fitz.open(path)
    page = doc[0]
    mat  = fitz.Matrix(dpi / 72, dpi / 72)
    pix  = page.get_pixmap(matrix=mat, alpha=False)
    arr  = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
               pix.height, pix.width, 3)
    doc.close()
    return arr


print('Loading sub-figures ...')
img_a = pdf_to_array(os.path.join(PARENT, 'Fig.3-1_LUNA-Net_arch_EN.pdf'))
img_b = pdf_to_array(os.path.join(PARENT, 'Fig.3-2_LLEM_arch_EN.pdf'))
img_c = pdf_to_array(os.path.join(PARENT, 'Fig.3-3_RSNE_arch_EN.pdf'))
img_d = pdf_to_array(os.path.join(PARENT, 'Fig.3-4_IAF_arch_EN.pdf'))

PANELS = [
    (img_a, r'(a) LUNA-Net Architecture Overview'),
    (img_b, r'(b) Low-Light Enhancement Module (LLEM)'),
    (img_c, r'(c) Road Surface Normal Estimation (RSNE)'),
    (img_d, r'(d) Illumination-Aware Fusion (IAF)'),
]

FIG_W = 14.0
FIG_H =  6.2

fig = plt.figure(figsize=(FIG_W, FIG_H))

gs = gridspec.GridSpec(
    3, 2,
    figure=fig,
    width_ratios=[1.05, 1],
    height_ratios=[232, 228, 271],
    hspace=0.12,
    wspace=0.04,
    left=0.005,
    right=0.995,
    top=0.995,
    bottom=0.055,
)

ax_a = fig.add_subplot(gs[:, 0])
ax_b = fig.add_subplot(gs[0, 1])
ax_c = fig.add_subplot(gs[1, 1])
ax_d = fig.add_subplot(gs[2, 1])

for ax, (img, label) in zip([ax_a, ax_b, ax_c, ax_d], PANELS):
    ax.imshow(img, interpolation='lanczos')
    ax.axis('off')
    ax.text(0.5, -0.03, label, transform=ax.transAxes,
            fontsize=12, ha='center', va='top')

out = os.path.join(BASE, 'Fig.3-0_LUNA-Net_main_EN')
fig.savefig(out + '.pdf')
fig.savefig(out + '.png', dpi=200)
print(f'Saved: {out}.{{pdf,png}}')
plt.close()