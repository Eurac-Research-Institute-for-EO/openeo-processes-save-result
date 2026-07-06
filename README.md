# openeo-processes-save-result

Custom implementation of the `save_result` process for the openEO processes ecosystem. Writes a `RasterCube` (xarray `Dataset`/`DataArray`) to a chosen output format (COG, NetCDF, Zarr) and returns STAC metadata via [`raster2stac`](https://pypi.org/project/raster2stac/).

## Backend compatibility

This package works with **both** upstream openEO process backends. Selection is automatic via a `try/except` import — it prefers `openeo_processes_dask` and falls back to `openeo_processes_dask_slim`:

| Backend | Branches tested | `RasterCube` type |
|---|---|---|
| [`openeo-processes-dask`](https://github.com/Eurac-Research-Institute-for-EO/openeo-processes-dask) | `main` | `xr.DataArray` |
| [`openeo-processes-dask-slim`](https://github.com/Eurac-Research-Institute-for-EO/openeo-processes-dask-slim) | `main` | `xr.DataArray` |
| [`openeo-processes-dask-slim`](https://github.com/Eurac-Research-Institute-for-EO/openeo-processes-dask-slim) | `dev_remodel` | `xr.Dataset` |

[`openeo-processes-dedl-cube-load`](https://github.com/Eurac-Research-Institute-for-EO/openeo-processes-dedl-cube-load) (`main` branch) pins `dask-slim@dev_remodel` — this package is fully compatible.

## Dependencies

- **Default:** [openeo-processes-dask](https://github.com/Eurac-Research-Institute-for-EO/openeo-processes-dask) (`main` branch)
- **Alternative:** [openeo-processes-dask-slim](https://github.com/Eurac-Research-Institute-for-EO/openeo-processes-dask-slim) (install with `[dask-slim]` extra)
- [raster2stac](https://pypi.org/project/raster2stac/) (`>=2026.6.2`)

## Installation

Requires Python >= 3.11.

### Development install (local checkouts, default dask backend)

```bash
git clone git@github.com:Eurac-Research-Institute-for-EO/openeo-processes-dask.git
git clone git@github.com:Eurac-Research-Institute-for-EO/openeo-processes-save-result.git

cd openeo-processes-dask && git checkout main && pip install -e ".[implementations]" && cd ..
pip install -e openeo-processes-save-result
```

### Alternative: use with openeo-processes-dask-slim

```bash
git clone git@github.com:Eurac-Research-Institute-for-EO/openeo-processes-dask-slim.git
git clone git@github.com:Eurac-Research-Institute-for-EO/openeo-processes-save-result.git

cd openeo-processes-dask-slim && git checkout dev_remodel && pip install -e ".[implementations]" && cd ..
pip install -e openeo-processes-save-result
```

### Standalone install

```bash
# Default (pulls openeo-processes-dask main)
pip install git+https://github.com/Eurac-Research-Institute-for-EO/openeo-processes-save-result.git

# With dask-slim instead of full dask
pip install git+https://github.com/Eurac-Research-Institute-for-EO/openeo-processes-save-result.git#egg=openeo-processes-save-result[dask-slim]
```

### Install test/dev extras

```bash
pip install -e ".[test,dev]"
```

## Usage

```python
from openeo_processes_save_result import save_result

stac = save_result(
    data=raster_cube,
    format="GTiff",
    options={
        "output_folder": "/tmp/my-output",
        "collection_id": "my-collection",
        "s3_upload": True,
        "bucket_name": "my-bucket",
        "aws_region": "eu-central-1",
    },
)
# stac is a STAC Collection dict with Items and Assets
```

## Supported formats

| openEO format | GDAL code | Description |
|---|---|---|
| `GTiff` / `COG` | `GTiff` | Cloud Optimized GeoTIFF (via rioxarray) |
| `NetCDF` | `NetCDF` | NetCDF (via xarray) |
| `Zarr` | `Zarr` | Zarr v3 (via xarray) |

## `options` parameters

| Option | Default | Description |
|---|---|---|
| `output_folder` | auto-generated timestamp dir | Output directory for files |
| `collection_id` | `"save_result"` | STAC collection identifier |
| `collection_url` | `""` | Base URL for the STAC collection |
| `s3_upload` | `False` | Upload files to S3 |
| `bucket_name` | `None` | S3 bucket name |
| `bucket_file_prefix` | `None` | Key prefix for S3 objects |
| `aws_region` | `None` | AWS region |
| `aws_access_key` | `None` | AWS access key |
| `aws_secret_key` | `None` | AWS secret key |
| `zarr_format` | `3` | Zarr format version (2 or 3) |
| `consolidated` | `None` | Zarr consolidated metadata |

## Exceptions

- `FormatUnsuitable` — raised when the requested output format is not supported
- `DataCubeEmpty` — raised when an empty data cube is written to NetCDF or Zarr

## Testing

```bash
pip install -e ".[test]"
pytest
```
