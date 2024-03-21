"""OpenAPI Documentation Bot for AutoETL."""

import contextlib
import os
from anthropic import Anthropic
import dotenv
from prefect import flow

from autoetl.config import Config, load_config

dotenv.load_dotenv()

# Set up the Anthropic API client

DEFAULT_SYSTEM_MESSAGE = """You are called autoETLDocBot.
You are a helpful assistant that generates OpenAPI compliant documentation and are a programming expert.
"""

from openapi_spec_validator import (
    OpenAPIV2SpecValidator,
    OpenAPIV30SpecValidator,
    OpenAPIV31SpecValidator,
    validate,
)
import json
from openapi_spec_validator import validate_url
from openapi_spec_validator import OpenAPIV31SpecValidator


def isvalid_openapi_spec(spec: dict) -> bool:
    """Check if the spec is a valid OpenAPI spec"""
    try:
        validate(spec, cls=OpenAPIV31SpecValidator)
        return True
    except Exception as e:
        return False


def determine_next_upgrade_goal(
    spec: dict,
) -> tuple[
    str, str, OpenAPIV2SpecValidator | OpenAPIV30SpecValidator | OpenAPIV31SpecValidator
]:
    """Determine the next upgrade goal for the OpenAPI spec"""
    valid_version = None
    target_version = "3.1"
    with contextlib.suppress(Exception):
        validate(spec, cls=OpenAPIV2SpecValidator)
        valid_version = "2.0"
        target_version = "3.0"
        target_validator = OpenAPIV30SpecValidator
    with contextlib.suppress(Exception):
        validate(spec, cls=OpenAPIV30SpecValidator)
        valid_version = "3.0"
        target_version = "3.1"
        target_validator = OpenAPIV31SpecValidator
    with contextlib.suppress(Exception):
        validate(spec, cls=OpenAPIV31SpecValidator)
        valid_version = OpenAPIV31SpecValidator
        target_version = None
        target_validator = None
    return valid_version, target_version, target_validator


class AutoETLDocBot:
    def __init__(self, config: Config = None):
        config = config or load_config()
        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set in the environment")
        self.client = Anthropic(api_key=config.anthropic_api_key)
        self.system_message = DEFAULT_SYSTEM_MESSAGE

    def fast_completion(self, prompt: str, context: str = None):
        system_message = (
            f"{self.system_message}\n\n{context}" if context else self.system_message
        )
        return self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [{"type": "text", "text": f"{context}\n\n{prompt}"}],
                },
            ],
            system=self.system_message,
        )

    def fix_openapi_error(self, spec: dict, error: str, version: str = "3.1.0"):
        """Fix an OpenAPI spec error"""
        return self.fast_completion(
            f"Fix the following error in the given openapi_json_spec, using minimal changes to comply with the {version} spec:\n<error>\n{error}\n</error>\nreturn only the fixed openapi_json_spec",
            f"<openapi_json_spec>{json.dumps(spec, indent=2)}</openapi_json_spec>",
        )

    def upgrade_openapi_spec(self, spec, max_tries=3):
        """Upgrade the OpenAPI spec to version 3.1.0"""

        while not isvalid_openapi_spec(spec) and max_tries > 0:
            _, target_version, target_validator = determine_next_upgrade_goal(spec)
            if target_version is None:
                break

            for error in target_validator(spec).iter_errors():
                response = self.fix_openapi_error(
                    spec, error.message, version=target_version
                )
                spec = json.loads(response["content"][0]["text"])

            max_tries -= 1
        return spec
