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
    'font.size': 8,
    'figure.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
})

DATA = '/home/admin1/Mycode/Master_Thesis/A_My_master_thesis/figures/ch3/LUNA-Net-paper/carla_qual_source'
OUT = DATA

WEATHERS = ['ClearDay', 'ClearNight', 'HeavyFoggyNight', 'HeavyRainFoggyNight']
COL_LABELS = ['(1) Clear Day', '(2) Clear Night', '(3) Heavy Foggy Night', '(4) Heavy Rain Foggy Night']

ROW_LABELS = [
    r'(a) RGB Input',
    r'(b) LUNA-Net',
    r'(c) GT',
    r'(d) Error Map',
]

GREEN = np.array([0, 200, 0], dtype=np.uint8)
RED   = np.array([220, 50, 50], dtype=np.uint8)
BLUE  = np.array([60, 60, 220], dtype=np.uint8)
ALPHA = 0.45


def overlay_mask(rgb, mask, color=GREEN, alpha=ALPHA):
    out = rgb.copy()
    roi = mask > 0
    out[roi] = (rgb[roi].astype(np.float32) * (1 - alpha)
                + color.astype(np.float32) * alpha).astype(np.uint8)
    return out


def error_map(rgb, pred, gt_bin):
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


def load_weather(weather):
    d = np.load(f'{DATA}/carla_{weather}.npz')
    return d['rgb'], d['pred'], d['gt']


# --- Build figure ---
# 4 cols (weathers) x 4 rows, with left margin reserved for row labels
ncols, nrows = len(WEATHERS), len(ROW_LABELS)
LEFT_MARGIN = 0.19          # images start here (fraction of figure width)
LABEL_X     = 0.07          # left-aligned label x position (increase to move right)
fig = plt.figure(figsize=(6.3, 6.3 * nrows / ncols * 0.42))
gs = gridspec.GridSpec(nrows, ncols, wspace=0.03, hspace=0.06,
                       left=LEFT_MARGIN, right=1, top=0.94, bottom=0.06)

# Store first-column axes to read their y-centers later
row_axes = [None] * nrows

for c, weather in enumerate(WEATHERS):
    rgb, pred, gt = load_weather(weather)
    gt_bin = (gt > 0).astype(np.uint8)
    f1, iou = calc_metrics(pred, gt_bin)
    imgs = [
        rgb,
        overlay_mask(rgb, pred, GREEN),
        overlay_mask(rgb, gt_bin, GREEN),
        error_map(rgb, pred, gt_bin),
    ]
    for r, img in enumerate(imgs):
        ax = fig.add_subplot(gs[r, c])
        ax.imshow(img)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_linewidth(0.3)
        if c == 0:
            row_axes[r] = ax
        if r == 0:
            ax.set_title(COL_LABELS[c], fontsize=7.5, pad=3)
        if r == 3:
            ax.text(0.98, 0.96,
                    f'F1={f1:.3f}\nIoU={iou:.3f}',
                    transform=ax.transAxes, fontsize=7.5,
                    color='white', ha='right', va='top',
                    bbox=dict(facecolor='black', alpha=0.5,
                              edgecolor='none', pad=1.2))
            if c == 0:
                legend_txt = (r'\textcolor[rgb]{0,0.78,0}{\rule{6pt}{6pt}}\,TP  '
                              r'\textcolor[rgb]{0.86,0.2,0.2}{\rule{6pt}{6pt}}\,FP  '
                              r'\textcolor[rgb]{0.24,0.24,0.86}{\rule{6pt}{6pt}}\,FN')
                ax.text(0.02, 0.96, legend_txt,
                        transform=ax.transAxes, fontsize=7,
                        color='white', ha='left', va='top',
                        bbox=dict(facecolor='black', alpha=0.6,
                                  edgecolor='none', pad=1.5))

# Place row labels in the left margin using fig.text (absolute figure coords)
fig.canvas.draw()  # force layout so get_position() returns final values
for r in range(nrows):
    pos = row_axes[r].get_position()
    y_center = (pos.y0 + pos.y1) / 2
    fig.text(LABEL_X, y_center, ROW_LABELS[r],
             fontsize=9, ha='left', va='center')

fig.savefig(f'{OUT}/Fig.3-11_CARLA_qual_EN.pdf')
fig.savefig(f'{OUT}/Fig.3-11_CARLA_qual_EN.png', dpi=300)
print('CARLA qualitative figure (English) done')
plt.close(fig)
