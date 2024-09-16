import json
import logging

logger = logging.getLogger(__name__)


def parse_swagger_spec(swagger_json_file):
    try:
        with open(swagger_json_file, "r") as file:
            swagger_spec = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading Swagger JSON specification: {e}")
        return {}

    parsed_endpoints = []

    try:
        for path, path_info in swagger_spec["paths"].items():
            for http_method, endpoint_info in path_info.items():
                endpoint = {
                    "path": path,
                    "method": http_method.upper(),
                    "parameters": [],
                }

                for parameter in endpoint_info.get("parameters", []):
                    param = {
                        "name": parameter["name"],
                        "type": parameter["type"],
                        "required": parameter.get("required", False),
                        "in": parameter["in"],
                    }

                    if "format" in parameter:
                        param["format"] = parameter["format"]

                    if "minimum" in parameter:
                        param["minimum"] = parameter["minimum"]

                    if "maximum" in parameter:
                        param["maximum"] = parameter["maximum"]

                    endpoint["parameters"].append(param)

                parsed_endpoints.append(endpoint)
    except (KeyError, TypeError) as e:
        logger.error(f"Error parsing Swagger specification: {e}")
        return {}

    return parsed_endpoints
