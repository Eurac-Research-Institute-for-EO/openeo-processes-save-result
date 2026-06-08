from __future__ import annotations

import numpy as np
import pytest
import xarray as xr


@pytest.fixture
def sample_raster_cube() -> xr.Dataset:
    return xr.Dataset(
        {
            "B01": (["y", "x", "t"], np.ones((3, 4, 2))),
            "B02": (["y", "x", "t"], np.ones((3, 4, 2)) * 2),
        },
        coords={
            "y": np.arange(3),
            "x": np.arange(4),
            "t": np.arange(2),
        },
        attrs={
            "openeo_x_dim": "x",
            "openeo_y_dim": "y",
            "openeo_temporal_dims": ["t"],
            "openeo_band_dims": ["bands"],
        },
    )


@pytest.fixture
def empty_raster_cube() -> xr.Dataset:
    return xr.Dataset(
        {"B01": (["y", "x"], np.array([[]]).reshape(0, 0))},
        coords={"y": np.array([]), "x": np.array([])},
    )
