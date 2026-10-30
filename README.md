# Photon Monte Carlo

Monte Carlo simulation of photon transport through a homogeneous scattering slab.

A narrow beam of photons enters a slab with thickness \(d\). As photons travel through the material, they undergo absorption and scattering. Photons leaving through the bottom surface are recorded on a two-dimensional detector, while photons leaving through the top surface contribute to the reflectance.

The simulation is based on the Monte Carlo approach to light transport described in [Scratchapixel – Monte Carlo Simulation](https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/monte-carlo-methods-in-practice/monte-carlo-simulation.html).

![Transmitted photons for different slab thicknesses](assets/thickness_grid.png)

## Usage

```bash
git clone <repository-url>
cd photon-monte-carlo
```

Generates detector images for different slab thicknesses.

```bash
python3 plot_passes.py
```

Shows progressive refinement of the detector image at a fixed slab thickness.

### Using the simulation directly

The simulation can also be imported and used independently:

```python
import numpy as np
from config import Config
from particle import simulate

settings = Config()

result = simulate(
    1.0,
    settings,
    np.random.default_rng()
)

result.grid            # detector image, shape (height, width)
result.transmittance   # T, fraction of photon weight leaving through the bottom
result.reflectance     # Rd, fraction of photon weight leaving through the top
```

## Progressive refinement

`plot_passes.py` runs the simulation multiple times for the same slab thickness and averages the resulting detector images.

Each pass uses a new set of randomly sampled photon paths. The accumulated image is averaged over the number of passes:

\[
I_{\mathrm{average}} =
\frac{1}{M}\sum_{k=1}^{M} I_k
\]

where \(M\) is the number of independent simulation passes.

The statistical noise decreases approximately as:

\[
\frac{1}{\sqrt{M}}
\]

For example, 16 independent passes produce approximately four times less statistical noise than one pass, assuming the same number of photons per pass.

![Progressive refinement](assets/passes_grid.png)

## Configuration

Simulation parameters are defined in the `Config` dataclass in `config.py`.

| Parameter | Default | Description |
|---|---:|---|
| `photons` | 100000 | Number of photon packets per simulation |
| `width` | 512 | Detector width in pixels |
| `height` | 512 | Detector height in pixels |
| `sigma_a` | 1.0 | Absorption coefficient |
| `sigma_s` | 1.0 | Scattering coefficient |
| `anisotropy` | 0.75 | Scattering anisotropy, -1 < g < 1 |
| `detector_size` | 1.0 | Physical width and height of the square detector |
| `roulette_threshold` | 0.001 | Weight below which Russian roulette starts |
| `roulette_survival` | 0.1 | Survival probability in Russian roulette |

The default values can be changed directly in `config.py` or overridden when creating a configuration object:

```python
settings = Config(
    photons=1_000_000,
    anisotropy=0.9,
    sigma_a=0.5,
    sigma_s=1.5
)
```

Slab thicknesses, the number of simulation passes, and snapshot settings are defined in `plot_thickness.py` and `plot_passes.py`.

## Why a logarithmic colour scale?

A fraction of the photons pass through the slab without experiencing any interaction.

The probability of no interaction over a distance \(d\) is:

\[
P_{\mathrm{no\ interaction}} = e^{-\sigma_t d}
\]

With the default parameters, \(\sigma_t = 2\), this probability is approximately 82% at \(d = 0.1\).

These photons maintain their initial direction and reach approximately the same central detector pixel. As a result, the central pixel can be much brighter than the surrounding scattered distribution.

A linear colour scale would make the weaker scattered contributions difficult to distinguish. Therefore, the detector images use a logarithmic colour scale. The upper limit is set to the 99.9th percentile of non-empty pixel values to make the scattered distribution visible while allowing the central pixel to saturate.

## Results

The following results were obtained using the default parameters:

- \(\sigma_a = 1.0\)
- \(\sigma_s = 1.0\)
- `anisotropy = 0.75`
- 100,000 photon packets

| Slab thickness \(d\) | Transmittance \(T\) | Reflectance \(R_d\) |
|---:|---:|---:|
| 0.0 | 1.000 | 0.000 |
| 0.1 | 0.897 | 0.005 |
| 1.0 | 0.305 | 0.018 |
| 2.0 | 0.084 | 0.019 |

The values are Monte Carlo estimates and may vary between simulation runs due to random sampling.

As the slab thickness increases, fewer photons reach the bottom surface. Photons also undergo more interactions on average, resulting in a broader spatial distribution of transmitted light.

The sum of reflectance and transmittance is generally less than one because part of the initial photon weight is absorbed inside the material.

## Reference

- [Scratchapixel – Monte Carlo Simulation](https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/monte-carlo-methods-in-practice/monte-carlo-simulation.html)
