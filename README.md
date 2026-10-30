# Photon Monte Carlo

Monte Carlo simulation of photon transport through a homogeneous scattering slab.

A narrow beam of photons enters a slab with thickness \(d\). As photons travel through the material, they undergo absorption and scattering. Photons leaving through the bottom surface are recorded on a two-dimensional detector, while photons leaving through the top surface contribute to the reflectance.

The simulation is based on the Monte Carlo approach to light transport described in [Scratchapixel – Monte Carlo Simulation](https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/monte-carlo-methods-in-practice/monte-carlo-simulation.html).

![Transmitted photons for different slab thicknesses](assets/thickness_grid.png)

## How it works

Every photon starts at position `(0, 0, 0)`, moving straight down along the positive z-axis, with an initial weight `w = 1`.

The simulation repeats the following steps for each active photon:

1. **Free path sampling.** Sample the distance to the next interaction from an exponential distribution:

   \[
   s = -\frac{\ln(\xi)}{\sigma_t},
   \qquad
   \sigma_t = \sigma_a + \sigma_s
   \]

   where \(\xi\) is a uniformly distributed random number between 0 and 1.

2. **Boundary check.** Calculate the distance to the next slab boundary. If the sampled free path is longer than this distance, the photon leaves the slab before its next interaction. Photons leaving through the bottom contribute to the transmittance (**T**) and are recorded on the detector. Photons leaving through the top contribute to the reflectance (**Rd**).

3. **Absorption.** If the photon does not reach a boundary, it moves to the next interaction point. Its weight is reduced according to the scattering probability:

   \[
   w \leftarrow w \frac{\sigma_s}{\sigma_t}
   \]

   This is an implicit capture approach: the absorbed fraction of the photon weight is removed, while the remaining fraction continues to propagate.

4. **Russian roulette.** If the photon weight falls below `roulette_threshold`, the photon survives with probability `roulette_survival`. Surviving photons have their weights divided by the survival probability; otherwise, they are terminated. This reduces computational effort while preserving an unbiased estimate.

5. **Scattering.** The photon direction is updated by sampling a new scattering angle from the Henyey–Greenstein phase function. The parameter `anisotropy` controls the preferred scattering direction: positive values favour forward scattering, negative values favour backward scattering, and zero corresponds to isotropic scattering.

All photons are simulated simultaneously using vectorized NumPy arrays. Each array element represents one photon packet. This avoids explicit Python loops over individual photons and improves computational efficiency.

## Theoretical Background

The simulation uses the Monte Carlo method to model the probabilistic nature of photon transport.

The total interaction coefficient is defined as:

\[
\sigma_t = \sigma_a + \sigma_s
\]

where:

- \(\sigma_a\) is the absorption coefficient.
- \(\sigma_s\) is the scattering coefficient.
- \(\sigma_t\) is the total interaction coefficient.

The probability density of the distance \(s\) to the next interaction is:

\[
p(s) = \sigma_t e^{-\sigma_t s}
\]

The free path is sampled using inverse transform sampling:

\[
s = -\frac{\ln(\xi)}{\sigma_t}
\]

For scattering, the simulation uses the Henyey–Greenstein phase function:

\[
p(\cos\theta) =
\frac{1-g^2}
{2(1+g^2-2g\cos\theta)^{3/2}}
\]

where \(g\) is the anisotropy parameter, represented by `anisotropy` in the implementation.

The theoretical principles of Monte Carlo sampling and photon transport are based on:

[Scratchapixel – Monte Carlo Simulation](https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/monte-carlo-methods-in-practice/monte-carlo-simulation.html)

## Requirements

- Python 3.7+
- NumPy
- Matplotlib 3.5+

Install the dependencies:

```bash
pip install numpy matplotlib
```

## Usage

Run the scripts from the project root. Generated images are saved in the `assets/` directory.

```bash
python3 plot_thickness.py
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
