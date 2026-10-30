# Photon Monte Carlo

Monte Carlo simulation of light passing through a scattering slab. A narrow beam of
photons enters a slab of thickness `d`, photons are absorbed and scattered inside, and
the ones that come out of the bottom are recorded on a 2D detector.

![Transmitted photons for different slab thicknesses](assets/thickness_grid.png)

## How it works

Every photon starts at `(0, 0, 0)` moving straight down (`+z`) with weight `w = 1`.
Then it repeats:

1. **Step.** Sample a free path length `s ~ Exp(sigma_t)`, `sigma_t = sigma_a + sigma_s`.
2. **Exit check.** If `s` is longer than the distance to the slab boundary, the photon
   leaves the slab: through the bottom it counts as transmitted (**T**) and is recorded
   on the detector, through the top it counts as reflected (**Rd**).
3. **Absorption.** Otherwise the photon moves by `s` and loses part of its weight:
   `w *= sigma_s / sigma_t`.
4. **Russian roulette.** If `w < roulette_threshold`, the photon survives with
   probability `roulette_survival` (and its weight is divided by it), otherwise it dies.
   This ends the walk without biasing the result.
5. **Scattering.** A new direction is sampled from the Henyey–Greenstein phase
   function with anisotropy `g` (`g > 0` scatters mostly forward).

All photons are traced at the same time as numpy arrays (one array element = one
photon), so 100 000 photons take a fraction of a second.

## Requirements

- Python 3.7+ (tested with 3.12)
- numpy
- matplotlib 3.5+ (tested with 3.6)

```bash
pip install numpy matplotlib
```

## Usage

Run from the project root. Images are saved to `assets/`.

```bash
python3 plot_thickness.py   # one detector image per slab thickness
python3 plot_passes.py      # progressive refinement at one thickness
```

### Using the simulation directly

```python
import numpy as np
from config import Config
from particle import simulate

result = simulate(1.0, Config(), np.random.default_rng())
result.grid            # detector image, shape (height, width)
result.transmittance   # T, fraction of photon weight leaving through the bottom
result.reflectance     # Rd, fraction leaving through the top
```

## Progressive refinement

`plot_passes.py` runs the simulation many times for the same thickness and averages
the detector images. Each pass adds new photons, so the noise drops as
`1 / sqrt(passes)`: 16 passes have 4x less noise than one.

![Progressive refinement](assets/passes_grid.png)

## Configuration

All settings are in `config.py`, grouped into dataclasses:

| class | used by | settings |
|---|---|---|
| `Config` | `simulate()` | physics: `photons`, detector `width` / `height` / `detector_size`, `sigma_a`, `sigma_s`, `g`, `roulette_threshold`, `roulette_survival` |
| `PlotConfig` | `plotting.py` | `cmap`, `empty_color`, `vmax_percentile`, `log_scale`, `ticks`, `panel_size`, `dpi`, `output_dir`, `colorbar_label` |
| `ThicknessStudy` | `plot_thickness.py` | `d_min`, `d_max`, `steps`, `cols`, `filename` |
| `PassesStudy` | `plot_passes.py` | `thickness`, `npasses`, `snapshot_at`, `filename` |

Change the defaults in `config.py`, or override them in a script:

```python
plot = PlotConfig(cmap="viridis", dpi=200)
study = ThicknessStudy(d_max=5.0, steps=12, cols=4)
```

### Why a log colour scale

A fraction exp(-sigma_t * d) of the photons never collide (82 % at d = 0.1 with
the defaults). They pass straight through
and all land in the centre cell, which is thousands of times brighter than the
scattered halo. With a linear scale only that single pixel is visible. The plots
therefore use a log scale (`log_scale = True`) whose top is the 99.9th percentile of
the non-empty cells (`vmax_percentile`), so the centre just saturates to white.

## Results

With the default parameters (`sigma_a = sigma_s = 1`, `g = 0.75`, 100 000 photons):

| d | T (transmitted) | Rd (reflected) |
|---|---|---|
| 0.0 | 1.000 | 0.000 |
| 0.1 | 0.897 | 0.005 |
| 1.0 | 0.305 | 0.018 |
| 2.0 | 0.084 | 0.019 |

Values vary by about ±0.001 between runs (Monte Carlo noise).

## Files

| file | purpose |
|---|---|
| `particle.py` | the simulation: `simulate()`, scattering, boundaries, detector |
| `config.py` | all settings, and the `Result` returned by `simulate()` |
| `plotting.py` | shared plotting helpers (colour scale, detector image, subplot grid, saving) |
| `plot_thickness.py` | detector images for a range of thicknesses |
| `plot_passes.py` | progressive refinement at a single thickness |
