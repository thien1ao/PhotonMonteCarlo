import numpy as np

from config import Config, PlotConfig, ThicknessStudy
from particle import simulate
from plotting import detector_norm, show_detector, make_grid, save

config = Config()
plot = PlotConfig()
study = ThicknessStudy()
rng = np.random.default_rng()

thicknesses = study.thicknesses()
results = []
for d in thicknesses:
    r = simulate(d, config, rng)
    print(f"d = {d:.2f}  Rd = {r.reflectance:.4f}  T = {r.transmittance:.4f}")
    results.append(r)

norm = detector_norm([r.grid for r in results], plot)
fig, axes = make_grid(len(results), study.cols, plot)
for ax, d, r in zip(axes.flat, thicknesses, results):
    im = show_detector(ax, r.grid, norm, config.detector_size, plot)
    ax.set_title(f"d = {d:.2f}")
fig.colorbar(im, ax=axes, shrink=0.6, label=plot.colorbar_label)
fig.suptitle(f"Transmitted photons on the detector ({config.photons:,} photons per thickness)")
save(fig, study.filename, plot)
