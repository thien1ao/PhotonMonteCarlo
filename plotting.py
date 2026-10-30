import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


def detector_norm(images):
    nonzero = np.concatenate([img[img > 0] for img in images])
    return LogNorm(vmin=nonzero.min(), vmax=np.percentile(nonzero, 99.9), clip=True)


def show_detector(ax, image, norm, detector_size):
    cmap = plt.get_cmap("hot").copy()
    cmap.set_bad("black")
    a = detector_size / 2
    im = ax.imshow(np.ma.masked_equal(image, 0), cmap=cmap, norm=norm,
                   origin="lower", extent=[-a, a, -a, a], interpolation_stage="rgba")
    ax.set_xticks([-a, 0, a])
    ax.set_yticks([-a, 0, a])
    return im
