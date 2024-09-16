import logging

logger = logging.getLogger(__name__)


def determine_auth_rbac(swagger_spec):
    auth_details = {"auth_mechanism": None, "scopes": {}}

    rbac_mapping = {}

    try:
        security_definitions = swagger_spec.get("securityDefinitions", {})
        if security_definitions:
            auth_mechanism = None
            for definition_name, definition in security_definitions.items():
                if definition["type"] == "apiKey":
                    auth_mechanism = "API Key"
                elif definition["type"] == "oauth2":
                    auth_mechanism = "OAuth 2.0"
                    auth_details["scopes"] = definition.get("scopes", {})
                elif definition["type"] == "basic":
                    auth_mechanism = "Basic Authentication"
                else:
                    logger.warning(
                        f"Unsupported authentication mechanism: {definition['type']}"
                    )

            auth_details["auth_mechanism"] = auth_mechanism

        for endpoint_info in swagger_spec:
            endpoint = endpoint_info["path"]
            method = endpoint_info["method"]
            security_requirements = endpoint_info.get("security", [])
            if not security_requirements:
                security_requirements = endpoint_info.get("x-security", [])

            if security_requirements:
                rbac_mapping[(endpoint, method)] = security_requirements
            else:
                rbac_mapping[(endpoint, method)] = []

    except (KeyError, TypeError) as e:
        logger.error(f"Error determining authentication and RBAC: {e}")
        return {"auth_details": {}, "rbac_mapping": {}}

    return {"auth_details": auth_details, "rbac_mapping": rbac_mapping}
