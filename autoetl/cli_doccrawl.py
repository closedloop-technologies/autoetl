from pathlib import Path
from typing import List, Optional
import pyfiglet
from rich import print
from typer import Typer
import yaml

from autoetl import __description__ as DESCRIPTION
from autoetl import __version__ as VERSION
from autoetl import name as NAME
from autoetl.admin import get_projects
from autoetl.apis.crud import create_api, get_api, list_apis
from autoetl.apis.models import API
from autoetl.cli_ui import banner
from autoetl.config import Config, load_config
from autoetl.helpers import make_valid_folder_name
from autoetl.project import ETLProject, delete_project_files, load_project


app = Typer(help="Register, Crawl and Manage Source APIs")


def get_project(project_id: str, config: Config = None):
    if project_id is None or project_id.lower() == "none":
        project_id = None
    config = config or load_config()
    if project := load_project(project_id, config=config):
        return project
    if project_id:
        raise ValueError(f"Project {project_id} not found")
    raise ValueError("No active project found")


@app.command()
def get(api_id: str, project_id: str = None):
    """Gets the details of an API."""
    print(banner())
    project = get_project(project_id)
    if api := get_api(api_id, project.fdir):
        print(f"\nAPI:\n")
        print(f"  {api}")
        print(f"\n")
    else:
        print(f"\nNo API found in {project.id} with id {api_id}\n")


@app.command()
def list(project_id: str = None):
    """List all APIs in a project"""
    print(banner())
    project = get_project(project_id)
    if apis := list_apis(project.fdir):
        print(f"\nAPIs:\n")
        for api in apis:
            print(f"  {api}")
        print(f"\n")
    else:
        print(f"\nNo APIs found in {project.id}\n")


@app.command()
def create(
    name: str,
    api_id: Optional[str] = None,
    openapi_spec_url: Optional[str] = None,
    docs: List[str] = None,
    project_id: str = None,
):
    """Create a new API in a project."""
    if name is None or not name:
        raise ValueError("name cannot be None")

    print(banner())
    project = get_project(project_id)
    api = API(
        id=make_valid_folder_name(api_id or name).lower(),
        name=name,
        openapi_spec_url=openapi_spec_url or None,
        docs=docs or [],
    )
    api = create_api(api, project.fdir)
    print(f"\nCreated API:\n")
    print(f"  {api}")
    print(f"\n")


@app.command()
def delete(
    api_id: str,
    project_id: str = None,
    force: bool = False,
):
    """Deletes an api. Use the --force flag to skip the confirmation prompt."""
    print(banner())
    project = get_project(project_id)
    api = get_api(api_id, project.fdir)
    if not api:
        print(f"\nNo API found in {project.id} with id {api_id}\n")
        return
    print(f"Found API: {api}\n")

    if not force:
        print(f"Are you sure you want to delete api {api_id} in project {project.id}?")
        print("Type [green]'yes'[/green] to confirm or [red]'no'[/red] to cancel:")
        confirm = input()
        if confirm != "yes":
            print(f"Cancelled deletion of api: {api_id}")
            return

    # Delete API
    api_root = Path(project.fdir) / "apis" / api_id
    if not (api_root / "spec.yaml").exists():
        print(f"API {api_id} not found in {api_root}")
        return

    # Delete Crawls nested in api
    # Find if there are subdirectories in api_root

    print(f" * [red]Deleting api files in[/red]: {api_root}")
    for sub_dir in api_root.iterdir():
        if sub_dir.is_dir():
            print(f"   * [red]Deleting sub directory[/red]: {sub_dir}")
            sub_dir.unlink()

    (api_root / "spec.yaml").unlink()
    api_root.rmdir()
    print(f" * [green]Deleted api[/green]: {api_id}")
