import datetime
import logging
from pathlib import Path
from typing import Optional

import xarray as xr

from openeo_processes_dask_slim.process_implementations.data_model import RasterCube
from openeo_processes_dask_slim.process_implementations.exceptions import OpenEOException

from ._raster_formats import SUPPORTED_FORMATS, write_and_create_stac

_log = logging.getLogger(__name__)


class FormatUnsuitable(OpenEOException):
    pass


class DataCubeEmpty(OpenEOException):
    pass


def save_result(
    data: RasterCube,
    format: str,
    options: Optional[dict] = None,
) -> dict:
    if options is None:
        options = {}

    fmt_upper = format.upper()

    if fmt_upper not in SUPPORTED_FORMATS:
        raise FormatUnsuitable(
            f"Data can't be transformed into the requested output format '{format}'. "
            f"Supported formats: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    _validate_data_cube(data, fmt_upper)

    output_folder = options.pop("output_folder", None)
    if output_folder is None:
        output_folder = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S%f")[:-3]

    Path(output_folder).mkdir(parents=True, exist_ok=True)

    stac_options = _extract_stac_options(options)

    stac_dict = write_and_create_stac(
        data=data,
        format=fmt_upper,
        output_folder=output_folder,
        **stac_options,
    )

    return stac_dict


def _validate_data_cube(data: xr.Dataset, fmt_upper: str) -> None:
    empty_formats = {"NETCDF", "ZARR"}

    if _is_cube_empty(data) and fmt_upper in empty_formats:
        raise DataCubeEmpty(
            "The file format doesn't support storing empty data cubes."
        )


def _is_cube_empty(data: xr.Dataset) -> bool:
    if data is None:
        return True
    for var in data.data_vars:
        if data[var].size > 0:
            return False
    return True


def _extract_stac_options(options: dict) -> dict:
    stac_params = {
        "collection_id": options.pop("collection_id", "save_result"),
        "collection_url": options.pop("collection_url", ""),
        "s3_upload": options.pop("s3_upload", False),
        "bucket_name": options.pop("bucket_name", None),
        "bucket_file_prefix": options.pop("bucket_file_prefix", None),
        "aws_region": options.pop("aws_region", None),
        "aws_access_key": options.pop("aws_access_key", None),
        "aws_secret_key": options.pop("aws_secret_key", None),
        "zarr_format": options.pop("zarr_format", 3),
        "consolidated": options.pop("consolidated", None),
        "chunks": options.pop("chunks", None),
        "item_prefix": options.pop("item_prefix", ""),
    }

    stac_params.update(options)
    return stac_params
