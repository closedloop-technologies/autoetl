import datetime
import tempfile
from logging import getLogger
from pathlib import Path

import yaml

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
    ):
        if not name:
            raise ValueError("Project name is required")
        self.name = name
        self.fdir, self.id = self._set_project_and_fdir(name, fdir, project_id)

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

    def dict(self, safe=False):
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "fdir": str(self.fdir) if safe else self.fdir,
            "id": self.id,
        }

    def __repr__(self) -> str:
        description = f"Description: {self.description}" if self.description else ""
        created_time = self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        return f"<ETLProject name={self.name} id={self.id} created={created_time} fdir={self.fdir}>\n\t{description}".strip()

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
            settings = yaml.safe_load(f) if len(f.read()) else {}
        self.name = settings.get("name")
        self.description = settings.get("description")
        self.created_at = settings.get("created_at")
        self.fdir = Path(fdir)
        self.id = settings.get("id")

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
        fdir = Path(self.fdir)
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
        logger.info(f"Deleted project {self.name} from {self.fdir}")

    async def add_api(
        self,
        name: str | None = None,
        url: str | None = None,
        spec: str | None = None,
        docs: list[str] | None = None,
    ):
        """
        Adds an API to the project
        If missing the name, url, or spec,
        the user will be prompted to enter the missing information
        or auto-suggest an API based on the name and project info
        """

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


async def crawl(source: any):
    """Crawls the APIs and databases and configures the project"""
