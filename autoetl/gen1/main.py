import argparse
import logging
import os
from autoetl.gen1.swagger_parser import parse_swagger_spec
from autoetl.gen1.auth_rbac import determine_auth_rbac
from autoetl.gen1.type_generator import generate_request_types, generate_response_types
from autoetl.gen1.entity_types import identify_entity_types
from autoetl.gen1.api_client import generate_api_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(swagger_file, output_dir, language):
    # Parse the Swagger JSON specification
    swagger_spec = parse_swagger_spec(swagger_file)
    if not swagger_spec:
        logger.error("Failed to parse the Swagger specification.")
        return

    # Determine the authentication mechanism and RBAC structure
    auth_rbac_info = determine_auth_rbac(swagger_spec)

    # Generate request and response types
    request_types = generate_request_types(swagger_spec)
    response_types = generate_response_types(swagger_spec)

    # Identify and define entity types
    entity_types = identify_entity_types(swagger_spec)

    # Generate the API client
    api_client_code = generate_api_client(
        swagger_spec,
        auth_rbac_info,
        request_types,
        response_types,
        entity_types,
        language,
    )

    # Save the generated API client code to a file
    output_file = os.path.join(output_dir, f"api_client.{language}")
    with open(output_file, "w") as file:
        file.write(api_client_code)
    logger.info(f"Generated API client saved to {output_file}")

    # TODO: Generate documentation and examples


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a type-safe API client from a Swagger specification."
    )
    parser.add_argument("swagger_file", help="Path to the Swagger JSON file.")
    parser.add_argument(
        "-o", "--output", default=".", help="Output directory for the generated files."
    )
    parser.add_argument(
        "-l",
        "--language",
        default="py",
        choices=["py", "ts"],
        help="Programming language for the generated code (Python or TypeScript).",
    )
    args = parser.parse_args()

    main(args.swagger_file, args.output, args.language)
