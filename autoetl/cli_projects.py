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
def list():
    """List all projects."""
    print(banner())
    config = load_config()
    projects = get_projects(config.config_dir)
    if project_list := (projects or {}).get("projects", {}):
        print(f"\nProjects:\n")
        active_project = projects.get("active", None)
        for project in project_list:
            if project == active_project:
                # Print active in green text
                print(f"[green]→ {project}[/green]")
            else:
                print(f"  {project}")
        print(f"\n")
    else:
        print(f"No projects found in {config.config_dir}\n")


@app.command()
def create(
    name: str,
    description: str = None,
    fdir: str | None = None,
    project_id: str | None = None,
):
    """Creates a new project."""
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
def activate(
    project_id: str,
):
    """Activates a project."""
    print(f"{banner()}\n")
    config = load_config()
    projects = get_projects(config.config_dir)
    if project_list := (projects or {}).get("projects", {}):
        if project_id in project_list:
            projects["active"] = project_id
            config_projects_file = Path(config.config_dir) / "projects.yaml"
            with open(config_projects_file, "w") as fh:
                yaml.safe_dump(projects, fh)
            print(f"Activated project: {project_id}")
        else:
            print(f"Project {project_id} not found in {config.config_dir}")
    else:
        print(f"No projects found in {config.config_dir}\n")


@app.command()
def delete(
    project_id: str,
    force: bool = False,
):
    """Deletes a project. Use the --force flag to skip the confirmation prompt."""
    print(f"{banner()}\n")
    config = load_config()
    projects = get_projects(config.config_dir)

    if project_list := (projects or {}).get("projects", {}):
        if project_id not in project_list:
            print(f"Project {project_id} not found in {config.config_dir}")
            return

        if not force:
            print(f"Are you sure you want to delete project {project_id}?")
            print("Type [green]'yes'[/green] to confirm or [red]'no'[/red] to cancel:")
            confirm = input()
            if confirm != "yes":
                print(f"Cancelled deletion of project: {project_id}")
                return
    else:
        print(f"No projects found in {config.config_dir}\n")
        return

    # Remove Project files
    # project_list[project_id]["fdir"]
    project_dir = Path(project_list[project_id]["fdir"])
    print(f" * [red]Deleting project files in[/red]: {project_dir}")
    delete_project_files(project_dir)

    # Delete Project
    del projects["projects"][project_id]

    # Deactivate Project
    if projects.get("active") == project_id:
        del projects["active"]
        if len(projects["projects"]):
            projects["active"] = sorted(projects["projects"].keys())[0]
    config_projects_file = Path(config.config_dir) / "projects.yaml"
    with open(config_projects_file, "w") as fh:
        yaml.safe_dump(projects, fh)
    print(f" * [green]Deleted project[/green]: {project_id}")


@app.command()
def show(project_id: str = None, file_tree: bool = False):
    """Shows the details of a project."""
    print(f"{banner()}\n")
    if project_id is None or project_id.lower() == "none":
        project_id = None

    config = load_config()
    if project := load_project(project_id, config=config):
        print(project)
        if file_tree:
            print("\nProject Files:\n")
            show_file_tree(project.fdir)


from pathlib import Path


def show_file_tree(fdir: Path, level: int = 0, prefix: str = ""):
    if not fdir.is_dir():
        raise ValueError(f"{fdir} is not a valid directory.")

    if level == 0:
        print(f"[blue]{fdir}[/blue]")

    files = sorted(fdir.glob("*"))
    num_files = len(files)

    for index, file in enumerate(files, start=1):
        is_last = index == num_files
        connector = "└── " if is_last else "├── "

        if file.is_file():
            print(f"{prefix}{connector}{file.name}")
        else:
            print(f"{prefix}{connector}[blue]{file.name}[/blue]")

        if file.is_dir():
            if is_last:
                new_prefix = prefix + "    "
            else:
                new_prefix = prefix + "│   "
            show_file_tree(file, level + 1, new_prefix)


if __name__ == "__main__":
    show()
