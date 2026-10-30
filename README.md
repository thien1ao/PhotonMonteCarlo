# Photon Monte Carlo

A vectorized Monte Carlo simulation of photon transport through a homogeneous scattering slab.

A narrow beam of photons enters a slab at normal incidence. Photons can be absorbed, scattered, reflected, or transmitted. The simulation estimates the spatial distribution of transmitted light on a detector and calculates the total reflectance and transmittance.

## Physical Model

The slab occupies the region:

$$
0 \leq z \leq d
$$

where $d$ is the slab thickness.

Each photon starts at the origin:

$$
\mathbf{r}_0 = (0,0,0)
$$

with initial direction:

$$
\mathbf{u}_0 = (0,0,1)
$$

and weight:

$$
w_0 = 1
$$

The simulation follows each photon until it leaves the slab or its contribution becomes negligible.

### 1. Sampling the free path

The distance a photon travels before its next interaction is sampled from an exponential distribution:

$$
p(s) = \sigma_t e^{-\sigma_t s}
$$

where the total interaction coefficient is:

$$
\sigma_t = \sigma_a + \sigma_s
$$

Here:

- $\sigma_a$ — absorption coefficient
- $\sigma_s$ — scattering coefficient
- $\sigma_t$ — total interaction coefficient

Using inverse transform sampling, the free path is calculated as:

$$
s = -\frac{\ln(\xi)}{\sigma_t}
$$

where $\xi$ is a uniformly distributed random number in the interval $(0,1)$.

### 2. Boundary intersection

After sampling the free path, the simulation checks whether the photon reaches a slab boundary before its next interaction.

The photon exits through:

- The bottom boundary ($z=d$): transmitted photon.
- The top boundary ($z=0$): reflected photon.

Photons that leave through the bottom boundary can contribute to the detector image.

### 3. Absorption: implicit capture

Instead of randomly deciding whether a photon is absorbed, the simulation reduces its weight after each interaction.

The weight is updated according to:

$$
w_{\text{new}} =
w_{\text{old}}
\frac{\sigma_s}{\sigma_t}
$$

The remaining fraction represents the absorbed contribution.

This technique is known as **implicit capture**. It reduces statistical noise compared with explicitly sampling absorption events.

### 4. Russian roulette

As photons undergo repeated interactions, their weights decrease.

To avoid spending computational resources on photons with very small weights, Russian roulette is applied when:

$$
w < w_{\text{threshold}}
$$

A photon survives with probability $p$:

$$
P(\text{survival}) = p
$$

If it survives, its weight is increased:

$$
w_{\text{new}} = \frac{w_{\text{old}}}{p}
$$

Otherwise, the photon is terminated.

This preserves the expected photon weight and therefore does not introduce bias into the estimator.

### 5. Scattering direction

After an interaction, the photon receives a new direction sampled from the Henyey–Greenstein phase function:

$$
p(\cos\theta) =
\frac{1-g^2}
{2(1+g^2-2g\cos\theta)^{3/2}}
$$

where $g$ is the anisotropy parameter.

Its interpretation:

- $g=0$: isotropic scattering.
- $g>0$: preferential forward scattering.
- $g<0$: preferential backward scattering.

The parameter must satisfy:

$$
-1 < g < 1
$$

## Implementation

The simulation is implemented in Python using NumPy.

Instead of processing photons individually, the implementation stores photon positions, directions, and weights in NumPy arrays. Operations such as free-path sampling, boundary checks, weight updates, and scattering are performed on entire photon arrays.

This vectorized approach significantly reduces Python-level loop overhead.

### Project structure

```text
.
├── config.py
├── particle.py
├── plot_thickness.py
├── plot_passes.py
└── assets/
    ├── thickness_grid.png
    └── passes_grid.png
```

## Requirements

- Python 3.7+
- NumPy
- Matplotlib

Install the dependencies:

```bash
pip install numpy matplotlib
```

## Usage

Run the thickness comparison:

```bash
python3 plot_thickness.py
```

Run the progressive refinement comparison:

```bash
python3 plot_passes.py
```

### Direct simulation

The simulation can also be called directly:

```python
import numpy as np

from config import Config
from particle import simulate

settings = Config()

result = simulate(
    thickness=1.0,
    settings=settings,
    rng=np.random.default_rng()
)

detector_image = result.grid
transmittance = result.transmittance
reflectance = result.reflectance
```

## Configuration

Simulation parameters can be adjusted in `config.py`.

| Parameter | Description |
|---|---|
| `photons` | Number of simulated photons |
| `width` | Detector image width in pixels |
| `height` | Detector image height in pixels |
| `sigma_a` | Absorption coefficient |
| `sigma_s` | Scattering coefficient |
| `anisotropy` | Henyey–Greenstein anisotropy parameter $g$ |
| `detector_size` | Physical size of the detector |
| `roulette_threshold` | Weight threshold for Russian roulette |
| `roulette_survival` | Survival probability in Russian roulette |

## Results

The simulation produces three main outputs:

- **Detector image:** spatial distribution of transmitted photon weight.
- **Transmittance:** fraction of initial photon weight transmitted through the slab.
- **Reflectance:** fraction of initial photon weight reflected from the slab.

The transmittance and reflectance are normalized by the initial number of photons:

$$
T = \frac{N_{\text{transmitted}}}{N_{\text{initial}}}
$$

$$
R = \frac{N_{\text{reflected}}}{N_{\text{initial}}}
$$

The detector image is normalized in the same way, so its pixel values represent transmitted photon weight per initial photon.

### Progressive refinement

The progressive refinement experiment averages independent simulation runs.

For independent Monte Carlo samples, the statistical uncertainty approximately scales as:

$$
\sigma \propto \frac{1}{\sqrt{N}}
$$

Therefore, increasing the number of independent runs reduces statistical noise. For example, averaging 16 independent runs gives approximately four times lower standard error than a single run with the same number of photons.

## Example results

The following values illustrate the behavior of the simulation for different slab thicknesses using the default configuration.

| Thickness $d$ | Transmittance $T$ | Reflectance $R$ |
|---:|---:|---:|
| 0.0 | 1.000 | 0.000 |
| 0.1 | 0.897 | 0.005 |
| 1.0 | 0.305 | 0.018 |
| 2.0 | 0.084 | 0.019 |

Monte Carlo results may vary slightly between runs because of random sampling.

## Visualization

### Different slab thicknesses

![Photon distribution for different slab thicknesses](assets/thickness_grid.png)

### Progressive refinement

![Progressive refinement of the detector image](assets/passes_grid.png)

## References

- [Scratchapixel — Monte Carlo Simulation](https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/monte-carlo-methods-in-practice/monte-carlo-simulation.html)
- [GitHub Docs — Writing mathematical expressions](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions)
