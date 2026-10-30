import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize


def detector_norm(images, plot):
    nonzero = np.concatenate([img[img > 0] for img in images])
    vmax = np.percentile(nonzero, plot.vmax_percentile)
    if plot.log_scale:
        return LogNorm(vmin=nonzero.min(), vmax=vmax, clip=True)
    return Normalize(vmin=0, vmax=vmax, clip=True)


def show_detector(ax, image, norm, detector_size, plot):
    cmap = plt.get_cmap(plot.cmap).copy()
    cmap.set_bad(plot.empty_color)
    a = detector_size / 2
    im = ax.imshow(np.ma.masked_equal(image, 0), cmap=cmap, norm=norm,
                   origin="lower", extent=[-a, a, -a, a], interpolation_stage="rgba")
    ax.set_xticks(np.linspace(-a, a, plot.ticks))
    ax.set_yticks(np.linspace(-a, a, plot.ticks))
    return im


def make_grid(n, cols, plot):
    """Figure with n subplots in a grid of `cols` columns; unused cells hidden."""
    rows = -(-n // cols)  # ceil(n / cols)
    fig, axes = plt.subplots(rows, cols, squeeze=False, constrained_layout=True,
                             figsize=(plot.panel_size * cols, (plot.panel_size + 0.2) * rows))
    for ax in axes.flat[n:]:
        ax.set_visible(False)
    return fig, axes


def save(fig, filename, plot):
    os.makedirs(plot.output_dir, exist_ok=True)
    path = os.path.join(plot.output_dir, filename)
    fig.savefig(path, dpi=plot.dpi)
    print("saved", path)
