"""
Compose the main LUNA-Net architecture figure (Fig.3-0):
  (a) LUNA-Net overall architecture  -- left column, full height
  (b) LLEM module architecture       -- right column, top
  (c) RSNE module architecture       -- right column, middle
  (d) IAF module architecture        -- right column, bottom
"""

import os

import fitz  # PyMuPDF
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import rcParams
from PIL import Image

rcParams.update({
    'font.family': 'serif',
    'font.size': 8,
    'figure.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
})

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)


def pdf_to_array(pdf_path: str, dpi: int = 300) -> np.ndarray:
    """Render the first page of a PDF to an RGB numpy array."""
    doc = fitz.open(pdf_path)
    page = doc[0]
    mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return np.array(img)


# ---------------------------------------------------------------------------
# Load panel images
# ---------------------------------------------------------------------------
img_a = pdf_to_array(os.path.join(ROOT, 'Fig.3-1_LUNA-Net_arch_EN.pdf'))
img_b = pdf_to_array(os.path.join(ROOT, 'Fig.3-2_LLEM_arch_EN.pdf'))
img_c = pdf_to_array(os.path.join(ROOT, 'Fig.3-3_RSNE_arch_EN.pdf'))
img_d = pdf_to_array(os.path.join(ROOT, 'Fig.3-4_IAF_arch_EN.pdf'))

# ---------------------------------------------------------------------------
# Figure layout
# Fig.3-1 aspect ≈ 1.216  (w/h)
# Fig.3-2 aspect ≈ 3.541
# Fig.3-3 aspect ≈ 3.595
# Fig.3-4 aspect ≈ 3.378
#
# Target: equal total height for left and right columns.
# With width_ratio left≈0.51, right≈0.49 the heights balance well.
# ---------------------------------------------------------------------------
FIG_W = 13.5          # total figure width in inches
LEFT_FRAC = 0.51      # fraction of width for left column
LABEL_Y_LEFT = -0.04   # y-offset for left-panel caption (in axes fraction)
LABEL_Y_RIGHT = -0.08  # y-offset for right-panel captions (in axes fraction)
HSPACE_RIGHT = 0.22    # vertical gap between right panels (fraction of avg subplot height)

w_L = FIG_W * LEFT_FRAC
w_R = FIG_W * (1.0 - LEFT_FRAC)

# Compute height from Fig.3-1 aspect ratio
h_a_aspect = img_a.shape[1] / img_a.shape[0]   # width / height
fig_h = w_L / h_a_aspect

# Compute individual heights for right panels so they fill the right column
h_b_frac = (img_b.shape[0] / img_b.shape[1])  # height/width
h_c_frac = (img_c.shape[0] / img_c.shape[1])
h_d_frac = (img_d.shape[0] / img_d.shape[1])
total_h_frac = h_b_frac + h_c_frac + h_d_frac

height_ratios = [h_b_frac / total_h_frac,
                 h_c_frac / total_h_frac,
                 h_d_frac / total_h_frac]

# ---------------------------------------------------------------------------
# Build figure with outer GridSpec (1 row × 2 cols) +
# inner GridSpec (3 rows × 1 col) for the right column
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(FIG_W, fig_h))
outer = gridspec.GridSpec(
    1, 2,
    figure=fig,
    width_ratios=[LEFT_FRAC, 1.0 - LEFT_FRAC],
    wspace=0.03,
)

# Left panel (a)
ax_a = fig.add_subplot(outer[0, 0])
ax_a.imshow(img_a)
ax_a.text(0.5, LABEL_Y_LEFT, r'(a) LUNA-Net Architecture',
          transform=ax_a.transAxes, fontsize=8, ha='center', va='top')
ax_a.axis('off')

# Right column: nested GridSpec
inner = gridspec.GridSpecFromSubplotSpec(
    3, 1,
    subplot_spec=outer[0, 1],
    hspace=HSPACE_RIGHT,
    height_ratios=height_ratios,
)

panels_right = [
    (img_b, r'(b) LLEM Module Architecture'),
    (img_c, r'(c) RSNE Module Architecture'),
    (img_d, r'(d) IAF Module Architecture'),
]
for i, (img, label) in enumerate(panels_right):
    ax = fig.add_subplot(inner[i])
    ax.imshow(img)
    ax.text(0.5, LABEL_Y_RIGHT, label,
            transform=ax.transAxes, fontsize=8, ha='center', va='top')
    ax.axis('off')

# ---------------------------------------------------------------------------
# Save outputs
# ---------------------------------------------------------------------------
out_stem = os.path.join(ROOT, 'Fig.3-0_LUNA-Net_EN')
fig.savefig(out_stem + '.pdf')
fig.savefig(out_stem + '.png', dpi=200)
print(f'Saved: {out_stem}.{{pdf,png}}')
plt.close()
