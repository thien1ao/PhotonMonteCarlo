import os

import numpy as np
import matplotlib.pyplot as plt

from config import Config
from particle import simulate
from plotting import detector_norm, show_detector

thicknesses = np.linspace(0.0, 2.0, 21)
rows, cols = 3, 7

config = Config()
rng = np.random.default_rng()
os.makedirs("assets", exist_ok=True)

results = []
for d in thicknesses:
    r = simulate(d, config, rng)
    print(f"d = {d:.2f}  Rd = {r.reflectance:.4f}  T = {r.transmittance:.4f}")
    results.append(r)

norm = detector_norm([r.grid for r in results])
fig, axes = plt.subplots(rows, cols, figsize=(3 * cols, 3.2 * rows), constrained_layout=True)
for ax, d, r in zip(axes.flat, thicknesses, results):
    im = show_detector(ax, r.grid, norm, config.detector_size)
    ax.set_title(f"d = {d:.2f}")
fig.colorbar(im, ax=axes, shrink=0.6, label="photon weight")
fig.suptitle(f"Transmitted photons on the detector ({config.photons:,} photons per thickness)")
fig.savefig("assets/thickness_grid.png", dpi=100)
print("saved assets/thickness_grid.png")
