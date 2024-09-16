import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def generate_request_types(swagger_spec: List[Dict]) -> Dict[str, str]:
    request_types = {}

    try:
        for endpoint_info in swagger_spec:
            path = endpoint_info["path"]
            method = endpoint_info["method"]
            type_name = f"{path}_{method}_Request"
            type_definition = "export interface {} {{\n".format(type_name)

            for param in endpoint_info["parameters"]:
                param_name = param["name"]
                param_type = param["type"]
                required = param["required"]
                type_definition += "  {}: {};\n".format(param_name, param_type)

            type_definition += "}\n"
            request_types[type_name] = type_definition
    except KeyError as e:
        logger.error(f"Error generating request types: {e}")

    return request_types


def generate_response_types(swagger_spec: List[Dict]) -> Dict[str, str]:
    response_types = {}

    try:
        for endpoint_info in swagger_spec:
            path = endpoint_info["path"]
            method = endpoint_info["method"]
            type_name = f"{path}_{method}_Response"
            type_definition = "export interface {} {{\n".format(type_name)

            # TODO: Extract response schema from Swagger spec and generate type definition
            type_definition += "  // TODO: Add response properties\n"

            type_definition += "}\n"
            response_types[type_name] = type_definition
    except KeyError as e:
        logger.error(f"Error generating response types: {e}")

    return response_types
