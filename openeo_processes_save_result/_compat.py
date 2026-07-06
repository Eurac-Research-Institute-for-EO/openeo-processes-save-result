try:
    from openeo_processes_dask.process_implementations.data_model import RasterCube
    from openeo_processes_dask.process_implementations.exceptions import OpenEOException
    from openeo_processes_dask.specs import save_result as save_result_spec

    _BACKEND = "dask"
except ImportError:
    from openeo_processes_dask_slim.process_implementations.data_model import RasterCube
    from openeo_processes_dask_slim.process_implementations.exceptions import OpenEOException
    from openeo_processes_dask_slim.specs import save_result as save_result_spec

    _BACKEND = "dask-slim"

__all__ = ["RasterCube", "OpenEOException", "save_result_spec", "_BACKEND"]
