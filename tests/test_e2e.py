from __future__ import annotations

import json
import os
import tempfile

import pytest

from openeo_processes_save_result import save_result


@pytest.mark.slow
def test_save_result_cog_e2e(sample_raster_cube):
    with tempfile.TemporaryDirectory() as tmpdir:
        stac = save_result(
            data=sample_raster_cube,
            format="GTiff",
            options={"output_folder": tmpdir, "collection_id": "test-001"},
        )

        assert isinstance(stac, dict)
        assert stac["type"] == "Collection"
        assert stac["id"] == "test-001"

        files = os.listdir(tmpdir)
        assert "test-001.json" in files

        meta_path = os.path.join(tmpdir, "test-001.json")
        with open(meta_path) as f:
            meta = json.load(f)
        assert meta["type"] == "Collection"
        assert meta["id"] == "test-001"


@pytest.mark.slow
@pytest.mark.xfail(reason="scipy netCDF writer has Unicode dtype issue", strict=False)
def test_save_result_netcdf_e2e(sample_raster_cube):
    with tempfile.TemporaryDirectory() as tmpdir:
        stac = save_result(
            data=sample_raster_cube,
            format="NetCDF",
            options={"output_folder": tmpdir, "collection_id": "test-netcdf"},
        )

        assert stac["type"] == "Collection"
        assert stac["id"] == "test-netcdf"


@pytest.mark.slow
def test_save_result_zarr_e2e(sample_raster_cube):
    with tempfile.TemporaryDirectory() as tmpdir:
        stac = save_result(
            data=sample_raster_cube,
            format="Zarr",
            options={"output_folder": tmpdir, "collection_id": "test-zarr"},
        )

        assert stac["type"] == "Collection"
        assert stac["id"] == "test-zarr"
