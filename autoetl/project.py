import datetime
import tempfile
from pathlib import Path

from autoetl.helpers import make_valid_folder_name
from autoetl.service import Service
from autoetl.templates import get_templates

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
        base_dir = project_root / base_dir.format(
            domain_name="domain_name",
            api_name="api_name",
            version="version",
            namespace="namespace",
            fn_name="fn_name",
            database_name="database_name",
            etl_name="etl_name",
            deployment_name="deployment_name",
        )
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
        self.description = description
        self.created_at = datetime.datetime.now(datetime.timezone.utc)
        self.fdir, self.id = self._set_project_and_fdir(name, fdir, project_id)

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

    def init(self):
        """Initializes the project"""
        # Example usage
        create_etl_project_structure(self.fdir)

    async def teardown(self):
        """Tears down the project"""

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
