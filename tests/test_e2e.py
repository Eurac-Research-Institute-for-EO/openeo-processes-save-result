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


@pytest.mark.parametrize(
    ("fmt", "asset_relpath"),
    [
        ("GTiff", ("static", "tmean_static.tif")),
        ("NetCDF", ("static", "static.nc")),
        ("Zarr", ("static.zarr",)),
    ],
)
@pytest.mark.slow
def test_save_result_e2e_temporally_reduced_cube(
    fmt,
    asset_relpath,
    sample_temporally_reduced_raster_cube,
):
    with tempfile.TemporaryDirectory() as tmpdir:
        stac = save_result(
            data=sample_temporally_reduced_raster_cube,
            format=fmt,
            options={
                "output_folder": tmpdir,
                "collection_id": "test-no-time",
                "skip_validation": True,
            },
        )

        item_path = os.path.join(tmpdir, "items", "static.json")
        asset_path = os.path.join(tmpdir, *asset_relpath)

        assert stac["type"] == "Collection"
        assert stac["id"] == "test-no-time"
        assert os.path.exists(asset_path)

        with open(item_path) as f:
            item = json.load(f)

        cube_dimensions = item["properties"].get(
            "cube:dimensions", stac.get("cube:dimensions", {})
        )
        assert "t" not in cube_dimensions

        item_datetime = item["properties"].get("datetime") or item[
            "properties"
        ].get("start_datetime")
        assert item_datetime == "2020-06-01T00:00:00Z"


@pytest.mark.parametrize(
    ("fmt", "asset_relpath"),
    [
        (
            "NetCDF",
            (
                "20240101000000_20240102000000",
                "20240101000000_20240102000000.nc",
            ),
        ),
        ("Zarr", ("20240101000000_20240102000000.zarr",)),
    ],
)
@pytest.mark.slow
def test_save_result_e2e_spatially_reduced_cube(
    fmt,
    asset_relpath,
    sample_spatially_reduced_raster_cube,
):
    with tempfile.TemporaryDirectory() as tmpdir:
        stac = save_result(
            data=sample_spatially_reduced_raster_cube,
            format=fmt,
            options={
                "output_folder": tmpdir,
                "collection_id": "test-no-space",
                "skip_validation": True,
            },
        )

        item_id = "20240101000000_20240102000000"
        item_path = os.path.join(tmpdir, "items", f"{item_id}.json")
        asset_path = os.path.join(tmpdir, *asset_relpath)

        assert stac["type"] == "Collection"
        assert stac["id"] == "test-no-space"
        assert stac["extent"]["spatial"]["bbox"] == [
            [-180.0, -90.0, 180.0, 90.0]
        ]
        assert os.path.exists(asset_path)

        with open(item_path) as f:
            item = json.load(f)

        assert "bbox" not in item
        assert item["geometry"] is None
        assert set(item["properties"]["cube:dimensions"]) == {"t"}


@pytest.mark.slow
def test_save_result_e2e_spatially_reduced_cube_rejects_gtiff(
    sample_spatially_reduced_raster_cube,
):
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(
            ValueError,
            match="COG output requires x and y spatial dimensions",
        ):
            save_result(
                data=sample_spatially_reduced_raster_cube,
                format="GTiff",
                options={
                    "output_folder": tmpdir,
                    "collection_id": "test-no-space",
                    "skip_validation": True,
                },
            )


@pytest.mark.slow
@pytest.mark.xfail(
    reason="pystac CRS validation requires remote JSON schema (network access)",
    strict=False,
)
def test_save_result_zarr_e2e(sample_raster_cube):
    with tempfile.TemporaryDirectory() as tmpdir:
        stac = save_result(
            data=sample_raster_cube,
            format="Zarr",
            options={"output_folder": tmpdir, "collection_id": "test-zarr"},
        )

        assert stac["type"] == "Collection"
        assert stac["id"] == "test-zarr"
