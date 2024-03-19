from rich import print
from typer import Typer

from autoetl import __description__ as DESCRIPTION
from autoetl import __version__ as VERSION
from autoetl import name as NAME
from autoetl.cli_ui import banner
from autoetl.config import load_config
from autoetl.project import ETLProject
from autoetl.cli_projects import app as project_cli
from autoetl.cli_apis import app as api_cli


app = Typer(help=f"{(NAME or '').replace('_', ' ')} CLI")
app.add_typer(project_cli, name="projects")
app.add_typer(api_cli, name="apis")


@app.command()
def init(
    name: str,
    description: str = None,
    fdir: str | None = None,
    project_id: str | None = None,
):
    """Create a new ETL Project"""
    print(f"{banner()}\n")
    print("Creating a new project.\n")
    project = ETLProject(
        name=name,
        description=description,
        fdir=fdir,
        project_id=project_id,
    )
    project.init()
    print(project)


@app.command()
def show_config():
    """Show the current config."""
    print(f"{banner()}\n")
    print(
        "Set `AUTOETL_ENV_FILE` or `AUTOETL_CONFIG_DIR` environment variables to change config.\n"
    )
    print(load_config())
