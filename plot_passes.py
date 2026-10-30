import os

import numpy as np
import matplotlib.pyplot as plt

from config import Config
from particle import simulate
from plotting import detector_norm, show_detector

thickness = 1.0
npasses = 16
snapshot_at = [1, 2, 4, 8, 16]

config = Config()
rng = np.random.default_rng()
os.makedirs("assets", exist_ok=True)

records = np.zeros((config.height, config.width))
T_sum = Rd_sum = 0.0
snapshots = {}
T_mean, Rd_mean = [], []

for p in range(1, npasses + 1):
    r = simulate(thickness, config, rng)
    records += r.grid
    T_sum += r.transmittance
    Rd_sum += r.reflectance
    T_mean.append(T_sum / p)
    Rd_mean.append(Rd_sum / p)
    print(f"pass {p:2d}: T = {T_mean[-1]:.4f}  Rd = {Rd_mean[-1]:.4f}")
    if p in snapshot_at:
        snapshots[p] = records / p

norm = detector_norm([snapshots[snapshot_at[0]]])

fig, axes = plt.subplots(1, len(snapshots), figsize=(4 * len(snapshots), 4.6), constrained_layout=True)
for ax, (p, img) in zip(axes, snapshots.items()):
    im = show_detector(ax, img, norm, config.detector_size)
    ax.set_title(f"{p} passes ({p * config.photons:,} photons)")

fig.colorbar(im, ax=axes, shrink=0.8, label="photon weight")
fig.savefig("assets/passes_grid.png", dpi=100)
print("saved assets/passes_grid.png")

