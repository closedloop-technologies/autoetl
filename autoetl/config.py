"""Loads the configuration file for the AutoETL package."""

# Load the configuration file
from dataclasses import dataclass
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


def load_config() -> Config:
    load_dotenv(
        verbose=True,
        dotenv_path=Path(__file__).parent.joinpath(".env"),
        override=False,
    )
    return Config(
        name=name,
        description=description,
        version=version,
    )
