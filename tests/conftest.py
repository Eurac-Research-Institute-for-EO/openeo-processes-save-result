from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import rioxarray  # noqa: F401  registers .rio accessor
import xarray as xr


@pytest.fixture
def sample_raster_cube() -> xr.Dataset:
    data = xr.Dataset(
        {
            "B01": (["y", "x", "t"], np.ones((3, 4, 2))),
            "B02": (["y", "x", "t"], np.ones((3, 4, 2)) * 2),
        },
        coords={
            "y": np.arange(3).astype(float),
            "x": np.arange(4).astype(float),
            "t": pd.to_datetime(["2024-01-01", "2024-01-02"]),
        },
        attrs={
            "openeo_x_dim": "x",
            "openeo_y_dim": "y",
            "openeo_temporal_dims": ["t"],
            "openeo_band_dims": ["bands"],
        },
    )
    return data.rio.write_crs("EPSG:4326")


@pytest.fixture
def sample_dataarray_raster_cube() -> xr.DataArray:
    data = xr.DataArray(
        np.ones((2, 3, 4, 2)),
        dims=("bands", "y", "x", "t"),
        coords={
            "bands": ["B01", "B02"],
            "y": np.arange(3).astype(float),
            "x": np.arange(4).astype(float),
            "t": pd.to_datetime(["2024-01-01", "2024-01-02"]),
        },
        attrs={
            "openeo_x_dim": "x",
            "openeo_y_dim": "y",
            "openeo_temporal_dims": ["t"],
            "openeo_band_dims": ["bands"],
        },
        name="cube",
    )
    return data.rio.write_crs("EPSG:4326")


@pytest.fixture
def empty_raster_cube() -> xr.Dataset:
    return xr.Dataset(
        {"B01": (["y", "x"], np.array([[]]).reshape(0, 0))},
        coords={"y": np.array([]), "x": np.array([])},
    )


@pytest.fixture
def empty_dataarray_raster_cube() -> xr.DataArray:
    return xr.DataArray(
        np.array([]),
        dims=("x",),
        coords={"x": np.array([])},
        name="empty",
    )
