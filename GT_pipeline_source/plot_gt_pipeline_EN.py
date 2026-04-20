"""
Compose GT preprocessing pipeline figure: 8 stages in 2x4 grid (English version).
"""
import os
import matplotlib; matplotlib.use('pgf')
import matplotlib.pyplot as plt
from matplotlib import rcParams
from PIL import Image

rcParams.update({
    'pgf.texsystem': 'xelatex',
    'pgf.rcfonts': False,
    'pgf.preamble': (
        r'\usepackage{xcolor}'
        r'\definecolor{sduColor}{cmyk}{0.26,1,1,0.28}'
        r'\usepackage{fontspec}'
        r'\setmainfont{Times New Roman}'
    ),
    'font.family': 'serif',
    'font.size': 8, 'figure.dpi': 300,
    'savefig.bbox': 'tight', 'savefig.pad_inches': 0.05,
})

BASE = os.path.dirname(__file__)
SRC = '/home/admin1/Mycode/Master_Thesis/Ch3_LUNA-Net/outputs/_Paper/GT_Preprocessing_Visualization_2'

panels = [
    ('sample4_1_rgb.png',            r'(a) Original RGB'),
    ('sample4_2_all_lidarseg.png',   r'(b) Semantic Point Cloud'),
    ('sample4_3_road_points.png',    r'(c) Road Point Filtering'),
    ('sample4_4_delaunay.png',       r'(d) Delaunay Triangulation'),
    ('sample4_5_morphology.png',     r'(e) Morphological Closing'),
    ('sample4_6_smoothed.png',       r'(f) Contour Approximation'),
    ('sample4_7_final.png',          r'(g) Final Ground Truth'),
    ('sample4_8_final_vs_lidar.png', r'(h) GT vs Point Cloud'),
]

fig, axes = plt.subplots(2, 4, figsize=(6.3, 2.5))
for ax, (fname, title) in zip(axes.flat, panels):
    img = Image.open(os.path.join(SRC, fname)).convert('RGB')
    ax.imshow(img)
    ax.text(0.5, -0.08, title, transform=ax.transAxes, fontsize=7,
            ha='center', va='top')
    ax.axis('off')

plt.subplots_adjust(wspace=0.06, hspace=0.02)
out = os.path.join(BASE, 'gt_pipeline_EN')
fig.savefig(out + '.pdf')
fig.savefig(out + '.png', dpi=200)
print(f'Saved: {out}.{{pdf,png}}')
plt.close()
