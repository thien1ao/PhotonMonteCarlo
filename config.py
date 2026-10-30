import numpy as np
from dataclasses import dataclass

@dataclass
class Config:
    photons: int = 100000
    width: int = 512;
    height: int = 512

    sigma_a: float = 1.0
    sigma_s: float = 1.0
    g: float = 0.75

    detector_size: float = 1.0
    roulette_threshold: float = 0.001
    roulette_survival: float = 0.1

@dataclass
class Result:
    grid: np.ndarray
    reflectance: float
    transmittance: float
