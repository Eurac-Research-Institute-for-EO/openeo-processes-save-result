from __future__ import annotations

import inspect
import tempfile
from unittest.mock import patch

import pytest
import xarray as xr

from openeo_processes_save_result.save_result import (
    DataCubeEmpty,
    FormatUnsuitable,
    _is_cube_empty,
    _validate_data_cube,
    save_result,
)
from openeo_processes_save_result.specs import save_result as save_result_spec


def test_save_result_keeps_process_spec_signature():
    params = list(inspect.signature(save_result).parameters)

    assert params == ["data", "format", "options"]


def test_package_exposes_standard_save_result_spec():
    assert save_result_spec["id"] == "save_result"


def test_is_cube_empty_with_none():
    assert _is_cube_empty(None) is True


def test_is_cube_empty_with_empty_dataset():
    ds = xr.Dataset()
    assert _is_cube_empty(ds) is True


def test_is_cube_empty_with_empty_dataarray(empty_dataarray_raster_cube):
    assert _is_cube_empty(empty_dataarray_raster_cube) is True


def test_is_cube_empty_with_data(sample_raster_cube):
    assert _is_cube_empty(sample_raster_cube) is False


def test_is_cube_empty_with_dataarray(sample_dataarray_raster_cube):
    assert _is_cube_empty(sample_dataarray_raster_cube) is False


def test_validate_data_cube_nonempty_passes(sample_raster_cube):
    _validate_data_cube(sample_raster_cube, "GTIFF")


def test_validate_dataarray_cube_nonempty_passes(sample_dataarray_raster_cube):
    _validate_data_cube(sample_dataarray_raster_cube, "GTIFF")


@pytest.mark.parametrize("fmt", ["NETCDF", "ZARR"])
def test_validate_data_cube_empty_raises(empty_raster_cube, fmt):
    with pytest.raises(DataCubeEmpty):
        _validate_data_cube(empty_raster_cube, fmt)


@pytest.mark.parametrize("fmt", ["NETCDF", "ZARR"])
def test_validate_dataarray_cube_empty_raises(empty_dataarray_raster_cube, fmt):
    with pytest.raises(DataCubeEmpty):
        _validate_data_cube(empty_dataarray_raster_cube, fmt)


def test_validate_data_cube_empty_cog_ok(empty_raster_cube):
    _validate_data_cube(empty_raster_cube, "GTIFF")


def test_format_unsuitable_unknown_format(sample_raster_cube):
    with pytest.raises(FormatUnsuitable, match="HDF5"):
        save_result(data=sample_raster_cube, format="HDF5")


def test_format_unsuitable_case_insensitive(sample_raster_cube):
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch(
            "openeo_processes_save_result.save_result.write_and_create_stac"
        ) as mock_write:
            mock_write.return_value = {"type": "Collection"}
            result = save_result(
                data=sample_raster_cube,
                format="gtiff",
                options={"output_folder": tmpdir},
            )
            assert result == {"type": "Collection"}
            assert mock_write.call_args[1]["format"] == "GTIFF"


def test_save_result_accepts_dataarray_raster_cube(sample_dataarray_raster_cube):
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch(
            "openeo_processes_save_result.save_result.write_and_create_stac"
        ) as mock_write:
            mock_write.return_value = {"type": "Collection"}
            save_result(
                data=sample_dataarray_raster_cube,
                format="GTiff",
                options={"output_folder": tmpdir},
            )
            assert mock_write.call_args[1]["data"] is sample_dataarray_raster_cube


def test_save_result_passes_output_folder(sample_raster_cube):
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch(
            "openeo_processes_save_result.save_result.write_and_create_stac"
        ) as mock_write:
            mock_write.return_value = {"type": "Collection"}
            save_result(
                data=sample_raster_cube,
                format="GTiff",
                options={"output_folder": tmpdir},
            )
            assert mock_write.call_args[1]["output_folder"] == tmpdir


def test_save_result_returns_stac_dict(sample_raster_cube):
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch(
            "openeo_processes_save_result.save_result.write_and_create_stac"
        ) as mock_write:
            expected = {
                "type": "Collection",
                "id": "test-collection",
                "stac_version": "1.0.0",
            }
            mock_write.return_value = expected
            result = save_result(
                data=sample_raster_cube,
                format="Zarr",
                options={"output_folder": tmpdir, "collection_id": "test-collection"},
            )
            assert result == expected


def test_save_result_does_not_mutate_options(sample_raster_cube):
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch(
            "openeo_processes_save_result.save_result.write_and_create_stac"
        ) as mock_write:
            mock_write.return_value = {"type": "Collection"}
            options = {
                "output_folder": tmpdir,
                "collection_id": "test-collection",
                "zarr_format": 2,
                "custom_option": "forwarded",
            }

            save_result(data=sample_raster_cube, format="Zarr", options=options)

            assert options == {
                "output_folder": tmpdir,
                "collection_id": "test-collection",
                "zarr_format": 2,
                "custom_option": "forwarded",
            }


def test_save_result_forwards_stac_options(sample_raster_cube):
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch(
            "openeo_processes_save_result.save_result.write_and_create_stac"
        ) as mock_write:
            mock_write.return_value = {}
            save_result(
                data=sample_raster_cube,
                format="COG",
                options={
                    "output_folder": tmpdir,
                    "collection_id": "my-coll",
                    "s3_upload": True,
                    "bucket_name": "my-bucket",
                },
            )
            kwargs = mock_write.call_args[1]
            assert kwargs["collection_id"] == "my-coll"
            assert kwargs["s3_upload"] is True
            assert kwargs["bucket_name"] == "my-bucket"
