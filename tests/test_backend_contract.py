from __future__ import annotations

import os
import tempfile
from unittest.mock import patch

import pytest
import xarray as xr

from openeo_processes_save_result._compat import RasterCube, _BACKEND
from openeo_processes_save_result.save_result import save_result


@pytest.fixture
def backend_contract_cube(
    sample_dataarray_raster_cube, sample_raster_cube
) -> xr.DataArray | xr.Dataset:
    expected_type = os.environ.get("OPENEO_SAVE_RESULT_EXPECTED_RASTERCUBE")
    if expected_type == "DataArray":
        return sample_dataarray_raster_cube
    if expected_type == "Dataset":
        return sample_raster_cube
    return sample_dataarray_raster_cube


def test_backend_rastercube_type_matches_contract():
    expected_type = os.environ.get("OPENEO_SAVE_RESULT_EXPECTED_RASTERCUBE")
    if expected_type is None:
        pytest.skip("OPENEO_SAVE_RESULT_EXPECTED_RASTERCUBE is not set")

    expected_class = {"DataArray": xr.DataArray, "Dataset": xr.Dataset}[expected_type]
    args = getattr(RasterCube, "__args__", ())
    assert expected_class in args or RasterCube is expected_class


def test_backend_name_matches_contract():
    expected_backend = os.environ.get("OPENEO_SAVE_RESULT_EXPECTED_BACKEND")
    if expected_backend is None:
        pytest.skip("OPENEO_SAVE_RESULT_EXPECTED_BACKEND is not set")

    assert _BACKEND == expected_backend


def test_save_result_accepts_backend_contract_cube(backend_contract_cube):
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch(
            "openeo_processes_save_result.save_result.write_and_create_stac"
        ) as mock_write:
            mock_write.return_value = {"type": "Collection"}

            result = save_result(
                data=backend_contract_cube,
                format="GTiff",
                options={"output_folder": tmpdir},
            )

            assert result == {"type": "Collection"}
            assert mock_write.call_args[1]["data"] is backend_contract_cube
