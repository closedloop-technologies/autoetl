from pathlib import Path
import pyfiglet
from rich import print
from typer import Typer
import yaml

from autoetl import __description__ as DESCRIPTION
from autoetl import __version__ as VERSION
from autoetl import name as NAME
from autoetl.admin import get_projects
from autoetl.cli_ui import banner
from autoetl.config import load_config
from autoetl.project import ETLProject, delete_project_files, load_project


app = Typer(help="List and activate ETL projects")


@app.command()
def add_api(
    name: str,
    description: str | None = None,
    openapi_spec_url: str | None = None,
    endpoints: list[str] | None = None,
    docs_urls: list[str] | None = None,
    project_id: str | None = None,
):
    """
    # Add API endpoint configuration
    autoetl add-api "PetstoreMain"

    # Crawl the API to improve documentation and add typing
    autoetl api crawl --name "MyAPIEndpoint" --generate-typing
    """
    # Load project
    if project := load_project(project_id, config=config):
        print(project)
    else:
        print("No project found.")
        return

    config = load_config()
    projects = get_projects(config.config_dir)
    if not project_id or project_id is None or project_id.lower() == "none":
        project_id = projects.get("active")

    project = ETLProject(
        name=name,
        description=description,
        fdir=fdir,
        project_id=project_id,
    )
    project.init()
    print(project)


if __name__ == "__main__":
    show()
