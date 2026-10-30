# Monte Carlo Simulation of Photon Transport

This project implements the algorithm from the Scratchapixel lesson [Monte Carlo Simulation](https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/monte-carlo-methods-in-practice/monte-carlo-simulation.html) (part of *Monte Carlo Methods in Practice*), rewritten in Python with NumPy.

![Transmitted photons for different slab thicknesses](assets/thickness_grid.png)

## 📋 What was done

1. **Implemented the lesson's algorithm**: free path sampling, photon weights, Russian roulette, Henyey–Greenstein scattering (see [Algorithm](#algorithm)).
2. **Reimplemented in Python using NumPy arrays** Instead of a loop over photons, all photons are traced simultaneously using NumPy arrays. Photons that escape the slab are terminated by Russian roulette.
3. **Reproduced the lesson's experiments:**
   - spatial distribution of transmitted photon weights,
   - increasing values of $d$ (the thickness of the slab) from $0$ to $2$ (`plot_thickness.py`),
   - multiple simulation passes: averaging the results of Monte Carlo approximations (`plot_passes.py`).

## ⚙️ Algorithm

Every photon packet starts at $(0, 0, 0)$ on the top surface and moves along $+z$, which points down into the slab (the top surface is at $z = 0$, the bottom at $z = d$). Its initial weight is $w = 1$. It then repeats the following steps until it leaves the slab or is killed.

**1. Free path:** Sample distance to the next interaction using Beer–Lambert law , $p(s) = \sigma_t e^{-\sigma_t s}$ with $\sigma_t = \sigma_a + \sigma_s$:

$$s = -\frac{\ln \xi}{\sigma_t}, \qquad \xi \sim U(0, 1)$$

**2. Boundary test:** Determine whether the photon reaches the slab boundary before its next interaction:

$$s_b = \frac{d - z}{\mu_z} \ \text{ if } \mu_z > 0, \qquad s_b = -\frac{z}{\mu_z} \ \text{ if } \mu_z < 0$$

**3. Absorption:** Account for absorption using implicit capture:

$$w \leftarrow w\frac{\sigma_a}{\sigma_t}$$

**4. Russian roulette.** Terminate low-weight photons probabilistically.

**5. Scattering:** Sample a new direction using the Henyey–Greenstein phase function with anisotropy $g$:

$$
\cos\theta =
\begin{cases}
\displaystyle
\frac{1}{2g}
\left[
1+g^2-
\left(
\frac{1-g^2}{1-g+2g\xi}
\right)^2
\right], & g \neq 0, \\[1.2em]
2\xi-1, & g=0.
\end{cases}
$$

The formulas for each coordinate of the new direction vector are as follows:

$$\mu'_x = \mu_x\cos\theta + \frac{\sin\theta\(\mu_x\mu_z\cos\phi - \mu_y\sin\phi)}{\sqrt{1 - \mu_z^2}}$$

$$\mu'_y = \mu_y\cos\theta + \frac{\sin\theta\(\mu_y\mu_z\cos\phi + \mu_x\sin\phi)}{\sqrt{1 - \mu_z^2}}$$

$$\mu'_z = \mu_z\cos\theta - \sqrt{1 - \mu_z^2}\ \sin\theta\cos\phi$$

**6. Repeat:** Continue until all photons have escaped or been terminated.

:exclamation:
The equations above are intended as a brief overview of the mathematical concepts. For a more detailed explanation and derivation, please refer to the [original lesson](https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/monte-carlo-methods-in-practice/monte-carlo-simulation.html).


## 🛠️ Installation

```bash
git clone https://github.com/thien1ao/PhotonMonteCarlo.git
cd PhotonMonteCarlo
```

### pip

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install numpy matplotlib
```

### conda

```bash
conda create -y -n photon-mc python numpy matplotlib
conda activate photon-mc
```

## 🚀 Usage

```bash
python3 plot_thickness.py
python3 plot_passes.py
```
Generated plots are saved in the `assets/` directory with corresponding filenames:
 - `assets/thickness_grid.png`
 - `assets/passes_grid.png`

## ⚙️ Configuration

| Parameter | Default | Description |
|---|---:|---|
| `photons` | 100000 | Number of photon packets per simulation |
| `width` | 512 | Detector width in pixels |
| `height` | 512 | Detector height in pixels |
| `sigma_a` | 1.0 | Absorption coefficient $\sigma_a$ |
| `sigma_s` | 1.0 | Scattering coefficient $\sigma_s$ |
| `g` | 0.75 | Scattering anisotropy, $-1 < g < 1$ ($0$ = isotropic) |
| `detector_size` | 1.0 | Physical width and height of the detector |
| `roulette_threshold` | 0.001 | Photon weight threshold below which Russian roulette is applied |
| `roulette_survival` | 0.1 | Survival probability in Russian roulette |



## Multiple Simulation Passes

As discussed in the lesson, a single simulation of $N$ photons is generally insufficient to produce visually smooth, low-noise results. To reduce statistical noise, the simulation can be repeated multiple times using independent random photon paths. The resulting detector images are then averaged:

$$I_{\text{average}} = \frac{1}{M}\sum_{k=1}^{M} I_k$$

The standard deviation of statistical noise decreases as $\frac{1}{M}$. For example, averaging 16 independent passes reduces the noise by a factor of 4 compared to a single pass with the same number of photons.

![Progressive refinement](assets/passes_grid.png)

## Why a logarithmic colour scale?

The lesson notes that the detector values may need to be scaled to be visible. The reason is the photons that cross the slab without any interaction. By the Beer–Lambert law their fraction is

$$P_{\text{no interaction}} = e^{-\sigma_t d}$$

With the default parameters ($\sigma_t = 2$) this is about 82 % at $d = 0.1$. These photons keep their initial direction and all land in the central detector pixel, which is therefore thousands of times brighter than the scattered halo around it.

On a linear colour scale only that single pixel would be visible. The detector images therefore use a logarithmic colour scale, with the upper limit at the 99.9th percentile of the non-empty pixel values: the scattered distribution becomes visible and the central pixel simply saturates.

## Results

| Slab thickness $d$ | Transmittance $T$ | Reflectance $R_d$ | Absorbed $1 - T - R_d$ |
|---:|---:|---:|---:|
| 0.0 | 1.000 | 0.000 | 0.000 |
| 0.1 | 0.897 | 0.005 | 0.098 |
| 1.0 | 0.305 | 0.018 | 0.677 |
| 2.0 | 0.084 | 0.019 | 0.897 |
