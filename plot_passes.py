import numpy as np

from config import Config, PlotConfig, PassesStudy
from particle import simulate
from plotting import detector_norm, show_detector, make_grid, save

config = Config()
plot = PlotConfig()
study = PassesStudy()
rng = np.random.default_rng()

records = np.zeros((config.height, config.width))
snapshots = {}
for p in range(1, study.npasses + 1):
    r = simulate(study.thickness, config, rng)
    records += r.grid
    if p in study.snapshot_at:
        snapshots[p] = records / p

norm = detector_norm([snapshots[min(snapshots)]], plot)
fig, axes = make_grid(len(snapshots), len(snapshots), plot)
for ax, (p, img) in zip(axes.flat, snapshots.items()):
    im = show_detector(ax, img, norm, config.detector_size, plot)
    ax.set_title(f"{p} passes ({p * config.photons:,} photons)")
fig.colorbar(im, ax=axes, shrink=0.8, label=plot.colorbar_label)
fig.suptitle(f"Progressive refinement, d = {study.thickness}")
save(fig, study.filename, plot)
