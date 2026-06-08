import json
import logging
from pathlib import Path
from typing import Any, Optional

import xarray as xr
from raster2stac import Raster2STAC

_log = logging.getLogger(__name__)

_FORMAT_METHOD_MAP = {
    "GTIFF": "generate_cog_stac",
    "COG": "generate_cog_stac",
    "NETCDF": "generate_netcdf_stac",
    "ZARR": "generate_zarr_stac",
}

SUPPORTED_FORMATS = set(_FORMAT_METHOD_MAP.keys())


def write_and_create_stac(
    data: xr.Dataset,
    format: str,
    output_folder: str,
    collection_id: str = "save_result",
    collection_url: str = "",
    s3_upload: bool = False,
    bucket_name: Optional[str] = None,
    bucket_file_prefix: Optional[str] = None,
    aws_region: Optional[str] = None,
    aws_access_key: Optional[str] = None,
    aws_secret_key: Optional[str] = None,
    zarr_format: int = 3,
    consolidated: Optional[bool] = None,
    chunks: Optional[Any] = None,
    item_prefix: str = "",
    **kwargs,
) -> dict:
    fmt_upper = format.upper()
    method_name = _FORMAT_METHOD_MAP.get(fmt_upper)
    if method_name is None:
        raise ValueError(f"Unsupported output format: {format}")

    stac = Raster2STAC(
        data=data,
        collection_id=collection_id,
        collection_url=collection_url,
        output_folder=output_folder,
        s3_upload=s3_upload,
        bucket_name=bucket_name,
        bucket_file_prefix=bucket_file_prefix,
        aws_region=aws_region,
        aws_access_key=aws_access_key,
        aws_secret_key=aws_secret_key,
        zarr_format=zarr_format,
        consolidated=consolidated,
        chunks=chunks,
        item_prefix=item_prefix,
    )

    generate_method = getattr(stac, method_name)

    if method_name == "generate_zarr_stac":
        item_id = kwargs.pop("item_id", None)
        generate_method(item_id=item_id)
    else:
        generate_method()

    stac_path = Path(stac.output_folder) / stac.output_file
    if stac_path.exists():
        with open(stac_path) as f:
            stac_dict = json.load(f)
    else:
        _log.warning("STAC metadata file not found at %s, returning empty dict", stac_path)
        stac_dict = {}

    return stac_dict
