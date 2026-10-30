import numpy as np
from dataclasses import dataclass, field


@dataclass
class Config:
    """Physics: everything simulate() needs."""
    photons: int = 100000
    width: int = 512
    height: int = 512

    sigma_a: float = 1.0
    sigma_s: float = 1.0
    g: float = 0.75

    detector_size: float = 1.0
    roulette_threshold: float = 0.001
    roulette_survival: float = 0.1


@dataclass
class PlotConfig:
    """Appearance: everything plotting.py needs."""
    cmap: str = "hot"
    empty_color: str = "black"          # colour of cells with no photons
    vmax_percentile: float = 99.9       # top of colour scale; 100 = true maximum
    log_scale: bool = True
    ticks: int = 3                      # tick marks per axis
    panel_size: float = 3.0             # inches per subplot
    dpi: int = 100
    output_dir: str = "assets"
    colorbar_label: str = "photon weight"


@dataclass
class ThicknessStudy:
    """plot_thickness.py: one image per thickness."""
    d_min: float = 0.0
    d_max: float = 2.0
    steps: int = 21
    cols: int = 7                       # rows are computed from steps / cols
    filename: str = "thickness_grid.png"

    def thicknesses(self):
        return np.linspace(self.d_min, self.d_max, self.steps)


@dataclass
class PassesStudy:
    """plot_passes.py: progressive refinement at one thickness."""
    thickness: float = 1.0
    npasses: int = 16
    snapshot_at: list = field(default_factory=lambda: [1, 2, 4, 8, 16])
    filename: str = "passes_grid.png"


@dataclass
class Result:
    grid: np.ndarray
    reflectance: float
    transmittance: float
