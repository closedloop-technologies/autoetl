import os
from pathlib import Path
import yaml

from autoetl.apis.models import API


def get_api(api_id: str, fdir: Path | str | None = None):
    """Get an API from the config file."""
    if api_id is None or not api_id:
        raise ValueError("api_id cannot be None")
    if fdir is None:
        raise ValueError("fdir cannot be None")
    spec_path = Path(fdir) / "apis" / api_id / "spec.yaml"
    if not spec_path.exists():
        return None

    with open(spec_path, "r") as fh:
        return API(**yaml.safe_load(fh))


def create_api(api: API, fdir: Path | str | None = None):
    """Create an API in the config file."""
    if api.id is None or not api.id:
        raise ValueError("api.id cannot be None")
    if fdir is None:
        raise ValueError("fdir cannot be None")
    if get_api(api.id, fdir):
        raise ValueError(f"API with id {api.id} already exists")

    spec_path = Path(fdir) / "apis" / api.id / "spec.yaml"
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    with open(spec_path, "w") as fh:
        yaml.safe_dump(api.model_dump(), fh)
    return api


def update_api(api: API, fdir: Path | str | None = None):
    """Update an API in the config file."""
    if api.id is None or not api.id:
        raise ValueError("api.id cannot be None")
    if fdir is None:
        raise ValueError("fdir cannot be None")
    if not get_api(api.id, fdir):
        raise ValueError(f"API with id {api.id} does not exist")

    spec_path = Path(fdir) / "apis" / api.id / "spec.yaml"
    with open(spec_path, "w") as fh:
        yaml.safe_dump(api.model_dump(), fh)
    return api


def delete_api(api_id: str, fdir: Path | str | None = None):
    """Delete an API from the config file."""
    if api_id is None or not api_id:
        raise ValueError("api_id cannot be None")
    if fdir is None:
        raise ValueError("fdir cannot be None")
    spec_path = Path(fdir) / "apis" / api_id / "spec.yaml"
    if not spec_path.exists():
        return None
    spec_path.unlink()
    # remove the directory if it is empty
    # TODO remove the rest of the files in the directory
    spec_path.parent.rmdir()
    return api_id


def list_apis(fdir: Path | str | None = None):
    """List all APIs."""
    if fdir is None:
        raise ValueError("fdir cannot be None")
    apis_path = Path(fdir) / "apis"
    if not apis_path.exists():
        return None
    return [
        get_api(str(api).split(os.sep)[-1], fdir)
        for api in apis_path.iterdir()
        if api.is_dir() and (api / "spec.yaml").exists()
    ]
