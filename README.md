# openeo-processes-save-result

Custom implementation of the `save_result` process for the openEO processes ecosystem. Writes a `RasterCube` (xarray `Dataset`) to a chosen output format (COG, NetCDF, Zarr) and returns STAC metadata via [`raster-to-stac`](https://github.com/Eurac-Research-Institute-for-EO/raster-to-stac).

## Dependencies

- [openeo-processes-dask-slim](https://github.com/Eurac-Research-Institute-for-EO/openeo-processes-dask-slim) (`dev_remodel` branch) — provides the `RasterCube` data model, process spec, and exception base classes
- [raster-to-stac](https://github.com/Eurac-Research-Institute-for-EO/raster-to-stac) (`main` branch) — STAC metadata generation from raster data

## Installation

Requires Python >= 3.12.

### Development install (local checkouts)

```bash
git clone git@github.com:Eurac-Research-Institute-for-EO/openeo-processes-dask-slim.git
git clone git@github.com:Eurac-Research-Institute-for-EO/raster-to-stac.git
git clone git@github.com:Eurac-Research-Institute-for-EO/openeo-processes-save-result.git

# Install dask-slim from the dev_remodel branch
cd openeo-processes-dask-slim && git checkout dev_remodel && pip install -e ".[implementations]" && cd ..

# Install raster-to-stac
pip install -e raster-to-stac

# Install save-result
pip install -e openeo-processes-save-result

# Or with uv
uv pip install -e openeo-processes-dask-slim
uv pip install -e raster-to-stac
uv pip install -e openeo-processes-save-result
```

### Standalone install (pulls git deps automatically)

```bash
pip install -e openeo-processes-save-result
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
