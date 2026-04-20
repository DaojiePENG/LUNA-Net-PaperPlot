import matplotlib; matplotlib.use('pgf')
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.gridspec as gridspec
import numpy as np

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
    'font.size': 10,
    'figure.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
})

DATA = '/home/admin1/Mycode/Master_Thesis/A_My_master_thesis/figures/ch3/gen_scripts/fig_nuscenes_qual'
OUT = '/home/admin1/Mycode/Master_Thesis/A_My_master_thesis/figures/ch3/LUNA-Net-paper/nuscenes_qual_source'

DATA = DATA + '/previews'
SAMPLES = [0, 1, 2, 3, 4]
COL_LABELS = [
    r'(a) RGB Input',
    r'(b) LUNA-Net',
    r'(c) GT',
    r'(d) Error Map',
]

GREEN = np.array([0, 200, 0], dtype=np.uint8)   # TP
RED   = np.array([220, 50, 50], dtype=np.uint8)  # FP
BLUE  = np.array([60, 60, 220], dtype=np.uint8)  # FN
ALPHA = 0.45


def overlay_mask(rgb, mask, color=GREEN, alpha=ALPHA):
    """Overlay binary mask on RGB image with semi-transparent color."""
    out = rgb.copy()
    roi = mask > 0
    out[roi] = (rgb[roi].astype(np.float32) * (1 - alpha)
                + color.astype(np.float32) * alpha).astype(np.uint8)
    return out


def error_map(rgb, pred, gt_bin):
    """TP=green, FP=red, FN=blue on original RGB."""
    out = rgb.copy().astype(np.float32)
    tp = (pred == 1) & (gt_bin == 1)
    fp = (pred == 1) & (gt_bin == 0)
    fn = (pred == 0) & (gt_bin == 1)
    alpha = 0.55
    for mask, color in [(tp, GREEN), (fp, RED), (fn, BLUE)]:
        out[mask] = out[mask] * (1 - alpha) + color.astype(np.float32) * alpha
    return out.astype(np.uint8)


def calc_metrics(pred, gt_bin):
    tp = ((pred == 1) & (gt_bin == 1)).sum()
    fp = ((pred == 1) & (gt_bin == 0)).sum()
    fn = ((pred == 0) & (gt_bin == 1)).sum()
    iou = tp / (tp + fp + fn + 1e-8)
    f1 = 2 * tp / (2 * tp + fp + fn + 1e-8)
    return f1, iou


def load_sample(idx):
    d = np.load(f'{DATA}/sample_{idx:02d}.npz')
    return d['rgb'], d['pred'], d['gt']


# --- Build figure ---
nrows, ncols = len(SAMPLES), len(COL_LABELS)
fig = plt.figure(figsize=(6.3, 6.3 * nrows / ncols * 0.52))
gs = gridspec.GridSpec(nrows, ncols, wspace=0.03, hspace=0.06,
                       left=0.03, right=1, top=0.96, bottom=0)

for r, si in enumerate(SAMPLES):
    rgb, pred, gt = load_sample(si)
    gt_bin = (gt > 0).astype(np.uint8)
    f1, iou = calc_metrics(pred, gt_bin)
    imgs = [
        rgb,
        overlay_mask(rgb, pred, GREEN),
        overlay_mask(rgb, gt_bin, GREEN),
        error_map(rgb, pred, gt_bin),
    ]
    for c, img in enumerate(imgs):
        ax = fig.add_subplot(gs[r, c])
        ax.imshow(img)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_linewidth(0.3)
        if r == 0:
            ax.set_title(COL_LABELS[c], fontsize=10, pad=3)
        # Row label on leftmost column (black color)
        if c == 0:
            ax.text(-0.06, 0.5, r'(' + str(r+1) + r')',
                    transform=ax.transAxes, fontsize=9,
                    ha='center', va='center', rotation=0)
        # Metrics on error map column — top right
        if c == 3:
            ax.text(0.98, 0.96,
                    f'F1={f1:.3f}\nIoU={iou:.3f}',
                    transform=ax.transAxes, fontsize=7.5,
                    color='white', ha='right', va='top',
                    bbox=dict(facecolor='black', alpha=0.6,
                              edgecolor='none', pad=1.5))
            # TP/FP/FN legend — top left (only on first row)
            if r == 0:
                legend_txt = (r'\textcolor[rgb]{0,0.78,0}{\rule{6pt}{6pt}}\,TP  '
                              r'\textcolor[rgb]{0.86,0.2,0.2}{\rule{6pt}{6pt}}\,FP  '
                              r'\textcolor[rgb]{0.24,0.24,0.86}{\rule{6pt}{6pt}}\,FN')
                ax.text(0.02, 0.96, legend_txt,
                        transform=ax.transAxes, fontsize=7,
                        color='white', ha='left', va='top',
                        bbox=dict(facecolor='black', alpha=0.6,
                                  edgecolor='none', pad=1.5))

fig.savefig(f'{OUT}/Fig.3-10_nuscenes_qual_EN.pdf')
fig.savefig(f'{OUT}/Fig.3-10_nuscenes_qual_EN.png', dpi=300)
print('nuScenes qualitative figure (English) done')
plt.close(fig)
