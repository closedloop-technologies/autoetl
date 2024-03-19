import datetime
import tempfile
from logging import getLogger
from pathlib import Path
from typing import Dict, Set
from autoetl.apis.crud import create_api, get_api
from autoetl.doc_crawler.crawler_flow import crawl
from autoetl.doc_crawler.crud import create_doccrawl
from autoetl.helpers import cuid_generator

import yaml

from autoetl.admin import get_projects, upsert_project_in_config
from autoetl.apis.models import API, DocCrawl
from autoetl.config import Config, load_config
from autoetl.helpers import make_valid_folder_name
from autoetl.service import Service
from autoetl.templates import get_templates

logger = getLogger(__name__)

BASE_DIRS = [
    "./domain_knowledge",
    "./apis",
    "./fns",
    "./db",
    "./etl",
    "./deployment",
    "./serve",
]

FILE_STRUCTURES = {
    "root": ["autoetl.yaml", ".env"],
    # "domain_knowledge": ["README.md", "domain.graph"],
    # "apis": ["spec.yaml", "openapi_time_hash.yaml", "openapi.yaml", "model.py", "schema.graph"],
    # "fns": ["spec.yaml", "openapi.yaml", "model.py", "schema.graph"],
    # "db": ["spec.yaml", "schema.prisma", "model.py", "schema.graph"],
    # "etl": ["schema_alignment.graph", "query_plan.graph", "resolution.graph", "script.py", "test_script.py"],
    # "deployment": ["config.yaml", "run.py"],
    # "serve": ["spec.yaml", "openapi.yaml", "model.py", "api.py"]
}


def delete_project_files(fdir: str | Path):
    fdir = Path(fdir)
    if not fdir.exists():
        raise FileNotFoundError(f"Project directory {fdir} does not exist")
    autoetl_yaml = fdir / "autoetl.yaml"
    if not autoetl_yaml.exists():
        raise FileNotFoundError(
            f"autoetl.yaml file not found in {fdir}. Is this a valid project?"
        )

    for base_dir in BASE_DIRS:
        base_dir = fdir / base_dir
        if base_dir.exists():
            # TODO might need to add a check for subfolders
            for file in base_dir.iterdir():
                file.unlink()
            base_dir.rmdir()

    autoetl_yaml = fdir / "autoetl.yaml"
    autoetl_yaml.unlink()
    autoetl_env = fdir / ".env"
    autoetl_env.unlink()
    fdir.rmdir()


def create_file_from_template(path, template_name):
    if template_content := get_templates(template_name):
        with open(path, "w") as f:
            # Here you would render the template with JINJA
            f.write(template_content)
    else:
        open(path, "a").close()  # Just create an empty file if no template is available


def create_etl_project_structure(project_root: Path, project_name: str = "autoetl"):
    project_root = Path(project_root)
    # Create base directories
    for base_dir in BASE_DIRS:
        base_dir = project_root / base_dir
        base_dir.mkdir(parents=True, exist_ok=True)

    # Create files for each directory
    dir_key = "root"
    for file in FILE_STRUCTURES[dir_key]:
        create_file_from_template(project_root / file, file)


