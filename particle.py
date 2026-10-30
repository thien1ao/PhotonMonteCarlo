import numpy as np
from config import Result

def sample_cos_theta(g, n, rng):
    ksi = rng.random(n)
    if g == 0:
        return 2.0 * ksi - 1.0
    ratio = (1.0 - g**2) / (1.0 - g + 2.0 * g * ksi)
    cos_theta = (1.0 + g**2 - ratio**2) / (2.0 * g)

    return np.clip(cos_theta, -1.0, 1.0)


def scatter(mu, g, rng):
    mu_x, mu_y, mu_z = mu[:, 0], mu[:, 1], mu[:, 2]
    n = mu.shape[0]

    cos_theta = sample_cos_theta(g, n, rng)
    sin_theta = np.sqrt(1.0 - cos_theta**2)
    phi = rng.uniform(0.0, 2.0 * np.pi, n)
    sin_phi = np.sin(phi)
    cos_phi = np.cos(phi)

    border = np.abs(mu_z) >= 1.0 - 1e-12
    regular = ~border

    mu_new = np.empty_like(mu, dtype=float)

    mx = mu_x[regular]
    my = mu_y[regular]
    mz = mu_z[regular]

    ct = cos_theta[regular]
    st = sin_theta[regular]
    cp = cos_phi[regular]
    sp = sin_phi[regular]

    denom = np.sqrt(1.0 - mz**2)
    mz_cos_phi = mz * cp

    mu_new[regular, 0] = (
        st * (mx * mz_cos_phi - my * sp) / denom
        + mx * ct
    )

    mu_new[regular, 1] = (
        st * (my * mz_cos_phi + mx * sp) / denom
        + my * ct
    )

    mu_new[regular, 2] = (
        -denom * st * cp
        + mz * ct
    )

    sign = np.sign(mu_z[border])

    mu_new[border, 0] = sin_theta[border] * cos_phi[border]
    mu_new[border, 1] = sign * sin_theta[border] * sin_phi[border]
    mu_new[border, 2] = sign * cos_theta[border]

    return mu_new

def distance_to_boundary(p, mu, thickness):
    z = p[:, 2]
    mu_z = mu[:, 2]

    dist = np.full(len(p), np.inf)
    forward = mu_z > 0.0
    backward = mu_z < 0.0

    dist[forward] = (thickness - z[forward]) / mu_z[forward]
    dist[backward] = -z[backward] / mu_z[backward]

    return dist

def record_detector(image, positions, weights, detector_size):
    height, width = image.shape

    pixel_positions = np.floor((positions[:, :2] / detector_size + 0.5) * [width, height]).astype(int)
    valid = np.all((pixel_positions >= 0) & (pixel_positions < [width, height]), axis=1)

    np.add.at(image, (pixel_positions[valid, 1], pixel_positions[valid, 0]), weights[valid])

def simulate(thickness, config, rng):
    if thickness < 0:
        raise ValueError("Thickness must be nonnegative")

    if config.photons <= 0:
        raise ValueError("Photon count must be positive")

    if not -1.0 < config.g < 1.0:
        raise ValueError("Anisotropy must lie between -1 and 1")

    if config.sigma_a < 0 or config.sigma_s < 0:
        raise ValueError("Coefficients must be nonnegative")

    if config.detector_size <= 0:
        raise ValueError("Detector size must be positive.")

    if not 0.0 < config.roulette_survival <= 1.0:
        raise ValueError("Roulette survival must be in (0, 1]")

    sigma_t = config.sigma_s + config.sigma_a
    if sigma_t <= 0:
        raise ValueError("sigma_a + sigma_s must be positive")

    image = np.zeros((config.height, config.width))

    positions = np.zeros((config.photons, 3))
    directions = np.zeros_like(positions)
    directions[:, 2] = 1.0

    weights = np.ones(config.photons)

    reflected_counter = 0
    transmitted_counter = 0

    while weights.size:
        step = rng.exponential(scale=1.0 / sigma_t, size=weights.size)

        boundary = distance_to_boundary(positions, directions, thickness)
        escaped = step > boundary

        exit_pos = positions[escaped] + boundary[escaped, None] * directions[escaped]
        exit_weights = weights[escaped]
        exit_bottom = directions[escaped, 2] > 0.0

        transmitted_counter += exit_weights[exit_bottom].sum()
        reflected_counter += exit_weights[~exit_bottom].sum()

        record_detector(image, exit_pos[exit_bottom], exit_weights[exit_bottom], config.detector_size)

        remaining = ~escaped
        positions = positions[remaining] + step[remaining, None] * directions[remaining]

        directions = directions[remaining]
        weights = weights[remaining]

        weights *= config.sigma_s / sigma_t

        weights_below_threshold = weights < config.roulette_threshold
        survived_weights = np.ones(weights.size, dtype=bool)
        survived_weights[weights_below_threshold] = rng.random(np.count_nonzero(weights_below_threshold)) < config.roulette_survival

        weights[weights_below_threshold & survived_weights] /= config.roulette_survival

        positions = positions[survived_weights]
        directions = directions[survived_weights]
        weights = weights[survived_weights]

        directions = scatter(directions, config.g, rng)

    return Result(image / config.photons, reflected_counter / config.photons, transmitted_counter / config.photons)

