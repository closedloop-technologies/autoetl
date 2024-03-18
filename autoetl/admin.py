# Manages the data in ~/.autoetl directory


from pathlib import Path

import yaml


def get_projects(project_fdir: str | Path):
    project_fdir = Path.cwd() if project_fdir is None else Path(project_fdir)

    if not (project_fdir / "projects.yaml").exists():
        return None

    with open(project_fdir / "projects.yaml", "r") as fh:
        # TODO type check this
        return yaml.safe_load(fh)


def upsert_project_in_config(project: any):
    """Upsert a project in the config file"""
    config = project._config
    projects = get_projects(config.config_dir) or {}
    projects["projects"] = projects.get("projects", {})
    active_project = projects.get("active", None)
    if active_project is None:
        projects["active"] = project.id
    projects["projects"].update({project.id: project.dict(safe=True)})

    config_projects_file = Path(config.config_dir) / "projects.yaml"
    config_projects_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_projects_file, "w") as fh:
        yaml.safe_dump(projects, fh)