class ETLProject:
    def __init__(
        self,
        name: str,
        description: str = None,
        fdir: str | Path | None = None,
        project_id: str | None = None,
        created_at: datetime.datetime | None = None,
        config: Config | None = None,
        **kwargs,
    ):
        if not name:
            raise ValueError("Project name is required")
        self.name = name
        self.description = description
        self.created_at = created_at
        self._config: Config = config or load_config()
        self.id = None
        self.fdir = None

        self.fdir, self.id = self._set_project_and_fdir(
            name, fdir, kwargs.get("id", project_id)
        )

        if self.id.lower() == "none":
            raise ValueError(
                "Project name cannot be 'none' and must have at least one alpha-numerical character"
            )

        try:
            self.load(self.fdir)
            logger.info(f"Loaded project {self.name} from {self.fdir}")
        except FileNotFoundError:
            self.init()
            logger.info(f"Initialized project {self.name} in {self.fdir}")

        self.description = description or self.description
        self.created_at = self.created_at or datetime.datetime.now(
            datetime.timezone.utc
        )

        # Create an activate project in config
        upsert_project_in_config(self)

    def dict(self, safe=False):
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "fdir": str(self.fdir) if safe else self.fdir,
            "id": self.id,
        }

    def __repr__(self) -> str:
        description = f'"{self.description}"' if self.description else '""'
        created_time = self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        return f"<ETLProject name={self.name} id={self.id} created={created_time} fdir={self.fdir} description={description}>".strip()

    @staticmethod
    def _set_project_and_fdir(name, fdir, project_id):
        project_id = project_id or name
        project_id = make_valid_folder_name(project_id or name).lower()
        if len(project_id) == 0:
            raise ValueError(
                "Project name must have at least one alpha-numerical character"
            )
        if fdir in [".", "cwd"]:
            fdir = Path.cwd() / project_id
        elif fdir is None:
            fdir = Path(tempfile.mkdtemp(suffix=f"_{project_id}", prefix="autoetl_"))
        else:
            fdir = Path(fdir)
        return fdir, project_id

    def load(self, fdir: str | Path):
        """Loads an existing project"""
        fdir = Path(fdir)
        if not fdir.exists():
            raise FileNotFoundError(f"Project directory {fdir} does not exist")
        autoetl_yaml = fdir / "autoetl.yaml"
        if not autoetl_yaml.exists():
            raise FileNotFoundError(
                f"autoetl.yaml file not found in {fdir}. Is this a valid project?"
            )
        with open(autoetl_yaml) as f:
            if len(f.read()) == 0:
                raise FileNotFoundError(
                    f"autoetl.yaml file is empty in {fdir}. Is this a valid project?"
                )
            settings = yaml.safe_load(f) or {}
        self.name = settings.get("name") or self.name
        self.description = settings.get("description") or self.description
        self.created_at = settings.get("created_at") or self.created_at
        self.id = settings.get("id") or self.id
        self.fdir = Path(fdir)

    def init(self):
        """Initializes the project"""
        # Example usage
        create_etl_project_structure(self.fdir)

        # Update the autoetl.yaml file with the project name
        autoetl_yaml = self.fdir / "autoetl.yaml"
        with open(autoetl_yaml) as f:
            content = f.read()
            settings = yaml.safe_load(content) if len(content) else {}

        settings.update(**self.dict(safe=True))
        with open(autoetl_yaml, "w") as f:
            yaml.safe_dump(settings, f)

    async def teardown(self):
        """Tears down the project"""
        self.delete_project_files(self.fdir)
        logger.info(f"Deleted project {self.name} from {self.fdir}")

    async def add_api(
        self,
        id: str | None = None,
        name: str | None = None,
        spec: str | None = None,
        docs: list[str] | None = None,
    ):
        return create_api(
            API(
                id=make_valid_folder_name(id or name).lower(),
                name=name,
                openapi_spec_url=spec,
                docs=docs,
            ),
            self.fdir,
        )

    async def crawl_api_docs(
        self,
        api_id: str,
        seed_urls: list[str] | None = None,
        url_prefixes: Set[str] | None = None,
        auth: Dict[str, str] | None = None,
        max_crawl_depth: int = 3,
        max_crawl_count: int = 100,
    ):
        """Crawls the API docs and configures the project"""
        api = get_api(api_id, self.fdir)
        if api is None:
            raise ValueError(f"API with id {api_id} does not exist")

        seed_urls = seed_urls or []
        if api.openapi_spec_url:
            seed_urls.append(api.openapi_spec_url)
        if api.docs:
            seed_urls.extend(api.docs)
        seed_urls = sorted(set(seed_urls))

        dc = create_doccrawl(
            api_id=api_id,
            fdir=self.fdir,
            seed_urls=seed_urls,
            url_prefixes=url_prefixes,
            auth=auth,
            max_crawl_depth=max_crawl_depth,
            max_crawl_count=max_crawl_count,
            start_time=datetime.datetime.now(datetime.timezone.utc),
        )
        await crawl(
            storage_dir=dc.storage_dir,
            seed_urls=dc.seed_urls,
            url_prefixes=dc.url_prefixes,
            auth=dc.auth,
            max_crawl_count=dc.max_crawl_count,
            max_crawl_depth=dc.max_crawl_depth,
        )

    async def add_database(self, *args, **kwargs):
        """Adds a database to the project"""

    async def add_function(self, *args, **kwargs):
        """Registers functions to the project"""

    async def build_etl(self, *args, **kwargs):
        """Builds the ETL pipeline"""
        return Service(id="etl")

    async def build_service(self, *args, **kwargs):
        """
        Creates fastAPI server with two chat endpoints
        1. /autoetl/chat/data
        2. /autoetl/chat/admin
        """
        return Service(id="api")

    async def deploy(self, services: list[any], **kwargs):
        """Deploys the project"""
        return {s.id: s for s in services}


def load_project(project_id: str | None = None, config: Config | None = None):
    config = config or load_config()
    projects = get_projects(config.config_dir)
    if not project_id or project_id is None or project_id.lower() == "none":
        project_id = projects.get("active")

    if project_list := (projects or {}).get("projects", {}):
        if project_id in project_list:
            return ETLProject(**project_list[project_id])
        else:
            logger.error(f"Project {project_id} not found in {config.config_dir}")
    else:
        logger.error(f"No projects found in {config.config_dir}\n")
