"""Loads the configuration file for the AutoETL package."""

# Load the configuration file
from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

from autoetl import __description__ as description
from autoetl import __name__ as name
from autoetl import __version__ as version


@dataclass
class Config:
    """Configuration class for AutoETL"""

    # Add configuration variables here
    # Example:
    # MY_VAR: str = "my_value"
    name: str = name
    description: str = description
    version: str = version
    env_file: str = ".env"
    config_dir: str = Path.home().joinpath(".autoetl")
    anthropic_api_key: str | None = None


def load_config() -> Config:
    config_dir = Path(
        os.environ.get("AUTOETL_CONFIG_DIR", None) or Path.home()
    ).joinpath(".autoetl")
    env_file = Path(
        os.environ.get("AUTOETL_ENV_FILE", None)
        or Path(__file__).parent.parent.joinpath(".env")
    )

    load_dotenv(verbose=True, dotenv_path=env_file, override=False)

    return Config(
        name=name,
        description=description,
        version=version,
        env_file=str(env_file),
        config_dir=str(config_dir),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    )
